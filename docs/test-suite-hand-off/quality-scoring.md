# Quality Scoring

The quality scoring system evaluates how well AI-generated answers actually solve the user's problem — not just whether a link was found (the test suite handles that), but whether the *text response* is useful.

---

## What it is

A pipeline that takes AI-generated responses (from Docs Assistant, ChatGPT, or Gemini test runs) and scores each one on a 1–4 scale:

| Score | Label | Meaning |
| :--- | :--- | :--- |
| **1** | Useless | Irrelevant or misleading; links don't help |
| **2** | Link-dependent | Text alone is insufficient; user must click links to find the answer |
| **3** | Partially direct | Useful text, but links are still needed for the full answer |
| **4** | Fully direct | The text itself completely solves the user's problem |

The system uses a **three-phase approach**:

1. **Automated scoring** — AI rates all responses (fast, cheap, covers everything)
2. **Human validation** — A reviewer scores ~10% of the sample to calibrate the AI
3. **Report generation** — Compares AI vs. human scores and measures agreement

---

## What it can do

- Batch-score hundreds of AI responses automatically.
- Identify weak responses (score 1–2) that need content improvement.
- Provide a browser-based review interface for human scoring (no JSON editing required).
- Generate a calibration report comparing AI vs. human agreement.
- Track quality over time by scoring different test runs.

## What it cannot do

- Measure link discoverability (that's the [test suite's](test-suite.md) job).
- Replace human review entirely — the 10% sample validation is essential for calibration.
- Score responses from paths that don't produce text (e.g., Algolia returns links, not text answers).
- Run without Cursor IDE — the review workflow uses Cursor skills.

---

## How to use

There are two ways to run quality scoring:

1. **Integrated analysis stage** (below) — a single opt-in flag on `analysis_system.py` that scores text-answer paths automatically as part of a run. Best for unattended, repeatable scoring.
2. **Full review workflow** (further down) — the Cursor-driven pipeline with human calibration. Best when you need validated, calibrated scores.

### Integrated analysis stage (optional, default off)

`analysis_system.py run` can score answer quality as an extra stage, reusing the same `tools/quality-scoring/` extractor and scorer. It is **off by default**, so normal runs are unchanged (`mean_quality` stays `null`, `quality_scored` stays `[]`).

```powershell
# Default run — link/rank metrics only, no quality scoring:
python tools/test-suite/analysis_system.py run

# Opt in to quality scoring for text-answer paths:
python tools/test-suite/analysis_system.py run --score-quality
python tools/test-suite/analysis_system.py run --score-quality --quality-scorer simple
```

When enabled:

- Only **text-answer paths** are scored: `docs-assistant.api`, `llm.chatgpt`, `llm.gemini`. Link-only paths (Algolia, Hybrid Search, Google) are left untouched.
- `mean_quality` is populated on the per-path-locale aggregates and per-issue aggregates for scored paths.
- `run_summary.json` lists the scored source keys under `quality_scored`.
- `--quality-scorer` accepts `simple` (heuristic, the default) or `llm`; `llm` is not wired for unattended runs yet and falls back to `simple` with a warning.
- The stage **fails soft**: if scoring errors, it logs a warning and leaves `mean_quality` as `None` rather than aborting the analysis.

This integrated stage does **not** perform human calibration. For validated scores, use the full workflow below.

### Full review workflow

The review workflow is driven by **Cursor skills** (in `.cursor/skills/`). Ask the agent to run a skill by name, or run the underlying scripts directly. You need Cursor IDE open in this repository.

### Full workflow (recommended)

Ask the agent to run the `quality-scoring-workflow` skill. It runs the automated phase (extract responses, score them, sample for review) and then pauses for your manual review. The agent asks for the test run directory before starting.

### Step-by-step breakdown

| Step | What happens | Your action |
| :--- | :--- | :--- |
| 1 | Select which test run to score | Provide the run directory when asked |
| 2 | Extract AI responses into JSON | Automatic |
| 3 | Score all responses (1–4) | Automatic |
| 4 | Sample ~10% for human review | Automatic |
| — | **Workflow pauses here** | — |
| 5 | Review sampled items and set your scores | Manual (see below) |
| 6 | Generate quality report | Run the `generate-quality-report` skill |

### Human review (Step 5)

After the automated phase, review the sampled items using the HTML tool — ask the agent to run the `generate-review-tool` skill (or run `python tools/quality-scoring/launch-review.py`).

This opens a browser interface at `localhost:8000` where you:

1. Read each query + AI response + provided links.
2. See the AI's score and reasoning.
3. Set your own score (1–4) and optional notes.
4. Click "Export Data" to save.

Press `Ctrl+C` in the terminal to stop the server when done.

### Generate the final report (Step 6)

Ask the agent to run the `generate-quality-report` skill, or run the script directly:

```bash
python tools/quality-scoring/generate_quality_report.py \
  --run-dir "results/docs-assistant/api/docs-assistant 2026-03-17 16-23/quality-scoring-2026-06-23T12-52-44Z"
```

---

## Output files

All outputs are saved in a timestamped folder inside the test run directory:

```
results/<test-type>/<run-name>/quality-scoring-YYYY-MM-DDTHH-MM-SSZ/
├── quality_scores_ai.json       All responses with AI scores and reasoning
├── sampled_for_review.json      ~10% sample with human_score fields
├── review.html                  Browser-based review interface
└── QUALITY_REPORT.md            Final report comparing AI vs. human scores
```

---

## The report

`QUALITY_REPORT.md` contains:

- **Executive summary** — total scored, sample size, average AI vs. human scores
- **Score distribution** — breakdown by score level (1–4)
- **Agreement metrics** — exact agreement %, within ±1 agreement %
- **Calibration insights** — whether AI tends to score higher or lower than humans
- **Recommendations** — areas where content needs improvement

---

## Available skills

Project skills live in `.cursor/skills/`. Ask the agent to run one by name.

| Skill | Purpose |
| :--- | :--- |
| `quality-scoring-workflow` | Full pipeline: extract + score + sample (then pauses for review) |
| `generate-review-tool` | Open browser-based review interface for human scoring |
| `generate-quality-report` | Generate final AI vs. human comparison report |
| `batch-status` | Track scoring progress across review batches |
| `merge-batches` | Consolidate scored batches into one file |

---

## Troubleshooting

| Problem | Solution |
| :--- | :--- |
| Skill not applied | Ask the agent to run the skill by name (e.g. "run the `quality-scoring-workflow` skill") |
| "File not found" error | Use the full path to the test run directory |
| Port 8000 in use | Edit `tools/quality-scoring/review-server.py` to change port |
| Scores not saving | Check browser console (F12) for network errors |
| Need to resume later | Run the `generate-review-tool` skill again — scores are saved in localStorage |
| Python import error | Ensure Python 3.6+ is installed |
