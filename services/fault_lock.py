"""服务故障互斥锁。

确保同一服务在同一时间只允许存在一个活跃故障。
基于 service_fault_lock 表的 UNIQUE(service_name) 约束实现互斥。
"""

import sqlite3
from typing import Any, Optional

from models.database import get_db


def acquire_lock(service_name: str, execution_id: int) -> bool:
    """尝试为指定服务获取故障锁。

    利用 service_name 的 UNIQUE 约束：INSERT 成功即获取锁，
    IntegrityError 表示已被其他执行占用。

    Args:
        service_name: 目标服务名称
        execution_id: 持有锁的执行记录 ID

    Returns:
        True 获取成功，False 已被占用
    """
    db = get_db()
    try:
        db.execute(
            """INSERT INTO service_fault_lock (service_name, execution_id)
               VALUES (?, ?)""",
            (service_name, execution_id),
        )
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def release_lock(service_name: str) -> None:
    """释放指定服务的故障锁。

    Args:
        service_name: 目标服务名称
    """
    db = get_db()
    db.execute(
        "DELETE FROM service_fault_lock WHERE service_name = ?",
        (service_name,),
    )
    db.commit()


def is_locked(service_name: str) -> Optional[dict[str, Any]]:
    """检查指定服务是否已被锁定。

    Args:
        service_name: 目标服务名称

    Returns:
        锁信息字典（含 execution_id, locked_at），未锁定返回 None
    """
    db = get_db()
    row = db.execute(
        """SELECT id, service_name, execution_id, locked_at
           FROM service_fault_lock
           WHERE service_name = ?""",
        (service_name,),
    ).fetchone()

    if row is None:
        return None

    return {
        "id": row["id"],
        "service_name": row["service_name"],
        "execution_id": row["execution_id"],
        "locked_at": row["locked_at"],
    }
