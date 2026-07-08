# `run-algolia-path.py`

> **Deprecated:** Algolia is being deprecated in the portals following the baseline, and **Hybrid Search** ([`run-hybrid-search-path.py`](run-hybrid-search-path.md)) is now the internal-search path. This runner is **off by default** in `run_all_runners.py`; it remains fully runnable on demand via `--include algolia` (prints a deprecation notice) or by calling the script directly. The code, docs, and historical results are kept for recoverability.

## Purpose

Runs internal-search queries against the VTEX Algolia indices:

- `helpcenter-docs`
- `devportal-docs`

For each query, the script captures top search hits and checks whether the issue's `target_doc_url` appears in the results.

## Required input

- Query source:
  - preferred: `data/test-suite/internal-search/all_queries.json`
  - fallback: `docs/test-suite/issues/*.md`
- Environment variables:
  - `ALGOLIA_APP_ID` or `NEXT_PUBLIC_ALGOLIA_APP_ID`
  - one of:
    - `ALGOLIA_SEARCH_API_KEY`
    - `ALGOLIA_SEARCH_KEY`
    - `NEXT_PUBLIC_ALGOLIA_WRITE_KEY`

## Usage

```powershell
python "tools/test-suite/internal-search/run-algolia-path.py"
```

## Parameters

### CLI parameters

| Parameter | Required | Type | Default | Example | Notes |
|---|---|---|---|---|---|
| `--path` | No | enum | `both` | `--path helpcenter` | Allowed values: `helpcenter`, `devportal`, `both` |
| `--run-id` | No | string | auto-generated timestamped ID | `--run-id algolia-helpcenter-baseline` | If omitted, the script builds `algolia-{path}-run-YYYY-MM-DD-HHmmss` |
| `--issues` | No | list of strings | all issues | `--issues audit-search-01 checkout-api-orders-01` | Filters the run to specific issue IDs |
| `--top-n` | No | integer | `10` | `--top-n 5` | Number of results stored per query |
| `--output-dir` | No | path | `results/internal-search` | `--output-dir "results/internal-search"` | Base directory where per-run folders are created |
| `--delay` | No | float | `0.5` | `--delay 1.0` | Delay between API calls in seconds |
| `--locale` | No | enum | `all` | `--locale en` | Allowed values: `en`, `es`, `pt`, `all` |
| `--no-analysis` | No | flag | `false` | `--no-analysis` | Skips generation of the markdown analysis report |

### Environment variables

| Variable | Required | Type | Default | Example | Notes |
|---|---|---|---|---|---|
| `ALGOLIA_APP_ID` | Yes, unless `NEXT_PUBLIC_ALGOLIA_APP_ID` is set | string | none | `ALGOLIA_APP_ID=ABC123` | Primary application ID |
| `NEXT_PUBLIC_ALGOLIA_APP_ID` | Yes, unless `ALGOLIA_APP_ID` is set | string | none | `NEXT_PUBLIC_ALGOLIA_APP_ID=ABC123` | Alternate application ID source |
| `ALGOLIA_SEARCH_API_KEY` | Yes, unless another accepted key is set | string | none | `ALGOLIA_SEARCH_API_KEY=xxxxxxxx` | Preferred search key |
| `ALGOLIA_SEARCH_KEY` | Yes, unless another accepted key is set | string | none | `ALGOLIA_SEARCH_KEY=xxxxxxxx` | Alternate search key |
| `NEXT_PUBLIC_ALGOLIA_WRITE_KEY` | Yes, unless another accepted key is set | string | none | `NEXT_PUBLIC_ALGOLIA_WRITE_KEY=xxxxxxxx` | Also accepted by this script |

## Example usage

Run both indices:

```powershell
python "tools/test-suite/internal-search/run-algolia-path.py" --path both --locale all
```

Run only Help Center:

```powershell
python "tools/test-suite/internal-search/run-algolia-path.py" --path helpcenter --locale en
```

Run a filtered sample:

```powershell
python "tools/test-suite/internal-search/run-algolia-path.py" --path devportal --issues audit-search-01 checkout-api-orders-01 --locale en --top-n 5
```

## Expected output

Output base directory:

- `results/internal-search/`

Variant subdirectories:

- `results/internal-search/algolia-helpcenter/`
- `results/internal-search/algolia-devportal/`

Per-run folders:

- `algolia-helpcenter YYYY-MM-DD HH-MM`
- `algolia-devportal YYYY-MM-DD HH-MM`

Files written:

- `<run-id>.json`
- `analysis-<run-id>.md` unless `--no-analysis` is used

The JSON result contains:

- `run_id`
- `path`
- `timestamp`
- `config`
- `summary_by_issue`
- `errors`
- `results`

Each query result includes:

- `issue_id`
- `path`
- `query`
- `query_style`
- `query_locale`
- `target_doc_url`
- `found`
- `found_at_rank`
- `top_results`
- `algolia_response`

## Behavior details

- When `--path devportal` is used, the script forces English-only queries because `devportal-docs` supports only `en`.
- When `--path both` is used, Help Center can run all locales while Dev Portal is filtered to English.
- The script loads `.env` from the workspace root if present.

## Typical workflow

1. Generate `data/test-suite/internal-search/all_queries.json`
2. Export Algolia credentials
3. Run the script for `helpcenter`, `devportal`, or `both`
4. Review the JSON output and markdown analysis

