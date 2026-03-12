"""故障类型 → Chaos Mesh Workflow JSON 构建器。

根据演练计划信息生成符合 Chaos Mesh Workflow API 规范的 JSON 结构。
支持 10 种故障类型，每种类型映射到对应的 templateType 和参数。
"""

import json
import time
from typing import Any, Dict, Optional, Tuple

from config import Config


# 故障类型 → (templateType, action) 映射
FAULT_TYPE_MAP: Dict[str, Tuple[str, Optional[str]]] = {
    "network_loss":      ("NetworkChaos", "loss"),
    "network_delay":     ("NetworkChaos", "delay"),
    "network_partition": ("NetworkChaos", "partition"),
    "pod_failure":       ("PodChaos", "pod-failure"),
    "pod_kill":          ("PodChaos", "pod-kill"),
    "stress_cpu":        ("StressChaos", None),
    "stress_mem":        ("StressChaos", None),
    "dns_error":         ("DNSChaos", "error"),
    "node_cpu":          ("PhysicalMachineChaos", "stress-cpu"),
    "node_mem":          ("PhysicalMachineChaos", "stress-mem"),
}


def build_workflow(plan: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """根据演练计划构建 Chaos Mesh Workflow JSON。

    Args:
        plan: 演练计划字典，需包含以下字段：
            - id: 计划 ID
            - fault_type: 故障类型（如 network_delay）
            - target_service: 目标服务名（如 ts-ui-dashboard）
            - fault_params: 故障参数 JSON 字符串或字典
            - duration: 持续时间（如 30s）

    Returns:
        (workflow_name, workflow_json) 元组

    Raises:
        ValueError: 不支持的故障类型
    """
    fault_type: str = plan["fault_type"]
    if fault_type not in FAULT_TYPE_MAP:
        raise ValueError(f"不支持的故障类型: {fault_type}")

    # 解析故障参数
    fault_params = plan["fault_params"]
    if isinstance(fault_params, str):
        fault_params = json.loads(fault_params)

    target_service: str = plan["target_service"]
    duration: str = plan.get("duration", "30s")
    namespace: str = Config.TARGET_NAMESPACE

    # 生成唯一 workflow 名称
    timestamp = int(time.time())
    workflow_name = f"ischaos-{plan['id']}-{timestamp}"

    template_type, action = FAULT_TYPE_MAP[fault_type]

    # 构建模板内容
    template_spec = _build_template_spec(
        fault_type=fault_type,
        template_type=template_type,
        action=action,
        target_service=target_service,
        namespace=namespace,
        fault_params=fault_params,
    )

    # 组装 Workflow JSON
    workflow_json: dict[str, Any] = {
        "apiVersion": "chaos-mesh.org/v1alpha1",
        "kind": "Workflow",
        "metadata": {
            "name": workflow_name,
            "namespace": namespace,
        },
        "spec": {
            "entry": "entry",
            "templates": [
                {
                    "name": "entry",
                    "templateType": template_type,
                    "deadline": duration,
                    **template_spec,
                }
            ],
        },
    }

    return workflow_name, workflow_json


def _build_template_spec(
    fault_type: str,
    template_type: str,
    action: Optional[str],
    target_service: str,
    namespace: str,
    fault_params: Dict[str, Any],
) -> Dict[str, Any]:
    """根据故障类型构建模板内部的 spec 字段。

    Args:
        fault_type: 故障类型标识
        template_type: Chaos Mesh 模板类型
        action: Chaos Mesh action 字段
        target_service: 目标服务名
        namespace: 目标命名空间
        fault_params: 故障参数字典

    Returns:
        模板 spec 字典，作为 template 的一部分合并
    """
    # 通用的 Pod selector（K8s 级故障使用）
    selector = {
        "namespaces": [namespace],
        "labelSelectors": {"app": target_service},
    }

    if template_type == "NetworkChaos":
        return _build_network_chaos(action, selector, fault_params)
    elif template_type == "PodChaos":
        return _build_pod_chaos(action, selector, fault_params)
    elif template_type == "StressChaos":
        return _build_stress_chaos(fault_type, selector, fault_params)
    elif template_type == "DNSChaos":
        return _build_dns_chaos(selector, fault_params)
    elif template_type == "PhysicalMachineChaos":
        return _build_physical_machine_chaos(action, fault_params)
    else:
        raise ValueError(f"未知的模板类型: {template_type}")


def _build_network_chaos(
    action: str, selector: dict, params: dict
) -> dict[str, Any]:
    """构建 NetworkChaos 模板。"""
    spec: dict[str, Any] = {
        "networkChaos": {
            "action": action,
            "direction": params.get("direction", "to"),
            "mode": "all",
            "selector": selector,
        }
    }
    chaos = spec["networkChaos"]

    if action == "delay":
        chaos["delay"] = {
            "latency": params.get("latency", "200ms"),
            "jitter": params.get("jitter", "0ms"),
            "correlation": params.get("correlation", "0"),
        }
    elif action == "loss":
        chaos["loss"] = {
            "loss": params.get("loss", "50"),
            "correlation": params.get("correlation", "0"),
        }
    elif action == "partition":
        chaos["direction"] = params.get("direction", "both")

    return spec


def _build_pod_chaos(
    action: str, selector: dict, params: dict
) -> dict[str, Any]:
    """构建 PodChaos 模板。"""
    spec: dict[str, Any] = {
        "podChaos": {
            "action": action,
            "mode": "all",
            "selector": selector,
        }
    }
    if action == "pod-kill" and "gracePeriod" in params:
        spec["podChaos"]["gracePeriod"] = int(params["gracePeriod"])

    return spec


def _build_stress_chaos(
    fault_type: str, selector: dict, params: dict
) -> dict[str, Any]:
    """构建 StressChaos 模板。"""
    spec: dict[str, Any] = {
        "stressChaos": {
            "mode": "all",
            "selector": selector,
            "stressors": {},
        }
    }
    stressors = spec["stressChaos"]["stressors"]

    if fault_type == "stress_cpu":
        stressors["cpu"] = {
            "workers": int(params.get("workers", 1)),
            "load": int(params.get("load", 80)),
        }
    elif fault_type == "stress_mem":
        stressors["memory"] = {
            "workers": int(params.get("workers", 1)),
            "size": params.get("size", "256MB"),
        }

    return spec


def _build_dns_chaos(
    selector: dict, params: dict
) -> dict[str, Any]:
    """构建 DNSChaos 模板。"""
    spec: dict[str, Any] = {
        "dnsChaos": {
            "action": "error",
            "mode": "all",
            "selector": selector,
        }
    }
    if "patterns" in params:
        patterns = params["patterns"]
        if isinstance(patterns, str):
            patterns = [p.strip() for p in patterns.split(",")]
        spec["dnsChaos"]["patterns"] = patterns

    return spec


def _build_physical_machine_chaos(
    action: str, params: dict
) -> dict[str, Any]:
    """构建 PhysicalMachineChaos 模板（物理机级别故障）。"""
    spec: dict[str, Any] = {
        "physicalmachineChaos": {
            "action": action,
            "address": [params.get("address", "")],
        }
    }
    chaos = spec["physicalmachineChaos"]

    if action == "stress-cpu":
        chaos["stress-cpu"] = {
            "workers": int(params.get("workers", 1)),
            "load": int(params.get("load", 80)),
        }
    elif action == "stress-mem":
        chaos["stress-mem"] = {
            "size": params.get("size", "256MB"),
        }

    return spec
