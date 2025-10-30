from __future__ import annotations

from .graph import build_graph
from .llm import LLM


def ask(question: str, db_path: str, llm: LLM, max_attempts: int = 3) -> dict:
    graph = build_graph(llm, db_path, max_attempts=max_attempts)
    return graph.invoke({"question": question})
