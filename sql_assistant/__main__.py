"""Offline demo: build a sample SQLite DB and answer a question with a scripted SQL."""
from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

from .assistant import ask
from .llm import ScriptedLLM


def _sample_db() -> str:
    path = Path(tempfile.mkdtemp()) / "demo.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, city TEXT)")
    conn.executemany("INSERT INTO users(name, city) VALUES (?,?)",
                     [("Ava", "NYC"), ("Ben", "LA"), ("Cy", "NYC")])
    conn.commit(); conn.close()
    return str(path)


def main():
    db = _sample_db()
    llm = ScriptedLLM(["SELECT city, COUNT(*) AS n FROM users GROUP BY city ORDER BY city"])
    out = ask("how many users per city?", db, llm)
    print("SQL:", out["sql"])
    print("rows:", out["rows"])
    print("answer:", out["answer"])


if __name__ == "__main__":
    main()
