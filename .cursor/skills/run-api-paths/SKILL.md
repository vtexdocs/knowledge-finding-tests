---
name: run-api-paths
description: >-
  Runs the internal-search API path runners (Hybrid Search, and the deprecated
  Algolia) against test-suite issues and records whether the target doc was
  found and at what rank. Use when the user asks to run the internal-search /
  API paths, run Hybrid Search or Algolia runners, or collect internal-search
  results.
disable-model-invocation: true
---

# Run API paths — Test suite runners

Execute API-based internal-search runners. Two paths are supported:

1. **VTEX Docs Hybrid Search API** (BM25 + vector search + reranking) — the current internal-search path.
2. **Algolia Search API** (Help Center & Dev Portal indexes) — **deprecated, off by default**; run on demand. Hybrid Search supersedes it.

Both read test-suite issues, execute `query_internal` queries against their API, and record results in a unified format tracking whether `target_doc_url` was found and at which rank.

- **Query source:** `data/test-suite/internal-search/all_queries.json` (falls back to parsing `docs/test-suite/issues/` if absent)
- **Output:** JSON with `(issue_id, path, query, query_style, found, found_at_rank, top_results)`

## Quick start

From the project root:

```bash
# Hybrid Search (current path)
python tools/test-suite/internal-search/run-hybrid-search-path.py

# Algolia (deprecated, both indexes) — run only if you specifically need it
python tools/test-suite/internal-search/run-algolia-path.py --path both

# Skip analysis reports: add --no-analysis to either command
# Combined comparison report: run Algolia first, then Hybrid Search with --generate-api-call-results
```

Set API credentials in `.env` (see below) before running.

## Prerequisites

- Query source `data/test-suite/internal-search/all_queries.json` (regenerate with `python tools/test-suite/extract_queries_by_path.py`).
- API credentials set (see Environment variables).
- Python 3.7+.

## Environment variables (set in `.env` at project root)

Hybrid Search (current path):
```env
HYBRID_SEARCH_API_URL=https://vtexdocs-edge.vtex.com
HYBRID_SEARCH_INTERNAL_KEY=your_internal_access_key_here
```

Algolia (deprecated path — only needed if you run it):
```env
NEXT_PUBLIC_ALGOLIA_APP_ID=your_app_id_here
NEXT_PUBLIC_ALGOLIA_WRITE_KEY=your_api_key_here
```
Alternative names checked in order: App ID → `ALGOLIA_APP_ID` or `NEXT_PUBLIC_ALGOLIA_APP_ID`; API key → `ALGOLIA_SEARCH_API_KEY` (preferred), `ALGOLIA_SEARCH_KEY`, or `NEXT_PUBLIC_ALGOLIA_WRITE_KEY`.

## Input (ask the user)

1. **Which API path?** `hybrid-search` (default), `algolia` (deprecated), or `all`.

Then common params: **run ID** (default `{path}-run-YYYY-MM-DD-HHmmss`), **issue filter** (space-separated IDs; default all), **top N** (default 10), **API delay** seconds (default 0.5), **generate analysis** (on by default; `--no-analysis` to disable), **output directory** (default `results/internal-search`).

Path-specific: **Algolia index** `helpcenter|devportal|both` (default `both`); **locale** `en|es|pt|all` for both APIs (default `all`; note `devportal-docs` supports only `en`).

## Actions

1. **Output directories** — scripts create `results/internal-search/{hybrid-search,algolia-helpcenter,algolia-devportal}` automatically.
2. **Collect parameters** — apply defaults for missing values.
3. **Run the selected path(s)** — see commands below.

Hybrid Search:
```bash
python tools/test-suite/internal-search/run-hybrid-search-path.py \
  --run-id [run_id] --issues [ids] --top-n [n] \
  --output-dir "results/internal-search" --delay [s] --locale [en|es|pt|all] \
  [--no-analysis] [--generate-api-call-results]
```

Algolia (deprecated):
```bash
python tools/test-suite/internal-search/run-algolia-path.py \
  --path [helpcenter|devportal|both] --run-id [run_id] --issues [ids] --top-n [n] \
  --output-dir "results/internal-search" --delay [s] --locale [en|es|pt|all] [--no-analysis]
```

All paths (run Algolia first, then Hybrid Search to build the combined comparison report):
```bash
python tools/test-suite/internal-search/run-algolia-path.py --path both [options]
python tools/test-suite/internal-search/run-hybrid-search-path.py --generate-api-call-results [options]
```

4. **Save results** — unified JSON at `results/internal-search/{path}/{run_id}.json`.
5. **Analysis reports** (unless `--no-analysis`) — per-index markdown at `results/internal-search/{path}/analysis-{run_id}.md`; combined internal-search comparison at `results/internal-search/internal-search-comparison-{timestamp}.md` when Hybrid runs with `--generate-api-call-results`.

## Output

- JSON results file(s), per-index markdown analysis reports (default), the combined comparison report (with `--generate-api-call-results`), and console progress + summary.

## API details, report structure, comparison, and full examples

See [reference.md](reference.md).

## Reference

- Scripts: `tools/test-suite/internal-search/`
- Shared utilities: `tools/test-suite/internal-search/test_runner_utils.py`
- Query source: `data/test-suite/internal-search/all_queries.json`
- Test suite issues (for `target_doc_url`): `docs/test-suite/issues/`
- Unified output format: `docs/test-suite/results-layout.md`; query structure: [Phase 1 Overview](https://github.com/vtexdocs/education-26h1-kr1/blob/main/docs/Planning/Phase%201/Phase%201%20Overview.md) (§3.4), in the source KR project repo
