"""数据库初始化脚本 — 建表 + 从 topology_report.md 导入 15 个接口拓扑。

与上一版的区别：
  - 通过 trace 详情解析每个服务实际访问的 MongoDB 实例名称
  - 将通用 "MONGODB" 节点拆分为各服务独立的 MongoDB 节点（如 ts-auth-mongo）
  - 边也相应更新为指向具体的 MongoDB 节点

用法:
    python init_db.py                              # 使用默认 docs 路径
    python init_db.py /path/to/topology_report.md  # 指定文件
"""

import json
import os
import re
import sqlite3
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from models.database import init_schema


# ── 从 trace span 中提取 service→mongo_db 映射 ──────────────

# span 格式: [ts-xxx-service] find|insert|update|delete db_name.collection
_DB_OP_RE = re.compile(
    r"\[(?P<service>ts-[\w-]+)\]\s+"
    r"(?:find|insert|update|delete|aggregate|command)\s+"
    r"(?P<db>[\w-]+)\.(?P<collection>\w+)"
)


def extract_mongo_mappings(section: str) -> dict[str, str]:
    """从一个接口段落的 trace 详情中提取 service → mongo_node_name 映射。

    策略：
    - 如果 db_name 本身含 'mongo'（如 ts-auth-mongo），直接用作节点名
    - 否则，根据服务名推导：ts-xxx-service → ts-xxx-mongo
    """
    mappings: dict[str, str] = {}

    for match in _DB_OP_RE.finditer(section):
        service = match.group("service")
        db_name = match.group("db")

        if service in mappings:
            continue  # 同一接口内同一服务只记录一次

        if "mongo" in db_name.lower():
            # db_name 已经是 mongo 实例名，如 ts-auth-mongo
            mongo_node = db_name
        else:
            # 从服务名推导：ts-xxx-service → ts-xxx-mongo
            mongo_node = re.sub(r"-service$", "-mongo", service)
            # 特殊处理：ts-food-map-service → ts-food-map-mongo
            # ts-travel2-service → ts-travel2-mongo（直接替换即可）

        mappings[service] = mongo_node

    return mappings


def fix_topology(topology: dict, mongo_mappings: dict[str, str]) -> dict:
    """修正拓扑数据：将通用 MONGODB 节点拆分为各服务独立的 MongoDB 节点。

    Args:
        topology: 原始拓扑 {"nodes": [...], "edges": [...]}
        mongo_mappings: service_name → mongo_node_name 映射

    Returns:
        修正后的拓扑
    """
    old_nodes = topology.get("nodes", [])
    old_edges = topology.get("edges", [])

    # 收集非 MONGODB 的节点
    new_nodes = [n for n in old_nodes if n["id"] != "MONGODB"]

    # 收集需要替换的 MONGODB 边 → 具体 mongo 节点
    new_edges = []
    created_mongo_nodes: set[str] = set()

    for edge in old_edges:
        if edge["target"] == "MONGODB":
            source_service = edge["source"]
            mongo_node = mongo_mappings.get(source_service)

            if mongo_node is None:
                # trace 中没有找到该服务的 MongoDB 操作
                # 兜底：从服务名推导
                mongo_node = re.sub(r"-service$", "-mongo", source_service)

            # 创建对应的 mongo 节点（去重）
            if mongo_node not in created_mongo_nodes:
                created_mongo_nodes.add(mongo_node)
                new_nodes.append({
                    "id": mongo_node,
                    "type": "db",
                    "label": mongo_node,
                    "root": False,
                })

            new_edges.append({
                "source": source_service,
                "target": mongo_node,
                "label": edge["label"],  # 保留原协议标签（MONGODB）
            })
        else:
            new_edges.append(edge)

    return {"nodes": new_nodes, "edges": new_edges}


# ── 解析 topology_report.md ──────────────────────────────────

def parse_topology_report(filepath: str) -> list[dict[str, Any]]:
    """从 topology_report.md 中提取所有接口的元数据和修正后的拓扑 JSON。"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    sections = re.split(r"(?=^## 接口 \d+:)", content, flags=re.MULTILINE)

    interfaces: list[dict[str, Any]] = []

    for section in sections:
        title_match = re.match(r"^## 接口 \d+:\s*(.+)$", section, re.MULTILINE)
        if not title_match:
            continue

        name = title_match.group(1).strip()

        url_match = re.search(r"\*\*URL\*\*:\s*`([^`]+)`", section)
        url = url_match.group(1) if url_match else ""

        span_match = re.search(r"\*\*Coroot SpanName\*\*:\s*`([^`]+)`", section)
        span_name = span_match.group(1) if span_match else ""

        method = span_name.split(" ")[0] if span_name else "GET"

        req_match = re.search(r"\*\*总请求数\*\*:\s*(\d+)", section)
        total_requests = int(req_match.group(1)) if req_match else 0

        json_match = re.search(r"```json\s*\n(.*?)\n```", section, re.DOTALL)
        if not json_match:
            print(f"  [警告] 接口 '{name}' 未找到 JSON 拓扑数据，跳过")
            continue

        try:
            topo_data = json.loads(json_match.group(1))
        except json.JSONDecodeError as e:
            print(f"  [错误] 接口 '{name}' JSON 解析失败: {e}，跳过")
            continue

        topology = topo_data.get("topology", {})

        # 从 trace 详情提取 MongoDB 映射并修正拓扑
        mongo_mappings = extract_mongo_mappings(section)
        has_mongodb = any(n["id"] == "MONGODB" for n in topology.get("nodes", []))

        if has_mongodb and mongo_mappings:
            topology = fix_topology(topology, mongo_mappings)
            mongo_names = list(set(mongo_mappings.values()))
            print(f"  [修正] '{name}': MONGODB → {mongo_names}")
        elif has_mongodb and not mongo_mappings:
            # 边表有 MONGODB 但 trace 中没找到具体操作 → 兜底推导
            topology = fix_topology(topology, {})
            print(f"  [兜底] '{name}': MONGODB → 按服务名推导")

        interfaces.append({
            "name": name,
            "url": url,
            "span_name": span_name,
            "method": method,
            "total_requests": total_requests,
            "topology_json": json.dumps(topology, ensure_ascii=False),
        })

    return interfaces


# ── 数据库操作 ────────────────────────────────────────────────

def import_interfaces(interfaces: list[dict[str, Any]]) -> int:
    """清空旧数据后重新导入所有接口。"""
    db = sqlite3.connect(Config.DATABASE_PATH)
    db.row_factory = sqlite3.Row

    # 清空旧数据（级联删除不影响其他表，interface_topology 是被引用的）
    db.execute("DELETE FROM interface_topology")
    db.commit()

    imported = 0
    for iface in interfaces:
        db.execute(
            """INSERT INTO interface_topology
               (name, url, span_name, method, total_requests, topology_json)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                iface["name"],
                iface["url"],
                iface["span_name"],
                iface["method"],
                iface["total_requests"],
                iface["topology_json"],
            ),
        )
        imported += 1

        # 解析 topology 统计信息
        topo = json.loads(iface["topology_json"])
        db_nodes = [n["id"] for n in topo.get("nodes", []) if n["type"] == "db"]
        svc_count = sum(1 for n in topo.get("nodes", []) if n["type"] == "service")
        print(f"  [导入] #{imported:2d} {iface['name']:<12s}  "
              f"服务:{svc_count} DB:{db_nodes}")

    db.commit()
    db.close()
    return imported


def main() -> None:
    """入口：建表 → 解析（含 MongoDB 修正）→ 清空重导。"""
    if len(sys.argv) > 1:
        report_path = sys.argv[1]
    else:
        project_root = os.path.dirname(os.path.abspath(__file__))
        report_path = os.path.join(project_root, "..", "docs", "topology_report.md")

    report_path = os.path.abspath(report_path)

    if not os.path.exists(report_path):
        print(f"[错误] 文件不存在: {report_path}")
        sys.exit(1)

    os.makedirs("data", exist_ok=True)

    print("=== ISChaos 数据库初始化（MongoDB 拓扑修正版）===")
    print(f"数据库: {os.path.abspath(Config.DATABASE_PATH)}")
    print(f"数据源: {report_path}")
    print()

    print("[1/3] 创建数据库 schema ...")
    init_schema()
    print("  完成")

    print("[2/3] 解析 topology_report.md + 修正 MongoDB 拓扑 ...")
    interfaces = parse_topology_report(report_path)
    print(f"  解析到 {len(interfaces)} 个接口")

    print("[3/3] 清空旧数据并重新导入 ...")
    imported = import_interfaces(interfaces)

    # 汇总统计
    all_db_nodes: set[str] = set()
    for iface in interfaces:
        topo = json.loads(iface["topology_json"])
        for n in topo.get("nodes", []):
            if n["type"] == "db":
                all_db_nodes.add(n["id"])

    print(f"\n=== 完成：导入 {imported} 个接口 ===")
    print(f"全局 MongoDB 实例: {sorted(all_db_nodes)}")


if __name__ == "__main__":
    main()
