"""SQLite 连接管理与 schema 初始化。"""

import sqlite3

from flask import g

from config import Config


def get_db() -> sqlite3.Connection:
    """获取当前请求的 SQLite 连接（Flask g 对象管理，线程安全）。"""
    if "db" not in g:
        g.db = sqlite3.connect(Config.DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


def close_db(exc: BaseException = None) -> None:
    """关闭当前请求的数据库连接。"""
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ── Schema 定义 ──────────────────────────────────────────────

SCHEMA_SQL = """
-- 接口拓扑表：存储 15 个业务接口及其调用链拓扑
CREATE TABLE IF NOT EXISTS interface_topology (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,               -- 接口名称，如 "Login"
    url             TEXT    NOT NULL,               -- 请求 URL
    span_name       TEXT    NOT NULL,               -- Coroot SpanName
    method          TEXT    NOT NULL DEFAULT 'POST', -- HTTP 方法
    total_requests  INTEGER NOT NULL DEFAULT 0,     -- 压测总请求数
    topology_json   TEXT    NOT NULL,               -- 拓扑 JSON（nodes + edges）
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- 演练计划表
CREATE TABLE IF NOT EXISTS drill_plan (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,               -- 计划名称
    interface_id    INTEGER NOT NULL,               -- 关联的接口 ID
    fault_type      TEXT    NOT NULL,               -- 故障类型（如 network_delay）
    target_service  TEXT    NOT NULL,               -- 注入目标服务
    fault_params    TEXT    NOT NULL DEFAULT '{}',  -- 故障参数 JSON
    duration        TEXT    NOT NULL DEFAULT '30s', -- 故障持续时间
    status          TEXT    NOT NULL DEFAULT 'draft', -- draft / ready / archived
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (interface_id) REFERENCES interface_topology(id)
);

-- 演练执行记录表
CREATE TABLE IF NOT EXISTS drill_execution (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id         INTEGER NOT NULL,               -- 关联的计划 ID
    workflow_name   TEXT,                            -- Chaos Mesh Workflow 名称
    status          TEXT    NOT NULL DEFAULT 'pending',  -- pending / running / collecting / completed / failed
    started_at      TEXT,
    finished_at     TEXT,
    fault_inject_at TEXT,                            -- 故障实际注入时间
    fault_end_at    TEXT,                            -- 故障实际结束时间
    result_json     TEXT    NOT NULL DEFAULT '{}',  -- 收集到的观测数据摘要
    error_message   TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (plan_id) REFERENCES drill_plan(id)
);

-- 服务故障互斥锁表：同一服务同一时间只允许一个活跃故障
CREATE TABLE IF NOT EXISTS service_fault_lock (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name    TEXT    NOT NULL UNIQUE,         -- 被锁定的服务名
    execution_id    INTEGER NOT NULL,               -- 持有锁的执行记录 ID
    locked_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (execution_id) REFERENCES drill_execution(id)
);
"""


def init_schema() -> None:
    """执行建表 SQL（使用独立连接，不依赖 Flask g 对象）。"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
