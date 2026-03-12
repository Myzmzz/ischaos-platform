"""页面渲染路由 — 返回 Jinja2 模板。"""

from flask import Blueprint, render_template

page_bp = Blueprint("pages", __name__)


@page_bp.route("/")
def index():
    """首页 — 平台概览。"""
    return render_template("base.html", page_title="首页", content="")


@page_bp.route("/interfaces")
def interfaces():
    """接口列表页。"""
    return render_template("interfaces.html", page_title="接口列表")


@page_bp.route("/topology/<int:interface_id>")
def topology(interface_id: int):
    """链路拓扑详情页。"""
    return render_template("topology.html", page_title="链路拓扑", interface_id=interface_id)


@page_bp.route("/plans")
def plans():
    """演练计划列表页。"""
    return render_template("plans.html", page_title="演练计划")


@page_bp.route("/executions")
def executions():
    """演练记录列表页。"""
    return render_template("executions.html", page_title="演练记录")


@page_bp.route("/executions/<int:execution_id>")
def execution_detail(execution_id: int):
    """执行详情页。"""
    return render_template("execution.html", page_title="执行详情", execution_id=execution_id)
