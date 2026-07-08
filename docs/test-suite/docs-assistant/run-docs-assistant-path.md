# `run-docs-assistant-path.js`

## Purpose

Runs docs-assistant queries through `https://docs-assistant.vtex.com/stream`, parses the streaming response, extracts surfaced references, and writes a result set that mirrors the user-facing experience.

## Required input

- `data/test-suite/docs-assistant/all_queries.json`
- Issue markdown files in `docs/test-suite/issues/` for `target_doc_url` lookup
- Node.js
- Network access to the Docs Assistant endpoint

## Usage

```powershell
node "tools/test-suite/docs-assistant/run-docs-assistant-path.js"
```

## Parameters

| Parameter | Required | Type | Default | Example | Notes |
|---|---|---|---|---|---|
| `--run-id` | No | string | auto-generated timestamped ID | `--run-id docs-assistant-baseline` | If omitted, the script builds `docs-assistant-run-YYYY-MM-DD-HH-MM-SS` |
| `--issues` | No | comma-separated string list | all issues | `--issues audit-search-01,checkout-api-orders-01` | Filters the run to specific issue IDs |
| `--top-n` | No | integer | `10` | `--top-n 5` | Stored in run config; useful for consistency even though docs assistant output is link-based |
| `--output-dir` | No | path | `results/docs-assistant` | `--output-dir "results/docs-assistant"` | Base directory where per-run folders are created |
| `--generate-analysis` | No | flag | `true` | `--generate-analysis` | Explicitly enables the markdown analysis report |
| `--no-generate-analysis` | No | flag | `false` | `--no-generate-analysis` | Disables the markdown analysis report |
| `--delay` | No | integer | `1000` | `--delay 1500` | Delay between API calls in milliseconds |

## Example usage

Run all issues:

```powershell
node "tools/test-suite/docs-assistant/run-docs-assistant-path.js"
```

Run one issue:

```powershell
node "tools/test-suite/docs-assistant/run-docs-assistant-path.js" --issues audit-search-01
```

Increase the API delay:

```powershell
node "tools/test-suite/docs-assistant/run-docs-assistant-path.js" --delay 1500
```

## Expected output

Output base directory by default:

- `results/docs-assistant/`

Variant subdirectory:

- `results/docs-assistant/api/`

Per-run folder:

- `docs-assistant YYYY-MM-DD HH-MM`

Standard path example:

- `results/docs-assistant/api/docs-assistant YYYY-MM-DD HH-MM/`

Files written:

- `<run-id>.json`
- `analysis-<run-id>.md` unless `--no-generate-analysis` is used

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
- `answer_markdown`
- `links`
- `locale`
- `confidence`
- `raw_response_length`

When a target doc is known, the result may also include:

- `target_doc_url`
- `target_doc_url_found`
- `target_doc_url_rank`

## Behavior details

- The script parses SSE events and tries to match the UI behavior shown in the docs assistant interface.
- Link extraction merges:
  - markdown links inside the answer
  - suggested source links
- `summary_by_issue` records link counts by query style rather than only pass/fail.

