# `test_runner_utils.py`

## Purpose

Shared utility module for the internal-search runners.

This file is not a standalone command-line tool. It provides reusable logic for:

- loading `.env`
- parsing issue markdown files
- loading issues from `all_queries.json`
- normalizing and comparing URLs
- computing statistics
- generating comparison reports
- deduplicating repeated results

## Used by

- `run-algolia-path.py`
- `run-hybrid-search-path.py`

## How to use

Import the functions you need from another Python script in the same directory.

Example:

```python
from test_runner_utils import load_issues_from_all_queries_json, check_expected_doc_found
```

## Parameters

This module has no command-line parameters.

### Important function inputs

| Function / input | Required | Type | Default | Example | Notes |
|---|---|---|---|---|---|
| `load_env_file()` | No | function call | n/a | `load_env_file()` | Loads `.env` from the workspace root if present |
| `parse_issue_file(filepath)` | Yes | `Path` | none | `parse_issue_file(Path("docs/test-suite/issues/audit-search-01.md"))` | Parses issue metadata and `query_internal` |
| `load_issues_from_all_queries_json(all_queries_path, issues_dir, filter_issue_ids, locale_filter)` | Yes for first two args | `Path`, `Path`, optional list, optional string | `filter_issue_ids=None`, `locale_filter=None` | `load_issues_from_all_queries_json(p, issues_dir, ["audit-search-01"], "en")` | Main loader used by the internal-search runners |
| `check_expected_doc_found(top_results, target_url)` | Yes | list of dicts, string | none | `check_expected_doc_found(results, target_url)` | Returns `(found, rank)`. The function name is legacy; use it as the target-doc matcher. |
| `generate_apis_comparison_analysis(...)` | Yes | multiple result dicts + output path | none | `generate_apis_comparison_analysis(helpcenter, devportal, out_path)` | Writes the internal-search comparison report |

## Key inputs handled by this module

- `.env` in the workspace root
- `docs/test-suite/issues/*.md`
- `data/test-suite/internal-search/all_queries.json`
- internal-search runner result objects

## Key outputs produced by this module

The module itself does not write files directly unless one of its report-generation helpers is called from another script.

Its functions can produce:

- parsed issue objects
- normalized URLs
- pass/fail and rank comparisons
- grouped style statistics
- markdown comparison reports

## Notes

- URL matching is intentionally more flexible than exact-string equality.
- The helper supports both preferred `target_doc_url` / `target_docs` fields and legacy `expected_doc_url` / `expected_docs` compatibility inputs.

