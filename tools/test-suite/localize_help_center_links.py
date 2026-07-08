#!/usr/bin/env python3
"""
Ensure Help Center URLs in issue markdown files list EN, PT, and ES variants.

Reads slug mappings from help-center-content public/navigation.json and adds
any missing localized URLs to target_docs and other_helpful_docs arrays.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse, urlunparse

LOCALES = ("en", "pt", "es")


@dataclass(frozen=True)
class MarkdownDoc:
    slug_prefix: str
    slug: dict[str, str]


def _walk_categories(
    nodes: list[dict],
    slug_prefix: str,
    out: list[MarkdownDoc],
) -> None:
    for node in nodes:
        if node.get("type") == "markdown":
            slug = node.get("slug")
            if isinstance(slug, dict) and all(
                isinstance(slug.get(loc), str) for loc in LOCALES
            ):
                out.append(
                    MarkdownDoc(
                        slug_prefix=slug_prefix,
                        slug={loc: slug[loc] for loc in LOCALES},
                    )
                )
            continue
        children = node.get("children")
        if isinstance(children, list):
            _walk_categories(children, slug_prefix, out)


def load_markdown_docs(navigation_path: Path) -> list[MarkdownDoc]:
    data = json.loads(navigation_path.read_text(encoding="utf-8"))
    navbar = data.get("navbar")
    if not isinstance(navbar, list):
        raise ValueError("navigation.json: missing or invalid 'navbar' array")
    out: list[MarkdownDoc] = []
    for section in navbar:
        prefix = section.get("slugPrefix")
        categories = section.get("categories")
        if not isinstance(prefix, str):
            continue
        if isinstance(categories, list):
            _walk_categories(categories, prefix, out)
    return out


def _build_indexes(docs: list[MarkdownDoc]) -> tuple[dict[str, list[MarkdownDoc]], dict[tuple[str, str], MarkdownDoc]]:
    """By (slug_prefix, any locale slug value) and by slug value alone (ambiguous)."""
    by_prefix_slug: dict[tuple[str, str], MarkdownDoc] = {}
    by_slug_only: dict[str, list[MarkdownDoc]] = {}
    for d in docs:
        for loc in LOCALES:
            s = d.slug[loc]
            key = (d.slug_prefix, s)
            if key not in by_prefix_slug:
                by_prefix_slug[key] = d
            by_slug_only.setdefault(s, []).append(d)
    return by_slug_only, by_prefix_slug


def _strip_fragment_query(url: str) -> str:
    p = urlparse(url)
    clean = urlunparse((p.scheme, p.netloc, p.path, "", "", ""))
    return clean


def parse_help_center_url(url: str) -> tuple[str | None, str, list[str]] | None:
    """
    Returns (locale or None, slug_prefix, slug_path_parts) or None if not a HC URL we handle.

    slug_path_parts are path segments after the slug prefix (usually one segment).
    """
    raw = url.strip()
    p = urlparse(raw)
    if "help.vtex.com" not in (p.netloc or ""):
        return None
    path = (p.path or "").strip("/")
    if not path:
        return None
    parts = [x for x in path.split("/") if x]
    if not parts:
        return None

    locale: str | None = None
    if parts[0] in LOCALES:
        locale = parts[0]
        parts = parts[1:]
    if not parts:
        return None

    # Longest / most specific prefixes first
    if len(parts) >= 3 and parts[0] == "docs" and parts[1] == "tutorials":
        return locale, "docs/tutorials", parts[2:]
    if len(parts) >= 3 and parts[0] == "docs" and parts[1] == "tracks":
        return locale, "docs/tracks", parts[2:]
    if len(parts) >= 3 and parts[0] == "docs" and parts[1] == "troubleshooting":
        return locale, "troubleshooting", parts[2:]
    if len(parts) >= 3 and parts[0] == "docs" and parts[1] == "faq":
        return locale, "faq", parts[2:]
    if len(parts) >= 2 and parts[0] in ("tutorial", "tutorials"):
        return locale, "docs/tutorials", parts[1:]
    if len(parts) >= 2 and parts[0] == "faq":
        return locale, "faq", parts[1:]
    if len(parts) >= 2 and parts[0] == "troubleshooting":
        return locale, "troubleshooting", parts[1:]
    if len(parts) >= 2 and parts[0] == "announcements":
        return locale, "announcements", parts[1:]
    if len(parts) >= 2 and parts[0] == "known-issues":
        return locale, "known-issues", parts[1:]

    return None


def find_doc_for_url(
    url: str,
    by_slug_only: dict[str, list[MarkdownDoc]],
    by_prefix_slug: dict[tuple[str, str], MarkdownDoc],
) -> MarkdownDoc | None:
    parsed = parse_help_center_url(_strip_fragment_query(url))
    if not parsed:
        return None
    _locale, slug_prefix, slug_parts = parsed
    if not slug_parts:
        return None
    slug_str = "/".join(slug_parts)

    direct = by_prefix_slug.get((slug_prefix, slug_str))
    if direct:
        return direct

    candidates = by_slug_only.get(slug_str, [])
    if len(candidates) == 1:
        return candidates[0]
    for c in candidates:
        if c.slug_prefix == slug_prefix:
            return c
    return None


def canonical_help_urls(doc: MarkdownDoc) -> list[str]:
    return [
        f"https://help.vtex.com/{loc}/{doc.slug_prefix}/{doc.slug[loc]}"
        for loc in LOCALES
    ]


def is_dev_portal(url: str) -> bool:
    try:
        return "developers.vtex.com" in urlparse(url).netloc
    except Exception:
        return "developers.vtex.com" in url


def is_help_center(url: str) -> bool:
    try:
        return "help.vtex.com" in urlparse(url).netloc
    except Exception:
        return "help.vtex.com" in url


ARRAY_FIELD_RE = re.compile(
    r"^(\|\s*\*\*(target_docs|expected_docs|other_helpful_docs)\*\*\s*\|\s*)(\[.*\])(\s*\|)\s*$"
)


def parse_table_array_line(line: str) -> tuple[str, str, list[str], str, str] | None:
    """
    Returns (prefix, field_name, urls list, suffix, full_line_ending) if matched.
    """
    m = ARRAY_FIELD_RE.match(line.rstrip("\r\n"))
    if not m:
        return None
    prefix, field, json_blob, tail = m.group(1), m.group(2), m.group(3), m.group(4)
    try:
        arr = json.loads(json_blob)
    except json.JSONDecodeError:
        return None
    if not isinstance(arr, list):
        return None
    urls = [x for x in arr if isinstance(x, str)]
    return prefix, field, urls, tail, line[len(line.rstrip("\r\n")) :]


def extend_localized_urls(
    urls: list[str],
    by_slug_only: dict[str, list[MarkdownDoc]],
    by_prefix_slug: dict[tuple[str, str], MarkdownDoc],
) -> tuple[list[str], list[tuple[str, str]]]:
    """
    Returns (new_list, events) where each event is ("add", url) or ("warn", detail).
    """
    seen = set(urls)
    out = list(urls)
    events: list[tuple[str, str]] = []

    for u in urls:
        if is_dev_portal(u) or not is_help_center(u):
            continue
        doc = find_doc_for_url(u, by_slug_only, by_prefix_slug)
        if not doc:
            events.append(("warn", f"no navigation match for Help Center URL: {u}"))
            continue
        for canonical in canonical_help_urls(doc):
            if canonical not in seen:
                out.append(canonical)
                seen.add(canonical)
                events.append(("add", canonical))

    return out, events


def process_markdown_file(
    path: Path,
    by_slug_only: dict[str, list[MarkdownDoc]],
    by_prefix_slug: dict[tuple[str, str], MarkdownDoc],
    write: bool,
) -> tuple[list[str], bool]:
    """Returns (log lines for this file, whether array content would change)."""
    log: list[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    changed = False

    for i, line in enumerate(lines):
        parsed = parse_table_array_line(line)
        if not parsed:
            continue
        prefix, field, urls, tail, _ = parsed
        new_urls, events = extend_localized_urls(
            urls, by_slug_only, by_prefix_slug
        )
        for kind, payload in events:
            if kind == "add":
                log.append(f"{path.name} | {field} | added: {payload}")
            else:
                log.append(f"{path.name} | {field} | warn: {payload}")
        if new_urls != urls:
            changed = True
            blob = json.dumps(new_urls, ensure_ascii=False)
            lines[i] = f"{prefix}{blob}{tail}\n"

    if changed and write:
        path.write_text("".join(lines), encoding="utf-8", newline="")

    return log, changed


def default_navigation_path() -> Path:
    repo_root = Path(__file__).resolve().parent.parent.parent
    sibling = repo_root.parent / "help-center-content" / "public" / "navigation.json"
    return sibling


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add missing EN/PT/ES Help Center URLs to issue docs (target_docs, other_helpful_docs)."
    )
    parser.add_argument(
        "--issues-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent
        / "docs"
        / "test-suite"
        / "issues",
        help="Directory containing issue .md files",
    )
    parser.add_argument(
        "--navigation",
        type=Path,
        default=None,
        help="Path to help-center-content public/navigation.json",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write changes to markdown files (default is dry-run)",
    )
    args = parser.parse_args()
    nav_path = args.navigation or default_navigation_path()
    if not nav_path.is_file():
        print(
            f"Error: navigation.json not found at {nav_path}\n"
            "Pass --navigation with the correct path.",
            file=sys.stderr,
        )
        return 1

    docs = load_markdown_docs(nav_path)
    by_slug_only, by_prefix_slug = _build_indexes(docs)

    issue_files = sorted(args.issues_dir.glob("*.md"))
    if not issue_files:
        print(f"No .md files in {args.issues_dir}", file=sys.stderr)
        return 1

    all_log: list[str] = []
    unchanged_names: list[str] = []
    for f in issue_files:
        file_log, file_changed = process_markdown_file(
            f, by_slug_only, by_prefix_slug, write=args.write
        )
        all_log.extend(file_log)
        if not file_changed:
            unchanged_names.append(f.name)

    if all_log:
        print("Changes (file | field | added: or warn:):")
        for line in all_log:
            print(line)
    else:
        print("Changes: none")

    warns = sum(1 for x in all_log if " | warn:" in x)
    adds = sum(1 for x in all_log if " | added: " in x)

    print()
    print(f"Unchanged files ({len(unchanged_names)}):")
    if unchanged_names:
        for name in unchanged_names:
            print(f"  {name}")
    else:
        print("  (none)")

    if warns:
        print(f"\n{warns} warning(s) - fix URLs or navigation data.", file=sys.stderr)
    print(
        f"\nSummary: {len(issue_files)} file(s) scanned; "
        f"{adds} URL addition(s); {len(unchanged_names)} unchanged file(s).",
        flush=True,
    )
    return 1 if warns else 0


if __name__ == "__main__":
    raise SystemExit(main())
