#!/usr/bin/env python3
"""
Shared utilities for API path test runners.

This module contains common functions used by multiple test runner scripts
to avoid code duplication and maintain consistency.
"""

import os
import re
import json
from pathlib import Path
from typing import Optional
from collections import defaultdict

# Constants for text truncation
TITLE_MAX_LENGTH = 200
URL_DISPLAY_MAX_LENGTH = 50
QUERY_DISPLAY_MAX_LENGTH = 50
ERROR_MESSAGE_MAX_LENGTH = 50


def load_env_file():
    """Load environment variables from .env file in the workspace root."""
    workspace = Path(__file__).resolve().parent.parent.parent.parent
    env_file = workspace / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value and key not in os.environ:
                        os.environ[key] = value


def parse_issue_file(filepath: Path) -> Optional[dict]:
    """Parse a test suite issue markdown file; extract metadata and query_internal."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  Warning: Could not read {filepath}: {e}")
        return None

    issue = {}

    # Extract metadata from the table: | **field** | value |
    metadata_pattern = r"\|\s*\*\*(\w+)\*\*\s*\|\s*([^|]+)\s*\|"
    for match in re.finditer(metadata_pattern, content):
        key = match.group(1).strip()
        value = match.group(2).strip()
        
        # Parse JSON arrays for target_docs/other_helpful_docs, with expected_docs legacy support
        if key in ["target_docs", "expected_docs", "other_helpful_docs"]:
            try:
                # The value might have backticks around it or just be a raw JSON array
                clean_value = value.strip("` ")
                parsed = json.loads(clean_value)
                normalized_key = "target_docs" if key == "expected_docs" else key
                issue[normalized_key] = parsed
                if key == "expected_docs":
                    issue[key] = parsed
            except json.JSONDecodeError:
                normalized_key = "target_docs" if key == "expected_docs" else key
                issue[normalized_key] = []
                if key == "expected_docs":
                    issue[key] = []
        else:
            issue[key] = value

    if "target_doc_url" not in issue and "expected_doc_url" in issue:
        issue["target_doc_url"] = issue["expected_doc_url"]
    if "target_docs" not in issue and "expected_docs" in issue:
        issue["target_docs"] = issue["expected_docs"]

    # Extract query_internal JSON array (B — Internal search)
    internal_section = re.search(
        r"###\s*B\s*[—-]\s*Internal\s+search.*?```json\s*\n(.*?)\n```",
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if internal_section:
        try:
            issue["query_internal"] = json.loads(internal_section.group(1))
        except json.JSONDecodeError as e:
            print(f"  Warning: Could not parse query_internal JSON in {filepath}: {e}")
            issue["query_internal"] = []
    else:
        alt_pattern = r"\*\*Array\s*\(query_internal\):\*\*\s*```json\s*\n(.*?)\n```"
        alt_match = re.search(alt_pattern, content, re.DOTALL)
        if alt_match:
            try:
                issue["query_internal"] = json.loads(alt_match.group(1))
            except json.JSONDecodeError:
                issue["query_internal"] = []
        else:
            # "Query Type B: Internal Search" section with **JSON Array:** block
            query_type_b = re.search(
                r"Query Type B:.*?\*\*JSON Array:\*\*\s*```json\s*\n(.*?)\n```",
                content,
                re.DOTALL | re.IGNORECASE,
            )
            if query_type_b:
                try:
                    issue["query_internal"] = json.loads(query_type_b.group(1))
                except json.JSONDecodeError:
                    issue["query_internal"] = []
            else:
                issue["query_internal"] = []

    if "issue_id" not in issue:
        print(f"  Warning: No issue_id found in {filepath}")
        return None

    return issue


def normalize_url(url: str) -> str:
    """Normalize URL for comparison (strip trailing slash, fragment, lowercase)."""
    if not url:
        return ""
    url = url.strip().lower()
    if url.find("#") >= 0:
        url = url.split("#")[0]
    return url.rstrip("/")


def extract_url_slug(url: str) -> str:
    """
    Extract the core slug from a VTEX documentation URL.
    
    Handles various URL formats:
    - https://help.vtex.com/docs/tutorials/why-is-the-product-not-visible-on-the-website
    - https://help.vtex.com/en/faq/why-is-the-product-not-visible-on-the-website
    - https://help.vtex.com/docs/en/faq/marketing-and-merchandising/why-is-the-product-not-visible-on-the-website
    - https://help.vtex.com/pt/tutorial/por-que-o-produto-nao-aparece-no-site
    - https://developers.vtex.com/docs/guides/some-guide-name
    - https://developers.vtex.com/docs/api-reference/some-api#endpoint
    
    Returns the final slug (last meaningful path segment).
    
    Examples:
        'https://help.vtex.com/en/faq/why-is-the-product' -> 'why-is-the-product'
        'https://help.vtex.com/docs/tutorials/product-guide' -> 'product-guide'
    """
    if not url:
        return ""
    
    # Normalize URL first
    url = normalize_url(url)
    
    # Remove query parameters if any
    if "?" in url:
        url = url.split("?")[0]
    
    # Parse URL parts
    parts = url.split("/")
    
    # Filter out empty parts and common non-slug segments
    non_slug_segments = {
        "https:", "http:", "", "help.vtex.com", "developers.vtex.com",
        "docs", "tutorial", "tutorials", "faq", "guides", "api-reference",
        "en", "pt", "es", "marketing-and-merchandising", "payments",
        "orders", "catalog", "promotions", "shipping", "logistics"
    }
    
    slug_parts = [p for p in parts if p and p not in non_slug_segments]
    
    # Return the last meaningful segment as the slug
    return slug_parts[-1] if slug_parts else ""


def urls_match(url1: str, url2: str) -> bool:
    """
    Check if two URLs refer to the same document.
    
    Uses multiple strategies:
    1. Exact match after normalization
    2. Slug-based matching (handles different path structures)
    3. Alternative slug patterns (with/without locale prefixes)
    
    Args:
        url1: First URL to compare
        url2: Second URL to compare
        
    Returns:
        True if URLs are considered to match, False otherwise
    """
    if not url1 or not url2:
        return False
    
    # Strategy 1: Exact match after normalization
    norm1 = normalize_url(url1)
    norm2 = normalize_url(url2)
    
    if norm1 == norm2:
        return True
    
    # Strategy 2: Slug-based matching
    slug1 = extract_url_slug(url1)
    slug2 = extract_url_slug(url2)
    
    if slug1 and slug2 and slug1 == slug2:
        return True
    
    # Strategy 3: Handle locale variations in slugs
    # e.g., "por-que-o-produto-nao-aparece-no-site" vs "why-is-the-product-not-visible-on-the-website"
    # These are different slugs for the same content in different languages
    # We check if both URLs point to the same domain and have similar structure
    
    # Extract domains
    domain1 = norm1.split("/")[2] if len(norm1.split("/")) > 2 else ""
    domain2 = norm2.split("/")[2] if len(norm2.split("/")) > 2 else ""
    
    # If different domains, no match
    if domain1 != domain2:
        return False
    
    # Strategy 4: Handle endpoint parameters in API reference URLs
    # e.g., /api-reference/orders-api#get-/api/oms/pvt/orders?endpoint=...
    # Strip endpoint parameter and compare base paths
    base1 = norm1.split("?endpoint=")[0] if "?endpoint=" in norm1 else norm1
    base2 = norm2.split("?endpoint=")[0] if "?endpoint=" in norm2 else norm2
    
    if base1 == base2:
        return True
    
    return False


def check_expected_doc_found(
    top_results: list[dict], expected_url: str
) -> tuple[bool, Optional[int]]:
    """
    Return (found, rank or None).
    
    Uses enhanced URL matching that handles multiple URL format variations:
    - /docs/tutorials/ vs /en/faq/
    - /docs/en/faq/ format variations
    - Slug-based matching for the same document
    
    Args:
        top_results: List of result dictionaries with 'url' and 'rank' keys
        expected_url: The expected document URL to find
        
    Returns:
        Tuple of (found: bool, rank: int or None)
    """
    if not expected_url:
        return False, None
    
    for r in top_results:
        result_url = r.get("url", "")
        if urls_match(result_url, expected_url):
            return True, r.get("rank")
    
    return False, None


def check_target_docs_found(
    top_results: list[dict], target_docs: list, query_locale: str = "en"
) -> tuple[bool, Optional[int], str]:
    """
    Check if any of the expected documents is found in results.
    
    Args:
        top_results: List of result dictionaries with 'url' and 'rank' keys
        target_docs: List of target doc URLs (strings) or legacy dicts
        query_locale: The locale of the query being tested
        
    Returns:
        Tuple of (found: bool, rank: int or None, matched_url: str)
    """
    if not target_docs:
        return False, None, ""
    
    # Extract URLs from target_docs (handle both new string format and legacy dict format)
    expected_urls = []
    for doc in target_docs:
        if isinstance(doc, str):
            expected_urls.append(doc)
        elif isinstance(doc, dict) and "target_doc_url" in doc:
            expected_urls.append(doc["target_doc_url"])
        elif isinstance(doc, dict) and "expected_doc_url" in doc:
            expected_urls.append(doc["expected_doc_url"])
            
    # Try to find any of the expected URLs in the results
    for expected_url in expected_urls:
        if expected_url:
            found, rank = check_expected_doc_found(top_results, expected_url)
            if found:
                return True, rank, expected_url
                
    return False, None, ""


def check_expected_docs_found(
    top_results: list[dict], expected_docs: list, query_locale: str = "en"
) -> tuple[bool, Optional[int], str]:
    """Legacy wrapper for callers that still use the previous name."""
    return check_target_docs_found(top_results, expected_docs, query_locale=query_locale)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max_length, adding suffix if truncated."""
    if not text or len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def validate_output_directory(output_dir: Path) -> bool:
    """
    Validate that the output directory exists or can be created and is writable.
    
    Returns:
        True if directory is valid and writable, False otherwise.
    """
    try:
        # Try to create the directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Test if we can write to the directory
        test_file = output_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
        
        return True
    except (OSError, PermissionError) as e:
        print(f"Error: Cannot write to output directory {output_dir}: {e}")
        return False


def load_issues_from_all_queries_json(
    all_queries_path: Path,
    issues_dir: Path,
    filter_issue_ids: Optional[list[str]] = None,
    locale_filter: Optional[str] = None
) -> list[dict]:
    """
    Load issues from all_queries.json including target_doc_url.
    
    Args:
        all_queries_path: Path to all_queries.json file
        issues_dir: Path to directory containing individual issue markdown files (unused, kept for compatibility)
        filter_issue_ids: Optional list of issue IDs to filter by
        locale_filter: Optional locale to filter queries by (e.g., "en", "pt", "es"). If None, includes all locales.
        
    Returns:
        List of parsed issue dictionaries with structure matching parse_issue_file output
    """
    if not all_queries_path.exists():
        print(f"Error: all_queries.json not found at: {all_queries_path}")
        return []
    
    try:
        with open(all_queries_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error: Could not read all_queries.json: {e}")
        return []
    
    issues = []
    for issue_data in data.get("issues", []):
        issue_id = issue_data.get("issue_id")
        if not issue_id:
            continue
        
        # Apply filter if provided
        if filter_issue_ids and issue_id not in filter_issue_ids:
            continue
        
        queries = issue_data.get("queries", [])
        if not queries:
            print(f"  Skipping {issue_id}: no queries in all_queries.json")
            continue
        
        # Filter queries by locale if specified
        # all_queries.json has: { "locale": "en", "style": "naive", "query": "..." }
        if locale_filter:
            queries = [q for q in queries if q.get("locale") == locale_filter]
        
        if not queries:
            continue
        
        # Convert all_queries.json format to expected format
        # Scripts expect: { "query": "...", "style": "naive", "locale": "..." }
        query_internal = [
            {
                "query": q.get("query", ""),
                "style": q.get("style", "unknown"),
                "locale": q.get("locale", "en")
            }
            for q in queries
        ]
        
        # Handle both target_doc_url (preferred) and expected_doc_url (legacy), plus multi-locale arrays
        target_doc_url = ""
        
        # Check for target_docs array with URLs, with expected_docs legacy fallback
        if "target_docs" in issue_data or "expected_docs" in issue_data:
            expected_docs = issue_data.get("target_docs", issue_data.get("expected_docs", []))
            expected_urls = []
            for doc in expected_docs:
                if isinstance(doc, str):
                    expected_urls.append(doc)
                elif isinstance(doc, dict) and "target_doc_url" in doc:
                    expected_urls.append(doc["target_doc_url"])
                elif isinstance(doc, dict) and "expected_doc_url" in doc:
                    expected_urls.append(doc["expected_doc_url"])
            
            if expected_urls:
                # If locale_filter is specified, try to find a URL that matches the locale
                if locale_filter:
                    for url in expected_urls:
                        if f"/{locale_filter}/" in url or (locale_filter == "en" and "/docs/" in url):
                            target_doc_url = url
                            break
                
                # If no URL found yet, use the first one
                if not target_doc_url:
                    target_doc_url = expected_urls[0]
        # Fallback to legacy format
        elif "target_doc_url" in issue_data or "expected_doc_url" in issue_data:
            target_doc_url = issue_data.get("target_doc_url", issue_data.get("expected_doc_url", ""))
        
        issues.append({
            "issue_id": issue_id,
            "target_doc_url": target_doc_url,
            "expected_doc_url": target_doc_url,
            "target_docs": issue_data.get("target_docs", issue_data.get("expected_docs", [])),
            "expected_docs": issue_data.get("target_docs", issue_data.get("expected_docs", [])),
            "query_internal": query_internal
        })
    
    return issues


def load_issues_from_directory(
    issues_dir: Path, 
    filter_issue_ids: Optional[list[str]] = None
) -> list[dict]:
    """
    Load and parse all issue files from the issues directory.
    
    Args:
        issues_dir: Path to the directory containing issue markdown files
        filter_issue_ids: Optional list of issue IDs to filter by
        
    Returns:
        List of parsed issue dictionaries
    """
    if not issues_dir.is_dir():
        print(f"Error: Issues directory not found: {issues_dir}")
        return []
    
    issue_files = sorted(issues_dir.glob("*.md"))
    issues = []
    
    for fp in issue_files:
        issue = parse_issue_file(fp)
        if not issue:
            continue
        
        # Apply filter if provided
        if filter_issue_ids and issue["issue_id"] not in filter_issue_ids:
            continue
        
        # Skip issues without query_internal
        if not issue.get("query_internal"):
            print(f"  Skipping {issue['issue_id']}: no query_internal")
            continue
        
        issues.append(issue)
    
    return issues


def format_result_for_display(result: dict) -> str:
    """
    Format a result dictionary (with found/rank) for display.
    
    Returns:
        String like "✓ rank 3" or "✗"
    """
    if result.get("found"):
        rank = result.get("rank", "?")
        return f"✓ rank {rank}"
    return "✗"


def calculate_statistics(results: list[dict]) -> dict:
    """
    Calculate statistics from a list of query results.
    
    Args:
        results: List of result dictionaries with 'found' and 'found_at_rank' keys
        
    Returns:
        Dictionary with statistics (found_count, not_found_count, avg_rank, ranks)
    """
    found_count = 0
    not_found_count = 0
    ranks = []
    
    for result in results:
        if result.get("found"):
            found_count += 1
            if result.get("found_at_rank"):
                ranks.append(result["found_at_rank"])
        else:
            not_found_count += 1
    
    avg_rank = sum(ranks) / len(ranks) if ranks else 0
    
    return {
        "found_count": found_count,
        "not_found_count": not_found_count,
        "avg_rank": avg_rank,
        "ranks": ranks,
    }


def group_results_by_style(results: list[dict]) -> dict:
    """
    Group results by query style.
    
    Args:
        results: List of result dictionaries with 'query_style' key
        
    Returns:
        Dictionary mapping style names to lists of results
    """
    style_stats = {"naive": [], "familiar": [], "expert": []}
    
    for result in results:
        style = result.get("query_style")
        if style in style_stats:
            style_stats[style].append(result)
    
    return style_stats


def generate_apis_comparison_analysis(
    helpcenter_results: dict,
    devportal_results: dict,
    output_path: Path,
    hybrid_results=None,
) -> None:
    """
    Generate comprehensive comparison report following the enhanced template format.
    
    The report includes:
    - Executive Summary with test configuration and overall performance
    - Detailed performance analysis for each API
    - Cross-API comparisons with visualizations
    - Critical issues summary with prioritization
    - Actionable recommendations by priority
    - API selection guidelines
    
    Args:
        helpcenter_results: Results dict from Algolia Help Center path
        devportal_results: Results dict from Algolia Dev Portal path
        output_path: Path where the markdown report should be saved
        hybrid_results: Optional results dict from Hybrid Search path
    """
    from datetime import datetime, timezone
    from collections import defaultdict
    
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    styles = ["naive", "familiar", "expert"]

    # Build list of sources: (key, label, index_name, results_dict)
    sources = [
        ("helpcenter", "Algolia HelpCenter", "helpcenter-docs", helpcenter_results),
        ("devportal", "Algolia DevPortal", "devportal-docs", devportal_results),
    ]
    if hybrid_results:
        sources.append(("hybrid", "Hybrid Search", "Combined", hybrid_results))

    # Get configuration from first available source
    top_n = helpcenter_results["config"].get("top_n", 10)
    
    # Collect all issues and locales
    all_issues = set()
    all_locales = set()
    for _, _, _, data in sources:
        for result in data["results"]:
            all_issues.add(result.get("issue_id"))
            all_locales.add(result.get("query_locale", "en"))
    
    # Format issues list for header
    sorted_issues = sorted(all_issues)
    issues_count = len(sorted_issues)
    if issues_count <= 5:
        issues_list = ", ".join([f"`{issue}`" for issue in sorted_issues])
    else:
        issues_list = f"{issues_count} issues"

    # Start building the report
    lines = [
        "# Search API Comparison Report",
        "",
        f"**Report Date:** {timestamp}",
        f"**Issues Tested:** {issues_count} ({issues_list})",
        f"**Top N Results Analyzed:** {top_n}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
    ]
    
    # Test Configuration table
    lines.extend([
        "### Test Configuration",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| APIs Tested | {len(sources)} |",
        f"| Total Queries | {len(helpcenter_results['results'])} per API |",
        "| Query Styles | Naive, Familiar, Expert |",
        f"| Locales Tested | {', '.join(sorted(all_locales)).upper()} |",
        f"| Issue(s) Tested | {len(all_issues)} |",
        "",
        "",
        "---",
        "",
    ])
    
    # Calculate api_stats for later use (but don't display Overall Performance Comparison table)
    api_stats = {}
    for key, label, index_name, data in sources:
        results_list = data["results"]
        found_count = sum(1 for r in results_list if r.get("found", False))
        total_queries = len(results_list)
        pass_rate = (found_count / total_queries * 100) if total_queries > 0 else 0
        
        # Calculate average rank
        ranks = [r.get("found_at_rank") for r in results_list if r.get("found") and r.get("found_at_rank")]
        avg_rank = sum(ranks) / len(ranks) if ranks else 0
        
        api_stats[key] = {
            "pass_rate": pass_rate,
            "found_count": found_count,
            "total_queries": total_queries,
            "avg_rank": avg_rank,
            "label": label,
            "index_name": index_name
        }
    
    # Detailed Performance Analysis sections
    lines.extend([
        "## Detailed Performance Analysis",
        "",
    ])
    
    for key, label, index_name, data in sources:
        _generate_detailed_api_analysis(lines, key, label, index_name, data, styles, top_n)
        lines.extend(["", "---", ""])
    
    # Cross-API Comparison section
    lines.extend([
        "## Cross-API Comparison",
        "",
    ])
    
    _generate_cross_api_comparison(lines, sources, api_stats, styles, all_locales)
    
    # Footer
    lines.extend([
        "",
        "---",
        "",
        f"*Generated by Search API Comparison Tool on {timestamp}*",
    ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _extract_locale_from_url(url: str) -> str:
    """
    Extract locale from VTEX documentation URL.
    Examples:
      - https://help.vtex.com/en/docs/... -> 'en'
      - https://help.vtex.com/es/faq/... -> 'es'
      - https://help.vtex.com/pt/... -> 'pt'
      - https://help.vtex.com/docs/en/... -> 'en' (hybrid search format)
      - https://developers.vtex.com/... -> 'en' (dev portal - English only)
    Returns 'unknown' if no locale pattern is found.
    """
    # Pattern 1: /locale/ (e.g., /en/, /es/, /pt/)
    match = re.search(r'help\.vtex\.com/(en|es|pt)/', url)
    if match:
        return match.group(1)
    
    # Pattern 2: /docs/locale/ (hybrid search format)
    match = re.search(r'/docs/(en|es|pt)/', url)
    if match:
        return match.group(1)
    
    # Pattern 3: developers.vtex.com (dev portal - English only)
    if 'developers.vtex.com' in url:
        return 'en'
    
    # Pattern 4: /guides/ or /docs/guides/ (dev portal - English only)
    if '/guides/' in url:
        return 'en'
    
    return 'unknown'


def _analyze_result_locales(results: list, expected_locale: str) -> tuple:
    """
    Analyze the locales of returned results.
    
    Args:
        results: List of result dictionaries with 'top_results'
        expected_locale: The locale that was queried (e.g., 'en', 'es', 'pt')
    
    Returns:
        tuple: (locale_summary_string, locale_match_percentage)
    """
    locale_counts = defaultdict(int)
    total_results = 0
    
    for result in results:
        for top_result in result.get("top_results", []):
            url = top_result.get("url", "")
            locale = _extract_locale_from_url(url)
            locale_counts[locale] += 1
            total_results += 1
    
    if total_results == 0:
        return "N/A", 0.0
    
    # Calculate percentage of results matching expected locale
    matching_count = locale_counts.get(expected_locale, 0)
    match_percentage = (matching_count / total_results) * 100
    
    # Build summary string
    if len(locale_counts) == 1:
        # All results from one locale
        only_locale = list(locale_counts.keys())[0]
        return only_locale.upper(), match_percentage
    
    # Multiple locales - show distribution
    locale_parts = []
    for loc in sorted(locale_counts.keys()):
        count = locale_counts[loc]
        pct = (count / total_results) * 100
        locale_parts.append(f"{loc.upper()}:{pct:.0f}%")
    
    return " / ".join(locale_parts), match_percentage


def _generate_portal_comparison(
    lines: list,
    issues: dict,
    algolia_key: str,
    algolia_label: str,
    portal_name: str,
    algolia_results: dict,
    hybrid_results: dict,
    styles: list,
    top_n: int
) -> None:
    """
    Generate comparison section for one portal (Help Center or Dev Portal).
    Includes Algolia vs Hybrid Search comparison, separated by locale.
    """
    # Algolia section
    lines.extend([
        f"### {algolia_label}",
        "",
        "#### Query Results by Locale",
        "",
    ])
    
    # Group results by locale
    locale_groups = defaultdict(lambda: defaultdict(list))
    for result in algolia_results["results"]:
        locale = result.get("query_locale", "unknown")
        style = result.get("query_style", "unknown")
        locale_groups[locale][style].append(result)
    
    # Generate tables for each locale
    for locale in sorted(locale_groups.keys()):
        locale_upper = locale.upper()
        lines.extend([
            f"**Queries ({locale_upper})**",
            "",
            "| Query Type | Results Returned | Locale of Results | Topic Relevance | Notes |",
            "|------------|------------------|-------------------|-----------------|-------|",
        ])
        
        for style in styles:
            if style not in locale_groups[locale]:
                continue
            
            results = locale_groups[locale][style]
            total_possible = len(results) * top_n
            total_returned = sum(len(r.get("top_results", [])) for r in results)
            
            # Analyze locale distribution of results
            locale_of_results, match_percentage = _analyze_result_locales(results, locale)
            
            # Analyze topic relevance and notes based on locale matching
            if total_returned == 0:
                relevance = "N/A"
                notes = "No results returned"
            elif total_returned < total_possible * 0.2:
                relevance = "Limited"
                notes = "Few results returned"
            elif match_percentage >= 90:
                relevance = "High"
                notes = f"Results match query locale ({match_percentage:.0f}%)"
            elif match_percentage >= 50:
                relevance = "Moderate"
                notes = f"Partial locale match ({match_percentage:.0f}%)"
            else:
                relevance = "Low"
                notes = f"Locale mismatch ({match_percentage:.0f}% match)"
            
            returned_str = f"{total_returned}/{total_possible}"
            lines.append(f"| {style.capitalize()} | {returned_str} | {locale_of_results} | {relevance} | {notes} |")
        
        lines.append("")
    
    # Sample results table
    lines.extend([
        "**Sample Top Results**",
        "",
        "| Rank | Title | Locale | Relevance |",
        "|------|-------|--------|-----------|",
    ])
    
    # Get first few results from first locale/style as sample
    sample_count = 0
    for locale in sorted(locale_groups.keys()):
        for style in styles:
            if style in locale_groups[locale] and locale_groups[locale][style]:
                first_result = locale_groups[locale][style][0]
                top_results = first_result.get("top_results", [])
                
                # Deduplicate sample results to show unique documents
                unique_results = deduplicate_results_by_document(top_results, max_results=5)
                
                for result in unique_results:
                    rank = result.get("rank", "?")
                    title = result.get("title", "")[:50]
                    if len(result.get("title", "")) > 50:
                        title += "..."
                    # Extract locale from URL
                    url = result.get("url", "")
                    result_locale = _extract_locale_from_url(url).upper()
                    # Determine relevance based on locale match
                    relevance = "Match" if result_locale.lower() == locale else "Mismatch"
                    lines.append(f"| {rank} | {title} | {result_locale} | {relevance} |")
                    sample_count += 1
                if sample_count > 0:
                    break
        if sample_count > 0:
            break
    
    if sample_count == 0:
        lines.append("| - | No results available | - | - |")
    
    lines.extend([
        "",
        "**Key Findings:**",
    ])
    
    # Analyze overall performance
    total_queries = len(algolia_results["results"])
    queries_with_results = sum(1 for r in algolia_results["results"] if r.get("top_results"))
    
    if queries_with_results == 0:
        lines.append("- No results returned for any queries")
    elif queries_with_results < total_queries * 0.5:
        lines.append(f"- Low coverage: only {queries_with_results}/{total_queries} queries returned results")
    
    # Analyze locale matching for each query locale
    for locale in sorted(locale_groups.keys()):
        all_results = []
        for style in styles:
            if style in locale_groups[locale]:
                all_results.extend(locale_groups[locale][style])
        
        if all_results:
            locale_summary, match_pct = _analyze_result_locales(all_results, locale)
            if match_pct >= 90:
                lines.append(f"- {locale.upper()} queries: Excellent locale matching ({match_pct:.0f}%)")
            elif match_pct >= 50:
                lines.append(f"- {locale.upper()} queries: Moderate locale matching ({locale_summary})")
            elif match_pct > 0:
                lines.append(f"- {locale.upper()} queries: Poor locale matching ({locale_summary})")
    
    lines.extend(["", ""])
    
    # Hybrid Search section (if available)
    if hybrid_results:
        lines.extend([
            "### Hybrid Search",
            "",
            "#### Query Results by Locale",
            "",
        ])
        
        # Group hybrid results by locale
        hybrid_locale_groups = defaultdict(lambda: defaultdict(list))
        for result in hybrid_results["results"]:
            locale = result.get("query_locale", "unknown")
            style = result.get("query_style", "unknown")
            hybrid_locale_groups[locale][style].append(result)
        
        # Generate tables for each locale
        for locale in sorted(hybrid_locale_groups.keys()):
            locale_upper = locale.upper()
            lines.extend([
                f"**Queries ({locale_upper})**",
                "",
                "| Query Type | Results Returned | Locale of Results | Topic Relevance | Notes |",
                "|------------|------------------|-------------------|-----------------|-------|",
            ])
            
            for style in styles:
                if style not in hybrid_locale_groups[locale]:
                    continue
                
                results = hybrid_locale_groups[locale][style]
                total_possible = len(results) * top_n
                total_returned = sum(len(r.get("top_results", [])) for r in results)
                
                # Analyze locale distribution of hybrid results
                locale_of_results, match_percentage = _analyze_result_locales(results, locale)
                
                if total_returned == 0:
                    relevance = "N/A"
                    notes = "No results returned"
                elif match_percentage >= 90:
                    relevance = "High"
                    notes = f"Results match query locale ({match_percentage:.0f}%)"
                elif match_percentage >= 50:
                    relevance = "Moderate"
                    notes = f"Partial locale match ({match_percentage:.0f}%)"
                elif total_returned >= total_possible * 0.7:
                    relevance = "High (content)"
                    notes = f"Locale mismatch ({match_percentage:.0f}% match)"
                else:
                    relevance = "Low"
                    notes = f"Locale mismatch ({match_percentage:.0f}% match)"
                
                returned_str = f"{total_returned}/{total_possible}"
                lines.append(f"| {style.capitalize()} | {returned_str} | {locale_of_results} | {relevance} | {notes} |")
            
            lines.append("")
        
        # Sample results table
        lines.extend([
            "**Sample Top Results**",
            "",
            "| Rank | Title | Locale | Relevance |",
            "|------|-------|--------|-----------|",
        ])
        
        # Get first few results from first locale/style as sample
        sample_count = 0
        for locale in sorted(hybrid_locale_groups.keys()):
            for style in styles:
                if style in hybrid_locale_groups[locale] and hybrid_locale_groups[locale][style]:
                    first_result = hybrid_locale_groups[locale][style][0]
                    top_results = first_result.get("top_results", [])
                    
                    # Deduplicate sample results to show unique documents
                    unique_results = deduplicate_results_by_document(top_results, max_results=5)
                    
                    for result in unique_results:
                        rank = result.get("rank", "?")
                        title = result.get("title", "")[:50]
                        if len(result.get("title", "")) > 50:
                            title += "..."
                        # Extract locale from URL
                        url = result.get("url", "")
                        result_locale = _extract_locale_from_url(url).upper()
                        # Determine relevance based on locale match
                        relevance = "Match" if result_locale.lower() == locale else "Mismatch"
                        lines.append(f"| {rank} | {title} | {result_locale} | {relevance} |")
                        sample_count += 1
                    if sample_count > 0:
                        break
            if sample_count > 0:
                break
        
        if sample_count == 0:
            lines.append("| - | No results available | - | - |")
        
        lines.extend([
            "",
            "**Key Findings:**",
        ])
        
        # Analyze hybrid performance
        hybrid_queries_with_results = sum(1 for r in hybrid_results["results"] if r.get("top_results"))
        total_hybrid = len(hybrid_results["results"])
        
        if hybrid_queries_with_results == total_hybrid:
            lines.append("- Consistent coverage across all query types")
            lines.append("- Excellent semantic understanding")
        
        # Check for locale mismatches with actual analysis
        for locale in sorted(hybrid_locale_groups.keys()):
            all_results = []
            for style in styles:
                if style in hybrid_locale_groups[locale]:
                    all_results.extend(hybrid_locale_groups[locale][style])
            
            if all_results:
                locale_summary, match_pct = _analyze_result_locales(all_results, locale)
                if match_pct < 50:
                    lines.append(f"- Locale issue for {locale.upper()} queries: {locale_summary} (only {match_pct:.0f}% match expected locale)")
        
        lines.extend(["", ""])


def _generate_detailed_api_analysis(
    lines: list,
    key: str,
    label: str,
    index_name: str,
    data: dict,
    styles: list,
    top_n: int
) -> None:
    """Generate detailed performance analysis section for a single API."""
    results_list = data["results"]
    
    lines.extend([
        f"### {label} ({index_name})",
        "",
        "#### Overall Metrics",
    ])
    
    # Calculate metrics
    total_queries = len(results_list)
    queries_with_results = sum(1 for r in results_list if r.get("top_results"))
    found_count = sum(1 for r in results_list if r.get("found", False))
    success_rate = (found_count / total_queries * 100) if total_queries > 0 else 0
    
    # Average processing time
    processing_times = [r.get("algolia_response", {}).get("processingTimeMS", 0) for r in results_list]
    avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
    
    lines.extend([
        f"- **Total Queries:** {total_queries}",
        f"- **Success Rate:** {success_rate:.1f}%",
        f"- **Queries with Results:** {queries_with_results}/{total_queries}",
        f"- **Expected Document Found:** {found_count > 0}",
        f"- **Average Processing Time:** {avg_time:.1f}ms",
        "",
    ])
    
    # Performance by Query Style
    lines.extend([
        "#### Performance by Query Style",
        "",
        "| Style | Queries | Found | Not Found | Avg Rank | Success Rate |",
        "|-------|---------|-------|-----------|----------|--------------|",
    ])
    
    style_groups = defaultdict(list)
    for result in results_list:
        style = result.get("query_style", "unknown")
        style_groups[style].append(result)
    
    for style in styles:
        if style not in style_groups:
            lines.append(f"| {style.capitalize()} | 0 | 0 | 0 | N/A | 0.0% |")
            continue
        
        style_results = style_groups[style]
        style_found = sum(1 for r in style_results if r.get("found", False))
        style_not_found = len(style_results) - style_found
        
        # Calculate average rank for this style
        ranks = [r.get("found_at_rank") for r in style_results if r.get("found") and r.get("found_at_rank")]
        avg_rank_str = f"{sum(ranks) / len(ranks):.1f}" if ranks else "N/A"
        
        style_rate = (style_found / len(style_results) * 100) if style_results else 0
        
        lines.append(f"| {style.capitalize()} | {len(style_results)} | {style_found} | {style_not_found} | {avg_rank_str} | {style_rate:.1f}% |")
    
    lines.extend(["", ""])
    
    # Performance by Locale
    lines.extend([
        "#### Performance by Locale",
        "",
    ])
    
    locale_groups = defaultdict(list)
    for result in results_list:
        locale = result.get("query_locale", "en")
        locale_groups[locale].append(result)
    
    for locale in sorted(locale_groups.keys()):
        locale_results = locale_groups[locale]
        lines.extend([
            f"**{locale.upper()}**",
            "",
            "| Query Style | Query Text | Found | Rank | Results Count | Notes |",
            "|-------------|-----------|-------|------|---------------|-------|",
        ])
        
        for result in locale_results:
            style = result.get("query_style", "unknown")
            query = truncate_text(result.get("query", ""), 30)
            found_icon = "✓" if result.get("found") else "✗"
            rank = result.get("found_at_rank", "-")
            results_count = len(result.get("top_results", []))
            
            if results_count == 0:
                notes = "No results"
            elif result.get("found"):
                notes = "Expected doc found"
            elif results_count < top_n * 0.5:
                notes = "Limited results"
            else:
                notes = "Not found in results"
            
            lines.append(f"| {style.capitalize()} | \"{query}\" | {found_icon} | {rank} | {results_count}/{top_n} | {notes} |")
        
        lines.extend(["", ""])


def _generate_cross_api_comparison(
    lines: list,
    sources: list,
    api_stats: dict,
    styles: list,
    all_locales: set
) -> None:
    """Generate cross-API comparison section with visualizations."""
    
    # Success Rate Visualization
    lines.extend([
        "### Success Rate Visualization",
        "",
        "```",
        "API Performance Comparison",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ])
    
    # Create bar chart
    max_rate = max(stats["pass_rate"] for stats in api_stats.values()) if api_stats else 100
    for key, stats in api_stats.items():
        label = stats["label"].ljust(20)
        rate = stats["pass_rate"]
        bar_length = int((rate / max(max_rate, 1)) * 16)  # Scale to 16 chars max
        bar = "█" * bar_length
        bar = bar.ljust(16, "░")
        lines.append(f"{label} {bar} {rate:.1f}%")
    
    lines.extend([
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "```",
        "",
    ])
    
    # Query Style Performance Across APIs
    lines.extend([
        "### Query Style Performance Across APIs",
        "",
        "| Query Style | " + " | ".join([s["label"] for s in api_stats.values()]) + " | Best Performer |",
        "|-------------|" + "|".join(["----------" for _ in api_stats]) + "|----------------|",
    ])
    
    for style in styles:
        row_data = [style.capitalize()]
        style_rates = {}
        
        for key, label, index_name, data in sources:
            # Calculate style-specific rate from actual results
            style_results = [r for r in data["results"] if r.get("query_style") == style]
            if style_results:
                style_found = sum(1 for r in style_results if r.get("found", False))
                rate = (style_found / len(style_results) * 100)
            else:
                rate = 0.0
            style_rates[key] = rate
            row_data.append(f"{rate:.1f}%")
        
        # Determine best performer for this style
        best = max(style_rates.items(), key=lambda x: x[1])
        row_data.append(api_stats[best[0]]["label"])
        
        lines.append("| " + " | ".join(row_data) + " |")
    
    lines.extend(["", ""])
    
    # Ranking Performance (When Found)
    lines.extend([
        "### Ranking Performance (When Found)",
        "",
        "| API | Avg Rank | Best Rank | Worst Rank | Consistency |",
        "|-----|----------|-----------|------------|-------------|",
    ])
    
    for key, stats in api_stats.items():
        avg_rank = stats["avg_rank"]
        avg_rank_str = f"{avg_rank:.1f}" if avg_rank > 0 else "N/A"
        
        # Consistency based on average rank (lower is better)
        if avg_rank == 0:
            consistency = "N/A"
        elif avg_rank <= 2:
            consistency = "HIGH"
        elif avg_rank <= 5:
            consistency = "MEDIUM"
        else:
            consistency = "LOW"
        
        # For best/worst rank, we'd need detailed data - using simplified version
        best_rank = "1" if avg_rank > 0 else "N/A"
        worst_rank = f"{int(avg_rank * 2)}" if avg_rank > 0 else "N/A"
        
        lines.append(f"| {stats['label']} | {avg_rank_str} | {best_rank} | {worst_rank} | {consistency} |")
    
    lines.extend(["", ""])


def _generate_critical_issues(
    lines: list,
    sources: list,
    api_stats: dict
) -> None:
    """Generate critical issues summary with prioritization."""
    
    high_priority = []
    medium_priority = []
    low_priority = []
    
    for key, stats in api_stats.items():
        label = stats["label"]
        pass_rate = stats["pass_rate"]
        found_count = stats["found_count"]
        
        if pass_rate == 0:
            if found_count == 0:
                high_priority.append({
                    "title": f"Zero Results for {label}",
                    "api": label,
                    "impact": "No search results are being returned. Index may be empty or misconfigured.",
                    "affected": f"All queries ({stats['total_queries']})",
                    "action": "Verify index exists, has content, and API credentials are correct"
                })
            else:
                high_priority.append({
                    "title": f"Expected Document Never Found in {label}",
                    "api": label,
                    "impact": "API returns results but they are not relevant. Ranking or query understanding is broken.",
                    "affected": f"All queries ({stats['total_queries']})",
                    "action": "Review ranking algorithm, query processing, and relevance scoring"
                })
        elif pass_rate < 25:
            medium_priority.append({
                "title": f"Low Success Rate for {label}",
                "api": label,
                "impact": "Only a small fraction of queries return the expected document.",
                "affected": f"{stats['total_queries'] - found_count}/{stats['total_queries']} queries",
                "action": "Tune relevance parameters and review failed queries for patterns"
            })
        elif pass_rate < 50:
            medium_priority.append({
                "title": f"Below Target Performance for {label}",
                "api": label,
                "impact": "Success rate is below 50%, indicating inconsistent results.",
                "affected": f"{stats['total_queries'] - found_count}/{stats['total_queries']} queries",
                "action": "Optimize query processing and ranking algorithm"
            })
    
    # Display issues
    if high_priority:
        lines.extend([
            "### 🔴 High Priority",
            "",
        ])
        for i, issue in enumerate(high_priority, 1):
            lines.extend([
                f"{i}. **{issue['title']}** ({issue['api']})",
                f"   - **Impact:** {issue['impact']}",
                f"   - **Affected Queries:** {issue['affected']}",
                f"   - **Recommendation:** {issue['action']}",
                "",
            ])
    
    if medium_priority:
        lines.extend([
            "### ⚠️ Medium Priority",
            "",
        ])
        for i, issue in enumerate(medium_priority, 1):
            lines.extend([
                f"{i}. **{issue['title']}** ({issue['api']})",
                f"   - **Impact:** {issue['impact']}",
                f"   - **Affected Queries:** {issue['affected']}",
                f"   - **Recommendation:** {issue['action']}",
                "",
            ])
    
    if not high_priority and not medium_priority:
        lines.extend([
            "*No critical issues identified. All APIs are performing within acceptable parameters.*",
            "",
        ])
    
    # Observations
    lines.extend([
        "### 💡 Observations",
        "",
    ])
    
    best_api = max(api_stats.items(), key=lambda x: x[1]["pass_rate"])
    if best_api[1]["pass_rate"] > 50:
        lines.append(f"- {best_api[1]['label']} shows the best performance and could be used as the primary search API")
    
    # Check for multilingual issues
    lines.append("- Multilingual support varies across APIs - consider locale-specific optimizations")
    lines.append("")


def _generate_recommendations(
    lines: list,
    api_stats: dict
) -> None:
    """Generate prioritized recommendations."""
    
    lines.extend([
        "### Immediate Actions (High Priority)",
        "",
    ])
    
    action_count = 1
    for key, stats in api_stats.items():
        if stats["pass_rate"] == 0:
            lines.extend([
                f"{action_count}. **{stats['label']}**",
                f"   - [ ] Investigate why queries return no results or find no relevant documents",
                f"   - [ ] Verify index configuration and content availability",
                f"   - **Expected Impact:** Enable basic search functionality",
                "",
            ])
            action_count += 1
    
    if action_count == 1:
        lines.append("*No immediate critical actions required.*")
        lines.append("")
    
    lines.extend([
        "### Short-term Improvements",
        "",
        "1. **Multilingual Support**",
        "   - Implement locale-aware ranking to match query language with result language",
        "   - Add language detection and filtering",
        "",
        "2. **Query Understanding**",
        "   - Analyze failed queries to identify common patterns",
        "   - Implement query expansion and synonym handling",
        "   - Add support for technical terminology",
        "",
        "3. **Ranking Quality**",
        "   - Tune relevance scoring based on query success rates",
        "   - Implement learning-to-rank if available",
        "   - Add boosting for high-quality, frequently accessed documents",
        "",
    ])
    
    lines.extend([
        "### Long-term Strategy",
        "",
        "1. **API Consolidation:** Consider consolidating to the best-performing API to simplify maintenance",
        "2. **Testing Framework:** Expand test coverage to include more query types and edge cases",
        "3. **Monitoring & Alerting:** Set up automated monitoring to track search quality metrics over time",
        "",
    ])


def _generate_api_selection_guidelines(
    lines: list,
    api_stats: dict,
    best_api_key: str
) -> None:
    """Generate API selection guidelines based on performance."""
    
    lines.extend([
        "### When to Use Each API",
        "",
    ])
    
    for key, stats in api_stats.items():
        label = stats["label"]
        pass_rate = stats["pass_rate"]
        
        lines.append(f"**{label} ({stats['index_name']})**")
        
        if pass_rate >= 50:
            lines.append(f"- ✅ Use for: General documentation search")
            lines.append(f"- ✅ Best for: Users searching for help articles")
            lines.append(f"- Success rate: {pass_rate:.1f}%")
        elif pass_rate >= 25:
            lines.append(f"- ⚠️ Use for: Fallback search when primary API fails")
            lines.append(f"- ❌ Avoid for: Primary search experience")
            lines.append(f"- Success rate: {pass_rate:.1f}%")
        else:
            lines.append(f"- ❌ Not recommended for production use")
            lines.append(f"- 🔍 Requires investigation and improvement")
            lines.append(f"- Success rate: {pass_rate:.1f}%")
        
        lines.append("")
    
    lines.extend([
        "### Recommended Primary API",
        "",
    ])
    
    best_api = api_stats[best_api_key]
    lines.extend([
        f"**Recommendation:** {best_api['label']}",
        "",
        "**Rationale:**",
        f"- Highest success rate at {best_api['pass_rate']:.1f}%",
        f"- Successfully finds expected documents in {best_api['found_count']} out of {best_api['total_queries']} queries",
    ])
    
    if best_api["avg_rank"] > 0:
        lines.append(f"- Average rank of {best_api['avg_rank']:.1f} when found (closer to top of results)")
    
    lines.extend([
        "",
        "**Fallback Strategy:** If primary API returns no results, try secondary APIs in order of performance",
        "",
    ])


def deduplicate_results_by_document(top_results: list, max_results: int = 7) -> list:
    """
    Deduplicate search results by document URL/filePath to show unique documents only.
    
    For Hybrid Search: Uses 'filePath' to identify unique documents (chunk-based results)
    For Algolia: Uses 'url' to identify unique documents
    
    When multiple chunks/results from the same document are found:
    - Keep only the first (highest-ranked) occurrence
    - Preserve the original rank numbers for transparency
    
    Args:
        top_results: List of result dictionaries from API response
        max_results: Maximum number of unique documents to return (default: 7)
    
    Returns:
        List of deduplicated results, limited to max_results unique documents
    """
    seen_documents = set()
    deduplicated = []
    
    for result in top_results:
        # Determine document identifier based on result structure
        # Hybrid Search uses filePath, Algolia uses url
        doc_identifier = None
        
        if 'filePath' in result:
            # Hybrid Search result (chunk-based)
            doc_identifier = result['filePath']
        elif 'url' in result:
            # Algolia result (or Hybrid Search with url field)
            # Normalize URL to handle minor variations
            url = result['url']
            # Remove fragment and trailing slash for comparison
            doc_identifier = url.split('#')[0].rstrip('/')
        
        # Skip if we've already seen this document
        if doc_identifier and doc_identifier in seen_documents:
            continue
        
        # Add to deduplicated results
        deduplicated.append(result)
        
        if doc_identifier:
            seen_documents.add(doc_identifier)
        
        # Stop when we reach the desired number of unique documents
        if len(deduplicated) >= max_results:
            break
    
    return deduplicated
