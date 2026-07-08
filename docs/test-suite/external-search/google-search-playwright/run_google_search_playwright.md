# `run_google_search_playwright.py`

## Purpose

Runs Google searches in a browser with Playwright, extracts the first organic results from the SERP, and stores them in the external-search test format.

This is the browser-simulation alternative to the Google Custom Search API script.

## Warning

Google may interrupt runs with consent prompts or reCAPTCHA challenges. For larger or repeated runs, expect that some sessions may require manual intervention.

## Required input

- `data/test-suite/external-search/all_queries.json`
- Python Playwright package
- Installed Chromium browser via Playwright

## Usage

```powershell
python "tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py" run
```

## Parameters

| Parameter | Required | Type | Default | Example | Notes |
|---|---|---|---|---|---|
| `--queries` | No | path | `data/test-suite/external-search/all_queries.json` | `--queries "data/test-suite/external-search/all_queries.json"` | Source file for the external-search query set |
| `--output-dir` | No | path | `results/external-search` | `--output-dir "results/external-search"` | Base output directory |
| `--limit-issues` | No | integer | all issues | `--limit-issues 3` | Runs only the first N issues after filtering |
| `--issue` | No | string | none | `--issue audit-search-01` | Runs only one issue ID |
| `--locale` | No | enum | all locales in selected issues | `--locale pt` | Allowed values: `en`, `es`, `pt` |
| `--style` | No | enum | all styles | `--style expert` | Allowed values: `naive`, `familiar`, `expert` |
| `--query` | No | string | none | `--query "checkout api update order request body format"` | Exact query text match |
| `--delay` | No | float | `2.0` | `--delay 3.0` | Delay between browser requests in seconds |
| `--dry-run` | No | flag | `false` | `--dry-run` | Prints the selected workload without launching the browser |
| `--no-headless` | No | flag | `false` | `--no-headless` | Shows the browser window |
| `--wait-for-captcha` | No | flag | `false` | `--wait-for-captcha` | Waits for manual captcha or consent resolution |
| `--no-persistent-profile` | No | flag | `false` | `--no-persistent-profile` | Uses an ephemeral browser instead of the persistent profile directory |
| `--debug-save-html` | No | flag | `false` | `--debug-save-html` | Saves SERP HTML when result extraction fails |

## Example usage

Full run:

```powershell
python "tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py" run
```

One issue in a visible browser:

```powershell
python "tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py" run --issue checkout-api-orders-01 --locale pt --no-headless --wait-for-captcha
```

Recommended mode when Google is likely to challenge the session:

```powershell
python "tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py" run --no-headless --wait-for-captcha
```

Only expert queries:

```powershell
python "tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py" run --style expert
```

Exact-query test:

```powershell
python "tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py" run --query "checkout api update order request body format"
```

## Expected output

Default output base:

- `results/external-search/`

Path subfolder:

- `google-search-playwright/`

Per-run folder:

- `google-search-playwright YYYY-MM-DD HH-MM`

The JSON contains:

- `path`
- `runner`
- `generated_at`
- `source_file`
- `session_1`

Each `session_1.output` issue contains:

- `issue_id`
- `source_file`
- `queries`

Each query contains:

- `query`
- `style`
- `output_urls`
- `ai_overview_content`

Each `output_urls` entry contains:

- `rank`
- `url_address`
- `url_description`

Current output file name:

- `results.json`

## Behavior details

- The script attempts to extract AI Overview content when present.
- Organic results are normalized to remove Google-internal wrapper URLs.
- If Google shows consent or captcha pages, `--no-headless --wait-for-captcha` is the safest mode.
- `--debug-save-html` helps when selectors fail and no results are extracted.
- reCAPTCHA can still interrupt long runs even in a persistent profile, so plan for manual supervision when collecting a full dataset.
