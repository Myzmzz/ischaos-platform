"""Coroot REST API 客户端封装。

提供登录认证、应用详情获取、节点详情获取三个核心方法，
通过 requests.Session 维护登录态（Cookie）。
"""

import json
import logging
from typing import Any, Dict, Optional

import requests

from config import Config

logger = logging.getLogger(__name__)

# API 请求超时（秒）
REQUEST_TIMEOUT = 15


def _log_response(method: str, url: str, resp: requests.Response) -> None:
    """记录 HTTP 响应详情（截断过长响应）。"""
    body_text = resp.text[:3000] if resp.text else "(empty)"
    if len(resp.text) > 3000:
        body_text += "...(truncated)"
    logger.debug(
        "[CorootClient] <<< %s %s %d [%d bytes]\n    Response: %s",
        method, url, resp.status_code, len(resp.text), body_text,
    )


class CorootClientError(Exception):
    """Coroot API 调用异常。"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class CorootClient:
    """Coroot REST API 客户端，封装认证和数据获取。

    使用 requests.Session 保持登录态，首次请求自动登录。
    """

    def __init__(self) -> None:
        self.base_url: str = Config.COROOT_URL.rstrip("/")
        self.username: str = Config.COROOT_USERNAME
        self.password: str = Config.COROOT_PASSWORD
        self.project_id: str = Config.COROOT_PROJECT_ID
        self.session: requests.Session = requests.Session()
        self._logged_in: bool = False

    def login(self) -> None:
        """通过用户名密码登录 Coroot，获取会话 Cookie。"""
        url = f"{self.base_url}/api/login"
        payload = {"email": self.username, "password": self.password}

        logger.debug(
            "[CorootClient] >>> POST %s\n    Body: %s",
            url, json.dumps({"email": self.username, "password": "***"}),
        )

        try:
            resp = self.session.post(url, json=payload, timeout=REQUEST_TIMEOUT)
            _log_response("POST", url, resp)
            if resp.status_code != 200:
                raise CorootClientError(
                    f"Coroot 登录失败: HTTP {resp.status_code}",
                    status_code=resp.status_code,
                )
            self._logged_in = True
            logger.info("[CorootClient] 登录成功")
        except requests.exceptions.RequestException as e:
            logger.error("[CorootClient] 登录连接失败: %s", e)
            raise CorootClientError(f"Coroot 连接失败: {e}")

    def _ensure_login(self) -> None:
        """确保已登录。"""
        if not self._logged_in:
            self.login()

    def get_application(
        self,
        app_id: str,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
    ) -> Dict[str, Any]:
        """获取应用详情数据。

        Args:
            app_id: 应用 ID（格式: project:namespace:Kind:name）
            from_ts: 起始时间戳（毫秒）
            to_ts: 结束时间戳（毫秒）

        Returns:
            应用详情 JSON 数据
        """
        self._ensure_login()

        url = f"{self.base_url}/api/project/{self.project_id}/app/{app_id}"
        params: Dict[str, Any] = {}
        if from_ts is not None:
            params["from"] = from_ts
        if to_ts is not None:
            params["to"] = to_ts

        logger.debug(
            "[CorootClient] >>> GET %s\n    Params: %s",
            url, params,
        )

        try:
            resp = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            _log_response("GET", url, resp)
            if resp.status_code != 200:
                raise CorootClientError(
                    f"获取应用数据失败: HTTP {resp.status_code}",
                    status_code=resp.status_code,
                )
            return resp.json()
        except requests.exceptions.RequestException as e:
            logger.error("[CorootClient] GET %s 请求失败: %s", url, e)
            raise CorootClientError(f"Coroot API 请求失败: {e}")

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """通用 GET 请求，路径相对于 /api/project/{project_id}/。

        Args:
            path: 相对路径（如 "overview/applications"）
            params: 查询参数

        Returns:
            JSON 响应
        """
        self._ensure_login()
        url = f"{self.base_url}/api/project/{self.project_id}/{path}"
        logger.debug("[CorootClient] >>> GET %s\n    Params: %s", url, params)

        try:
            resp = self.session.get(url, params=params or {}, timeout=REQUEST_TIMEOUT)
            _log_response("GET", url, resp)
            if resp.status_code != 200:
                raise CorootClientError(
                    f"GET {path} 失败: HTTP {resp.status_code}",
                    status_code=resp.status_code,
                )
            return resp.json()
        except requests.exceptions.RequestException as e:
            logger.error("[CorootClient] GET %s 请求失败: %s", url, e)
            raise CorootClientError(f"Coroot API 请求失败: {e}")

    def get_app_tracing(
        self,
        app_id: str,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
    ) -> Dict[str, Any]:
        """获取应用的 tracing 数据。"""
        params: Dict[str, Any] = {}
        if from_ts is not None:
            params["from"] = from_ts
        if to_ts is not None:
            params["to"] = to_ts
        return self.get(f"app/{app_id}/tracing", params)

    def get_app_logs(
        self,
        app_id: str,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
        severity: Optional[str] = None,
    ) -> Dict[str, Any]:
        """获取应用日志。"""
        params: Dict[str, Any] = {"source": "agent"}
        if from_ts is not None:
            params["from"] = from_ts
        if to_ts is not None:
            params["to"] = to_ts
        if severity is not None:
            params["severity"] = severity
        return self.get(f"app/{app_id}/logs", params)

    def get_overview_applications(self) -> Dict[str, Any]:
        """获取应用概览列表。"""
        return self.get("overview/applications")

    def get_overview_nodes(self) -> Dict[str, Any]:
        """获取节点概览列表。"""
        return self.get("overview/nodes")

    def get_overview_traces(
        self,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
    ) -> Dict[str, Any]:
        """获取调用链概览。"""
        params: Dict[str, Any] = {}
        if from_ts is not None:
            params["from"] = from_ts
        if to_ts is not None:
            params["to"] = to_ts
        return self.get("overview/traces", params)

    def get_node(
        self,
        node_name: str,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
    ) -> Dict[str, Any]:
        """获取节点详情数据。

        Args:
            node_name: 节点名称
            from_ts: 起始时间戳（毫秒）
            to_ts: 结束时间戳（毫秒）

        Returns:
            节点详情 JSON 数据
        """
        self._ensure_login()

        url = f"{self.base_url}/api/project/{self.project_id}/node/{node_name}"
        params: Dict[str, Any] = {}
        if from_ts is not None:
            params["from"] = from_ts
        if to_ts is not None:
            params["to"] = to_ts

        logger.debug(
            "[CorootClient] >>> GET %s\n    Params: %s",
            url, params,
        )

        try:
            resp = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            _log_response("GET", url, resp)
            if resp.status_code != 200:
                raise CorootClientError(
                    f"获取节点数据失败: HTTP {resp.status_code}",
                    status_code=resp.status_code,
                )
            return resp.json()
        except requests.exceptions.RequestException as e:
            logger.error("[CorootClient] GET %s 请求失败: %s", url, e)
            raise CorootClientError(f"Coroot API 请求失败: {e}")


# 模块级单例，避免每次请求都新建 Session
_client: Optional[CorootClient] = None


def get_coroot_client() -> CorootClient:
    """获取 Coroot 客户端单例。"""
    global _client
    if _client is None:
        _client = CorootClient()
    return _client
