# `llm_runner.py`

## Purpose

Runs external-LLM test cases in ChatGPT or Gemini through Playwright.

The script supports:

- login session capture
- full data collection runs
- retrying failed runs
- locale filtering
- per-case markdown output with extracted URLs

## Warning

This runner requires an authenticated browser session before collection starts. If the login step has not been completed, run commands will fail because the providers will redirect to authentication flows instead of answering queries.

## Required input

- `data/test-suite/external-llms/all_queries.json`
- Python Playwright package
- Installed Chrome or Chromium
- Saved auth state for the target provider:
  - `data/test-suite/external-llms/.auth/chatgpt.json`
  - `data/test-suite/external-llms/.auth/gemini.json`

Optional for Gemini:

- `data/test-suite/external-llms/.auth/gemini_profile`

## Usage

This script uses subcommands.

### Login

```powershell
python "tools/test-suite/external-llms/llm_runner.py" login-chatgpt
python "tools/test-suite/external-llms/llm_runner.py" login-gemini
```

Login parameters:

| Parameter | Required | Type | Default | Example | Notes |
|---|---|---|---|---|---|
| `--headless` | No | flag | `false` | `login-chatgpt --headless` | Available for login subcommands, but interactive login is usually easier without it |

### Run

```powershell
python "tools/test-suite/external-llms/llm_runner.py" run --provider chatgpt
```

Run parameters:

| Parameter | Required | Type | Default | Example | Notes |
|---|---|---|---|---|---|
| `--provider` | No | enum | `chatgpt` | `--provider gemini` | Allowed values: `chatgpt`, `gemini` |
| `--output` | No | path | `results/external-llms` | `--output "results/external-llms"` | Base directory for per-run folders |
| `--queries` | No | path | `data/test-suite/external-llms/all_queries.json` | `--queries "data/test-suite/external-llms/all_queries.json"` | Source query file |
| `--limit` | No | integer | all cases | `--limit 10` | Limits the number of selected cases |
| `--delay` | No | float | `3.0` | `--delay 5.0` | Delay between requests in seconds |
| `--locale` | No | string | `en` | `--locale all` | Accepts `en`, `pt`, `es`, comma-separated values like `en,pt`, or `all` |
| `--headless` | No | flag | `false` | `--headless` | Runs the browser without a visible UI |
| `--dry-run` | No | flag | `false` | `--dry-run` | Prints the generated URLs without sending prompts |

### Retry

```powershell
python "tools/test-suite/external-llms/llm_runner.py" retry --provider chatgpt
```

Retry parameters:

| Parameter | Required | Type | Default | Example | Notes |
|---|---|---|---|---|---|
| `--provider` | No | enum | `chatgpt` | `--provider gemini` | Allowed values: `chatgpt`, `gemini` |
| `--output` | No | path | `results/external-llms` | `--output "results/external-llms"` | Base directory used to locate existing runs |
| `--run-dir` | No | path | latest run for provider | `--run-dir "results/external-llms/chatgpt/external-llms-chatgpt 2026-03-17 14-30"` | Specific run folder to retry |
| `--queries` | No | path | `data/test-suite/external-llms/all_queries.json` | `--queries "data/test-suite/external-llms/all_queries.json"` | Used to reconstruct the original cases |
| `--delay` | No | float | `3.0` | `--delay 5.0` | Delay between retry requests in seconds |
| `--headless` | No | flag | `false` | `--headless` | Runs the retry browser session headlessly |

## Example usage

Record ChatGPT auth:

```powershell
python "tools/test-suite/external-llms/llm_runner.py" login-chatgpt
```

Record Gemini auth:

```powershell
python "tools/test-suite/external-llms/llm_runner.py" login-gemini
```

Run all English ChatGPT cases:

```powershell
python "tools/test-suite/external-llms/llm_runner.py" run --provider chatgpt --locale en
```

Run all locales in Gemini:

```powershell
python "tools/test-suite/external-llms/llm_runner.py" run --provider gemini --locale all
```

Dry-run preview:

```powershell
python "tools/test-suite/external-llms/llm_runner.py" run --provider chatgpt --dry-run
```

Retry the latest failed Gemini run:

```powershell
python "tools/test-suite/external-llms/llm_runner.py" retry --provider gemini
```

## Expected output

Default output base:

- `results/external-llms/`

Provider subdirectories:

- `results/external-llms/chatgpt/`
- `results/external-llms/gemini/`

Each run creates a timestamped folder such as:

- `external-llms-chatgpt 2026-03-17 14-30/`
- `external-llms-gemini 2026-03-17 14-30/`

Each run folder contains:

- one markdown file per `(issue_id, locale, style)` case
- `run_metadata.json`

Each markdown file contains:

- metadata
- prompt
- captured response
- extracted URLs

`run_metadata.json` contains:

- `provider`
- `locales`
- `total_cases`
- `limit`
- `delay_sec`
- `queries_file`
- `started_at`
- `ended_at`
- `completed`
- `skipped`
- `errors`
- `retried`

## Behavior details

- The script appends a locale-specific "search the web" instruction to prompts.
- Failed outputs can be retried automatically after the main pass.
- The `retry` subcommand can rerun failed cases from the latest or a specific run folder.
- Gemini runs may rely on a copied Chrome profile to preserve login state.
- Before any `run` or `retry` command, confirm the corresponding auth file already exists in `.auth/`; otherwise, start with the relevant login command.
