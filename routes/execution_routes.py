"""演练执行 API 路由。

提供执行记录的查询、实时状态刷新、停止操作和故障指标查询。
"""

import logging
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from models import execution as execution_model
from models import plan as plan_model
from services.chaos_client import (
    get_workflow_status,
    stop_workflow,
    ChaosClientError,
)
from services.execution_manager import sync_execution_status
from services.fault_lock import release_lock
from services.fault_metrics import get_fault_metrics

logger = logging.getLogger(__name__)

execution_bp = Blueprint("executions", __name__)


@execution_bp.route("/executions", methods=["GET"])
def list_executions():
    """获取所有执行记录，附带关联计划信息。"""
    executions = execution_model.list_all()
    # 批量补充计划信息（名称、故障类型、目标服务）
    for ex in executions:
        plan = plan_model.get_by_id(ex["plan_id"])
        if plan:
            ex["plan_name"] = plan["name"]
            ex["fault_type"] = plan["fault_type"]
            ex["target_service"] = plan["target_service"]
        else:
            ex["plan_name"] = f"计划#{ex['plan_id']}(已删除)"
            ex["fault_type"] = ""
            ex["target_service"] = ""
    return jsonify({"code": 200, "message": "success", "data": executions})


@execution_bp.route("/executions/<int:execution_id>", methods=["GET"])
def get_execution(execution_id: int):
    """获取单条执行记录详情。"""
    execution = execution_model.get_by_id(execution_id)
    if execution is None:
        return jsonify({"code": 404, "message": "执行记录不存在", "data": None}), 404
    return jsonify({"code": 200, "message": "success", "data": execution})


@execution_bp.route("/executions/<int:execution_id>/status", methods=["GET"])
def get_execution_status(execution_id: int):
    """查询执行的实时状态并同步更新。

    通过 execution_manager.sync_execution_status() 完成：
    1. 查询 Chaos Mesh Workflow 实时状态
    2. 判断完成/超时，自动更新本地记录
    3. 完成或超时时自动释放故障锁

    返回最新的本地执行记录 + Chaos Mesh 原始状态。
    """
    execution, chaos_status = sync_execution_status(execution_id)
    if execution is None:
        return jsonify({"code": 404, "message": "执行记录不存在", "data": None}), 404

    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "execution": execution,
            "chaos_status": chaos_status,
        },
    })


@execution_bp.route("/executions/<int:execution_id>/stop", methods=["PUT"])
def stop_execution(execution_id: int):
    """停止正在运行的演练执行。

    流程：
    1. 校验执行记录存在且状态为 running
    2. 调用 Chaos Mesh 停止 Workflow
    3. 释放服务故障互斥锁
    4. 更新执行状态为 completed
    """
    # 1. 校验
    execution = execution_model.get_by_id(execution_id)
    if execution is None:
        return jsonify({"code": 404, "message": "执行记录不存在", "data": None}), 404
    if execution["status"] != "running":
        return jsonify({
            "code": 400,
            "message": f"执行状态为 '{execution['status']}'，只有 'running' 状态才能停止",
            "data": None,
        }), 400

    workflow_name = execution["workflow_name"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 2. 停止 Chaos Mesh Workflow
    try:
        stop_resp = stop_workflow(workflow_name)
        logger.info("Workflow 已停止: %s, 响应: %s", workflow_name, stop_resp)
    except ChaosClientError as e:
        logger.error("停止 Workflow 失败: %s", e)
        return jsonify({
            "code": 502,
            "message": f"Chaos Mesh API 调用失败: {e}",
            "data": None,
        }), 502

    # 3. 释放故障锁 — 需要从计划中获取 target_service
    plan = plan_model.get_by_id(execution["plan_id"])
    if plan:
        release_lock(plan["target_service"])

    # 4. 更新状态
    execution_model.update_status(
        execution_id, "completed",
        finished_at=now,
        fault_end_at=now,
    )

    execution = execution_model.get_by_id(execution_id)
    return jsonify({"code": 200, "message": "success", "data": execution})


@execution_bp.route("/executions/<int:execution_id>", methods=["DELETE"])
def delete_execution(execution_id: int):
    """删除演练执行记录。

    运行中的执行不允许直接删除，需先停止。
    删除时同步释放可能残留的故障锁。
    """
    execution = execution_model.get_by_id(execution_id)
    if execution is None:
        return jsonify({"code": 404, "message": "执行记录不存在", "data": None}), 404

    if execution["status"] == "running":
        return jsonify({
            "code": 400,
            "message": "运行中的执行不能删除，请先停止",
            "data": None,
        }), 400

    # 释放可能残留的故障锁
    plan = plan_model.get_by_id(execution["plan_id"])
    if plan:
        release_lock(plan["target_service"])

    execution_model.delete_by_id(execution_id)
    logger.info("已删除执行记录 #%d", execution_id)
    return jsonify({"code": 200, "message": "success", "data": None})


# ── 故障指标 ─────────────────────────────────────────────────


@execution_bp.route("/executions/<int:execution_id>/metrics", methods=["GET"])
def get_execution_metrics(execution_id: int):
    """获取执行对应的故障验证指标数据。

    从 Coroot 可观测平台获取该执行故障类型对应的时序指标，
    用于 ECharts 图表展示。

    查询参数（可选）：
        from: 起始时间戳（毫秒），默认最近 1 小时
        to: 结束时间戳（毫秒），默认当前时间
    """
    # 获取执行记录
    execution = execution_model.get_by_id(execution_id)
    if execution is None:
        return jsonify({"code": 404, "message": "执行记录不存在", "data": None}), 404

    # 获取关联的计划，拿到 fault_type 和 target_service
    plan = plan_model.get_by_id(execution["plan_id"])
    if plan is None:
        return jsonify({"code": 404, "message": "关联计划不存在", "data": None}), 404

    fault_type = plan["fault_type"]
    target_service = plan["target_service"]

    # 解析时间范围参数
    from_ts = request.args.get("from", type=int)
    to_ts = request.args.get("to", type=int)

    # 自动计算时间范围：故障注入前 10 分钟 ~ 故障恢复后 10 分钟
    ten_min_ms = 10 * 60 * 1000

    if from_ts is None and execution.get("fault_inject_at"):
        try:
            inject_dt = datetime.fromisoformat(
                execution["fault_inject_at"].replace("Z", "+00:00")
            )
            inject_ms = int(inject_dt.timestamp() * 1000)
            from_ts = inject_ms - ten_min_ms
        except (ValueError, AttributeError):
            pass

    if to_ts is None and execution.get("fault_end_at"):
        try:
            end_dt = datetime.fromisoformat(
                execution["fault_end_at"].replace("Z", "+00:00")
            )
            end_ms = int(end_dt.timestamp() * 1000)
            to_ts = end_ms + ten_min_ms
        except (ValueError, AttributeError):
            pass

    # 如果故障尚未恢复，to_ts 取当前时间
    if to_ts is None and from_ts is not None:
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        to_ts = now_ms

    # 获取故障参数中的 node address（物理机故障使用）
    fault_params = plan.get("fault_params", {})
    node_name = None
    if fault_type in ("node_cpu", "node_mem"):
        node_name = fault_params.get("address", "").split("/")[-1] or None

    # 查询指标数据
    try:
        metrics = get_fault_metrics(
            fault_type=fault_type,
            target_service=target_service,
            from_ts=from_ts,
            to_ts=to_ts,
            node_name=node_name,
        )
    except Exception as e:
        logger.error("获取故障指标失败: %s", e)
        return jsonify({
            "code": 500,
            "message": f"获取指标失败: {e}",
            "data": None,
        }), 500

    return jsonify({"code": 200, "message": "success", "data": metrics})
