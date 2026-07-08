# Test Suite

The test suite simulates how users search for VTEX documentation and measures whether the correct articles appear in the results.

---

## What it is

A collection of scripts that send realistic queries to five "knowledge-finding paths" and check if target documentation shows up:

| Path | What it simulates |
| :--- | :--- |
| **Internal search (Algolia)** _(deprecated)_ | User typing in the Help Center or Dev Portal search bar. **Off by default** — superseded by Hybrid Search. |
| **Internal search (Hybrid Search)** | User using the newer hybrid-search experience (the current internal-search path) |
| **Docs Assistant** | User asking the AI assistant on the docs site |
| **External search (Google)** | User Googling their problem |
| **External LLMs (ChatGPT / Gemini)** | User asking a chatbot directly |

Each path is tested in **3 locales** (en, pt, es) and **3 query styles** (naive, familiar, expert) across **35 curated test cases**.

---

## What it can do

- Measure whether your target article appears when users search — and at what position.
- Compare discoverability across English, Portuguese, and Spanish.
- Compare how different query styles perform (naive vs. expert).
- Run before/after to quantify the impact of content changes.
- Produce JSON analysis artifacts that feed into dashboards (see [dashboards.md](dashboards.md)).

## What it cannot do

- Score the quality of AI-generated text answers (use [Quality Scoring](quality-scoring.md) for that).
- Run fully unattended for browser-based paths — Google, ChatGPT, and Gemini may show CAPTCHAs or rate-limit pop-ups that require manual intervention.
- Test unpublished content — all paths hit live endpoints.
- Run fast — a full 35-issue run takes hours because steps run sequentially.

---

## The tools

| Script | Role |
| :--- | :--- |
| `tools/test-suite/extract_queries_by_path.py` | Reads issue markdown files and generates query JSON for each path |
| `tools/test-suite/run_all_runners.py` | Runs all steps in sequence (single entry point) |
| `tools/test-suite/internal-search/run-algolia-path.py` | Queries Algolia indices (Help Center + Dev Portal). **Deprecated, off by default** — run on demand with `--include algolia`; Hybrid Search is the replacement. |
| `tools/test-suite/internal-search/run-hybrid-search-path.py` | Queries the Hybrid Search API |
| `tools/test-suite/docs-assistant/run-docs-assistant-path.js` | Queries the Docs Assistant API |
| `tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py` | Simulates Google searches via browser |
| `tools/test-suite/external-llms/llm_runner.py` | Automates ChatGPT / Gemini via browser |
| `tools/test-suite/analysis_system.py` | Processes raw results and computes metrics |
| `tools/test-suite/render_analysis_dashboard.py` | Generates HTML dashboards from analysis data |

---

## Prerequisites (one-time setup)

All commands run from the **repository root**. On Windows, use `py` instead of `python` if the latter opens the Microsoft Store.

### 1. Install runtimes

- Python 3.x (`python --version` or `py --version`)
- Node.js (`node --version`)

### 2. Install dependencies

```powershell
pip install playwright requests
playwright install chromium
```

### 3. Create credentials file

Create `.env` at the repo root:

```env
ALGOLIA_APP_ID=your-app-id
ALGOLIA_SEARCH_API_KEY=your-search-key
HYBRID_SEARCH_API_URL=https://vtexdocs-edge.vtex.com
HYBRID_SEARCH_INTERNAL_KEY=your-internal-key
```

### 4. Authenticate LLM providers

```powershell
python "tools/test-suite/external-llms/llm_runner.py" login-chatgpt
python "tools/test-suite/external-llms/llm_runner.py" login-gemini
```

> **Gemini:** Chrome must be completely closed before running `login-gemini`. If you get `WinError 32`, end all Chrome processes in Task Manager.

---

## How to use

### Run the full test suite

```powershell
python "tools/test-suite/extract_queries_by_path.py"
python "tools/test-suite/run_all_runners.py" --external-search-no-headless --external-search-wait-for-captcha
```

The script prompts whether to generate analysis after collection. Type `y`.

### Test a single issue (smoke test)

```powershell
python "tools/test-suite/extract_queries_by_path.py"
python "tools/test-suite/internal-search/run-hybrid-search-path.py" --issues audit-search-01 --locale en
node "tools/test-suite/docs-assistant/run-docs-assistant-path.js" --issues audit-search-01
python "tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py" run --issue audit-search-01 --locale en --no-headless --wait-for-captcha
python "tools/test-suite/analysis_system.py" run
# Optional (deprecated Algolia path, run only if you need it):
python "tools/test-suite/internal-search/run-algolia-path.py" --path both --issues audit-search-01 --locale en
```

### Compare before/after a content change

```powershell
# Before: run and generate analysis
python "tools/test-suite/run_all_runners.py" --no-confirm-analysis
python "tools/test-suite/analysis_system.py" run --analysis-id "before-change"

# (Make your content change and publish)

# After: run and generate analysis
python "tools/test-suite/run_all_runners.py" --no-confirm-analysis
python "tools/test-suite/analysis_system.py" run --analysis-id "after-change"

# Compare
python "tools/test-suite/analysis_system.py" compare `
  --baseline "results/analysis-system/<before-folder>" `
  --candidate "results/analysis-system/<after-folder>"
```

---

## Key metrics

| Metric | Meaning |
| :--- | :--- |
| **Target pass rate** | % of queries where the correct article appeared in results |
| **MRR (Mean Reciprocal Rank)** | Average of 1/rank — higher means target appears earlier (1.0 = always first) |
| **Helpful pass rate** | % of queries where at least one partially-relevant article appeared |
| **Not available** | Query excluded because the path/locale doesn't apply (e.g., Dev Portal is English-only) |

For what these mean in practice and how to improve them, see [workflow-guide.md](workflow-guide.md#what-each-metric-means-for-users).

---

## How to create a new test case

Each test case is a markdown file in `docs/test-suite/issues/`. Use the following template:

### Template

```markdown
# Issue: <Short description>

| Field | Value |
| :--- | :--- |
| **issue_id** | <unique-slug-nn> |
| **persona** | <Developer / Decision maker / Store operator / Agency partner> |
| **product** | <Product or feature area> |
| **user_intent** | <What the user wants to accomplish> |
| **target_doc_url** | <Primary target URL> |
| **surface** | <help-center / developers-portal> |
| **target_docs** | ["<URL-1>", "<URL-2>"] |
| **other_helpful_docs** | ["<URL-A>", "<URL-B>"] |
| **source** | <How this issue was identified> |

---

## Queries by path

### A — External search (Google)

| locale | style | query |
| :--- | :--- | :--- |
| en | naive | <...> |
| en | familiar | <...> |
| en | expert | <...> |
| pt | naive | <...> |
| pt | familiar | <...> |
| pt | expert | <...> |
| es | naive | <...> |
| es | familiar | <...> |
| es | expert | <...> |

**Array (query_external):**

```json
[
  { "locale": "en", "style": "naive", "query": "..." },
  { "locale": "en", "style": "familiar", "query": "..." },
  { "locale": "en", "style": "expert", "query": "..." },
  { "locale": "pt", "style": "naive", "query": "..." },
  { "locale": "pt", "style": "familiar", "query": "..." },
  { "locale": "pt", "style": "expert", "query": "..." },
  { "locale": "es", "style": "naive", "query": "..." },
  { "locale": "es", "style": "familiar", "query": "..." },
  { "locale": "es", "style": "expert", "query": "..." }
]
```

### B — Internal search (Algolia / Hybrid Search)

(Same table + JSON structure as section A)

### C — Docs assistant API (MCP-backed)

(Same table + JSON structure as section A)

### D — External LLMs

(Same table + JSON structure as section A)

### Writing good queries

| Path | How users phrase queries |
| :--- | :--- |
| **Google** | Full questions; include "vtex" since Google needs context |
| **Internal search** | Shorter keywords; omit "vtex" — user is already on the site |
| **Docs Assistant** | Conversational but concise |
| **LLMs** | Full questions, as if asking a knowledgeable person |

Query styles:

| Style | Description | Example |
| :--- | :--- | :--- |
| **naive** | No prior VTEX knowledge | "how to refund a customer payment on vtex" |
| **familiar** | Uses correct VTEX terms | "vtex payment refund process" |
| **expert** | Minimal keywords | "refund" |

### After creating the issue

```powershell
python "tools/test-suite/extract_queries_by_path.py"
python "tools/test-suite/internal-search/run-hybrid-search-path.py" --issues <your-issue-id> --locale en
```

---

## Troubleshooting

| Problem | Solution |
| :--- | :--- |
| `python` opens Microsoft Store | Use `py` instead |
| Missing credentials error | Check `.env` at repo root (not inside `docs/` or `tools/`) |
| LLM auth expired | Re-run `login-chatgpt` / `login-gemini` |
| Gemini login: `WinError 32` | Close all Chrome processes (including system tray), then retry |
| Google CAPTCHA blocks the run | Add `--no-headless --wait-for-captcha` and solve manually |
| Run fails partway | Add `--continue-on-error` to skip failing steps |
| New issue not picked up | Verify `issue_id` exists in file and JSON arrays are valid |
