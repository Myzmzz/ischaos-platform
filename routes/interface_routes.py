"""接口相关 API 路由。"""

from flask import Blueprint, jsonify

interface_bp = Blueprint("interfaces", __name__)


@interface_bp.route("/interfaces", methods=["GET"])
def list_interfaces():
    """获取所有接口列表。"""
    # TODO: Step 1 实现数据库查询
    return jsonify({"code": 200, "message": "success", "data": []})
