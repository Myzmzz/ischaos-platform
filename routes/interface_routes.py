"""接口相关 API 路由。"""

from flask import Blueprint, jsonify

from models.interface import list_all, get_by_id

interface_bp = Blueprint("interfaces", __name__)


@interface_bp.route("/interfaces", methods=["GET"])
def list_interfaces():
    """获取所有接口列表（概览信息，不含完整拓扑）。"""
    interfaces = list_all()
    return jsonify({"code": 200, "message": "success", "data": interfaces})


@interface_bp.route("/interfaces/<int:interface_id>", methods=["GET"])
def get_interface(interface_id: int):
    """获取单个接口详情（含完整拓扑）。"""
    interface = get_by_id(interface_id)
    if interface is None:
        return jsonify({"code": 404, "message": "接口不存在", "data": None}), 404
    return jsonify({"code": 200, "message": "success", "data": interface})
