# Dashboards

The test suite produces three types of HTML dashboards. They are static files — open them directly in a browser, no server needed.

---

## Overview

| Dashboard | What it answers | Where to find it |
| :--- | :--- | :--- |
| **Analysis Runs** | How good is discoverability right now? (per run) | `results/analysis-system/index.html` |
| **Comparison Runs** | What changed between two runs? | `results/analysis-system-comparisons/index.html` |
| **Timeline** | How have metrics evolved over time? | `results/analysis-system/timeline-dashboard/index.html` |

Each has an **index page** (hub) that links to individual dashboards.

---

## 1. Analysis Runs (`results/analysis-system/`)

### The index

Open `results/analysis-system/index.html` in your browser.

This is the main hub — a sortable table listing all analysis runs with:

- Date
- Target pass rate (%)
- MRR (Mean Reciprocal Rank)
- Total queries analyzed
- Link to each run's detailed dashboard

From here, you can also navigate to the **Comparisons hub** or the **Timeline dashboard** via the header links.

### Individual run dashboards

Click any run in the index to open its dashboard (`<run-folder>/dashboard/index.html`). Each run dashboard contains:

| Section | What it shows |
| :--- | :--- |
| **Overview** | Headline metrics (target pass rate, MRR, helpful pass rate), best/worst paths and locales |
| **Path Performance** | Bar charts and tables comparing each search channel |
| **Locale View** | How EN, PT, ES compare; locale gap vs. English |
| **Style View** | How naive/familiar/expert queries perform |
| **Persona View** | Performance grouped by user persona |
| **Worst Issues** | Issues with the lowest pass rates |
| **Failure Explorer** | Filterable list of every query that failed to find the target doc |
| **Issue Drilldown** | Searchable per-issue detail with classified link results |

**Interaction:** Tables are sortable. Use the section nav at the top to jump between sections. The "Presentation mode" button formats the dashboard for screen sharing.

### JSON files in each run folder

Each run folder also contains the raw JSON artifacts the dashboard is built from:

| File | Contents |
| :--- | :--- |
| `run_summary.json` | Run metadata, selected source runs, overall headline metrics |
| `issues_processed.json` | Full per-issue results: pass/fail, rank, classified links |
| `aggregates_by_path_locale.json` | Metrics by path and locale |
| `aggregates_by_locale.json` | Metrics by locale only |
| `aggregates_by_style.json` | Metrics by query style |
| `aggregates_by_persona.json` | Metrics by user persona |
| `failure_list.json` | All failing queries with issue/path/locale/style |

---

## 2. Comparison Runs (`results/analysis-system-comparisons/`)

### The index

Open `results/analysis-system-comparisons/index.html` in your browser.

Lists all comparison runs with:

- Type (Pairwise / Multi-chain / Multi-fan)
- Baseline and candidate run references
- Delta in target pass rate
- Link to each comparison dashboard

### Individual comparison dashboards

Click any comparison to open its dashboard. It shows:

| Section | What it shows |
| :--- | :--- |
| **Overview** | Delta cards (improvement/regression in pass rate, MRR) |
| **Top Movers** | Issues with the biggest positive or negative change |
| **Path/Locale/Style deltas** | Where improvements and regressions happened |
| **Failure Changes** | New failures, resolved failures, still failing |

**Reading the deltas:** Positive numbers (green) mean the candidate run improved over the baseline. Negative numbers (red) mean regression.

### Types of comparisons

| Type | What it compares |
| :--- | :--- |
| **Pairwise** | One baseline vs. one candidate (before/after) |
| **Chain** | Consecutive pairs (run1→run2, run2→run3, etc.) — shows step-by-step progression |
| **Fan** | Multiple candidates all compared against one baseline — shows cumulative progress |

### JSON files in each comparison folder

| File | Contents |
| :--- | :--- |
| `comparison_summary.json` | Overall metric deltas |
| `comparison_by_path_locale.json` | Deltas per path and locale |
| `comparison_by_issue.json` | Per-issue pass rate changes |
| `failure_delta.json` | Lists of `new_failures`, `resolved_failures`, `still_failing` |
| `multi_comparison.json` | (Multi only) All pairwise results in one file |

---

## 3. Timeline Dashboard (`results/analysis-system/timeline-dashboard/`)

### The index

Open `results/analysis-system/timeline-dashboard/index.html` — it redirects to the latest timeline snapshot.

The timeline shows how metrics evolved across multiple analysis runs as line charts:

| Section | What it shows |
| :--- | :--- |
| **Summary cards** | Latest metrics and delta vs. first run |
| **Overall Metrics** | Line chart of pass rate, MRR, helpful pass rate over time |
| **Pass Rate by Path** | How each channel's pass rate changed over time |
| **MRR by Path** | How rankings changed per channel |
| **By Locale / Style** | Trends broken down by locale and query style |
| **Top Movers** | Biggest improvements and regressions from first to last run |
| **Per-Issue Trends** | Table with sparklines showing each issue's evolution |
| **All Runs** | Full table of every run with metrics and delta highlighting |

Timeline snapshots are timestamped (`timeline_YYYY-MM-DD_HH-MM.html`) and never overwritten, so you keep a history of generated reports.

---

## How to generate dashboards

Dashboards are generated by the analysis and rendering scripts. Here are the key commands:

```powershell
# Generate analysis + dashboard for the latest collection run
python "tools/test-suite/analysis_system.py" run --render-dashboard

# Compare two runs and generate a comparison dashboard
python "tools/test-suite/analysis_system.py" compare `
  --baseline "results/analysis-system/<run-1>" `
  --candidate "results/analysis-system/<run-2>" `
  --render-dashboard

# Generate a timeline dashboard from multiple runs
python "tools/test-suite/render_analysis_dashboard.py" `
  --timeline-runs "results/analysis-system/<run-1>" `
                  "results/analysis-system/<run-2>" `
                  "results/analysis-system/<run-3>"

# Rebuild all index pages
python "tools/test-suite/render_analysis_dashboard.py" --build-index
```

---

## Tips for reading dashboards

1. **Start with the Timeline** to see overall trends — is discoverability improving or regressing?
2. **Use Comparisons** to understand what specific change caused an improvement or regression.
3. **Drill into individual runs** to investigate specific issues or paths that are underperforming.
4. **Use the Failure Explorer** to find exactly which queries are failing and why.
5. **Sort by delta** in comparison views to find the biggest wins and losses.
6. **Share via PDF** — use your browser's Print → Save as PDF for stakeholder reports.

All dashboards cross-link to each other (hub → runs, comparison → baseline/candidate runs, timeline → hub), so you can navigate without returning to the file system.
