# Knowledge-finding tests

A toolkit that measures whether VTEX documentation is discoverable: **when users look for help, do they find the right articles?** It simulates real searches across the channels people actually use, checks whether target documentation appears (and at what rank), and optionally scores how well AI-generated answers solve the user's problem.

## What it measures

The suite runs curated test cases across five "knowledge-finding paths", each in three locales (en, pt, es) and three query styles (naive, familiar, expert):

| Path | What it simulates |
| :--- | :--- |
| Internal search — Hybrid Search | The current internal search on the Help Center / Dev Portal |
| Internal search — Algolia _(deprecated)_ | Legacy search bar; off by default, superseded by Hybrid Search |
| Docs Assistant | The AI assistant on the docs site |
| External search — Google | A user Googling their problem |
| External LLMs — ChatGPT / Gemini | A user asking a chatbot directly |

Two complementary measurements:

- **Test Suite** — whether the correct documentation link appears in results, and at what position.
- **Quality Scoring** — whether AI text answers (Docs Assistant, ChatGPT, Gemini) actually solve the user's problem, on a 1–4 scale. It runs as an optional stage of the analysis.

Results feed a set of **dashboards** (per run, timeline, and before/after comparisons).

## Repository layout

| Path | Contents |
| :--- | :--- |
| `tools/test-suite/` | Data-collection runners, `analysis_system.py`, dashboard rendering |
| `tools/quality-scoring/` | AI answer quality-scoring pipeline |
| `data/test-suite/` | Generated query inputs (`*/all_queries.json`) |
| `docs/test-suite/` | Tool how-to and the 35 test-case definitions under `issues/` |
| `docs/test-suite-hand-off/` | Onboarding docs — start here |
| `docs/quality-scoring/` | Quality-scoring docs |
| `.cursor/skills/` | Cursor skills that automate common workflows |
| `results/` | Run outputs (starts empty except `README.md`) |

## Quick start

All commands run from the repository root. On Windows, use `py` if `python` opens the Microsoft Store.

1. Install runtimes: Python 3.x and Node.js.
2. Install dependencies:

```bash
pip install playwright requests
playwright install chromium
```

3. Create credentials: copy `.env.example` to `.env` at the repo root and fill in the values.
4. (Optional) Authenticate LLM providers for the ChatGPT / Gemini paths:

```bash
python "tools/test-suite/external-llms/llm_runner.py" login-chatgpt
python "tools/test-suite/external-llms/llm_runner.py" login-gemini
```

5. Run a single-issue smoke test:

```bash
python "tools/test-suite/extract_queries_by_path.py"
python "tools/test-suite/internal-search/run-hybrid-search-path.py" --issues audit-search-01 --locale en
node "tools/test-suite/docs-assistant/run-docs-assistant-path.js" --issues audit-search-01
python "tools/test-suite/analysis_system.py" run
python "tools/test-suite/analysis_system.py" run --score-quality   # optional quality scoring
```

## Documentation

Start with the hand-off guide: [`docs/test-suite-hand-off/README.md`](docs/test-suite-hand-off/README.md).

| Guide | Read it to |
| :--- | :--- |
| [test-suite.md](docs/test-suite-hand-off/test-suite.md) | Understand the core measurement system and full setup |
| [dashboards.md](docs/test-suite-hand-off/dashboards.md) | Navigate the visual reports |
| [quality-scoring.md](docs/test-suite-hand-off/quality-scoring.md) | Evaluate AI answer quality |
| [workflow-guide.md](docs/test-suite-hand-off/workflow-guide.md) | Know when to run tests and how to act on results |

For deeper reference beyond onboarding:

- **Per-tool details** — [`docs/test-suite/`](docs/test-suite/README.md) (one doc per runner + the analysis system) and [`docs/quality-scoring/`](docs/quality-scoring/README.md).
- **Automation** — common workflows ship as Cursor skills in [`.cursor/skills/`](.cursor/skills/); ask the Cursor agent to run one by name (e.g. _"run the quality-scoring-workflow skill"_).

## Notes

- `results/` ships empty (only `README.md`). Dashboards render once a first run produces data.
- Never commit secrets: `.env`, `data/test-suite/external-llms/.auth/`, and any `.playwright-profile/` are gitignored.
