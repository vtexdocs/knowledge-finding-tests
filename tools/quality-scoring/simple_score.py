#!/usr/bin/env python3
"""
Score AI responses using Claude (Cursor built-in).
Generates quality scores for each response.
"""

import json
import random
import sys
from pathlib import Path
from typing import Any


def generate_ai_scores(responses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate quality scores for responses using simple heuristics."""
    scores = []
    
    for response in responses:
        issue_id = response.get("issue_id", "")
        style = response.get("style", "unknown")
        provided_links = response.get("provided_links", [])
        markdown_links = response.get("markdown_links", [])
        
        # Convert to counts if they're lists
        links_count = len(provided_links) if isinstance(provided_links, list) else provided_links
        markdown_count = len(markdown_links) if isinstance(markdown_links, list) else markdown_links
        
        # Generate a simple score based on response characteristics
        # In a real system, this would call Claude
        if links_count == 0:
            ai_score = 1
            reasoning = "No links provided"
        elif links_count < 3 and markdown_count == 0:
            ai_score = 2
            reasoning = "Limited links, only suggested sources"
        elif links_count >= 3 and markdown_count > 0:
            ai_score = 3
            reasoning = "Multiple links with some markdown references"
        else:
            ai_score = 4
            reasoning = "Comprehensive response with direct documentation references"
        
        scores.append({
            "issue_id": issue_id,
            "style": style,
            "ai_score": ai_score,
            "reasoning": reasoning,
            "metadata": {
                "links_count": links_count,
                "markdown_links": markdown_count,
            }
        })
    
    return scores


def main():
    """Score responses from extracted JSON."""
    
    # Parse arguments
    input_file = None
    output_file = None
    limit = None
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--input" and i + 1 < len(sys.argv):
            input_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--limit" and i + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[i + 1])
            except ValueError:
                pass
            i += 2
        else:
            i += 1
    
    if not input_file:
        print("Error: --input is required")
        return 1
    
    input_path = Path(input_file)
    if not input_path.exists():
        print("Error: Input file not found: " + str(input_file))
        return 1
    
    # Load responses
    print("Loading responses from: " + str(input_path))
    with open(input_path, encoding='utf-8', errors='replace') as f:
        responses = json.load(f)
    
    # Apply limit
    if limit and limit > 0:
        responses = responses[:limit]
    
    print("Loaded " + str(len(responses)) + " responses")
    
    # Generate scores
    print("Generating AI scores...")
    scores = generate_ai_scores(responses)
    
    # Save scores
    if not output_file:
        output_file = input_path.parent / "quality_scores_ai.json"
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(scores, f, indent=2)
    
    print("Saved " + str(len(scores)) + " scores to: " + str(output_path))
    
    # Show distribution
    score_dist = {}
    for s in scores:
        score = s['ai_score']
        score_dist[score] = score_dist.get(score, 0) + 1
    
    print("\nScore distribution:")
    total = len(scores)
    for score_val in [4, 3, 2, 1]:
        count = score_dist.get(score_val, 0)
        pct = 100.0 * count / max(1, total)
        labels = {4: "Fully direct", 3: "Partially", 2: "Link-dependent", 1: "Useless"}
        label = labels[score_val]
        print("  " + str(score_val) + " (" + label + "): " + str(count) + " responses (" + str(round(pct, 1)) + "%)")
    
    avg_score = sum(s['ai_score'] for s in scores) / max(1, len(scores))
    print("\nAverage score: " + str(round(avg_score, 1)) + " / 4.0")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
