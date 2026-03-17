"""演练计划 API 路由。

提供计划的 CRUD 操作及执行触发接口。
POST /api/plans/<id>/execute 是核心：校验 → 加锁 → 构建 Workflow → 提交 Chaos Mesh。
"""

import logging
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from models import plan as plan_model
from models import execution as execution_model
from services.workflow_builder import build_workflow
from services.chaos_client import create_workflow, ChaosClientError
from services.fault_lock import acquire_lock, release_lock

logger = logging.getLogger(__name__)

plan_bp = Blueprint("plans", __name__)


# ── CRUD ─────────────────────────────────────────────────────


@plan_bp.route("/plans", methods=["GET"])
def list_plans():
    """获取所有演练计划。"""
    plans = plan_model.list_all()
    return jsonify({"code": 200, "message": "success", "data": plans})


@plan_bp.route("/plans/<int:plan_id>", methods=["GET"])
def get_plan(plan_id: int):
    """获取单个演练计划详情。"""
    plan = plan_model.get_by_id(plan_id)
    if plan is None:
        return jsonify({"code": 404, "message": "计划不存在", "data": None}), 404
    return jsonify({"code": 200, "message": "success", "data": plan})


@plan_bp.route("/plans", methods=["POST"])
def create_plan():
    """创建演练计划。

    请求体 JSON 字段：
        - name: 计划名称
        - interface_id: 关联接口 ID
        - fault_type: 故障类型
        - target_service: 目标服务
        - fault_params: 故障参数（对象）
        - duration: 持续时间（如 "30s"）
        - status: 状态（draft/ready/archived，默认 draft）
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"code": 400, "message": "请求体不能为空", "data": None}), 400

    # 校验必填字段
    required = ["name", "interface_id", "fault_type", "target_service"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({
            "code": 400,
            "message": f"缺少必填字段: {', '.join(missing)}",
            "data": None,
        }), 400

    plan = plan_model.create(data)
    return jsonify({"code": 200, "message": "success", "data": plan})


@plan_bp.route("/plans/<int:plan_id>", methods=["PUT"])
def update_plan(plan_id: int):
    """更新演练计划。"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"code": 400, "message": "请求体不能为空", "data": None}), 400

    plan = plan_model.update(plan_id, data)
    if plan is None:
        return jsonify({"code": 404, "message": "计划不存在", "data": None}), 404
    return jsonify({"code": 200, "message": "success", "data": plan})


@plan_bp.route("/plans/batch-delete", methods=["POST"])
def batch_delete_plans():
    """批量删除演练计划。

    请求体 JSON：{"ids": [1, 2, 3]}
    有活跃执行记录的计划会被跳过，返回跳过原因。
    """
    data = request.get_json(silent=True)
    if not data or not isinstance(data.get("ids"), list):
        return jsonify({"code": 400, "message": "请提供 ids 列表", "data": None}), 400

    plan_ids = data["ids"]
    if not plan_ids:
        return jsonify({"code": 400, "message": "ids 列表不能为空", "data": None}), 400

    result = plan_model.delete_batch(plan_ids)
    return jsonify({"code": 200, "message": "success", "data": result})


@plan_bp.route("/plans/<int:plan_id>", methods=["DELETE"])
def delete_plan(plan_id: int):
    """删除演练计划（级联删除关联执行记录）。

    如果该计划存在活跃（running/pending）的执行记录，返回 409。
    """
    result = plan_model.delete(plan_id)
    if result["ok"]:
        return jsonify({"code": 200, "message": "success", "data": None})
    if result["reason"] == "not_found":
        return jsonify({"code": 404, "message": "计划不存在", "data": None}), 404
    if result["reason"] == "has_active":
        return jsonify({
            "code": 409,
            "message": f"该计划存在 {result['active_count']} 个活跃执行记录，无法删除",
            "data": None,
        }), 409
    return jsonify({"code": 500, "message": "未知错误", "data": None}), 500


@plan_bp.route("/plans/<int:plan_id>/workflow", methods=["GET"])
def preview_workflow(plan_id: int):
    """预览计划对应的 Chaos Mesh Workflow JSON（不实际提交）。"""
    plan = plan_model.get_by_id(plan_id)
    if plan is None:
        return jsonify({"code": 404, "message": "计划不存在", "data": None}), 404

    try:
        workflow_name, workflow_json = build_workflow(plan)
    except ValueError as e:
        return jsonify({"code": 400, "message": str(e), "data": None}), 400

    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "workflow_name": workflow_name,
            "workflow_json": workflow_json,
        },
    })


# ── 执行触发 ─────────────────────────────────────────────────


@plan_bp.route("/plans/<int:plan_id>/execute", methods=["POST"])
def execute_plan(plan_id: int):
    """触发执行演练计划。

    流程：
    1. 校验计划存在且 status='ready'
    2. 构建 Chaos Mesh Workflow JSON
    3. 创建执行记录
    4. 获取服务故障互斥锁
    5. 提交 Workflow 到 Chaos Mesh
    6. 更新执行状态为 running
    """
    # 1. 校验计划
    plan = plan_model.get_by_id(plan_id)
    if plan is None:
        return jsonify({"code": 404, "message": "计划不存在", "data": None}), 404
    if plan["status"] != "ready":
        return jsonify({
            "code": 400,
            "message": f"计划状态为 '{plan['status']}'，只有 'ready' 状态的计划才能执行",
            "data": None,
        }), 400

    # 2. 构建 Workflow JSON
    try:
        workflow_name, workflow_json = build_workflow(plan)
    except ValueError as e:
        return jsonify({"code": 400, "message": str(e), "data": None}), 400

    # 3. 创建执行记录
    execution = execution_model.create(plan_id, workflow_name)
    execution_id = execution["id"]

    # 4. 获取故障互斥锁
    target_service = plan["target_service"]
    if not acquire_lock(target_service, execution_id):
        # 锁已被占用，标记执行失败
        execution_model.update_status(
            execution_id, "failed",
            error_message=f"服务 '{target_service}' 已有活跃故障，请等待完成后再试",
        )
        return jsonify({
            "code": 409,
            "message": f"服务 '{target_service}' 已有活跃故障",
            "data": None,
        }), 409

    # 5. 提交到 Chaos Mesh
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        chaos_resp = create_workflow(workflow_json)
        logger.info("Workflow 创建成功: %s, 响应: %s", workflow_name, chaos_resp)
    except ChaosClientError as e:
        # 提交失败 → 释放锁、标记失败
        logger.error("Workflow 创建失败: %s", e)
        release_lock(target_service)
        execution_model.update_status(
            execution_id, "failed",
            error_message=str(e),
        )
        return jsonify({
            "code": 502,
            "message": f"Chaos Mesh API 调用失败: {e}",
            "data": None,
        }), 502

    # 6. 更新状态为 running
    execution_model.update_status(
        execution_id, "running",
        started_at=now,
        fault_inject_at=now,
    )

    # 重新获取完整的执行记录
    execution = execution_model.get_by_id(execution_id)
    return jsonify({"code": 200, "message": "success", "data": execution})
