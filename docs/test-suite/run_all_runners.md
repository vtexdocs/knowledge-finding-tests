# `run_all_runners.py`

## Purpose

Runs the full Phase 1 collection flow from a single command by orchestrating the existing child runners in sequence:

1. `tools/test-suite/extract_queries_by_path.py`
2. `tools/test-suite/internal-search/run-algolia-path.py` — **deprecated, off by default** (opt in with `--include algolia`)
3. `tools/test-suite/internal-search/run-hybrid-search-path.py`
4. `tools/test-suite/docs-assistant/run-docs-assistant-path.js`
5. `tools/test-suite/external-search/google-search-playwright/run_google_search_playwright.py`
6. `tools/test-suite/external-llms/llm_runner.py`
7. `tools/test-suite/analysis_system.py` (with interactive confirmation)

This is a parent script only. It does not replace the child scripts' own validation or setup requirements.

> **Before you start:** Make sure the environment is ready (Python, Node.js, Playwright, credentials, LLM auth). See the [Quick start](README.md#quick-start) and [Prerequisites](README.md#prerequisites) sections in the test suite README for the full step-by-step setup.

## Required input

- The same inputs required by the child scripts you choose to run
- Issue files in `docs/test-suite/issues/*.md`
- Credentials and auth for the paths you include
- Python runtime
- Node.js for the Docs Assistant step

## Warnings

- External LLM steps require saved authentication before execution. If `external-llms` is included, make sure `llm_runner.py login-chatgpt` and/or `llm_runner.py login-gemini` have already been completed successfully. Close Chrome completely before running `login-gemini` (see [README.md](README.md#5-external-llm-authentication)).
- On Windows, `python` may not be available. Use `py` instead (the Python Launcher for Windows).

### Monitoring during execution

The browser-based steps (Google Search, ChatGPT, Gemini) can be interrupted at any time by provider-side checks. **Keep the browser window visible and monitor the run periodically** to avoid the process hanging silently.

- **Google Search:** reCAPTCHA challenges. Use `--external-search-no-headless --external-search-wait-for-captcha` so the browser stays visible and the script waits for you to solve the captcha.
- **ChatGPT:** Rate-limit pop-ups when too many requests are sent in a short period. You may need to click a dismiss button or wait a few minutes before the script can continue.
- **Gemini:** Similar rate-limit or session-related pop-ups that require manual dismissal or a short wait.

If these interruptions are not resolved, the affected step will hang indefinitely or fail. Using `--continue-on-error` ensures that later steps still run even if one step is interrupted.

## Usage

```powershell
python "tools/test-suite/run_all_runners.py"
```

## Parameters

| Parameter | Required | Type | Default | Example | Notes |
|---|---|---|---|---|---|
| `--include` | No | list of enums | all non-deprecated paths | `--include extract algolia hybrid` | Allowed values: `extract`, `algolia`, `hybrid`, `docs-assistant`, `external-search`, `external-llms`, `analysis`. Default excludes deprecated `algolia`; pass `--include algolia` to run it (prints a deprecation notice). |
| `--skip` | No | list of enums | none | `--skip external-llms docs-assistant` | Skips selected paths |
| `--issues` | No | list of strings | all issues | `--issues audit-search-01 checkout-api-orders-01` | Passed through to supported child scripts |
| `--locale` | No | string | `all` | `--locale en` | Shared locale override for supported runners |
| `--top-n` | No | integer | `10` | `--top-n 5` | Passed to supported runners |
| `--delay` | No | float | child default | `--delay 1.0` | Shared delay override; units depend on each child script |
| `--llm-providers` | No | list of enums | `chatgpt gemini` | `--llm-providers chatgpt` | Used only when `external-llms` is included |
| `--llm-limit` | No | integer | all cases | `--llm-limit 10` | Passed only to `llm_runner.py` |
| `--llm-headless` | No | flag | `false` | `--llm-headless` | Passes `--headless` to `llm_runner.py` |
| `--external-search-no-headless` | No | flag | `false` | `--external-search-no-headless` | Shows the Google Search Playwright browser window |
| `--external-search-wait-for-captcha` | No | flag | `false` | `--external-search-wait-for-captcha` | Passes `--wait-for-captcha` to the external-search runner |
| `--external-search-debug-save-html` | No | flag | `false` | `--external-search-debug-save-html` | Passes `--debug-save-html` to the external-search runner |
| `--run-id-prefix` | No | string | none | `--run-id-prefix baseline-2026-03-17` | Builds child run IDs like `baseline-2026-03-17-algolia` where supported |
| `--dry-run` | No | flag | `false` | `--dry-run` | Prints the generated commands without running them |
| `--continue-on-error` | No | flag | `false` | `--continue-on-error` | Continues later steps even if one child script fails |
| `--analysis-id` | No | string | auto-generated | `--analysis-id phase2-baseline` | Explicit analysis ID passed to `analysis_system.py` |
| `--no-confirm-analysis` | No | flag | `false` | `--no-confirm-analysis` | Skips the interactive confirmation prompt before the analysis step |

## Example usage

Run everything:

```powershell
python "tools/test-suite/run_all_runners.py"
```

Run a smoke test without external LLMs:

```powershell
python "tools/test-suite/run_all_runners.py" --issues audit-search-01 --locale en --skip external-llms
```

Run with Google Search in a visible browser so reCAPTCHA can be handled:

```powershell
python "tools/test-suite/run_all_runners.py" --external-search-no-headless --external-search-wait-for-captcha --skip external-llms
```

Preview the full command plan:

```powershell
python "tools/test-suite/run_all_runners.py" --dry-run
```

Run only the internal-search flow:

```powershell
python "tools/test-suite/run_all_runners.py" --include extract algolia hybrid --locale all --run-id-prefix baseline-2026-03-17
```

Run everything except the browser-sensitive steps:

```powershell
python "tools/test-suite/run_all_runners.py" --skip external-search external-llms docs-assistant
```

Run only the analysis step (re-analyze existing results):

```powershell
python "tools/test-suite/run_all_runners.py" --include analysis --no-confirm-analysis
```

## Expected output

The parent script does not produce a new consolidated artifact of its own.

Instead, it triggers the child scripts, which write to their normal output locations:

- `data/test-suite/internal-search/all_queries.json`
- `data/test-suite/docs-assistant/all_queries.json`
- `data/test-suite/external-search/all_queries.json`
- `data/test-suite/external-llms/all_queries.json`
- `results/internal-search/...`
- `results/docs-assistant/api/...`
- `results/external-search/google-search-playwright/...`
- `results/external-llms/<provider>/...`

Each runner now creates a dedicated per-run folder named with the path and the run time, under its variant folder, for example:

- `results/internal-search/algolia-helpcenter/algolia-helpcenter 2026-03-17 14-30`
- `results/internal-search/hybrid-search/hybrid-search 2026-03-17 14-30`
- `results/docs-assistant/api/docs-assistant 2026-03-17 14-30`
- `results/external-search/google-search-playwright/google-search-playwright 2026-03-17 14-30`
- `results/external-llms/chatgpt/external-llms-chatgpt 2026-03-17 14-30`

If the analysis step runs, it also writes:

- `results/analysis-system/analysis-system YYYY-MM-DD HH-MM/` containing `run_summary.json`, `issues_processed.json`, `aggregates_by_path_locale.json`, `failure_list.json`, and other analysis artifacts. See [analysis-system.md](analysis-system.md) for details.

## Behavior details

- Steps run sequentially, not in parallel.
- The script stops on the first failure unless `--continue-on-error` is used.
- `--issues` is only passed to child scripts that support issue filtering.
- For the Google Search Playwright step, `--issue` is passed only when exactly one issue ID is provided.
- Child scripts still enforce their own credentials, dependencies, and runtime assumptions.
- In practice, the most common blockers are missing LLM auth state and Google consent or reCAPTCHA interruptions.
- After all data-collection steps finish, the script displays a separator and prompts:

  ```text
  Proceed with the analysis report? [y/N]
  ```

  Type `y` to generate the analysis report immediately, or press Enter / type `n` to skip it. Use `--no-confirm-analysis` to skip the prompt entirely (useful for fully automated / CI runs). The analysis can always be generated later with `python "tools/test-suite/analysis_system.py" run`.

## Post-collection: timeline dashboard

After one or more analysis runs are available, use `render_analysis_dashboard.py --timeline-runs` to build an interactive timeline dashboard:

```powershell
python "tools/test-suite/render_analysis_dashboard.py" `
  --timeline-runs "results/analysis-system/analysis-system 2026-03-25 17-12" `
                  "results/analysis-system/analysis-system 2026-04-02 13-38"
```

Each dashboard is saved with a timestamped filename (e.g. `timeline_2026-04-08_11-38.html`) under `results/analysis-system/timeline-dashboard/`. Previous dashboards are never overwritten, so you keep a full history of generated reports.

See the [test suite README](README.md#post-collection-analysis-and-timeline-dashboard) and [analysis-system.md](analysis-system.md#82-timeline-dashboard) for more details.
