# Quality Scoring System

Score AI-generated responses using Cursor Agent with built-in Claude. **Zero API costs. Full workflow automation.**

This page is a quick overview. For details, see:

- **All commands & flags:** [CURSOR_COMMANDS.md](CURSOR_COMMANDS.md)
- **Architecture, data formats & scoring rubric:** [quality-scoring.md](quality-scoring.md)

---

## How It Works

A two-phase pipeline:

- **Phase A (automated):** extract responses → score 1-4 with Claude → sample 10% for human review (all style variants kept — `naive`, `familiar`, `expert`; backfills after random/low-score pool overlap so the full 10% target is reached).
- **Phase B (manual + report):** a human reviews the sample, then a report compares AI vs human scores.

The scoring scale is 1-4 (see the [full rubric](quality-scoring.md#scoring-scale-1-4) for the decision tree and examples):

| Score | Label | Meaning |
|-------|-------|---------|
| 1 | Useless | Irrelevant/misleading; links don't help |
| 2 | Link-dependent | Text is navigation; links solve it |
| 3 | Partially direct | Text + links needed to fully solve |
| 4 | Fully direct | Text alone solves the problem |

---

## Quick Start (the happy path)

Each command will ask you for the required inputs before doing anything.

```bash
# 1. Score everything and prepare a sample (Phase A, ~5-10 min)
#    → Agent asks: which test results directory?
/quality-scoring-workflow

# 2. Review the sample in your browser (Phase B, ~8-12 min)
#    → Agent asks: path to sampled_for_review.json? how many batches? which port?
#    Score each item 1-4, then click "Export Data" to save to disk. Ctrl+C to stop.
/generate-review-tool

# 3. Generate the report (~1 min)
#    → Agent asks: which quality-scoring run directory?
/generate-quality-report
```

**Total time:** ~15-25 minutes.

<details>
<summary>Alternative review method</summary>

- **Direct edit:** open `sampled_for_review.json` in a text editor and set `human_score` (1-4) per item.

See [CURSOR_COMMANDS.md](CURSOR_COMMANDS.md) for every flag and the distributed batch-review workflow.
</details>

---

## Commands

| Command | Purpose | Time |
|---------|---------|------|
| `/quality-scoring-workflow` | Complete automated pipeline (Phase A) | ~5-10 min |
| `/generate-review-tool` | Interactive HTML review interface (single or batched) | ~8-12 min |
| `/generate-quality-report` | Generate the final AI-vs-human report | ~1 min |
| `/batch-status` | Track scoring progress across review batches | ~1 sec |
| `/merge-batches` | Consolidate scored batches into one file | ~1 sec |

**→ See [CURSOR_COMMANDS.md](CURSOR_COMMANDS.md) for full command reference and examples.**

---

## Outputs

All outputs land in a timestamped directory `results/<test>/quality-scoring-YYYY-MM-DDTHH-MM-SSZ/`:

- `quality_scores_ai.json` — all AI scores with reasoning
- `sampled_for_review.json` — the sample, with `human_score` filled in after review
- `review.html` — interactive review tool (generated on demand)
- `QUALITY_REPORT.md` — AI vs human comparison analysis

See [quality-scoring.md](quality-scoring.md#directory-versioning) for the versioning scheme and full directory layout.

---

## Key Features

- **Zero API costs** — uses Cursor's built-in Claude.
- **Browser-based review** — click scores, no JSON editing; server auto-saves to disk via "Export Data".
- **Distributed batch review** — split a sample across reviewers, track progress, and merge results.
- **Version history** — every run is preserved in its own timestamped directory.

---

## Agent Guidelines

Agents running these commands must keep the workspace clean (outputs only in timestamped directories, use existing tools in `tools/quality-scoring/`, run the workflow once per session, clean up temp files). The authoritative version of these rules lives in the [`/quality-scoring-workflow`](../../.cursor/commands/quality-scoring-workflow.md) command under "Best Practices & Agent Guidelines".

---

**Status:** Production-ready  
**Last Updated:** Jun 23, 2026
