# `extract_queries_by_path.py`

## Purpose

Builds one path-specific query file from the issue markdown files in `docs/test-suite/issues`.

Generated outputs:

- `data/test-suite/internal-search/all_queries.json`
- `data/test-suite/docs-assistant/all_queries.json`
- `data/test-suite/external-search/all_queries.json`
- `data/test-suite/external-llms/all_queries.json`

## How it works

The script scans each issue markdown file, extracts:

- `issue_id`
- query blocks for query types `A`, `B`, `C`, and `D`
- localized query entries with:
  - `locale`
  - `style`
  - `query`

Then it groups the queries by path and writes a JSON payload per destination folder.

## Required input

- Issue files in `docs/test-suite/issues/*.md`
- Each issue should contain:
  - a valid issue ID
  - one or more query sections
  - query entries using valid styles:
    - `naive`
    - `familiar`
    - `expert`

Accepted section mappings:

- `A` -> External search
- `B` -> Internal search
- `C` -> Docs assistant
- `D` -> External LLMs

## Usage

```powershell
python "tools/test-suite/extract_queries_by_path.py"
```

## Parameters

| Parameter | Required | Type | Default | Example | Notes |
|---|---|---|---|---|---|
| `--issues-dir` | No | path | `docs/test-suite/issues` | `--issues-dir "docs/test-suite/issues"` | Directory containing issue markdown files |
| `--filename` | No | string | `all_queries.json` | `--filename baseline_queries.json` | Output filename written inside each path folder |

## Example usage

Default run:

```powershell
python "tools/test-suite/extract_queries_by_path.py"
```

Custom filename:

```powershell
python "tools/test-suite/extract_queries_by_path.py" --filename baseline_queries.json
```

Custom issue source:

```powershell
python "tools/test-suite/extract_queries_by_path.py" --issues-dir "docs/test-suite/issues"
```

## Expected output

Each generated file has this structure:

```json
{
  "path": "Internal search",
  "generated_from": "docs/test-suite/issues",
  "total_issues": 12,
  "total_queries": 108,
  "issues": [
    {
      "issue_id": "audit-search-01",
      "source_file": "audit-search-01.md",
      "queries": [
        {
          "locale": "en",
          "style": "naive",
          "query": "search audit log issue"
        }
      ]
    }
  ]
}
```

## Notes

- If an issue has no detectable `issue_id`, it is skipped.
- If a query block exists but no valid `locale` + `style` + `query` entries are found, that block is skipped.
- The script is safe to rerun and simply rewrites the destination JSON files.
