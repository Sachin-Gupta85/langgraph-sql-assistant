import sqlite3
import pytest
from sql_assistant.assistant import ask
from sql_assistant.llm import ScriptedLLM


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "t.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, city TEXT)")
    conn.executemany("INSERT INTO users(name, city) VALUES (?,?)",
                     [("Ava", "NYC"), ("Ben", "LA"), ("Cy", "NYC")])
    conn.commit(); conn.close()
    return str(path)


def test_happy_path(db):
    llm = ScriptedLLM(["SELECT name FROM users ORDER BY name"])
    out = ask("list users", db, llm)
    assert [r["name"] for r in out["rows"]] == ["Ava", "Ben", "Cy"]
    assert out["attempts"] == 1
    assert "LIMIT 100" in out["sql"]


def test_repairs_invalid_sql(db):
    # first a forbidden mutation (fails validation), then a valid select
    llm = ScriptedLLM(["DELETE FROM users", "SELECT city FROM users"])
    out = ask("show cities", db, llm)
    assert out["attempts"] == 2 and not out["error"]
    assert len(out["rows"]) == 3


def test_repairs_execution_error(db):
    # valid SELECT but a bad column (DB error), then a good one
    llm = ScriptedLLM(["SELECT nope FROM users", "SELECT name FROM users"])
    out = ask("names please", db, llm)
    assert out["attempts"] == 2 and not out["error"]


def test_gives_up_after_budget(db):
    llm = ScriptedLLM(["DELETE FROM users", "DROP TABLE users", "UPDATE users SET name='x'"])
    out = ask("bad", db, llm, max_attempts=3)
    assert out["error"] and out["answer"].startswith("Could not answer")
    assert out["attempts"] == 3
