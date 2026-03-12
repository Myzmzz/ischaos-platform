"""Kubernetes API 客户端封装。

自动检测运行环境（集群内 / 本地开发），提供 Pod、Node、Service
部署拓扑和实体列表查询功能。
"""

import logging
import math
from typing import Any, Dict, List, Optional

from kubernetes import client, config
from kubernetes.client.rest import ApiException

from config import Config

logger = logging.getLogger(__name__)

# 模块级单例
_core_api: Optional[client.CoreV1Api] = None
_apps_api: Optional[client.AppsV1Api] = None


# ============================================================================
# 客户端初始化
# ============================================================================


def _load_config() -> None:
    """加载 K8s 配置，优先尝试集群内模式，失败则回退到本地 kubeconfig。"""
    try:
        config.load_incluster_config()
        logger.info("已加载集群内（in-cluster）Kubernetes 配置")
    except config.ConfigException:
        kubeconfig_path = Config.KUBECONFIG_PATH
        logger.info("加载本地 kubeconfig: %s", kubeconfig_path)
        config.load_kube_config(config_file=kubeconfig_path)


def get_core_api() -> client.CoreV1Api:
    """获取 CoreV1Api 单例。"""
    global _core_api
    if _core_api is None:
        _load_config()
        _core_api = client.CoreV1Api()
    return _core_api


def get_apps_api() -> client.AppsV1Api:
    """获取 AppsV1Api 单例。"""
    global _apps_api
    if _apps_api is None:
        _load_config()
        _apps_api = client.AppsV1Api()
    return _apps_api


# ============================================================================
# 辅助函数
# ============================================================================


def _parse_memory_to_gb(memory_str: str) -> float:
    """将 K8s 内存字符串（如 '32Gi', '16384Ki'）转换为 GB。"""
    if not memory_str:
        return 0.0

    units = {
        "Ki": 1024,
        "Mi": 1024 ** 2,
        "Gi": 1024 ** 3,
        "Ti": 1024 ** 4,
        "K": 1000,
        "M": 1000 ** 2,
        "G": 1000 ** 3,
        "T": 1000 ** 4,
    }

    for suffix, multiplier in units.items():
        if memory_str.endswith(suffix):
            value = float(memory_str[: -len(suffix)])
            return round(value * multiplier / (1024 ** 3), 1)

    # 纯数字 → 字节
    try:
        return round(float(memory_str) / (1024 ** 3), 1)
    except ValueError:
        return 0.0


def _parse_cpu(cpu_str: str) -> int:
    """将 K8s CPU 字符串（如 '8', '4000m'）转换为核数（整数）。"""
    if not cpu_str:
        return 0
    if cpu_str.endswith("m"):
        return math.ceil(float(cpu_str[:-1]) / 1000)
    try:
        return int(float(cpu_str))
    except ValueError:
        return 0


def _get_pod_service_name(pod: client.V1Pod) -> str:
    """从 Pod 推断所属服务名。

    优先使用 'app' label，其次通过 ownerReferences 链找 Deployment。
    """
    # 方式 1：使用 app label
    labels = pod.metadata.labels or {}
    for label_key in ("app", "app.kubernetes.io/name"):
        if label_key in labels:
            return labels[label_key]

    # 方式 2：通过 ownerReferences 找 ReplicaSet → Deployment
    owner_refs = pod.metadata.owner_references or []
    for ref in owner_refs:
        if ref.kind == "ReplicaSet":
            # ReplicaSet 名格式: <deployment-name>-<hash>
            rs_name = ref.name
            parts = rs_name.rsplit("-", 1)
            if len(parts) == 2:
                return parts[0]
            return rs_name

    # 兜底：使用 Pod 名（去掉尾部 hash）
    pod_name = pod.metadata.name or ""
    parts = pod_name.rsplit("-", 2)
    if len(parts) >= 3:
        return "-".join(parts[:-2])
    return pod_name


def _get_node_status(node: client.V1Node) -> str:
    """获取 Node 状态：遍历 conditions 找 Ready。"""
    conditions = node.status.conditions or []
    for cond in conditions:
        if cond.type == "Ready":
            return "Ready" if cond.status == "True" else "NotReady"
    return "Unknown"


def _is_target_service(pod: client.V1Pod) -> bool:
    """判断 Pod 是否属于目标业务服务（排除中间件）。"""
    service_name = _get_pod_service_name(pod).lower()
    db_keywords = ("mongo", "mysql", "rabbitmq", "redis")
    return not any(kw in service_name for kw in db_keywords)


# ============================================================================
# 对外接口
# ============================================================================


def get_topology(namespace: str) -> Dict[str, Any]:
    """获取部署拓扑：services、nodes、dependencies。

    Args:
        namespace: 目标命名空间（如 'train-ticket'）

    Returns:
        {
            "services": [{"service_name": "...", "pods": [...]}],
            "nodes": [{"node_name": "...", "pods": [...], "cpu_total": 8, "memory_total_gb": 32}],
            "dependencies": [{"caller": "...", "callee": "..."}]
        }
    """
    core_api = get_core_api()

    # 1. 获取所有 Pod
    pods = core_api.list_namespaced_pod(namespace=namespace)

    # 按 service 分组
    service_pods: Dict[str, List[str]] = {}
    # 按 node 分组
    node_pods: Dict[str, List[str]] = {}

    for pod in pods.items:
        if not _is_target_service(pod):
            continue

        pod_name = pod.metadata.name
        service_name = _get_pod_service_name(pod)
        node_name = pod.spec.node_name or "unknown"

        # 按 service 聚合
        if service_name not in service_pods:
            service_pods[service_name] = []
        service_pods[service_name].append(pod_name)

        # 按 node 聚合
        if node_name not in node_pods:
            node_pods[node_name] = []
        node_pods[node_name].append(pod_name)

    # 2. 获取所有 Node 信息
    all_nodes = core_api.list_node()
    nodes: List[Dict[str, Any]] = []
    for node in all_nodes.items:
        node_name = node.metadata.name
        capacity = node.status.capacity or {}
        nodes.append({
            "node_name": node_name,
            "pods": node_pods.get(node_name, []),
            "cpu_total": _parse_cpu(capacity.get("cpu", "0")),
            "memory_total_gb": _parse_memory_to_gb(capacity.get("memory", "0")),
        })

    # 3. 构造 services 列表
    services: List[Dict[str, Any]] = []
    for svc_name, pod_list in sorted(service_pods.items()):
        services.append({
            "service_name": svc_name,
            "pods": sorted(pod_list),
        })

    # 4. Dependencies：从 Coroot 获取（K8s API 无法提供调用关系）
    dependencies = _get_dependencies_from_coroot()

    return {
        "services": services,
        "nodes": nodes,
        "dependencies": dependencies,
    }


def get_entities(
    namespace: str, entity_type: Optional[str] = None
) -> Dict[str, Any]:
    """获取实体列表：pods、services、nodes。

    Args:
        namespace: 目标命名空间
        entity_type: 可选过滤类型 ('pod', 'service', 'node')

    Returns:
        {"pods": [...], "services": [...], "nodes": [...]}
    """
    core_api = get_core_api()
    result: Dict[str, List[Any]] = {"pods": [], "services": [], "nodes": []}

    # 获取所有 Pod
    pods = core_api.list_namespaced_pod(namespace=namespace)

    # 按 service 聚合统计
    service_pod_counts: Dict[str, int] = {}

    for pod in pods.items:
        if not _is_target_service(pod):
            continue

        pod_name = pod.metadata.name
        service_name = _get_pod_service_name(pod)
        node_name = pod.spec.node_name or "unknown"
        status = (pod.status.phase or "Unknown").lower()

        # Pods
        if entity_type is None or entity_type == "pod":
            result["pods"].append({
                "pod_name": pod_name,
                "service": service_name,
                "node": node_name,
                "status": status,
            })

        # 统计每个 service 的 pod 数
        service_pod_counts[service_name] = (
            service_pod_counts.get(service_name, 0) + 1
        )

    # Services
    if entity_type is None or entity_type == "service":
        for svc_name, count in sorted(service_pod_counts.items()):
            result["services"].append({
                "service_name": svc_name,
                "pods_count": count,
            })

    # Nodes
    if entity_type is None or entity_type == "node":
        all_nodes = core_api.list_node()
        # 统计每个 node 上的目标 Pod 数量
        node_pod_counts: Dict[str, int] = {}
        for pod in pods.items:
            if not _is_target_service(pod):
                continue
            n = pod.spec.node_name or "unknown"
            node_pod_counts[n] = node_pod_counts.get(n, 0) + 1

        for node in all_nodes.items:
            node_name = node.metadata.name
            result["nodes"].append({
                "node_name": node_name,
                "pods_count": node_pod_counts.get(node_name, 0),
                "status": _get_node_status(node).lower(),
            })

    return result


# ============================================================================
# 从 Coroot 获取依赖关系（K8s API 无法提供）
# ============================================================================


def _get_dependencies_from_coroot() -> List[Dict[str, str]]:
    """从 Coroot 获取服务间调用依赖关系。

    K8s API 无法提供服务间的调用关系，通过逐个查询每个应用的
    app_map.dependencies 来获取调用依赖。
    """
    try:
        from services.coroot_client import get_coroot_client

        client = get_coroot_client()
        overview = client.get_overview_applications()
        all_apps = overview.get("data", {}).get("applications", [])

        namespace = Config.TARGET_NAMESPACE
        db_keywords = ("mongo", "mysql", "rabbitmq", "redis")
        dependencies: List[Dict[str, str]] = []
        seen: set = set()

        # 过滤出 train-ticket 命名空间的业务服务
        tt_apps = []
        for app in all_apps:
            app_id = app.get("id", "")
            parts = app_id.split(":")
            if len(parts) < 4 or parts[1] != namespace:
                continue
            name = parts[3].lower()
            if any(kw in name for kw in db_keywords):
                continue
            tt_apps.append(app)

        # 逐个获取应用详情，提取 app_map.dependencies
        for app in tt_apps:
            app_id = app["id"]
            parts = app_id.split(":")
            caller = parts[3]
            try:
                app_detail = client.get_application(app_id)
                app_map = app_detail.get("data", {}).get("app_map", {})
                deps = app_map.get("dependencies", [])
                for dep in deps:
                    dep_id = dep.get("id", "") if isinstance(dep, dict) else str(dep)
                    dep_parts = dep_id.split(":")
                    if len(dep_parts) < 4:
                        continue
                    callee = dep_parts[3]
                    # 排除中间件和非同命名空间的依赖
                    if dep_parts[1] != namespace:
                        continue
                    if any(kw in callee.lower() for kw in db_keywords):
                        continue
                    key = (caller, callee)
                    if key not in seen:
                        seen.add(key)
                        dependencies.append({
                            "caller": caller,
                            "callee": callee,
                        })
            except Exception as e:
                logger.debug("获取 %s 依赖失败: %s", app_id, e)
                continue

        return dependencies

    except Exception as e:
        logger.warning("从 Coroot 获取依赖关系失败: %s", e)
        return []
