import sqlite3
import pytest
from sql_assistant.safety import validate_sql, ensure_limit
from sql_assistant.schema import describe_schema, list_tables


def test_validate_accepts_select_and_with():
    assert validate_sql("SELECT * FROM t") == "SELECT * FROM t"
    assert validate_sql("  WITH x AS (SELECT 1) SELECT * FROM x ;") == "WITH x AS (SELECT 1) SELECT * FROM x"


def test_validate_rejects_mutations_and_chaining():
    for bad in ["DELETE FROM t", "UPDATE t SET a=1", "DROP TABLE t",
                "SELECT 1; DROP TABLE t", "INSERT INTO t VALUES (1)"]:
        with pytest.raises(ValueError):
            validate_sql(bad)


def test_ensure_limit():
    assert ensure_limit("SELECT * FROM t") == "SELECT * FROM t LIMIT 100"
    assert ensure_limit("SELECT * FROM t LIMIT 5") == "SELECT * FROM t LIMIT 5"


def test_describe_schema():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users(id INTEGER, name TEXT)")
    conn.execute("CREATE TABLE orders(id INTEGER, total REAL)")
    assert list_tables(conn) == ["orders", "users"]
    desc = describe_schema(conn)
    assert "users(" in desc and "name TEXT" in desc
