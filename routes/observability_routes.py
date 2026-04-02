"""观测数据 API 路由。

提供调用链、指标、日志、拓扑、实体的查询接口，
以及故障状态查询接口。

所有接口挂载在 /api/v1/ 前缀下。
"""

import logging

from flask import Blueprint, jsonify, request

from config import Config
from services import observability

logger = logging.getLogger(__name__)

observability_bp = Blueprint("observability", __name__)


@observability_bp.route("/traces", methods=["GET"])
def get_traces():
    """获取分布式调用链数据。

    查询参数：
        start_time: 起始时间戳（毫秒）
        end_time: 结束时间戳（毫秒）
        trace_id: 指定 trace ID（可选）
        limit: 返回条数上限（默认 1000）
    """
    try:
        data = observability.get_traces(
            start_time=request.args.get("start_time", type=int),
            end_time=request.args.get("end_time", type=int),
            trace_id=request.args.get("trace_id"),
            limit=request.args.get("limit", 1000, type=int),
        )
        return jsonify({"code": 200, "message": "success", "data": data})
    except Exception as e:
        logger.error("获取调用链失败: %s", e)
        return jsonify({"code": 500, "message": f"获取调用链失败: {e}", "data": None}), 500


@observability_bp.route("/metrics", methods=["GET"])
def get_metrics():
    """获取监控指标时序数据。

    查询参数：
        start_time: 起始时间戳（毫秒）
        end_time: 结束时间戳（毫秒）
        metric_names: 逗号分隔的指标名（如 "cpu_usage,memory_usage"）
        service_name: 服务名（如 "ts-travel-service"，自动构建 Coroot app_id）
        app_id: 完整 Coroot 应用 ID（兼容旧参数，优先级低于 service_name）
        interval: 采样间隔（秒，可选）
    """
    try:
        # 支持 service_name 参数，自动构建完整 Coroot app_id
        app_id = request.args.get("app_id")
        service_name = request.args.get("service_name")
        if service_name:
            resource_type = "StatefulSet" if service_name == "nacos" else "Deployment"
            app_id = (
                f"{Config.COROOT_PROJECT_ID}:{Config.TARGET_NAMESPACE}"
                f":{resource_type}:{service_name}"
            )

        data = observability.get_metrics(
            start_time=request.args.get("start_time", type=int),
            end_time=request.args.get("end_time", type=int),
            metric_names=request.args.get("metric_names"),
            app_id=app_id,
            interval=request.args.get("interval", type=int),
        )
        return jsonify({"code": 200, "message": "success", "data": data})
    except Exception as e:
        logger.error("获取指标数据失败: %s", e)
        return jsonify({"code": 500, "message": f"获取指标数据失败: {e}", "data": None}), 500


@observability_bp.route("/node_metrics", methods=["GET"])
def get_node_metrics():
    """获取节点级监控指标时序数据。

    查询参数：
        start_time: 起始时间戳（毫秒）
        end_time: 结束时间戳（毫秒）
        metric_names: 逗号分隔的指标名（如 "disk_read_bytes,disk_write_bytes"）
        node_name: 节点名称（如 "tcse-v100-02"）
        interval: 采样间隔（秒，可选）
    """
    try:
        data = observability.get_node_metrics(
            start_time=request.args.get("start_time", type=int),
            end_time=request.args.get("end_time", type=int),
            metric_names=request.args.get("metric_names"),
            node_name=request.args.get("node_name"),
            interval=request.args.get("interval", type=int),
        )
        return jsonify({"code": 200, "message": "success", "data": data})
    except Exception as e:
        logger.error("获取节点指标数据失败: %s", e)
        return jsonify({"code": 500, "message": f"获取节点指标数据失败: {e}", "data": None}), 500


@observability_bp.route("/logs", methods=["GET"])
def get_logs():
    """获取结构化日志数据。

    查询参数：
        start_time: 起始时间戳（毫秒）
        end_time: 结束时间戳（毫秒）
        anomalous_only: 是否只返回异常日志（true/false，默认 false）
        limit: 返回条数上限（默认 500）
    """
    anomalous_str = request.args.get("anomalous_only", "false")
    anomalous = anomalous_str.lower() in ("true", "1", "yes")
    try:
        data = observability.get_logs(
            start_time=request.args.get("start_time", type=int),
            end_time=request.args.get("end_time", type=int),
            anomalous_only=anomalous,
            limit=request.args.get("limit", 500, type=int),
        )
        return jsonify({"code": 200, "message": "success", "data": data})
    except Exception as e:
        logger.error("获取日志失败: %s", e)
        return jsonify({"code": 500, "message": f"获取日志失败: {e}", "data": None}), 500


@observability_bp.route("/topology", methods=["GET"])
def get_topology():
    """获取部署拓扑关系。

    返回服务列表、节点列表、服务间依赖关系。
    """
    try:
        data = observability.get_topology()
        return jsonify({"code": 200, "message": "success", "data": data})
    except Exception as e:
        logger.error("获取拓扑失败: %s", e)
        return jsonify({"code": 500, "message": f"获取拓扑失败: {e}", "data": None}), 500


@observability_bp.route("/entities", methods=["GET"])
def get_entities():
    """获取实体列表。

    查询参数：
        type: 实体类型过滤（service/pod/node，可选，默认返回全部）
    """
    try:
        data = observability.get_entities(
            entity_type=request.args.get("type"),
        )
        return jsonify({"code": 200, "message": "success", "data": data})
    except Exception as e:
        logger.error("获取实体列表失败: %s", e)
        return jsonify({"code": 500, "message": f"获取实体列表失败: {e}", "data": None}), 500


@observability_bp.route("/fault/status", methods=["GET"])
def get_fault_status():
    """获取当前故障状态。

    返回所有活跃的故障锁定信息，包括关联的执行记录和计划详情。
    """
    try:
        data = observability.get_fault_status()
        return jsonify({"code": 200, "message": "success", "data": data})
    except Exception as e:
        logger.error("获取故障状态失败: %s", e)
        return jsonify({"code": 500, "message": f"获取故障状态失败: {e}", "data": None}), 500
