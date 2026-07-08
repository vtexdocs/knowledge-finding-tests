---
name: generate-review-tool
description: >-
  Launches the interactive HTML quality-review tool with a local auto-saving
  server, optionally splitting the sample into per-reviewer batches. Use when
  the user asks to review AI responses, open the human-scoring interface, start
  the review server, or split reviews across reviewers.
disable-model-invocation: true
---

# Generate Review Tool

Launch an interactive HTML review tool with automatic score saving. Generates the review HTML interface, starts a local server with auto-save, and opens the browser for interactive review. Scores save to disk as you review (no download/upload needed). Uses Cursor's built-in Claude — zero API cost.

## Always ask before acting

**Do NOT** auto-detect `sampled_for_review.json`, assume a batch count, or assume a port. Ask for all three inputs and validate them before proceeding.

Ask immediately:
1. Path to `sampled_for_review.json` (e.g. `results/.../quality-scoring-2026-06-23T12-52-44Z/sampled_for_review.json`).
2. How many batches (enter `1` for a single reviewer, or higher to distribute).
3. Which port (e.g. `8000`; use a different port if in use or for parallel batch servers).

Wait for all three answers before doing anything.

## Input

1. **Responses source** (REQUIRED — no auto-detect): `--input "path/to/sampled_for_review.json"`.
2. **Number of batches** (REQUIRED — no default): `--num-batches N` (use 1 for a single reviewer) or `--batch-size N`.
3. **Port** (REQUIRED — no default): `--port N`.
4. **Optional:** `--reviewer NAME` (repeat in order per batch); `--batch-id N` (launch the server for a specific, already-generated batch).

## Actions

1. **Collect and validate inputs** — ask for `--input`, `--num-batches` (or `--batch-size`), and `--port` if not provided; verify the file exists and is valid JSON; do not proceed until all three are confirmed.
2. **Generate HTML review tool (if needed)** — if `review.html` is missing in the directory, run `generate_review_html.py` to create it (embeds all response data for offline use).
3. **Start local review server** — launch `review-server.py` with the sampled file and HTML; serves at `http://localhost:<port>`; opens the browser; handles `POST /export-data` to save scores.
4. **Auto-save scores** — as the user scores in the browser, the server writes to `sampled_for_review.json`; scores persist on disk after the browser closes.
5. **Continue workflow** — when done (Ctrl+C to stop the server), run the `generate-quality-report` skill to produce `QUALITY_REPORT.md`.

## Usage

Single reviewer:

```bash
python tools/quality-scoring/launch-review.py \
  --input "results/.../quality-scoring-2026-06-23T12-52-44Z/sampled_for_review.json" \
  --num-batches 1 \
  --port 8000
```

Stop the server with Ctrl+C when done, then run:

```bash
python tools/quality-scoring/generate_quality_report.py --run-dir "results/.../quality-scoring-2026-06-23T12-52-44Z"
```

## Scoring scale (shown in the HTML)

Assume the user will not click links; score how well the text alone solves the task. Full rubric: `docs/quality-scoring/quality-scoring.md#scoring-scale-1-4`.

| Score | Label | One-line definition |
|-------|-------|---------------------|
| **1** | Useless | Wrong/off-topic/misleading, or links don't help |
| **2** | Link-dependent | Text is navigation only; answer lives behind links |
| **3** | Partially direct | Text correct but a required step/value needs a link |
| **4** | Fully direct | Text alone fully solves the problem; links optional |

## Batch mode, examples, and server details

For distributed multi-reviewer scoring, error messages, workflow integration, and server technical details, see [reference.md](reference.md).

## See also

- `quality-scoring-workflow` skill — complete automated pipeline
- `generate-quality-report` skill — merge scores & generate the report
- `batch-status` skill — track progress across review batches
- `merge-batches` skill — consolidate scored batches into one file
- Scripts: `tools/quality-scoring/launch-review.py`, `review-server.py`, `generate_review_html.py`
