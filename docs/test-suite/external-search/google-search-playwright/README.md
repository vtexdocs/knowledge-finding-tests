# Google Search Playwright

Runner that **simulates a user searching on Google** using Playwright (Chromium). It opens `https://www.google.com/search?q=...`, parses the SERP for the first 7 organic results and any AI Overview, and writes JSON with session_1 (structured output). You can run all queries or filter by issue, locale, style, limit (first N issues), or a single query text. Output files are now saved under **`results/external-search/google-search-playwright/`** in one folder per run.

**Input:** `all_queries.json` in the parent folder (External search).  
**Output:** Each run creates a folder named like `google-search-playwright YYYY-MM-DD HH-MM` under **`results/external-search/google-search-playwright/`**. The JSON output file is saved as `results.json`.

No API key is required. Google’s DOM and consent/captcha handling can vary by region; use `--no-headless` to show the browser if you hit consent or captcha.

## Run from Cursor

In Cursor you can run the same script via the **`/run-google-search-playwright`** command. Type the command and add any options in the message; the agent will run the script with those flags.

| What you want | Example in Cursor |
|---------------|-------------------|
| First 3 issues, visible browser, wait for captcha | `/run-google-search-playwright 3 --no-headless --wait-for-captcha` |
| All queries for locale `en` | `/run-google-search-playwright --locale en --no-headless --wait-for-captcha` |
| One issue only | `/run-google-search-playwright --issue bitcoin-payment-01 --no-headless --wait-for-captcha` |
| Issue + locale | `/run-google-search-playwright --issue audit-search-01 --locale pt --no-headless --wait-for-captcha` |
| One style only | `/run-google-search-playwright --style familiar --no-headless --wait-for-captcha` |
| One specific query | `/run-google-search-playwright --query "checkout api update order request body format vtex" --no-headless --wait-for-captcha` |

You can combine filters and add `--no-headless`, `--wait-for-captcha`, `--no-persistent-profile`, etc. as needed.

## Requirements

- Python 3.x
- `pip install playwright`
- `playwright install chromium`

## Windows note

On some Windows setups, `python` points to the Microsoft Store alias instead of an installed interpreter, which causes this error:

```text
Python nao foi encontrado; executar sem argumentos para instalar do Microsoft Store...
```

If that happens, use the Python launcher instead:

```powershell
py .\run_google_search_playwright.py run --limit-issues 3
```

If you want `python` to work as well, add your Python installation to `PATH` or disable the Windows app execution alias for `python.exe`.

## Usage

```bash
# From this folder (Google Search Playwright)
py .\run_google_search_playwright.py run

# First issue only (e.g. audit-search-01, 3 queries)
py .\run_google_search_playwright.py run --limit-issues 1

# Show browser window (helps with consent/captcha)
py .\run_google_search_playwright.py run --no-headless

# On captcha/consent: solve in browser; script polls automatically for up to 120 seconds
py .\run_google_search_playwright.py run --no-headless --wait-for-captcha

# Dry run: list queries only, no browser
py .\run_google_search_playwright.py run --dry-run

# Longer delay between queries (default 2s) to reduce captcha risk
py .\run_google_search_playwright.py run --delay 3

# If browser fails to start (TargetClosedError), use ephemeral profile
py .\run_google_search_playwright.py run --no-persistent-profile
```

## Customized search (filter by issue, locale, style, or query)

Filters can be combined (e.g. `--issue X --locale pt`). Each run type uses the same `run` command with different options:

| Run type | Command example |
|----------|------------------|
| **1. All queries** | `py .\run_google_search_playwright.py run` |
| **2. First N issues** | `py .\run_google_search_playwright.py run --limit-issues 3` |
| **3. All queries for a locale** | `py .\run_google_search_playwright.py run --locale en` (or `es`, `pt`) |
| **4. All queries from one issue** | `py .\run_google_search_playwright.py run --issue checkout-api-orders-01` |
| **5. Queries for a locale in one issue** | `py .\run_google_search_playwright.py run --issue checkout-api-orders-01 --locale pt` |
| **6. One specific query (exact text)** | `py .\run_google_search_playwright.py run --query "checkout api update order request body format vtex"` |
| **7. All queries of a given style** | `py .\run_google_search_playwright.py run --style familiar` (or `naive`, `expert`) |

You can also combine with `--limit-issues`, `--no-headless`, `--wait-for-captcha`, etc.

## Output folder structure

Outputs are saved under:

- `results/external-search/google-search-playwright/`

Each run creates a new folder named:

- `google-search-playwright YYYY-MM-DD HH-MM`

Example layout:

```text
results/external-search/google-search-playwright/
└── google-search-playwright 2026-03-17 14-30/
    └── results.json
```

## Output file content

Output is **session_1** only: one structured block per issue with `output_urls` and `ai_overview_content`. No separate raw/session_2 block. This runner does not include a cost estimate (no Custom Search API).

**`ai_overview_content`** is filled with the **AI Overview** text when Google shows it for the query (e.g. “AI Overview” / “Visão geral criada por IA”). If there is no AI Overview on the page, `ai_overview_content` is empty.

## reCAPTCHA and many searches in a row

You **cannot** disable reCAPTCHA — Google shows it to block automation. To reduce how often it appears:

- **Persistent profile:** The runner uses a browser profile in `.playwright-profile/` (cookies/session). After you solve consent/captcha once with `--no-headless`, later runs may reuse the same session and see fewer prompts.
- **Pacing:** Use a longer `--delay` (e.g. 3–5 seconds) between queries so it looks less like a bot.
- **Non-headless:** `--no-headless` is less likely to trigger captcha than headless in some environments.
- **`--wait-for-captcha`:** When a consent/captcha page is detected, the script prints a message and polls the browser automatically for up to 120 seconds. Solve the challenge(s) in the browser window; once normal search results appear, the script resumes without terminal input.

If `output_urls` is still empty, run once with `--debug-save-html` to save the SERP HTML when no results are found; inspect the file to see if the page is consent/captcha or if Google’s DOM changed.

- **Profile / browser won’t start:** If you see `TargetClosedError` (browser closes immediately), the persistent profile may be locked or corrupted. Run with `--no-persistent-profile` to use an ephemeral browser (no profile); you may see more consent/captcha prompts.

## Caveats

- Google’s HTML can change; if results are empty, try `--no-headless` and `--debug-save-html`.
- Automated access to Google Search may conflict with Google’s terms; use for internal/testing only.
