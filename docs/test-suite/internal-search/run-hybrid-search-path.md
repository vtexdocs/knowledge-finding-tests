# `run-hybrid-search-path.py`

## Purpose

Runs internal-search queries against the VTEX Docs Hybrid Search API and checks whether the issue's target document is returned in the top results.

## Required input

- Query source:
  - preferred: `data/test-suite/internal-search/all_queries.json`
  - fallback: `docs/test-suite/issues/*.md`
- Environment variables:
  - `HYBRID_SEARCH_API_URL`
  - `HYBRID_SEARCH_INTERNAL_KEY`

## Usage

```powershell
python "tools/test-suite/internal-search/run-hybrid-search-path.py"
```

## Parameters

### CLI parameters

| Parameter | Required | Type | Default | Example | Notes |
|---|---|---|---|---|---|
| `--run-id` | No | string | auto-generated timestamped ID | `--run-id hybrid-search-baseline` | If omitted, the script builds `hybrid-search-run-YYYY-MM-DD-HHmmss` |
| `--issues` | No | list of strings | all issues | `--issues audit-search-01 checkout-api-orders-01` | Filters the run to specific issue IDs |
| `--top-n` | No | integer | `10` | `--top-n 5` | Number of results stored per query |
| `--output-dir` | No | path | `results/internal-search` | `--output-dir "results/internal-search"` | Base directory where per-run folders are created |
| `--delay` | No | float | `0.5` | `--delay 1.0` | Delay between API calls in seconds |
| `--locale` | No | enum | `all` | `--locale en` | Allowed values: `en`, `es`, `pt`, `all` |
| `--no-analysis` | No | flag | `false` | `--no-analysis` | Skips the markdown analysis report |
| `--generate-api-call-results` | No | flag | `false` | `--generate-api-call-results` | Generates the combined internal-search comparison report if Algolia outputs exist |

### Environment variables

| Variable | Required | Type | Default | Example | Notes |
|---|---|---|---|---|---|
| `HYBRID_SEARCH_API_URL` | Yes | URL string | none | `HYBRID_SEARCH_API_URL=https://vtexdocs-edge.vtex.com` | Base URL for the Hybrid Search API |
| `HYBRID_SEARCH_INTERNAL_KEY` | Yes | string | none | `HYBRID_SEARCH_INTERNAL_KEY=xxxxxxxx` | Authentication key sent in `x-internal-access-key` |

## Example usage

Run all locales:

```powershell
python "tools/test-suite/internal-search/run-hybrid-search-path.py" --locale all
```

Run one issue:

```powershell
python "tools/test-suite/internal-search/run-hybrid-search-path.py" --issues audit-search-01 --locale en
```

Run and generate the combined comparison report:

```powershell
python "tools/test-suite/internal-search/run-hybrid-search-path.py" --locale all --generate-api-call-results
```

## Expected output

Output base directory:

- `results/internal-search/`

Variant subdirectory:

- `results/internal-search/hybrid-search/`

Per-run folder:

- `hybrid-search YYYY-MM-DD HH-MM`

Files written:

- `<run-id>.json`
- `analysis-<run-id>.md` unless `--no-analysis` is used

When `--generate-api-call-results` is used and recent Algolia outputs are available, the script also writes an internal-search comparison markdown report inside the current hybrid-search run folder.

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

Each top result preserves Hybrid Search fields such as:

- `id`
- `title`
- `filePath`
- `repository`
- `snippet`
- `content`
- `score`
- `metadata`
- `url`

## Behavior details

- The script loads `.env` from the workspace root if present.
- Locale filtering happens before the run when `all_queries.json` is loaded.
- The script can compare Hybrid Search with the latest Algolia runs if those files already exist.

