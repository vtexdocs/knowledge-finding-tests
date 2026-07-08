#!/usr/bin/env python3
"""
Sample responses for human review using smart strategy.

This module implements intelligent sampling:
- 50% random selection (diverse coverage)
- 50% lowest AI scores (quality verification)

All style variants (naive, familiar, expert) of the same issue are kept —
deduplication is only performed on exact (issue_id, style) pairs to prevent
the identical response from appearing twice. When the random and low-score
pools overlap, remaining candidates are backfilled (lowest scores first)
until the sample reaches the full target (e.g. 10% of all scored entries).

The sampled items include all necessary fields for the HTML review tool,
including full response text and links.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any


def _item_key(item: dict[str, Any]) -> tuple[Any, Any]:
    return (item.get("issue_id"), item.get("style"))


def _prepare_sample_item(item: dict[str, Any]) -> dict[str, Any]:
    """Ensure fields required by the review tool are present."""
    item["human_score"] = None
    item["human_notes"] = None

    if "response_text" not in item:
        item["response_text"] = item.get("answer", item.get("markdown_content", ""))

    if "links_found" not in item:
        links = item.get("provided_links", item.get("markdown_links", []))
        if links and isinstance(links, list):
            if isinstance(links[0], str):
                item["links_found"] = [
                    {"url": url, "title": url.split("/")[-1] or url.split("/")[-2]}
                    for url in links
                ]
            else:
                item["links_found"] = links
        else:
            item["links_found"] = []

    return item


def sample_responses_for_review(
    scores_file: Path,
    sample_percent: float = 10,
    output_file: Path | None = None,
    random_seed: int | None = None,
) -> tuple[list[dict[str, Any]], Path]:
    """
    Sample responses for human review using combined strategy.
    
    Strategy: 50% random + 50% lowest-scoring items
    This balances representative sampling with targeted QA verification.
    
    Args:
        scores_file: Path to quality_scores_ai.json (or similar)
        sample_percent: Percentage of items to sample (default: 10)
        output_file: Where to save sampled_for_review.json (default: auto)
        random_seed: Optional seed for reproducible sampling
    
    Returns:
        Tuple of (sampled_items, output_path)
    
    Raises:
        FileNotFoundError: If scores_file doesn't exist
        ValueError: If sample_percent is invalid
        json.JSONDecodeError: If JSON is malformed
    """
    if not scores_file.exists():
        raise FileNotFoundError(f"Scores file not found: {scores_file}")
    
    if not 0 < sample_percent <= 100:
        raise ValueError(f"sample_percent must be 0-100, got {sample_percent}")
    
    # Load all scores
    with open(scores_file) as f:
        all_scores = json.load(f)
    
    if not all_scores:
        raise ValueError("Scores file is empty")
    
    total_count = len(all_scores)
    sample_size = max(1, int(total_count * sample_percent / 100))
    
    # Set random seed for reproducibility
    if random_seed is not None:
        random.seed(random_seed)
    
    # Split into two groups: random and low-scoring
    random_count = sample_size // 2
    low_score_count = sample_size - random_count
    
    # Random selection
    random_sample = random.sample(all_scores, min(random_count, total_count))
    
    # Low-scoring selection (sorted by ai_score, lowest first)
    if low_score_count > 0:
        sorted_by_score = sorted(
            all_scores,
            key=lambda x: x.get("ai_score", 4)
        )
        low_sample = sorted_by_score[:low_score_count]
    else:
        low_sample = []
    
    # Combine random and low-scoring selections, then deduplicate by (issue_id, style)
    # to avoid the exact same response appearing twice while keeping all style variants.
    sampled = random_sample + low_sample
    seen: set[tuple[Any, Any]] = set()
    unique_sampled: list[dict[str, Any]] = []

    for item in sampled:
        key = _item_key(item)
        if key not in seen:
            seen.add(key)
            unique_sampled.append(_prepare_sample_item(item))

    # Overlap between the two pools can shrink the sample below the target.
    # Backfill from remaining entries, preferring lowest scores first.
    if len(unique_sampled) < sample_size:
        remaining = [
            item for item in all_scores if _item_key(item) not in seen
        ]
        remaining.sort(key=lambda x: x.get("ai_score", 4))
        for item in remaining:
            if len(unique_sampled) >= sample_size:
                break
            key = _item_key(item)
            seen.add(key)
            unique_sampled.append(_prepare_sample_item(item))

    unique_sampled = unique_sampled[:sample_size]
    
    # Determine output file
    if output_file is None:
        output_file = scores_file.parent / "sampled_for_review.json"
    
    # Save sampled responses
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(unique_sampled, f, indent=2)
    
    return unique_sampled, output_file


def main():
    """Command-line interface for sampling."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sample responses for human review"
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to quality_scores_ai.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file (default: sampled_for_review.json)",
    )
    parser.add_argument(
        "--percent",
        type=float,
        default=10,
        help="Percentage to sample (default: 10)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )
    
    args = parser.parse_args()
    
    try:
        sampled, output_path = sample_responses_for_review(
            scores_file=args.input,
            sample_percent=args.percent,
            output_file=args.output,
            random_seed=args.seed,
        )
        
        print(f"[OK] Sampled {len(sampled)} items from {args.input}")
        print(f"[OK] Strategy: 50% random + 50% lowest-scoring")
        print(f"[OK] Saved to: {output_path}")
        
    except Exception as e:
        print(f"Error: {e}", file=__import__("sys").stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
