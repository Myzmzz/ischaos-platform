#!/bin/sh
# 容器启动入口：先幂等导入拓扑数据，再启动 gunicorn。
# 注意：init_db.py 会 DELETE 再 INSERT interface_topology 表，
# 单副本场景安全；多副本部署请改用 init container 或 Job。
set -e

REPORT_PATH="${TOPOLOGY_REPORT_PATH:-/app/docs/topology_report.md}"

if [ -f "$REPORT_PATH" ]; then
    echo "[entrypoint] importing topology from $REPORT_PATH ..."
    python /app/init_db.py "$REPORT_PATH"
else
    echo "[entrypoint] WARN: $REPORT_PATH not found, skipping init_db"
fi

echo "[entrypoint] starting gunicorn ..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 600 "app:create_app()"
