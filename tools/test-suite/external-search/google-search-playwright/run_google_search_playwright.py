#!/usr/bin/env python3
"""
Google Search Playwright runner: simulate a user searching on google.com and parse the SERP.

Reads `data/test-suite/external-search/all_queries.json` by default, opens each query in a browser
(Playwright Chromium), collects the first 7 organic results per query, and writes
`results.json` inside a per-run folder under `results/external-search/google-search-playwright/`.

No API key required. Requires: pip install playwright && playwright install chromium.

Usage:
  python run_google_search_playwright.py run
  python run_google_search_playwright.py run --limit-issues 3
  python run_google_search_playwright.py run --locale en
  python run_google_search_playwright.py run --issue checkout-api-orders-01 --locale pt
  python run_google_search_playwright.py run --style familiar
  python run_google_search_playwright.py run --query "exact query text"
  python run_google_search_playwright.py run --headless      # force headless (default is a visible browser)
"""

import argparse
import json
import re
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent.parent
DEFAULT_QUERIES_FILE = REPO_ROOT / "data" / "test-suite" / "external-search" / "all_queries.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "results" / "external-search"
GOOGLE_SEARCH_URL = "https://www.google.com/search"
NUM_RESULTS = 7


def load_queries(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def create_run_directory(base_output: Path, path_slug: str, timestamp: datetime | None = None) -> Path:
    """Create a per-run output folder named '<path> YYYY-MM-DD HH-MM'."""
    ts = timestamp or datetime.now()
    folder_name = f"{path_slug} {ts.strftime('%Y-%m-%d %H-%M')}"
    run_dir = base_output / path_slug / folder_name
    if not run_dir.exists():
        run_dir.mkdir(parents=True, exist_ok=False)
        return run_dir

    suffix = 2
    while True:
        candidate = base_output / path_slug / f"{folder_name} ({suffix})"
        if not candidate.exists():
            candidate.mkdir(parents=True, exist_ok=False)
            return candidate
        suffix += 1


def _apply_filters(
    issues: list,
    issue_id: str | None = None,
    locale: str | None = None,
    style: str | None = None,
    query_text: str | None = None,
    limit_issues: int | None = None,
) -> list:
    """Filter issues and their queries by issue_id, locale, style, and/or exact query text. Returns new list of issues (with filtered queries)."""
    out = []
    for issue in issues:
        if issue_id is not None and issue.get("issue_id") != issue_id:
            continue
        queries = list(issue.get("queries", []))
        if locale is not None:
            queries = [q for q in queries if (q.get("locale") or "").strip().lower() == locale.strip().lower()]
        if style is not None:
            queries = [q for q in queries if (q.get("style") or "").strip().lower() == style.strip().lower()]
        if query_text is not None:
            qnorm = query_text.strip()
            queries = [q for q in queries if (q.get("query") or "").strip() == qnorm]
        if not queries:
            continue
        out.append({**issue, "queries": queries})
    if limit_issues is not None:
        out = out[:limit_issues]
    return out


def _url_to_fallback_description(url: str) -> str:
    """Return a short readable label for a URL when title/snippet are missing."""
    if not url or not url.strip():
        return "(no description)"
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = (parsed.netloc or "").strip()
        path = (parsed.path or "").strip().strip("/")
        if netloc and path:
            return f"{netloc}/{path}"
        if netloc:
            return netloc
        if path:
            return path
        return url[:200] if len(url) > 200 else url
    except Exception:
        return url[:200] if url and len(url) > 200 else (url or "(no description)")


def _normalize_google_url(href: str) -> str | None:
    """Return a clean external URL, or None for Google-internal / invalid links."""
    if not href or not href.strip():
        return None
    href = href.strip()
    if "google.com/sorry" in href or "accounts.google" in href:
        return None
    if "/url?q=" in href:
        m = re.search(r"/url\?q=([^&]+)", href)
        if m:
            href = urllib.parse.unquote(m.group(1))
    # Exclude any Google-owned URL (except webcache) so only organic external links count
    if "google.com" in href and "webcache" not in href:
        return None
    return href if href.startswith("http") else None


def _extract_urls_from_html(html: str, max_results: int) -> list[dict]:
    """Fallback: extract /url?q=... links from raw HTML (sometimes DOM selectors miss)."""
    results = []
    seen = set()
    for m in re.finditer(r'href\s*=\s*["\']/url\?q=([^&"\']+)', html):
        raw = m.group(1)
        try:
            href = urllib.parse.unquote(raw)
        except Exception:
            href = raw
        if not href.startswith("http") or "google.com" in href and "/search" not in href:
            continue
        if href in seen:
            continue
        seen.add(href)
        results.append({"link": href, "title": "", "snippet": ""})
        if len(results) >= max_results:
            break
    return results


def _extract_serp_results(page, max_results: int) -> list[dict]:
    """Parse Google SERP for organic results. Returns list of {link, title, snippet}."""
    results = []
    try:
        page.wait_for_selector("#search, #rso, #main, [role='main']", timeout=20000)
        time.sleep(3)
    except Exception:
        pass

    def extract_from_block(block):
        try:
            title_el = block.query_selector("h3")
            link_el = block.query_selector("h3 a[href]") if title_el else block.query_selector("a[href^='http']")
            if not link_el:
                link_el = block.query_selector("a[href*='/url?q=']")
            if not link_el:
                return None
            href = link_el.get_attribute("href") or ""
            href = _normalize_google_url(href)
            if not href:
                return None
            title = (title_el.inner_text() or "").strip() if title_el else ""
            snippet_el = block.query_selector(".VwiC3b, [data-sncf]")
            if not snippet_el:
                for div in block.query_selector_all("div"):
                    text = (div.inner_text() or "").strip()
                    if 30 < len(text) < 400 and href not in text:
                        snippet_el = div
                        break
            snippet = (snippet_el.inner_text() or "").strip()[:500] if snippet_el else ""
            return {"link": href, "title": title, "snippet": snippet}
        except Exception:
            return None

    for selector in [
        "div#rso div.MjjYud",
        "div#rso div.g",
        "div.MjjYud",
        "div.g",
        "#search div.g",
    ]:
        try:
            blocks = page.query_selector_all(selector)
            for block in blocks:
                if len(results) >= max_results:
                    break
                item = extract_from_block(block)
                if item and not any(r["link"] == item["link"] for r in results):
                    results.append(item)
            # Do not return early: keep trying other selectors and fallback until we have enough
            if len(results) >= max_results:
                return results[:max_results]
        except Exception:
            continue

    try:
        rso = page.query_selector("#rso")
        if rso:
            for a in rso.query_selector_all("a[href*='http']"):
                if len(results) >= max_results:
                    break
                href = a.get_attribute("href") or ""
                href = _normalize_google_url(href)
                if not href:
                    continue
                try:
                    parent = a.evaluate_handle("el => el.closest('div.g') || el.closest('div[class]') || el.parentElement")
                    try:
                        title_el = parent.query_selector("h3") if parent else None
                        title = (title_el.inner_text() or "").strip() if title_el else (a.inner_text() or "").strip()
                    finally:
                        if parent:
                            parent.dispose()
                except Exception:
                    title = (a.inner_text() or "").strip()
                if not title and len(href) < 20:
                    continue
                if not any(r["link"] == href for r in results):
                    results.append({"link": href, "title": title[:300] if title else "", "snippet": ""})
    except Exception:
        pass

    # Fallback: regex on raw HTML for /url?q= links (DOM may differ by locale/A-B test)
    if len(results) < max_results:
        try:
            html = page.content()
            regex_results = _extract_urls_from_html(html, max_results)
            for r in regex_results:
                if len(results) >= max_results:
                    break
                link = _normalize_google_url(r.get("link") or "")
                if not link or any(x["link"] == link for x in results):
                    continue
                results.append({"link": link, "title": r.get("title") or "", "snippet": r.get("snippet") or ""})
        except Exception:
            pass

    return results[:max_results]


def _extract_ai_overview(page) -> str:
    """Extract AI Overview (Visão geral criada por IA) text from the SERP if present."""
    parts = []
    # Known selectors for AI Overview content (Google may change class names over time)
    content_selectors = [
        "div.WaaZC",  # main AI overview text container
        "[data-tts-attrid='waiazc']",
        "div[data-attrid='waiazc']",
        ".AIrSbb",  # alternative class seen in some regions
        "div.g .w8qArf",  # overview snippet area
    ]
    for sel in content_selectors:
        try:
            els = page.query_selector_all(sel)
            for el in els:
                try:
                    text = (el.inner_text() or "").strip()
                    if text and len(text) > 20 and text not in parts:
                        parts.append(text)
                except Exception:
                    pass
        except Exception:
            continue

    # Try to find a block that contains the AI Overview label (EN/PT) and get its text
    for label in ["AI Overview", "Visão geral criada por IA", "Overview", "Resumo"]:
        try:
            loc = page.get_by_text(label, exact=False)
            if loc.count() > 0:
                for i in range(min(loc.count(), 2)):
                    try:
                        node = loc.nth(i).locator("xpath=./ancestor::div[@class][1]")
                        if node.count() > 0:
                            text = (node.first.inner_text() or "").strip()
                            if text and len(text) > 30 and text not in parts:
                                parts.append(text)
                                break
                    except Exception:
                        pass
        except Exception:
            pass

    # Fallback: regex in HTML for common AI overview wrapper text
    if not parts:
        try:
            html = page.content()
            # Match content inside typical overview blocks (obfuscated class names may vary)
            for pattern in [
                r'(?:AI Overview|Visão geral criada por IA)[^<]*(?:</[^>]+>)\s*([^<]+(?:(?:<(?!/div)[^>]*>[^<]*)*)?)',
                r'class="[^"]*WaaZC[^"]*"[^>]*>([^<]+)',
            ]:
                for m in re.finditer(pattern, html, re.IGNORECASE | re.DOTALL):
                    text = re.sub(r"<[^>]+>", " ", m.group(1)).strip()
                    text = re.sub(r"\s+", " ", text)[:3000]
                    if len(text) > 40 and text not in parts:
                        parts.append(text)
                        break
        except Exception:
            pass

    if not parts:
        return ""
    # Deduplicate and join; prefer first (usually the main overview)
    seen = set()
    unique = []
    for p in parts:
        key = p[:200]
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return "\n\n".join(unique)[:15000].strip()


def _is_captcha_page(url: str, html: str) -> bool:
    """Return True if the current page is a Google consent/captcha/sorry page.

    Uses specific structural signals to avoid false positives from search results
    that merely contain the words 'captcha' or 'sorry' in their text.
    """
    if "consent.google" in url or "sorry/index" in url:
        return True
    # Specific HTML structural markers for Google captcha/consent/sorry pages
    specific_markers = [
        'id="captcha-form"',
        'action="https://www.google.com/sorry',
        'google.com/sorry',
        'class="g-recaptcha"',
        'data-sitekey=',
        'name="recaptcha"',
        'id="recaptcha"',
        'detected unusual traffic',
        'unusual traffic from your',
        'our systems have detected unusual',
        'please solve this captcha',
        'i\'m not a robot',
    ]
    html_lower = html.lower()
    return any(marker.lower() in html_lower for marker in specific_markers)


def _has_search_results(page) -> bool:
    """Return True if the page has Google search results loaded."""
    try:
        return page.query_selector("#search, #rso") is not None
    except Exception:
        return False


def _scrape_into_entry(page, entry: dict, query_text: str, debug_save_dir: Path | None) -> None:
    """Extract SERP results and AI overview from the current page and populate entry in-place."""
    items = _extract_serp_results(page, NUM_RESULTS)
    ai_overview = _extract_ai_overview(page)
    entry["ai_overview_content"] = ai_overview
    if not items and debug_save_dir:
        try:
            safe = re.sub(r"[^\w\-]", "_", query_text)[:80]
            html = page.content()
            (debug_save_dir / f"serp_{safe}.html").write_text(html, encoding="utf-8")
            print(f"    [debug] No results; saved SERP HTML to serp_{safe}.html")
        except Exception:
            pass
    for rank, item in enumerate(items, start=1):
        link = item.get("link", "")
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        description = title
        if snippet:
            description = f"{title}: {snippet}" if title else snippet
        if not (description or "").strip():
            description = _url_to_fallback_description(link)
        entry["output_urls"].append({
            "rank": str(rank),
            "url_address": link,
            "url_description": description,
        })


def _wait_for_captcha_resolved(page, timeout_sec: int = 120, poll_sec: float = 2.0) -> bool:
    """Poll the browser page until the captcha/consent is gone or timeout expires.

    Returns True if the page recovered (search results visible), False on timeout.
    The user solves the captcha manually in the visible browser window; this function
    detects the resolution automatically without requiring any terminal input.
    Maximum wait is capped at 120 seconds regardless of the caller's value.
    """
    timeout_sec = min(timeout_sec, 120)
    print(f"    [Captcha/consent detected] Solve it in the browser window. "
          f"Script will resume automatically once search results appear "
          f"(timeout: {timeout_sec}s)...")
    elapsed = 0
    while elapsed < timeout_sec:
        time.sleep(poll_sec)
        elapsed += poll_sec
        try:
            current_url = page.url
            current_html = page.content()
        except Exception:
            continue
        if not _is_captcha_page(current_url, current_html):
            print(f"    [Captcha resolved after {elapsed:.0f}s] Continuing...")
            return True
        if int(elapsed) % 30 == 0:
            print(f"    [Waiting for captcha... {elapsed:.0f}s elapsed]")
    return False


def run_single_pass(
    issues: list,
    delay_sec: float,
    dry_run: bool,
    page,
    headless: bool,
    debug_save_dir: Path | None = None,
    wait_for_captcha: bool = False,
) -> list:
    session_1_output = []

    for issue in issues:
        issue_id = issue.get("issue_id", "")
        source_file = issue.get("source_file", "")
        queries_in = issue.get("queries", [])
        queries_out = []

        for q in queries_in:
            query_text = q.get("query", "")
            style = q.get("style", "")
            entry = {
                "query": query_text,
                "style": style,
                "output_urls": [],
                "ai_overview_content": "",
            }
            if dry_run:
                queries_out.append(entry)
                continue

            url = f"{GOOGLE_SEARCH_URL}?q={urllib.parse.quote(query_text)}"
            try:
                page.goto(url, wait_until="load", timeout=25000)
                page_html = page.content()
                if _is_captcha_page(page.url, page_html):
                    if wait_for_captcha:
                        resolved = _wait_for_captcha_resolved(page)
                        if resolved:
                            _scrape_into_entry(page, entry, query_text, debug_save_dir)
                        else:
                            entry["ai_overview_content"] = "[Error: Captcha/consent not resolved within timeout; re-run to retry]"
                    else:
                        entry["ai_overview_content"] = "[Error: Google consent or captcha page; try --no-headless and --wait-for-captcha to solve manually]"
                else:
                    _scrape_into_entry(page, entry, query_text, debug_save_dir)
            except Exception as e:
                entry["ai_overview_content"] = f"[Error: {e}]"

            queries_out.append(entry)
            if delay_sec > 0:
                time.sleep(delay_sec)

        session_1_output.append({
            "issue_id": issue_id,
            "source_file": source_file,
            "queries": queries_out,
        })

    return session_1_output


def run(
    queries_path: Path,
    output_dir: Path,
    limit_issues: int | None,
    delay_sec: float,
    dry_run: bool,
    headless: bool,
    debug_save_html: bool = False,
    wait_for_captcha: bool = False,
    no_persistent_profile: bool = False,
    issue_id: str | None = None,
    locale: str | None = None,
    style: str | None = None,
    query_text: str | None = None,
) -> None:
    data = load_queries(queries_path)
    issues = _apply_filters(
        data.get("issues", []),
        issue_id=issue_id,
        locale=locale,
        style=style,
        query_text=query_text,
        limit_issues=limit_issues,
    )
    if not issues:
        print("No issues or queries match the filters.")
        return

    total_queries = sum(len(i.get("queries", [])) for i in issues)
    filters_desc = []
    if issue_id:
        filters_desc.append(f"issue={issue_id}")
    if locale:
        filters_desc.append(f"locale={locale}")
    if style:
        filters_desc.append(f"style={style}")
    if query_text:
        filters_desc.append("query=...")
    if limit_issues is not None and not (issue_id and not locale and not style and not query_text):
        filters_desc.append(f"limit={limit_issues}")
    filter_str = " [" + ", ".join(filters_desc) + "]" if filters_desc else ""
    print(f"Running {len(issues)} issue(s), {total_queries} query(ies){filter_str}. Headless={headless}. Dry-run={dry_run}.")

    run_started_at = datetime.now()
    run_dir = create_run_directory(output_dir, "google-search-playwright", run_started_at)

    if dry_run:
        session_1_output = run_single_pass(issues, delay_sec, True, None, headless)
    else:
        with sync_playwright() as p:
            if no_persistent_profile:
                # Ephemeral context: no profile dir, avoids TargetClosedError when profile is locked/corrupted
                browser = p.chromium.launch(headless=headless)
                context = browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    locale="en-US",
                    extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
                )
                page = context.new_page()
            else:
                # Persistent context: reuses cookies/session across runs to reduce consent/recaptcha
                profile_dir = SCRIPT_DIR / ".playwright-profile"
                profile_dir.mkdir(exist_ok=True)
                context = p.chromium.launch_persistent_context(
                    profile_dir,
                    headless=headless,
                    viewport={"width": 1280, "height": 800},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    locale="en-US",
                    extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
                )
                page = context.pages[0] if context.pages else context.new_page()
            page.set_default_timeout(25000)
            try:
                session_1_output = run_single_pass(
                    issues, delay_sec, False, page, headless,
                    debug_save_dir=run_dir if debug_save_html else None,
                    wait_for_captcha=wait_for_captcha,
                )
            finally:
                context.close()

    out_file = run_dir / "results.json"
    result = {
        "path": data.get("path", "External search"),
        "runner": "Google Search Playwright",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_file": queries_path.name,
        "run_directory": str(run_dir),
        "session_1": {"output": session_1_output},
    }
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Google Search Playwright: simulate user search on google.com and parse SERP"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    run_parser = sub.add_parser(
        "run",
        help="Run searches and write results.json inside a per-run output folder",
    )
    run_parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES_FILE, help="Path to all_queries.json")
    run_parser.add_argument("-o", "--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory")
    run_parser.add_argument("-n", "--limit-issues", type=int, default=None, help="Run only first N issues")
    run_parser.add_argument("--issue", type=str, default=None, metavar="ISSUE_ID", help="Run only queries from this issue (e.g. checkout-api-orders-01)")
    run_parser.add_argument("--locale", type=str, default=None, choices=["en", "es", "pt"], help="Run only queries for this locale (en, es, pt)")
    run_parser.add_argument("--style", type=str, default=None, choices=["naive", "familiar", "expert"], help="Run only queries with this style")
    run_parser.add_argument("--query", type=str, default=None, metavar="TEXT", help="Run only the query whose text matches exactly (e.g. \"checkout api update order request body format vtex\")")
    run_parser.add_argument("--delay", type=float, default=2.0, help="Seconds between requests (default: 2.0)")
    run_parser.add_argument("--dry-run", action="store_true", help="List queries only, no browser")
    run_parser.add_argument("--headless", action="store_true", dest="headless", help="Run headless (no visible window). Default is a visible browser to reduce consent/captcha walls.")
    run_parser.add_argument("--no-headless", action="store_true", dest="no_headless", help="(Deprecated; visible browser is now the default) Show browser window")
    run_parser.add_argument("--wait-for-captcha", action="store_true", dest="wait_for_captcha", help="On captcha/consent: poll browser automatically until search results appear (solve in browser window, no Enter needed)")
    run_parser.add_argument("--no-persistent-profile", action="store_true", dest="no_persistent_profile", help="Use ephemeral browser (no profile dir); use if persistent context fails with TargetClosedError")
    run_parser.add_argument("--debug-save-html", action="store_true", help="Save SERP HTML when no results (for debugging)")

    args = parser.parse_args()
    if args.cmd == "run":
        run(
            queries_path=args.queries,
            output_dir=args.output_dir,
            limit_issues=getattr(args, "limit_issues", None),
            delay_sec=args.delay,
            dry_run=args.dry_run,
            headless=getattr(args, "headless", False),
            debug_save_html=getattr(args, "debug_save_html", False),
            wait_for_captcha=getattr(args, "wait_for_captcha", False),
            no_persistent_profile=getattr(args, "no_persistent_profile", False),
            issue_id=getattr(args, "issue", None),
            locale=getattr(args, "locale", None),
            style=getattr(args, "style", None),
            query_text=getattr(args, "query", None),
        )


if __name__ == "__main__":
    main()
