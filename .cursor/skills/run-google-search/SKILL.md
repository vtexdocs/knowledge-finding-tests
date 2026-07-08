---
name: run-google-search
description: >-
  Explains that external Google search is implemented with the Playwright runner
  (no Custom Search API key) and points to the run-google-search-playwright
  skill. Use when the user asks about the Google Custom Search API path,
  run_google_search.py, or how external Google search is run.
disable-model-invocation: true
---

# Run Google Search — External Search (Custom Search API)

This repository does **not** ship the historical **Google Custom Search JSON API** runner (`run_google_search.py`). External search is implemented with the **Playwright** runner, which drives a real browser against google.com (no API key).

Use the `run-google-search-playwright` skill (or run the script below) for Google external search.

- **Script:** `tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py`
- **Input:** `data/test-suite/external-search/all_queries.json`
- **Output:** under `results/external-search/google-search-playwright/` (per-run folders; see that runner's README)

## Prerequisites

- `pip install playwright && playwright install chromium`
- Regenerated queries: `python tools/test-suite/extract_queries_by_path.py`

## Reference

- Playwright runner: `run-google-search-playwright` skill
- Runner README: `docs/test-suite/external-search/google-search-playwright/README.md`
