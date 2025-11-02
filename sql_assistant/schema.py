"""SQLite schema introspection -> a compact text description for the prompt."""
from __future__ import annotations

import sqlite3


def list_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [r[0] for r in rows]


def describe_schema(conn: sqlite3.Connection) -> str:
    lines = []
    for table in list_tables(conn):
        cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
        col_desc = ", ".join(f"{c[1]} {c[2]}".strip() for c in cols)
        lines.append(f"{table}({col_desc})")
    return "\n".join(lines)
