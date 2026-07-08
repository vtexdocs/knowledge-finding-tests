# Analysis Dashboard

| Field | Value |
| :---- | :---- |
| Created | Mar 25, 2026 |
| Updated | May 27, 2026 |
| Status | Implemented (iterating) |
| Related | [Analysis system](analysis-system.md) |
| Related | [Dashboard improvements backlog](analysis-dashboard-improvements-backlog.md) |

This document explains the static HTML dashboard flow for processed analysis-system outputs.

The dashboard generator is in active use for baseline reviews and run-to-run comparisons. Terminology follows the analysis-system model: target docs are the primary success condition, while helpful docs support the broader helpful pass rate.

## 1. Script

Script path:

`tools/test-suite/render_analysis_dashboard.py`

## 2. Supported modes

The script supports five entry points:

1. **Single-run** — one processed analysis run (`--analysis-run`)
2. **Comparison** — one pairwise comparison run (`--comparison-run`)
3. **Timeline** — trends across two or more analysis runs (`--timeline-runs`)
4. **Multi-comparison** — `compare-chain` / `compare-all` output (`--multi-comparison-run`)
5. **Runs index** — browse all analysis runs (`--build-index`)

It reads processed JSON outputs only. It does not read raw runner artifacts directly.

## 3. Usage

Render a dashboard for a processed analysis run:

```powershell
py tools/test-suite/render_analysis_dashboard.py `
  --analysis-run "results/analysis-system/analysis-system 2026-05-21 16-54"
```

Render a dashboard for a processed comparison run:

```powershell
py tools/test-suite/render_analysis_dashboard.py `
  --comparison-run "results/analysis-system-comparisons/analysis-system 2026-05-21 16-57"
```

Render a timeline dashboard across multiple runs:

```powershell
py tools/test-suite/render_analysis_dashboard.py `
  --timeline-runs "results/analysis-system/analysis-system 2026-04-30 15-00" `
                  "results/analysis-system/analysis-system 2026-05-21 16-54"
```

Also write a Markdown executive summary (Slack/Jira-ready):

```powershell
py tools/test-suite/render_analysis_dashboard.py `
  --comparison-run "results/analysis-system-comparisons/analysis-system 2026-05-21 16-57" `
  --report markdown
```

Override the output directory:

```powershell
py tools/test-suite/render_analysis_dashboard.py `
  --analysis-run "results/analysis-system/analysis-system 2026-03-25 17-12" `
  --output-dir "results/analysis-system/analysis-system 2026-03-25 17-12/custom-dashboard"
```

Build the analysis runs index and comparison runs index (cross-linked):

```powershell
py tools/test-suite/render_analysis_dashboard.py --build-index
```

This writes:

- `results/analysis-system/index.html` — all analysis runs (links to **All comparisons** and timeline when present)
- `results/analysis-system-comparisons/index.html` — all comparison runs (links back to **All analysis runs**)

To rebuild only the comparisons table:

```powershell
py tools/test-suite/render_analysis_dashboard.py --build-comparisons-index
```

To refresh every analysis run dashboard (Latest Analysis Run pages):

```powershell
py tools/test-suite/render_analysis_dashboard.py --rebuild-all-analysis-dashboards
```

To refresh every comparison dashboard:

```powershell
py tools/test-suite/render_analysis_dashboard.py --rebuild-all-comparison-dashboards
```

Render a multi-comparison dashboard from `multi_comparison.json`:

```powershell
py tools/test-suite/render_analysis_dashboard.py `
  --multi-comparison-run "results/analysis-system-comparisons/analysis-system 2026-04-02 14-06"
```

Auto-render after analysis or compare (no separate command):

```powershell
py tools/test-suite/analysis_system.py run --render-dashboard
py tools/test-suite/analysis_system.py compare --baseline "..." --candidate "..." --render-dashboard
py tools/test-suite/analysis_system.py compare-chain --runs "..." "..." --render-dashboard
```

Or use `run_all_runners.py` and accept the dashboard prompt at the end of the pipeline.

## 4. Output layout

By default, dashboards are rendered into the processed run folder:

| Mode | Default output |
| :---- | :---- |
| Single run | `results/analysis-system/<run-folder>/dashboard/` |
| Comparison | `results/analysis-system-comparisons/<run-folder>/dashboard/` |
| Timeline | `results/analysis-system/timeline-dashboard/` (`index.html` → latest `timeline_*.html`; timestamped snapshots kept) |
| Multi-comparison | `results/analysis-system-comparisons/<run>/dashboard/` |
| Runs index | `results/analysis-system/index.html` |

Artifacts written:

- `dashboard/index.html` (timeline: `timeline_YYYY-MM-DD_HH-MM.html` plus `timeline-dashboard/index.html` redirect to the latest)
- `dashboard/assets/dashboard.css` — shared shell (tokens, layout, tables, timeline sidebar, presentation/print)
- `dashboard/assets/chart.umd.min.js` — vendored Chart.js (offline-safe bar/line charts)
- `dashboard/assets/analysis_dashboard.css` — analysis/comparison-specific (heatmap, drilldown, charts)
- `dashboard/assets/dashboard_shared.js` — presentation mode, print expand, and help-tip interaction
- `dashboard/assets/dashboard.js` — analysis/comparison interactivity
- `dashboard/assets/dashboard-data.js` — embedded view model (analysis/comparison only)
- `dashboard/summary.md` when `--report markdown` is set (timeline: `summary.md` beside the HTML file)

Cross-link related dashboards (optional):

```powershell
py tools/test-suite/render_analysis_dashboard.py `
  --comparison-run "results/analysis-system-comparisons/analysis-system 2026-05-27 15-37" `
  --related-timeline "results/analysis-system/timeline-dashboard"
```

Flags: `--related-timeline`, `--related-analysis`, `--related-comparison`. Comparison dashboards also auto-link baseline/candidate run dashboards when `dashboard/index.html` exists under each run folder.

### 4.1 In-dashboard help for new users

Every hub page and dashboard includes a collapsible panel: **About dashboards & how to run a new audit**. It explains:

1. **Dashboard types** — Latest Analysis Run vs Comparison vs Timeline vs Multi-comparison (table with when to use each).
2. **Audit workflow** — copy-paste commands from collection → `analysis_system.py run` → render/index/compare/timeline.

Hub indexes (**Analysis Runs**, **Comparison Runs**) open this panel expanded by default. Edit copy in `tools/test-suite/dashboard_glossary.py` (`MODE_INTRO`, `DASHBOARD_TYPE_ROWS`, `AUDIT_WORKFLOW_STEPS`).

### 4.2 Hub indexes and back navigation

| Page | Path | Links to |
| :---- | :---- | :---- |
| Analysis runs index | `results/analysis-system/index.html` | Each analysis dashboard; **All comparisons**; timeline (if generated) |
| Comparisons index | `results/analysis-system-comparisons/index.html` | Each comparison dashboard; baseline/candidate analysis run links; **All analysis runs** |

Single-run dashboards show **← All analysis runs**. Comparison and multi-comparison dashboards show **← All comparisons**. Timeline dashboards show **← All analysis runs** plus the current page label.

Re-render indexes after adding new runs or comparisons so tables and cross-links stay current.

## 5. Dashboard scope

### 5.1 Single-run dashboard

1. Overview cards and callouts (best/weakest path, locale, style, path family, hardest issue)
2. Selected source runs
3. Path and locale performance (table + **bar chart** + **heatmap** toggle; pass rate / MRR metric toggle on charts)
4. **Path families** — weighted pass/MRR by Internal search, Docs Assistant, External search, External LLMs
5. **Locale gap vs EN** — ES−EN and PT−EN gaps per path
6. Locale, style, and persona views (table + bar chart toggle)
7. **Styles per locale**, **personas per locale**, and **portals by locale**
8. Docs Assistant link-source split
9. Worst issues
10. Failure explorer (filterable)
11. Issue drilldown (searchable)

### 5.2 Comparison dashboard

1. Delta overview cards
2. Baseline and candidate context
3. **Top movers** — largest improvements and regressions (path×locale, locale, style)
4. Path, locale, and style delta views (table + **bar chart** + **heatmap** toggle; pass rate / MRR metric toggle)
5. **Path families** — weighted delta pass/MRR by discovery family
6. **Persona deltas**, **style×locale deltas**, and **persona×locale deltas**
7. **Locale gap vs EN** — ES−EN and PT−EN pass-rate gaps per path
8. **Issue regressions / improvements** — top issue-level deltas
9. **Failure changes** — new, resolved, and still-failing queries
10. Docs Assistant link-source deltas

### 5.3 Timeline dashboard

1. Summary cards (latest metrics vs first run)
2. Overall metrics over time (pass rate, MRR, helpful pass)
3. Pass rate and MRR by path, locale, and query style
4. Styles per locale, personas per locale, portals by locale
5. Top movers (first run → last run)
6. Per-issue trends with sparklines
7. All-runs table with delta highlighting
8. Line/bar chart toggle per section

## 6. Interaction model

The dashboard is static HTML with local assets:

1. Tables are sortable in the browser
2. Sections can be expanded and collapsed
3. Path, locale, style, and persona sections support table/bar chart toggle
4. The failure explorer supports local filtering
5. The issue drilldown supports local search and detailed inspection
6. Timeline charts support dataset toggles and line/bar chart type switching
7. **Presentation mode** — hero toggle expands core sections, hides filters; preference stored in `localStorage`
8. **Print** — browser Print expands panels, shows heatmaps, and uses light-theme print styles (no server-side PDF)
9. **Metric help** — Overview includes a collapsible **How to read this dashboard** guide; labels show a `?` tooltip (hover on desktop, tap on mobile)

Chart.js is vendored into each dashboard’s `assets/chart.umd.min.js` (copied from `tools/test-suite/dashboard_assets/` on render). Charts work on `file://` without CDN access. No backend or frontend build step is required.

### 6.1 Metric glossary and tooltips

Definitions live in `tools/test-suite/dashboard_glossary.py` (not duplicated in HTML templates). The renderer maps labels to help keys and emits:

1. **Metrics guide** — collapsible panel at the top of Overview (content depends on dashboard mode).
2. **`?` tooltips** — on overview cards, section navigation, panel titles, table headers, and chart view toggles where wired.
3. **Comparison reading guide** — short callout on pairwise comparison dashboards explaining delta direction.

To update copy, edit `dashboard_glossary.py` and re-render the dashboard. Tooltips are hidden when printing; the comparison reading guide remains visible in print output.

## 7. Source data used

For analysis dashboards:

1. `run_summary.json`
2. `aggregates_by_path_locale.json`
3. `aggregates_by_locale.json`
4. `aggregates_by_style.json`
5. `aggregates_by_persona.json`
6. `issues_processed.json`
7. `failure_list.json`

For comparison dashboards:

1. `comparison_summary.json`
2. `comparison_by_path_locale.json`
3. `comparison_by_locale.json`
4. `comparison_by_style.json`
5. `comparison_by_persona.json`
6. `comparison_by_style_locale.json`
7. `comparison_by_persona_locale.json`
8. `comparison_by_issue.json`
9. `failure_delta.json`

For timeline dashboards, the script reads the same analysis-run artifacts from each `--timeline-runs` directory. Older runs without `aggregates_by_style_locale.json` or `aggregates_by_persona_locale.json` derive those dimensions from `issues_processed.json`.

## 8. Current limitations

1. The dashboard presents processed analysis outputs exactly as generated by the analysis system.
2. Phase 1 dashboards visualize link and rank metrics only (no AI answer quality scoring).
3. Comparison mode requires a comparison run generated by `analysis_system.py compare` (older comparison folders may lack persona, issue, and failure-delta artifacts).
4. PDF export is deferred; use browser **Print → Save as PDF** (print styles in `dashboard.css`).

## 9. Data quality warnings (overview)

The Overview section shows yellow **warning banners** when:

1. **Analysis run** — a source is unhealthy, incomplete (`is_full == false`), has low nonempty ratio (&lt;90%), or many queries are `n_not_available`.
2. **Comparison run** — baseline and candidate used different source keys, different collection folders for the same source, or mismatched source health.

Warnings also appear in `summary.md` when `--report markdown` is set. Comparison dashboards list baseline and candidate source-run tables under Overview.
