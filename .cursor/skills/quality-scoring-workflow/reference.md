# Quality Scoring Workflow — reference

Detailed material for the `quality-scoring-workflow` skill: output versioning, cleanup rules, error scenarios, and agent conduct rules.

## Output directory versioning

Each workflow run creates a timestamped subdirectory to prevent overwrites and preserve history.

```
results/docs-assistant/api/docs-assistant 2026-04-09 10-54/
├── quality-scoring-2026-04-22T10-30-45Z/    ← First run
│   ├── quality_scores_ai.json
│   ├── sampled_for_review.json              ← includes human scores after review
│   └── QUALITY_REPORT.md
├── quality-scoring-2026-04-22T11-15-22Z/    ← Second run
│   └── ...
```

- **Format:** `quality-scoring-YYYY-MM-DDTHH-MM-SSZ` (UTC, `Z` suffix). Unique and sortable — no overwrites.
- **Benefits:** version history, no data loss, traceability, concurrent runs, easy comparison across runs.

Regenerate a report from a previous run with the `generate-quality-report` skill:
```bash
python tools/quality-scoring/generate_quality_report.py --run-dir "results/.../quality-scoring-2026-04-22T10-30-45Z"
```

## Two-phase execution

- **Phase A (automated):** Steps 1–4 — extract, score, sample. No user intervention.
- **Phase B (manual + finalization):** Steps 5–6 — human scoring, then report generation.

### Skip human review (AI-only report)
Acknowledge skipping Step 5; the report will show only AI score distribution and is less useful without human calibration.

### Use existing files
If a `responses_to_score.json` already exists in the run directory, extraction is skipped and it is used directly. To add human scores to an existing sample, skip to Step 5 and edit `sampled_for_review.json`.

## Error handling

- **Any step fails:** print a clear message; offer retry or proceed; progress is saved so you can resume.
- **Missing human scores in Step 5:** warn that `sampled_for_review.json` has no human scores; the user must set `human_score` for each item before Step 6.
- **Attempting Step 6 without human scores:** block report generation; instruct the user to set `human_score` values (or use the `generate-review-tool` skill), then run `generate-quality-report`.

## Agent conduct rules (critical)

1. **Never create files in project root** during the workflow. Display information in terminal/chat output instead. Outputs go only in `results/*/quality-scoring-YYYY-MM-DDTHH-MM-SSZ/`.
2. **Use existing tools in `tools/quality-scoring/`.** Do not create temporary scripts in a `scripts/` folder. If an existing script has issues, fix it in place. The orchestrator `generate_quality_workflow.py` already calls the right tools.
3. **Clean up temporary scripts immediately after use.** Only permanent, reusable tools should live in the repo.
4. **Run the workflow only once per session.** Investigate and fix the root cause of any error before retrying; delete incomplete/failed timestamped folders from the session before running again. Do not create multiple timestamped folders from repeated attempts.
5. **Keep the workspace clean:** outputs → `results/*/quality-scoring-*/`; configuration/tools → `tools/quality-scoring/`; project root → only source code and docs, never workflow artifacts.

## Cleanup rules

At the end of the workflow, remove temporary files **within the timestamped output directory** only:

- Step 2: `responses_to_score.json` (temporary extraction file).
- Step 3: `quality_scores_batch_*.json`, `scoring_progress_*.tmp`.
- Step 4: `sample_working_*.tmp`, `candidates_*.json`.
- Step 5: `review_cache_*.tmp`, `comparison_*.tmp`, `*_backup.json`.
- Step 6: `report_draft_*.tmp`, `metrics_*.tmp`.

**Keep (never delete):** `quality_scores_ai.json`, `sampled_for_review.json`, `QUALITY_REPORT.md`, all previous timestamped directories, the user's test results directory, and all user-provided inputs.

Cleanup procedure: determine the timestamped directory; scan for temporary patterns (`*.tmp`, `*.cache`, `*.working`, `*_backup.json`, `scoring_progress_*`, `batch_*.json`, `sample_working_*`, `report_draft_*`); delete confirmed internal working files and report each deletion; verify permanent outputs exist (warn, don't delete, if missing); never touch other `quality-scoring-*` directories; print a cleanup summary. On cleanup error, log it, don't fail the workflow, and tell the user which files remain.

**Archival, not deletion:** if many runs accumulate (>20), move old ones to an archive location rather than deleting; keep at least 3–5 recent runs for comparison.

## What "temporary script" means

- **Temporary** (delete after use): on-the-fly workaround scripts, duplicate/variant versions of existing tools, one-off solutions.
- **Permanent** (keep): the orchestrator `generate_quality_workflow.py`, core tools like `extract_responses_for_scoring.py`, and anything committed under `tools/quality-scoring/`.

Modify an existing tool when it's almost right but has issues (encoding, auth, bugs) or needs adaptation. Create a new tool only when it solves a fundamentally different problem and belongs in `tools/quality-scoring/` permanently. Never create one-off workarounds to bypass existing tools.
