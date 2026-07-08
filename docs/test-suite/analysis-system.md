# Analysis System

| Field | Value |
| :---- | :---- |
| Created | Mar 25, 2026 |
| Updated | Mar 26, 2026 |
| Status | Implemented |
| Related | [Analysis dashboard](analysis-dashboard.md) |
| Related | [Dashboard improvements backlog](analysis-dashboard-improvements-backlog.md) |
| Related | [Unified Analysis Improvements](unified-analysis-improvements.md) |

This document explains the implemented Phase 1 analysis system in `tools/test-suite/analysis_system.py`.

## 1. Scope

The analysis system processes raw outputs from all Phase 1 paths:

1. Internal search
2. Docs Assistant
3. External search
4. External LLMs

Phase 1 currently implements:

1. Link matching
2. Rank analysis
3. Per-issue processed outputs
4. Aggregate rollups
5. Run-to-run comparison

Phase 1 intentionally does **not** implement:

1. AI answer quality scoring
2. Human review scoring

## 2. Source Of Truth

The analysis system follows the investigation rules:

1. Issue markdown files in `docs/test-suite/issues/` are the canonical source for metadata and ground truth.
2. Raw runner artifacts are the canonical source for surfaced links and answer text.
3. Runner-level summary fields such as `found`, `rank`, `target_doc_url_found`, and similar per-runner convenience flags are ignored.

The script reads:

- `target_docs` as the target-doc set
- `other_helpful_docs`
- `persona`
- `product`
- `user_intent`

from the issue docs, and joins those with the raw outputs collected under `results/`.

The result classifier uses these link types where applicable:

- `target_doc`
- `target_doc_different_loc`
- `other_helpful_doc`
- `other_helpful_doc_different_loc`
- `unrelated`

`target_doc_different_loc` means the surfaced link matches a target doc for the issue, but in a different locale than the query. `other_helpful_doc_different_loc` means the surfaced link is in the issue's `other_helpful_docs` set, but in a different locale than the query.

## 3. Implemented Script

Script path:

`tools/test-suite/analysis_system.py`

Available commands:

```powershell
python "tools/test-suite/analysis_system.py" run
python "tools/test-suite/analysis_system.py" compare --baseline "<analysis-run-dir>" --candidate "<analysis-run-dir>"
```

## 4. Default Run Selection

When you run the `run` command without overrides, the script automatically selects the **latest full comparable run per source**.

That selection logic is intentionally not "latest folder wins".

The script:

1. Discovers all run folders under the canonical `results/<path-family>/<variant>/` layout.
2. Computes whether each run is structurally full for that source.
3. Applies a health check where needed.
4. Chooses the newest healthy full run, or the newest full run if no healthy one exists.

Current source keys:

1. `internal-search.algolia-helpcenter`
2. `internal-search.algolia-devportal`
3. `internal-search.hybrid-search`
4. `docs-assistant.api`
5. `external-search.google-search-playwright`
6. `llm.chatgpt`
7. `llm.gemini`

External search has an additional health rule so obviously broken full runs are skipped when a healthier full run exists.

## 5. URL Matching Rules

The implemented matcher follows the clarified investigation rules.

### 5.1 Help Center URLs

For Help Center URLs, the matcher requires:

1. Same portal: `help.vtex.com`
2. Same doctype
3. Same exact slug
4. Locale may be explicit or omitted

The matcher normalizes:

1. Optional locale prefixes such as `/en/`, `/pt/`, `/es/`
2. Optional `docs/` prefix
3. Legacy singular doctype aliases such as `tutorial` -> `tutorials`
4. Query strings such as `?utm_source=...` are ignored for identity (path-only matching)
5. Help Center `?locale=en|pt|es` is read when the path has no locale segment, so links like `/docs/tutorials/foo?locale=en` classify as English rather than inheriting the query locale

Cross-locale partial credit (`target_doc_different_loc`) applies when the surfaced URL has an explicit locale (path or `?locale=`) that differs from the query locale but the same portal + doctype + slug as a ground-truth target doc.

The matcher does **not**:

1. Treat translated slugs as equivalent
2. Treat different doctypes as equivalent

Examples:

1. `https://help.vtex.com/docs/tracks/visao-geral-da-integracao-shopee` matches `https://help.vtex.com/pt/docs/tracks/visao-geral-da-integracao-shopee`
2. `https://help.vtex.com/docs/tracks/visao-geral-da-integracao-shopee` does not match `https://help.vtex.com/en/docs/tracks/integration-overview-shopee`
3. `https://help.vtex.com/en/docs/tracks/unified-commerce-101` does not match `https://help.vtex.com/en/docs/tutorials/unified-commerce-101`

### 5.2 Developers Portal URLs

Developers Portal URLs do not have locale variants in this system.

The implementation treats them as exact document identities after normalizing:

1. Host
2. Path
3. Trailing slash
4. Query string removal

Regular hash fragments are preserved for identity on non-Help Center URLs, while browser text fragments such as `#:~:text=...` are ignored.

## 6. Path-Specific Ingestion

### 6.1 Internal Search

The script reads `results[].top_results` from the raw JSON files and:

1. Classifies all returned links
2. Computes metrics using only the first `7` links
3. Ignores runner summary fields

### 6.2 Docs Assistant

The script reads `results[].links` and computes:

1. A combined ranked list using the original link positions
2. A per-source breakdown for `markdown`
3. A per-source breakdown for `suggested_sources`

Combined Docs Assistant metrics are used for global rollups so the path is not double-counted in overall metrics.

Per-source Docs Assistant metrics are still exported in:

1. `issues_processed.json`
2. `aggregates_by_path_locale.json`
3. `failure_list.json`

### 6.3 External Search

The script reads `session_*.output[].queries[]` from `results.json` and:

1. Uses `output_urls` as the ranked link list
2. Recovers `locale` by joining `(issue_id, style, query)` back to `data/test-suite/external-search/all_queries.json`

### 6.4 External LLMs

The script reads the per-case markdown artifacts and:

1. Extracts `issue_id`, `locale`, `style`, and prompt text from the metadata blocks
2. Reads URLs from the `## Extracted URLs` section
3. Ignores historical `run_metadata.json` counters for evaluation

## 7. Output Artifacts

Each analysis run writes a new folder under:

`results/analysis-system/`

Example:

`results/analysis-system/analysis-system 2026-03-25 13-33 (1)/`

Artifacts written:

1. `issues_processed.json`
2. `aggregates_by_path_locale.json`
3. `aggregates_by_locale.json`
4. `aggregates_by_style.json`
5. `aggregates_by_persona.json`
6. `failure_list.json`
7. `run_summary.json`

The `run_summary.json` file records:

1. The selected raw runs
2. Success-threshold rules
3. Paths included
4. Overall metrics
5. `quality_scored` — the source keys scored by the optional quality stage (empty `[]` unless `--score-quality` is passed; see §7.1)

### 7.1 Optional Quality Scoring (default off)

By default the analysis computes link/rank metrics only: `mean_quality` is `null` everywhere and `run_summary.json` has `quality_scored: []`. This is unchanged, byte-for-byte, from earlier behavior.

Passing `--score-quality` opts into an extra stage that reuses `tools/quality-scoring/` to score the **text-answer paths** and populate the reserved fields:

```powershell
python "tools/test-suite/analysis_system.py" run --score-quality
python "tools/test-suite/analysis_system.py" run --score-quality --quality-scorer simple
```

- **Scored paths:** `docs-assistant.api`, `llm.chatgpt`, `llm.gemini`. Link-only paths (Algolia, Hybrid Search, Google) have no text answer and keep `mean_quality: null`.
- **Where it lands:** `mean_quality` on the per-path-locale aggregates (`aggregates_by_path_locale.json`) and the per-issue aggregates (`issues_processed.json`); scored source keys under `quality_scored` in `run_summary.json`.
- **`--quality-scorer`:** `simple` (heuristic, default) or `llm`. `llm` is not wired for unattended runs yet and falls back to `simple` with a warning.
- **Fail-soft:** a scoring error logs a warning and leaves `mean_quality` as `None`; it never aborts the analysis.

See [`docs/test-suite-hand-off/quality-scoring.md`](../test-suite-hand-off/quality-scoring.md) for the full quality-scoring workflow, including human calibration.

## 8. Comparison Runs

The `compare` command measures what changed between two analysis runs — a **baseline** (before) and a **candidate** (after). This is the primary tool for evaluating whether changes to documentation, search configuration, or infrastructure actually improved discoverability.

Typical use case: run the full test suite before and after an improvement (e.g. adding structured data, updating Algolia settings), generate an analysis for each, then compare them to see which paths, locales, or query styles improved or regressed.

The `compare` command writes a separate processed folder under:

`results/analysis-system-comparisons/`

Artifacts written:

1. `comparison_summary.json` — overall pass-rate and MRR deltas
2. `comparison_by_path_locale.json` — per-path, per-locale deltas
3. `comparison_by_locale.json` — per-locale deltas
4. `comparison_by_style.json` — per-query-style deltas
5. `comparison_by_persona.json` — per-persona deltas
6. `comparison_by_style_locale.json` — per-style, per-locale deltas
7. `comparison_by_persona_locale.json` — per-persona, per-locale deltas
8. `comparison_by_issue.json` — per-issue target/helpful pass deltas
9. `failure_delta.json` — `new_failures`, `resolved_failures`, `still_failing`

This gives a lightweight delta view between two analysis outputs without recomputing raw-path collection.

### 8.1 Multi-Run Comparisons

When you have more than two analysis runs, two additional commands avoid having to compare them one pair at a time.

#### `compare-chain`

Compares each consecutive pair in a list of runs (run 1 vs 2, run 2 vs 3, etc.). This shows how metrics moved at each step — useful to identify which specific change caused an improvement or regression.

```powershell
python "tools/test-suite/analysis_system.py" compare-chain `
  --runs "results/analysis-system/run-1" `
         "results/analysis-system/run-2" `
         "results/analysis-system/run-3"
```

#### `compare-all`

Compares all candidate runs against a single baseline. This shows cumulative progress from a fixed starting point — useful when measuring total improvement since the initial baseline.

```powershell
python "tools/test-suite/analysis_system.py" compare-all `
  --baseline "results/analysis-system/run-1" `
  --candidates "results/analysis-system/run-2" `
               "results/analysis-system/run-3"
```

Both commands write a single `multi_comparison.json` file under `results/analysis-system-comparisons/`. The file contains:

1. `mode` — `"chain"` or `"fan"`
2. `runs` — snapshot of each run's key metrics (analysis ID, timestamp, target pass rate, helpful pass rate, MRR)
3. `comparisons` — array of pairwise comparison results, each with `summary`, `by_path_locale`, `by_locale`, and `by_style` breakdowns

Render a multi-comparison dashboard (step and cumulative delta charts):

```powershell
py tools/test-suite/render_analysis_dashboard.py `
  --multi-comparison-run "results/analysis-system-comparisons/analysis-system 2026-04-02 14-06"
```

Output: `dashboard/index.html` under the comparison folder. Chain mode shows consecutive pair step deltas and a running cumulative sum; fan mode shows each candidate’s delta versus the shared baseline.

Auto-render after `compare`, `compare-chain`, or `compare-all` when you pass `--render-dashboard` (optional `--render-dashboard-report` for `summary.md`).

### 8.2 Timeline Dashboard

To visualize metric trends across multiple analysis runs, use the timeline dashboard:

```powershell
python "tools/test-suite/render_analysis_dashboard.py" `
  --timeline-runs "results/analysis-system/run-1" `
                  "results/analysis-system/run-2" `
                  "results/analysis-system/run-3"
```

Each dashboard is saved with a timestamped filename (e.g. `timeline_2026-04-08_11-38.html`) under `results/analysis-system/timeline-dashboard/`. Previous dashboards are never overwritten, so you keep a full history of generated reports.

The dashboard includes:

1. Summary cards showing latest metrics and delta vs first run
2. Line chart of overall pass rate, MRR, helpful found rate, and any relevant rate over time (with metric toggle buttons)
3. Line chart of pass rate by path over time (with path toggle buttons)
4. Line chart of MRR by path over time
5. Line chart of pass rate by locale over time
6. Line chart of pass rate by query style over time
7. Top movers: biggest improvements and regressions between the first and last run
8. Per-issue trends: sortable table with sparklines showing individual issue pass rate evolution
9. Table listing all runs with their key metrics and delta highlighting

Use `--output-dir` to write the dashboard to a custom location.

## 9. Usage Examples

Run with the default source selection:

```powershell
python "tools/test-suite/analysis_system.py" run
```

Render the dashboard in the same step (optional):

```powershell
python "tools/test-suite/analysis_system.py" run --render-dashboard
```

Use `--no-render-dashboard` from automation/CI wrappers, or `--render-dashboard-report` to also write `dashboard/summary.md`. The parent runner `run_all_runners.py` prompts whether to pass `--render-dashboard` to the analysis step (before analysis runs) unless `--render-dashboard` or `--no-render-dashboard` is already set.

Run with an explicit stable identifier:

```powershell
python "tools/test-suite/analysis_system.py" run --analysis-id "phase1-default"
```

Override one selected raw run:

```powershell
python "tools/test-suite/analysis_system.py" run `
  --source-run "external-search.google-search-playwright=results/external-search/google-search-playwright/google-search-playwright 2026-03-06 18-06"
```

Compare two processed runs:

```powershell
python "tools/test-suite/analysis_system.py" compare `
  --baseline "results/analysis-system/analysis-system 2026-03-25 13-33 (1)" `
  --candidate "results/analysis-system/analysis-system 2026-03-25 13-33 (2)"
```

Render the current WIP static dashboard from a processed run:

```powershell
python "tools/test-suite/render_analysis_dashboard.py" `
  --analysis-run "results/analysis-system/analysis-system 2026-03-25 17-12"
```

Compare multiple runs as consecutive pairs:

```powershell
python "tools/test-suite/analysis_system.py" compare-chain `
  --runs "results/analysis-system/analysis-system 2026-03-25 13-33 (1)" `
         "results/analysis-system/analysis-system 2026-03-25 17-12" `
         "results/analysis-system/analysis-system 2026-04-02 13-38"
```

Compare multiple candidates against a single baseline:

```powershell
python "tools/test-suite/analysis_system.py" compare-all `
  --baseline "results/analysis-system/analysis-system 2026-03-25 13-33 (1)" `
  --candidates "results/analysis-system/analysis-system 2026-03-25 17-12" `
               "results/analysis-system/analysis-system 2026-04-02 13-38"
```

Render a timeline dashboard across all runs:

```powershell
python "tools/test-suite/render_analysis_dashboard.py" `
  --timeline-runs "results/analysis-system/analysis-system 2026-03-25 13-33 (1)" `
                  "results/analysis-system/analysis-system 2026-03-25 17-12" `
                  "results/analysis-system/analysis-system 2026-04-02 13-38"
```

The dashboard generator is still under development and should be treated as an experimental visualization layer pending further testing and refinement.

## 10. Implementation Notes

Important implementation decisions:

1. Help Center locale-less URLs are matched only when their slug and doctype correspond to a localized doc for the evaluated locale.
2. Docs Assistant per-source metrics are preserved, but combined Docs Assistant metrics drive cross-path rollups.
3. `coverage_status` becomes `not_available` when a query locale has no eligible target doc for that source.
4. Aggregates exclude `not_available` rows from target-pass, helpful-pass, and MRR denominators.
5. Internal search metrics use top 7, while the exported classified result list still preserves all returned links.

