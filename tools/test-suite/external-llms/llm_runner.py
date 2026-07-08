#!/usr/bin/env python3
"""
Playwright-based runner for External LLM tests (ChatGPT, Gemini).
Opens query URLs, waits for responses, and saves results as markdown.
Uses storage state for one-time login; selectors may need updates when provider UIs change.
"""

import argparse
import json
import os
import re
import shutil
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("Playwright not installed. Run: pip install playwright && playwright install chromium")

# --- Paths and config ---
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent
ISSUES_DIR = REPO_ROOT / "docs" / "test-suite" / "issues"
DATA_EXTERNAL_LLMS = REPO_ROOT / "data" / "test-suite" / "external-llms"
DEFAULT_QUERIES_FILE = DATA_EXTERNAL_LLMS / "all_queries.json"
AUTH_DIR = DATA_EXTERNAL_LLMS / ".auth"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "results" / "external-llms"


CHATGPT_BASE = "https://chatgpt.com"
CHATGPT_URL_TEMPLATE = "https://chatgpt.com/?q={encoded}"  # Native support.
GEMINI_BASE = "https://gemini.google.com"
GEMINI_URL_TEMPLATE = "https://gemini.google.com/app?prompt={encoded}"  # Needs Gemini URL Prompt extension.

VALID_STYLES = {"naive", "familiar", "expert"}
VALID_LOCALES = {"en", "pt", "es"}

# Selectors for response extraction (UI may change; update if needed)
CHATGPT_RESPONSE_SELECTORS = [
    '[data-message-author-role="assistant"]',
    "main [class*='markdown']",
    "main article",
    "main",
]
GEMINI_RESPONSE_SELECTORS = [
    "[data-response-content]",
    "main [class*='content']",
    "main [class*='markdown']",
    "main",
]

# Send button selectors: clicked after navigation if the prompt wasn't auto-submitted.
CHATGPT_SEND_SELECTORS = [
    'button[data-testid="send-button"]',
    'button[aria-label*="Send"]',
]
GEMINI_SEND_SELECTORS = [
    'button[aria-label*="Send message"]',
    'button[aria-label*="Send"]',
]

# Localized instruction appended to every prompt to trigger web search.
WEB_SEARCH_SUFFIX: dict[str, str] = {
    "en": "Search the web to come up with the answer and list the links you used to answer.",
    "pt": "Pesquise na web para encontrar a resposta e liste os links que usou para responder.",
    "es": "Busca en la web para encontrar la respuesta y enumera los enlaces que usaste para responder.",
}


def create_run_directory(base_output: Path, path_slug: str, timestamp: datetime | None = None) -> Path:
    """Create a per-run output folder named '<path> YYYY-MM-DD HH-MM'."""
    ts = timestamp or datetime.now()
    folder_name = f"{path_slug} {ts.strftime('%Y-%m-%d %H-%M')}"
    run_dir = base_output / folder_name
    if not run_dir.exists():
        run_dir.mkdir(parents=True, exist_ok=False)
        return run_dir

    suffix = 2
    while True:
        candidate = base_output / f"{folder_name} ({suffix})"
        if not candidate.exists():
            candidate.mkdir(parents=True, exist_ok=False)
            return candidate
        suffix += 1


def get_provider_output_root(base_output: Path, provider: str) -> Path:
    """Return results/external-llms/<provider> for the given provider."""
    return base_output / provider


def extract_llm_queries(content: str) -> list[dict[str, str]]:
    """Extract localized Query Type D entries as [{locale, style, query}, ...]."""
    section_d_patterns = [
        r"##\s+Query Type D:\s*External LLMs.*?\n(.*?)(?=\n##|\Z)",
        r"###\s+D\s*[\u2014\u2013-]\s*External LLMs.*?\n(.*?)(?=\n###|\n##|\Z)",
    ]
    section_d = None
    for pattern in section_d_patterns:
        m = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if m:
            section_d = m.group(1)
            break
    if not section_d:
        return []

    json_match = re.search(r"```json\s*(\[[\s\S]*?\])\s*```", section_d)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            if isinstance(data, list):
                cleaned = []
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    locale = str(item.get("locale", "")).strip().lower()
                    style = str(item.get("style", "")).strip().lower()
                    query = str(item.get("query", "")).strip()
                    if locale in VALID_LOCALES and style in VALID_STYLES and query:
                        cleaned.append({"locale": locale, "style": style, "query": query})
                if cleaned:
                    return cleaned
        except json.JSONDecodeError:
            pass

    # Fallback table parser: | locale | style | query |
    rows = re.finditer(
        r"\|\s*([a-z]{2})\s*\|\s*(naive|familiar|expert)\s*\|\s*(.+?)\s*\|",
        section_d,
        re.IGNORECASE,
    )

    queries = []
    for m in rows:
        locale = m.group(1).lower()
        style = m.group(2).lower()
        query = m.group(3).strip()
        if locale in VALID_LOCALES and style in VALID_STYLES and query:
            queries.append({"locale": locale, "style": style, "query": query})
    return queries


def extract_issue_id(content: str) -> str | None:
    """Extract issue_id from issue content."""
    for pattern in [r"-\s*\*\*Issue ID:\*\*\s*(.+?)(?:\n|$)", r"\*\*[Ii]ssue [Ii][Dd]\*\*\s*\|\s*(.+?)\s*\|"]:
        m = re.search(pattern, content, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def build_url(provider: str, query: str, locale: str = "en") -> str:
    suffix = WEB_SEARCH_SUFFIX.get(locale, WEB_SEARCH_SUFFIX["en"])
    if provider == "chatgpt":
        encoded = urllib.parse.quote(f"{query}.\n\n{suffix}", safe="")
        return CHATGPT_URL_TEMPLATE.format(encoded=encoded)
    if provider == "gemini":
        return GEMINI_BASE  # Gemini: navigate to base URL and type the prompt directly.
    raise ValueError(f"Unknown provider: {provider}")


def parse_locale_filter(locale_arg: str) -> set[str]:
    val = (locale_arg or "en").strip().lower()
    if val == "all":
        return set(VALID_LOCALES)
    locales = {part.strip() for part in val.split(",") if part.strip()}
    invalid = sorted(locales - VALID_LOCALES)
    if invalid:
        raise ValueError(f"Invalid locale(s): {', '.join(invalid)}. Use en, pt, es, comma-separated, or all.")
    return locales


def load_test_cases(issues_dir: Path, locales: set[str]) -> list[dict]:
    """Load test cases from issue markdown files; one case per (issue_id, locale, style)."""
    cases = []
    for f in sorted(issues_dir.glob("*.md")):
        content = f.read_text(encoding="utf-8")
        issue_id = extract_issue_id(content)
        if not issue_id:
            continue

        queries = extract_llm_queries(content)
        if not queries:
            continue

        for item in queries:
            if item["locale"] not in locales:
                continue
            cases.append(
                {
                    "issue_id": issue_id,
                    "query": item["query"],
                    "query_style": item["style"],
                    "query_locale": item["locale"],
                }
            )
    return cases


def load_test_cases_from_json(queries_file: Path, locales: set[str]) -> list[dict]:
    """Load test cases from all_queries.json; one case per (issue_id, locale, style)."""
    try:
        payload = json.loads(queries_file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FileNotFoundError(f"Queries file not found: {queries_file}") from None
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {queries_file}: {e}") from e

    issues = payload.get("issues", []) if isinstance(payload, dict) else []
    if not isinstance(issues, list):
        raise ValueError(f"Invalid queries structure in {queries_file}: expected top-level 'issues' array.")

    cases = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        issue_id = str(issue.get("issue_id", "")).strip()
        if not issue_id:
            continue

        queries = issue.get("queries", [])
        if not isinstance(queries, list):
            continue

        for item in queries:
            if not isinstance(item, dict):
                continue
            locale = str(item.get("locale", "")).strip().lower()
            style = str(item.get("style", "")).strip().lower()
            query = str(item.get("query", "")).strip()
            if locale not in locales or style not in VALID_STYLES or not query:
                continue

            cases.append(
                {
                    "issue_id": issue_id,
                    "query": query,
                    "query_style": style,
                    "query_locale": locale,
                }
            )
    return cases


def extract_urls_from_markdown(text: str) -> list[str]:
    """Extract URLs from markdown: [text](url) and bare https? URLs."""
    urls = []
    for m in re.finditer(r"\[([^\]]*)\]\((\s*<?([^)\s>]+)>?\s*)\)", text):
        urls.append(m.group(3).strip())
    for m in re.finditer(r"https?://[^\s\)\]\`]+", text):
        urls.append(m.group(0).rstrip(".,;:)"))
    return list(dict.fromkeys(urls))


def extract_urls_from_dom(page, response_selectors: list[str], provider: str) -> list[str]:
    """Extract hrefs from <a> tags in the page.

    ChatGPT: scans within the response element (citations are inline).
    Gemini: scans the full page body because sources appear in a separate
            panel outside the response container.
    """
    js = "els => [...new Set(els.map(el => el.href).filter(h => h.startsWith('http')))]"

    if provider == "gemini":
        try:
            return page.eval_on_selector_all("body a[href]", js)
        except Exception:
            return []

    targeted = [s for s in response_selectors if s not in ("main", "body")]
    for sel in targeted:
        try:
            urls = page.eval_on_selector_all(f"{sel} a[href]", js)
            if urls:
                return urls
        except Exception:
            continue
    return []



def submit_prompt(
    page,
    send_selectors: list[str],
    text_to_type: str | None = None,
) -> None:
    """Focus the composer, optionally type the prompt, then submit.

    When text_to_type is provided (Gemini), the query is typed directly into the
    composer instead of being pre-filled via the URL query string.
    For ChatGPT the composer is already pre-filled; we just focus and submit.
    """
    composer_selectors = [
        "textarea#prompt-textarea",
        "textarea[data-id]",
        "textarea",
        "[contenteditable='true'][role='textbox']",
        "[contenteditable='true']",
    ]

    composer = None
    for sel in composer_selectors:
        try:
            el = page.locator(sel).last
            el.wait_for(state="visible", timeout=2_000)
            el.click()
            composer = el
            break
        except Exception:
            continue

    if text_to_type and composer:
        composer.type(text_to_type, delay=20)  # Small delay to avoid dropped chars.

    # Try clicking a Send button.
    for sel in send_selectors:
        try:
            btn = page.locator(sel).last
            btn.wait_for(state="visible", timeout=2_000)
            if btn.is_enabled():
                btn.click()
                return
        except Exception:
            continue

    # Final fallback: press Enter (works when composer is focused).
    page.keyboard.press("Enter")


def wait_for_stable_response(
    page,
    response_selectors: list[str],
    stable_for_sec: float = 5.0,
    poll_sec: float = 2.0,
    timeout_sec: float = 180.0,
) -> str:
    """Poll until the assistant response text stops changing (streaming done).

    Only matches the specific response selectors — never broad fallbacks like 'main'
    that would capture page chrome before a real answer appears.
    Returns the final stable text, or empty string on timeout.
    """
    # Use only targeted selectors; discard overly broad fallbacks like "main".
    targeted = [s for s in response_selectors if s not in ("main", "body")]

    deadline = time.time() + timeout_sec
    last_text = ""
    stable_since: float | None = None

    while time.time() < deadline:
        text = ""
        for sel in targeted:
            try:
                loc = page.locator(sel).last
                candidate = loc.inner_text(timeout=1500)
                if candidate and len(candidate.strip()) > 50:
                    text = candidate.strip()
                    break
            except Exception:
                continue

        if text and text == last_text:
            if stable_since is None:
                stable_since = time.time()
            elif time.time() - stable_since >= stable_for_sec:
                return text
        else:
            stable_since = None
            last_text = text

        time.sleep(poll_sec)

    return last_text.strip()


def _launch_args() -> list[str]:
    return ["--disable-blink-features=AutomationControlled"]


def _webdriver_hide_script() -> str:
    return "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"


def _real_chrome_user_data_dir() -> Path | None:
    """Return the system Chrome User Data directory, or None if not found."""
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA", "")
        candidate = Path(local) / "Google" / "Chrome" / "User Data"
    elif sys.platform == "darwin":
        candidate = Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
    else:
        candidate = Path.home() / ".config" / "google-chrome"
    return candidate if candidate.exists() else None


def _copy_chrome_auth_files(src: Path, dst: Path) -> None:
    """Copy the minimal Chrome files needed to restore a Google session.

    Chrome refuses CDP remote debugging when using its default User Data directory,
    so we copy auth files to a custom directory that Playwright can use freely.
    Close Chrome before calling this to avoid copying a locked Cookies database.
    """
    # Files relative to the User Data root that carry Google session state.
    AUTH_FILES = [
        Path("Local State"),                         # Master AES key (DPAPI-wrapped)
        Path("Default") / "Cookies",                 # Chrome < 96
        Path("Default") / "Network" / "Cookies",     # Chrome >= 96
        Path("Default") / "Login Data",
        Path("Default") / "Preferences",
        Path("Default") / "Secure Preferences",
    ]
    for rel in AUTH_FILES:
        src_file = src / rel
        if not src_file.exists():
            continue
        dst_file = dst / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)


def cmd_login(provider: str, headless: bool = False) -> None:
    """Record login: open browser, user signs in manually, storage state saved to .auth/{provider}.json.

    Gemini copies Google session files from the real Chrome profile to a custom directory
    that Playwright can use (Chrome blocks CDP on its default User Data dir).
    Close Chrome before running login-gemini.
    """
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    auth_path = AUTH_DIR / f"{provider}.json"
    base_url = CHATGPT_BASE if provider == "chatgpt" else GEMINI_BASE

    with sync_playwright() as p:
        if provider == "gemini":
            profile_dir = AUTH_DIR / "gemini_profile"
            real_user_data = _real_chrome_user_data_dir()
            if real_user_data:
                print(f"Copying Google session from {real_user_data} → {profile_dir}")
                print("NOTE: Chrome must be fully closed before continuing.")
                profile_dir.mkdir(parents=True, exist_ok=True)
                _copy_chrome_auth_files(real_user_data, profile_dir)
                print("Copy done. Launching browser...")
            else:
                profile_dir.mkdir(parents=True, exist_ok=True)
                print(f"Real Chrome profile not found; using fresh profile: {profile_dir}")

            context = p.chromium.launch_persistent_context(
                str(profile_dir),
                channel="chrome",
                headless=headless,
                args=_launch_args(),
            )
            context.add_init_script(_webdriver_hide_script())
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(base_url)
            print("Verify you are logged in to Gemini, then press Enter...")
            input()
            context.storage_state(path=str(auth_path))
            context.close()
        else:
            browser = p.chromium.launch(channel="chrome", headless=headless, args=_launch_args())
            context = browser.new_context()
            context.add_init_script(_webdriver_hide_script())
            page = context.new_page()
            page.goto(base_url)
            print(f"Log in to {provider} in the browser, then press Enter...")
            input()
            context.storage_state(path=str(auth_path))
            browser.close()
    print(f"Saved auth state to {auth_path}")


def _failure_reason(path: Path) -> str | None:
    """Return a short failure label if the output file is considered failed, else None."""
    try:
        content = path.read_text(encoding="utf-8")
        if "## Response\n\n(empty)" in content:
            return "Empty response"
        if "## Response\n\n[Error:" in content:
            return "Error"
        if "## Extracted URLs\n- (none)" in content:
            return "No URLs"
        return None
    except Exception:
        return "Unreadable"


def _find_failed_cases(
    run_dir: Path, cases: list[dict], provider: str
) -> tuple[list[dict], dict[str, int]]:
    """Return cases whose output files are failed or missing, deleting those files.

    Also returns a dict with failure reason counts for reporting.
    """
    failed = []
    counts: dict[str, int] = {}
    for case in cases:
        out_name = (
            f"{provider.title()}-{case['query_style'].capitalize()}"
            f"-{case['query_locale']}_{case['issue_id']}.md"
        )
        out_path = run_dir / out_name
        if not out_path.exists():
            reason = "Missing"
        else:
            reason = _failure_reason(out_path)
        if reason is not None:
            if out_path.exists():
                out_path.unlink()
            failed.append(case)
            counts[reason] = counts.get(reason, 0) + 1
    return failed, counts


def _summarize_run_outcomes(
    run_dir: Path, cases: list[dict], provider: str
) -> tuple[int, dict[str, int]]:
    """Summarize final per-case outcomes from the files currently present in a run folder."""
    n_completed = 0
    failure_counts: dict[str, int] = {}

    for case in cases:
        out_name = (
            f"{provider.title()}-{case['query_style'].capitalize()}"
            f"-{case['query_locale']}_{case['issue_id']}.md"
        )
        out_path = run_dir / out_name
        if not out_path.exists():
            reason = "Missing"
        else:
            reason = _failure_reason(out_path)

        if reason is None:
            n_completed += 1
        else:
            failure_counts[reason] = failure_counts.get(reason, 0) + 1

    return n_completed, failure_counts


def _open_browser_context(p, provider: str, auth_path: Path, headless: bool):
    """Open a Playwright browser context for the given provider."""
    gemini_profile = AUTH_DIR / "gemini_profile"
    if provider == "gemini" and gemini_profile.exists():
        context = p.chromium.launch_persistent_context(
            str(gemini_profile),
            channel="chrome",
            headless=headless,
            args=_launch_args(),
        )
        return None, context
    browser = p.chromium.launch(channel="chrome", headless=headless, args=_launch_args())
    context = browser.new_context(storage_state=str(auth_path))
    return browser, context


def _run_query_loop(
    page,
    cases: list[dict],
    provider: str,
    run_dir: Path,
    selectors: list[str],
    send_selectors: list[str],
    delay_sec: float,
    label: str = "",
) -> tuple[int, int, int]:
    """Run a list of cases through the browser, saving output files.

    Returns (n_completed, n_skipped, n_errors).
    """
    n_completed = n_skipped = n_errors = 0
    total = len(cases)

    for i, case in enumerate(cases, 1):
        issue_id = case["issue_id"]
        query_style = case["query_style"]
        query_locale = case["query_locale"]
        query = case["query"]
        url = build_url(provider, query, query_locale)
        out_name = f"{provider.title()}-{query_style.capitalize()}-{query_locale}_{issue_id}.md"
        out_path = run_dir / out_name

        if out_path.exists():
            print(f"  {label}[{i}/{total}] SKIP (exists): {out_name}")
            n_skipped += 1
            continue

        print(f"  {label}[{i}/{total}] {issue_id} / {query_locale} / {query_style}...")
        error_msg = None
        try:
            page.goto(url, wait_until="domcontentloaded")
            suffix = WEB_SEARCH_SUFFIX.get(query_locale, WEB_SEARCH_SUFFIX["en"])
            text_to_type = f"{query}. {suffix}" if provider == "gemini" else None
            submit_prompt(page, send_selectors, text_to_type)
            response_text = wait_for_stable_response(page, selectors)
        except Exception as e:
            response_text = f"[Error: {e}]"
            error_msg = str(e)
            print(f"    Error: {e}")

        if error_msg:
            n_errors += 1
        else:
            n_completed += 1

        md_urls = extract_urls_from_markdown(response_text) if response_text else []
        dom_urls = extract_urls_from_dom(page, selectors, provider) if response_text else []
        urls = list(dict.fromkeys(md_urls + dom_urls))
        ts = datetime.now(timezone.utc).isoformat()
        md = (
            f"# {provider.title()} - {query_style.capitalize()} - {query_locale} - {issue_id}\n\n"
            f"## Metadata\n"
            f"- issue_id: `{issue_id}`\n"
            f"- query_locale: `{query_locale}`\n"
            f"- query_style: `{query_style}`\n"
            f"- llm_provider: `{provider}`\n"
            f"- timestamp: `{ts}`\n\n"
            f"## Prompt\n{query}\n\n"
            f"## Response\n\n{response_text or '(empty)'}\n\n"
            f"## Extracted URLs\n"
        )
        for u in urls:
            md += f"- {u}\n"
        if not urls:
            md += "- (none)\n"
        out_path.write_text(md, encoding="utf-8")
        print(f"    Saved: {out_path.name}")

        if i < total and delay_sec > 0:
            time.sleep(delay_sec)

    return n_completed, n_skipped, n_errors


def cmd_run(
    provider: str,
    output_dir: Path,
    queries_file: Path,
    limit: int | None,
    delay_sec: float,
    headless: bool,
    dry_run: bool,
    locale_arg: str,
) -> None:
    """Run queries via Playwright; each invocation creates a timestamped run folder.

    After the main pass, failed outputs (empty, error, or no links) are
    automatically retried once.
    """
    auth_path = AUTH_DIR / f"{provider}.json"
    if not auth_path.exists():
        print(f"Auth not found: {auth_path}. Run: python llm_runner.py login-{provider}")
        sys.exit(1)

    try:
        locales = parse_locale_filter(locale_arg)
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    try:
        cases = load_test_cases_from_json(queries_file, locales)
    except (FileNotFoundError, ValueError) as e:
        print(str(e))
        sys.exit(1)

    if limit:
        cases = cases[:limit]
    if not cases:
        print("No test cases found.")
        sys.exit(0)
    print(f"Running {len(cases)} queries for {provider} (locales: {', '.join(sorted(locales))})")

    selectors = CHATGPT_RESPONSE_SELECTORS if provider == "chatgpt" else GEMINI_RESPONSE_SELECTORS
    send_selectors = CHATGPT_SEND_SELECTORS if provider == "chatgpt" else GEMINI_SEND_SELECTORS

    if dry_run:
        for c in cases:
            url = build_url(provider, c["query"], c["query_locale"])
            preview = c["query"][:80]
            print(f"  {c['issue_id']} / {c['query_locale']} / {c['query_style']}: {url} | {preview}...")
        return

    started_at = datetime.now(timezone.utc)
    provider_output_dir = get_provider_output_root(output_dir, provider)
    run_dir = create_run_directory(
        provider_output_dir,
        f"external-llms-{provider}",
        started_at.replace(tzinfo=None),
    )

    metadata: dict = {
        "provider": provider,
        "locales": sorted(locales),
        "total_cases": len(cases),
        "limit": limit,
        "delay_sec": delay_sec,
        "queries_file": str(queries_file),
        "started_at": started_at.isoformat(),
        "ended_at": None,
        "completed": 0,
        "skipped": 0,
        "errors": 0,
        "retried": 0,
    }
    metadata_path = run_dir / "run_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Run folder: {run_dir}")

    # --- Main pass ---
    with sync_playwright() as p:
        browser, context = _open_browser_context(p, provider, auth_path, headless)
        context.add_init_script(_webdriver_hide_script())
        page = context.new_page()
        page.set_default_timeout(120_000)
        _, n_skipped, _ = _run_query_loop(
            page, cases, provider, run_dir, selectors, send_selectors, delay_sec
        )
        context.close() if browser is None else browser.close()

    # --- Retry pass ---
    failed_cases, failure_counts = _find_failed_cases(run_dir, cases, provider)
    n_retried = len(failed_cases)
    if failed_cases:
        breakdown = ", ".join(f"{r}: {c}" for r, c in sorted(failure_counts.items()))
        print(f"\nRetrying {n_retried} failed queries ({breakdown})...")
        with sync_playwright() as p:
            browser, context = _open_browser_context(p, provider, auth_path, headless)
            context.add_init_script(_webdriver_hide_script())
            page = context.new_page()
            page.set_default_timeout(120_000)
            _run_query_loop(
                page, failed_cases, provider, run_dir, selectors, send_selectors, delay_sec,
                label="RETRY "
            )
            context.close() if browser is None else browser.close()

    final_completed, final_failure_counts = _summarize_run_outcomes(run_dir, cases, provider)
    remaining_failures = sum(final_failure_counts.values())
    recovered_failures = n_retried - remaining_failures
    if failed_cases:
        print(f"Retry done. recovered={recovered_failures} still_failing={remaining_failures}")

    metadata["ended_at"] = datetime.now(timezone.utc).isoformat()
    metadata["completed"] = final_completed
    metadata["skipped"] = n_skipped
    metadata["errors"] = remaining_failures
    metadata["retried"] = n_retried
    metadata["failure_breakdown"] = final_failure_counts
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(
        f"\nDone. completed={metadata['completed']} skipped={n_skipped} "
        f"errors={metadata['errors']} retried={n_retried}"
    )
    print(f"Output: {run_dir}")


def _find_latest_run_dir(output_dir: Path, provider: str) -> Path | None:
    """Return the most recently created run folder for the given provider."""
    provider_output_dir = get_provider_output_root(output_dir, provider)
    candidates = []

    if provider_output_dir.exists():
        candidates.extend(
            d for d in provider_output_dir.iterdir()
            if d.is_dir() and d.name.startswith(f"external-llms-{provider} ")
        )

    # Backward-compatible fallback for older flat layouts.
    if output_dir.exists():
        candidates.extend(
            d for d in output_dir.iterdir()
            if d.is_dir() and d.name.startswith(f"external-llms-{provider} ")
        )

    candidates = sorted(candidates, key=lambda d: d.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def cmd_retry(
    provider: str,
    output_dir: Path,
    run_dir: Path | None,
    queries_file: Path,
    delay_sec: float,
    headless: bool,
) -> None:
    """Retry failed outputs in the most recent (or specified) run folder."""
    auth_path = AUTH_DIR / f"{provider}.json"
    if not auth_path.exists():
        print(f"Auth not found: {auth_path}. Run: python llm_runner.py login-{provider}")
        sys.exit(1)

    if run_dir is None:
        run_dir = _find_latest_run_dir(output_dir, provider)
        if run_dir is None:
            print(f"No existing run folders found for '{provider}' in {output_dir}")
            sys.exit(1)

    if not run_dir.exists():
        print(f"Run folder not found: {run_dir}")
        sys.exit(1)

    metadata_path = run_dir / "run_metadata.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Could not read run_metadata.json: {e}")
        sys.exit(1)

    # Reconstruct cases from the original queries file and the run's locale list.
    locales = set(metadata.get("locales", ["en"]))
    try:
        cases = load_test_cases_from_json(queries_file, locales)
    except (FileNotFoundError, ValueError) as e:
        print(str(e))
        sys.exit(1)

    failed_cases, failure_counts = _find_failed_cases(run_dir, cases, provider)
    if not failed_cases:
        print(f"No failed outputs found in {run_dir}")
        return

    breakdown = ", ".join(f"{r}: {c}" for r, c in sorted(failure_counts.items()))
    print(f"Run folder: {run_dir}")
    print(f"Retrying {len(failed_cases)} failed queries ({breakdown})...")

    selectors = CHATGPT_RESPONSE_SELECTORS if provider == "chatgpt" else GEMINI_RESPONSE_SELECTORS
    send_selectors = CHATGPT_SEND_SELECTORS if provider == "chatgpt" else GEMINI_SEND_SELECTORS

    with sync_playwright() as p:
        browser, context = _open_browser_context(p, provider, auth_path, headless)
        context.add_init_script(_webdriver_hide_script())
        page = context.new_page()
        page.set_default_timeout(120_000)
        _run_query_loop(
            page, failed_cases, provider, run_dir, selectors, send_selectors, delay_sec,
            label="RETRY "
        )
        context.close() if browser is None else browser.close()

    final_completed, final_failure_counts = _summarize_run_outcomes(run_dir, cases, provider)
    remaining_failures = sum(final_failure_counts.values())
    recovered_failures = len(failed_cases) - remaining_failures
    metadata["retried"] = metadata.get("retried", 0) + len(failed_cases)
    metadata["completed"] = final_completed
    metadata["errors"] = remaining_failures
    metadata["failure_breakdown"] = final_failure_counts
    metadata["ended_at"] = datetime.now(timezone.utc).isoformat()
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Retry done. recovered={recovered_failures} still_failing={remaining_failures}")
    print(f"Output: {run_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="External LLM test runner (ChatGPT, Gemini)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for prov in ("chatgpt", "gemini"):
        p = sub.add_parser(f"login-{prov}", help=f"Record login session for {prov}")
        p.add_argument("--headless", action="store_true", help="Run headless (not recommended for login)")
        p.set_defaults(cmd=f"login-{prov}", provider=prov)

    run_parser = sub.add_parser("run", help="Run queries and save markdown")
    run_parser.add_argument("--provider", choices=("chatgpt", "gemini"), default="chatgpt")
    run_parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory")
    run_parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES_FILE, help="Path to all_queries.json")
    run_parser.add_argument("--limit", "-n", type=int, help="Max number of queries to run")
    run_parser.add_argument("--delay", type=float, default=3.0, help="Seconds between requests")
    run_parser.add_argument("--locale", default="en", help="Locale filter: en, pt, es, comma-separated (e.g. en,pt), or all")
    run_parser.add_argument("--headless", action="store_true")
    run_parser.add_argument("--dry-run", action="store_true", help="Print URLs only, do not run")

    retry_parser = sub.add_parser("retry", help="Retry failed outputs from the latest (or specified) run")
    retry_parser.add_argument("--provider", choices=("chatgpt", "gemini"), default="chatgpt")
    retry_parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT_DIR, help="Base output directory to search for runs")
    retry_parser.add_argument("--run-dir", type=Path, default=None, help="Specific run folder to retry (default: latest for provider)")
    retry_parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES_FILE, help="Path to all_queries.json")
    retry_parser.add_argument("--delay", type=float, default=3.0, help="Seconds between requests")
    retry_parser.add_argument("--headless", action="store_true")

    args = parser.parse_args()
    if args.cmd.startswith("login-"):
        cmd_login(args.provider, getattr(args, "headless", False))
    elif args.cmd == "retry":
        cmd_retry(
            provider=args.provider,
            output_dir=args.output,
            run_dir=args.run_dir,
            queries_file=args.queries,
            delay_sec=args.delay,
            headless=args.headless,
        )
    else:
        cmd_run(
            provider=args.provider,
            output_dir=args.output,
            queries_file=args.queries,
            limit=getattr(args, "limit", None),
            delay_sec=args.delay,
            headless=args.headless,
            dry_run=args.dry_run,
            locale_arg=args.locale,
        )


if __name__ == "__main__":
    main()
