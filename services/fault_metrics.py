"""故障类型 → Coroot 观测指标映射与数据提取。

根据故障类型从 Coroot 可观测平台获取对应的时序指标数据，
用于在执行详情页展示故障验证图表。

支持 10 种故障类型，K8s 层级使用应用级接口，物理机层级使用节点级接口。
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from config import Config
from services.coroot_client import get_coroot_client, CorootClientError

logger = logging.getLogger(__name__)

# 默认应用 ID 模板：{project_id}:{namespace}:Deployment:{service_name}
DEFAULT_DNS_APP_ID = f"{Config.COROOT_PROJECT_ID}:kube-system:Deployment:coredns"
DEFAULT_NODE_NAME = "tcse-v100-02"

# ── 故障类型 → 指标映射 ─────────────────────────────────────

# 故障类型英文名 → Coroot 指标配置
# 键与 workflow_builder.py 中的 FAULT_TYPE_MAP 保持一致
FAULT_METRIC_MAP: Dict[str, Dict[str, Any]] = {
    "network_loss": {
        "metric_name": "TCP Retransmissions",
        "metric_unit": "segments/second",
        "data_source": "app",
        "report_name": "Net",
        "chart_title_keyword": "TCP retransmissions",
        "description": "TCP 重传速率，丢包导致 TCP 重传增加",
    },
    "network_delay": {
        "metric_name": "Network RTT",
        "metric_unit": "seconds",
        "data_source": "app",
        "report_name": "Net",
        "chart_title_keyword": "Network RTT",
        "description": "集群内网络往返时延",
    },
    "network_partition": {
        "metric_name": "Active TCP Connections",
        "metric_unit": "connections",
        "data_source": "app",
        "report_name": "Net",
        "chart_title_keyword": "Active TCP connections",
        "description": "活跃 TCP 连接数，网络分区导致连接数骤降",
    },
    "pod_failure": {
        "metric_name": "Instance Count",
        "metric_unit": "count",
        "data_source": "app",
        "report_name": "Instances",
        "chart_title_keyword": "Instances",
        "description": "运行实例数，Pod 故障导致可用实例减少",
    },
    "pod_kill": {
        "metric_name": "Container Restarts",
        "metric_unit": "count",
        "data_source": "app",
        "report_name": "Instances",
        "chart_title_keyword": "Restarts",
        "description": "容器重启次数，Pod 被 Kill 后 K8s 自动重启",
    },
    "stress_cpu": {
        "metric_name": "Container CPU Usage",
        "metric_unit": "cores",
        "data_source": "app",
        "report_name": "CPU",
        "chart_title_keyword": "CPU usage",
        "chart_group_chart_index": 0,
        "description": "容器 CPU 使用量",
    },
    "stress_mem": {
        "metric_name": "Container Memory RSS",
        "metric_unit": "bytes",
        "data_source": "app",
        "report_name": "Memory",
        "chart_title_keyword": "Memory usage",
        "chart_group_chart_index": 0,
        "description": "容器 RSS 内存使用量",
    },
    "dns_error": {
        "metric_name": "DNS Errors",
        "metric_unit": "errors/second",
        "data_source": "dns_app",
        "report_name": "DNS",
        "chart_title_keyword": "DNS errors",
        "description": "DNS 错误速率（含 NXDOMAIN 和 Server Error）",
    },
    "node_cpu": {
        "metric_name": "Node CPU Usage",
        "metric_unit": "%",
        "data_source": "node",
        "chart_title_keyword": "CPU usage",
        "description": "节点 CPU 使用率（user/system/iowait 等）",
    },
    "node_mem": {
        "metric_name": "Node Memory Usage",
        "metric_unit": "bytes",
        "data_source": "node",
        "chart_title_keyword": "Memory usage, bytes",
        "description": "节点内存使用量（free/cache/used）",
    },
}


def get_fault_metrics(
    fault_type: str,
    target_service: str,
    from_ts: Optional[int] = None,
    to_ts: Optional[int] = None,
    node_name: Optional[str] = None,
) -> Dict[str, Any]:
    """根据故障类型获取对应的 Coroot 指标时序数据。

    Args:
        fault_type: 故障类型（如 "network_loss", "stress_cpu" 等）
        target_service: 目标服务名（用于构造 Coroot app_id）
        from_ts: 起始时间戳（毫秒），默认最近 1 小时
        to_ts: 结束时间戳（毫秒），默认当前时间
        node_name: 节点名称（仅物理机故障使用）

    Returns:
        包含 metric_name, metric_unit, description, time_range, series 的字典
    """
    if fault_type not in FAULT_METRIC_MAP:
        return {
            "fault_type": fault_type,
            "error": f"不支持的故障类型: {fault_type}",
            "series": [],
        }

    config = FAULT_METRIC_MAP[fault_type]

    # 设置默认时间范围
    if to_ts is None:
        to_ts = int(time.time() * 1000)
    if from_ts is None:
        from_ts = to_ts - 3600 * 1000  # 默认最近 1 小时

    client = get_coroot_client()
    data_source = config["data_source"]

    try:
        widgets = _fetch_widgets(
            client, data_source, target_service, node_name, from_ts, to_ts, config
        )
    except CorootClientError as e:
        logger.error("获取 Coroot 数据失败: %s", e)
        return {
            "fault_type": fault_type,
            "metric_name": config["metric_name"],
            "metric_unit": config["metric_unit"],
            "description": config["description"],
            "time_range": {"from": from_ts, "to": to_ts},
            "series": [],
            "error": str(e),
        }

    # 从 widgets 中提取目标 chart
    chart_data = _extract_chart(widgets, config)
    if chart_data is None:
        return {
            "fault_type": fault_type,
            "metric_name": config["metric_name"],
            "metric_unit": config["metric_unit"],
            "description": config["description"],
            "time_range": {"from": from_ts, "to": to_ts},
            "series": [],
            "error": "未找到对应的 chart 数据",
        }

    # 解析时间轴与 series
    return _parse_chart_data(fault_type, config, chart_data, from_ts, to_ts)


def _fetch_widgets(
    client: Any,
    data_source: str,
    target_service: str,
    node_name: Optional[str],
    from_ts: int,
    to_ts: int,
    config: Dict[str, Any],
) -> List[Any]:
    """根据数据源类型获取 Coroot widget 列表。"""
    if data_source == "node":
        # 物理机层级 → 节点详情
        name = node_name or DEFAULT_NODE_NAME
        raw_data = client.get_node(name, from_ts, to_ts)
        return raw_data.get("data", {}).get("widgets", [])

    elif data_source == "dns_app":
        # DNS 故障 → CoreDNS 应用
        raw_data = client.get_application(DEFAULT_DNS_APP_ID, from_ts, to_ts)
        report = _find_report(raw_data, config["report_name"])
        return report.get("widgets", []) if report else []

    else:
        # K8s 层级 → 目标服务应用
        app_id = (
            f"{Config.COROOT_PROJECT_ID}:{Config.TARGET_NAMESPACE}"
            f":Deployment:{target_service}"
        )
        raw_data = client.get_application(app_id, from_ts, to_ts)
        report = _find_report(raw_data, config["report_name"])
        return report.get("widgets", []) if report else []


def _find_report(
    raw_data: Dict[str, Any], report_name: str
) -> Optional[Dict[str, Any]]:
    """从应用数据中查找指定名称的 report。"""
    reports = raw_data.get("data", {}).get("reports", [])
    for report in reports:
        if report and report.get("name") == report_name:
            return report
    return None


def _extract_chart(
    widgets: List[Any], config: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """从 widgets 列表中根据标题关键词搜索目标 chart。

    搜索策略：
    1. 遍历所有 widget，检查 chart.title 或 chart_group.title
    2. 匹配包含 chart_title_keyword 的标题（大小写不敏感）
    3. 对于 chart_group，使用 chart_group_chart_index 选择子 chart
    """
    keyword = config.get("chart_title_keyword", "").lower()

    for widget in widgets:
        if widget is None:
            continue

        # 检查单独的 chart
        chart = widget.get("chart")
        if chart and keyword in chart.get("title", "").lower():
            return chart

        # 检查 chart_group
        chart_group = widget.get("chart_group")
        if chart_group and keyword in chart_group.get("title", "").lower():
            charts = chart_group.get("charts", [])
            chart_index = config.get("chart_group_chart_index", 0)
            if chart_index < len(charts) and charts[chart_index]:
                return charts[chart_index]

    return None


def _parse_chart_data(
    fault_type: str,
    config: Dict[str, Any],
    chart_data: Dict[str, Any],
    from_ts: int,
    to_ts: int,
) -> Dict[str, Any]:
    """将 Coroot chart 数据解析为标准化的时序响应。"""
    ctx = chart_data.get("ctx", {})
    step = ctx.get("step", 15000)
    data_from = ctx.get("from", from_ts)
    data_to = ctx.get("to", to_ts)

    # 提取所有 series
    series_list: List[Dict[str, Any]] = []
    for s in chart_data.get("series", []):
        name = s.get("name", s.get("title", "unknown"))
        raw_values = s.get("data", [])

        # 构造带时间戳的数据点
        data_points: List[List[Any]] = []
        for i, val in enumerate(raw_values):
            ts = data_from + i * step
            data_points.append([ts, val])

        # 计算统计值
        non_null = [v for v in raw_values if v is not None]
        stats: Dict[str, Any] = {}
        if non_null:
            stats = {
                "latest": non_null[-1],
                "avg": round(sum(non_null) / len(non_null), 4),
                "max": max(non_null),
                "min": min(non_null),
                "count": len(non_null),
            }

        series_list.append({
            "name": name,
            "stats": stats,
            "data_points": data_points,
        })

    # 提取 threshold（如 CPU limit）
    threshold_info = None
    threshold = chart_data.get("threshold")
    if threshold:
        t_data = threshold.get("data", [])
        t_val = t_data[0] if t_data else None
        threshold_info = {
            "name": threshold.get("name", ""),
            "value": t_val,
        }

    return {
        "fault_type": fault_type,
        "metric_name": config["metric_name"],
        "metric_unit": config["metric_unit"],
        "description": config["description"],
        "time_range": {
            "from": data_from,
            "to": data_to,
            "step": step,
        },
        "threshold": threshold_info,
        "series": series_list,
    }
