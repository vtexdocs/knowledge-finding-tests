---
name: generate-quality-report
description: >-
  Generates the final quality report comparing AI scores to human review
  scores, with agreement metrics, calibration insights, and recommendations, for
  a given quality-scoring run directory. Use when the user asks to generate the
  quality report, compare AI vs human scores, or finish the quality-scoring
  workflow after manual scoring.
disable-model-invocation: true
---

# Generate Quality Report

Generate a comprehensive quality report comparing AI scores against human review scores. Creates the final analysis with agreement metrics, calibration insights, and recommendations.

**Use this AFTER human scoring (Step 5) — all `human_score` values must be set.**

## Always ask before acting

**Do NOT** auto-detect or assume the quality-scoring run directory, and do NOT proceed without a confirmed `--run-dir`.

**Do:** ask for the full path to the quality-scoring run directory immediately; validate it exists and contains `quality_scores_ai.json` and `sampled_for_review.json`; verify every `human_score` is set (not null) before generating; wait for the user's response.

Example prompt:

```
Before generating the report, I need the path to the quality-scoring run directory.
Examples:
  results/docs-assistant/api/docs-assistant 2026-03-17 16-23/quality-scoring-2026-06-23T12-52-44Z
  results/external-llms/chatgpt/external-llms-chatgpt 2026-04-01 20-56/quality-scoring-2026-05-03T18-28-22Z
Which directory should I use?
```

## Input

**`--run-dir` is always required** (ask if not provided). Paths are inferred from standard file names:

- `--run-dir "results/.../quality-scoring-YYYY-MM-DDTHH-MM-SSZ"` — **required**
  - `--ai-scores` → `<run-dir>/quality_scores_ai.json`
  - `--human-scores` → `<run-dir>/sampled_for_review.json` (batch reviews merged back by the `merge-batches` skill)
  - `--output` → `<run-dir>/QUALITY_REPORT.md`

**Advanced overrides** (only when a file lives outside the run dir): `--ai-scores`, `--human-scores`, `--output`.

## Actions

1. **Collect and validate inputs** — ask for `--run-dir` if missing (no auto-detect); verify the directory and both JSON files exist; block if any `human_score` is null; count AI scores vs human reviews.
2. **Load and merge scores** — parse both JSON files and merge AI and human scores by `issue_id` (AI scores + reasoning; human scores + timestamps).
3. **Calculate metrics** — agreement (exact match %, within ±1, disagreements); score distribution (1/2/3/4 for AI and human; bias detection); quality estimates (average scores, confidence, estimated batch quality).
4. **Generate report** — executive summary, AI vs human comparison, agreement metrics, outliers/discrepancies, calibration analysis, actionable recommendations.
5. **Save output** — write `QUALITY_REPORT.md` to the run directory.

## Usage

Standard — provide the run directory (always required):

```bash
python tools/quality-scoring/generate_quality_report.py \
  --run-dir "results/docs-assistant/api/docs-assistant 2026-03-17 16-23/quality-scoring-2026-06-23T12-52-44Z"
```

Advanced — explicit override (only when files are outside the standard run dir):

```bash
python tools/quality-scoring/generate_quality_report.py \
  --run-dir "results/.../quality-scoring-2026-06-23T12-52-44Z" \
  --human-scores "path/to/custom/sampled_for_review.json"
```

## Report structure

`QUALITY_REPORT.md` contains:

- **Executive summary** — date/time, response counts (total analyzed, sampled), average scores.
- **Score distribution** — AI and human breakdown (1–4), with the labels: 1 Useless, 2 Link-dependent, 3 Partially, 4 Fully direct.
- **Agreement analysis** — exact match %, within ±1 %, disagreement rate + specific examples.
- **Calibration analysis** — scorer bias detection, consistency metrics, confidence levels.
- **Quality insights & recommendations** — which response types work best, problem areas, batch-quality guidance.

## Error handling

- **`--run-dir` not provided:** ask the user for the full path (do not auto-detect).
- **Run directory not found:** report the missing path; it must contain `quality_scores_ai.json` and `sampled_for_review.json` (with all `human_score` set).
- **AI scores file not found:** run the `quality-scoring-workflow` skill first to generate AI scores.
- **Invalid JSON in human scores:** verify `sampled_for_review.json` is valid and all `human_score` values are set.
- **Missing human score:** every item must have `human_score` set (1–4); set missing scores and retry.

## Workflow integration

```
quality-scoring-workflow  → (Steps 1–4 automated, pauses at Step 5)
generate-review-tool      → human scores each item in the browser, exports data
generate-quality-report   → merges AI + human scores, writes QUALITY_REPORT.md
```

## See also

- `generate-review-tool` skill — interactive HTML review interface
- `quality-scoring-workflow` skill — complete automated pipeline
- `merge-batches` skill — consolidate scored batches before reporting
- `docs/quality-scoring/README.md` — quick start guide
- Underlying script: `tools/quality-scoring/generate_quality_report.py`
