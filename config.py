"""ISChaos-sub 平台配置管理 — 从环境变量读取，提供合理默认值。"""

import os


class Config:
    """应用配置，所有外部依赖地址通过环境变量注入。"""

    # Flask
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ischaos-dev-secret-key")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1", "yes")

    # SQLite 数据库路径
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/ischaos.db")

    # Chaos Mesh Dashboard
    CHAOS_MESH_URL: str = os.getenv("CHAOS_MESH_URL", "http://116.63.51.45:30854")

    # Coroot 观测平台
    COROOT_URL: str = os.getenv("COROOT_URL", "http://116.63.51.45:30800")
    COROOT_USERNAME: str = os.getenv("COROOT_USERNAME", "admin")
    COROOT_PASSWORD: str = os.getenv("COROOT_PASSWORD", "123456")
    COROOT_PROJECT_ID: str = os.getenv("COROOT_PROJECT_ID", "9auios5b")

    # Kubernetes 配置
    KUBECONFIG_PATH: str = os.getenv(
        "KUBECONFIG", os.path.expanduser("~/.kube/coroot-config")
    )

    # 故障注入目标命名空间
    TARGET_NAMESPACE: str = os.getenv("TARGET_NAMESPACE", "train-ticket")
