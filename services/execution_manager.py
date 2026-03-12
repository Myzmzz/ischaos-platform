"""执行状态管理器。

负责根据 Chaos Mesh Workflow 的实际状态同步更新本地执行记录，
包括：完成检测、超时检测、故障锁释放。

状态流转:
    pending → running → completed (正常完成)
    pending → running → failed    (超时 / Chaos Mesh 异常)
    pending → failed              (锁冲突 / Workflow 提交失败)

判定逻辑:
    - Workflow 三个步骤 (Inject/Wait/Recover) 均有 startTime + endTime → completed
    - 超过 deadline (duration × 2) 仍未完成 → failed (超时)
    - Chaos Mesh 返回异常 → 保持 running，等待下次同步
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from models import execution as execution_model
from models import plan as plan_model
from services.chaos_client import get_workflow_status, ChaosClientError
from services.fault_lock import release_lock

logger = logging.getLogger(__name__)

# 无效时间标记（Chaos Mesh 用此表示"尚未开始"）
_ZERO_TIME = "1970-01-01T00:00:00Z"


def sync_execution_status(execution_id: int) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """同步执行状态：查询 Chaos Mesh 并更新本地记录。

    每次查询 /status 时调用，确保本地状态与 Chaos Mesh 一致。

    Args:
        execution_id: 执行记录 ID

    Returns:
        (execution_dict, chaos_status_dict) 元组
    """
    execution = execution_model.get_by_id(execution_id)
    if execution is None:
        return None, None

    # 终态不再同步
    if execution["status"] in ("completed", "failed"):
        chaos_status = _safe_get_chaos_status(execution["workflow_name"])
        return execution, chaos_status

    workflow_name = execution["workflow_name"]
    if not workflow_name:
        return execution, None

    # 查询 Chaos Mesh 实时状态
    chaos_status = _safe_get_chaos_status(workflow_name)
    if chaos_status is None or "error" in chaos_status:
        return execution, chaos_status

    # ── 状态判定 ──
    node_info = _get_first_node(chaos_status)
    if node_info is None:
        return execution, chaos_status

    step_span_list = node_info.get("stepSpanList", [])
    now_utc = datetime.now(timezone.utc)
    now_str = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1) 检查是否所有步骤都已完成
    if _all_steps_done(step_span_list):
        _mark_completed(execution, node_info, now_str)
        execution = execution_model.get_by_id(execution_id)
        return execution, chaos_status

    # 2) 检查是否超时
    plan = plan_model.get_by_id(execution["plan_id"])
    if plan and _is_timed_out(execution, plan, now_utc):
        _mark_timeout(execution, plan, now_str)
        execution = execution_model.get_by_id(execution_id)
        return execution, chaos_status

    # 3) 更新中间状态的时间点（如 fault_inject_at）
    _update_intermediate_times(execution, step_span_list)
    execution = execution_model.get_by_id(execution_id)

    return execution, chaos_status


def _safe_get_chaos_status(workflow_name: str) -> Optional[Dict[str, Any]]:
    """安全查询 Chaos Mesh Workflow 状态，失败返回带 error 的字典。"""
    if not workflow_name:
        return None
    try:
        return get_workflow_status(workflow_name)
    except ChaosClientError as e:
        logger.warning("查询 Workflow 状态失败: %s", e)
        return {"error": str(e)}


def _get_first_node(chaos_status: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """获取 Chaos Mesh 状态中的第一个 nodeInfo。"""
    node_list = chaos_status.get("nodeInfoList")
    if not node_list:
        return None
    return node_list[0]


def _has_valid_time(time_str: Optional[str]) -> bool:
    """判断时间字符串是否有效（非空、非 1970 零值）。"""
    return bool(time_str) and time_str != _ZERO_TIME


def _all_steps_done(step_span_list: list) -> bool:
    """判断 Workflow 所有步骤是否都已完成。

    每个步骤必须同时有有效的 startTime 和 endTime。
    """
    if len(step_span_list) < 3:
        return False
    return all(
        _has_valid_time(step.get("startTime")) and _has_valid_time(step.get("endTime"))
        for step in step_span_list[:3]
    )


def _parse_duration_seconds(duration: str) -> int:
    """将时间字符串（如 "30s", "5m", "1h"）解析为秒数。"""
    try:
        if duration.endswith("s"):
            return int(duration[:-1])
        elif duration.endswith("m"):
            return int(duration[:-1]) * 60
        elif duration.endswith("h"):
            return int(duration[:-1]) * 3600
        else:
            return int(duration)
    except (ValueError, IndexError):
        return 120  # 默认 2 分钟


def _is_timed_out(
    execution: Dict[str, Any],
    plan: Dict[str, Any],
    now: datetime,
) -> bool:
    """判断执行是否超时。

    超时判定：从 started_at 算起，超过 duration × 3 视为超时。
    给 3 倍余量是因为 Workflow deadline 本身是 2 倍 duration，
    再留一倍给网络延迟和 Recover 操作。
    """
    started_at = execution.get("started_at")
    if not started_at:
        return False

    try:
        start_dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return False

    duration_s = _parse_duration_seconds(plan.get("duration", "30s"))
    # 超时阈值 = duration × 3
    timeout_threshold_s = duration_s * 3
    elapsed = (now - start_dt).total_seconds()

    return elapsed > timeout_threshold_s


def _mark_completed(
    execution: Dict[str, Any],
    node_info: Dict[str, Any],
    now_str: str,
) -> None:
    """标记执行为已完成，释放故障锁。"""
    execution_id = execution["id"]

    # 从 Recover 步骤的 endTime 获取故障结束时间
    step_span_list = node_info.get("stepSpanList", [])
    fault_end = now_str
    if len(step_span_list) >= 3:
        recover_end = step_span_list[2].get("endTime")
        if _has_valid_time(recover_end):
            fault_end = recover_end

    # 从 Inject 步骤获取故障注入时间
    update_kwargs: Dict[str, Any] = {
        "finished_at": now_str,
        "fault_end_at": fault_end,
    }
    if len(step_span_list) >= 1:
        inject_start = step_span_list[0].get("startTime")
        if _has_valid_time(inject_start) and not execution.get("fault_inject_at"):
            update_kwargs["fault_inject_at"] = inject_start

    execution_model.update_status(execution_id, "completed", **update_kwargs)

    # 释放故障锁
    plan = plan_model.get_by_id(execution["plan_id"])
    if plan:
        release_lock(plan["target_service"])
        logger.info(
            "执行 #%d 已完成，服务 '%s' 故障锁已释放",
            execution_id, plan["target_service"],
        )


def _mark_timeout(
    execution: Dict[str, Any],
    plan: Dict[str, Any],
    now_str: str,
) -> None:
    """标记执行为超时失败，释放故障锁。"""
    execution_id = execution["id"]
    duration = plan.get("duration", "30s")

    execution_model.update_status(
        execution_id, "failed",
        finished_at=now_str,
        error_message=f"执行超时：超过预期时长 ({duration} × 3) 仍未完成",
    )

    release_lock(plan["target_service"])
    logger.warning(
        "执行 #%d 已超时，服务 '%s' 故障锁已释放",
        execution_id, plan["target_service"],
    )


def _update_intermediate_times(
    execution: Dict[str, Any],
    step_span_list: list,
) -> None:
    """更新执行过程中的中间时间点（fault_inject_at, fault_end_at）。

    在 Workflow 还未全部完成时，根据已完成的步骤更新时间。
    """
    if not step_span_list:
        return

    update_kwargs: Dict[str, Any] = {}

    # Inject 步骤开始 → 记录 fault_inject_at
    if len(step_span_list) >= 1 and not execution.get("fault_inject_at"):
        inject_start = step_span_list[0].get("startTime")
        if _has_valid_time(inject_start):
            update_kwargs["fault_inject_at"] = inject_start

    # Recover 步骤结束 → 记录 fault_end_at
    if len(step_span_list) >= 3 and not execution.get("fault_end_at"):
        recover_end = step_span_list[2].get("endTime")
        if _has_valid_time(recover_end):
            update_kwargs["fault_end_at"] = recover_end

    if update_kwargs:
        execution_model.update_status(
            execution["id"], execution["status"], **update_kwargs
        )
