"""Chaos Mesh REST API 封装。

提供创建 Workflow、查询状态、停止 Workflow 三个核心方法，
统一异常处理与超时配置。
"""

import logging
from typing import Any

import requests

from config import Config

logger = logging.getLogger(__name__)

# API 请求超时（秒）
REQUEST_TIMEOUT = 10


class ChaosClientError(Exception):
    """Chaos Mesh API 调用异常。"""

    def __init__(self, message: str, status_code: int | None = None):
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
    logger.info("创建 Workflow: POST %s", url)

    try:
        resp = requests.post(url, json=workflow_json, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        raise ChaosClientError("Chaos Mesh API 请求超时")
    except requests.exceptions.ConnectionError:
        raise ChaosClientError("无法连接 Chaos Mesh API")
    except requests.exceptions.HTTPError as e:
        # 尝试从响应体获取错误信息
        error_msg = _extract_error_message(e.response)
        raise ChaosClientError(
            f"Chaos Mesh API 返回错误: {error_msg}",
            status_code=e.response.status_code,
        )


def get_workflow_status(
    workflow_name: str, namespace: str | None = None
) -> dict[str, Any]:
    """查询 Workflow 运行状态。

    Args:
        workflow_name: Workflow 名称
        namespace: 命名空间，默认使用 Config.TARGET_NAMESPACE

    Returns:
        Workflow 状态摘要 JSON

    Raises:
        ChaosClientError: API 调用失败
    """
    if namespace is None:
        namespace = Config.TARGET_NAMESPACE

    url = f"{_base_url()}/real_time/workflow/{workflow_name}/summary"
    params = {"namespace": namespace}
    logger.info("查询 Workflow 状态: GET %s", url)

    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        raise ChaosClientError("Chaos Mesh API 请求超时")
    except requests.exceptions.ConnectionError:
        raise ChaosClientError("无法连接 Chaos Mesh API")
    except requests.exceptions.HTTPError as e:
        error_msg = _extract_error_message(e.response)
        raise ChaosClientError(
            f"查询 Workflow 状态失败: {error_msg}",
            status_code=e.response.status_code,
        )


def stop_workflow(
    workflow_name: str, namespace: str | None = None
) -> dict[str, Any]:
    """停止正在运行的 Workflow。

    Args:
        workflow_name: Workflow 名称
        namespace: 命名空间，默认使用 Config.TARGET_NAMESPACE

    Returns:
        Chaos Mesh API 响应 JSON

    Raises:
        ChaosClientError: API 调用失败
    """
    if namespace is None:
        namespace = Config.TARGET_NAMESPACE

    url = f"{_base_url()}/real_time/workflow/{workflow_name}/stop"
    params = {"namespace": namespace}
    logger.info("停止 Workflow: PUT %s", url)

    try:
        resp = requests.put(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        # 部分 Chaos Mesh 版本停止操作返回空 body
        if resp.text:
            return resp.json()
        return {"status": "stopped"}
    except requests.exceptions.Timeout:
        raise ChaosClientError("Chaos Mesh API 请求超时")
    except requests.exceptions.ConnectionError:
        raise ChaosClientError("无法连接 Chaos Mesh API")
    except requests.exceptions.HTTPError as e:
        error_msg = _extract_error_message(e.response)
        raise ChaosClientError(
            f"停止 Workflow 失败: {error_msg}",
            status_code=e.response.status_code,
        )


def _extract_error_message(response: requests.Response) -> str:
    """从响应体中提取错误消息。"""
    try:
        body = response.json()
        # Chaos Mesh 通常返回 {"message": "..."} 或 {"error": "..."}
        return body.get("message") or body.get("error") or str(body)
    except Exception:
        return response.text or f"HTTP {response.status_code}"
