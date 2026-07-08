# External LLM Runner - Usage

Playwright-based script to automate running localized queries against ChatGPT and Gemini web UIs, capturing responses and saving them as markdown.

## Prerequisites

1. **Python 3.10+**
2. **Playwright**:
   ```bash
   pip install playwright
   playwright install chromium
   ```

## Commands

Run the script from the repo root:

```bash
python tools/test-suite/external-llms/llm_runner.py <command> [options]
```

### 1. Record login (one-time per provider)

Both ChatGPT and Gemini require login. Record your session once so the script can reuse it:

```bash
# ChatGPT - opens browser; log in, then press Enter
python tools/test-suite/external-llms/llm_runner.py login-chatgpt

# Gemini - copies your real Chrome session to bypass Google automation detection.
# Close all Chrome windows before running.
python tools/test-suite/external-llms/llm_runner.py login-gemini
```

Auth state is saved under `data/test-suite/external-llms/.auth/` (gitignored). Sessions expire periodically; re-run the login command when needed.

### 2. Full run (all providers, all locales)

```bash
python tools/test-suite/external-llms/llm_runner.py run --provider chatgpt --locale all && \
python tools/test-suite/external-llms/llm_runner.py run --provider gemini --locale all
```

### 3. Run queries

```bash
# Run ChatGPT queries in English only (default)
python tools/test-suite/external-llms/llm_runner.py run --provider chatgpt

# Run Gemini in Portuguese and Spanish
python tools/test-suite/external-llms/llm_runner.py run --provider gemini --locale pt,es

# Run all locales (en, pt, es)
python tools/test-suite/external-llms/llm_runner.py run --provider chatgpt --locale all

# Limit to first 5 queries (for testing)
python tools/test-suite/external-llms/llm_runner.py run --provider chatgpt --limit 5

# Dry run: print queries only, do not open browser
python tools/test-suite/external-llms/llm_runner.py run --dry-run
```

**Options for `run`:**

| Option | Default | Description |
|--------|---------|-------------|
| `--provider` | `chatgpt` | `chatgpt` or `gemini` |
| `--output`, `-o` | `results/external-llms` | Base output directory |
| `--queries` | `data/test-suite/external-llms/all_queries.json` | Path to queries JSON file |
| `--limit`, `-n` | None | Max queries to run |
| `--delay` | 3.0 | Seconds between requests (rate limiting) |
| `--locale` | `en` | `en`, `pt`, `es`, comma-separated, or `all` |
| `--headless` | False | Run browser in background |
| `--dry-run` | False | Print queries only, do not run |

### 4. Retry failed queries

After a run completes, failed outputs (empty response, error, or no links extracted) are retried automatically. You can also trigger a retry pass manually:

```bash
# Retry failed outputs from the latest ChatGPT run
python tools/test-suite/external-llms/llm_runner.py retry --provider chatgpt

# Retry a specific run folder
python tools/test-suite/external-llms/llm_runner.py retry --provider chatgpt \
  --run-dir "results/external-llms/chatgpt/external-llms-chatgpt 2026-03-17 14-30"
```

**Options for `retry`:**

| Option | Default | Description |
|--------|---------|-------------|
| `--provider` | `chatgpt` | `chatgpt` or `gemini` |
| `--output`, `-o` | `results/external-llms` | Base directory to search for runs |
| `--run-dir` | None | Specific run folder (default: latest for provider) |
| `--queries` | `data/test-suite/external-llms/all_queries.json` | Path to queries JSON file |
| `--delay` | 3.0 | Seconds between requests |
| `--headless` | False | Run browser in background |

## Output format

Each run creates a timestamped folder inside the provider subdirectory (e.g. `results/external-llms/chatgpt/external-llms-chatgpt 2026-03-17 14-30/`) containing:

- One markdown file per query: `ChatGPT-Naive-en_cms-migration-01.md`
- A `run_metadata.json` with run parameters and outcome counts

```json
{
  "provider": "chatgpt",
  "locales": ["en", "es", "pt"],
  "total_cases": 225,
  "started_at": "2026-03-04T18:00:00+00:00",
  "ended_at": "2026-03-04T20:15:00+00:00",
  "completed": 218,
  "skipped": 0,
  "errors": 3,
  "retried": 4
}
```

Each query file:

```markdown
# ChatGPT - Naive - en - cms-migration-01

## Metadata
- issue_id: `cms-migration-01`
- query_locale: `en`
- query_style: `naive`
- llm_provider: `chatgpt`
- timestamp: `2026-03-04T18:05:00+00:00`

## Prompt
I need to upgrade my VTEX store...

## Response
[LLM response text]

## Extracted URLs
- https://developers.vtex.com/...
```

The script skips queries whose output file already exists, so interrupted runs can be resumed by re-running the same command.

## Input sources

Queries are read from `all_queries.json`. Each issue entry must have a `queries` array where each item contains:

- `locale` (`en` | `pt` | `es`)
- `style` (`naive` | `familiar` | `expert`)
- `query` (string)

## Troubleshooting

| Issue | Action |
|-------|--------|
| "Auth not found" | Run `login-chatgpt` or `login-gemini` |
| Login page appears during run | Session expired; re-run login command |
| Gemini login hangs or blocks sign-in | Close all Chrome windows and re-run `login-gemini` |
| Empty or truncated response | UI selectors may have changed; update `CHATGPT_RESPONSE_SELECTORS` / `GEMINI_RESPONSE_SELECTORS` in `llm_runner.py` |
| No links extracted | Run `retry` — DOM link extraction may have timed out |
| Rate limits / throttling | Increase `--delay` (e.g. `--delay 10`) |
