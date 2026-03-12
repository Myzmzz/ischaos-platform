"""演练执行 API 路由。

提供执行记录的查询、实时状态刷新和停止操作。
"""

import logging
from datetime import datetime, timezone

from flask import Blueprint, jsonify

from models import execution as execution_model
from models import plan as plan_model
from services.chaos_client import (
    get_workflow_status,
    stop_workflow,
    ChaosClientError,
)
from services.fault_lock import release_lock

logger = logging.getLogger(__name__)

execution_bp = Blueprint("executions", __name__)


@execution_bp.route("/executions", methods=["GET"])
def list_executions():
    """获取所有执行记录。"""
    executions = execution_model.list_all()
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
    """从 Chaos Mesh 查询执行的实时状态。

    返回本地执行记录 + Chaos Mesh 端的 Workflow 状态。
    """
    execution = execution_model.get_by_id(execution_id)
    if execution is None:
        return jsonify({"code": 404, "message": "执行记录不存在", "data": None}), 404

    workflow_name = execution["workflow_name"]
    if not workflow_name:
        return jsonify({
            "code": 200,
            "message": "success",
            "data": {"execution": execution, "chaos_status": None},
        })

    # 查询 Chaos Mesh 实时状态
    try:
        chaos_status = get_workflow_status(workflow_name)
    except ChaosClientError as e:
        logger.warning("查询 Workflow 状态失败: %s", e)
        chaos_status = {"error": str(e)}

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
