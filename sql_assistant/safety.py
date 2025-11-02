"""SQL safety gate: accept a single read-only SELECT, and bound result size."""
from __future__ import annotations

import re

_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum|grant|truncate)\b",
    re.IGNORECASE,
)


def validate_sql(sql: str) -> str:
    """Return the trimmed SQL if it is a single read-only SELECT/WITH, else raise."""
    stripped = sql.strip().rstrip(";").strip()
    if not stripped:
        raise ValueError("empty SQL")
    if ";" in stripped:
        raise ValueError("multiple statements are not allowed")
    if not re.match(r"(?is)^\s*(select|with)\b", stripped):
        raise ValueError("only SELECT queries are allowed")
    if _FORBIDDEN.search(stripped):
        raise ValueError("query contains a forbidden keyword")
    return stripped


def ensure_limit(sql: str, default: int = 100) -> str:
    """Append a LIMIT when the query has none, so results stay bounded."""
    if re.search(r"(?is)\blimit\b", sql):
        return sql
    return f"{sql} LIMIT {default}"
