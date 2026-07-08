# Generate Review Tool — reference

Detailed material for the `generate-review-tool` skill: batch mode, error handling, examples, workflow integration, and server internals.

## Batch mode (distributed human scoring)

For large reviews, split the work across multiple reviewers so each scores their portion independently and in parallel.

### How it works

1. **Generate batches** — splits `sampled_for_review.json` into per-batch subdirectories, each with its own data file and HTML interface, plus a `batches_manifest.json` that tracks assignments and progress.

```bash
# Batches of 10 items each, assigned to reviewers in order
python tools/quality-scoring/launch-review.py --input "<sampled_for_review.json>" --batch-size 10 --port 8001 --reviewer Alice --reviewer Bob

# Or split into a fixed number of equal batches
python tools/quality-scoring/launch-review.py --input "<sampled_for_review.json>" --num-batches 5 --port 8001
```

This creates:
```
quality-scoring-YYYY-MM-DDTHH-MM-SSZ/
  batches_manifest.json
  batch-1/
    sampled_for_review_batch_1.json
    review_batch_1.html
  batch-2/
    ...
```

2. **Launch a batch for review** — each reviewer launches their batch on a distinct port. The UI header shows "Batch X of N" and the reviewer name. Scores auto-save to that batch's data file.

```bash
python tools/quality-scoring/launch-review.py --batch-id 1 --port 8001   # Alice
python tools/quality-scoring/launch-review.py --batch-id 2 --port 8002   # Bob
```

3. **Track progress** — use the `batch-status` skill:

```bash
python tools/quality-scoring/batch_status.py
```

4. **Consolidate results** — use the `merge-batches` skill; merged scores are written back into `sampled_for_review.json`:

```bash
python tools/quality-scoring/merge_batches.py
```

5. **Generate the report** — use the `generate-quality-report` skill:

```bash
python tools/quality-scoring/generate_quality_report.py --run-dir "results/.../quality-scoring-YYYY-MM-DDTHH-MM-SSZ"
```

### Notes

- Number of batches is always required — use `--num-batches 1` for a single reviewer.
- Item assignment is sequential, so no item is duplicated or omitted by default.
- Each batch is self-contained: full query, response text, links, AI reference, and scoring UI.

## Output — what the interface provides

- Displays all sampled items; shows full query, response text, and provided links.
- Radio-button scoring (1–4) with an optional notes field per item.
- Previous/Next navigation and a progress indicator.
- Buttons: **Export Data** (saves scores + notes to `sampled_for_review.json`), **Download Progress** (JSON backup), **Save & Next**.

On **Export Data**, the browser POSTs to `/export-data`; the server writes to `sampled_for_review.json` and confirms.

## Error handling

- **`--input` not provided:** ask for the full path to `sampled_for_review.json`.
- **`--num-batches` not provided:** ask how many batches (1 for a single reviewer).
- **`--port` not provided:** ask which port (e.g. 8000; a different one if in use or for parallel servers).
- **Input file not found:** report the path and ask again.
- **Server fails to start:** ensure `tools/quality-scoring/review-server.py` exists.

## Workflow integration

```
quality-scoring-workflow  → (Steps 1–4, creates timestamped quality-scoring-*/, pauses at Step 5)
generate-review-tool      → ask path / batches / port → generate HTML → launch server → user scores (auto-save) → Ctrl+C
generate-quality-report   → --run-dir "quality-scoring-YYYY-MM-DDTHH-MM-SSZ"
```

## Tips

- Always provide `--input`, `--num-batches`, and `--port` (no auto-detect / defaults).
- Click "Export Data" before refreshing or closing the browser; server-side save is primary, localStorage is backup.
- Use distinct ports for parallel batch servers (e.g. 8001, 8002, 8003).
- The notes field is optional but useful for flagging unclear responses.

## Server technical details

### How Export Data works
1. User selects a score (1–4) and optionally adds notes.
2. User clicks "Export Data".
3. JavaScript POSTs to `http://localhost:<port>/export-data`.
4. Server writes to `sampled_for_review.json` and shows a confirmation.

### Port configuration
- Always specified by the user — no default.
- Use distinct ports for parallel batch servers.
- Server stops on Ctrl+C.

### Browser compatibility
Chrome/Chromium (recommended), Firefox, Safari, Edge — any modern browser with JavaScript enabled.
