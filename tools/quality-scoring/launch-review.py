#!/usr/bin/env python3
"""
Automated launcher for the quality review tool with auto-save functionality.

This script automatically detects the latest timestamped sampled_for_review.json file,
generates the review HTML if needed, starts a local review server with auto-save,
and opens the browser for interactive review.

Workflow integration:
  - Automatically finds latest quality-scoring-YYYY-MM-DDTHH-MM-SSZ/ directory
  - Works with any sampled_for_review.json from the workflow
  - Generates HTML review tool if missing
  - Starts review server with auto-save to sampled_for_review.json
  - Opens browser automatically
  - Stops when user presses Ctrl+C

Usage:
    python launch-review.py [--input PATH]
    
Optional args:
    --input PATH    Specify exact path to sampled_for_review.json
                    If omitted, auto-detects latest timestamped directory
"""

from __future__ import annotations

import sys
import io
import argparse
import subprocess
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def find_latest_sampled_file() -> Optional[Path]:
    """
    Auto-detect the latest timestamped sampled_for_review.json in results/ directory.
    
    Looks for: results/**/quality-scoring-YYYY-MM-DDTHH-MM-SSZ/sampled_for_review.json
    Returns the most recently modified timestamped directory.
    """
    results_dir = Path('results')
    
    if not results_dir.exists():
        return None
    
    # Find all sampled_for_review.json files in timestamped directories
    sampled_files = list(results_dir.glob('**/quality-scoring-*/sampled_for_review.json'))
    
    if not sampled_files:
        return None
    
    # Return the most recently modified one
    return max(sampled_files, key=lambda p: p.stat().st_mtime)


def get_output_dir(sampled_file: Path) -> Path:
    """Get the timestamped output directory containing the sampled file."""
    return sampled_file.parent


def split_into_batches(
    items: list,
    batch_size: Optional[int] = None,
    num_batches: Optional[int] = None,
) -> list[list]:
    """
    Split a list of items into batches using sequential assignment.

    Exactly one of batch_size or num_batches should be provided. If both are
    given, batch_size takes precedence. Items are assigned sequentially so no
    item is duplicated or omitted.

    Args:
        items: Full list of review items.
        batch_size: Number of items per batch.
        num_batches: Total number of batches to produce (items split as evenly as possible).

    Returns:
        A list of batches, where each batch is a list of items.
    """
    total = len(items)
    if total == 0:
        return []

    if batch_size is not None:
        size = max(1, batch_size)
        batches = [items[i:i + size] for i in range(0, total, size)]
        return batches
    elif num_batches is not None:
        count = max(1, num_batches)
        # Distribute items as evenly as possible
        # For 13 items and 4 batches: base_size=3, remainder=1
        # Results in: [4, 3, 3, 3] (first batch gets the extra item)
        base_size = total // count  # Integer division
        remainder = total % count   # Items that don't divide evenly
        
        batches = []
        start_idx = 0
        for i in range(count):
            # First 'remainder' batches get one extra item
            batch_size_for_this = base_size + (1 if i < remainder else 0)
            end_idx = start_idx + batch_size_for_this
            batches.append(items[start_idx:end_idx])
            start_idx = end_idx
        
        return batches
    else:
        # No batching requested: single batch containing everything.
        return [items]


def write_batches(
    sampled_file: Path,
    batches: list[list],
    reviewers: Optional[list[str]] = None,
    batch_size: Optional[int] = None,
) -> Path:
    """
    Write each batch to its own subdirectory and create a manifest file.

    Layout (relative to the sampled file's directory):
        batch-1/sampled_for_review_batch_1.json
        batch-2/sampled_for_review_batch_2.json
        ...
        batches_manifest.json

    Args:
        sampled_file: Path to the original sampled_for_review.json.
        batches: List of batches (each a list of items).
        reviewers: Optional list of reviewer names, indexed by batch position.
        batch_size: The configured batch size (for the manifest, if any).

    Returns:
        Path to the generated batches_manifest.json.
    """
    output_dir = get_output_dir(sampled_file)
    total_items = sum(len(b) for b in batches)
    num_batches = len(batches)

    manifest_batches = []

    for idx, batch in enumerate(batches, start=1):
        batch_dir = output_dir / f"batch-{idx}"
        batch_dir.mkdir(parents=True, exist_ok=True)

        data_file = batch_dir / f"sampled_for_review_batch_{idx}.json"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(batch, f, indent=2, ensure_ascii=False)

        reviewer = None
        if reviewers and idx - 1 < len(reviewers):
            reviewer = reviewers[idx - 1]

        manifest_batches.append({
            "batch_id": idx,
            "reviewer": reviewer,
            "items": [item.get("issue_id") for item in batch],
            "status": "pending",
            "html_file": f"batch-{idx}/review_batch_{idx}.html",
            "data_file": f"batch-{idx}/sampled_for_review_batch_{idx}.json",
            "item_count": len(batch),
        })

    manifest = {
        "total_items": total_items,
        "batch_size": batch_size,
        "num_batches": num_batches,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_file": str(sampled_file.resolve()),
        "batches": manifest_batches,
    }

    manifest_file = output_dir / "batches_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return manifest_file


def generate_batch_html(
    batch_data_file: Path,
    batch_id: int,
    total_batches: int,
    reviewer: Optional[str] = None,
) -> Optional[Path]:
    """
    Generate the review HTML for a single batch using generate_review_html.py.

    Returns the path to the generated HTML file, or None on failure.
    """
    html_file = batch_data_file.parent / f"review_batch_{batch_id}.html"
    generator_script = Path('tools/quality-scoring/generate_review_html.py')

    if not generator_script.exists():
        print(f"Error: {generator_script} not found")
        return None

    cmd = [
        sys.executable,
        str(generator_script),
        '--input', str(batch_data_file),
        '--output', str(html_file),
        '--batch-id', str(batch_id),
        '--total-batches', str(total_batches),
    ]
    if reviewer:
        cmd += ['--reviewer', reviewer]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            print(f"Error generating batch HTML: {result.stderr}")
            return None
        print(result.stdout)
    except Exception as e:
        print(f"Error running generator: {e}")
        return None

    if not html_file.exists():
        print(f"Error: Batch HTML file was not created at {html_file}")
        return None

    return html_file


def generate_html_if_needed(sampled_file: Path, force_regenerate: bool = False) -> Path:
    """
    Generate review.html with cache-busting strategy.
    
    Always regenerates HTML to ensure data freshness (prevents stale cache issues).
    This solves the caching problem where old review.html had embedded old data.
    
    Uses generate_review_html.py to create the HTML review tool.
    """
    output_dir = get_output_dir(sampled_file)
    html_file = output_dir / 'review.html'
    
    # CACHE-BUSTING: Always regenerate to ensure data is fresh
    # This prevents issues where review.html had old/cached data embedded
    if html_file.exists() and not force_regenerate:
        # Check if HTML is newer than sampled_file
        html_mtime = html_file.stat().st_mtime
        sampled_mtime = sampled_file.stat().st_mtime
        
        if html_mtime >= sampled_mtime:
            print("✓ Review tool is up-to-date (generated after last sampled_for_review.json edit)")
            return html_file
        else:
            print("⚠ Review tool is stale (sampled_for_review.json was edited after HTML generation)")
            print("  Regenerating to ensure data freshness...")
    else:
        print("Generating review HTML tool...")
    
    # Generate HTML using the existing script
    generator_script = Path('tools/quality-scoring/generate_review_html.py')
    
    if not generator_script.exists():
        print(f"Error: {generator_script} not found")
        return None
    
    cmd = [
        sys.executable,
        str(generator_script),
        '--input', str(sampled_file),
        '--output', str(html_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            print(f"Error generating HTML: {result.stderr}")
            return None
        print(result.stdout)
    except Exception as e:
        print(f"Error running generator: {e}")
        return None
    
    if not html_file.exists():
        print(f"Error: HTML file was not created at {html_file}")
        return None
    
    return html_file


def launch_review_server(sampled_file: Path, html_file: Path, port: int = 8000) -> int:
    """
    Launch the local review server with auto-save functionality.
    
    The server will:
    - Serve the review HTML at http://localhost:<port>
    - Auto-save scores to sampled_for_review.json when user scores items
    - Open browser automatically
    - Continue until user presses Ctrl+C
    """
    server_script = Path('tools/quality-scoring/review-server.py')
    
    if not server_script.exists():
        print(f"Error: {server_script} not found")
        return 1
    
    print("=" * 80)
    print("QUALITY SCORE REVIEW TOOL")
    print("=" * 80)
    print()
    print(f"Sampled file:  {sampled_file.resolve()}")
    print(f"Review tool:   {html_file.resolve()}")
    print(f"Port:          {port}")
    print()
    print("Starting review server with auto-save...")
    print()
    
    # Start the server
    # Use resolve() to get absolute paths and pass them properly
    cmd = [
        sys.executable,
        str(server_script),
        str(sampled_file.resolve()),
        str(html_file.resolve()),
        '--port', str(port),
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print()
        print("=" * 80)
        print("Review tool stopped.")
        print("=" * 80)
        return 0
    
    return 0


def generate_batches(
    sampled_file: Path,
    batch_size: Optional[int],
    num_batches: Optional[int],
    reviewers: Optional[list[str]],
) -> int:
    """
    Split the sampled file into batches, write batch files, and generate HTML
    for each batch. Does NOT launch any server (use --batch-id to review one).
    """
    try:
        with open(sampled_file, 'r', encoding='utf-8') as f:
            items = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error: Could not read sampled file: {e}")
        return 1

    if not items:
        print("Error: Sampled file is empty, nothing to batch.")
        return 1

    batches = split_into_batches(items, batch_size=batch_size, num_batches=num_batches)

    print("=" * 80)
    print("GENERATING REVIEW BATCHES")
    print("=" * 80)
    print()
    print(f"Source file:   {sampled_file.resolve()}")
    print(f"Total items:   {len(items)}")
    print(f"Batches:       {len(batches)}")
    print()

    manifest_file = write_batches(
        sampled_file, batches, reviewers=reviewers, batch_size=batch_size
    )

    total_batches = len(batches)
    for idx in range(1, total_batches + 1):
        batch_data_file = sampled_file.parent / f"batch-{idx}" / f"sampled_for_review_batch_{idx}.json"
        reviewer = reviewers[idx - 1] if reviewers and idx - 1 < len(reviewers) else None
        html_file = generate_batch_html(batch_data_file, idx, total_batches, reviewer)
        if html_file:
            reviewer_label = f" (Reviewer: {reviewer})" if reviewer else ""
            print(f"  [OK] Batch {idx}/{total_batches}{reviewer_label}: {html_file}")

    print()
    print(f"[OK] Manifest written: {manifest_file.resolve()}")
    print()
    print("Next steps:")
    print("  • Launch a specific batch for review:")
    print(f"      python launch-review.py --input \"{sampled_file}\" --batch-id 1 --port 8001")
    print("  • Check progress across all batches:")
    print(f"      python tools/quality-scoring/batch_status.py --manifest \"{manifest_file}\"")
    print("  • Merge completed batches:")
    print(f"      python tools/quality-scoring/merge_batches.py --manifest \"{manifest_file}\"")
    return 0


def launch_single_batch(sampled_file: Path, batch_id: int, port: int) -> int:
    """
    Launch the review server for a single, already-generated batch.

    Resolves the batch's data file and HTML file from the batch subdirectory,
    regenerating the HTML if it does not yet exist.
    """
    output_dir = get_output_dir(sampled_file)
    batch_dir = output_dir / f"batch-{batch_id}"
    batch_data_file = batch_dir / f"sampled_for_review_batch_{batch_id}.json"
    html_file = batch_dir / f"review_batch_{batch_id}.html"

    if not batch_data_file.exists():
        print(f"Error: Batch {batch_id} data file not found: {batch_data_file}")
        print("Generate batches first with --batch-size or --num-batches.")
        return 1

    total_batches = batch_id
    reviewer = None
    manifest_file = output_dir / "batches_manifest.json"
    if manifest_file.exists():
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            total_batches = manifest.get("num_batches", batch_id)
            for b in manifest.get("batches", []):
                if b.get("batch_id") == batch_id:
                    reviewer = b.get("reviewer")
                    break
        except (json.JSONDecodeError, IOError):
            pass

    if not html_file.exists():
        print(f"Batch {batch_id} HTML missing, regenerating...")
        regenerated = generate_batch_html(batch_data_file, batch_id, total_batches, reviewer)
        if not regenerated:
            return 1
        html_file = regenerated

    print("=" * 80)
    print(f"LAUNCHING REVIEW FOR BATCH {batch_id}/{total_batches}")
    if reviewer:
        print(f"Reviewer: {reviewer}")
    print("=" * 80)
    print()

    return launch_review_server(batch_data_file, html_file, port=port)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Launch interactive quality review tool with auto-save',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python launch-review.py
    (auto-detects latest sampled_for_review.json)
  
  python launch-review.py --input "results/path/quality-scoring-YYYY-MM-DDTHH-MM-SSZ/sampled_for_review.json"
    (use specific file)

  python launch-review.py --batch-size 10
    (split the review into batches of 10 items each)

  python launch-review.py --num-batches 5
    (split the review into 5 equal batches)

  python launch-review.py --batch-id 1 --port 8001
    (launch review server for batch 1 on port 8001)
        '''
    )
    
    parser.add_argument(
        '--input',
        type=str,
        default=None,
        help='Path to sampled_for_review.json (auto-detects if omitted)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=None,
        help='Split the review into batches of this many items each'
    )
    parser.add_argument(
        '--num-batches',
        type=int,
        default=None,
        help='Split the review into this many equal batches'
    )
    parser.add_argument(
        '--batch-id',
        type=int,
        default=None,
        help='Launch the review server for a specific (already generated) batch'
    )
    parser.add_argument(
        '--reviewer',
        type=str,
        action='append',
        default=None,
        help='Reviewer name for a batch (repeat for multiple batches, in order)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port for the review server (default: 8000)'
    )
    
    args = parser.parse_args()
    
    # Determine sampled_for_review.json path
    if args.input:
        sampled_file = Path(args.input)
    else:
        sampled_file = find_latest_sampled_file()
    
    if not sampled_file:
        print("Error: Could not find sampled_for_review.json")
        if not args.input:
            print()
            print("Auto-detection failed. Possible reasons:")
            print("  • No results/ directory found")
            print("  • No quality-scoring-YYYY-MM-DDTHH-MM-SSZ/ directories exist")
            print("  • No sampled_for_review.json files in timestamped directories")
            print()
            print("Use --input to specify the file path explicitly:")
            print("  python launch-review.py --input /path/to/sampled_for_review.json")
        return 1
    
    if not sampled_file.exists():
        print(f"Error: File not found: {sampled_file}")
        return 1

    # Mode 1: Launch a specific, already-generated batch.
    if args.batch_id is not None:
        return launch_single_batch(sampled_file, args.batch_id, args.port)

    # Mode 2: Generate batches (does not launch a server).
    if args.batch_size is not None or args.num_batches is not None:
        return generate_batches(
            sampled_file,
            batch_size=args.batch_size,
            num_batches=args.num_batches,
            reviewers=args.reviewer,
        )

    # Mode 3: Single-review (existing, backward-compatible behavior).
    print("=" * 80)
    print("AUTO-LAUNCHING QUALITY REVIEW TOOL")
    print("=" * 80)
    print()
    print(f"Found sampled file: {sampled_file.resolve()}")
    print()
    
    # Generate HTML if needed
    html_file = generate_html_if_needed(sampled_file)
    if not html_file:
        return 1
    
    print()
    
    # Launch review server
    return launch_review_server(sampled_file, html_file, port=args.port)


if __name__ == '__main__':
    sys.exit(main())
