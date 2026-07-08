#!/usr/bin/env python3
"""
Extract all issue queries and generate path-level JSON files.

Output files are written under data/test-suite/<path>/all_queries.json.
"""

import argparse
import json
import re
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
ISSUES_DIR = REPO_ROOT / "docs" / "test-suite" / "issues"
DATA_TEST_SUITE = REPO_ROOT / "data" / "test-suite"

# Mapping from issue section to output folder (knowledge-finding path).
PATH_CONFIG = {
    "A": {
        "path_name": "External search",
        "data_subdir": "external-search",
        "title_hint": "External Search",
    },
    "B": {
        "path_name": "Internal search",
        "data_subdir": "internal-search",
        "title_hint": "Internal Search",
    },
    "C": {
        "path_name": "Docs assistant",
        "data_subdir": "docs-assistant",
        "title_hint": "MCP",
    },
    "D": {
        "path_name": "External LLMs",
        "data_subdir": "external-llms",
        "title_hint": "External LLMs",
    },
}

VALID_STYLES = {"naive", "familiar", "expert"}


def extract_issue_id(content: str) -> str | None:
    patterns = [
        r"-\s*\*\*Issue ID:\*\*\s*(.+?)(?:\n|$)",
        r"\*\*[Ii]ssue [Ii][Dd]\*\*\s*\|\s*(.+?)\s*\|",
        r"\|\s*\*\*issue_id\*\*\s*\|\s*(.+?)\s*\|",
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def extract_query_block(content: str, query_type: str, title_hint: str) -> str | None:
    pattern = rf"##\s+Query Type {query_type}:\s*{re.escape(title_hint)}.*?\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)

    # Alternate format used in issue files: "### A - External search (Google)"
    pattern_alt = rf"###\s+{query_type}\s*[\u2014\u2013-]\s*{re.escape(title_hint)}.*?\n(.*?)(?=\n###|\n##|\Z)"
    match = re.search(pattern_alt, content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)

    # Fallback to query type only in case section label changes slightly.
    pattern_fallback = rf"(?:##\s+Query Type {query_type}:|###\s+{query_type}\s*[\u2014\u2013-]).*?\n(.*?)(?=\n###|\n##|\Z)"
    match = re.search(pattern_fallback, content, re.DOTALL | re.IGNORECASE)
    return match.group(1) if match else None


def extract_queries_from_block(block: str) -> list[dict]:
    """Extract only valid localized query objects with locale/style/query."""
    # Prefer JSON array when available.
    json_match = re.search(r"```json\s*(\[[\s\S]*?\])\s*```", block, re.IGNORECASE)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            if isinstance(data, list):
                cleaned = []
                for item in data:
                    if not isinstance(item, dict):
                        continue

                    query = str(item.get("query", "")).strip()
                    style = str(item.get("style", "")).strip().lower()
                    locale = str(item.get("locale", "")).strip().lower()

                    if query and locale and style in VALID_STYLES:
                        cleaned.append({"locale": locale, "style": style, "query": query})
                if cleaned:
                    return cleaned
        except json.JSONDecodeError:
            pass

    # Fallback: parse localized markdown table rows (locale | style | query).
    localized_rows = re.finditer(
        r"\|\s*([a-z]{2})\s*\|\s*\*?\*?(naive|familiar|expert)\*?\*?\s*\|\s*(.+?)\s*\|",
        block,
        re.IGNORECASE,
    )

    queries = []
    for row in localized_rows:
        queries.append(
            {
                "locale": row.group(1).lower(),
                "style": row.group(2).lower(),
                "query": row.group(3).strip(),
            }
        )
    return queries


def build_path_payload(path_name: str, generated_from: Path) -> dict:
    try:
        display_path = str(generated_from.relative_to(REPO_ROOT))
    except ValueError:
        display_path = str(generated_from)
    return {
        "path": path_name,
        "generated_from": display_path,
        "total_issues": 0,
        "total_queries": 0,
        "issues": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate path JSON query files from issue docs.")
    parser.add_argument("--issues-dir", type=Path, default=ISSUES_DIR, help="Issues directory path.")
    parser.add_argument("--filename", default="all_queries.json", help="Output JSON filename for each path folder.")
    args = parser.parse_args()

    issues_dir = args.issues_dir.resolve()
    issue_files = sorted(issues_dir.glob("*.md"))

    payloads = {
        section: build_path_payload(conf["path_name"], issues_dir)
        for section, conf in PATH_CONFIG.items()
    }

    for issue_file in issue_files:
        content = issue_file.read_text(encoding="utf-8")
        issue_id = extract_issue_id(content)
        if not issue_id:
            continue

        for section, conf in PATH_CONFIG.items():
            block = extract_query_block(content, section, conf["title_hint"])
            if not block:
                continue

            queries = extract_queries_from_block(block)
            if not queries:
                continue

            payloads[section]["issues"].append(
                {
                    "issue_id": issue_id,
                    "source_file": issue_file.name,
                    "queries": queries,
                }
            )

    for section, conf in PATH_CONFIG.items():
        payload = payloads[section]
        payload["total_issues"] = len(payload["issues"])
        payload["total_queries"] = sum(len(issue["queries"]) for issue in payload["issues"])

        output_dir = DATA_TEST_SUITE / conf["data_subdir"]
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / args.filename
        output_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote: {output_file}")


if __name__ == "__main__":
    main()

