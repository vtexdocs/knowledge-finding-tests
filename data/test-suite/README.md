# Test suite data

Machine-readable inputs for the Phase 1 runners.

| Path | Contents |
|------|----------|
| `internal-search/all_queries.json` | Consolidated internal-search queries (from issue docs) |
| `docs-assistant/all_queries.json` | Docs Assistant / MCP-style query set |
| `external-search/all_queries.json` | External (Google) search queries |
| `external-llms/all_queries.json` | External LLM queries |
| `external-llms/.auth/` | Saved browser sessions for LLM runners (gitignored; create via `llm_runner.py login-*`) |

Regenerate the `all_queries.json` files with `python tools/test-suite/extract_queries_by_path.py`.
