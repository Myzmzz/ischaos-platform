"""演练计划 API 路由。"""

from flask import Blueprint, jsonify

plan_bp = Blueprint("plans", __name__)


@plan_bp.route("/plans", methods=["GET"])
def list_plans():
    """获取所有演练计划。"""
    # TODO: Step 3 实现
    return jsonify({"code": 200, "message": "success", "data": []})
