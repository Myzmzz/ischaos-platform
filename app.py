"""ISChaos-sub 第二代混沌工程演练平台 — Flask 主入口。"""

import logging
import os
import time
from logging.handlers import RotatingFileHandler

from flask import Flask, request, g

from config import Config
from models.database import init_schema, close_db
from routes.page_routes import page_bp
from routes.interface_routes import interface_bp
from routes.plan_routes import plan_bp
from routes.execution_routes import execution_bp
from routes.observability_routes import observability_bp


def _setup_logging(app: Flask) -> None:
    """配置全局日志：同时输出到文件和控制台。

    日志文件：logs/ischaos.log，按大小轮转（10MB × 5 个备份）。
    """
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "ischaos.log")

    # 日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 文件 handler — 10MB 轮转，保留 5 个备份
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    # 配置 root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    # 避免重复添加 handler（debug 模式 Flask 会 reload）
    if not root_logger.handlers:
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    # Flask 自带 logger 也用同样的 handler
    app.logger.handlers = []
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG)

    # 降低第三方库的日志噪音
    logging.getLogger("werkzeug").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def _register_request_logging(app: Flask) -> None:
    """注册 Flask 请求/响应日志钩子。

    记录每个 API 请求的方法、URL、参数、请求体，
    以及响应状态码和耗时。
    """
    req_logger = logging.getLogger("ischaos.request")

    @app.before_request
    def log_request_info():
        """请求开始时记录详细信息。"""
        g.request_start_time = time.time()

        # 只记录 API 请求，跳过静态资源
        if request.path.startswith("/static"):
            return

        parts = [
            f">>> {request.method} {request.url}",
            f"    Remote: {request.remote_addr}",
        ]

        # 查询参数
        if request.args:
            parts.append(f"    Query: {dict(request.args)}")

        # 请求体
        if request.content_type and "json" in request.content_type:
            body = request.get_json(silent=True)
            if body is not None:
                parts.append(f"    Body: {body}")
        elif request.data:
            # 非 JSON 的请求体，截断过长内容
            body_str = request.data.decode("utf-8", errors="replace")[:2000]
            parts.append(f"    Body: {body_str}")

        req_logger.debug("\n".join(parts))

    @app.after_request
    def log_response_info(response):
        """请求结束时记录响应概要。"""
        if request.path.startswith("/static"):
            return response

        duration = time.time() - getattr(g, "request_start_time", time.time())
        duration_ms = round(duration * 1000, 1)

        # 对 JSON 响应记录响应体（截断到 2000 字符避免日志过大）
        resp_body = ""
        if response.content_type and "json" in response.content_type:
            resp_data = response.get_data(as_text=True)
            if len(resp_data) > 2000:
                resp_body = resp_data[:2000] + "...(truncated)"
            else:
                resp_body = resp_data

        parts = [
            f"<<< {response.status_code} {request.method} {request.path} [{duration_ms}ms]",
        ]
        if resp_body:
            parts.append(f"    Response: {resp_body}")

        req_logger.debug("\n".join(parts))
        return response


def create_app() -> Flask:
    """创建并配置 Flask 应用实例。"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # 配置日志
    _setup_logging(app)
    _register_request_logging(app)

    # 注册 Blueprint
    app.register_blueprint(page_bp)
    app.register_blueprint(interface_bp, url_prefix="/api")
    app.register_blueprint(plan_bp, url_prefix="/api")
    app.register_blueprint(execution_bp, url_prefix="/api")
    app.register_blueprint(observability_bp, url_prefix="/api/v1")

    # 初始化数据库 schema（建表，幂等操作）
    init_schema()

    # 每个请求结束后关闭数据库连接
    app.teardown_appcontext(close_db)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
