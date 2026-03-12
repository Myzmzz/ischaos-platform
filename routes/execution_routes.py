"""演练执行 API 路由。"""

from flask import Blueprint, jsonify

execution_bp = Blueprint("executions", __name__)


@execution_bp.route("/executions", methods=["GET"])
def list_executions():
    """获取所有执行记录。"""
    # TODO: Step 4 实现
    return jsonify({"code": 200, "message": "success", "data": []})
