"""LLM abstraction that turns a question + schema into a SQL string."""
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLM(Protocol):
    def complete(self, prompt: str) -> str:
        ...


class ScriptedLLM:
    """Returns queued SQL strings in order — for deterministic tests/demos."""

    def __init__(self, sqls: list[str]):
        self._sqls = list(sqls)
        self.calls: list[str] = []

    def complete(self, prompt: str) -> str:
        self.calls.append(prompt)
        if not self._sqls:
            raise AssertionError("ScriptedLLM ran out of SQL")
        return self._sqls.pop(0)


class OpenAILLM:
    def __init__(self, model: str = "gpt-4o-mini"):
        from langchain_openai import ChatOpenAI  # lazy

        self._chat = ChatOpenAI(model=model, temperature=0)

    def complete(self, prompt: str) -> str:
        text = self._chat.invoke(prompt).content.strip()
        # strip ``` fences a model may add
        return text.replace("```sql", "").replace("```", "").strip()
