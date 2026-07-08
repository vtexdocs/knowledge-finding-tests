---
name: batch-status
description: >-
  Reports scoring progress across quality-review batches created by the
  generate-review-tool skill. Use when the user asks for batch status, review
  progress, how many items are scored, or who still needs to review their batch.
disable-model-invocation: true
---

# Batch Status

Report scoring progress across review batches created by the `generate-review-tool` skill in batch mode. Shows per-batch and overall completion so coordinators can see what work remains and who is responsible for it.

## Input

1. **Manifest** (optional — auto-detects if omitted)
   - `--manifest "path/to/batches_manifest.json"` — use a specific manifest
   - If omitted: automatically detects the latest `quality-scoring-*/batches_manifest.json`

## Actions

1. Locate `batches_manifest.json` (explicit path or auto-detected).
2. For each batch, read its data file and count items with a `human_score`.
3. Classify each batch:
   - **COMPLETE** — all items scored
   - **IN PROGRESS** — some items scored
   - **PENDING** — no items scored
   - **MISSING** — batch data file not found
4. Print a status table and overall progress percentage.

## Usage

Run the underlying script directly:

```bash
# Auto-detect latest manifest
python tools/quality-scoring/batch_status.py

# Specific manifest
python tools/quality-scoring/batch_status.py --manifest "results/.../quality-scoring-2026-06-15T15-30-00Z/batches_manifest.json"
```

## Example output

```
============================================================
BATCH STATUS REPORT
============================================================
Batch 1/3 (Alice)               :   2/2   items ✓ COMPLETE
Batch 2/3 (Bob)                 :   0/2   items ⏸ PENDING
Batch 3/3 (Charlie)             :   0/1   items ⏸ PENDING
------------------------------------------------------------
Overall Progress                :   2/5   items (40%)
============================================================
```

## See also

- `generate-review-tool` skill — generate and launch review batches
- `merge-batches` skill — consolidate scored batches into one file
- Underlying script: `tools/quality-scoring/batch_status.py`
