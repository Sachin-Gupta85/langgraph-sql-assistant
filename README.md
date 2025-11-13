# 🗄️ langgraph-sql-assistant — natural language → SQL over SQLite

> A **LangGraph** agent that introspects a SQLite schema, asks an LLM for a query, **validates it through a read-only safety gate**, runs it, and **repairs** failing queries within an attempt budget.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-1.x-1c3c3c)
![Tests](https://img.shields.io/badge/tests-pytest%20(8)-brightgreen)

## 🧠 The loop
```
introspect ─▶ generate ─▶ validate ─┬ valid ─▶ execute ─┬ ok ──▶ finalize ─▶ END
                 ▲                   │                   │
                 └─ repair ◀ invalid ┘      db error ────┘   (while attempts remain)
```
- **Introspect** reads the live schema (`PRAGMA table_info`) into the prompt.
- **Safety gate** accepts only a *single read-only* `SELECT`/`WITH`, blocks
  mutations and statement chaining, and injects a `LIMIT`.
- **Repair loop** feeds validation *and* execution errors back to the model and
  retries, up to `max_attempts`, then gives up gracefully.

## 🧩 Swappable LLM
The graph depends on an `LLM.complete(prompt)` protocol. Tests/demos inject a
`ScriptedLLM` (deterministic SQL), so **everything runs green with no API key**;
production injects `OpenAILLM` (LangChain `ChatOpenAI`, lazy import).

## 🚀 Run
```bash
pip install -r requirements.txt
python -m sql_assistant        # builds a sample DB and answers a question offline
```

## ✅ Test
```bash
pip install -r requirements-dev.txt && python -m pytest -q
```
Covers the safety gate, schema introspection, the happy path, repair after a
**validation** failure, repair after a **DB execution** error, and the give-up path.

## ⚠️ Safety note
The gate is defence-in-depth for a demo. For untrusted input, also connect with a
read-only user/role and least privilege at the database layer.

## 📝 License
MIT — see [LICENSE](LICENSE).
