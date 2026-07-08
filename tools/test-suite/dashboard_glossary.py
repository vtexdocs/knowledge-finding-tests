"""
Metric and section help text for analysis dashboards (EDU-2026-KR-1-019).

Single source of truth for tooltips and the Overview metrics guide panel.
"""

from __future__ import annotations

# Keys used by render_help_tip() — metric IDs, section IDs, or column label aliases.

METRIC_HELP: dict[str, str] = {
    "target_pass_rate": (
        "Share of tested queries where the expected target document appeared in the ranked links. "
        "Primary success metric for Phase 1 (exact target-doc match)."
    ),
    "target_pass_any_locale": (
        "Target pass rate counting equivalent target docs in other locales (e.g. ES doc counts for an EN query)."
    ),
    "target_mrr": (
        "Mean reciprocal rank of the best target doc in the result list. Higher is better (1.0 = always rank 1)."
    ),
    "helpful_pass_rate": (
        "Share of tested queries with at least one helpful (relevant, non-unrelated) link in the results."
    ),
    "any_relevant_rate": (
        "Share of queries where any target or helpful link appeared in the returned links."
    ),
    "any_relevant_any_locale": (
        "Any-relevant rate including target/helpful docs in locales other than the query locale."
    ),
    "not_available": (
        "Queries excluded from pass-rate denominators because the path/locale combination does not apply "
        "(e.g. path not run for that locale)."
    ),
    "delta_target_pass": (
        "Change in target pass rate: candidate minus baseline. Positive = improvement."
    ),
    "delta_target_mrr": (
        "Change in mean reciprocal rank of target docs. Positive = target docs rank higher on average."
    ),
    "delta_helpful_pass": (
        "Change in helpful pass rate. Positive = more queries found a helpful link."
    ),
    "delta_any_relevant": (
        "Change in any-relevant rate between runs."
    ),
    "baseline_not_available": (
        "Count of baseline queries marked not available (excluded from rates)."
    ),
    "candidate_not_available": (
        "Count of candidate queries marked not available (excluded from rates)."
    ),
    "mrr": (
        "Mean reciprocal rank — average of 1/rank for the best target document. Higher is better."
    ),
    "pass_rate": (
        "Percentage of tested queries that met the success condition for this slice."
    ),
    "locale_gap_es": (
        "Spanish pass rate minus English pass rate on the same path. Negative means ES lags EN."
    ),
    "locale_gap_pt": (
        "Portuguese pass rate minus English pass rate on the same path."
    ),
    "gap_delta": (
        "Change in locale gap from baseline to candidate. Positive = gap shrank (locale catching up to EN)."
    ),
    "tested": (
        "Number of query×style combinations actually evaluated for this row."
    ),
    "na": (
        "Queries not applicable for this path/locale (excluded from pass-rate calculation)."
    ),
    "nonempty_ratio": (
        "Share of queries that returned at least one non-empty result from the collection run."
    ),
    "is_healthy": (
        "Whether the underlying collection run passed health checks (complete, usable artifact)."
    ),
    "is_full": (
        "Whether the collection run reached the expected query count for that source."
    ),
    "top_movers": (
        "Largest target-pass changes between baseline and candidate, grouped by path×locale, locale, or style."
    ),
    "path_family": (
        "Discovery paths grouped into Internal search, Docs Assistant, External search, and External LLMs."
    ),
    "failure_delta": (
        "Queries that newly fail, were fixed, or still fail when comparing baseline vs candidate."
    ),
    "issue_regression": (
        "Per-issue change in aggregated pass rate between baseline and candidate runs."
    ),
    "heatmap": (
        "Color grid of pass rates (or deltas) by path row and locale column. Greener = higher / improved."
    ),
    "view_table": (
        "Sortable table of numeric metrics for this dimension."
    ),
    "view_bar": (
        "Bar chart of the same metrics for quick visual comparison."
    ),
    "view_heatmap": (
        "Heatmap view for path×locale patterns."
    ),
    "metric_toggle_pass": (
        "Chart Y-axis uses target pass rate (0–100%)."
    ),
    "metric_toggle_mrr": (
        "Chart Y-axis uses target MRR (0–1 scale)."
    ),
    "step_delta": (
        "Metric change for one comparison step (one baseline→candidate pair)."
    ),
    "cumulative_delta": (
        "Running sum of step deltas along a chain; fan mode shows each candidate vs the same baseline."
    ),
    "pp": (
        "Percentage points — absolute difference between two percentages (e.g. 40% to 45% = +5pp)."
    ),
    "total_runs": (
        "Number of analysis runs included in this timeline (first to last on the charts)."
    ),
    "comparison_mode": (
        "Whether comparisons are chained (A→B→C) or fan-shaped (one baseline vs many candidates)."
    ),
    "baseline_anchor": (
        "The shared baseline run used as the reference point in fan multi-comparison mode."
    ),
}

SECTION_HELP: dict[str, str] = {
    "overview": "Summary cards, callouts, data-quality warnings, and how to read this dashboard.",
    "paths": "Target pass and MRR broken down by discovery path and locale (e.g. hybrid-search / ES).",
    "path-families": "Metrics rolled up to Internal search, Docs Assistant, External search, and External LLMs.",
    "locales": "Aggregated performance per locale (EN, ES, PT) across paths.",
    "locale-gaps": "How much ES or PT pass rate differs from EN on each path — highlights locale underperformance.",
    "styles": "Performance by query style (naive, familiar, expert).",
    "personas": "Performance by learner persona from the issue catalog.",
    "styles-locale": "Pass rate for each query style within each locale.",
    "personas-locale": "Pass rate for each persona within each locale.",
    "portals": "Pass rate by documentation portal and locale.",
    "issues": "Issues with the lowest hit rates in this analysis run.",
    "failures": "Filterable list of queries that did not pass, with path, locale, and style.",
    "issue-detail": "Drill into one issue’s per-path and per-style breakdown.",
    "movers": "Biggest improvements and regressions in target pass rate between baseline and candidate.",
    "issue-comparison": "Issues with the largest pass-rate increases or decreases between runs.",
    "failure-delta": "New failures, resolved failures, and queries still failing after the change.",
    "overall-step": "Overall target pass and MRR change for each comparison step.",
    "overall-cumulative": "Cumulative overall change across consecutive comparisons (chain mode).",
    "paths-step": "Per path×locale step deltas for the top movers.",
    "paths-cumulative": "Cumulative per path×locale change across the comparison chain.",
    "locales-step": "Per-locale step deltas across comparisons.",
    "comparisons": "Table of each baseline→candidate pair with headline deltas.",
}

CARD_LABEL_HELP: dict[str, str] = {
    "Target pass rate": "target_pass_rate",
    "Target pass any locale": "target_pass_any_locale",
    "Target MRR": "target_mrr",
    "Helpful pass rate": "helpful_pass_rate",
    "Any relevant rate": "any_relevant_rate",
    "Any relevant any locale": "any_relevant_any_locale",
    "Not available": "not_available",
    "Delta target pass": "delta_target_pass",
    "Delta target MRR": "delta_target_mrr",
    "Delta helpful pass": "delta_helpful_pass",
    "Delta any relevant": "delta_any_relevant",
    "Baseline not available": "baseline_not_available",
    "Candidate not available": "candidate_not_available",
    "Total Runs": "total_runs",
    "Target Pass (latest)": "target_pass_rate",
    "MRR (latest)": "target_mrr",
    "Helpful Pass (latest)": "helpful_pass_rate",
    "Mode": "comparison_mode",
    "Baseline / anchor": "baseline_anchor",
    "Latest step delta": "delta_target_pass",
}

COLUMN_LABEL_HELP: dict[str, str] = {
    "Target pass": "pass_rate",
    "Target pass any locale": "target_pass_any_locale",
    "Target MRR": "target_mrr",
    "Helpful pass": "helpful_pass_rate",
    "Tested": "tested",
    "N/A": "na",
    "Delta target pass": "delta_target_pass",
    "Delta MRR": "delta_target_mrr",
    "Delta helpful pass": "delta_helpful_pass",
    "Baseline target pass": "pass_rate",
    "Candidate target pass": "pass_rate",
    "Delta tested": "tested",
    "ES − EN gap": "locale_gap_es",
    "PT − EN gap": "locale_gap_pt",
    "ES − EN": "locale_gap_es",
    "PT − EN": "locale_gap_pt",
    "ES − EN (candidate)": "locale_gap_es",
    "PT − EN (candidate)": "locale_gap_pt",
    "ES − EN (baseline)": "locale_gap_es",
    "Delta ES gap": "gap_delta",
    "Delta PT gap": "gap_delta",
    "Gap Δ": "gap_delta",
    "EN pass": "pass_rate",
    "ES pass": "pass_rate",
    "PT pass": "pass_rate",
    "Δ pass": "delta_target_pass",
    "Δ MRR": "delta_target_mrr",
    "Δ helpful": "delta_helpful_pass",
    "Hit rate": "pass_rate",
    "Misses": "pass_rate",
    "Nonempty ratio": "nonempty_ratio",
    "Healthy": "is_healthy",
    "Full": "is_full",
    "Locale": "locales",
    "Path": "paths",
    "Style": "styles",
    "Persona": "personas",
    "Link source": "paths",
}

GUIDE_ENTRIES: dict[str, list[tuple[str, str]]] = {
    "analysis": [
        ("Target pass rate", "target_pass_rate"),
        ("Target MRR", "target_mrr"),
        ("Helpful pass rate", "helpful_pass_rate"),
        ("Not available", "not_available"),
        ("Locale gap vs EN", "locale-gaps"),
        ("Path families", "path_family"),
        ("MRR vs pass rate charts", "metric_toggle_mrr"),
    ],
    "comparison": [
        ("Delta target pass", "delta_target_pass"),
        ("Positive delta", "delta_target_pass"),
        ("Top movers", "top_movers"),
        ("Failure changes", "failure_delta"),
        ("Locale gap vs EN", "locale-gaps"),
        ("Different collection runs", "is_healthy"),
    ],
    "timeline": [
        ("Target pass over time", "target_pass_rate"),
        ("Top movers (first vs last)", "top_movers"),
        ("Per-issue trends", "issue_regression"),
    ],
    "multi_comparison": [
        ("Step delta", "step_delta"),
        ("Cumulative delta", "cumulative_delta"),
        ("Chain vs fan mode", "cumulative_delta"),
    ],
}

COMPARISON_READING_GUIDE = (
    "This dashboard compares two processed analysis runs. "
    "<strong>Positive delta</strong> means the candidate run improved vs baseline. "
    "Metrics are link/rank only (Phase 1) — not AI answer quality. "
    "Check warning banners if collection runs or source folders differ between runs."
)

CALLOUT_LABEL_HELP: dict[str, str] = {
    "Best path": "paths",
    "Weakest path": "paths",
    "Best locale": "locales",
    "Weakest locale": "locales",
    "Hardest issue": "issues",
}

# In-dashboard guide for new users (dashboard types + audit workflow).

MODE_INTRO: dict[str, tuple[str, str]] = {
    "hub_analysis": (
        "Analysis runs index",
        "Lists every processed audit (analysis run). Open a row to see that run’s Latest Analysis Run dashboard.",
    ),
    "hub_comparisons": (
        "Comparison runs index",
        "Lists every baseline→candidate comparison and multi-comparison report. Open a row for the comparison dashboard.",
    ),
    "analysis": (
        "Latest Analysis Run",
        "A single audit snapshot: how search performed at one point in time (paths, locales, styles, issues).",
    ),
    "comparison": (
        "Analysis Comparison (pairwise)",
        "Exactly two runs — baseline (before) vs candidate (after). Shows deltas, top movers, and failure changes.",
    ),
    "timeline": (
        "Timeline",
        "Two or more analysis runs in date order. Shows trends over time (charts), not just one before/after pair.",
    ),
    "multi_comparison": (
        "Multi-comparison",
        "Several pairwise comparisons in one report (chain: A→B→C, or fan: many candidates vs one baseline).",
    ),
}

DASHBOARD_TYPE_ROWS: list[tuple[str, str, str, str]] = [
    (
        "Latest Analysis Run",
        "How good is search right now?",
        "One processed analysis run.",
        "results/analysis-system/<run>/dashboard/",
    ),
    (
        "Analysis Comparison",
        "What changed between two runs?",
        "analysis_system.py compare (baseline + candidate).",
        "results/analysis-system-comparisons/<comparison>/dashboard/",
    ),
    (
        "Timeline",
        "How do metrics evolve over many runs?",
        "Pick 2+ analysis runs; no compare step.",
        "results/analysis-system/timeline-dashboard/timeline_*.html",
    ),
    (
        "Multi-comparison",
        "Many steps vs one baseline?",
        "compare-chain or compare-all.",
        "results/analysis-system-comparisons/<run>/dashboard/",
    ),
]

AUDIT_WORKFLOW_STEPS: list[tuple[str, str, str]] = [
    (
        "Collect search results",
        "Run Phase 1 path runners (internal search, Docs Assistant, external search, LLMs) so raw "
        "results exist under <code>results/</code>. The full pipeline can do this for you.",
        "py tools/test-suite/run_all_runners.py",
    ),
    (
        "Process the audit (analysis run)",
        "Joins issue ground truth with collected links and writes aggregates under "
        "<code>results/analysis-system/</code>. Use <code>--render-dashboard</code> to build the HTML in the same step.",
        "py tools/test-suite/analysis_system.py run --render-dashboard",
    ),
    (
        "Refresh the runs index",
        "Updates the table on this hub page and cross-links to comparisons.",
        "py tools/test-suite/render_analysis_dashboard.py --build-index",
    ),
    (
        "Compare before vs after (optional)",
        "After a second analysis run, measure deltas between baseline and candidate.",
        "py tools/test-suite/analysis_system.py compare --baseline \"...\" --candidate \"...\" --render-dashboard",
    ),
    (
        "Timeline across runs (optional)",
        "Visualize trends when you have several analysis runs (oldest→newest).",
        "py tools/test-suite/render_analysis_dashboard.py --timeline-runs \"run-a\" \"run-b\" \"run-c\"",
    ),
]
