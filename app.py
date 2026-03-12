"""ISChaos 混沌工程演练平台 — Flask 主入口。"""

from flask import Flask

from config import Config
from models.database import init_schema, close_db
from routes.page_routes import page_bp
from routes.interface_routes import interface_bp
from routes.plan_routes import plan_bp
from routes.execution_routes import execution_bp
from routes.observability_routes import observability_bp


def create_app() -> Flask:
    """创建并配置 Flask 应用实例。"""
    app = Flask(__name__)
    app.config.from_object(Config)

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
