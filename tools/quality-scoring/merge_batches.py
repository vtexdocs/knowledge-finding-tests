#!/usr/bin/env python3
"""
Consolidate scored review batches back into a single file.

Reads a batches_manifest.json (created by launch-review.py when batching is
enabled), loads every batch data file, and merges all items back into the
existing sampled_for_review.json (next to the manifest) so it is ready for the
existing report generation workflow (generate_quality_report.py).

Validation performed:
  - Detects duplicate (issue_id, style) entries across batches.
  - Warns about items missing a human_score (incomplete review).
  - Compares the merged item count against the manifest's total_items.

Usage:
    python merge_batches.py --manifest path/to/batches_manifest.json
    python merge_batches.py --manifest path/to/batches_manifest.json --output custom.json
    python merge_batches.py        (auto-detects latest batches_manifest.json)
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


def load_json(path: Path) -> Optional[Any]:
    """Load JSON from a file, returning None on failure."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def merge(manifest_file: Path, output_file: Optional[Path]) -> int:
    """Merge all batch data files into a single consolidated file."""
    manifest = load_json(manifest_file)
    if manifest is None:
        print(f"Error: Could not read manifest: {manifest_file}")
        return 1

    manifest_dir = manifest_file.parent
    batches = manifest.get('batches', [])

    if not batches:
        print("No batches found in manifest.")
        return 1

    merged: list[dict[str, Any]] = []
    seen_keys: set[tuple[Any, Any]] = set()
    duplicates: list[str] = []
    missing_files: list[str] = []
    unscored: list[str] = []

    for batch in batches:
        data_file = batch.get('data_file', '')
        path = manifest_dir / data_file
        items = load_json(path)

        if items is None:
            missing_files.append(data_file)
            continue

        for item in items:
            issue_id = item.get('issue_id')
            style = item.get('style', 'unknown')
            key = (issue_id, style)
            label = f"{issue_id} ({style})"
            if key in seen_keys:
                duplicates.append(label)
                continue
            seen_keys.add(key)
            if item.get('human_score') is None:
                unscored.append(label)
            merged.append(item)

    # Report validation findings.
    print("=" * 60)
    print("MERGE BATCHES")
    print("=" * 60)
    print(f"Manifest:       {manifest_file.resolve()}")
    print(f"Batches:        {len(batches)}")
    print(f"Merged items:   {len(merged)}")

    expected = manifest.get('total_items')
    if expected is not None and expected != len(merged):
        print(f"[WARNING] Expected {expected} items but merged {len(merged)}.")

    if missing_files:
        print(f"[WARNING] {len(missing_files)} batch data file(s) missing:")
        for f in missing_files:
            print(f"          - {f}")

    if duplicates:
        print(f"[WARNING] {len(duplicates)} duplicate (issue_id, style) entry(ies) skipped:")
        for d in duplicates:
            print(f"          - {d}")

    if unscored:
        print(f"[WARNING] {len(unscored)} item(s) have no human_score (incomplete):")
        for u in unscored:
            print(f"          - {u}")
    else:
        print("[OK] All merged items have a human_score.")

    # Determine output path. By default we write back into the run's existing
    # sampled_for_review.json (next to the manifest) rather than a separate file.
    if output_file is None:
        output_file = manifest_dir / "sampled_for_review.json"

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    print("-" * 60)
    print(f"[OK] Merged scores written back to: {output_file.resolve()}")
    print()
    print("Next step: generate the quality report, e.g.")
    print(
        "  python tools/quality-scoring/generate_quality_report.py \\\n"
        f"    --run-dir \"{manifest_dir}\""
    )
    print("=" * 60)

    # Non-zero exit if there are blocking issues (duplicates / missing files).
    if duplicates or missing_files:
        return 2
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consolidate scored review batches into a single file."
    )
    parser.add_argument(
        '--manifest',
        type=str,
        default=None,
        help='Path to batches_manifest.json (auto-detects latest if omitted)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output path (default: the run\'s existing sampled_for_review.json next to manifest)'
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

    output_file = Path(args.output) if args.output else None
    return merge(manifest_file, output_file)


if __name__ == '__main__':
    sys.exit(main())
