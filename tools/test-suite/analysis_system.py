#!/usr/bin/env python3
"""
Phase 1 analysis system for the VTEX docs test suite.

This script ingests the raw artifacts written by the path runners, joins them
with canonical issue metadata from docs/test-suite/issues, computes link/rank
metrics, and exports JSON artifacts aligned with the Analysis System RFC and
its follow-up investigation notes.

By default the analysis focuses on link and rank metrics only and ignores
answer-quality scoring (``mean_quality`` stays ``None``, ``quality_scored``
stays ``[]``). Passing ``run --score-quality`` opts into an extra stage that
scores text-answer paths via ``tools/quality-scoring`` and populates those
fields; the flag defaults to off so normal runs are unchanged.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse


LOCALES = ("en", "pt", "es")
STYLES = ("naive", "familiar", "expert")

HELP_CENTER_HOST = "help.vtex.com"
DEVELOPERS_HOST = "developers.vtex.com"

INTERNAL_SEARCH_TOP_K = 7
ALL_LINKS_TOP_K = "all_returned_links"

DOCS_ASSISTANT_LINK_SOURCES = ("markdown", "suggested_sources")

# Paths that produce a free-text answer eligible for optional quality scoring.
# Link-only paths (Algolia/Hybrid/Google) have no text answer and are skipped.
QUALITY_TEXT_ANSWER_SOURCE_KEYS = ("docs-assistant.api", "llm.chatgpt", "llm.gemini")

RUN_SELECTION_HEALTH_MINIMUMS = {
    "external-search.google-search-playwright": 0.50,
}

DOC_TYPE_ALIASES = {
    "tutorial": "tutorials",
    "track": "tracks",
    "trackarticle": "tracks",
}

ARTIFACT_FILENAMES = {
    "issues_processed": "issues_processed.json",
    "aggregates_by_path_locale": "aggregates_by_path_locale.json",
    "aggregates_by_locale": "aggregates_by_locale.json",
    "aggregates_by_style": "aggregates_by_style.json",
    "aggregates_by_persona": "aggregates_by_persona.json",
    "aggregates_by_style_locale": "aggregates_by_style_locale.json",
    "aggregates_by_persona_locale": "aggregates_by_persona_locale.json",
    "failure_list": "failure_list.json",
    "run_summary": "run_summary.json",
    "comparison_summary": "comparison_summary.json",
    "comparison_by_path_locale": "comparison_by_path_locale.json",
    "comparison_by_locale": "comparison_by_locale.json",
    "comparison_by_style": "comparison_by_style.json",
    "comparison_by_persona": "comparison_by_persona.json",
    "comparison_by_style_locale": "comparison_by_style_locale.json",
    "comparison_by_persona_locale": "comparison_by_persona_locale.json",
    "comparison_by_issue": "comparison_by_issue.json",
    "failure_delta": "failure_delta.json",
}


@dataclass(frozen=True)
class ParsedUrl:
    raw_url: str
    host: str
    is_help_center: bool
    locale: str | None
    doctype: str | None
    slug: str | None
    exact_identity: str


@dataclass
class IssueRecord:
    issue_id: str
    persona: str
    product: str
    user_intent: str
    surface: str
    source_file: str
    expected_docs: list[str]
    other_helpful_docs: list[str]
    expected_refs: list[ParsedUrl]
    helpful_refs: list[ParsedUrl]
    help_center_explicit_locale_keys: set[tuple[str, str, str, str]]


@dataclass(frozen=True)
class SourceConfig:
    key: str
    path_type: str
    variant: str
    family: str
    results_dir: Path
    query_file: Path | None
    supported_locales: tuple[str, ...]


@dataclass
class RunCandidate:
    run_dir: Path
    artifact_path: Path | None
    timestamp: datetime
    actual_queries: int
    expected_queries: int
    nonempty_queries: int
    nonempty_ratio: float
    is_full: bool
    is_healthy: bool


@dataclass
class QueryEvaluation:
    issue_id: str
    source_key: str
    path_type: str
    variant: str
    locale: str
    style: str
    query: str
    link_source: str | None
    coverage_status: str
    expected_rank: int | None
    expected_found: bool
    expected_count: int
    expected_mrr: float
    expected_translated_rank: int | None
    expected_translated_found: bool
    expected_translated_count: int
    expected_any_locale_rank: int | None
    expected_any_locale_found: bool
    expected_any_locale_count: int
    expected_any_locale_mrr: float
    helpful_rank: int | None
    helpful_found: bool
    helpful_count: int
    helpful_translated_rank: int | None
    helpful_translated_found: bool
    helpful_translated_count: int
    helpful_any_locale_rank: int | None
    helpful_any_locale_found: bool
    helpful_any_locale_count: int
    any_relevant_found: bool
    any_relevant_any_locale_found: bool
    classified_results: list[dict[str, Any]]
    include_in_global_rollups: bool
    include_in_path_rollups: bool
    include_in_failure_list: bool


def workspace_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value not in seen:
            deduped.append(value)
            seen.add(value)
    return deduped


def canonicalize_host(host: str) -> str:
    lowered = (host or "").strip().lower()
    return lowered[4:] if lowered.startswith("www.") else lowered


def normalize_fragment(fragment: str) -> str:
    normalized = unquote(fragment or "").strip().lower()
    if not normalized or normalized.startswith(":~:text="):
        return ""
    return normalized


def normalize_doc_type(value: str | None) -> str | None:
    normalized = (value or "").strip().lower()
    if not normalized:
        return None
    return DOC_TYPE_ALIASES.get(normalized, normalized)


def terminal_slug(parts: list[str]) -> str | None:
    if len(parts) < 2:
        return None
    slug = parts[-1].strip().lower()
    return slug or None


def locale_from_query_string(query: str) -> str | None:
    """Read Help Center locale from ?locale=en|pt|es when the path omits a locale segment."""
    if not query:
        return None
    raw_values = parse_qs(query, keep_blank_values=False).get("locale")
    if not raw_values:
        return None
    locale = str(raw_values[0]).strip().lower()
    return locale if locale in LOCALES else None


def normalize_help_center_path(path: str) -> tuple[str | None, str | None, str | None]:
    parts = [segment.lower() for segment in unquote(path).split("/") if segment]
    locale = None
    if parts and parts[0] == "docs":
        parts.pop(0)
    if parts and parts[0] in LOCALES:
        locale = parts.pop(0)
    if parts and parts[0] == "docs":
        parts.pop(0)
    if not parts:
        return locale, None, None
    doctype = normalize_doc_type(parts[0])
    slug = terminal_slug(parts)
    return locale, doctype, slug


def normalize_generic_identity(host: str, path: str, fragment: str) -> tuple[str | None, str | None, str]:
    parts = [segment.lower() for segment in unquote(path).split("/") if segment]
    doctype = None
    slug = None
    if host == DEVELOPERS_HOST:
        if parts[:2] == ["updates", "release-notes"]:
            doctype = "updates/release-notes"
            slug = terminal_slug(parts[1:]) or (parts[2].strip().lower() if len(parts) == 3 else None)
        elif parts and parts[0] == "docs":
            doctype = normalize_doc_type(parts[1] if len(parts) > 1 else "docs")
            slug = terminal_slug(parts[1:])
        elif parts:
            doctype = normalize_doc_type(parts[0])
            slug = terminal_slug(parts)
    elif parts:
        doctype = normalize_doc_type(parts[0])
        slug = terminal_slug(parts)

    normalized_path = "/" + "/".join(parts) if parts else "/"
    exact_identity = f"{host}|{normalized_path}"
    if fragment:
        exact_identity += f"#{fragment}"
    return doctype, slug, exact_identity


def parse_url(url: str) -> ParsedUrl:
    raw_url = (url or "").strip()
    try:
        parsed = urlparse(raw_url)
    except ValueError:
        # Some raw artifacts occasionally contain malformed URLs (for example,
        # broken bracket characters). Those should be treated as non-matching
        # links, not as fatal analysis errors.
        fallback_identity = raw_url.lower() if raw_url else "_invalid_url"
        return ParsedUrl(
            raw_url=url,
            host="",
            is_help_center=False,
            locale=None,
            doctype=None,
            slug=None,
            exact_identity=fallback_identity,
        )
    host = canonicalize_host(parsed.netloc)
    path = parsed.path or "/"
    fragment = normalize_fragment(parsed.fragment)

    if host == HELP_CENTER_HOST:
        locale, doctype, slug = normalize_help_center_path(path)
        if locale is None:
            locale = locale_from_query_string(parsed.query)
        exact_identity = f"{host}|{locale or '_'}|{doctype or '_'}|{slug or '_'}"
        return ParsedUrl(
            raw_url=url,
            host=host,
            is_help_center=True,
            locale=locale,
            doctype=doctype,
            slug=slug,
            exact_identity=exact_identity,
        )

    doctype, slug, exact_identity = normalize_generic_identity(host, path, fragment)
    return ParsedUrl(
        raw_url=url,
        host=host,
        is_help_center=False,
        locale=None,
        doctype=doctype,
        slug=slug,
        exact_identity=exact_identity,
    )


def help_center_match_key(host: str, locale: str, doctype: str | None, slug: str | None) -> str | None:
    if not doctype or not slug:
        return None
    return f"{host}|{locale}|{doctype}|{slug}"


def generic_match_key(host: str, doctype: str | None, slug: str | None) -> str | None:
    if not doctype or not slug:
        return None
    return f"{host}|{doctype}|{slug}"


def path_allowed_for_source(ref: ParsedUrl, source_key: str) -> bool:
    if source_key == "internal-search.algolia-helpcenter":
        return ref.host == HELP_CENTER_HOST
    if source_key == "internal-search.algolia-devportal":
        return ref.host == DEVELOPERS_HOST
    if source_key == "internal-search.hybrid-search":
        return ref.host in {HELP_CENTER_HOST, DEVELOPERS_HOST}
    return True


def ref_key_for_query_locale(issue: IssueRecord, ref: ParsedUrl, query_locale: str) -> str | None:
    if ref.is_help_center:
        if ref.locale == query_locale:
            return help_center_match_key(ref.host, query_locale, ref.doctype, ref.slug)
        if ref.locale is None:
            bridge_key = (ref.host, query_locale, ref.doctype or "", ref.slug or "")
            if bridge_key in issue.help_center_explicit_locale_keys:
                return help_center_match_key(ref.host, query_locale, ref.doctype, ref.slug)
        return None

    if query_locale != "en":
        return None

    return generic_match_key(ref.host, ref.doctype, ref.slug) or ref.exact_identity


def result_key_for_query_locale(ref: ParsedUrl, query_locale: str) -> str | None:
    if ref.is_help_center:
        if ref.locale not in (None, query_locale):
            return None
        return help_center_match_key(ref.host, query_locale, ref.doctype, ref.slug)
    return generic_match_key(ref.host, ref.doctype, ref.slug) or ref.exact_identity


def build_candidate_key_set(
    issue: IssueRecord, refs: list[ParsedUrl], query_locale: str, source_key: str
) -> set[str]:
    keys: set[str] = set()
    for ref in refs:
        if not path_allowed_for_source(ref, source_key):
            continue
        key = ref_key_for_query_locale(issue, ref, query_locale)
        if key:
            keys.add(key)
    return keys


def ref_any_locale_key(ref: ParsedUrl) -> str | None:
    if ref.is_help_center:
        return ref.exact_identity if ref.locale else None
    return generic_match_key(ref.host, ref.doctype, ref.slug) or ref.exact_identity


def result_any_locale_key(ref: ParsedUrl) -> str | None:
    if ref.is_help_center:
        return ref.exact_identity if ref.locale else None
    return generic_match_key(ref.host, ref.doctype, ref.slug) or ref.exact_identity


def build_any_locale_candidate_key_set(refs: list[ParsedUrl], source_key: str) -> set[str]:
    keys: set[str] = set()
    for ref in refs:
        if not path_allowed_for_source(ref, source_key):
            continue
        key = ref_any_locale_key(ref)
        if key:
            keys.add(key)
    return keys


def build_help_center_slug_identities(refs: list[ParsedUrl], source_key: str) -> set[tuple[str, str, str]]:
    identities: set[tuple[str, str, str]] = set()
    for ref in refs:
        if not ref.is_help_center or not ref.doctype or not ref.slug:
            continue
        if not path_allowed_for_source(ref, source_key):
            continue
        identities.add((ref.host, ref.doctype, ref.slug))
    return identities


def resolve_help_center_cross_locale_key(
    ref: ParsedUrl,
    refs: list[ParsedUrl],
    source_key: str,
) -> str | None:
    if not ref.is_help_center or not ref.doctype or not ref.slug:
        return None
    identity = (ref.host, ref.doctype, ref.slug)
    fallback_key: str | None = None
    for candidate in refs:
        if not candidate.is_help_center or not candidate.doctype or not candidate.slug:
            continue
        if (candidate.host, candidate.doctype, candidate.slug) != identity:
            continue
        if not path_allowed_for_source(candidate, source_key):
            continue
        candidate_key = ref_any_locale_key(candidate)
        if candidate_key is not None:
            return candidate_key
        # Catalog URL has no locale segment (e.g. /docs/tutorials/foo), so
        # ref_any_locale_key returns None. Keep its locale-less identity as a
        # fallback so a slug-matched cross-locale result still increments the
        # metric instead of being silently dropped. Prefer an explicit-locale
        # variant of the same doc if one exists later in the list.
        if fallback_key is None:
            fallback_key = candidate.exact_identity
    return fallback_key


def parse_issue_metadata_table(content: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    pattern = re.compile(r"^\|\s*\*\*(.+?)\*\*\s*\|\s*(.*?)\s*\|$", re.MULTILINE)
    for match in pattern.finditer(content):
        key = match.group(1).strip()
        value = match.group(2).strip()
        if key in {"target_docs", "expected_docs", "other_helpful_docs"}:
            try:
                parsed_value = json.loads(value.strip("` "))
            except json.JSONDecodeError:
                parsed_value = []
            normalized_key = "target_docs" if key == "expected_docs" else key
            metadata[normalized_key] = parsed_value
        else:
            metadata[key] = value
    return metadata


def load_issue_catalog(issues_dir: Path) -> dict[str, IssueRecord]:
    issue_catalog: dict[str, IssueRecord] = {}

    for issue_path in sorted(issues_dir.glob("*.md")):
        content = issue_path.read_text(encoding="utf-8")
        metadata = parse_issue_metadata_table(content)
        issue_id = str(metadata.get("issue_id", "")).strip()
        if not issue_id:
            continue

        expected_docs = dedupe_preserve_order(list(metadata.get("target_docs", metadata.get("expected_docs", []))))
        helpful_docs = dedupe_preserve_order(list(metadata.get("other_helpful_docs", [])))
        expected_refs = [parse_url(url) for url in expected_docs]
        helpful_refs = [parse_url(url) for url in helpful_docs]

        help_center_explicit_locale_keys = {
            (ref.host, ref.locale, ref.doctype or "", ref.slug or "")
            for ref in (expected_refs + helpful_refs)
            if ref.is_help_center and ref.locale
        }

        issue_catalog[issue_id] = IssueRecord(
            issue_id=issue_id,
            persona=str(metadata.get("persona", "")).strip(),
            product=str(metadata.get("product", "")).strip(),
            user_intent=str(metadata.get("user_intent", "")).strip(),
            surface=str(metadata.get("surface", "")).strip(),
            source_file=issue_path.name,
            expected_docs=expected_docs,
            other_helpful_docs=helpful_docs,
            expected_refs=expected_refs,
            helpful_refs=helpful_refs,
            help_center_explicit_locale_keys=help_center_explicit_locale_keys,
        )

    return issue_catalog


def load_query_definitions(query_file: Path) -> list[dict[str, str]]:
    payload = read_json(query_file)
    records: list[dict[str, str]] = []
    for issue in payload.get("issues", []):
        issue_id = str(issue.get("issue_id", "")).strip()
        for query in issue.get("queries", []):
            records.append(
                {
                    "issue_id": issue_id,
                    "locale": str(query.get("locale", "")).strip().lower(),
                    "style": str(query.get("style", "")).strip().lower(),
                    "query": str(query.get("query", "")).strip(),
                }
            )
    return records


def query_lookup_map(records: list[dict[str, str]]) -> dict[tuple[str, str, str], str]:
    lookup: dict[tuple[str, str, str], str] = {}
    for record in records:
        key = (
            record["issue_id"],
            record["style"],
            record["query"],
        )
        lookup[key] = record["locale"]
    return lookup


def build_source_configs(root: Path) -> list[SourceConfig]:
    data_root = root / "data" / "test-suite"
    results_root = root / "results"

    return [
        SourceConfig(
            key="internal-search.algolia-helpcenter",
            path_type="internal-search",
            variant="algolia-helpcenter",
            family="internal-search",
            results_dir=results_root / "internal-search" / "algolia-helpcenter",
            query_file=data_root / "internal-search" / "all_queries.json",
            supported_locales=LOCALES,
        ),
        SourceConfig(
            key="internal-search.algolia-devportal",
            path_type="internal-search",
            variant="algolia-devportal",
            family="internal-search",
            results_dir=results_root / "internal-search" / "algolia-devportal",
            query_file=data_root / "internal-search" / "all_queries.json",
            supported_locales=("en",),
        ),
        SourceConfig(
            key="internal-search.hybrid-search",
            path_type="internal-search",
            variant="hybrid-search",
            family="internal-search",
            results_dir=results_root / "internal-search" / "hybrid-search",
            query_file=data_root / "internal-search" / "all_queries.json",
            supported_locales=LOCALES,
        ),
        SourceConfig(
            key="docs-assistant.api",
            path_type="docs-assistant",
            variant="api",
            family="docs-assistant",
            results_dir=results_root / "docs-assistant" / "api",
            query_file=data_root / "docs-assistant" / "all_queries.json",
            supported_locales=LOCALES,
        ),
        SourceConfig(
            key="external-search.google-search-playwright",
            path_type="external-search",
            variant="google-search-playwright",
            family="external-search",
            results_dir=results_root / "external-search" / "google-search-playwright",
            query_file=data_root / "external-search" / "all_queries.json",
            supported_locales=LOCALES,
        ),
        SourceConfig(
            key="llm.chatgpt",
            path_type="llm",
            variant="chatgpt",
            family="llm",
            results_dir=results_root / "external-llms" / "chatgpt",
            query_file=data_root / "external-llms" / "all_queries.json",
            supported_locales=LOCALES,
        ),
        SourceConfig(
            key="llm.gemini",
            path_type="llm",
            variant="gemini",
            family="llm",
            results_dir=results_root / "external-llms" / "gemini",
            query_file=data_root / "external-llms" / "all_queries.json",
            supported_locales=LOCALES,
        ),
    ]


def expected_query_count(config: SourceConfig, query_records_by_file: dict[Path, list[dict[str, str]]]) -> int:
    if config.query_file is None:
        return 0
    records = query_records_by_file[config.query_file]
    return sum(1 for record in records if record["locale"] in config.supported_locales)


def parse_run_timestamp(run_dir: Path) -> datetime:
    match = re.search(r"(\d{4}-\d{2}-\d{2}) (\d{2}-\d{2})$", run_dir.name)
    if match:
        return datetime.strptime(f"{match.group(1)} {match.group(2)}", "%Y-%m-%d %H-%M").replace(tzinfo=timezone.utc)
    return datetime.fromtimestamp(run_dir.stat().st_mtime, tz=timezone.utc)


def internal_json_artifact(run_dir: Path) -> Path | None:
    candidates = sorted(
        path for path in run_dir.glob("*.json") if not path.name.startswith("analysis-")
    )
    return candidates[0] if candidates else None


def docs_assistant_json_artifact(run_dir: Path) -> Path | None:
    candidates = sorted(path for path in run_dir.glob("docs-assistant-run-*.json"))
    return candidates[0] if candidates else None


def external_search_json_artifact(run_dir: Path) -> Path | None:
    candidate = run_dir / "results.json"
    return candidate if candidate.exists() else None


def llm_markdown_artifacts(run_dir: Path, provider: str) -> list[Path]:
    prefix = provider.capitalize() if provider != "chatgpt" else "Chatgpt"
    return sorted(path for path in run_dir.glob(f"{prefix}-*.md"))


def inspect_internal_search_run(run_dir: Path, expected_queries: int) -> RunCandidate | None:
    artifact = internal_json_artifact(run_dir)
    if artifact is None:
        return None
    payload = read_json(artifact)
    results = payload.get("results", [])
    actual_queries = len(results)
    nonempty_queries = sum(1 for result in results if result.get("top_results"))
    ratio = (nonempty_queries / actual_queries) if actual_queries else 0.0
    return RunCandidate(
        run_dir=run_dir,
        artifact_path=artifact,
        timestamp=parse_run_timestamp(run_dir),
        actual_queries=actual_queries,
        expected_queries=expected_queries,
        nonempty_queries=nonempty_queries,
        nonempty_ratio=ratio,
        is_full=actual_queries >= expected_queries,
        is_healthy=ratio >= RUN_SELECTION_HEALTH_MINIMUMS.get("internal-search", 0.0),
    )


def inspect_docs_assistant_run(run_dir: Path, expected_queries: int) -> RunCandidate | None:
    artifact = docs_assistant_json_artifact(run_dir)
    if artifact is None:
        return None
    payload = read_json(artifact)
    results = payload.get("results", [])
    actual_queries = len(results)
    nonempty_queries = sum(1 for result in results if result.get("links"))
    ratio = (nonempty_queries / actual_queries) if actual_queries else 0.0
    return RunCandidate(
        run_dir=run_dir,
        artifact_path=artifact,
        timestamp=parse_run_timestamp(run_dir),
        actual_queries=actual_queries,
        expected_queries=expected_queries,
        nonempty_queries=nonempty_queries,
        nonempty_ratio=ratio,
        is_full=actual_queries >= expected_queries,
        is_healthy=True,
    )


def inspect_external_search_run(run_dir: Path, expected_queries: int, source_key: str) -> RunCandidate | None:
    artifact = external_search_json_artifact(run_dir)
    if artifact is None:
        return None
    payload = read_json(artifact)
    actual_queries = 0
    nonempty_queries = 0
    for key, session in payload.items():
        if not key.startswith("session_") or not isinstance(session, dict):
            continue
        for issue in session.get("output", []):
            for query in issue.get("queries", []):
                actual_queries += 1
                if query.get("output_urls"):
                    nonempty_queries += 1
    ratio = (nonempty_queries / actual_queries) if actual_queries else 0.0
    return RunCandidate(
        run_dir=run_dir,
        artifact_path=artifact,
        timestamp=parse_run_timestamp(run_dir),
        actual_queries=actual_queries,
        expected_queries=expected_queries,
        nonempty_queries=nonempty_queries,
        nonempty_ratio=ratio,
        is_full=actual_queries >= expected_queries,
        is_healthy=ratio >= RUN_SELECTION_HEALTH_MINIMUMS.get(source_key, 0.0),
    )


def parse_llm_case_metadata(content: str) -> tuple[str | None, str | None, str | None]:
    issue_id = re.search(r"- issue_id:\s*`([^`]+)`", content)
    query_locale = re.search(r"- query_locale:\s*`([^`]+)`", content)
    query_style = re.search(r"- query_style:\s*`([^`]+)`", content)
    return (
        issue_id.group(1).strip() if issue_id else None,
        query_locale.group(1).strip().lower() if query_locale else None,
        query_style.group(1).strip().lower() if query_style else None,
    )


def parse_llm_case_file(path: Path) -> dict[str, Any] | None:
    content = path.read_text(encoding="utf-8")
    issue_id, query_locale, query_style = parse_llm_case_metadata(content)
    if not issue_id or not query_locale or not query_style:
        return None

    prompt_match = re.search(r"## Prompt\s*\n(.*?)\n## Response", content, re.DOTALL)
    prompt = prompt_match.group(1).strip() if prompt_match else ""

    urls_block = re.search(r"## Extracted URLs\s*\n(.*?)(?:\n## |\Z)", content, re.DOTALL)
    urls: list[str] = []
    if urls_block:
        for line in urls_block.group(1).splitlines():
            line = line.strip()
            if line.startswith("- "):
                value = line[2:].strip()
                if value and value != "(none)":
                    urls.append(value)

    return {
        "issue_id": issue_id,
        "locale": query_locale,
        "style": query_style,
        "query": prompt,
        "links": [{"url": url, "rank": index + 1} for index, url in enumerate(urls)],
    }


def inspect_llm_run(run_dir: Path, expected_queries: int, provider: str) -> RunCandidate | None:
    markdown_files = llm_markdown_artifacts(run_dir, provider)
    if not markdown_files:
        return None
    parsed_cases = [parse_llm_case_file(path) for path in markdown_files]
    cases = [case for case in parsed_cases if case is not None]
    actual_queries = len(cases)
    nonempty_queries = sum(1 for case in cases if case["links"])
    ratio = (nonempty_queries / actual_queries) if actual_queries else 0.0
    return RunCandidate(
        run_dir=run_dir,
        artifact_path=run_dir / "run_metadata.json",
        timestamp=parse_run_timestamp(run_dir),
        actual_queries=actual_queries,
        expected_queries=expected_queries,
        nonempty_queries=nonempty_queries,
        nonempty_ratio=ratio,
        is_full=actual_queries >= expected_queries,
        is_healthy=True,
    )


def inspect_run(config: SourceConfig, run_dir: Path, expected_queries: int) -> RunCandidate | None:
    if config.family == "internal-search":
        return inspect_internal_search_run(run_dir, expected_queries)
    if config.family == "docs-assistant":
        return inspect_docs_assistant_run(run_dir, expected_queries)
    if config.family == "external-search":
        return inspect_external_search_run(run_dir, expected_queries, config.key)
    if config.key == "llm.chatgpt":
        return inspect_llm_run(run_dir, expected_queries, "chatgpt")
    if config.key == "llm.gemini":
        return inspect_llm_run(run_dir, expected_queries, "gemini")
    return None


def choose_default_run(config: SourceConfig, expected_queries: int) -> RunCandidate:
    if not config.results_dir.exists():
        raise FileNotFoundError(f"Results directory not found for {config.key}: {config.results_dir}")

    candidates: list[RunCandidate] = []
    for run_dir in sorted(path for path in config.results_dir.iterdir() if path.is_dir()):
        candidate = inspect_run(config, run_dir, expected_queries)
        if candidate is not None:
            candidates.append(candidate)

    if not candidates:
        raise FileNotFoundError(f"No runnable results found for {config.key} under {config.results_dir}")

    full_candidates = [candidate for candidate in candidates if candidate.is_full]
    if not full_candidates:
        raise RuntimeError(f"No structurally full runs found for {config.key}")

    healthy_full_candidates = [candidate for candidate in full_candidates if candidate.is_healthy]
    selection_pool = healthy_full_candidates or full_candidates
    selection_pool.sort(key=lambda candidate: candidate.timestamp, reverse=True)
    return selection_pool[0]


def parse_source_run_overrides(values: list[str]) -> dict[str, Path]:
    overrides: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid --source-run value '{value}'. Expected SOURCE_KEY=PATH.")
        key, raw_path = value.split("=", 1)
        overrides[key.strip()] = Path(raw_path.strip())
    return overrides


def load_selected_runs(
    configs: list[SourceConfig],
    query_records_by_file: dict[Path, list[dict[str, str]]],
    overrides: dict[str, Path],
) -> dict[str, RunCandidate]:
    selected: dict[str, RunCandidate] = {}
    for config in configs:
        expected_queries = expected_query_count(config, query_records_by_file)
        override_path = overrides.get(config.key)
        if override_path is not None:
            run_dir = override_path if override_path.is_dir() else override_path.parent
            candidate = inspect_run(config, run_dir, expected_queries)
            if candidate is None:
                raise FileNotFoundError(f"Could not inspect override run for {config.key}: {override_path}")
            selected[config.key] = candidate
        else:
            selected[config.key] = choose_default_run(config, expected_queries)
    return selected


def classify_ranked_links(
    links: list[dict[str, Any]],
    query_locale: str,
    expected_keys: set[str],
    expected_any_locale_keys: set[str],
    expected_slug_identities: set[tuple[str, str, str]],
    helpful_keys: set[str],
    helpful_any_locale_keys: set[str],
    helpful_slug_identities: set[tuple[str, str, str]],
    expected_refs: list[ParsedUrl],
    helpful_refs: list[ParsedUrl],
    source_key: str,
    eval_top_k: int | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    classified_results: list[dict[str, Any]] = []
    found_expected_keys: set[str] = set()
    found_expected_translated_keys: set[str] = set()
    found_helpful_keys: set[str] = set()
    found_helpful_translated_keys: set[str] = set()
    expected_rank: int | None = None
    expected_translated_rank: int | None = None
    helpful_rank: int | None = None
    helpful_translated_rank: int | None = None

    for link in links:
        parsed = parse_ranked_link(link)
        match_key = result_key_for_query_locale(parsed, query_locale)
        any_locale_key = result_any_locale_key(parsed)
        link_type = "unrelated"
        matched_strict_key: str | None = None
        matched_any_locale_key: str | None = None

        if match_key and match_key in expected_keys:
            link_type = "target_doc"
            matched_strict_key = match_key
        elif match_key and match_key in helpful_keys:
            link_type = "other_helpful_doc"
            matched_strict_key = match_key
        elif (
            parsed.is_help_center
            and parsed.locale not in (None, query_locale)
            and any_locale_key
            and any_locale_key in expected_any_locale_keys
        ):
            link_type = "target_doc_different_loc"
            matched_any_locale_key = any_locale_key
        elif (
            parsed.is_help_center
            and parsed.locale not in (None, query_locale)
            and parsed.doctype
            and parsed.slug
            and (parsed.host, parsed.doctype, parsed.slug) in expected_slug_identities
        ):
            link_type = "target_doc_different_loc"
            matched_any_locale_key = resolve_help_center_cross_locale_key(
                parsed, expected_refs, source_key
            )
        elif (
            parsed.is_help_center
            and parsed.locale not in (None, query_locale)
            and any_locale_key
            and any_locale_key in helpful_any_locale_keys
        ):
            link_type = "other_helpful_doc_different_loc"
            matched_any_locale_key = any_locale_key
        elif (
            parsed.is_help_center
            and parsed.locale not in (None, query_locale)
            and parsed.doctype
            and parsed.slug
            and (parsed.host, parsed.doctype, parsed.slug) in helpful_slug_identities
        ):
            link_type = "other_helpful_doc_different_loc"
            matched_any_locale_key = resolve_help_center_cross_locale_key(
                parsed, helpful_refs, source_key
            )

        result_row = {
            "url": str(link.get("url", "")).strip(),
            "rank": int(link.get("rank", 0)),
            "link_type": link_type,
        }
        if "link_source" in link and link["link_source"] is not None:
            result_row["link_source"] = link["link_source"]
        classified_results.append(result_row)

        within_eval_window = eval_top_k is None or result_row["rank"] <= eval_top_k
        if not within_eval_window:
            continue

        if link_type == "target_doc" and matched_strict_key:
            found_expected_keys.add(matched_strict_key)
            if expected_rank is None:
                expected_rank = result_row["rank"]
        elif link_type == "target_doc_different_loc" and matched_any_locale_key:
            found_expected_translated_keys.add(matched_any_locale_key)
            if expected_translated_rank is None:
                expected_translated_rank = result_row["rank"]
        elif link_type == "other_helpful_doc" and matched_strict_key:
            found_helpful_keys.add(matched_strict_key)
            if helpful_rank is None:
                helpful_rank = result_row["rank"]
        elif link_type == "other_helpful_doc_different_loc" and matched_any_locale_key:
            found_helpful_translated_keys.add(matched_any_locale_key)
            if helpful_translated_rank is None:
                helpful_translated_rank = result_row["rank"]

    expected_any_locale_rank = expected_rank
    if expected_any_locale_rank is None or (
        expected_translated_rank is not None and expected_translated_rank < expected_any_locale_rank
    ):
        expected_any_locale_rank = expected_translated_rank

    helpful_any_locale_rank = helpful_rank
    if helpful_any_locale_rank is None or (
        helpful_translated_rank is not None and helpful_translated_rank < helpful_any_locale_rank
    ):
        helpful_any_locale_rank = helpful_translated_rank

    metrics = {
        "expected_rank": expected_rank,
        "expected_found": expected_rank is not None,
        "expected_count": len(found_expected_keys),
        "expected_mrr": round(1 / expected_rank, 6) if expected_rank else 0.0,
        "expected_translated_rank": expected_translated_rank,
        "expected_translated_found": expected_translated_rank is not None,
        "expected_translated_count": len(found_expected_translated_keys),
        "expected_any_locale_rank": expected_any_locale_rank,
        "expected_any_locale_found": expected_any_locale_rank is not None,
        "expected_any_locale_count": len(found_expected_keys | found_expected_translated_keys),
        "expected_any_locale_mrr": round(1 / expected_any_locale_rank, 6) if expected_any_locale_rank else 0.0,
        "helpful_rank": helpful_rank,
        "helpful_found": helpful_rank is not None,
        "helpful_count": len(found_helpful_keys),
        "helpful_translated_rank": helpful_translated_rank,
        "helpful_translated_found": helpful_translated_rank is not None,
        "helpful_translated_count": len(found_helpful_translated_keys),
        "helpful_any_locale_rank": helpful_any_locale_rank,
        "helpful_any_locale_found": helpful_any_locale_rank is not None,
        "helpful_any_locale_count": len(found_helpful_keys | found_helpful_translated_keys),
        "any_relevant_found": bool(found_expected_keys or found_helpful_keys),
        "any_relevant_any_locale_found": bool(
            found_expected_keys
            or found_expected_translated_keys
            or found_helpful_keys
            or found_helpful_translated_keys
        ),
    }
    return classified_results, metrics


def evaluate_links(
    issue: IssueRecord,
    source_key: str,
    path_type: str,
    variant: str,
    locale: str,
    style: str,
    query: str,
    links: list[dict[str, Any]],
    eval_top_k: int | None,
    link_source: str | None,
    include_in_global_rollups: bool,
    include_in_failure_list: bool,
) -> QueryEvaluation:
    expected_keys = build_candidate_key_set(issue, issue.expected_refs, locale, source_key)
    expected_any_locale_keys = build_any_locale_candidate_key_set(issue.expected_refs, source_key)
    expected_slug_identities = build_help_center_slug_identities(issue.expected_refs, source_key)
    helpful_keys = build_candidate_key_set(issue, issue.helpful_refs, locale, source_key)
    helpful_any_locale_keys = build_any_locale_candidate_key_set(issue.helpful_refs, source_key)
    helpful_slug_identities = build_help_center_slug_identities(issue.helpful_refs, source_key)
    coverage_status = "tested" if expected_keys else "not_available"
    classified_results, metrics = classify_ranked_links(
        links,
        locale,
        expected_keys,
        expected_any_locale_keys,
        expected_slug_identities,
        helpful_keys,
        helpful_any_locale_keys,
        helpful_slug_identities,
        issue.expected_refs,
        issue.helpful_refs,
        source_key,
        eval_top_k,
    )

    return QueryEvaluation(
        issue_id=issue.issue_id,
        source_key=source_key,
        path_type=path_type,
        variant=variant,
        locale=locale,
        style=style,
        query=query,
        link_source=link_source,
        coverage_status=coverage_status,
        expected_rank=metrics["expected_rank"],
        expected_found=metrics["expected_found"],
        expected_count=metrics["expected_count"],
        expected_mrr=metrics["expected_mrr"],
        expected_translated_rank=metrics["expected_translated_rank"],
        expected_translated_found=metrics["expected_translated_found"],
        expected_translated_count=metrics["expected_translated_count"],
        expected_any_locale_rank=metrics["expected_any_locale_rank"],
        expected_any_locale_found=metrics["expected_any_locale_found"],
        expected_any_locale_count=metrics["expected_any_locale_count"],
        expected_any_locale_mrr=metrics["expected_any_locale_mrr"],
        helpful_rank=metrics["helpful_rank"],
        helpful_found=metrics["helpful_found"],
        helpful_count=metrics["helpful_count"],
        helpful_translated_rank=metrics["helpful_translated_rank"],
        helpful_translated_found=metrics["helpful_translated_found"],
        helpful_translated_count=metrics["helpful_translated_count"],
        helpful_any_locale_rank=metrics["helpful_any_locale_rank"],
        helpful_any_locale_found=metrics["helpful_any_locale_found"],
        helpful_any_locale_count=metrics["helpful_any_locale_count"],
        any_relevant_found=metrics["any_relevant_found"],
        any_relevant_any_locale_found=metrics["any_relevant_any_locale_found"],
        classified_results=classified_results,
        include_in_global_rollups=include_in_global_rollups,
        include_in_path_rollups=True,
        include_in_failure_list=include_in_failure_list,
    )


def derive_developers_doctype_from_metadata(parsed: ParsedUrl, metadata: dict[str, Any]) -> str | None:
    file_path = str(metadata.get("file_path", "")).strip().lower()
    if file_path:
        parts = [segment for segment in file_path.split("/") if segment]
        if len(parts) >= 2 and parts[0] == "docs":
            if parts[1] == "release-notes":
                return "updates/release-notes"
            return normalize_doc_type(parts[1])
    return parsed.doctype


def derive_developers_slug_from_metadata(parsed: ParsedUrl, metadata: dict[str, Any]) -> str | None:
    frontmatter = metadata.get("frontmatter")
    if isinstance(frontmatter, dict):
        slug = str(frontmatter.get("slug", "")).strip().lower()
        if slug:
            return slug

    file_path = str(metadata.get("file_path", "")).strip().lower()
    if file_path:
        filename = file_path.split("/")[-1]
        if "." in filename:
            filename = filename.rsplit(".", 1)[0]
        if filename:
            return filename

    return parsed.slug


def parse_ranked_link(link: dict[str, Any]) -> ParsedUrl:
    url = str(link.get("url", "")).strip()
    parsed = parse_url(url)
    metadata = link.get("metadata")
    if not isinstance(metadata, dict):
        return parsed

    if parsed.host != DEVELOPERS_HOST:
        return parsed

    doctype = derive_developers_doctype_from_metadata(parsed, metadata)
    slug = derive_developers_slug_from_metadata(parsed, metadata)
    if not doctype or not slug:
        return parsed

    return ParsedUrl(
        raw_url=url,
        host=parsed.host,
        is_help_center=False,
        locale=None,
        doctype=doctype,
        slug=slug,
        exact_identity=parsed.exact_identity,
    )


def load_internal_search_results(config: SourceConfig, run: RunCandidate) -> list[dict[str, Any]]:
    payload = read_json(run.artifact_path) if run.artifact_path else {}
    entries: list[dict[str, Any]] = []
    for result in payload.get("results", []):
        top_results = []
        for index, item in enumerate(result.get("top_results", [])):
            if not item.get("url"):
                continue
            link = {
                "url": item.get("url", ""),
                "rank": int(item.get("rank", index + 1)),
            }
            if isinstance(item.get("metadata"), dict):
                link["metadata"] = item["metadata"]
            top_results.append(link)
        entries.append(
            {
                "issue_id": str(result.get("issue_id", "")).strip(),
                "query": str(result.get("query", "")).strip(),
                "locale": str(result.get("query_locale", "")).strip().lower(),
                "style": str(result.get("query_style", "")).strip().lower(),
                "links": top_results,
            }
        )
    return entries


def load_docs_assistant_results(
    config: SourceConfig,
    run: RunCandidate,
    locale_lookup: dict[tuple[str, str, str], str],
) -> list[dict[str, Any]]:
    payload = read_json(run.artifact_path) if run.artifact_path else {}
    entries: list[dict[str, Any]] = []
    for result in payload.get("results", []):
        issue_id = str(result.get("issue_id", "")).strip()
        query = str(result.get("query", "")).strip()
        style = str(result.get("query_style", "")).strip().lower()
        locale = str(result.get("locale", "")).strip().lower()
        if not locale or locale == "none":
            locale = locale_lookup.get((issue_id, style, query), locale)
        links = [
            {
                "url": item.get("url", ""),
                "rank": int(item.get("position", index + 1)),
                "link_source": item.get("context"),
            }
            for index, item in enumerate(result.get("links", []))
            if item.get("url")
        ]
        entries.append(
            {
                "issue_id": issue_id,
                "query": query,
                "locale": locale,
                "style": style,
                "links": sorted(links, key=lambda link: link["rank"]),
            }
        )
    return entries


def load_external_search_results(
    config: SourceConfig,
    run: RunCandidate,
    locale_lookup: dict[tuple[str, str, str], str],
) -> list[dict[str, Any]]:
    payload = read_json(run.artifact_path) if run.artifact_path else {}
    entries: list[dict[str, Any]] = []
    for key, session in payload.items():
        if not key.startswith("session_") or not isinstance(session, dict):
            continue
        for issue in session.get("output", []):
            issue_id = str(issue.get("issue_id", "")).strip()
            for query in issue.get("queries", []):
                query_text = str(query.get("query", "")).strip()
                style = str(query.get("style", "")).strip().lower()
                locale = locale_lookup.get((issue_id, style, query_text))
                if not locale:
                    raise KeyError(
                        f"Could not recover locale for external-search query: "
                        f"{issue_id} / {style} / {query_text}"
                    )
                links = [
                    {
                        "url": item.get("url_address", ""),
                        "rank": index + 1,
                    }
                    for index, item in enumerate(query.get("output_urls", []))
                    if item.get("url_address")
                ]
                entries.append(
                    {
                        "issue_id": issue_id,
                        "query": query_text,
                        "locale": locale,
                        "style": style,
                        "links": links,
                    }
                )
    return entries


def load_llm_results(config: SourceConfig, run: RunCandidate) -> list[dict[str, Any]]:
    provider = config.variant
    markdown_files = llm_markdown_artifacts(run.run_dir, provider)
    entries: list[dict[str, Any]] = []
    for path in markdown_files:
        parsed = parse_llm_case_file(path)
        if parsed is not None:
            entries.append(parsed)
    return entries


def analyze_source(
    config: SourceConfig,
    run: RunCandidate,
    issue_catalog: dict[str, IssueRecord],
    external_search_locale_lookup: dict[tuple[str, str, str], str],
) -> list[QueryEvaluation]:
    evaluations: list[QueryEvaluation] = []

    if config.family == "internal-search":
        raw_results = load_internal_search_results(config, run)
        for entry in raw_results:
            issue = issue_catalog.get(entry["issue_id"])
            if issue is None:
                continue
            evaluations.append(
                evaluate_links(
                    issue=issue,
                    source_key=config.key,
                    path_type=config.path_type,
                    variant=config.variant,
                    locale=entry["locale"],
                    style=entry["style"],
                    query=entry["query"],
                    links=entry["links"],
                    eval_top_k=INTERNAL_SEARCH_TOP_K,
                    link_source=None,
                    include_in_global_rollups=True,
                    include_in_failure_list=True,
                )
            )
        return evaluations

    if config.family == "docs-assistant":
        docs_assistant_locale_lookup = query_lookup_map(
            load_query_definitions(config.query_file) if config.query_file else []
        )
        raw_results = load_docs_assistant_results(config, run, docs_assistant_locale_lookup)
        for entry in raw_results:
            issue = issue_catalog.get(entry["issue_id"])
            if issue is None:
                continue

            combined_links = sorted(entry["links"], key=lambda link: link["rank"])
            evaluations.append(
                evaluate_links(
                    issue=issue,
                    source_key=config.key,
                    path_type=config.path_type,
                    variant=config.variant,
                    locale=entry["locale"],
                    style=entry["style"],
                    query=entry["query"],
                    links=combined_links,
                    eval_top_k=None,
                    link_source=None,
                    include_in_global_rollups=True,
                    include_in_failure_list=False,
                )
            )

            for link_source in DOCS_ASSISTANT_LINK_SOURCES:
                source_links = [link for link in combined_links if link.get("link_source") == link_source]
                source_links = [
                    {
                        "url": link["url"],
                        "rank": index + 1,
                        "link_source": link_source,
                    }
                    for index, link in enumerate(source_links)
                ]
                evaluations.append(
                    evaluate_links(
                        issue=issue,
                        source_key=config.key,
                        path_type=config.path_type,
                        variant=config.variant,
                        locale=entry["locale"],
                        style=entry["style"],
                        query=entry["query"],
                        links=source_links,
                        eval_top_k=None,
                        link_source=link_source,
                        include_in_global_rollups=False,
                        include_in_failure_list=True,
                    )
                )
        return evaluations

    if config.family == "external-search":
        raw_results = load_external_search_results(config, run, external_search_locale_lookup)
        for entry in raw_results:
            issue = issue_catalog.get(entry["issue_id"])
            if issue is None:
                continue
            evaluations.append(
                evaluate_links(
                    issue=issue,
                    source_key=config.key,
                    path_type=config.path_type,
                    variant=config.variant,
                    locale=entry["locale"],
                    style=entry["style"],
                    query=entry["query"],
                    links=entry["links"],
                    eval_top_k=None,
                    link_source=None,
                    include_in_global_rollups=True,
                    include_in_failure_list=True,
                )
            )
        return evaluations

    if config.family == "llm":
        raw_results = load_llm_results(config, run)
        for entry in raw_results:
            issue = issue_catalog.get(entry["issue_id"])
            if issue is None:
                continue
            evaluations.append(
                evaluate_links(
                    issue=issue,
                    source_key=config.key,
                    path_type=config.path_type,
                    variant=config.variant,
                    locale=entry["locale"],
                    style=entry["style"],
                    query=entry["query"],
                    links=entry["links"],
                    eval_top_k=None,
                    link_source=None,
                    include_in_global_rollups=True,
                    include_in_failure_list=True,
                )
            )
        return evaluations

    return evaluations


def mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 6) if values else 0.0


def mean_or_none(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 6) if values else None


QualityScoreIndex = dict[tuple[str, str, str, str], float]


def compute_quality_scores(
    selected_runs: dict[str, "RunCandidate"],
    issues_dir: Path,
    scorer: str,
) -> QualityScoreIndex:
    """Score text-answer responses using the ``tools/quality-scoring`` pipeline.

    Returns a lookup keyed by ``(source_key, issue_id, locale, style)`` mapping to
    the 1-4 quality score. The stage is import-light (it reuses the existing
    extractor + scorer) and fails soft: any error logs a warning and yields an
    empty index so the analysis proceeds with ``mean_quality`` left as ``None``.
    """
    scores: QualityScoreIndex = {}

    quality_dir = workspace_root() / "tools" / "quality-scoring"
    try:
        if str(quality_dir) not in sys.path:
            sys.path.insert(0, str(quality_dir))
        import extract_responses_for_scoring as qs_extract
        import simple_score as qs_score
    except Exception as exc:  # pragma: no cover - defensive import guard
        print(f"Warning: quality scoring unavailable ({exc}); skipping.", file=sys.stderr)
        return scores

    if scorer != "simple":
        print(
            f"Warning: quality scorer '{scorer}' is not wired for unattended runs; "
            "falling back to the 'simple' heuristic scorer.",
            file=sys.stderr,
        )

    for source_key in QUALITY_TEXT_ANSWER_SOURCE_KEYS:
        run = selected_runs.get(source_key)
        if run is None:
            continue
        try:
            if source_key == "docs-assistant.api":
                responses = qs_extract.extract_docs_assistant_responses(run.run_dir, issues_dir)
            else:
                responses = qs_extract.extract_llm_responses(run.run_dir, issues_dir)
            scored = qs_score.generate_ai_scores(responses)
            for response, score in zip(responses, scored):
                issue_id = str(response.get("issue_id", "")).strip()
                locale = str(response.get("locale", "en")).strip().lower()
                style = str(response.get("style", "")).strip().lower()
                if not issue_id:
                    continue
                scores[(source_key, issue_id, locale, style)] = float(score["ai_score"])
        except Exception as exc:
            print(
                f"Warning: quality scoring failed for {source_key} ({exc}); "
                "leaving its mean_quality as None.",
                file=sys.stderr,
            )
    return scores


def mean_quality_for(
    records: list["QueryEvaluation"],
    quality_scores: QualityScoreIndex | None,
) -> float | None:
    """Mean 1-4 quality score across records that have a scored text answer.

    Records without a matching score (e.g. link-only paths, or docs-assistant
    ``link_source`` breakouts) are ignored. Returns ``None`` when scoring is off
    or no record in the group was scored."""
    if not quality_scores:
        return None
    values = [
        quality_scores[(record.source_key, record.issue_id, record.locale, record.style)]
        for record in records
        if record.link_source is None
        and (record.source_key, record.issue_id, record.locale, record.style) in quality_scores
    ]
    return mean(values) if values else None


def aggregate_record_group(
    records: list[QueryEvaluation],
    quality_scores: QualityScoreIndex | None = None,
) -> dict[str, Any]:
    tested = [record for record in records if record.coverage_status == "tested"]
    successful_expected_ranks = [float(record.expected_rank) for record in tested if record.expected_rank is not None]
    successful_expected_any_locale_ranks = [
        float(record.expected_any_locale_rank) for record in tested if record.expected_any_locale_rank is not None
    ]

    aggregate = {
        "n_queries": len(records),
        "n_tested_queries": len(tested),
        "n_not_available": len(records) - len(tested),
        "target_mean_mrr": mean([record.expected_mrr for record in tested]),
        "target_mean_rank": mean_or_none(successful_expected_ranks),
        "target_pass_rate": mean([1.0 if record.expected_found else 0.0 for record in tested]),
        "target_any_locale_mean_mrr": mean([record.expected_any_locale_mrr for record in tested]),
        "target_any_locale_mean_rank": mean_or_none(successful_expected_any_locale_ranks),
        "target_any_locale_pass_rate": mean([1.0 if record.expected_any_locale_found else 0.0 for record in tested]),
        "helpful_pass_rate": mean([1.0 if record.any_relevant_any_locale_found else 0.0 for record in tested]),
        "helpful_found_rate": mean([1.0 if record.helpful_found else 0.0 for record in tested]),
        "helpful_any_locale_found_rate": mean([1.0 if record.helpful_any_locale_found else 0.0 for record in tested]),
        "any_relevant_rate": mean([1.0 if record.any_relevant_found else 0.0 for record in tested]),
        "any_relevant_any_locale_rate": mean(
            [1.0 if record.any_relevant_any_locale_found else 0.0 for record in tested]
        ),
        "mean_quality": mean_quality_for(records, quality_scores),
    }
    if not tested:
        aggregate["coverage_status"] = "not_available"
    return aggregate


def aggregate_issue_path_locale(
    records: list[QueryEvaluation],
    quality_scores: QualityScoreIndex | None = None,
) -> dict[str, Any]:
    aggregate = aggregate_record_group(records, quality_scores)
    payload = {
        "target_mrr": aggregate["target_mean_mrr"],
        "target_mean_rank": aggregate["target_mean_rank"],
        "target_pass_rate": aggregate["target_pass_rate"],
        "target_any_locale_mrr": aggregate["target_any_locale_mean_mrr"],
        "target_any_locale_mean_rank": aggregate["target_any_locale_mean_rank"],
        "target_any_locale_pass_rate": aggregate["target_any_locale_pass_rate"],
        "helpful_pass_rate": aggregate["helpful_pass_rate"],
        "helpful_found_rate": aggregate["helpful_found_rate"],
        "helpful_any_locale_found_rate": aggregate["helpful_any_locale_found_rate"],
        "any_relevant_rate": aggregate["any_relevant_rate"],
        "any_relevant_any_locale_rate": aggregate["any_relevant_any_locale_rate"],
        "n_styles": len(records),
        "n_tested_styles": aggregate["n_tested_queries"],
        "n_not_available_styles": aggregate["n_not_available"],
        **({"coverage_status": "not_available"} if aggregate.get("coverage_status") == "not_available" else {}),
    }
    # Only surface the field when scoring is on, so default runs stay byte-identical.
    if quality_scores:
        payload["mean_quality"] = aggregate["mean_quality"]
    return payload


def metric_payload(record: QueryEvaluation) -> dict[str, Any]:
    return {
        "query": record.query,
        "coverage_status": record.coverage_status,
        "target_rank": record.expected_rank,
        "target_found": record.expected_found,
        "target_count": record.expected_count,
        "target_mrr": record.expected_mrr,
        "target_different_loc_rank": record.expected_translated_rank,
        "target_different_loc_found": record.expected_translated_found,
        "target_different_loc_count": record.expected_translated_count,
        "target_any_locale_rank": record.expected_any_locale_rank,
        "target_any_locale_found": record.expected_any_locale_found,
        "target_any_locale_count": record.expected_any_locale_count,
        "target_any_locale_mrr": record.expected_any_locale_mrr,
        "helpful_rank": record.helpful_rank,
        "helpful_found": record.helpful_found,
        "helpful_count": record.helpful_count,
        "helpful_translated_rank": record.helpful_translated_rank,
        "helpful_translated_found": record.helpful_translated_found,
        "helpful_translated_count": record.helpful_translated_count,
        "helpful_any_locale_rank": record.helpful_any_locale_rank,
        "helpful_any_locale_found": record.helpful_any_locale_found,
        "helpful_any_locale_count": record.helpful_any_locale_count,
        "any_relevant_found": record.any_relevant_found,
        "any_relevant_any_locale_found": record.any_relevant_any_locale_found,
        "classified_results": record.classified_results,
    }


def build_issue_outputs(
    issues: dict[str, IssueRecord],
    evaluations: list[QueryEvaluation],
    source_configs: list[SourceConfig],
    quality_scores: QualityScoreIndex | None = None,
) -> list[dict[str, Any]]:
    by_issue: dict[str, list[QueryEvaluation]] = defaultdict(list)
    for evaluation in evaluations:
        by_issue[evaluation.issue_id].append(evaluation)

    config_by_key = {config.key: config for config in source_configs}
    output: list[dict[str, Any]] = []

    for issue_id in sorted(issues):
        issue = issues[issue_id]
        issue_evals = by_issue.get(issue_id, [])

        path_payload: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for source_key in sorted({evaluation.source_key for evaluation in issue_evals}):
            config = config_by_key[source_key]
            source_evals = [evaluation for evaluation in issue_evals if evaluation.source_key == source_key]

            if source_key == "docs-assistant.api":
                locale_map: dict[str, dict[str, Any]] = {}
                for locale in sorted({evaluation.locale for evaluation in source_evals}):
                    style_map: dict[str, Any] = {}
                    for style in STYLES:
                        combined = next(
                            (
                                evaluation
                                for evaluation in source_evals
                                if evaluation.locale == locale
                                and evaluation.style == style
                                and evaluation.link_source is None
                            ),
                            None,
                        )
                        if combined is None:
                            continue
                        source_payload = {
                            link_source: metric_payload(evaluation)
                            for link_source in DOCS_ASSISTANT_LINK_SOURCES
                            for evaluation in source_evals
                            if evaluation.locale == locale
                            and evaluation.style == style
                            and evaluation.link_source == link_source
                        }
                        style_map[style] = {
                            "query": combined.query,
                            "coverage_status": combined.coverage_status,
                            "combined_ranked_list": metric_payload(combined),
                            "link_sources": source_payload,
                        }
                    if style_map:
                        locale_map[locale] = style_map
                if locale_map:
                    path_payload[config.path_type].append({config.variant: locale_map})
                continue

            locale_map = {}
            for locale in sorted({evaluation.locale for evaluation in source_evals}):
                style_map = {}
                for style in STYLES:
                    record = next(
                        (
                            evaluation
                            for evaluation in source_evals
                            if evaluation.locale == locale
                            and evaluation.style == style
                            and evaluation.link_source is None
                        ),
                        None,
                    )
                    if record is not None:
                        style_map[style] = metric_payload(record)
                if style_map:
                    locale_map[locale] = style_map
            if locale_map:
                path_payload[config.path_type].append({config.variant: locale_map})

        combined_issue_aggregates: dict[str, Any] = {}
        per_locale_aggregates: dict[str, Any] = {}

        non_source_evals = [evaluation for evaluation in issue_evals if evaluation.include_in_global_rollups]
        for source_key in sorted({evaluation.source_key for evaluation in non_source_evals}):
            grouped_by_locale: dict[str, list[QueryEvaluation]] = defaultdict(list)
            for evaluation in non_source_evals:
                if evaluation.source_key == source_key:
                    grouped_by_locale[evaluation.locale].append(evaluation)
            for locale, records in sorted(grouped_by_locale.items()):
                aggregate = aggregate_issue_path_locale(records, quality_scores)
                key = f"{source_key}.{locale}"
                if source_key == "docs-assistant.api":
                    source_specific = {
                        link_source: aggregate_issue_path_locale(
                            [
                                evaluation
                                for evaluation in issue_evals
                                if evaluation.source_key == source_key
                                and evaluation.locale == locale
                                and evaluation.link_source == link_source
                            ],
                            quality_scores,
                        )
                        for link_source in DOCS_ASSISTANT_LINK_SOURCES
                    }
                    aggregate["link_sources"] = source_specific
                combined_issue_aggregates[key] = aggregate

        grouped_issue_locales: dict[str, list[QueryEvaluation]] = defaultdict(list)
        for evaluation in non_source_evals:
            grouped_issue_locales[evaluation.locale].append(evaluation)
        for locale, records in sorted(grouped_issue_locales.items()):
            per_locale_aggregates[locale] = aggregate_issue_path_locale(records, quality_scores)

        output.append(
            {
                "issue_id": issue.issue_id,
                "persona": issue.persona,
                "product": issue.product,
                "user_intent": issue.user_intent,
                "target_docs": issue.expected_docs,
                "other_helpful_docs": issue.other_helpful_docs,
                "per_path_style": dict(path_payload),
                "aggregates": {
                    "by_path_locale": combined_issue_aggregates,
                    "by_locale": per_locale_aggregates,
                },
            }
        )

    return output


def build_aggregates_by_path_locale(
    evaluations: list[QueryEvaluation],
    quality_scores: QualityScoreIndex | None = None,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str | None], list[QueryEvaluation]] = defaultdict(list)
    for evaluation in evaluations:
        if evaluation.include_in_path_rollups:
            grouped[(evaluation.source_key, evaluation.locale, evaluation.link_source)].append(evaluation)

    rows: list[dict[str, Any]] = []
    for (source_key, locale, link_source), records in sorted(
        grouped.items(),
        key=lambda item: (item[0][0], item[0][1], item[0][2] or ""),
    ):
        aggregate = aggregate_record_group(records, quality_scores)
        row = {
            "path": source_key,
            "locale": locale,
            "n_issues": len({record.issue_id for record in records}),
            "n_queries": aggregate["n_queries"],
            "n_tested_queries": aggregate["n_tested_queries"],
            "target_mean_mrr": aggregate["target_mean_mrr"],
            "target_mean_rank": aggregate["target_mean_rank"],
            "target_pass_rate": aggregate["target_pass_rate"],
            "target_any_locale_mean_mrr": aggregate["target_any_locale_mean_mrr"],
            "target_any_locale_mean_rank": aggregate["target_any_locale_mean_rank"],
            "target_any_locale_pass_rate": aggregate["target_any_locale_pass_rate"],
            "helpful_pass_rate": aggregate["helpful_pass_rate"],
            "helpful_found_rate": aggregate["helpful_found_rate"],
            "helpful_any_locale_found_rate": aggregate["helpful_any_locale_found_rate"],
            "any_relevant_rate": aggregate["any_relevant_rate"],
            "any_relevant_any_locale_rate": aggregate["any_relevant_any_locale_rate"],
            "mean_quality": aggregate["mean_quality"],
            "n_not_available": aggregate["n_not_available"],
        }
        if link_source is not None:
            row["link_source"] = link_source
        rows.append(row)
    return rows


def build_aggregates_by_locale(evaluations: list[QueryEvaluation]) -> list[dict[str, Any]]:
    grouped: dict[str, list[QueryEvaluation]] = defaultdict(list)
    for evaluation in evaluations:
        if evaluation.include_in_global_rollups:
            grouped[evaluation.locale].append(evaluation)

    rows: list[dict[str, Any]] = []
    for locale, records in sorted(grouped.items()):
        aggregate = aggregate_record_group(records)
        rows.append(
            {
                "locale": locale,
                "n_queries": aggregate["n_queries"],
                "n_tested_queries": aggregate["n_tested_queries"],
                "target_mean_mrr": aggregate["target_mean_mrr"],
                "target_pass_rate": aggregate["target_pass_rate"],
                "target_mean_rank": aggregate["target_mean_rank"],
                "target_any_locale_mean_mrr": aggregate["target_any_locale_mean_mrr"],
                "target_any_locale_pass_rate": aggregate["target_any_locale_pass_rate"],
                "target_any_locale_mean_rank": aggregate["target_any_locale_mean_rank"],
                "helpful_pass_rate": aggregate["helpful_pass_rate"],
                "helpful_found_rate": aggregate["helpful_found_rate"],
                "helpful_any_locale_found_rate": aggregate["helpful_any_locale_found_rate"],
                "any_relevant_rate": aggregate["any_relevant_rate"],
                "any_relevant_any_locale_rate": aggregate["any_relevant_any_locale_rate"],
                "n_not_available": aggregate["n_not_available"],
            }
        )
    return rows


def build_aggregates_by_style(evaluations: list[QueryEvaluation]) -> list[dict[str, Any]]:
    grouped: dict[str, list[QueryEvaluation]] = defaultdict(list)
    for evaluation in evaluations:
        if evaluation.include_in_global_rollups:
            grouped[evaluation.style].append(evaluation)

    rows: list[dict[str, Any]] = []
    for style, records in sorted(grouped.items()):
        aggregate = aggregate_record_group(records)
        rows.append(
            {
                "style": style,
                "n_queries": aggregate["n_queries"],
                "n_tested_queries": aggregate["n_tested_queries"],
                "target_mean_mrr": aggregate["target_mean_mrr"],
                "target_pass_rate": aggregate["target_pass_rate"],
                "target_mean_rank": aggregate["target_mean_rank"],
                "target_any_locale_mean_mrr": aggregate["target_any_locale_mean_mrr"],
                "target_any_locale_pass_rate": aggregate["target_any_locale_pass_rate"],
                "target_any_locale_mean_rank": aggregate["target_any_locale_mean_rank"],
                "helpful_pass_rate": aggregate["helpful_pass_rate"],
                "helpful_found_rate": aggregate["helpful_found_rate"],
                "helpful_any_locale_found_rate": aggregate["helpful_any_locale_found_rate"],
                "any_relevant_rate": aggregate["any_relevant_rate"],
                "any_relevant_any_locale_rate": aggregate["any_relevant_any_locale_rate"],
                "n_not_available": aggregate["n_not_available"],
            }
        )
    return rows


def build_aggregates_by_persona(
    evaluations: list[QueryEvaluation],
    issues: dict[str, IssueRecord],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[QueryEvaluation]] = defaultdict(list)
    for evaluation in evaluations:
        if evaluation.include_in_global_rollups:
            persona = issues[evaluation.issue_id].persona
            grouped[persona].append(evaluation)

    rows: list[dict[str, Any]] = []
    for persona, records in sorted(grouped.items()):
        aggregate = aggregate_record_group(records)
        rows.append(
            {
                "persona": persona,
                "n_queries": aggregate["n_queries"],
                "n_tested_queries": aggregate["n_tested_queries"],
                "target_mean_mrr": aggregate["target_mean_mrr"],
                "target_pass_rate": aggregate["target_pass_rate"],
                "target_mean_rank": aggregate["target_mean_rank"],
                "target_any_locale_mean_mrr": aggregate["target_any_locale_mean_mrr"],
                "target_any_locale_pass_rate": aggregate["target_any_locale_pass_rate"],
                "target_any_locale_mean_rank": aggregate["target_any_locale_mean_rank"],
                "helpful_pass_rate": aggregate["helpful_pass_rate"],
                "helpful_found_rate": aggregate["helpful_found_rate"],
                "helpful_any_locale_found_rate": aggregate["helpful_any_locale_found_rate"],
                "any_relevant_rate": aggregate["any_relevant_rate"],
                "any_relevant_any_locale_rate": aggregate["any_relevant_any_locale_rate"],
                "n_not_available": aggregate["n_not_available"],
            }
        )
    return rows


def build_aggregates_by_style_locale(evaluations: list[QueryEvaluation]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[QueryEvaluation]] = defaultdict(list)
    for evaluation in evaluations:
        if evaluation.include_in_global_rollups:
            grouped[(evaluation.style, evaluation.locale)].append(evaluation)

    rows: list[dict[str, Any]] = []
    for (style, locale), records in sorted(grouped.items()):
        aggregate = aggregate_record_group(records)
        rows.append(
            {
                "style": style,
                "locale": locale,
                "n_queries": aggregate["n_queries"],
                "n_tested_queries": aggregate["n_tested_queries"],
                "target_mean_mrr": aggregate["target_mean_mrr"],
                "target_pass_rate": aggregate["target_pass_rate"],
                "target_mean_rank": aggregate["target_mean_rank"],
                "target_any_locale_mean_mrr": aggregate["target_any_locale_mean_mrr"],
                "target_any_locale_pass_rate": aggregate["target_any_locale_pass_rate"],
                "target_any_locale_mean_rank": aggregate["target_any_locale_mean_rank"],
                "helpful_pass_rate": aggregate["helpful_pass_rate"],
                "helpful_found_rate": aggregate["helpful_found_rate"],
                "helpful_any_locale_found_rate": aggregate["helpful_any_locale_found_rate"],
                "any_relevant_rate": aggregate["any_relevant_rate"],
                "any_relevant_any_locale_rate": aggregate["any_relevant_any_locale_rate"],
                "n_not_available": aggregate["n_not_available"],
            }
        )
    return rows


def build_aggregates_by_persona_locale(
    evaluations: list[QueryEvaluation],
    issues: dict[str, IssueRecord],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[QueryEvaluation]] = defaultdict(list)
    for evaluation in evaluations:
        if evaluation.include_in_global_rollups:
            persona = issues[evaluation.issue_id].persona
            grouped[(persona, evaluation.locale)].append(evaluation)

    rows: list[dict[str, Any]] = []
    for (persona, locale), records in sorted(grouped.items()):
        aggregate = aggregate_record_group(records)
        rows.append(
            {
                "persona": persona,
                "locale": locale,
                "n_queries": aggregate["n_queries"],
                "n_tested_queries": aggregate["n_tested_queries"],
                "target_mean_mrr": aggregate["target_mean_mrr"],
                "target_pass_rate": aggregate["target_pass_rate"],
                "target_mean_rank": aggregate["target_mean_rank"],
                "target_any_locale_mean_mrr": aggregate["target_any_locale_mean_mrr"],
                "target_any_locale_pass_rate": aggregate["target_any_locale_pass_rate"],
                "target_any_locale_mean_rank": aggregate["target_any_locale_mean_rank"],
                "helpful_pass_rate": aggregate["helpful_pass_rate"],
                "helpful_found_rate": aggregate["helpful_found_rate"],
                "helpful_any_locale_found_rate": aggregate["helpful_any_locale_found_rate"],
                "any_relevant_rate": aggregate["any_relevant_rate"],
                "any_relevant_any_locale_rate": aggregate["any_relevant_any_locale_rate"],
                "n_not_available": aggregate["n_not_available"],
            }
        )
    return rows


def build_failure_list(evaluations: list[QueryEvaluation]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for evaluation in evaluations:
        if not evaluation.include_in_failure_list:
            continue
        if evaluation.coverage_status != "tested":
            continue
        if evaluation.expected_found:
            continue

        path_identifier = f"{evaluation.source_key}.{evaluation.locale}"
        if evaluation.link_source is not None:
            path_identifier += f".{evaluation.link_source}"

        row = {
            "issue_id": evaluation.issue_id,
            "path": evaluation.source_key,
            "path_identifier": path_identifier,
            "locale": evaluation.locale,
            "style": evaluation.style,
            "query": evaluation.query,
            "target_different_loc_found": evaluation.expected_translated_found,
            "target_any_locale_found": evaluation.expected_any_locale_found,
            "helpful_found": evaluation.helpful_found,
            "helpful_translated_found": evaluation.helpful_translated_found,
            "helpful_any_locale_found": evaluation.helpful_any_locale_found,
        }
        if evaluation.link_source is not None:
            row["link_source"] = evaluation.link_source
        failures.append(row)

    failures.sort(key=lambda row: (row["path_identifier"], row["issue_id"], row["style"]))
    return failures


def build_overall_summary(evaluations: list[QueryEvaluation], issues: dict[str, IssueRecord]) -> dict[str, Any]:
    global_records = [evaluation for evaluation in evaluations if evaluation.include_in_global_rollups]
    aggregate = aggregate_record_group(global_records)
    return {
        "total_issues": len(issues),
        "total_queries": aggregate["n_queries"],
        "overall_target_pass_rate": aggregate["target_pass_rate"],
        "overall_target_mrr": aggregate["target_mean_mrr"],
        "overall_target_any_locale_mrr": aggregate["target_any_locale_mean_mrr"],
        "overall_target_any_locale_pass_rate": aggregate["target_any_locale_pass_rate"],
        "overall_helpful_pass_rate": aggregate["helpful_pass_rate"],
        "overall_helpful_found_rate": aggregate["helpful_found_rate"],
        "overall_helpful_any_locale_found_rate": aggregate["helpful_any_locale_found_rate"],
        "overall_any_relevant_rate": aggregate["any_relevant_rate"],
        "overall_any_relevant_any_locale_rate": aggregate["any_relevant_any_locale_rate"],
        "locales_included": sorted({evaluation.locale for evaluation in global_records}),
        "n_not_available": aggregate["n_not_available"],
    }


def relative_to_workspace(path: Path) -> str:
    root = workspace_root()
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path.resolve())


def create_analysis_run_dir(output_root: Path, timestamp: datetime) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    base_name = f"analysis-system {timestamp:%Y-%m-%d %H-%M}"
    run_dir = output_root / base_name
    counter = 1
    while run_dir.exists():
        run_dir = output_root / f"{base_name} ({counter})"
        counter += 1
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def build_run_summary(
    analysis_id: str,
    run_dir: Path,
    selected_runs: dict[str, RunCandidate],
    evaluations: list[QueryEvaluation],
    issues: dict[str, IssueRecord],
    aggregates_by_path_locale: list[dict[str, Any]],
    quality_scored: list[str] | None = None,
) -> dict[str, Any]:
    overall = build_overall_summary(evaluations, issues)
    paths_included = []
    for row in aggregates_by_path_locale:
        identifier = f"{row['path']}.{row['locale']}"
        if row.get("link_source"):
            identifier += f".{row['link_source']}"
        paths_included.append(identifier)

    selected_runs_payload = {}
    for source_key, run in selected_runs.items():
        selected_runs_payload[source_key] = {
            "run_dir": relative_to_workspace(run.run_dir),
            "artifact_path": relative_to_workspace(run.artifact_path) if run.artifact_path else None,
            "timestamp": run.timestamp.isoformat(),
            "actual_queries": run.actual_queries,
            "expected_queries": run.expected_queries,
            "nonempty_queries": run.nonempty_queries,
            "nonempty_ratio": round(run.nonempty_ratio, 6),
            "is_full": run.is_full,
            "is_healthy": run.is_healthy,
        }

    return {
        "analysis_id": analysis_id,
        "run_id": run_dir.name,
        "timestamp": utc_now().isoformat(),
        "success_thresholds": {
            "internal-search": {"top_k": INTERNAL_SEARCH_TOP_K},
            "docs-assistant": {"top_k": ALL_LINKS_TOP_K},
            "external-search": {"top_k": ALL_LINKS_TOP_K},
            "llm": {"top_k": ALL_LINKS_TOP_K},
        },
        "paths_included": sorted(paths_included),
        "locales_included": overall["locales_included"],
        "n_issues": len(issues),
        "n_queries_total": overall["total_queries"],
        "quality_scored": sorted(quality_scored) if quality_scored else [],
        "selected_runs": selected_runs_payload,
        **overall,
    }


def run_analysis(args: argparse.Namespace) -> None:
    root = workspace_root()
    issue_catalog = load_issue_catalog(root / "docs" / "test-suite" / "issues")
    source_configs = build_source_configs(root)

    query_records_by_file = {
        config.query_file: load_query_definitions(config.query_file)
        for config in source_configs
        if config.query_file is not None
    }
    external_search_lookup = query_lookup_map(
        query_records_by_file[root / "data" / "test-suite" / "external-search" / "all_queries.json"]
    )

    overrides = parse_source_run_overrides(args.source_run or [])
    selected_runs = load_selected_runs(source_configs, query_records_by_file, overrides)

    all_evaluations: list[QueryEvaluation] = []
    for config in source_configs:
        evaluations = analyze_source(config, selected_runs[config.key], issue_catalog, external_search_lookup)
        all_evaluations.extend(evaluations)

    timestamp = utc_now()
    analysis_id = args.analysis_id or f"analysis-{timestamp:%Y%m%d-%H%M%S}"
    output_root = Path(args.output_root) if args.output_root else (root / "results" / "analysis-system")
    run_dir = create_analysis_run_dir(output_root, timestamp)

    # Optional, default-off quality-scoring stage (Task 2). When disabled, quality_scores
    # is None so mean_quality stays None and quality_scored stays [] (unchanged behavior).
    quality_scores: QualityScoreIndex | None = None
    quality_scored: list[str] = []
    if getattr(args, "score_quality", False):
        quality_scores = compute_quality_scores(
            selected_runs,
            root / "docs" / "test-suite" / "issues",
            getattr(args, "quality_scorer", "simple"),
        )
        quality_scored = sorted({source_key for (source_key, *_rest) in quality_scores})
        print(
            f"Quality scoring enabled ({getattr(args, 'quality_scorer', 'simple')}): "
            f"scored paths -> {', '.join(quality_scored) if quality_scored else 'none'}"
        )

    issues_processed = build_issue_outputs(issue_catalog, all_evaluations, source_configs, quality_scores)
    aggregates_by_path_locale = build_aggregates_by_path_locale(all_evaluations, quality_scores)
    aggregates_by_locale = build_aggregates_by_locale(all_evaluations)
    aggregates_by_style = build_aggregates_by_style(all_evaluations)
    aggregates_by_persona = build_aggregates_by_persona(all_evaluations, issue_catalog)
    aggregates_by_style_locale = build_aggregates_by_style_locale(all_evaluations)
    aggregates_by_persona_locale = build_aggregates_by_persona_locale(all_evaluations, issue_catalog)
    failure_list = build_failure_list(all_evaluations)
    run_summary = build_run_summary(
        analysis_id=analysis_id,
        run_dir=run_dir,
        selected_runs=selected_runs,
        evaluations=all_evaluations,
        issues=issue_catalog,
        aggregates_by_path_locale=aggregates_by_path_locale,
        quality_scored=quality_scored,
    )

    write_json(run_dir / ARTIFACT_FILENAMES["issues_processed"], issues_processed)
    write_json(run_dir / ARTIFACT_FILENAMES["aggregates_by_path_locale"], aggregates_by_path_locale)
    write_json(run_dir / ARTIFACT_FILENAMES["aggregates_by_locale"], aggregates_by_locale)
    write_json(run_dir / ARTIFACT_FILENAMES["aggregates_by_style"], aggregates_by_style)
    write_json(run_dir / ARTIFACT_FILENAMES["aggregates_by_persona"], aggregates_by_persona)
    write_json(run_dir / ARTIFACT_FILENAMES["aggregates_by_style_locale"], aggregates_by_style_locale)
    write_json(run_dir / ARTIFACT_FILENAMES["aggregates_by_persona_locale"], aggregates_by_persona_locale)
    write_json(run_dir / ARTIFACT_FILENAMES["failure_list"], failure_list)
    write_json(run_dir / ARTIFACT_FILENAMES["run_summary"], run_summary)

    print(f"Analysis run written to: {run_dir}")
    for source_key, run in selected_runs.items():
        print(f"  {source_key}: {relative_to_workspace(run.run_dir)}")

    maybe_render_dashboard(run_dir, dashboard_mode="analysis", args=args)


def maybe_render_dashboard(
    run_dir: Path,
    *,
    dashboard_mode: str,
    args: argparse.Namespace,
) -> None:
    if getattr(args, "no_render_dashboard", False):
        return
    if not getattr(args, "render_dashboard", False):
        return

    script = Path(__file__).resolve().parent / "render_analysis_dashboard.py"
    cmd = [sys.executable, str(script)]
    if dashboard_mode == "analysis":
        cmd.extend(["--analysis-run", str(run_dir)])
    elif dashboard_mode == "comparison":
        cmd.extend(["--comparison-run", str(run_dir)])
    elif dashboard_mode == "multi_comparison":
        cmd.extend(["--multi-comparison-run", str(run_dir)])
    else:
        raise ValueError(f"Unknown dashboard mode: {dashboard_mode}")

    if getattr(args, "render_dashboard_report", False):
        cmd.extend(["--report", "markdown"])

    print(f"Rendering dashboard ({dashboard_mode})...")
    result = subprocess.run(cmd, cwd=workspace_root())
    if result.returncode != 0:
        print("Warning: dashboard render failed (analysis artifacts were still written).", file=sys.stderr)


def load_analysis_dir(path: Path) -> dict[str, Any]:
    if not path.is_dir():
        raise FileNotFoundError(f"Analysis directory not found: {path}")

    def _normalize_summary(summary: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(summary)
        if "overall_target_mrr" not in normalized:
            normalized["overall_target_mrr"] = normalized.get("overall_expected_mrr")
        if "overall_target_any_locale_mrr" not in normalized:
            normalized["overall_target_any_locale_mrr"] = normalized.get("overall_expected_any_locale_mrr")
        if "overall_target_any_locale_pass_rate" not in normalized:
            normalized["overall_target_any_locale_pass_rate"] = normalized.get("overall_expected_any_locale_pass_rate")
        if "overall_target_pass_rate" not in normalized:
            normalized["overall_target_pass_rate"] = normalized.get("overall_expected_pass_rate")
        if "overall_helpful_pass_rate" not in normalized:
            normalized["overall_helpful_pass_rate"] = normalized.get("overall_any_relevant_any_locale_rate")
        if "overall_any_relevant_any_locale_rate" not in normalized:
            normalized["overall_any_relevant_any_locale_rate"] = normalized.get("overall_helpful_pass_rate")
        return normalized

    def _normalize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized_rows: list[dict[str, Any]] = []
        for row in rows:
            normalized = dict(row)
            if "target_mean_mrr" not in normalized:
                normalized["target_mean_mrr"] = normalized.get("expected_mean_mrr")
            if "target_mean_rank" not in normalized:
                normalized["target_mean_rank"] = normalized.get("expected_mean_rank")
            if "target_pass_rate" not in normalized:
                normalized["target_pass_rate"] = normalized.get("expected_pass_rate")
            if "target_any_locale_mean_mrr" not in normalized:
                normalized["target_any_locale_mean_mrr"] = normalized.get("expected_any_locale_mean_mrr")
            if "target_any_locale_mean_rank" not in normalized:
                normalized["target_any_locale_mean_rank"] = normalized.get("expected_any_locale_mean_rank")
            if "target_any_locale_pass_rate" not in normalized:
                normalized["target_any_locale_pass_rate"] = normalized.get("expected_any_locale_pass_rate")
            normalized_rows.append(normalized)
        return normalized_rows

    return {
        "run_summary": _normalize_summary(read_json(path / ARTIFACT_FILENAMES["run_summary"])),
        "aggregates_by_path_locale": _normalize_rows(read_json(path / ARTIFACT_FILENAMES["aggregates_by_path_locale"])),
        "aggregates_by_locale": _normalize_rows(read_json(path / ARTIFACT_FILENAMES["aggregates_by_locale"])),
        "aggregates_by_style": _normalize_rows(read_json(path / ARTIFACT_FILENAMES["aggregates_by_style"])),
        "aggregates_by_persona": _normalize_rows(_read_optional_json_list(path / ARTIFACT_FILENAMES["aggregates_by_persona"])),
        "aggregates_by_style_locale": _normalize_rows(_read_optional_json_list(path / ARTIFACT_FILENAMES["aggregates_by_style_locale"])),
        "aggregates_by_persona_locale": _normalize_rows(_read_optional_json_list(path / ARTIFACT_FILENAMES["aggregates_by_persona_locale"])),
        "issues_processed": _read_optional_json_list(path / ARTIFACT_FILENAMES["issues_processed"]),
        "failure_list": _read_optional_json_list(path / ARTIFACT_FILENAMES["failure_list"]),
    }


def _read_optional_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = read_json(path)
    return payload if isinstance(payload, list) else []


def index_rows(rows: list[dict[str, Any]], keys: list[str]) -> dict[tuple[Any, ...], dict[str, Any]]:
    index: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        index[tuple(row.get(key) for key in keys)] = row
    return index


def compare_metric_rows(
    baseline_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    keys: list[str],
    metric_fields: list[str],
) -> list[dict[str, Any]]:
    baseline_index = index_rows(baseline_rows, keys)
    candidate_index = index_rows(candidate_rows, keys)
    all_keys = sorted(
        set(baseline_index) | set(candidate_index),
        key=lambda key_values: tuple("" if value is None else str(value) for value in key_values),
    )
    rows: list[dict[str, Any]] = []

    for key_values in all_keys:
        baseline_row = baseline_index.get(key_values)
        candidate_row = candidate_index.get(key_values)
        row = {key: value for key, value in zip(keys, key_values)}
        row["baseline_present"] = baseline_row is not None
        row["candidate_present"] = candidate_row is not None

        for field in metric_fields:
            baseline_value = baseline_row.get(field) if baseline_row else None
            candidate_value = candidate_row.get(field) if candidate_row else None
            row[f"baseline_{field}"] = baseline_value
            row[f"candidate_{field}"] = candidate_value
            if isinstance(baseline_value, (int, float)) and isinstance(candidate_value, (int, float)):
                row[f"delta_{field}"] = round(candidate_value - baseline_value, 6)
            else:
                row[f"delta_{field}"] = None

        rows.append(row)

    return rows


def _issue_pass_rate(issue: dict[str, Any], field: str) -> float | None:
    tested = 0
    weighted = 0.0
    for path_identifier, aggregate in issue.get("aggregates", {}).get("by_path_locale", {}).items():
        if path_identifier.endswith(".markdown") or path_identifier.endswith(".suggested_sources"):
            continue
        n = int(aggregate.get("n_tested_styles", 0))
        if n <= 0:
            continue
        rate = aggregate.get(field)
        if rate is None and field == "target_pass_rate":
            rate = aggregate.get("expected_pass_rate")
        if rate is None and field == "helpful_pass_rate":
            rate = aggregate.get("any_relevant_any_locale_rate")
        if rate is None:
            continue
        tested += n
        weighted += float(rate) * n
    if tested == 0:
        return None
    return round(weighted / tested, 6)


def compute_issue_level_rows(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for issue in issues:
        rows.append(
            {
                "issue_id": issue.get("issue_id"),
                "persona": issue.get("persona"),
                "product": issue.get("product"),
                "target_pass_rate": _issue_pass_rate(issue, "target_pass_rate"),
                "helpful_pass_rate": _issue_pass_rate(issue, "helpful_pass_rate"),
            }
        )
    return rows


def failure_entry_key(row: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        str(row.get("path") or ""),
        str(row.get("locale") or ""),
        str(row.get("style") or ""),
        str(row.get("issue_id") or ""),
        str(row.get("link_source") or ""),
    )


def compute_failure_delta(
    baseline_failures: list[dict[str, Any]],
    candidate_failures: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    baseline_index = {failure_entry_key(row): row for row in baseline_failures}
    candidate_index = {failure_entry_key(row): row for row in candidate_failures}
    baseline_keys = set(baseline_index)
    candidate_keys = set(candidate_index)

    def summarize_row(row: dict[str, Any]) -> dict[str, Any]:
        query = str(row.get("query") or "")
        return {
            "path": row.get("path"),
            "locale": row.get("locale"),
            "style": row.get("style"),
            "issue_id": row.get("issue_id"),
            "query": query if len(query) <= 120 else query[:117] + "...",
            "link_source": row.get("link_source") or "-",
        }

    new_failures = [summarize_row(candidate_index[key]) for key in sorted(candidate_keys - baseline_keys)]
    resolved_failures = [summarize_row(baseline_index[key]) for key in sorted(baseline_keys - candidate_keys)]
    still_failing = [summarize_row(candidate_index[key]) for key in sorted(baseline_keys & candidate_keys)]
    return {
        "new_failures": new_failures,
        "resolved_failures": resolved_failures,
        "still_failing": still_failing,
    }


def enrich_issue_comparison_rows(
    rows: list[dict[str, Any]],
    baseline_issues: list[dict[str, Any]],
    candidate_issues: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    metadata: dict[str, dict[str, Any]] = {}
    for issue in baseline_issues + candidate_issues:
        issue_id = issue.get("issue_id")
        if issue_id:
            metadata[issue_id] = issue
    enriched: list[dict[str, Any]] = []
    for row in rows:
        merged = dict(row)
        meta = metadata.get(row.get("issue_id"), {})
        merged["persona"] = meta.get("persona")
        merged["product"] = meta.get("product")
        enriched.append(merged)
    return enriched


COMPARISON_METRIC_FIELDS = [
    "target_pass_rate",
    "target_mean_mrr",
    "target_mean_rank",
    "target_any_locale_mean_mrr",
    "target_any_locale_mean_rank",
    "target_any_locale_pass_rate",
    "helpful_pass_rate",
    "helpful_found_rate",
    "helpful_any_locale_found_rate",
    "any_relevant_rate",
    "any_relevant_any_locale_rate",
    "n_queries",
    "n_tested_queries",
    "n_not_available",
]


def compute_pairwise_comparison(
    baseline_data: dict[str, Any],
    candidate_data: dict[str, Any],
    baseline_dir: Path,
    candidate_dir: Path,
) -> dict[str, Any]:
    by_path_locale = compare_metric_rows(
        baseline_data["aggregates_by_path_locale"],
        candidate_data["aggregates_by_path_locale"],
        ["path", "locale", "link_source"],
        COMPARISON_METRIC_FIELDS,
    )
    by_locale = compare_metric_rows(
        baseline_data["aggregates_by_locale"],
        candidate_data["aggregates_by_locale"],
        ["locale"],
        COMPARISON_METRIC_FIELDS,
    )
    by_style = compare_metric_rows(
        baseline_data["aggregates_by_style"],
        candidate_data["aggregates_by_style"],
        ["style"],
        COMPARISON_METRIC_FIELDS,
    )
    by_persona = compare_metric_rows(
        baseline_data.get("aggregates_by_persona") or [],
        candidate_data.get("aggregates_by_persona") or [],
        ["persona"],
        COMPARISON_METRIC_FIELDS,
    )
    by_style_locale = compare_metric_rows(
        baseline_data.get("aggregates_by_style_locale") or [],
        candidate_data.get("aggregates_by_style_locale") or [],
        ["style", "locale"],
        COMPARISON_METRIC_FIELDS,
    )
    by_persona_locale = compare_metric_rows(
        baseline_data.get("aggregates_by_persona_locale") or [],
        candidate_data.get("aggregates_by_persona_locale") or [],
        ["persona", "locale"],
        COMPARISON_METRIC_FIELDS,
    )

    baseline_issue_rows = compute_issue_level_rows(baseline_data.get("issues_processed") or [])
    candidate_issue_rows = compute_issue_level_rows(candidate_data.get("issues_processed") or [])
    by_issue = enrich_issue_comparison_rows(
        compare_metric_rows(
            baseline_issue_rows,
            candidate_issue_rows,
            ["issue_id"],
            ["target_pass_rate", "helpful_pass_rate"],
        ),
        baseline_issue_rows,
        candidate_issue_rows,
    )
    failure_delta = compute_failure_delta(
        baseline_data.get("failure_list") or [],
        candidate_data.get("failure_list") or [],
    )

    b_sum = baseline_data["run_summary"]
    c_sum = candidate_data["run_summary"]

    def _safe_delta(field: str) -> float | int:
        b_val = b_sum.get(field, 0) or 0
        c_val = c_sum.get(field, 0) or 0
        result = c_val - b_val
        return round(result, 6) if isinstance(result, float) else result

    summary = {
        "baseline_analysis_id": b_sum.get("analysis_id"),
        "candidate_analysis_id": c_sum.get("analysis_id"),
        "baseline_run_dir": relative_to_workspace(baseline_dir),
        "candidate_run_dir": relative_to_workspace(candidate_dir),
        "timestamp": utc_now().isoformat(),
        "baseline_total_queries": b_sum.get("total_queries"),
        "candidate_total_queries": c_sum.get("total_queries"),
        "delta_total_queries": _safe_delta("total_queries"),
        "baseline_overall_target_pass_rate": b_sum.get("overall_target_pass_rate"),
        "candidate_overall_target_pass_rate": c_sum.get("overall_target_pass_rate"),
        "delta_overall_target_pass_rate": _safe_delta("overall_target_pass_rate"),
        "baseline_overall_target_mrr": b_sum.get("overall_target_mrr"),
        "candidate_overall_target_mrr": c_sum.get("overall_target_mrr"),
        "delta_overall_target_mrr": _safe_delta("overall_target_mrr"),
        "baseline_overall_target_any_locale_mrr": b_sum.get("overall_target_any_locale_mrr"),
        "candidate_overall_target_any_locale_mrr": c_sum.get("overall_target_any_locale_mrr"),
        "delta_overall_target_any_locale_mrr": _safe_delta("overall_target_any_locale_mrr"),
        "baseline_overall_target_any_locale_pass_rate": b_sum.get("overall_target_any_locale_pass_rate"),
        "candidate_overall_target_any_locale_pass_rate": c_sum.get("overall_target_any_locale_pass_rate"),
        "delta_overall_target_any_locale_pass_rate": _safe_delta("overall_target_any_locale_pass_rate"),
        "baseline_overall_helpful_pass_rate": b_sum.get("overall_helpful_pass_rate"),
        "candidate_overall_helpful_pass_rate": c_sum.get("overall_helpful_pass_rate"),
        "delta_overall_helpful_pass_rate": _safe_delta("overall_helpful_pass_rate"),
        "baseline_overall_helpful_found_rate": b_sum.get("overall_helpful_found_rate"),
        "candidate_overall_helpful_found_rate": c_sum.get("overall_helpful_found_rate"),
        "delta_overall_helpful_found_rate": _safe_delta("overall_helpful_found_rate"),
        "baseline_overall_helpful_any_locale_found_rate": b_sum.get("overall_helpful_any_locale_found_rate"),
        "candidate_overall_helpful_any_locale_found_rate": c_sum.get("overall_helpful_any_locale_found_rate"),
        "delta_overall_helpful_any_locale_found_rate": _safe_delta("overall_helpful_any_locale_found_rate"),
        "baseline_overall_any_relevant_rate": b_sum.get("overall_any_relevant_rate"),
        "candidate_overall_any_relevant_rate": c_sum.get("overall_any_relevant_rate"),
        "delta_overall_any_relevant_rate": _safe_delta("overall_any_relevant_rate"),
        "baseline_overall_any_relevant_any_locale_rate": b_sum.get("overall_any_relevant_any_locale_rate"),
        "candidate_overall_any_relevant_any_locale_rate": c_sum.get("overall_any_relevant_any_locale_rate"),
        "delta_overall_any_relevant_any_locale_rate": _safe_delta("overall_any_relevant_any_locale_rate"),
    }

    return {
        "summary": summary,
        "by_path_locale": by_path_locale,
        "by_locale": by_locale,
        "by_style": by_style,
        "by_persona": by_persona,
        "by_style_locale": by_style_locale,
        "by_persona_locale": by_persona_locale,
        "by_issue": by_issue,
        "failure_delta": failure_delta,
    }


def _run_snapshot(run_dir: Path, run_data: dict[str, Any]) -> dict[str, Any]:
    s = run_data["run_summary"]
    return {
        "run_dir": relative_to_workspace(run_dir),
        "analysis_id": s.get("analysis_id"),
        "timestamp": s.get("timestamp"),
        "total_queries": s.get("total_queries"),
        "overall_target_pass_rate": s.get("overall_target_pass_rate"),
        "overall_target_mrr": s.get("overall_target_mrr"),
        "overall_target_any_locale_pass_rate": s.get("overall_target_any_locale_pass_rate"),
        "overall_target_any_locale_mrr": s.get("overall_target_any_locale_mrr"),
        "overall_helpful_pass_rate": s.get("overall_helpful_pass_rate"),
        "overall_helpful_found_rate": s.get("overall_helpful_found_rate"),
        "overall_helpful_any_locale_found_rate": s.get("overall_helpful_any_locale_found_rate"),
        "overall_any_relevant_rate": s.get("overall_any_relevant_rate"),
        "overall_any_relevant_any_locale_rate": s.get("overall_any_relevant_any_locale_rate"),
    }
def run_compare(args: argparse.Namespace) -> None:
    baseline_dir = Path(args.baseline)
    candidate_dir = Path(args.candidate)
    baseline = load_analysis_dir(baseline_dir)
    candidate = load_analysis_dir(candidate_dir)

    timestamp = utc_now()
    output_root = Path(args.output_root) if args.output_root else (workspace_root() / "results" / "analysis-system-comparisons")
    comparison_dir = create_analysis_run_dir(output_root, timestamp)

    comparison = compute_pairwise_comparison(baseline, candidate, baseline_dir, candidate_dir)

    write_json(comparison_dir / ARTIFACT_FILENAMES["comparison_summary"], comparison["summary"])
    write_json(comparison_dir / ARTIFACT_FILENAMES["comparison_by_path_locale"], comparison["by_path_locale"])
    write_json(comparison_dir / ARTIFACT_FILENAMES["comparison_by_locale"], comparison["by_locale"])
    write_json(comparison_dir / ARTIFACT_FILENAMES["comparison_by_style"], comparison["by_style"])
    write_json(comparison_dir / ARTIFACT_FILENAMES["comparison_by_persona"], comparison["by_persona"])
    write_json(comparison_dir / ARTIFACT_FILENAMES["comparison_by_style_locale"], comparison["by_style_locale"])
    write_json(comparison_dir / ARTIFACT_FILENAMES["comparison_by_persona_locale"], comparison["by_persona_locale"])
    write_json(comparison_dir / ARTIFACT_FILENAMES["comparison_by_issue"], comparison["by_issue"])
    write_json(comparison_dir / ARTIFACT_FILENAMES["failure_delta"], comparison["failure_delta"])

    print(f"Comparison written to: {comparison_dir}")
    maybe_render_dashboard(comparison_dir, dashboard_mode="comparison", args=args)


def run_compare_chain(args: argparse.Namespace) -> None:
    run_dirs = [Path(p) for p in args.runs]
    if len(run_dirs) < 2:
        raise ValueError("compare-chain requires at least 2 run directories.")

    run_data_list = [(d, load_analysis_dir(d)) for d in run_dirs]

    comparisons: list[dict[str, Any]] = []
    for i in range(len(run_data_list) - 1):
        b_dir, b_data = run_data_list[i]
        c_dir, c_data = run_data_list[i + 1]
        pair = compute_pairwise_comparison(b_data, c_data, b_dir, c_dir)
        comparisons.append(pair)

    output_root = Path(args.output_root) if args.output_root else (workspace_root() / "results" / "analysis-system-comparisons")
    comparison_dir = create_analysis_run_dir(output_root, utc_now())

    consolidated = {
        "mode": "chain",
        "timestamp": utc_now().isoformat(),
        "n_comparisons": len(comparisons),
        "runs": [_run_snapshot(d, data) for d, data in run_data_list],
        "comparisons": comparisons,
    }
    write_json(comparison_dir / "multi_comparison.json", consolidated)
    print(f"Chain comparison ({len(comparisons)} pairs) written to: {comparison_dir}")
    maybe_render_dashboard(comparison_dir, dashboard_mode="multi_comparison", args=args)


def run_compare_all(args: argparse.Namespace) -> None:
    baseline_dir = Path(args.baseline)
    candidate_dirs = [Path(p) for p in args.candidates]
    if not candidate_dirs:
        raise ValueError("compare-all requires at least 1 candidate directory.")

    baseline_data = load_analysis_dir(baseline_dir)
    candidates = [(d, load_analysis_dir(d)) for d in candidate_dirs]

    comparisons: list[dict[str, Any]] = []
    for c_dir, c_data in candidates:
        pair = compute_pairwise_comparison(baseline_data, c_data, baseline_dir, c_dir)
        comparisons.append(pair)

    output_root = Path(args.output_root) if args.output_root else (workspace_root() / "results" / "analysis-system-comparisons")
    comparison_dir = create_analysis_run_dir(output_root, utc_now())

    all_run_data = [(baseline_dir, baseline_data)] + candidates
    consolidated = {
        "mode": "fan",
        "timestamp": utc_now().isoformat(),
        "n_comparisons": len(comparisons),
        "baseline": _run_snapshot(baseline_dir, baseline_data),
        "runs": [_run_snapshot(d, data) for d, data in all_run_data],
        "comparisons": comparisons,
    }
    write_json(comparison_dir / "multi_comparison.json", consolidated)
    print(f"Fan comparison ({len(comparisons)} pairs vs baseline) written to: {comparison_dir}")
    maybe_render_dashboard(comparison_dir, dashboard_mode="multi_comparison", args=args)


def add_dashboard_render_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--render-dashboard",
        action="store_true",
        help="Render a static HTML dashboard after this command completes.",
    )
    parser.add_argument(
        "--no-render-dashboard",
        action="store_true",
        help="Skip dashboard rendering (for CI/automation).",
    )
    parser.add_argument(
        "--render-dashboard-report",
        action="store_true",
        help="Also write dashboard/summary.md when rendering the dashboard.",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 1 analysis system for the VTEX docs test suite.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Analyze the latest full comparable runs (or explicit overrides).")
    run_parser.add_argument(
        "--analysis-id",
        help="Optional stable identifier stored in run_summary.json.",
    )
    run_parser.add_argument(
        "--output-root",
        help="Directory where processed analysis runs will be created. Default: results/analysis-system",
    )
    run_parser.add_argument(
        "--source-run",
        action="append",
        default=[],
        help="Override a selected raw run: SOURCE_KEY=PATH_TO_RUN_DIR",
    )
    run_parser.add_argument(
        "--score-quality",
        action="store_true",
        default=False,
        help=(
            "Opt into the answer-quality scoring stage for text-answer paths "
            "(docs-assistant, ChatGPT, Gemini). Default off; when off, mean_quality "
            "stays null and quality_scored stays []."
        ),
    )
    run_parser.add_argument(
        "--quality-scorer",
        choices=["simple", "llm"],
        default="simple",
        help="Scorer used when --score-quality is set (default: simple heuristic).",
    )
    add_dashboard_render_args(run_parser)

    compare_parser = subparsers.add_parser("compare", help="Compare two previously generated analysis runs.")
    compare_parser.add_argument("--baseline", required=True, help="Path to the baseline analysis run directory.")
    compare_parser.add_argument("--candidate", required=True, help="Path to the candidate analysis run directory.")
    compare_parser.add_argument(
        "--output-root",
        help="Directory where comparison runs will be created. Default: results/analysis-system-comparisons",
    )
    add_dashboard_render_args(compare_parser)

    chain_parser = subparsers.add_parser(
        "compare-chain",
        help="Compare multiple analysis runs as consecutive pairs (run1 vs run2, run2 vs run3, ...).",
    )
    chain_parser.add_argument(
        "--runs", nargs="+", required=True,
        help="Paths to 2 or more analysis run directories, in chronological order.",
    )
    chain_parser.add_argument(
        "--output-root",
        help="Directory where the multi-comparison output will be created. Default: results/analysis-system-comparisons",
    )
    add_dashboard_render_args(chain_parser)

    fan_parser = subparsers.add_parser(
        "compare-all",
        help="Compare multiple candidate runs against a single baseline.",
    )
    fan_parser.add_argument("--baseline", required=True, help="Path to the baseline analysis run directory.")
    fan_parser.add_argument(
        "--candidates", nargs="+", required=True,
        help="Paths to 1 or more candidate analysis run directories.",
    )
    fan_parser.add_argument(
        "--output-root",
        help="Directory where the multi-comparison output will be created. Default: results/analysis-system-comparisons",
    )
    add_dashboard_render_args(fan_parser)

    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.command == "run":
        run_analysis(args)
        return
    if args.command == "compare":
        run_compare(args)
        return
    if args.command == "compare-chain":
        run_compare_chain(args)
        return
    if args.command == "compare-all":
        run_compare_all(args)
        return

    parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise
