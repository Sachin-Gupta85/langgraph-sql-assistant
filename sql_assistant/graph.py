"""NL->SQL workflow as a LangGraph with a validate/execute repair loop.

introspect ─▶ generate ─▶ validate ─┬ valid ─▶ execute ─┬ ok ──▶ finalize ─▶ END
                 ▲                   │                   │
                 │                   └ invalid ──┐       └ db error ─┐
                 └──────── repair (attempts left) ◀──────────────────┘
"""
from __future__ import annotations

import sqlite3

from langgraph.graph import END, START, StateGraph

from .llm import LLM
from .safety import ensure_limit, validate_sql
from .schema import describe_schema
from .state import SQLState


def build_graph(llm: LLM, db_path: str, max_attempts: int = 3):
    def introspect(state: SQLState) -> dict:
        conn = sqlite3.connect(db_path)
        try:
            return {"schema": describe_schema(conn), "attempts": 0}
        finally:
            conn.close()

    def generate(state: SQLState) -> dict:
        prompt = (
            "Given this SQLite schema:\n" + state["schema"] +
            f"\n\nWrite a single read-only SQL SELECT that answers: {state['question']}"
        )
        if state.get("error"):
            prompt += f"\nThe previous attempt failed with: {state['error']}. Fix it."
        return {"sql": llm.complete(prompt), "attempts": state.get("attempts", 0) + 1, "error": ""}

    def validate(state: SQLState) -> dict:
        try:
            return {"sql": ensure_limit(validate_sql(state["sql"])), "error": ""}
        except ValueError as exc:
            return {"error": f"validation: {exc}"}

    def execute(state: SQLState) -> dict:
        conn = sqlite3.connect(db_path)
        try:
            conn.row_factory = sqlite3.Row
            rows = [dict(r) for r in conn.execute(state["sql"]).fetchall()]
            return {"rows": rows, "error": ""}
        except sqlite3.Error as exc:
            return {"error": f"execution: {exc}"}
        finally:
            conn.close()

    def finalize(state: SQLState) -> dict:
        if state.get("error"):
            return {"answer": f"Could not answer: {state['error']}"}
        rows = state.get("rows", [])
        return {"answer": f"{len(rows)} row(s)." if rows else "No rows."}

    def after(state: SQLState) -> str:
        if not state.get("error"):
            return "ok"
        return "repair" if state.get("attempts", 0) < max_attempts else "give_up"

    g = StateGraph(SQLState)
    for name, fn in [("introspect", introspect), ("generate", generate),
                     ("validate", validate), ("execute", execute), ("finalize", finalize)]:
        g.add_node(name, fn)

    g.add_edge(START, "introspect")
    g.add_edge("introspect", "generate")
    g.add_edge("generate", "validate")
    g.add_conditional_edges("validate", after, {"ok": "execute", "repair": "generate", "give_up": "finalize"})
    g.add_conditional_edges("execute", after, {"ok": "finalize", "repair": "generate", "give_up": "finalize"})
    g.add_edge("finalize", END)
    return g.compile()
