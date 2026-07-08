---
name: quality-scoring-workflow
description: >-
  Runs the end-to-end quality-scoring pipeline — extract responses, score with
  Claude, sample 10% for human review, then hand off for manual scoring and
  report generation. Use when the user asks to score answer quality, run the
  quality-scoring workflow, or evaluate how well AI responses solve user
  problems.
disable-model-invocation: true
---

# Quality Scoring Workflow

Complete end-to-end pipeline for quality scoring: extract responses → score with Claude → human review → generate report. This is the main entry point for the quality scoring system. Uses Cursor's built-in Claude — zero API cost.

## Critical: Step 5 is a human handoff

The workflow **pauses at Step 5 (human review)** because human judgment is required. This is NOT an automation opportunity.

**Do NOT:**
- Auto-detect or assume the test results directory — always ask first.
- Proceed before the user provides a valid directory path.
- Automatically fill in `human_score` values.
- Assume AI scores are correct and confirm them as human reviews.
- Skip Step 5, or proceed without explicit user confirmation.

**Do:**
- Ask for the test results directory BEFORE anything else (no auto-detect); validate it exists.
- Pause at Step 5 and clearly present the sampled items with AI scores and reasoning.
- Recommend the default review path: run the `generate-review-tool` skill.
- Wait for the user's response and give clear next steps.

Why: human review provides independent calibration; agreement metrics are meaningless if human scores just copy AI scores.

## Directory input (asked before anything else)

Ask immediately, then validate before Step 1:

```
Before starting, I need to know which test results to score.
Examples:
  results/docs-assistant/api/docs-assistant 2026-03-17 16-23
  results/external-llms/chatgpt/external-llms-chatgpt 2026-04-01 20-56
  results/analysis-system/analysis-system 2026-05-21 16-54
Which directory should I use?
```

If the path is invalid, tell the user and ask again — do not proceed with a wrong path.

## Workflow steps

```
User provides test results directory
  → 1. Load test results from the directory
  → 2. Extract AI responses
  → 3. Score with Claude (LLM-as-Judge)
  → 4. Sample 10% for human review
  → 5. Prepare sampled_for_review.json for manual scoring  [PAUSE — human handoff]
User sets human scores (via generate-review-tool or by editing the file)
  → 6. Run the generate-quality-report skill with --run-dir "<this run's directory>"
```

### Step 1 — Load source
Detect the test type from the directory (`docs-assistant.api`, `llm.chatgpt`, etc.), scan for responses, and create the timestamped output directory `quality-scoring-YYYY-MM-DDTHH-MM-SSZ/`.

### Step 2 — Extract responses
Run the extractor over the run directory to build the scoring inputs. Reuse `tools/quality-scoring/extract_responses_for_scoring.py`.

### Step 3 — Score with Claude
Apply the same rubric human reviewers use. Assume the user will not click links; score how well the text alone solves the task (stop at first match):
1. Wrong/off-topic/misleading, or links don't help → **1 (Useless)**
2. Text is navigation only ("see [link]"); answer lives behind links → **2 (Link-dependent)**
3. Text correct but a required step/value needs a link → **3 (Partially direct)**
4. Text alone fully solves it; links optional → **4 (Fully direct)**

Edge cases: correct-but-link-heavy → 3 (not 4); wrong-but-self-contained → 1 (not 4). Full rubric: `docs/quality-scoring/quality-scoring.md#scoring-scale-1-4`. Writes `quality_scores_ai.json`.

### Step 4 — Sample for review
Sample 10% using a smart strategy (≈50% random + 50% lowest AI scores for verification). Writes `sampled_for_review.json`. The workflow then pauses and hands off.

### Step 5 — Manual scoring (human handoff)
Present the sampled items and set each `human_score` (1–4). Recommend the `generate-review-tool` skill (browser UI, auto-saves on Export Data). Alternatives: edit `sampled_for_review.json` directly, or use `--no-server` offline. When you reach this handoff, substitute the real timestamped directory into the report command so the user can paste it without editing.

### Step 6 — Generate report
Only after all `human_score` values are set, run the `generate-quality-report` skill:

```bash
python tools/quality-scoring/generate_quality_report.py --run-dir "results/.../quality-scoring-YYYY-MM-DDTHH-MM-SSZ"
```

It merges AI + human scores by issue ID, computes agreement metrics and bias detection, and writes `QUALITY_REPORT.md`.

## Success criteria

- Agent asks for and validates the test results directory before doing anything.
- Steps 1–4 run automatically; Step 5 clearly requires manual scoring; Step 6 runs only after human scores are set.
- Report generated with AI vs human comparison; outputs saved at each stage; zero API cost.

## Output versioning, cleanup, and agent guidelines

Each run creates a timestamped `quality-scoring-YYYY-MM-DDTHH-MM-SSZ/` directory (never overwritten). For directory structure, temporary-file cleanup rules, error scenarios, and strict agent conduct rules (never write artifacts to project root; use existing tools in `tools/quality-scoring/`; run the workflow only once per session), see [reference.md](reference.md).

## See also

- `generate-review-tool` skill — browser review interface with auto-save
- `generate-quality-report` skill — merge scores & generate the report
- `docs/quality-scoring/README.md` — quick start & overview
- `docs/quality-scoring/quality-scoring.md` — technical details
- Orchestrator: `tools/quality-scoring/generate_quality_workflow.py`
