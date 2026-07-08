#!/usr/bin/env python3
"""
Extract AI responses from test results for quality scoring.

This script reads the markdown result files from test runners and extracts
the response text, links, and metadata needed for quality scoring.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def extract_docs_assistant_responses(
    run_dir: Path,
    issues_dir: Path = None,
) -> list[dict[str, Any]]:
    """
    Extract responses from Docs Assistant results (JSON or markdown).
    
    Args:
        run_dir: Path to docs-assistant run directory
        issues_dir: Path to issues metadata directory
    
    Returns:
        List of dicts with issue_id, response_text, links, etc.
    """
    if issues_dir is None:
        issues_dir = Path("docs/test-suite/issues")
    
    responses = []
    issue_metadata = {}
    
    # Load issue metadata
    if issues_dir.exists():
        for issue_file in issues_dir.glob("*.md"):
            issue_id = issue_file.stem
            metadata = _parse_issue_metadata(issue_file)
            issue_metadata[issue_id] = metadata
    
    # Try JSON format first
    json_file = None
    for f in run_dir.glob("*.json"):
        if "run" in f.name:
            json_file = f
            break
    
    if json_file:
        return _extract_from_json(json_file, issue_metadata)
    
    # Fall back to markdown format
    result_file = None
    for f in run_dir.glob("*.md"):
        if "analysis" in f.name:
            result_file = f
            break
    
    if not result_file:
        print(f"No analysis markdown found in {run_dir}")
        return responses
    
    # Parse markdown
    content = result_file.read_text(encoding="utf-8")
    
    # Split by issue sections
    issue_sections = re.split(r'\n### (?P<issue_id>[a-z0-9\-]+) — (?P<style>\w+)\n', content)
    
    # Process pairs (issue_id — style, content)
    for i in range(1, len(issue_sections), 2):
        issue_id = issue_sections[i].strip()
        style = issue_sections[i+1].strip()
        section_content = issue_sections[i+2] if i+2 < len(issue_sections) else ""
        
        # Extract query
        query_match = re.search(r'\*\*Query:\*\* (.+?)(?:\n|$)', section_content)
        query = query_match.group(1) if query_match else ""
        
        # Extract links section
        links = _extract_links_from_section(section_content)
        
        # Extract answer markdown
        answer_markdown = _extract_answer_markdown(section_content)
        
        if not answer_markdown or not links:
            continue
        
        # Get issue metadata
        meta = issue_metadata.get(issue_id, {})
        
        # Infer locale from URL (default to en)
        locale = _infer_locale_from_query(query)
        
        responses.append({
            "issue_id": issue_id,
            "locale": locale,
            "style": style,
            "query": query,
            "response_text": answer_markdown,
            "provided_links": links,
            "user_intent": meta.get("user_intent", ""),
            "expected_docs": meta.get("expected_docs", []),
            "other_helpful_docs": meta.get("other_helpful_docs", []),
            "path_variant": "docs-assistant.api",
            "link_sources": ["markdown", "suggested_sources"],
        })
    
    return responses


def extract_llm_responses(
    run_dir: Path,
    issues_dir: Path = None,
) -> list[dict[str, Any]]:
    """
    Extract responses from external LLM markdown results (ChatGPT, Gemini, etc.).
    
    Args:
        run_dir: Path to llm run directory (e.g., results/llm/chatgpt/...)
        issues_dir: Path to issues metadata directory
    
    Returns:
        List of dicts with issue_id, response_text, links, etc.
    """
    if issues_dir is None:
        issues_dir = Path("docs/test-suite/issues")
    
    responses = []
    issue_metadata = {}
    
    # Load issue metadata
    for issue_file in issues_dir.glob("*.md"):
        issue_id = issue_file.stem
        metadata = _parse_issue_metadata(issue_file)
        issue_metadata[issue_id] = metadata
    
    # Find markdown files (one per issue)
    for issue_file in run_dir.glob("*.md"):
        if issue_file.name.startswith("analysis-"):
            continue  # Skip summary files
        
        content = issue_file.read_text(encoding="utf-8")
        
        # Extract metadata block (YAML format: key: value lines starting with -)
        parsed_meta = {}
        yaml_match = re.search(
            r'## Metadata\n((?:- .*?\n)+)',
            content
        )
        
        if yaml_match:
            yaml_lines = yaml_match.group(1)
            for line in yaml_lines.split("\n"):
                if line.startswith("- "):
                    # Parse YAML format: - key: value
                    match = re.match(r'- (\w+):\s*`?([^`]+)`?', line)
                    if match:
                        key, value = match.groups()
                        parsed_meta[key.lower()] = value.strip('`')
        else:
            # Try table format as fallback
            metadata_match = re.search(
                r'(?:\|.*?\|\n)+',
                content
            )
            
            if not metadata_match:
                continue
            
            meta_lines = metadata_match.group(0).split("\n")
            for line in meta_lines:
                if "|" in line:
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 2:
                        key, value = parts[0], parts[1]
                        parsed_meta[key.lower()] = value
        
        # Extract the issue_id from metadata
        issue_id = parsed_meta.get("issue_id", issue_file.stem)
        # Clean up issue_id if it has extra formatting
        issue_id = issue_id.strip('`').strip()
        
        # Extract query style from metadata or filename
        style = parsed_meta.get("query_style", "expert").lower()

        # Extract prompt (the query sent to the LLM)
        prompt_match = re.search(
            r'## Prompt\n+(.*?)(?=\n## |\Z)',
            content,
            re.DOTALL,
        )
        query = prompt_match.group(1).strip() if prompt_match else ""
        
        # Extract response section
        response_match = re.search(
            r'## Response\n+(.*?)(?=\n## |\Z)',
            content,
            re.DOTALL
        )
        
        if not response_match:
            continue
        
        answer_text = response_match.group(1).strip()
        
        if not answer_text:
            continue
        
        # Extract URLs from "Extracted URLs" section first, then from response text
        urls = []
        
        # Try to get URLs from "Extracted URLs" section
        urls_match = re.search(
            r'## Extracted URLs\n((?:- https?://.*\n?)+)',
            content
        )
        
        if urls_match:
            urls_text = urls_match.group(1)
            urls = re.findall(r'https?://[^\s\n]+', urls_text)
        else:
            # Fallback: extract from response text
            urls = re.findall(
                r'https?://[^\s\)]+',
                answer_text
            )
        
        links = [
            {
                "url": url.rstrip('-'),  # Remove trailing dashes from markdown list items
                "title": urlparse(url.rstrip('-')).path.split("/")[-1] or urlparse(url.rstrip('-')).netloc
            }
            for url in urls
            if url.strip()
        ]
        
        # Get issue metadata
        issue_meta = issue_metadata.get(issue_id, {})
        
        # Detect locale from metadata or response
        locale = parsed_meta.get("query_locale", "en")
        
        # Determine LLM variant from directory
        llm_variant = _infer_llm_variant(run_dir)
        
        responses.append({
            "issue_id": issue_id,
            "locale": locale,
            "style": style,
            "query": query,
            "response_text": answer_text,
            "provided_links": links,
            "user_intent": issue_meta.get("user_intent", ""),
            "expected_docs": issue_meta.get("expected_docs", []),
            "other_helpful_docs": issue_meta.get("other_helpful_docs", []),
            "path_variant": f"llm.{llm_variant}",
        })
    
    return responses


def _extract_from_json(json_file: Path, issue_metadata: dict) -> list[dict[str, Any]]:
    """Extract responses from JSON format test results."""
    responses = []
    
    try:
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading JSON file {json_file}: {e}")
        return responses
    
    # Handle different JSON structures
    results = None
    if isinstance(data, dict) and "results" in data:
        results = data["results"]
    elif isinstance(data, list):
        results = data
    
    if not results:
        print(f"Could not find results in {json_file}")
        return responses
    
    for result in results:
        if not isinstance(result, dict):
            continue
        
        response_obj = {
            "issue_id": result.get("issue_id", ""),
            "locale": result.get("locale", "en"),
            "style": result.get("query_style", "unknown"),
            "query": result.get("query", ""),
            "response_text": result.get("answer_markdown", ""),
            "provided_links": [
                {"title": link.get("title", ""), "url": link.get("url", "")}
                for link in result.get("links", [])
                if link.get("url")
            ],
            "user_intent": "",
            "expected_docs": [],
            "other_helpful_docs": [],
            "path_variant": "docs-assistant.api",
            "link_sources": ["markdown", "suggested_sources"],
        }
        
        # Try to get metadata if available
        meta = issue_metadata.get(response_obj["issue_id"], {})
        response_obj["user_intent"] = meta.get("user_intent", "")
        response_obj["expected_docs"] = meta.get("expected_docs", [])
        response_obj["other_helpful_docs"] = meta.get("other_helpful_docs", [])
        
        responses.append(response_obj)
    
    return responses


def _parse_issue_metadata(issue_file: Path) -> dict[str, Any]:
    """Parse issue metadata from markdown file."""
    content = issue_file.read_text(encoding="utf-8")
    
    metadata = {
        "issue_id": issue_file.stem,
        "user_intent": "",
        "expected_docs": [],
        "other_helpful_docs": [],
        "persona": "",
        "product": "",
    }
    
    # Extract from markdown table at top
    table_lines = []
    for line in content.split("\n"):
        if line.startswith("|"):
            table_lines.append(line)
        elif table_lines:
            break
    
    for line in table_lines:
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 2:
            continue
        key = parts[0].lower().replace("*", "").strip()
        value = parts[1]
        if "user_intent" in key:
            metadata["user_intent"] = value
        elif key == "persona":
            metadata["persona"] = value
        elif key == "product":
            metadata["product"] = value
    
    # Extract arrays from JSON
    expected_match = re.search(r'"expected_docs"\s*:\s*(\[[^\]]+\])', content)
    if expected_match:
        try:
            metadata["expected_docs"] = json.loads(expected_match.group(1))
        except json.JSONDecodeError:
            pass
    
    helpful_match = re.search(r'"other_helpful_docs"\s*:\s*(\[[^\]]+\])', content)
    if helpful_match:
        try:
            metadata["other_helpful_docs"] = json.loads(helpful_match.group(1))
        except json.JSONDecodeError:
            pass
    
    return metadata


def _extract_links_from_section(section: str) -> list[dict[str, str]]:
    """Extract links table from a section."""
    links = []
    
    # Find links table
    links_match = re.search(
        r'#### Links\n\n\|\s*#\s*\|.*?\n((?:\|.*?\n)+)',
        section
    )
    
    if not links_match:
        return links
    
    table_body = links_match.group(1)
    
    for line in table_body.split("\n"):
        if not line.strip() or "---" in line:
            continue
        
        parts = [p.strip() for p in line.split("|") if p.strip()]
        
        if len(parts) >= 3:
            # Format: | # | Title | URL | Context |
            title = parts[1] if len(parts) > 1 else ""
            url = parts[2] if len(parts) > 2 else ""
            
            if url.startswith("http"):
                links.append({"title": title, "url": url})
    
    return links


def _extract_answer_markdown(section: str) -> str:
    """Extract the answer markdown text from a section."""
    # Find "Answer markdown" section
    answer_match = re.search(
        r'#### Answer markdown\n\n(.*?)(?:\n###|$)',
        section,
        re.DOTALL
    )
    
    if answer_match:
        text = answer_match.group(1).strip()
        # Remove language/confidence line
        text = re.sub(r'\n\*Language:.*?\*\n?$', '', text)
        return text
    
    return ""


def _infer_locale_from_query(query: str) -> str:
    """Infer locale from query or default to 'en'."""
    # This is a simple heuristic
    if "português" in query.lower() or "pt/" in query:
        return "pt"
    elif "español" in query.lower() or "es/" in query:
        return "es"
    return "en"


def _infer_llm_variant(run_dir: Path) -> str:
    """Infer LLM variant from directory path."""
    dir_parts = run_dir.parts
    
    if "chatgpt" in str(run_dir).lower():
        return "chatgpt"
    elif "gemini" in str(run_dir).lower():
        return "gemini"
    elif "claude" in str(run_dir).lower():
        return "claude"
    
    # Try to extract from directory name
    for part in dir_parts:
        part_lower = part.lower()
        if part_lower in ["chatgpt", "gemini", "claude", "gpt", "openai"]:
            return part_lower
    
    return "unknown"


def main():
    """CLI for extracting responses."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract AI responses for quality scoring")
    parser.add_argument("--run-dir", type=Path, required=True, help="Test run directory")
    parser.add_argument("--output", type=Path, default=None, help="Output JSON file (default: {run-dir}/quality-scoring/responses_for_scoring.json)")
    parser.add_argument("--issues-dir", type=Path, default=Path("docs/test-suite/issues"), help="Issues directory")
    parser.add_argument("--type", choices=["docs-assistant", "llm", "auto"], default="auto", help="Run type")
    parser.add_argument("--versioned", action="store_true", help="Use timestamped output directories (quality-scoring-YYYY-MM-DDTHH-MM-SSZ/)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of responses to extract")
    
    args = parser.parse_args()
    
    if not args.run_dir.exists():
        print(f"Error: {args.run_dir} does not exist")
        sys.exit(1)
    
    # Create output directory if not specified
    if args.output is None:
        if args.versioned:
            # Create timestamped directory
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            timestamp = now.strftime("%Y-%m-%dT%H-%M-%SZ")
            output_dir = args.run_dir / f"quality-scoring-{timestamp}"
        else:
            output_dir = args.run_dir / "quality-scoring"
        output_dir.mkdir(parents=True, exist_ok=True)
        args.output = output_dir / "responses_for_scoring.json"
    else:
        # Ensure parent directory exists
        args.output.parent.mkdir(parents=True, exist_ok=True)
    
    run_type = args.type
    if run_type == "auto":
        if "docs-assistant" in str(args.run_dir):
            run_type = "docs-assistant"
        elif "llm" in str(args.run_dir):
            run_type = "llm"
        else:
            print("Error: Could not auto-detect run type. Use --type explicitly")
            sys.exit(1)
    
    print(f"Extracting responses from {args.run_dir} ({run_type})")
    
    if run_type == "docs-assistant":
        responses = extract_docs_assistant_responses(args.run_dir, args.issues_dir)
    else:
        responses = extract_llm_responses(args.run_dir, args.issues_dir)
    
    # Apply limit if specified
    if args.limit and args.limit > 0:
        responses = responses[:args.limit]
        print(f"Applied limit: using first {len(responses)} responses")
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(responses, f, indent=2, ensure_ascii=False)
    
    print("[OK] Extracted {} responses".format(len(responses)))
    print("[OK] Saved to {}".format(args.output))
    if args.versioned:
        print("[OK] Versioned output directory: {}".format(args.output.parent))


if __name__ == "__main__":
    main()
