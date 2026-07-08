#!/usr/bin/env python3
"""
Report scoring progress across review batches.

Reads a batches_manifest.json (created by launch-review.py when batching is
enabled), inspects each batch's data file to count how many items have a
human_score, and prints a status table plus overall progress.

A batch is classified as:
  - COMPLETE    : all items scored
  - IN PROGRESS : some (but not all) items scored
  - PENDING     : no items scored

Usage:
    python batch_status.py --manifest path/to/batches_manifest.json
    python batch_status.py        (auto-detects latest batches_manifest.json)
"""

from __future__ import annotations

import sys
import io
import argparse
import json
from pathlib import Path
from typing import Any, Optional

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def find_latest_manifest() -> Optional[Path]:
    """Auto-detect the most recently modified batches_manifest.json under results/."""
    results_dir = Path('results')
    if not results_dir.exists():
        return None
    manifests = list(results_dir.glob('**/quality-scoring-*/batches_manifest.json'))
    if not manifests:
        return None
    return max(manifests, key=lambda p: p.stat().st_mtime)


def count_scored(items: list[dict[str, Any]]) -> int:
    """Count items that have a non-null human_score."""
    return sum(
        1 for item in items
        if item.get('human_score') is not None
    )


def load_batch_items(manifest_dir: Path, data_file: str) -> Optional[list[dict[str, Any]]]:
    """Load a batch data file relative to the manifest directory."""
    path = manifest_dir / data_file
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def classify(scored: int, total: int) -> str:
    """Classify batch status from scored/total counts."""
    if total == 0:
        return 'PENDING'
    if scored >= total:
        return 'COMPLETE'
    if scored == 0:
        return 'PENDING'
    return 'IN PROGRESS'


STATUS_ICON = {
    'COMPLETE': '✓',
    'IN PROGRESS': '⚠',
    'PENDING': '⏸',
}


def report(manifest_file: Path) -> int:
    """Print the batch status report. Returns an exit code."""
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error: Could not read manifest: {e}")
        return 1

    manifest_dir = manifest_file.parent
    batches = manifest.get('batches', [])

    if not batches:
        print("No batches found in manifest.")
        return 1

    overall_scored = 0
    overall_total = 0
    rows = []

    for batch in batches:
        batch_id = batch.get('batch_id')
        reviewer = batch.get('reviewer') or 'Unassigned'
        total_meta = batch.get('item_count', 0)

        items = load_batch_items(manifest_dir, batch.get('data_file', ''))
        if items is None:
            scored = 0
            total = total_meta
            status = 'MISSING'
        else:
            total = len(items)
            scored = count_scored(items)
            status = classify(scored, total)

        overall_scored += scored
        overall_total += total
        rows.append((batch_id, reviewer, scored, total, status))

    num_batches = len(batches)
    print("=" * 60)
    print("BATCH STATUS REPORT")
    print("=" * 60)

    for batch_id, reviewer, scored, total, status in rows:
        icon = STATUS_ICON.get(status, '?')
        label = f"Batch {batch_id}/{num_batches} ({reviewer})"
        print(f"{label:<32}: {scored:>3}/{total:<3} items {icon} {status}")

    print("-" * 60)
    pct = (overall_scored / overall_total * 100) if overall_total else 0
    print(f"{'Overall Progress':<32}: {overall_scored:>3}/{overall_total:<3} items ({pct:.0f}%)")
    print("=" * 60)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report scoring progress across review batches."
    )
    parser.add_argument(
        '--manifest',
        type=str,
        default=None,
        help='Path to batches_manifest.json (auto-detects latest if omitted)'
    )
    args = parser.parse_args()

    if args.manifest:
        manifest_file = Path(args.manifest)
    else:
        manifest_file = find_latest_manifest()

    if not manifest_file:
        print("Error: Could not find batches_manifest.json")
        print("Generate batches first with: python launch-review.py --batch-size N")
        return 1

    if not manifest_file.exists():
        print(f"Error: Manifest not found: {manifest_file}")
        return 1

    return report(manifest_file)


if __name__ == '__main__':
    sys.exit(main())
