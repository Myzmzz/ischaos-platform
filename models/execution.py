"""演练执行记录表 CRUD 操作。"""

import json
from typing import Any, Optional

from models.database import get_db


def _row_to_dict(row) -> dict[str, Any]:
    """将数据库行转换为字典，解析 JSON 字段。"""
    return {
        "id": row["id"],
        "plan_id": row["plan_id"],
        "workflow_name": row["workflow_name"],
        "status": row["status"],
        "started_at": row["started_at"],
        "finished_at": row["finished_at"],
        "fault_inject_at": row["fault_inject_at"],
        "fault_end_at": row["fault_end_at"],
        "result_json": json.loads(row["result_json"]),
        "error_message": row["error_message"],
        "created_at": row["created_at"],
    }


def create(plan_id: int, workflow_name: str) -> dict[str, Any]:
    """创建新的执行记录，初始状态为 pending。

    Args:
        plan_id: 关联的演练计划 ID
        workflow_name: Chaos Mesh Workflow 名称

    Returns:
        新创建的执行记录
    """
    db = get_db()
    cursor = db.execute(
        """INSERT INTO drill_execution (plan_id, workflow_name, status)
           VALUES (?, ?, 'pending')""",
        (plan_id, workflow_name),
    )
    db.commit()
    return get_by_id(cursor.lastrowid)


def get_by_id(execution_id: int) -> Optional[dict[str, Any]]:
    """根据 ID 查询单条执行记录。"""
    db = get_db()
    row = db.execute(
        """SELECT id, plan_id, workflow_name, status,
                  started_at, finished_at, fault_inject_at, fault_end_at,
                  result_json, error_message, created_at
           FROM drill_execution
           WHERE id = ?""",
        (execution_id,),
    ).fetchone()

    if row is None:
        return None
    return _row_to_dict(row)


def update_status(execution_id: int, status: str, **kwargs: Any) -> None:
    """更新执行记录状态及相关字段。

    Args:
        execution_id: 执行记录 ID
        status: 新状态（pending/running/collecting/completed/failed）
        **kwargs: 可选更新字段，支持:
            - started_at: 开始时间
            - finished_at: 结束时间
            - fault_inject_at: 故障注入时间
            - fault_end_at: 故障结束时间
            - error_message: 错误信息
            - result_json: 结果数据（字典或 JSON 字符串）
    """
    allowed_fields = {
        "started_at", "finished_at", "fault_inject_at",
        "fault_end_at", "error_message", "result_json",
    }

    updates = ["status = ?"]
    values: list[Any] = [status]

    for field in allowed_fields:
        if field in kwargs:
            value = kwargs[field]
            if field == "result_json" and isinstance(value, dict):
                value = json.dumps(value, ensure_ascii=False)
            updates.append(f"{field} = ?")
            values.append(value)

    values.append(execution_id)

    db = get_db()
    db.execute(
        f"UPDATE drill_execution SET {', '.join(updates)} WHERE id = ?",
        values,
    )
    db.commit()


def delete_by_id(execution_id: int) -> None:
    """根据 ID 删除执行记录。"""
    db = get_db()
    db.execute("DELETE FROM drill_execution WHERE id = ?", (execution_id,))
    db.commit()


def list_all() -> list[dict[str, Any]]:
    """查询所有执行记录，按创建时间倒序。"""
    db = get_db()
    rows = db.execute(
        """SELECT id, plan_id, workflow_name, status,
                  started_at, finished_at, fault_inject_at, fault_end_at,
                  result_json, error_message, created_at
           FROM drill_execution
           ORDER BY created_at DESC"""
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def list_by_plan(plan_id: int) -> list[dict[str, Any]]:
    """查询指定计划的所有执行记录。"""
    db = get_db()
    rows = db.execute(
        """SELECT id, plan_id, workflow_name, status,
                  started_at, finished_at, fault_inject_at, fault_end_at,
                  result_json, error_message, created_at
           FROM drill_execution
           WHERE plan_id = ?
           ORDER BY created_at DESC""",
        (plan_id,),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]
