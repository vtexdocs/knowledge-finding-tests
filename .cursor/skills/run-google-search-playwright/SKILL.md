---
name: run-google-search-playwright
description: >-
  Runs the Google Search Playwright runner that drives a real Chromium browser
  against google.com, parses the SERP, and writes structured results. Use when
  the user asks to run the external Google search path, collect Google SERP
  results, or run run_google_search_playwright.py.
disable-model-invocation: true
---

# Run Google Search Playwright

Execute the **Google Search Playwright** runner: opens a browser (Playwright Chromium), navigates to `https://www.google.com/search?q=...` for each query in `all_queries.json`, parses the SERP for the first 7 organic results, and writes a timestamped JSON export (date + time so multiple runs per day do not overwrite).

- **Script:** `tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py`
- **Input:** `data/test-suite/external-search/all_queries.json`
- **Output:** `results/external-search/google-search-playwright/` (per-run folders — see runner README)

No API key required. Requires Playwright and Chromium: `pip install playwright && playwright install chromium`.

## Input (options)

- `--limit-issues N` — run only the first N issues.
- `--issue ISSUE_ID` — run only queries from that issue (e.g. `checkout-api-orders-01`).
- `--locale en|es|pt` — run only queries for that locale.
- `--style naive|familiar|expert` — run only queries with that style.
- `--query "exact text"` — run only the query whose text matches exactly.
- `--dry-run` — list queries only, no browser.
- `--no-headless` — show the browser window (helps with consent/captcha).
- `--wait-for-captcha` — on consent/captcha, poll the browser automatically until search results appear; solve it in the window, no Enter needed.
- Filters can be combined (e.g. `--issue checkout-api-orders-01 --locale pt`).

## Actions

1. Resolve script path: `tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py`.
2. Working directory: repository root (defaults resolve from repo root).
3. Run `run` with the desired options:

```bash
python tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py run \
  --limit-issues 3 --locale en --no-headless --wait-for-captcha --delay 2.0
```

4. Report success or failure and the output file path.

## Reference

- Script: `tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py`
- README: `docs/test-suite/external-search/google-search-playwright/README.md`
