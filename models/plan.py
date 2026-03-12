"""演练计划表 CRUD 操作。"""

import json
from typing import Any, Optional

from models.database import get_db


def _row_to_dict(row) -> dict[str, Any]:
    """将数据库行转换为字典，解析 JSON 字段。"""
    return {
        "id": row["id"],
        "name": row["name"],
        "interface_id": row["interface_id"],
        "fault_type": row["fault_type"],
        "target_service": row["target_service"],
        "fault_params": json.loads(row["fault_params"]),
        "duration": row["duration"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def list_all() -> list[dict[str, Any]]:
    """查询所有演练计划，按创建时间倒序。"""
    db = get_db()
    rows = db.execute(
        """SELECT id, name, interface_id, fault_type, target_service,
                  fault_params, duration, status, created_at, updated_at
           FROM drill_plan
           ORDER BY created_at DESC"""
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def get_by_id(plan_id: int) -> Optional[dict[str, Any]]:
    """根据 ID 查询单个演练计划。"""
    db = get_db()
    row = db.execute(
        """SELECT id, name, interface_id, fault_type, target_service,
                  fault_params, duration, status, created_at, updated_at
           FROM drill_plan
           WHERE id = ?""",
        (plan_id,),
    ).fetchone()

    if row is None:
        return None
    return _row_to_dict(row)


def create(data: dict[str, Any]) -> dict[str, Any]:
    """创建新的演练计划。

    Args:
        data: 计划数据，需包含 name, interface_id, fault_type,
              target_service, fault_params, duration, status

    Returns:
        新创建的计划记录
    """
    db = get_db()
    fault_params = data.get("fault_params", {})
    if isinstance(fault_params, dict):
        fault_params = json.dumps(fault_params, ensure_ascii=False)

    cursor = db.execute(
        """INSERT INTO drill_plan
               (name, interface_id, fault_type, target_service,
                fault_params, duration, status)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            data["name"],
            data["interface_id"],
            data["fault_type"],
            data["target_service"],
            fault_params,
            data.get("duration", "30s"),
            data.get("status", "draft"),
        ),
    )
    db.commit()
    return get_by_id(cursor.lastrowid)


def update(plan_id: int, data: dict[str, Any]) -> Optional[dict[str, Any]]:
    """更新演练计划。

    Args:
        plan_id: 计划 ID
        data: 要更新的字段

    Returns:
        更新后的计划记录，不存在返回 None
    """
    existing = get_by_id(plan_id)
    if existing is None:
        return None

    # 构建动态 UPDATE 语句
    allowed_fields = {
        "name", "interface_id", "fault_type", "target_service",
        "fault_params", "duration", "status",
    }
    updates = []
    values = []
    for field in allowed_fields:
        if field in data:
            value = data[field]
            if field == "fault_params" and isinstance(value, dict):
                value = json.dumps(value, ensure_ascii=False)
            updates.append(f"{field} = ?")
            values.append(value)

    if not updates:
        return existing

    # 自动更新 updated_at
    updates.append("updated_at = datetime('now')")
    values.append(plan_id)

    db = get_db()
    db.execute(
        f"UPDATE drill_plan SET {', '.join(updates)} WHERE id = ?",
        values,
    )
    db.commit()
    return get_by_id(plan_id)


def delete(plan_id: int) -> bool:
    """删除演练计划。

    Args:
        plan_id: 计划 ID

    Returns:
        True 删除成功，False 记录不存在
    """
    db = get_db()
    cursor = db.execute("DELETE FROM drill_plan WHERE id = ?", (plan_id,))
    db.commit()
    return cursor.rowcount > 0
