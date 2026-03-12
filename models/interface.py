"""接口拓扑表 CRUD 操作。"""

import json
from typing import Any, Optional

from models.database import get_db


def list_all() -> list[dict[str, Any]]:
    """查询所有接口，返回列表概览（不含完整拓扑 JSON）。"""
    db = get_db()
    rows = db.execute(
        """SELECT id, name, url, span_name, method, total_requests,
                  topology_json, created_at
           FROM interface_topology
           ORDER BY id"""
    ).fetchall()

    result = []
    for row in rows:
        topology = json.loads(row["topology_json"])
        # 统计服务节点数量（type == 'service'）
        service_count = sum(
            1 for node in topology.get("nodes", [])
            if node.get("type") == "service"
        )
        result.append({
            "id": row["id"],
            "name": row["name"],
            "url": row["url"],
            "span_name": row["span_name"],
            "method": row["method"],
            "total_requests": row["total_requests"],
            "service_count": service_count,
            "edge_count": len(topology.get("edges", [])),
            "created_at": row["created_at"],
        })

    return result


def get_by_id(interface_id: int) -> Optional[dict[str, Any]]:
    """根据 ID 查询单个接口（含完整拓扑）。"""
    db = get_db()
    row = db.execute(
        """SELECT id, name, url, span_name, method, total_requests,
                  topology_json, created_at
           FROM interface_topology
           WHERE id = ?""",
        (interface_id,),
    ).fetchone()

    if row is None:
        return None

    topology = json.loads(row["topology_json"])
    return {
        "id": row["id"],
        "name": row["name"],
        "url": row["url"],
        "span_name": row["span_name"],
        "method": row["method"],
        "total_requests": row["total_requests"],
        "topology": topology,
        "created_at": row["created_at"],
    }
