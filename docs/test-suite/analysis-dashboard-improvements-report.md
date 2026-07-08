# Analysis Dashboard Improvements — Progress Report

| Field | Value |
| :---- | :---- |
| Created | May 27, 2026 |
| Updated | May 28, 2026 |
| Status | **Complete** (P0–P8, EDU-2026-KR-1-001–025) |
| Related | [Improvements backlog](analysis-dashboard-improvements-backlog.md) |
| Related | [Analysis dashboard](analysis-dashboard.md) |

This report documents **what was delivered** for all dashboard improvement tasks (`EDU-2026-KR-1-001` through `EDU-2026-KR-1-025`). Use it for status updates, onboarding, and planning beyond Phase 1 visualization.

---

## 1. Executive summary

The search metrics visualization layer is implemented as **static HTML dashboards** (RFC Option A) with a shared visual shell, five render modes, two hub indexes (analysis + comparison runs), back navigation between pages, optional Markdown summaries, metric tooltips, and data-quality warnings.

**All backlog phases are complete (May 27–28, 2026):**

| Phase | Theme | Tasks | Outcome |
| :---- | :---- | :---- | :---- |
| **P0** | Quick wins | 001–003 | Top movers, `--report markdown`, docs/RFC sync |
| **P1** | Comparison parity | 004–007 | Persona/cross-dim compare, issue regressions, failure delta, locale gap |
| **P2** | Single-run depth | 008–011 | Cross-dim sections, MRR toggle, heatmap, path families |
| **P3** | Unified UX | 012–014 | Shared `dashboard.css`, presentation mode, print CSS |
| **P4** | Workflow | 015–017 | Auto-render flags, runs index, multi-comparison dashboard |
| **P5** | Data quality | 018 | Source-run health and comparison context warnings |
| **P6** | Discoverability | 019 | Metric tooltips and Overview glossary panel |
| **P7** | Navigation & onboarding | 020–022 | Hub indexes, back nav, onboarding panel, tooltip polish |
| **P8** | Reliability & deep links | 023–025 | Stable timeline URL, comparison run links, offline Chart.js |

**Primary script:** `tools/test-suite/render_analysis_dashboard.py`  
**Glossary:** `tools/test-suite/dashboard_glossary.py`  
**Analysis/compare:** `tools/test-suite/analysis_system.py`  
**Parent pipeline:** `tools/test-suite/run_all_runners.py` (optional dashboard prompt)

**Validation runs used throughout:**

- Single-run: `analysis-system 2026-05-21 16-54`
- Pairwise comparison: `analysis-system 2026-05-21 16-57` (Apr 30 vs May 21) and `analysis-system 2026-05-27 15-37`
- Multi-comparison: `analysis-system 2026-04-02 14-06` (chain), `analysis-system 2026-04-02 14-06 (1)` (fan)
- Timeline: Apr 30 → May 21 (2+ runs)

---

## 2. Status overview (all tasks)

| Task ID | Title | Status | Primary outputs |
| :---- | :---- | :---- | :---- |
| EDU-2026-KR-1-001 | Comparison Top movers | **Done** | Top Movers section, CSS, movers in `summary.md` |
| EDU-2026-KR-1-002 | Markdown executive summary | **Done** | `--report markdown`, `summary.md` per mode |
| EDU-2026-KR-1-003 | Documentation sync | **Done** | Updated docs + RFC status |
| EDU-2026-KR-1-004 | Persona & cross-dim comparison | **Done** | 3 JSON artifacts + 3 dashboard sections |
| EDU-2026-KR-1-005 | Issue-level regression list | **Done** | `comparison_by_issue.json` + dashboard table |
| EDU-2026-KR-1-006 | Failure delta explorer | **Done** | `failure_delta.json` + filterable panel |
| EDU-2026-KR-1-007 | Locale gap view (ES vs EN) | **Done** | Gap table in analysis + comparison |
| EDU-2026-KR-1-008 | Cross-dim single-run sections | **Done** | Styles/personas/portals per locale |
| EDU-2026-KR-1-009 | MRR chart toggle | **Done** | Pass rate / MRR toggle on path charts |
| EDU-2026-KR-1-010 | Path×locale heatmap | **Done** | Table / bar / heatmap views on paths |
| EDU-2026-KR-1-011 | Path family grouping | **Done** | Path Families section + overview callouts |
| EDU-2026-KR-1-012 | Unified dashboard CSS shell | **Done** | `dashboard.css`, timeline external CSS, related links |
| EDU-2026-KR-1-013 | Presentation mode toggle | **Done** | Hero toggle + `localStorage`, all main dashboards |
| EDU-2026-KR-1-014 | Print-ready stylesheet | **Done** | `@media print`, `beforeprint` panel expand |
| EDU-2026-KR-1-015 | Auto-render after analysis | **Done** | `--render-dashboard` on analysis_system + run_all_runners prompt |
| EDU-2026-KR-1-016 | Analysis runs index | **Done** | `--build-index` → `results/analysis-system/index.html` |
| EDU-2026-KR-1-017 | Multi-comparison dashboard | **Done** | `--multi-comparison-run`, chain/fan charts |
| EDU-2026-KR-1-018 | Source-run health warnings | **Done** | Warning banners in Overview + comparison source diff |
| EDU-2026-KR-1-019 | Metric tooltips and glossary | **Done** | `dashboard_glossary.py`, `?` tooltips, metrics guide panel |
| EDU-2026-KR-1-020 | Hub navigation and comparisons index | **Done** | Both hub indexes, back buttons, cross-links |
| EDU-2026-KR-1-021 | In-dashboard onboarding panel | **Done** | Types table + audit workflow in `dashboard_glossary.py` |
| EDU-2026-KR-1-022 | Help tooltip polish and batch re-render | **Done** | Fixed tooltips, `--rebuild-all-*` flags |
| EDU-2026-KR-1-023 | Stable timeline index.html | **Done** | `timeline-dashboard/index.html` → latest `timeline_*.html` |
| EDU-2026-KR-1-024 | Comparison index baseline/candidate links | **Done** | Comparisons hub links to analysis run dashboards |
| EDU-2026-KR-1-025 | Vendored Chart.js (offline charts) | **Done** | `assets/chart.umd.min.js` in every dashboard folder |

---

## 3. Delivered by phase

### P0 — Quick wins (001–003)

**001 — Comparison Top movers**

- `compute_comparison_movers()` and Top Movers panel in comparison dashboards.
- Surfaces largest target-pass improvements/regressions (path×locale, locale, style) with signed pp and baseline → candidate values.

**002 — Markdown executive summary**

- `--report markdown` writes `summary.md` beside each dashboard (analysis, comparison, timeline, multi-comparison).
- Replaces manual Slack/Jira write-ups with one command from the same data as the HTML dashboard.

**003 — Documentation sync**

- [analysis-dashboard.md](analysis-dashboard.md), [analysis-system.md](analysis-system.md), RFC, and backlog aligned with implementation.

**Regenerate example**

```powershell
py tools/test-suite/render_analysis_dashboard.py `
  --comparison-run "results/analysis-system-comparisons/analysis-system 2026-05-21 16-57" `
  --report markdown
```

**Sample comparison movers (Apr 30 → May 21)**

| Direction | Example |
| :---- | :---- |
| Improvement | llm.gemini / EN: +9.52pp (35.24% → 44.76%) |
| Regression | llm.chatgpt / PT: -22.81pp (82.46% → 59.65%) |

---

### P1 — Comparison parity (004–007)

**004 — Persona and cross-dimensional comparison**

| Artifact | Content |
| :---- | :---- |
| `comparison_by_persona.json` | Per-persona deltas |
| `comparison_by_style_locale.json` | Per (style, locale) deltas |
| `comparison_by_persona_locale.json` | Per (persona, locale) deltas |

Dashboard sections: Persona deltas, Style per locale, Persona per locale (table + chart toggle).

**005 — Issue-level regressions**

- `comparison_by_issue.json` + **Issue Regressions / Improvements** table (top deltas by issue).

**006 — Failure delta explorer**

- `failure_delta.json` (`new_failures`, `resolved_failures`, `still_failing`) + filterable **Failure Changes** panel.

**007 — Locale gap vs EN**

- `compute_locale_gaps()` — ES−EN and PT−EN pass-rate gaps per path in analysis and comparison dashboards.
- Supports the recurring ES-underperformance narrative without spreadsheet work.

**Regenerate flow**

```powershell
py tools/test-suite/analysis_system.py compare `
  --baseline "results/analysis-system/analysis-system 2026-04-30 15-00" `
  --candidate "results/analysis-system/analysis-system 2026-05-21 16-54"

py tools/test-suite/render_analysis_dashboard.py `
  --comparison-run "results/analysis-system-comparisons/<new-folder>" `
  --report markdown
```

---

### P2 — Single-run depth (008–011)

**008 — Cross-dimensions in single-run mode**

- Sections: **Styles per Locale**, **Personas per Locale**, **Portals by Locale** (with derivation fallback from `issues_processed.json` on older runs).

**009 — MRR chart toggle**

- Path performance: toggle **Pass rate** vs **MRR** on charts (`initPathMetricToggle` in `analysis_dashboard.js`).

**010 — Path×locale heatmap**

- Path sections: **Table / Bar / Heatmap** views; comparison heatmap uses delta coloring.

**011 — Path family grouping**

- **Path Families** section and overview callouts: Internal search, Docs Assistant, External search, External LLMs (weighted aggregates).

---

### P3 — Unified UX (012–014)

**012 — Shared dashboard shell**

| Asset | Role |
| :---- | :---- |
| `dashboard_assets/dashboard.css` | Shared tokens, layout, tables, timeline sidebar, warnings, print |
| `dashboard_assets/analysis_dashboard.css` | Analysis/comparison-specific (heatmap, drilldown, charts) |
| `dashboard_assets/dashboard_shared.js` | Presentation + print helpers |

- Timeline template uses external CSS (no large inline `<style>` block).
- `__RELATED_LINKS__` + CLI flags `--related-timeline`, `--related-analysis`, `--related-comparison`.
- Comparison auto-links baseline/candidate dashboards when present.

**013 — Presentation mode**

- Hero **Presentation mode** button; expands core sections, hides filters; persists in `localStorage`.
- Works on analysis, comparison, timeline, and multi-comparison dashboards.

**014 — Print-ready CSS**

- Light-theme `@media print`, panel body expansion, heatmap color preservation.
- Use browser **Print → Save as PDF** (server-side PDF export remains out of scope).

---

### P4 — Workflow (015–017)

**015 — Auto-render dashboard**

| Entry point | Behavior |
| :---- | :---- |
| `analysis_system.py run/compare/compare-chain/compare-all` | `--render-dashboard`, `--no-render-dashboard`, `--render-dashboard-report` |
| `run_all_runners.py` | Prompts “Render dashboard? [Y/n]” after analysis unless `--no-render-dashboard` |

**016 — Analysis runs index**

```powershell
py tools/test-suite/render_analysis_dashboard.py --build-index
```

- Writes `results/analysis-system/index.html` — sortable table of all analysis runs with links to `dashboard/index.html` or “Not generated” hint.
- Also writes `results/analysis-system-comparisons/index.html` (comparisons hub) with cross-links between indexes (extended in **020**).

**017 — Multi-comparison dashboard**

```powershell
py tools/test-suite/render_analysis_dashboard.py `
  --multi-comparison-run "results/analysis-system-comparisons/analysis-system 2026-04-02 14-06"
```

- Reads `multi_comparison.json` from `compare-chain` or `compare-all`.
- **Chain:** step deltas between consecutive pairs + cumulative sum.
- **Fan:** each candidate vs shared baseline.
- Charts: overall step/cumulative, path toggles, locale bars, comparisons table.

---

### P5 — Data quality (018)

**Source-run health and comparison context warnings**

Overview **warning banners** (yellow = warn, blue = info):

| Mode | Triggers |
| :---- | :---- |
| **Analysis** | Unhealthy source, incomplete run (`is_full`), low nonempty ratio (&lt;90%), `n_not_available` &gt; 0 |
| **Comparison** | Different source keys, different collection folders per source, health mismatch; plus baseline/candidate source-run tables |

- Unhealthy / not-full rows highlighted in source-run tables.
- Comparison adds **Baseline / Candidate not available** overview cards.
- Warnings included in `summary.md` when `--report markdown` is set.

---

### P6 — Discoverability (019)

**Metric tooltips and glossary panel**

- **`tools/test-suite/dashboard_glossary.py`** — single source of truth for metric definitions, section blurbs, table column help, and per-mode Overview guide bullets.
- **Inline `?` tooltips** on overview cards, section nav, panel summaries, sortable table headers, and chart view toggles (Table / Bar / Heatmap / Pass / MRR).
- **Overview “How to read this dashboard”** — collapsible `<details class="metrics-guide">` with mode-specific bullets (analysis, comparison, timeline, multi-comparison).
- **Comparison reading guide** — short delta interpretation callout on pairwise comparison dashboards.
- **CSS/JS** — `dashboard.css` (`.help-tip`, print hides tooltips); `dashboard_shared.js` (`initHelpTips()` for tap-to-toggle on mobile).

To change wording, edit `dashboard_glossary.py` and re-render dashboards.

---

### P7 — Navigation & onboarding (020–022)

**020 — Hub navigation and comparisons index**

| Page | Back / cross-links |
| :---- | :---- |
| Analysis runs index | **Also open:** All comparisons, Timeline (if generated) |
| Comparisons index | **Also open:** All analysis runs |
| Latest Analysis Run dashboard | **← All analysis runs** + current run id |
| Comparison / multi-comparison dashboard | **← All comparisons** + baseline vs candidate label |
| Timeline dashboard | **← All analysis runs** + “Timeline” label |

- `write_comparisons_index()` → `results/analysis-system-comparisons/index.html`
- `--build-index` writes both hub pages; `--build-comparisons-index` for comparisons only
- Templates: `comparisons_index.html`, `__DASHBOARD_NAV__` on all dashboard shells

**021 — In-dashboard onboarding panel**

Collapsible **About dashboards & how to run a new audit** on every hub and dashboard (`render_dashboard_help_panel()`).

| Content | Source in `dashboard_glossary.py` |
| :---- | :---- |
| Intro for this page type | `MODE_INTRO` |
| Dashboard types table (analysis vs comparison vs timeline) | `DASHBOARD_TYPE_ROWS` |
| Steps to run a new audit | `AUDIT_WORKFLOW_STEPS` |

Hub indexes open the panel expanded by default.

**022 — Help tooltip polish and batch re-render**

- Viewport-fixed tooltips (`positionHelpTip()` in `dashboard_shared.js`) — no clipping in tables/panels
- `.th-label` / `.label-with-help` for aligned `?` icons; wrapped tooltip text
- `--rebuild-all-analysis-dashboards` and `--rebuild-all-comparison-dashboards` refresh all existing HTML

```powershell
py tools/test-suite/render_analysis_dashboard.py --build-index
py tools/test-suite/render_analysis_dashboard.py --rebuild-all-analysis-dashboards
py tools/test-suite/render_analysis_dashboard.py --rebuild-all-comparison-dashboards
```

---

### P8 — Reliability & deep links (023–025)

**023 — Stable timeline dashboard entry**

- `timeline-dashboard/index.html` meta-refreshes to the newest `timeline_*.html` (updated on each timeline render and by `--build-index`).
- Analysis runs index and `find_timeline_dashboard()` use this stable path instead of a hard-coded timestamped filename.

**024 — Comparison index deep links**

- Pairwise rows on the comparisons hub link **Baseline run** and **Candidate run** to each run’s `dashboard/index.html` when it exists (`render_analysis_run_link()`).
- Missing dashboards show the run label with a re-render hint instead of a broken link.

**025 — Vendored Chart.js**

- Chart.js 4.4.1 UMD bundle committed at `tools/test-suite/dashboard_assets/chart.umd.min.js`.
- `write_dashboard_assets()` copies it into each dashboard `assets/` folder; templates load `assets/chart.umd.min.js` (no CDN).
- Charts work on `file://` without network access after rebuild.

---

## 4. Dashboard modes (reference)

| Mode | CLI | Default output |
| :---- | :---- | :---- |
| Single-run | `--analysis-run <dir>` | `<run>/dashboard/index.html` |
| Comparison | `--comparison-run <dir>` | `<comparison>/dashboard/index.html` |
| Timeline | `--timeline-runs <dir> ...` (≥2) | `timeline-dashboard/timeline_YYYY-MM-DD_HH-MM.html` (+ `index.html` redirect) |
| Multi-comparison | `--multi-comparison-run <dir>` | `<comparison>/dashboard/index.html` |
| Runs index | `--build-index` | `results/analysis-system/index.html` |
| Comparisons index | `--build-index` or `--build-comparisons-index` | `results/analysis-system-comparisons/index.html` |

**Shared assets per dashboard folder:** `assets/dashboard.css`, `assets/dashboard_shared.js`, `assets/chart.umd.min.js`, plus mode-specific JS/CSS as needed.

**Hub assets:** `dashboard.css` copied beside each `index.html` under `results/analysis-system/` and `results/analysis-system-comparisons/`.

---

## 5. Output inventory (repo examples)

| Type | Path |
| :---- | :---- |
| Analysis runs index | `results/analysis-system/index.html` |
| Comparisons index | `results/analysis-system-comparisons/index.html` |
| Single-run dashboard | `results/analysis-system/analysis-system 2026-05-21 16-54/dashboard/index.html` |
| Single-run summary | `results/analysis-system/analysis-system 2026-05-21 16-54/dashboard/summary.md` |
| Comparison dashboard | `results/analysis-system-comparisons/analysis-system 2026-05-27 15-37/dashboard/index.html` |
| Comparison summary | `results/analysis-system-comparisons/analysis-system 2026-05-27 15-37/dashboard/summary.md` |
| Timeline dashboard (stable entry) | `results/analysis-system/timeline-dashboard/index.html` → latest `timeline_*.html` |
| Timeline dashboard (snapshot) | `results/analysis-system/timeline-dashboard/timeline_2026-05-28_12-33.html` |
| Timeline summary | `results/analysis-system/timeline-dashboard/summary.md` |
| Multi-comparison (chain) | `results/analysis-system-comparisons/analysis-system 2026-04-02 14-06/dashboard/index.html` |
| Multi-comparison (fan) | `results/analysis-system-comparisons/analysis-system 2026-04-02 14-06 (1)/dashboard/index.html` |

---

## 6. Common commands

```powershell
# Full pipeline with dashboard prompt at the end
py tools/test-suite/run_all_runners.py --include analysis

# Analysis + dashboard in one step
py tools/test-suite/analysis_system.py run --render-dashboard --render-dashboard-report

# Compare + dashboard
py tools/test-suite/analysis_system.py compare `
  --baseline "results/analysis-system/analysis-system 2026-04-30 15-00" `
  --candidate "results/analysis-system/analysis-system 2026-05-21 16-54" `
  --render-dashboard --render-dashboard-report

# Re-render only (no re-analysis)
py tools/test-suite/render_analysis_dashboard.py --build-index
py tools/test-suite/render_analysis_dashboard.py --rebuild-all-analysis-dashboards
py tools/test-suite/render_analysis_dashboard.py --rebuild-all-comparison-dashboards
py tools/test-suite/render_analysis_dashboard.py --analysis-run "results/analysis-system/analysis-system 2026-05-21 16-54" --report markdown
py tools/test-suite/render_analysis_dashboard.py --comparison-run "results/analysis-system-comparisons/analysis-system 2026-05-27 15-37" --report markdown
py tools/test-suite/render_analysis_dashboard.py --timeline-runs "results/analysis-system/analysis-system 2026-04-30 15-00" "results/analysis-system/analysis-system 2026-05-21 16-54"
py tools/test-suite/render_analysis_dashboard.py --multi-comparison-run "results/analysis-system-comparisons/analysis-system 2026-04-02 14-06"
```

Open dashboards via `file://` in Chrome/Edge. Start from **Analysis runs** or **Comparisons** index for navigation. Expand **About dashboards & how to run a new audit** for types and audit commands. Use **Presentation mode** for reviews and **Print** for PDF export.

---

## 7. Maintenance

1. After new analysis or comparison runs: `py tools/test-suite/render_analysis_dashboard.py --build-index` (updates both hub indexes).
2. After changing `render_analysis_dashboard.py`, `dashboard_glossary.py`, or `dashboard_assets/`: use `--rebuild-all-analysis-dashboards` and/or `--rebuild-all-comparison-dashboards`, then `--build-index` if timeline was regenerated.
3. Edit onboarding copy in `dashboard_glossary.py` (`MODE_INTRO`, `DASHBOARD_TYPE_ROWS`, `AUDIT_WORKFLOW_STEPS`) and re-render affected HTML.
4. Older runs without `aggregates_by_style_locale.json` still work (derivation from `issues_processed.json`).

---

## 8. Out of scope (unchanged)

- New scoring logic or AI answer quality visualization
- Live querying of external systems
- Full interactive app (Option B)
- Server-side PDF export

---

## 9. References

- [Improvements backlog](analysis-dashboard-improvements-backlog.md) — task specs and acceptance criteria
- [Analysis dashboard doc](analysis-dashboard.md) — usage, modes, warnings
- [Analysis system doc](analysis-system.md) — compare commands and artifact layout
