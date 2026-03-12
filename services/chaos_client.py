"""Chaos Mesh REST API 封装。

提供创建 Workflow、查询状态、停止 Workflow 三个核心方法，
统一异常处理与超时配置。
"""

import logging
from typing import Any, Optional

import requests

from config import Config

logger = logging.getLogger(__name__)

# API 请求超时（秒）
REQUEST_TIMEOUT = 10


class ChaosClientError(Exception):
    """Chaos Mesh API 调用异常。"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


def _base_url() -> str:
    """返回 Chaos Mesh API 基础 URL。"""
    return f"{Config.CHAOS_MESH_URL}/api"


def create_workflow(workflow_json: dict[str, Any]) -> dict[str, Any]:
    """创建 Chaos Mesh Workflow（提交故障注入）。

    Args:
        workflow_json: 完整的 Workflow JSON 对象

    Returns:
        Chaos Mesh API 响应 JSON

    Raises:
        ChaosClientError: API 调用失败
    """
    url = f"{_base_url()}/real_time/workflow"

    # Dashboard API 要求请求体包裹在 {"workflow": ..., "k6": {}} 中
    payload = {"workflow": workflow_json, "k6": {}}

    logger.debug(
        "[ChaosClient] >>> POST %s\n    Body: %s",
        url, _safe_json(payload),
    )

    try:
        resp = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        _log_response("POST", url, resp)
        resp.raise_for_status()
        # Chaos Mesh 成功时可能返回 200 + 空 body
        result = _parse_response_body(resp)
        # Chaos Mesh 失败时也可能返回 200，但 body 中包含 error 信息
        return result
    except requests.exceptions.Timeout:
        logger.error("[ChaosClient] POST %s TIMEOUT", url)
        raise ChaosClientError("Chaos Mesh API 请求超时")
    except requests.exceptions.ConnectionError:
        logger.error("[ChaosClient] POST %s CONNECTION ERROR", url)
        raise ChaosClientError("无法连接 Chaos Mesh API")
    except requests.exceptions.HTTPError as e:
        error_msg = _extract_error_message(e.response)
        raise ChaosClientError(
            f"Chaos Mesh API 返回错误: {error_msg}",
            status_code=e.response.status_code,
        )


def get_workflow_status(
    workflow_name: str, namespace: Optional[str] = None
) -> dict[str, Any]:
    """查询 Workflow 运行状态。

    Args:
        workflow_name: Workflow 名称
        namespace: 命名空间，默认 chaos-mesh

    Returns:
        Workflow 状态摘要 JSON

    Raises:
        ChaosClientError: API 调用失败
    """
    if namespace is None:
        namespace = "chaos-mesh"

    url = f"{_base_url()}/real_time/workflow/{workflow_name}/summary"
    params = {"namespace": namespace}

    logger.debug(
        "[ChaosClient] >>> GET %s\n    Params: %s",
        url, params,
    )

    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        _log_response("GET", url, resp)
        resp.raise_for_status()
        result = _parse_response_body(resp)
        return result
    except requests.exceptions.Timeout:
        logger.error("[ChaosClient] GET %s TIMEOUT", url)
        raise ChaosClientError("Chaos Mesh API 请求超时")
    except requests.exceptions.ConnectionError:
        logger.error("[ChaosClient] GET %s CONNECTION ERROR", url)
        raise ChaosClientError("无法连接 Chaos Mesh API")
    except requests.exceptions.HTTPError as e:
        error_msg = _extract_error_message(e.response)
        raise ChaosClientError(
            f"查询 Workflow 状态失败: {error_msg}",
            status_code=e.response.status_code,
        )


def stop_workflow(
    workflow_name: str, namespace: Optional[str] = None
) -> dict[str, Any]:
    """停止正在运行的 Workflow。

    Args:
        workflow_name: Workflow 名称
        namespace: 命名空间，默认 chaos-mesh

    Returns:
        Chaos Mesh API 响应 JSON

    Raises:
        ChaosClientError: API 调用失败
    """
    if namespace is None:
        namespace = "chaos-mesh"

    url = f"{_base_url()}/real_time/workflow/{workflow_name}/stop"
    params = {"namespace": namespace}

    logger.debug(
        "[ChaosClient] >>> PUT %s\n    Params: %s",
        url, params,
    )

    try:
        resp = requests.put(url, params=params, timeout=REQUEST_TIMEOUT)
        _log_response("PUT", url, resp)
        resp.raise_for_status()
        result = _parse_response_body(resp)
        return result
    except requests.exceptions.Timeout:
        logger.error("[ChaosClient] PUT %s TIMEOUT", url)
        raise ChaosClientError("Chaos Mesh API 请求超时")
    except requests.exceptions.ConnectionError:
        logger.error("[ChaosClient] PUT %s CONNECTION ERROR", url)
        raise ChaosClientError("无法连接 Chaos Mesh API")
    except requests.exceptions.HTTPError as e:
        error_msg = _extract_error_message(e.response)
        raise ChaosClientError(
            f"停止 Workflow 失败: {error_msg}",
            status_code=e.response.status_code,
        )


def _parse_response_body(resp: requests.Response) -> dict[str, Any]:
    """安全解析响应体 JSON，空 body 返回空字典。"""
    if not resp.text or not resp.text.strip():
        return {"status": "ok"}
    try:
        return resp.json()
    except (ValueError, requests.exceptions.JSONDecodeError):
        logger.warning(
            "[ChaosClient] 响应体非 JSON: %s", resp.text[:500],
        )
        return {"raw_response": resp.text[:500]}



def _extract_error_message(response: requests.Response) -> str:
    """从响应体中提取错误消息。"""
    try:
        body = response.json()
        # Chaos Mesh 通常返回 {"message": "..."} 或 {"error": "..."}
        return body.get("message") or body.get("error") or str(body)
    except Exception:
        return response.text or f"HTTP {response.status_code}"


def _log_response(method: str, url: str, resp: requests.Response) -> None:
    """记录 HTTP 响应详情。"""
    body_text = resp.text[:3000] if resp.text else "(empty)"
    logger.debug(
        "[ChaosClient] <<< %s %s %d\n    Response: %s",
        method, url, resp.status_code, body_text,
    )


def _safe_json(obj: Any) -> str:
    """安全地将对象序列化为 JSON 字符串（用于日志）。"""
    import json
    try:
        text = json.dumps(obj, ensure_ascii=False, indent=2)
        if len(text) > 3000:
            return text[:3000] + "...(truncated)"
        return text
    except (TypeError, ValueError):
        return str(obj)[:3000]
