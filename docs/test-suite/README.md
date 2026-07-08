# Test suite overview

This directory holds **test-suite documentation** and **issue definitions** for the knowledge-finding paths. Runnable scripts live under `tools/test-suite/`; query JSON inputs under `data/test-suite/`; run outputs under `results/`.

- Internal search via Algolia _(deprecated — off by default; Hybrid Search supersedes it)_
- Internal search via Hybrid Search API
- Docs Assistant API
- External search via Google Search Playwright
- External LLMs via ChatGPT or Gemini

The script-specific details live next to each script. This document gives the high-level map and the step-by-step process for running a full collection.

Results layout reference: [results-layout.md](results-layout.md)

## Quick start

Run all test suite steps from the **repository root** (`knowledge-finding-tests/`). On Windows, use `py` instead of `python` if the latter is not available.

```powershell
# 1. Install dependencies (one-time)
pip install playwright requests
playwright install chromium

# 2. Create a .env file at the repo root with your credentials
#    (see "Environment variables" section below for required keys)

# 3. Authenticate external LLM providers (one-time, repeat when sessions expire)
#    Close Chrome completely before running login-gemini
python "tools/test-suite/external-llms/llm_runner.py" login-chatgpt
python "tools/test-suite/external-llms/llm_runner.py" login-gemini

# 4. Run the full test suite (includes analysis at the end)
python "tools/test-suite/run_all_runners.py"
# After all data-collection steps finish, the script will ask:
#   "Proceed with the analysis report? [y/N]"
# Type 'y' to generate the analysis, or 'n' to skip it.

# Or with visible browser + captcha support for Google Search:
python "tools/test-suite/run_all_runners.py" --external-search-no-headless --external-search-wait-for-captcha

# Or skip steps you don't need:
python "tools/test-suite/run_all_runners.py" --skip external-llms

# Or continue past failures:
python "tools/test-suite/run_all_runners.py" --continue-on-error

# 5. (Optional) Generate a timeline dashboard to visualize trends across runs
python "tools/test-suite/render_analysis_dashboard.py" `
  --timeline-runs "results/analysis-system/<run-1>" "results/analysis-system/<run-2>"
# Each dashboard is saved as timeline_YYYY-MM-DD_HH-MM.html (not overwritten)
```

> **Heads up:** Browser-based steps (Google Search, ChatGPT, Gemini) may require human intervention during the run — reCAPTCHA challenges, rate-limit pop-ups, or session interruptions. Keep the browser visible and monitor periodically. See [Monitoring browser-based runs](#monitoring-browser-based-runs) for details.

For detailed configuration, prerequisites, and individual runner usage, see the sections below.

## Script map

| Path | Script | Script documentation |
|---|---|---|
| Query extraction | `tools/test-suite/extract_queries_by_path.py` | [extract_queries_by_path.md](extract_queries_by_path.md) |
| Parent runner | `tools/test-suite/run_all_runners.py` | [run_all_runners.md](run_all_runners.md) |
| Results normalization | `tools/test-suite/standardize_results_layout.py` | [results-layout.md](results-layout.md) |
| Unified analysis | `tools/test-suite/analysis_system.py` | [analysis-system.md](analysis-system.md) |
| Analysis dashboard (WIP) | `tools/test-suite/render_analysis_dashboard.py` | [analysis-dashboard.md](analysis-dashboard.md) |
| Internal search (deprecated) | `tools/test-suite/internal-search/run-algolia-path.py` | [run-algolia-path.md](internal-search/run-algolia-path.md) |
| Internal search | `tools/test-suite/internal-search/run-hybrid-search-path.py` | [run-hybrid-search-path.md](internal-search/run-hybrid-search-path.md) |
| Internal search shared module | `tools/test-suite/internal-search/test_runner_utils.py` | [test_runner_utils.md](internal-search/test_runner_utils.md) |
| Docs Assistant | `tools/test-suite/docs-assistant/run-docs-assistant-path.js` | [run-docs-assistant-path.md](docs-assistant/run-docs-assistant-path.md) |
| External search | `tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py` | [run_google_search_playwright.md](external-search/google-search-playwright/run_google_search_playwright.md) |
| External LLMs | `tools/test-suite/external-llms/llm_runner.py` | [llm_runner.md](external-llms/llm_runner.md) |

## Data collection flow

The scripts are designed to run in this order:

1. Prepare issue files in `docs/test-suite/issues/`
2. Generate path-specific `all_queries.json` files
3. Run each collection script for its path
4. Save raw outputs under `results/<path-family>/<variant>/<run-folder>/...`
5. Run the unified analysis system to generate processed JSON artifacts
6. Optionally render the current WIP static dashboard from a processed analysis run
7. Optionally generate comparison outputs and WIP comparison dashboards

## Preconditions

Before a full run, confirm these inputs are ready:

- Issue files exist in `docs/test-suite/issues/*.md`
- Queries are filled for the paths you want to run
- Each issue has an `issue_id`
- Each issue has `target_docs` and `other_helpful_docs` populated as the target-doc and helpful-doc ground truth
- Required credentials are available in environment variables or `.env`
- Playwright is installed for the browser-based scripts
- Auth state is recorded for external LLM runs

## Prerequisites

Before running all runners, make sure the local environment is ready.

### 1. Runtimes

- Python 3.x
- Node.js

> **Windows note:** The `python` command may not work on Windows because the default alias points to the Microsoft Store stub. Use `py` instead (the Python Launcher for Windows). All examples below use `python`, but replace it with `py` if needed. You can verify with `py --version`.

### 2. Python packages

Install the Python dependencies used by the browser-based and API-based runners:

```powershell
pip install playwright requests
```

Optional package:

```powershell
pip install python-dotenv
```

This is useful if you want scripts to load values from a local `.env` file automatically.

### 3. Playwright browser install

The browser-based runners require Playwright's Chromium browser:

```powershell
playwright install chromium
```

### 4. Environment variables

Some paths require credentials or internal access keys.

You can either set variables in your shell session or place them in a `.env` file at the **workspace root** (e.g. `knowledge-finding-tests/.env`). The runners load this file automatically via `load_env_file()`.

> **Important:** The `.env` file must be at the repository root, not inside `docs/` or `tools/`. The `.gitignore` already excludes `.env` files, so credentials will not be committed.

Example `.env` file:

```env
ALGOLIA_APP_ID=your-app-id
ALGOLIA_SEARCH_API_KEY=your-search-key
HYBRID_SEARCH_API_URL=https://vtexdocs-edge.vtex.com
HYBRID_SEARCH_INTERNAL_KEY=your-internal-key
```

#### Internal search: Algolia _(deprecated)_

> **Deprecated:** the Algolia path is off by default and superseded by Hybrid Search. These credentials are only needed if you explicitly run it with `--include algolia`.

Required:

- `ALGOLIA_APP_ID` or `NEXT_PUBLIC_ALGOLIA_APP_ID`
- one of:
  - `ALGOLIA_SEARCH_API_KEY`
  - `ALGOLIA_SEARCH_KEY`
  - `NEXT_PUBLIC_ALGOLIA_WRITE_KEY`

Example (PowerShell):

```powershell
$env:ALGOLIA_APP_ID="your-app-id"
$env:ALGOLIA_SEARCH_API_KEY="your-search-key"
```

#### Internal search: Hybrid Search API

Required:

- `HYBRID_SEARCH_API_URL`
- `HYBRID_SEARCH_INTERNAL_KEY`

Example (PowerShell):

```powershell
$env:HYBRID_SEARCH_API_URL="https://vtexdocs-edge.vtex.com"
$env:HYBRID_SEARCH_INTERNAL_KEY="your-internal-key"
```

### 5. External LLM authentication

External LLM runs require saved authenticated sessions before execution.

Run:

```powershell
python "tools/test-suite/external-llms/llm_runner.py" login-chatgpt
python "tools/test-suite/external-llms/llm_runner.py" login-gemini
```

> **Gemini login:** The `login-gemini` command copies authentication files from your local Chrome profile. **Chrome must be fully closed** before running it — including background processes. If you get `PermissionError: [WinError 32]`, check the system tray (bottom-right near the clock) for a Chrome icon and exit it, or use Task Manager (`Ctrl+Shift+Esc`) to end all `Google Chrome` processes.

This creates the auth files used by the runner under:

- `data/test-suite/external-llms/.auth/chatgpt.json`
- `data/test-suite/external-llms/.auth/gemini.json`

### 6. Input data

Make sure these exist before the collection run:

- issue files in `docs/test-suite/issues/*.md`
- filled query sections for the paths you want to test
- valid `issue_id` values
- `target_doc_url` where legacy runner compatibility still requires it

### 7. Recommended preflight checks

Before a full run, it is worth checking:

- `python --version`
- `node --version`
- `playwright install chromium` has already completed
- required env vars are loaded
- external LLM login files exist

## Warnings

- External LLM runs require authentication before execution. `llm_runner.py` will not work until a valid provider session has been saved with `login-chatgpt` and/or `login-gemini`.
- Google Search Playwright runs may trigger consent screens or reCAPTCHA challenges. Those runs can pause or fail unless you use a visible browser session and resolve the challenge manually.

### Monitoring browser-based runs

The browser-based steps (Google Search, ChatGPT, Gemini) can be interrupted at any time by provider-side checks that require human action. **Keep the browser window visible and monitor the run periodically.** Common interruptions:

- **Google Search:** reCAPTCHA challenges. Use `--external-search-no-headless --external-search-wait-for-captcha` so the browser stays visible and the script waits for you to solve the captcha before continuing.
- **ChatGPT:** Rate-limit pop-ups when too many requests are sent in a short period. You may need to click a dismiss button on the pop-up or wait a few minutes before the script can continue.
- **Gemini:** Similar rate-limit or session-related pop-ups that require manual dismissal or a short wait.

If any of these interruptions are not resolved, the script will either hang indefinitely or fail. Running with a visible browser (non-headless mode) makes it easier to spot and resolve these issues quickly.

## Full data collection run

If you want a single entrypoint, use the parent runner.

Before running it, make sure the external LLM providers are authenticated if you plan to include the `external-llms` step:

```powershell
python "tools/test-suite/external-llms/llm_runner.py" login-chatgpt
python "tools/test-suite/external-llms/llm_runner.py" login-gemini
```

Then run the full collection:

```powershell
python "tools/test-suite/run_all_runners.py"
```

If you do not want to run the external LLM path yet, you can skip it:

```powershell
python "tools/test-suite/run_all_runners.py" --skip external-llms
```

After all data-collection steps finish, the script will prompt:

```text
============================================================
Data collection finished. Ready to generate the analysis report.
============================================================

Proceed with the analysis report? [y/N]
```

Type `y` to generate the analysis report immediately, or `n` to skip it. You can always generate it later with:

```powershell
python "tools/test-suite/analysis_system.py" run
```

To skip the prompt entirely (e.g. for automated runs), use `--no-confirm-analysis`.

You can still run each child script individually when you want more control.

### 1. Generate the path query files

This step builds the `all_queries.json` inputs used by the downstream runners.

```powershell
python "tools/test-suite/extract_queries_by_path.py"
```

Expected outputs:

- `data/test-suite/internal-search/all_queries.json`
- `data/test-suite/docs-assistant/all_queries.json`
- `data/test-suite/external-search/all_queries.json`
- `data/test-suite/external-llms/all_queries.json`

### 2. Run internal search: Algolia _(deprecated, optional)_

> **Deprecated:** the Algolia path is off by default and superseded by Hybrid Search (step 3). Skip this step for normal runs. Run it only on demand — either directly (below) or via `run_all_runners.py --include algolia`, which prints a deprecation notice.

Run both Help Center and Dev Portal indices.

```powershell
python "tools/test-suite/internal-search/run-algolia-path.py" --path both --locale all
```

Expected outputs:

- New run folders in `results/internal-search/algolia-helpcenter/`
- New run folders in `results/internal-search/algolia-devportal/`
- Folder names like `algolia-helpcenter 2026-03-17 14-30`
- Folder names like `algolia-devportal 2026-03-17 14-30`
- Markdown analysis reports unless `--no-analysis` is used

### 3. Run internal search: Hybrid Search API

Hybrid Search is the current internal-search path. If you also ran the deprecated Algolia step, run this afterward so comparison reporting is available.

```powershell
python "tools/test-suite/internal-search/run-hybrid-search-path.py" --locale all --generate-api-call-results
```

Expected outputs:

- New run folders in `results/internal-search/hybrid-search/`
- Folder names like `hybrid-search 2026-03-17 14-30`
- Markdown analysis report unless `--no-analysis` is used
- Combined internal-search comparison report if Algolia results are already present

### 4. Run Docs Assistant collection

```powershell
node "tools/test-suite/docs-assistant/run-docs-assistant-path.js"
```

Expected outputs:

- New run folders in `results/docs-assistant/api/`
- Folder names like `docs-assistant 2026-03-17 14-30`
- Markdown analysis report unless `--no-generate-analysis` is used

### 5. Run external search

Use the Playwright-based Google Search runner to simulate a real Google search session.

Warning: Google may show consent or reCAPTCHA pages during collection. If that happens, rerun with a visible browser and captcha-wait support:

```powershell
python "tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py" run
```

Expected output:

- New run folders in `results/external-search/google-search-playwright/`
- Folder names like `google-search-playwright 2026-03-17 14-30`

### 6. Run external LLM collection

If this is the first time running a provider, save auth first:

Warning: these runs require an authenticated saved session before the parent workflow can complete successfully.

```powershell
python "tools/test-suite/external-llms/llm_runner.py" login-chatgpt
python "tools/test-suite/external-llms/llm_runner.py" login-gemini
```

Then run the provider you want:

```powershell
python "tools/test-suite/external-llms/llm_runner.py" run --provider chatgpt --locale all
python "tools/test-suite/external-llms/llm_runner.py" run --provider gemini --locale all
```

Expected outputs:

- Timestamped run folders in `results/external-llms/chatgpt/` or `results/external-llms/gemini/`
- Folder names like `external-llms-chatgpt 2026-03-17 14-30`
- Folder names like `external-llms-gemini 2026-03-17 14-30`
- One markdown result per `(issue, locale, style)`
- `run_metadata.json` per run folder

## Recommended smoke test flow

Before a full baseline run, a small smoke test is safer:

1. Regenerate `all_queries.json`
2. Run one or two issues per path
3. Confirm outputs are written where expected
4. Confirm credentials and auth are valid
5. Run the full collection

Example smoke test commands:

```powershell
python "tools/test-suite/extract_queries_by_path.py"
python "tools/test-suite/internal-search/run-algolia-path.py" --path helpcenter --issues audit-search-01 --locale en
python "tools/test-suite/internal-search/run-hybrid-search-path.py" --issues audit-search-01 --locale en
node "tools/test-suite/docs-assistant/run-docs-assistant-path.js" --issues audit-search-01
python "tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py" run --issue audit-search-01 --locale en
python "tools/test-suite/external-llms/llm_runner.py" run --provider chatgpt --limit 3 --locale en
```

## Output locations

| Path | Output location |
|---|---|
| Internal search Algolia | `results/internal-search/algolia-helpcenter/` and `results/internal-search/algolia-devportal/` with per-run folders like `algolia-helpcenter YYYY-MM-DD HH-MM` |
| Internal search Hybrid | `results/internal-search/hybrid-search/` with per-run folders like `hybrid-search YYYY-MM-DD HH-MM` |
| Docs Assistant | `results/docs-assistant/api/` with per-run folders like `docs-assistant YYYY-MM-DD HH-MM` |
| External search Playwright | `results/external-search/google-search-playwright/` with per-run folders like `google-search-playwright YYYY-MM-DD HH-MM` |
| External LLMs | `results/external-llms/<provider>/` with per-run folders like `external-llms-chatgpt YYYY-MM-DD HH-MM` |

## Post-collection: analysis and timeline dashboard

After collecting data, use the analysis system and timeline dashboard to interpret results.

### Generate an analysis report

If you skipped the analysis step during the collection run, generate it manually:

```powershell
python "tools/test-suite/analysis_system.py" run
```

The report is written to `results/analysis-system/analysis-system YYYY-MM-DD HH-MM/`. See [analysis-system.md](analysis-system.md) for details on output artifacts.

### Generate a timeline dashboard

To visualize metric trends across multiple analysis runs:

```powershell
python "tools/test-suite/render_analysis_dashboard.py" `
  --timeline-runs "results/analysis-system/analysis-system 2026-03-25 17-12" `
                  "results/analysis-system/analysis-system 2026-04-02 13-38"
```

Each dashboard is saved with a timestamped filename (e.g. `timeline_2026-04-08_11-38.html`) under `results/analysis-system/timeline-dashboard/`. Previous dashboards are preserved — the script never overwrites existing files.

Use `--output-dir` to write to a custom location.

### Compare analysis runs

To compare two or more analysis runs, see the `compare`, `compare-chain`, and `compare-all` commands in [analysis-system.md](analysis-system.md#8-comparison-runs).

## Notes

- Internal-search runners can fall back to issue markdown parsing if `all_queries.json` is missing.
- External search and external LLM scripts are easiest to run after the extraction step has already created their `all_queries.json` files.
- The browser-based scripts are more likely to hit consent screens, captchas, or session-expiration issues than the API-based scripts.