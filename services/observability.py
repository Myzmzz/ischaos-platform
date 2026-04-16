"""观测数据业务逻辑层。

调用链、指标、日志数据来自 Coroot 可观测平台；
拓扑和实体数据来自 Kubernetes API Server，供 observability_routes 路由调用。
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple

from config import Config
from services.coroot_client import get_coroot_client, CorootClientError
from services import k8s_client
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# train-ticket 命名空间过滤
TRAIN_TICKET_NAMESPACE = Config.TARGET_NAMESPACE


# ============================================================================
# 辅助工具
# ============================================================================


def _now_ms() -> int:
    """当前时间戳（毫秒）。"""
    return int(time.time() * 1000)


def _default_range(
    from_ts: Optional[int], to_ts: Optional[int]
) -> Tuple[int, int]:
    """设置默认时间范围（最近 1 小时）。"""
    if to_ts is None:
        to_ts = _now_ms()
    if from_ts is None:
        from_ts = to_ts - 3600 * 1000
    return int(from_ts), int(to_ts)


def _parse_app_id(app_id: str) -> Dict[str, str]:
    """从 Coroot app_id 中解析 namespace、kind、name。

    格式: project:namespace:Kind:name
    """
    parts = app_id.split(":")
    if len(parts) >= 4:
        return {
            "namespace": parts[1],
            "kind": parts[2],
            "name": parts[3],
        }
    return {"namespace": "", "kind": "", "name": app_id}


def _extract_service_name(app_id: str) -> str:
    """从 app_id 提取服务名。"""
    return _parse_app_id(app_id).get("name", app_id)


def _is_train_ticket_service(app_id: str) -> bool:
    """判断是否为 train-ticket 命名空间的服务型应用（排除中间件）。"""
    info = _parse_app_id(app_id)
    if info["namespace"] != TRAIN_TICKET_NAMESPACE:
        return False
    name = info["name"].lower()
    db_keywords = ["mongo", "mysql", "rabbitmq", "redis"]
    return not any(kw in name for kw in db_keywords)


def _get_tt_apps() -> List[Dict[str, Any]]:
    """获取所有 train-ticket 命名空间的应用列表。"""
    client = get_coroot_client()
    overview = client.get_overview_applications()
    all_apps = overview.get("data", {}).get("applications", [])
    return [a for a in all_apps if _is_train_ticket_service(a.get("id", ""))]


# ============================================================================
# API 1: 获取调用链数据
# ============================================================================


def get_traces(
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    trace_id: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """获取分布式调用链（Trace）数据。

    从所有 train-ticket 应用收集 eBPF tracing span 数据，
    按 trace_id 分组还原调用链。
    """
    start_time, end_time = _default_range(start_time, end_time)
    client = get_coroot_client()

    query_params = {"view":"traces","filters":[{"field":"ServiceName","op":"=","value":"ts-gateway-service"}],"include_aux":False,"diff":False}

    if trace_id:
        query_params["trace_id"] = trace_id
        spans = []
        trace_data = client.get_overview_traces(start_time, end_time, query_params)
        trace = trace_data.get("data", {}).get("traces", {}).get("trace", [])
        for span in trace:
            spans.append({
                "span_id": span.get("id", ""),
                "parent_id": span.get("parent_id", "") or "0",
                "service_name": span.get("service", ""),
                "operation_name": span.get("name", ""),
                "latency": int(span.get("duration", 0) * 1000),  # ms → μs
                "status_code": 1 if span.get("status", {}).get("error") else 0,
                "timestamp": span.get("timestamp", 0),
            })
        return {
            "total": len(spans),
            "spans": spans,
            "trace_id": trace_id,
        }
        
    traces_data = client.get_overview_traces(start_time, end_time, query_params)

    traces = traces_data.get("data", {}).get("traces", {}).get("traces", [])[:limit]

    data = []
    for t in traces:
        data.append({
            "trace_id": t.get("trace_id", ""),
            "id": t.get("id", ""),
            "service": t.get("service", ""),
            "name": t.get("name", ""),
            "timestamp": t.get("timestamp", 0),
            "status": t.get("status", ""),
            "status_code": 1 if t.get("status", {}).get("error") else 0,
            "latency": t.get("duration", 0),  # ms
            "spans": [],
        })
    return {
        "total": len(data),
        "traces": data,
    }


    # for t in traces:
    #     tid = t.get("trace_id", "")
    #     data_map = {
    #         "trace_id": tid,
    #         "spans": [],
    #     }
    #     query_params["trace_id"] = tid
    #     try:
    #         trace_data = client.get_overview_traces(start_time, end_time, query_params)
    #         trace = trace_data.get("data", {}).get("traces", {}).get("trace", [])
    #         for span in trace:
    #             data_map["spans"].append({
    #                 "span_id": span.get("id", ""),
    #                 "parent_id": span.get("parent_id", "") or "0",
    #                 "service_name": span.get("service", ""),
    #                 "operation_name": span.get("name", ""),
    #                 "latency": int(span.get("duration", 0) * 1000),  # ms → μs
    #                 "status_code": 1 if span.get("status", {}).get("error") else 0,
    #                 "timestamp": span.get("timestamp", 0),
    #             })
    #     except Exception as e:
    #         logger.debug("获取 %s trace 失败: %s", tid, e)
    #         continue
    #     data.append(data_map)

    # return {
    #     "total": len(data),
    #     "traces": data,
    # }

    # tt_apps = _get_tt_apps()

    # # 收集所有 spans
    # all_spans: List[Dict[str, Any]] = []
    # for app in tt_apps:
    #     app_id = app["id"]
    #     try:
    #         tracing_data = client.get_app_tracing(app_id, start_time, end_time)
    #         spans = tracing_data.get("data", {}).get("spans") or []
    #         all_spans.extend(spans)
    #     except Exception as e:
    #         logger.debug("获取 %s tracing 失败: %s", app_id, e)
    #         continue

    # # 如果指定了 trace_id，过滤
    # if trace_id:
    #     all_spans = [s for s in all_spans if s.get("trace_id") == trace_id]

    # # 按 trace_id 分组
    # trace_map: Dict[str, List[Dict[str, Any]]] = {}
    # for span in all_spans:
    #     tid = span.get("trace_id", "")
    #     if tid not in trace_map:
    #         trace_map[tid] = []
    #     trace_map[tid].append({
    #         "span_id": span.get("id", ""),
    #         "parent_id": span.get("parent_id", "") or "0",
    #         "service_name": span.get("service", ""),
    #         "operation_name": span.get("name", ""),
    #         "latency": int(span.get("duration", 0) * 1000),  # ms → μs
    #         "status_code": 1 if span.get("status", {}).get("error") else 0,
    #         "timestamp": span.get("timestamp", 0),
    #     })

    # # 构造响应
    # traces = []
    # for tid, spans in list(trace_map.items())[:limit]:
    #     traces.append({"trace_id": tid, "spans": spans})

    # return {
    #     "total": len(traces),
    #     "traces": traces,
    # }


# ============================================================================
# API 2: 获取监控指标数据
# ============================================================================

# 指标提取配置：指标名 → (report, chart_title_keyword, chart_group_index, unit)
METRIC_EXTRACT_CONFIG: Dict[str, Dict[str, Any]] = {
    "cpu_usage": {
        "source": "app",
        "report": "CPU",
        "keyword": "CPU usage",
        "chart_group_idx": 0,
        "unit": "%",
        "transform": "to_percent",
    },
    "memory_usage": {
        "source": "app",
        "report": "Memory",
        "keyword": "Memory usage",
        "chart_group_idx": 0,
        "unit": "%",
        "transform": "to_percent",
    },
    "network_in_bytes": {
        "source": "app",
        "report": "Net",
        "keyword": "Traffic",
        "chart_group_idx": 0,
        "unit": "bytes/s",
    },
    "network_out_bytes": {
        "source": "app",
        "report": "Net",
        "keyword": "Traffic",
        "chart_group_idx": 1,
        "unit": "bytes/s",
    },
    "disk_read_bytes": {
        "source": "node",
        "keyword": "Bandwidth",
        "chart_group_idx": 0,
        "unit": "bytes/s",
    },
    "disk_write_bytes": {
        "source": "node",
        "keyword": "Bandwidth",
        "chart_group_idx": 1,
        "unit": "bytes/s",
    },
    "request_latency_ms": {
        "source": "app",
        "report": "Net",
        "keyword": "Network RTT",
        "unit": "ms",
        "transform": "s_to_ms",
    },
    "error_rate": {
        "source": "app",
        "report": "SLO",
        "keyword": "Errors",
        "unit": "%",
    },
    "connection_count": {
        "source": "app",
        "report": "Net",
        "keyword": "Active TCP connections",
        "unit": "count",
    },
    "request_count": {
        "source": "app",
        "report": "SLO",
        "keyword": "Requests to the",
        "unit": "count/s",
    },
}


def _find_chart_in_widgets(
    widgets: List[Any],
    keyword: str,
    chart_group_idx: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """根据关键词在 widgets 中查找 chart。"""
    for w in widgets:
        if w is None:
            continue
        chart = w.get("chart")
        if chart and keyword.lower() in chart.get("title", "").lower():
            return chart
        cg = w.get("chart_group")
        if cg and keyword.lower() in cg.get("title", "").lower():
            charts = cg.get("charts", [])
            idx = chart_group_idx if chart_group_idx is not None else 0
            if idx < len(charts) and charts[idx]:
                return charts[idx]
    return None


def _chart_to_values(
    chart: Dict[str, Any], transform: Optional[str] = None
) -> List[Dict[str, Any]]:
    """将 chart 的所有 series 聚合为 [{timestamp, value}] 列表。"""
    ctx = chart.get("ctx", {})
    step = ctx.get("step", 15000)
    from_ts = ctx.get("from", 0)

    # 获取 threshold（用于百分比计算）
    threshold = chart.get("threshold") or {}
    limit_data = threshold.get("data") or []
    limit_val = limit_data[0] if limit_data else None

    # 聚合所有 series（取平均值）
    all_series = chart.get("series", [])
    if not all_series:
        return []

    data_len = max(len(s.get("data", [])) for s in all_series)
    values: List[Dict[str, Any]] = []

    for i in range(data_len):
        ts = from_ts + i * step
        vals = []
        for s in all_series:
            d = s.get("data", [])
            if i < len(d) and d[i] is not None:
                vals.append(d[i])
        if vals:
            avg = sum(vals) / len(vals)
            if transform == "to_percent" and limit_val and limit_val > 0:
                avg = (avg / limit_val) * 100
            elif transform == "s_to_ms":
                avg = avg * 1000
            values.append({"timestamp": ts, "value": round(avg, 4)})

    return values


def get_metrics(
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    metric_names: Optional[str] = None,
    app_id: Optional[str] = None,
    interval: Optional[int] = None,
) -> Dict[str, Any]:
    """获取监控指标时序数据。

    从指定应用的 Coroot 报告中提取各类指标。
    """
    start_time, end_time = _default_range(start_time, end_time)
    client = get_coroot_client()

    # 确定目标应用
    if not app_id:
        app_id = (
            f"{Config.COROOT_PROJECT_ID}:{TRAIN_TICKET_NAMESPACE}"
            f":Deployment:ts-travel-service"
        )

    # 确定需要获取的指标
    if metric_names:
        requested = [m.strip() for m in metric_names.split(",")]
    else:
        requested = list(METRIC_EXTRACT_CONFIG.keys())

    # 获取应用数据
    app_data = client.get_application(app_id, start_time, end_time)
    reports = app_data.get("data", {}).get("reports", [])

    # 获取节点数据（用于 disk 指标）
    node_widgets: Optional[List[Any]] = None
    need_node = any(
        METRIC_EXTRACT_CONFIG.get(m, {}).get("source") == "node"
        for m in requested
        if m in METRIC_EXTRACT_CONFIG
    )
    if need_node:
        node_name = _infer_node_name(reports)
        try:
            node_data = client.get_node(node_name, start_time, end_time)
            node_widgets = node_data.get("data", {}).get("widgets", [])
        except Exception as e:
            logger.warning("获取节点数据失败: %s", e)

    # 提取各指标
    metrics: List[Dict[str, Any]] = []
    for metric_name in requested:
        config = METRIC_EXTRACT_CONFIG.get(metric_name)
        if not config:
            continue

        chart = None
        source = config.get("source", "app")

        if source == "app":
            report_name = config.get("report", "")
            for r in reports:
                if r and r.get("name") == report_name:
                    chart = _find_chart_in_widgets(
                        r.get("widgets", []),
                        config["keyword"],
                        config.get("chart_group_idx"),
                    )
                    break
        elif source == "node" and node_widgets:
            chart = _find_chart_in_widgets(
                node_widgets,
                config["keyword"],
                config.get("chart_group_idx"),
            )

        if chart:
            values = _chart_to_values(chart, config.get("transform"))
            # 按 interval 采样
            if interval and interval > 0 and values:
                interval_ms = interval * 1000
                sampled = []
                last_ts = 0
                for v in values:
                    if v["timestamp"] - last_ts >= interval_ms:
                        sampled.append(v)
                        last_ts = v["timestamp"]
                values = sampled
        else:
            values = []

        metrics.append({
            "metric_name": metric_name,
            "unit": config["unit"],
            "values": values,
        })

    service_name = _extract_service_name(app_id)
    return {
        "service_name": service_name,
        "metrics": metrics,
    }


def _infer_node_name(reports: List[Dict[str, Any]]) -> str:
    """从应用报告中推断节点名称。"""
    for r in reports:
        if r and r.get("name") == "CPU":
            for w in r.get("widgets", []):
                cg = w.get("chart_group") if w else None
                if cg and "Node CPU" in cg.get("title", ""):
                    charts = cg.get("charts", [])
                    if charts and charts[0]:
                        return charts[0].get("title", "tcse-v100-02")
    return "tcse-v100-02"


# ============================================================================
# API 3: 获取日志数据
# ============================================================================


def get_logs(
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    anomalous_only: bool = False,
    limit: int = 500,
) -> Dict[str, Any]:
    """获取结构化日志数据。

    从所有 train-ticket 应用收集日志。
    """
    start_time, end_time = _default_range(start_time, end_time)
    client = get_coroot_client()
    tt_apps = _get_tt_apps()

    all_logs: List[Dict[str, Any]] = []

    for app in tt_apps:
        app_id = app["id"]
        service_name = _extract_service_name(app_id)
        try:
            log_data = client.get_app_logs(app_id, start_time, end_time)
            entries = log_data.get("data", {}).get("entries") or []
            for entry in entries:
                severity = entry.get("severity", "info").upper()
                is_anomalous = severity in ("ERROR", "CRITICAL")

                if anomalous_only and not is_anomalous:
                    continue

                raw_msg = entry.get("message", "")
                attrs = entry.get("attributes", {})
                event_template = attrs.get("pattern.hash", raw_msg[:100])

                log_entry: Dict[str, Any] = {
                    "service_name": service_name,
                    "timestamp": entry.get("timestamp", 0),
                    "level": severity,
                    "event_template": event_template,
                    "raw_message": raw_msg,
                    "is_anomalous": is_anomalous,
                }

                trace_id = entry.get("trace_id")
                if trace_id:
                    log_entry["trace_id"] = trace_id

                all_logs.append(log_entry)
        except Exception as e:
            logger.debug("获取 %s 日志失败: %s", app_id, e)
            continue

    # 按时间排序
    all_logs.sort(key=lambda x: x["timestamp"], reverse=True)
    all_logs = all_logs[:limit]

    return {
        "total": len(all_logs),
        "logs": all_logs,
    }


# ============================================================================
# API 4: 获取部署拓扑关系
# ============================================================================


def get_topology() -> Dict[str, Any]:
    """获取服务、Pod、节点之间的部署拓扑关系。

    数据来源：Kubernetes API Server（Pod/Node 部署信息）
    + Coroot（服务间调用依赖关系）。
    """
    return k8s_client.get_topology(Config.TARGET_NAMESPACE)


# ============================================================================
# API 5: 获取实体列表
# ============================================================================


def get_entities(entity_type: Optional[str] = None) -> Dict[str, Any]:
    """获取系统中所有监控实体列表。

    数据来源：Kubernetes API Server。
    """
    return k8s_client.get_entities(Config.TARGET_NAMESPACE, entity_type)


# ============================================================================
# 故障状态查询
# ============================================================================


def get_node_metrics(
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    metric_names: Optional[str] = None,
    node_name: Optional[str] = None,
    interval: Optional[int] = None,
) -> Dict[str, Any]:
    """获取节点级监控指标时序数据。

    从指定节点的 Coroot 数据中提取各类指标。
    """
    start_time, end_time = _default_range(start_time, end_time)
    client = get_coroot_client()

    # 确定目标节点
    if not node_name:
        node_name = "tcse-v100-02"

    # 确定需要获取的指标
    if metric_names:
        requested = [m.strip() for m in metric_names.split(",")]
    else:
        requested = [m for m in METRIC_EXTRACT_CONFIG.keys() if METRIC_EXTRACT_CONFIG.get(m, {}).get("source") == "node"]

    # 获取节点数据
    try:
        node_data = client.get_node(node_name, start_time, end_time)
        node_widgets = node_data.get("data", {}).get("widgets", [])
    except Exception as e:
        logger.warning("获取节点数据失败: %s", e)
        node_widgets = []

    # 提取各指标
    metrics: List[Dict[str, Any]] = []
    for metric_name in requested:
        config = METRIC_EXTRACT_CONFIG.get(metric_name)
        if not config:
            continue

        chart = None
        if node_widgets:
            chart = _find_chart_in_widgets(
                node_widgets,
                config["keyword"],
                config.get("chart_group_idx"),
            )

        if chart:
            values = _chart_to_values(chart, config.get("transform"))
            # 按 interval 采样
            if interval and interval > 0 and values:
                interval_ms = interval * 1000
                sampled = []
                last_ts = 0
                for v in values:
                    if v["timestamp"] - last_ts >= interval_ms:
                        sampled.append(v)
                        last_ts = v["timestamp"]
                values = sampled
        else:
            values = []

        metrics.append({
            "metric_name": metric_name,
            "unit": config["unit"],
            "values": values,
        })

    return {
        "node_name": node_name,
        "metrics": metrics,
    }


def get_fault_status() -> Dict[str, Any]:
    """获取当前所有活跃故障的状态。

    从 service_fault_lock 表中读取当前锁定的服务，
    并关联执行记录返回详细信息。
    """
    from models.database import get_db
    from models import execution as execution_model
    from models import plan as plan_model

    db = get_db()
    rows = db.execute(
        """SELECT id, service_name, execution_id, locked_at
           FROM service_fault_lock"""
    ).fetchall()

    active_faults: List[Dict[str, Any]] = []
    for row in rows:
        fault_info: Dict[str, Any] = {
            "service_name": row["service_name"],
            "execution_id": row["execution_id"],
            "locked_at": row["locked_at"],
        }

        # 补充执行记录信息
        execution = execution_model.get_by_id(row["execution_id"])
        if execution:
            fault_info["execution_status"] = execution["status"]
            fault_info["workflow_name"] = execution["workflow_name"]
            fault_info["started_at"] = execution["started_at"]

            # 补充计划信息
            plan = plan_model.get_by_id(execution["plan_id"])
            if plan:
                fault_info["fault_type"] = plan["fault_type"]
                fault_info["plan_name"] = plan["name"]

        active_faults.append(fault_info)

    return {
        "active_count": len(active_faults),
        "faults": active_faults,
    }
