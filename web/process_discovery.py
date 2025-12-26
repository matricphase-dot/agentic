#!/usr/bin/env python3
"""
Process Discovery / Mission Logging

Logs each mission and deployed script into a lightweight SQLite database.
Used later for Workflow Discovery and recommendations.
"""

import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path("workflow_logs.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS missions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal TEXT,
        script_path TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()


def log_mission(goal: str, script_path: str):
    init_db()
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO missions (goal, script_path, created_at) VALUES (?, ?, ?)",
        (goal, script_path, time.strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def list_missions(limit: int = 20) -> List[Dict[str, Any]]:
    init_db()
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, goal, script_path, created_at FROM missions ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "goal": r[1],
            "script_path": r[2],
            "created_at": r[3],
        }
        for r in rows
    ]
