# Analysis Dashboard Improvements — Implementation Backlog

| Field | Value |
| :---- | :---- |
| Created | May 27, 2026 |
| Status | Complete (P0–P8: EDU-2026-KR-1-001–025) |
| Related | [Analysis dashboard](analysis-dashboard.md) |
| Related | [Analysis system](analysis-system.md) |
| Related | [Improvements progress report](analysis-dashboard-improvements-report.md) |

This backlog turns the visualization improvement plan into concrete, file-level tasks. Tasks use IDs `EDU-2026-KR-1-###` for tracking in Jira or GitHub issues.

**Current baseline:** Phase 1A/1B are largely implemented; timeline dashboard exists beyond the original RFC. Gaps are comparison parity, stakeholder reports (RFC Phase 1C), presentation mode, and search-specific views.

---

## Summary by phase

| Phase | Theme | Tasks | Est. effort |
| :---- | :---- | :---- | :---- |
| **P0 — Quick wins** | Comparison movers, Markdown report, docs | EDU-2026-KR-1-001, EDU-2026-KR-1-002, EDU-2026-KR-1-003 | 2–4 days |
| **P1 — Comparison parity** | Persona/cross-dim deltas, issue regressions, failure delta | EDU-2026-KR-1-004, EDU-2026-KR-1-005, EDU-2026-KR-1-006, EDU-2026-KR-1-007 | 4–6 days |
| **P2 — Single-run depth** | Cross-dim sections, MRR charts, heatmap, locale gap | EDU-2026-KR-1-008, EDU-2026-KR-1-009, EDU-2026-KR-1-010, EDU-2026-KR-1-011 | 5–8 days |
| **P3 — Unified UX** | Shared shell, presentation mode, print CSS | EDU-2026-KR-1-012, EDU-2026-KR-1-013, EDU-2026-KR-1-014 | 4–6 days |
| **P4 — Workflow** | Auto-render, runs index, multi-comparison dashboard | EDU-2026-KR-1-015, EDU-2026-KR-1-016, EDU-2026-KR-1-017 | 5–8 days |
| **P5 — Data quality** | Source-run warnings, comparison context checks | EDU-2026-KR-1-018 | 2–3 days |
| **P6 — Discoverability** | Metric tooltips and glossary panel | EDU-2026-KR-1-019 | 1–2 days |
| **P7 — Navigation & onboarding** | Hub indexes, back nav, audit guide, tooltip polish | EDU-2026-KR-1-020, EDU-2026-KR-1-021, EDU-2026-KR-1-022 | 2–3 days |
| **P8 — Reliability & deep links** | Stable timeline URL, comparison run links, offline charts | EDU-2026-KR-1-023, EDU-2026-KR-1-024, EDU-2026-KR-1-025 | 1–2 days |

---

## P0 — Quick wins

### EDU-2026-KR-1-001 — Comparison “Top movers” section

**Goal:** Surface biggest improvements and regressions in the pairwise comparison dashboard (RFC §8), reusing timeline logic.

**Priority:** P0 | **Effort:** S (~0.5 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/render_analysis_dashboard.py` | Add `compute_comparison_movers(path_rows, locale_rows, style_rows, n=5)` using `delta_target_pass_rate` (fallback `delta_expected_pass_rate`). Add `render_comparison_movers_html()`. Wire into `render_sections()` for `mode == "comparison"`. |
| `tools/test-suite/dashboard_assets/analysis_dashboard.css` | Reuse or copy `.movers-grid`, `.movers-list`, `.up`, `.down` from timeline styles. |

**Reuse:** Adapt `_compute_top_movers()` pattern but for a single baseline→candidate pair (first = baseline metric, last = candidate metric, delta = candidate − baseline).

**Acceptance criteria**

1. Comparison dashboard shows “Top improvements” and “Top regressions” panels above path deltas.
2. Each row shows label (e.g. `internal-search.hybrid-search / ES`), signed delta in pp, and baseline → candidate values.
3. Works when some deltas are `0.0` (row still listed if in top N by absolute delta).

**Dependencies:** None.

---

### EDU-2026-KR-1-002 — Auto-generated Markdown executive summary (RFC Phase 1C)

**Goal:** Produce a Slack/Jira-ready `summary.md` beside each dashboard without manual report writing.

**Priority:** P0 | **Effort:** M (~1 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/render_analysis_dashboard.py` | Add `render_markdown_summary(view_model) -> str`. Add CLI flag `--report markdown` (default: off). Write `dashboard/summary.md` in `write_dashboard()`. |
| `docs/test-suite/analysis-dashboard.md` | Document `--report markdown` and output path. |

**Summary content (all modes)**

| Mode | Sections |
| :---- | :---- |
| `analysis` | Headline metrics, callouts (best/weakest path, locale, style, hardest issue), link to `index.html`, generated timestamp. |
| `comparison` | Delta headline metrics, comparison callouts, top movers (after EDU-2026-KR-1-001), baseline/candidate run ids. |
| `timeline` | First→last delta, top movers, run count, link to timeline HTML file. |

**Acceptance criteria**

1. `py tools/test-suite/render_analysis_dashboard.py --analysis-run "..." --report markdown` writes `dashboard/summary.md`.
2. Same for `--comparison-run` and `--timeline-runs`.
3. File is valid Markdown, under ~80 lines, suitable to paste into Slack.

**Dependencies:** EDU-2026-KR-1-001 optional for comparison (can ship summary first with callouts only).

---

### EDU-2026-KR-1-003 — Sync documentation with implementation

**Goal:** Docs reflect what exists today; RFC status updated.

**Priority:** P0 | **Effort:** S (~0.5 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `docs/test-suite/analysis-dashboard.md` | Add timeline mode, bar chart toggles, cross-dimensional timeline sections, `--report markdown` (after EDU-2026-KR-1-002). Update status from WIP to “Implemented (iterating)”. |
| `docs/test-suite/analysis-system.md` | Cross-link to backlog doc. |

**Acceptance criteria**

1. All three commands (`--analysis-run`, `--comparison-run`, `--timeline-runs`) documented with examples.
2. Known limitations list matches code (e.g. no persona comparison yet).

**Dependencies:** EDU-2026-KR-1-002 for report flag docs.

---

## P1 — Comparison parity

### EDU-2026-KR-1-004 — Persona and cross-dimensional comparison artifacts

**Goal:** Enable persona, style×locale, and persona×locale deltas in comparison dashboards.

**Priority:** P1 | **Effort:** M (~1.5 days)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/analysis_system.py` | In `run_compare()` / `build_comparison()`: add `comparison_by_persona.json`, `comparison_by_style_locale.json`, `comparison_by_persona_locale.json` via `compare_metric_rows()` on matching aggregate files. Register in `ARTIFACT_FILENAMES`. |
| `tools/test-suite/render_analysis_dashboard.py` | Load new JSON in `build_comparison_view_model()`. Add `render_dimension_rows(..., comparison=True)` sections. |
| `docs/test-suite/analysis-system.md` | List new comparison artifacts. |

**Acceptance criteria**

1. After `compare`, comparison folder contains three new JSON files.
2. Comparison dashboard shows Persona deltas, Style per locale deltas, Persona per locale deltas.
3. Backward compatible: older comparison folders without new files show “No data” or hide section.

**Dependencies:** `aggregates_by_persona_locale.json` and `aggregates_by_style_locale.json` must exist in both baseline and candidate runs (already written by current `run`).

---

### EDU-2026-KR-1-005 — Issue-level regression list (comparison)

**Goal:** Show issues that regressed or improved between baseline and candidate.

**Priority:** P1 | **Effort:** M (~1.5 days)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/analysis_system.py` | Add `comparison_by_issue.json`: per issue, delta target pass rate (and helpful pass) computed from `issues_processed.json` aggregates. |
| `tools/test-suite/render_analysis_dashboard.py` | Load issue comparison; render sortable table “Issue regressions / improvements” (top N each). Include in `render_data_js` for client sort. |
| `tools/test-suite/dashboard_assets/analysis_dashboard.js` | Optional: sort/filter for issue regression table. |

**Acceptance criteria**

1. Table lists issue id, product, persona, baseline pass %, candidate pass %, delta.
2. Default sort: largest regression first in regressions panel, largest improvement in improvements panel.

**Dependencies:** None beyond compare command.

---

### EDU-2026-KR-1-006 — Failure delta explorer (comparison)

**Goal:** Answer “what newly failed?” and “what was fixed?” between runs.

**Priority:** P1 | **Effort:** M (~1 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/analysis_system.py` | Add `failure_delta.json`: keys `new_failures`, `resolved_failures`, `still_failing` (compare `failure_list.json` from baseline vs candidate issue keys). |
| `tools/test-suite/render_analysis_dashboard.py` | New panel with three sub-tables or tabs. |
| `tools/test-suite/dashboard_assets/analysis_dashboard.js` | Reuse failure explorer filter UI for delta tables. |

**Acceptance criteria**

1. Comparison dashboard includes “Failure changes” section.
2. Each row: path, locale, style, issue id, query (truncated).
3. Counts match manual diff of `failure_list.json` for a known pair of runs.

**Dependencies:** Both runs must have `failure_list.json`.

---

### EDU-2026-KR-1-007 — Locale gap view (ES vs EN benchmark)

**Goal:** Make Spanish underperformance visible as a delta vs English, not only absolute ES metrics.

**Priority:** P1 | **Effort:** S (~1 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/render_analysis_dashboard.py` | Add `compute_locale_gaps(path_rows, baseline_locale="en")` → per path: `es_pass - en_pass`, `pt_pass - en_pass`. Render table “Locale gap vs EN” in analysis and comparison modes. |
| `tools/test-suite/dashboard_assets/analysis_dashboard.css` | Conditional formatting: negative gap in red, positive in green. |

**Acceptance criteria**

1. Single-run dashboard shows gap table under Locale view.
2. Comparison dashboard shows delta-of-gaps or candidate gap vs baseline gap.
3. Handles missing locale/path combinations gracefully.

**Dependencies:** None.

---

## P2 — Single-run depth

### EDU-2026-KR-1-008 — Cross-dimensional sections in single-run dashboard

**Goal:** Port timeline dimensions into analysis dashboard: style×locale, persona×locale, portal by locale.

**Priority:** P2 | **Effort:** M (~2 days)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/render_analysis_dashboard.py` | In `build_analysis_view_model()`: load `aggregates_by_style_locale.json`, `aggregates_by_persona_locale.json`; fallback to `_derive_style_locale_from_issues()` / `_derive_persona_locale_from_issues()` / `_derive_portal_locale_from_issues()` (already exist for timeline). Add three `_wrap_with_chart_toggle` sections in `render_sections()`. |
| `tools/test-suite/dashboard_assets/analysis_dashboard.js` | Extend `initChartDimension()` or add chart init for new section ids. |
| `tools/test-suite/render_data_js()` | Include `style_locale_rows`, `persona_locale_rows`, `portal_rows` in payload. |

**Acceptance criteria**

1. Single-run dashboard shows Styles per locale, Personas per locale, Portals by locale.
2. Older runs without aggregate files still render via derivation.
3. Bar chart toggle works for each section.

**Dependencies:** None (derivation functions exist).

---

### EDU-2026-KR-1-009 — MRR charts in single-run and comparison dashboards

**Goal:** Show target MRR alongside pass rate (timeline already has MRR by path).

**Priority:** P2 | **Effort:** S (~0.5 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/dashboard_assets/analysis_dashboard.js` | Add second metric option or dual-series bar chart (pass rate + MRR) for paths section; normalize MRR to 0–100 scale or use dual axis. |
| `tools/test-suite/render_analysis_dashboard.py` | Ensure `path_rows` include `target_mean_mrr` in table columns (verify `render_path_rows`). |

**Acceptance criteria**

1. Path section chart can show MRR or toggle between pass rate and MRR.
2. Comparison path chart shows delta MRR bars.

**Dependencies:** None.

---

### EDU-2026-KR-1-010 — Path × locale heatmap

**Goal:** At-a-glance matrix of pass rate by path (rows) and locale (columns).

**Priority:** P2 | **Effort:** M (~1.5 days)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/render_analysis_dashboard.py` | Add `render_path_locale_heatmap(path_rows)` → HTML table with color scale (CSS classes `heat-0` … `heat-100`). |
| `tools/test-suite/dashboard_assets/analysis_dashboard.css` | Heatmap cell colors (accessible contrast on dark theme). |
| `tools/test-suite/dashboard_assets/analysis_dashboard.js` | Optional: Chart.js matrix plugin or keep HTML-only for simplicity. |

**Acceptance criteria**

1. Heatmap appears in Path Performance section (table + heatmap toggle or sub-panel).
2. Comparison mode shows delta heatmap (green/red scale).
3. Print mode remains readable (EDU-2026-KR-1-014).

**Dependencies:** None.

---

### EDU-2026-KR-1-011 — Path family grouping in charts

**Goal:** Group paths for executive view: Internal search, Docs Assistant, External search, External LLMs.

**Priority:** P2 | **Effort:** S (~0.5 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/render_analysis_dashboard.py` | Add `PATH_FAMILY` map (`internal-search.*` → Internal, etc.). Add aggregated rows in view model or chart-only grouping in JS. |
| `tools/test-suite/dashboard_assets/analysis_dashboard.js` | Optional grouped bar chart by family. |

**Acceptance criteria**

1. Overview callout or chart shows family-level pass rate (weighted by query count).
2. Drill-down still available at path×locale level.

**Dependencies:** None.

---

## P3 — Unified UX and presentation

> **Completed phases (P3–P8):** Tasks in these sections are **done**. **Files to change** and **Acceptance criteria** preserve the original planning spec (imperative tense). **Delivered** summarizes what shipped; see [analysis-dashboard-improvements-report.md §3](analysis-dashboard-improvements-report.md#3-delivered-by-phase) for narrative detail by phase.

### EDU-2026-KR-1-012 — Shared dashboard shell and assets

**Status:** Complete (May 27, 2026)

**Delivered:** Shared `dashboard.css` and `dashboard_shared.js`; analysis-specific rules in `analysis_dashboard.css`; timeline template uses external CSS; `__RELATED_LINKS__` with `--related-timeline` / `--related-analysis` / `--related-comparison`; comparison dashboards auto-link baseline/candidate runs when present.

**Goal:** One visual system for analysis, comparison, and timeline dashboards.

**Priority:** P3 | **Effort:** L (~2–3 days)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/dashboard_assets/dashboard.css` | **New:** extract shared tokens, layout, tables, cards from `analysis_dashboard.css` and timeline inline styles. |
| `tools/test-suite/dashboard_assets/analysis_dashboard.css` | Import shared; keep analysis-specific rules only. |
| `tools/test-suite/dashboard_assets/timeline_dashboard.html` | Link external `dashboard.css` instead of large inline `<style>`. |
| `tools/test-suite/dashboard_assets/analysis_dashboard.html` | Add cross-mode links placeholder `__RELATED_LINKS__`. |
| `tools/test-suite/render_analysis_dashboard.py` | Populate related links when prior/next run paths passed via optional flags. |

**Acceptance criteria**

1. All three dashboards use same color tokens and typography.
2. Sidebar/nav pattern consistent between analysis and timeline.
3. No visual regression on existing published dashboards in `results/`.

**Dependencies:** None, but do after P0–P2 feature additions to avoid merge pain.

---

### EDU-2026-KR-1-013 — Presentation mode toggle

**Status:** Complete (May 27, 2026)

**Delivered:** Hero **Presentation mode** toggle on analysis, comparison, timeline, and multi-comparison dashboards; expands core sections and hides filters; preference stored in `localStorage`.

**Goal:** RFC §9 presentation workflow: one-click review layout.

**Priority:** P3 | **Effort:** M (~1 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/dashboard_assets/analysis_dashboard.html` | Button “Presentation mode” in hero. |
| `tools/test-suite/dashboard_assets/analysis_dashboard.js` | Toggle `body.presentation-mode`: expand overview + paths + locales; collapse failures/drilldown; hide filter controls. |
| `tools/test-suite/dashboard_assets/timeline_dashboard.html` | Same toggle. |
| `tools/test-suite/dashboard_assets/analysis_dashboard.css` | `.presentation-mode` rules: larger metric cards, simplified nav. |

**Acceptance criteria**

1. Toggle persists for session (optional: `localStorage`).
2. Core findings visible without scrolling past filters.
3. URL hash anchors still work.

**Dependencies:** EDU-2026-KR-1-012 optional.

---

### EDU-2026-KR-1-014 — Print and PDF-ready stylesheet

**Status:** Complete (May 27, 2026)

**Delivered:** Light-theme `@media print` rules, `beforeprint` panel expansion, heatmap colors preserved; browser **Print → Save as PDF** (no server-side PDF export).

**Goal:** RFC §9 print-friendly layout; Pedro deferred PDF export but print should work.

**Priority:** P3 | **Effort:** S (~0.5 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/dashboard_assets/analysis_dashboard.css` | Expand `@media print`: white bg, black text, page-break rules, hide sidebar, show all panel bodies, chart sizing. |
| `tools/test-suite/dashboard_assets/timeline_dashboard.html` | Print block in shared CSS. |

**Acceptance criteria**

1. Browser Print → PDF produces readable overview + path table + heatmap.
2. Charts not clipped across page breaks.

**Dependencies:** EDU-2026-KR-1-010 for heatmap print rules.

---

## P4 — Workflow and multi-run

### EDU-2026-KR-1-015 — Auto-render dashboard after analysis

**Status:** Complete (May 27, 2026)

**Delivered:** `--render-dashboard`, `--no-render-dashboard`, and `--render-dashboard-report` on `analysis_system.py` `run` / `compare` / `compare-chain` / `compare-all`; `run_all_runners.py` prompts whether to pass `--render-dashboard` before the analysis step (unless flags already set).

**Goal:** Dashboard is a default artifact, not a manual extra step.

**Priority:** P4 | **Effort:** S (~0.5 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/run_all_runners.py` | After successful `analysis_system.py run`, prompt “Render dashboard? [Y/n]” (mirror analysis prompt). Call `render_analysis_dashboard.py`. |
| `tools/test-suite/analysis_system.py` | Optional: `--render-dashboard` flag on `run` and `compare`. |

**Acceptance criteria**

1. Full pipeline can end with `dashboard/index.html` without separate command.
2. `--no-render-dashboard` skips for CI/automation.

**Dependencies:** None.

---

### EDU-2026-KR-1-016 — Analysis runs index page

**Status:** Complete (May 27, 2026)

**Delivered:** `--build-index` writes `results/analysis-system/index.html` — sortable table of runs with links to each `dashboard/index.html` (or generate hint when missing).

**Goal:** Browse all analysis runs and open dashboards from one HTML index.

**Priority:** P4 | **Effort:** M (~1 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/render_analysis_dashboard.py` | New command `--build-index` scanning `results/analysis-system/*/run_summary.json`. Write `results/analysis-system/index.html`. |
| `tools/test-suite/dashboard_assets/runs_index.html` | Template: table of run id, date, pass rate, MRR, link to `dashboard/index.html`. |

**Acceptance criteria**

1. Index lists all runs sorted by timestamp desc.
2. Rows without dashboard show “Generate” hint or grey link.

**Dependencies:** None.

---

### EDU-2026-KR-1-017 — Multi-comparison dashboard (`multi_comparison.json`)

**Status:** Complete (May 27, 2026)

**Delivered:** `--multi-comparison-run` reads `multi_comparison.json`; chain mode (step + cumulative deltas) and fan mode (vs shared baseline); path/locale charts and comparisons table (`multi_comparison_dashboard.html`).

**Goal:** Visualize `compare-chain` and `compare-all` output.

**Priority:** P4 | **Effort:** L (~2–3 days)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/render_analysis_dashboard.py` | New mode `--multi-comparison-run` reading `multi_comparison.json`. Build slope/step charts per path/locale across comparisons array. |
| `tools/test-suite/dashboard_assets/multi_comparison_dashboard.html` | New template (or extend timeline). |
| `docs/test-suite/analysis-system.md` | Document render command. |

**Acceptance criteria**

1. Fan mode (compare-all): cumulative delta from baseline across candidates.
2. Chain mode: step deltas between consecutive pairs.
3. Reuses timeline Chart.js patterns.

**Dependencies:** `compare-chain` / `compare-all` already implemented.

---

## P5 — Data quality and trust

### EDU-2026-KR-1-018 — Source-run health and comparison context warnings

**Status:** Complete (May 27, 2026)

**Delivered:** Overview warning banners (unhealthy/incomplete runs, low coverage, `n_not_available`); comparison warnings for mismatched sources/collection folders; highlighted source-run rows; baseline/candidate N/A cards; warnings copied into `summary.md` when `--report markdown`.

**Goal:** Prevent misreading metrics when underlying collection runs differ or are unhealthy.

**Priority:** P5 | **Effort:** M (~1 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/render_analysis_dashboard.py` | In overview: banner if any `selected_runs` has `is_healthy == false` or `is_full == false`. For comparison: diff `selected_runs` keys/paths between baseline and candidate; warn if different. |
| `tools/test-suite/dashboard_assets/analysis_dashboard.css` | `.warning-banner` styles. |

**Acceptance criteria**

1. Yellow banner on analysis dashboard when unhealthy source used.
2. Comparison dashboard warns when source run folders differ between baseline and candidate.
3. `n_not_available` surfaced in overview cards (already partially present — verify visible).

**Dependencies:** None.

---

## P6 — Discoverability

### EDU-2026-KR-1-019 — Metric tooltips and glossary panel

**Status:** Complete (May 27, 2026)

**Delivered:** `dashboard_glossary.py` as single source of truth; collapsible **How to read this dashboard** guide; `?` tooltips on cards, nav, tables, and chart toggles; comparison reading guide from `COMPARISON_READING_GUIDE`; `initHelpTips()` in `dashboard_shared.js`.

**Goal:** Help stakeholders read dashboards without opening the RFC — inline `?` tooltips on labels and a collapsible **How to read this dashboard** panel in Overview.

**Priority:** P6 | **Effort:** M (~1 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/dashboard_glossary.py` | **New** — `METRIC_HELP`, section/column/card label maps, per-mode `GUIDE_ENTRIES`, comparison reading guide text. |
| `tools/test-suite/render_analysis_dashboard.py` | `render_help_tip()`, `render_label_with_help()`, `render_metrics_guide()`, wire into cards, tables, nav, panels, chart toggles; `__METRICS_GUIDE__` for timeline/multi. |
| `tools/test-suite/dashboard_assets/dashboard.css` | `.help-tip`, `.metrics-guide`, `.reading-guide`; hide tooltips in print. |
| `tools/test-suite/dashboard_assets/dashboard_shared.js` | `initHelpTips()` — hover/focus + tap toggle on mobile. |
| `tools/test-suite/dashboard_assets/timeline_dashboard.html` | `__METRICS_GUIDE__` placeholder in Overview. |
| `tools/test-suite/dashboard_assets/multi_comparison_dashboard.html` | Same. |
| `docs/test-suite/analysis-dashboard.md` | Document tooltips and glossary maintenance. |

**Acceptance criteria**

1. Overview shows collapsible metrics guide (content varies by mode: analysis, comparison, timeline, multi-comparison).
2. Comparison dashboards show a short **How to read deltas** callout when applicable.
3. `?` icons on overview cards, section nav, panel titles, table headers, and chart view toggles (where wired).
4. Tooltips work via hover on desktop and tap on mobile; hidden when printing.
5. Glossary strings live in one Python module (no duplicated prose in HTML templates).

**Dependencies:** None.

---

## P7 — Navigation & onboarding

### EDU-2026-KR-1-020 — Hub navigation and comparisons index

**Status:** Complete (May 28, 2026)

**Delivered:** `results/analysis-system/index.html` and `results/analysis-system-comparisons/index.html`; **← All analysis runs** / **← All comparisons** on dashboards; cross-links to timeline and opposite hub; `--build-index` / `--build-comparisons-index`.

**Goal:** Let users move between analysis runs, comparison runs, and individual dashboards without browser back or memorizing folder paths.

**Priority:** P7 | **Effort:** M (~1 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/render_analysis_dashboard.py` | `render_dashboard_nav_html()`, `collect_dashboard_nav_crumbs()`, `write_comparisons_index()`, `scan_comparisons_for_index()`; extend `--build-index` to write both indexes; `--build-comparisons-index`. |
| `tools/test-suite/dashboard_assets/comparisons_index.html` | **New** — sortable comparisons table template. |
| `tools/test-suite/dashboard_assets/analysis_dashboard.html` | `__DASHBOARD_NAV__` placeholder. |
| `tools/test-suite/dashboard_assets/timeline_dashboard.html` | Same. |
| `tools/test-suite/dashboard_assets/multi_comparison_dashboard.html` | Same. |
| `tools/test-suite/dashboard_assets/runs_index.html` | `__DASHBOARD_NAV__` hub links. |
| `tools/test-suite/dashboard_assets/dashboard.css` | `.dashboard-nav`, `.dashboard-nav__back`, hub link styles. |
| `docs/test-suite/analysis-dashboard.md` | §4.1–4.2 hub navigation. |

**Acceptance criteria**

1. `results/analysis-system/index.html` lists analysis runs; **Also open** links to comparisons index and latest timeline when present.
2. `results/analysis-system-comparisons/index.html` lists pairwise and multi-comparison runs with **Also open** link to analysis runs index.
3. Analysis dashboards show **← All analysis runs**; comparison/multi dashboards show **← All comparisons**.
4. Timeline dashboards show **← All analysis runs** and current-page label.
5. `--build-index` refreshes both hub pages.

**Dependencies:** EDU-2026-KR-1-016 (analysis runs index).

---

### EDU-2026-KR-1-021 — In-dashboard onboarding (types + new audit workflow)

**Status:** Complete (May 28, 2026)

**Delivered:** Collapsible **About dashboards & how to run a new audit** on every hub and dashboard; types table and numbered audit workflow from `dashboard_glossary.py`; hub indexes open the panel expanded by default.

**Goal:** On-page explanation of dashboard types (analysis vs comparison vs timeline) and copy-paste steps to run a new search audit.

**Priority:** P7 | **Effort:** S (~0.5 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/dashboard_glossary.py` | `MODE_INTRO`, `DASHBOARD_TYPE_ROWS`, `AUDIT_WORKFLOW_STEPS`. |
| `tools/test-suite/render_analysis_dashboard.py` | `render_dashboard_help_panel()`, `render_dashboard_types_help_html()`, `render_audit_workflow_help_html()`; `__DASHBOARD_HELP__` on all templates. |
| `tools/test-suite/dashboard_assets/dashboard.css` | `.dashboard-help` panel styles. |
| `docs/test-suite/analysis-dashboard.md` | §4.1 in-dashboard help. |

**Acceptance criteria**

1. Collapsible **About dashboards & how to run a new audit** on every hub and dashboard page.
2. Table compares Latest Analysis Run, Comparison, Timeline, Multi-comparison (when to use each).
3. Numbered audit workflow with commands: collection → `analysis_system.py run` → `--build-index` → optional compare/timeline.
4. Hub indexes open the panel expanded by default.
5. Copy editable in `dashboard_glossary.py` only.

**Dependencies:** EDU-2026-KR-1-020 (users land on hubs first).

---

### EDU-2026-KR-1-022 — Help tooltip polish and batch re-render

**Status:** Complete (May 28, 2026)

**Delivered:** Viewport-fixed tooltips (`positionHelpTip()`); aligned `.th-label` / `.label-with-help`; `--rebuild-all-analysis-dashboards` and `--rebuild-all-comparison-dashboards` to refresh existing HTML after template changes.

**Goal:** Fix clipped/misaligned `?` tooltips; add CLI to refresh all existing HTML after template changes.

**Priority:** P7 | **Effort:** S (~0.5 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/dashboard_assets/dashboard.css` | `.help-tip` fixed layout; `.th-label` / `.label-with-help`; panel `overflow: visible`; tooltip `white-space: normal`. |
| `tools/test-suite/dashboard_assets/dashboard_shared.js` | `positionHelpTip()` viewport positioning on hover/focus/tap. |
| `tools/test-suite/dashboard_assets/analysis_dashboard.css` | Flex alignment on view-toggle / metric-toggle buttons. |
| `tools/test-suite/render_analysis_dashboard.py` | `.th-label` in table headers; `--rebuild-all-analysis-dashboards`, `--rebuild-all-comparison-dashboards`. |

**Acceptance criteria**

1. Tooltips in table headers (e.g. Style View → Target pass / Target MRR) fully visible and text wraps inside the box.
2. `?` icons align consistently in section nav, table headers, and toggle buttons.
3. `--rebuild-all-analysis-dashboards` re-renders every run under `results/analysis-system/` with `run_summary.json`.
4. `--rebuild-all-comparison-dashboards` re-renders every comparison folder with `comparison_summary.json` or `multi_comparison.json`.
5. Rebuilt dashboards include nav bar and help panel from 020–021.

**Dependencies:** EDU-2026-KR-1-019 (tooltips exist); EDU-2026-KR-1-020–021 (nav/help templates).

---

## P8 — Reliability & deep links

### EDU-2026-KR-1-023 — Stable timeline dashboard entry (`index.html`)

**Status:** Complete (May 28, 2026)

**Delivered:** `timeline-dashboard/index.html` redirects to the newest `timeline_*.html`; refreshed on each timeline render and via `--build-index`; analysis runs index links to this stable path.

**Goal:** Provide a fixed URL for the latest timeline dashboard instead of hunting timestamped filenames.

**Priority:** P8 | **Effort:** S (~0.25 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/render_analysis_dashboard.py` | `write_timeline_index_redirect()`, `refresh_timeline_index()`; call after `write_timeline_dashboard()` and `--build-index`. |
| `results/analysis-system/timeline-dashboard/index.html` | Generated redirect to latest `timeline_*.html`. |

**Acceptance criteria**

1. After rendering a timeline, `timeline-dashboard/index.html` redirects to the newest `timeline_*.html`.
2. Analysis runs index links to `timeline-dashboard/index.html` (stable path).
3. `--build-index` refreshes the redirect when timestamped timelines already exist.

**Dependencies:** EDU-2026-KR-1-016 / timeline dashboard mode.

---

### EDU-2026-KR-1-024 — Comparison index links to baseline/candidate analysis runs

**Status:** Complete (May 28, 2026)

**Delivered:** Comparisons hub **Baseline run** / **Candidate run** columns link to each run’s `dashboard/index.html` via `render_analysis_run_link()`; missing dashboards show label + re-render hint.

**Goal:** From the comparisons hub, open baseline and candidate **Latest Analysis Run** dashboards directly.

**Priority:** P8 | **Effort:** S (~0.25 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/render_analysis_dashboard.py` | `render_analysis_run_link()`; store `baseline_run_dir` / `candidate_run_dir` in index rows. |
| `tools/test-suite/dashboard_assets/comparisons_index.html` | Column headers: Baseline run / Candidate run. |

**Acceptance criteria**

1. Pairwise comparison rows link baseline and candidate cells to `…/dashboard/index.html` when present.
2. Missing analysis dashboards show run name with re-render hint (not a broken link).

**Dependencies:** EDU-2026-KR-1-020 (comparisons index).

---

### EDU-2026-KR-1-025 — Vendored Chart.js (offline-safe charts)

**Status:** Complete (May 28, 2026)

**Delivered:** Chart.js 4.4.1 UMD at `tools/test-suite/dashboard_assets/chart.umd.min.js`; copied into each dashboard `assets/` on render; templates load local `assets/chart.umd.min.js` (no jsDelivr CDN).

**Goal:** Charts work on `file://` without CDN/network access.

**Priority:** P8 | **Effort:** S (~0.25 day)

**Files to change**

| File | Change |
| :---- | :---- |
| `tools/test-suite/dashboard_assets/chart.umd.min.js` | **New** — Chart.js 4.4.1 UMD bundle (committed). |
| `tools/test-suite/render_analysis_dashboard.py` | `write_dashboard_assets()` copies `chart.umd.min.js` into each dashboard `assets/`. |
| `tools/test-suite/dashboard_assets/*.html` | `<script src="assets/chart.umd.min.js">` instead of jsDelivr CDN. |

**Acceptance criteria**

1. Analysis, comparison, timeline, and multi-comparison dashboards load Chart.js from local `assets/`.
2. Opening dashboards offline (or without CDN) still renders bar/line charts.
3. Rebuild copies updated vendor file into existing dashboard folders.

**Dependencies:** None.

---

## Delivery timeline (actual)

All phases **P0–P8** (tasks **EDU-2026-KR-1-001** through **025**) were completed in **two days** (May 27–28, 2026). See the [Decision log](#decision-log) below for the day-by-day breakdown.

| Date | Phases / tasks delivered |
| :---- | :---- |
| **May 27, 2026** | P0 (001–003), P1 (004–007), P2 (008–011), P3 (012–014), P4 (015–017), P5 (018), P6 (019) |
| **May 28, 2026** | P7 (020–022), P8 (023–025) |

**First slice shipped (May 27):** EDU-2026-KR-1-001 + 002 + 003 (top movers, Markdown summary, docs) — same bundle as originally proposed for Week 1.

For stakeholder-facing outcomes, use [analysis-dashboard-improvements-report.md](analysis-dashboard-improvements-report.md).

---

## Original planning estimate (superseded)

The schedule below was an **8-week hypothetical rollout** written when the backlog was created. It was **not** followed; delivery happened in the timeline above. Kept for historical context only.

```text
Week 1:  EDU-2026-KR-1-001 → EDU-2026-KR-1-002 → EDU-2026-KR-1-003
Week 2:  EDU-2026-KR-1-004 → EDU-2026-KR-1-007 → EDU-2026-KR-1-005
Week 3:  EDU-2026-KR-1-008 → EDU-2026-KR-1-009 → EDU-2026-KR-1-010
Week 4:  EDU-2026-KR-1-006 → EDU-2026-KR-1-011 → EDU-2026-KR-1-013 → EDU-2026-KR-1-014
Later:   EDU-2026-KR-1-012 → EDU-2026-KR-1-015 → EDU-2026-KR-1-016 → EDU-2026-KR-1-017 → EDU-2026-KR-1-018 → EDU-2026-KR-1-019
Post:    EDU-2026-KR-1-020 → EDU-2026-KR-1-021 → EDU-2026-KR-1-022
Polish:  EDU-2026-KR-1-023 → EDU-2026-KR-1-024 → EDU-2026-KR-1-025
```

---

## Jira / GitHub issue mapping (suggested)

| Task ID | Suggested title | Labels |
| :---- | :---- | :---- |
| EDU-2026-KR-1-001 | Comparison dashboard: top movers section | test-suite, dashboard |
| EDU-2026-KR-1-002 | Dashboard: auto-generated Markdown summary | test-suite, reporting |
| EDU-2026-KR-1-003 | Update analysis dashboard documentation | documentation |
| EDU-2026-KR-1-004 | Comparison artifacts for persona and cross-dimensions | test-suite, analysis |
| EDU-2026-KR-1-005 | Issue-level regression table in comparison | test-suite, dashboard |
| EDU-2026-KR-1-006 | Failure delta explorer for comparisons | test-suite, dashboard |
| EDU-2026-KR-1-007 | Locale gap view (ES vs EN) | test-suite, dashboard |
| EDU-2026-KR-1-008 | Single-run: style/persona/portal per locale | test-suite, dashboard |
| EDU-2026-KR-1-009 | MRR charts in analysis dashboard | test-suite, dashboard |
| EDU-2026-KR-1-010 | Path × locale heatmap | test-suite, dashboard |
| EDU-2026-KR-1-011 | Path family grouping in charts | test-suite, dashboard |
| EDU-2026-KR-1-012 | Unified dashboard CSS shell | test-suite, dashboard |
| EDU-2026-KR-1-013 | Presentation mode toggle | test-suite, dashboard |
| EDU-2026-KR-1-014 | Print-ready dashboard stylesheet | test-suite, dashboard |
| EDU-2026-KR-1-015 | Auto-render dashboard after analysis | test-suite, workflow |
| EDU-2026-KR-1-016 | Analysis runs index page | test-suite, dashboard |
| EDU-2026-KR-1-017 | Multi-comparison dashboard | test-suite, dashboard |
| EDU-2026-KR-1-018 | Source-run health warnings | test-suite, dashboard |
| EDU-2026-KR-1-019 | Metric tooltips and glossary | test-suite, dashboard, documentation |
| EDU-2026-KR-1-020 | Hub navigation and comparisons index | test-suite, dashboard |
| EDU-2026-KR-1-021 | In-dashboard onboarding panel | test-suite, dashboard, documentation |
| EDU-2026-KR-1-022 | Help tooltip polish and batch re-render | test-suite, dashboard |
| EDU-2026-KR-1-023 | Stable timeline index.html | test-suite, dashboard |
| EDU-2026-KR-1-024 | Comparison index baseline/candidate links | test-suite, dashboard |
| EDU-2026-KR-1-025 | Vendored Chart.js (offline charts) | test-suite, dashboard |

---

## Testing checklist (per task)

1. Render dashboard for `analysis-system 2026-05-21 16-54` (full aggregates).
2. Render comparison `analysis-system 2026-05-21 16-57` (Apr 30 vs May 21).
3. Render timeline with ≥3 runs including older runs without `aggregates_by_style_locale.json`.
4. Open `index.html` via `file://` in Chrome/Edge — no console errors.
5. Verify `summary.md` when `--report markdown` enabled.
6. Spot-check ES locale gap matches manual JSON inspection.

---

## Out of scope (per RFC)

- New scoring logic or AI answer quality visualization
- Live querying of external systems
- Full interactive app (Option B) unless Phase 2 revisits
- PDF export server-side (browser print only for Phase 1)

---

## Decision log

| Date | Decision |
| :---- | :---- |
| May 27, 2026 | Backlog created; P0 slice = movers + Markdown report + docs |
| May 27, 2026 | **EDU-2026-KR-1-001–003 done:** comparison top movers, `--report markdown`, docs/RFC sync |
| May 27, 2026 | **EDU-2026-KR-1-004–007 done:** persona/cross-dim comparison, issue regressions, failure delta, locale gap view |
| May 27, 2026 | **EDU-2026-KR-1-008–011 done:** cross-dim single-run, MRR toggle, heatmap, path families |
| | Keep static HTML architecture (RFC Option A) |
| May 27, 2026 | P3 complete: shared `dashboard.css`, presentation mode, print CSS (EDU-2026-KR-1-012–014) |
| | Timeline dashboard uses external CSS; cross-mode links via `--related-*` flags |
| May 27, 2026 | P4 complete: auto-render flags, runs index, multi-comparison dashboard (EDU-2026-KR-1-015–017) |
| May 27, 2026 | P5 complete: source-run health + comparison context warning banners (EDU-2026-KR-1-018) |
| May 27, 2026 | P6 complete: metric tooltips + Overview glossary panel (EDU-2026-KR-1-019) |
| May 28, 2026 | P7 complete: hub nav + comparisons index (020), onboarding panel (021), tooltip polish + batch re-render (022) |
| May 28, 2026 | P8 complete: stable timeline index (023), comparison deep links (024), vendored Chart.js (025) |
