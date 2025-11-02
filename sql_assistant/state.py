from __future__ import annotations

from typing import TypedDict


class SQLState(TypedDict, total=False):
    question: str
    schema: str
    sql: str
    error: str
    attempts: int
    rows: list
    answer: str
