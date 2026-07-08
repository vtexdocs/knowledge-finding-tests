---
name: merge-batches
description: >-
  Consolidates scored quality-review batches back into a run's
  sampled_for_review.json, validating for duplicate or missing items. Use when
  the user asks to merge, combine, or consolidate review batches before
  generating a quality report.
disable-model-invocation: true
---

# Merge Batches

Consolidate scored review batches (created by the `generate-review-tool` skill in batch mode) back into the run's existing `sampled_for_review.json`, ready for report generation. Validates that no items are duplicated or missing and warns about incomplete scoring.

## Input

1. **Manifest** (optional — auto-detects if omitted)
   - `--manifest "path/to/batches_manifest.json"` — use a specific manifest
   - If omitted: automatically detects the latest `quality-scoring-*/batches_manifest.json`

2. **Output** (optional)
   - `--output "path/to/output.json"` — custom output path
   - If omitted: writes back to the run's existing `sampled_for_review.json` next to the manifest

## Actions

1. Locate `batches_manifest.json` (explicit path or auto-detected).
2. Load every batch data file referenced in the manifest.
3. Merge all items into a single list, preserving `issue_id`, reviewer attribution, scores, and comments.
4. Validate:
   - **Duplicates** — skip and warn on repeated `issue_id` across batches.
   - **Missing files** — warn if a batch data file is absent.
   - **Incomplete scoring** — warn about items without a `human_score`.
   - **Count check** — compare merged count against the manifest's `total_items`.
5. Write the consolidated scores back into the run's `sampled_for_review.json` and print the suggested report command.

## Usage

```bash
# Auto-detect latest manifest, write back to its sampled_for_review.json
python tools/quality-scoring/merge_batches.py

# Specific manifest
python tools/quality-scoring/merge_batches.py --manifest "results/.../quality-scoring-2026-06-15T15-30-00Z/batches_manifest.json"
```

## Exit codes

- `0` — merge succeeded with no blocking issues.
- `2` — merge completed but found duplicates or missing batch files (review the warnings).
- `1` — could not read the manifest or no batches found.

## Next step

The updated `sampled_for_review.json` plugs directly into the report generator via `--run-dir` (use the `generate-quality-report` skill):

```bash
python tools/quality-scoring/generate_quality_report.py --run-dir "results/.../quality-scoring-2026-06-15T15-30-00Z"
```

## See also

- `generate-review-tool` skill — generate and launch review batches
- `batch-status` skill — track progress across review batches
- Underlying script: `tools/quality-scoring/merge_batches.py`
