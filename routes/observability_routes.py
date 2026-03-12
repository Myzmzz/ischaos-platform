"""观测数据 API 路由。"""

from flask import Blueprint, jsonify

observability_bp = Blueprint("observability", __name__)


@observability_bp.route("/traces", methods=["GET"])
def get_traces():
    """获取调用链数据。"""
    # TODO: Step 6 实现
    return jsonify({"code": 200, "message": "success", "data": []})
