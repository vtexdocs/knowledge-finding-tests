#!/usr/bin/env python3
"""
Render a static HTML dashboard from processed analysis-system outputs.

The dashboard is written directly into the corresponding analysis run folder:

- results/analysis-system/<run>/dashboard/
- results/analysis-system-comparisons/<run>/dashboard/
"""

from __future__ import annotations

import argparse
import html
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dashboard_glossary import (
    AUDIT_WORKFLOW_STEPS,
    CALLOUT_LABEL_HELP,
    CARD_LABEL_HELP,
    COLUMN_LABEL_HELP,
    COMPARISON_READING_GUIDE,
    DASHBOARD_TYPE_ROWS,
    GUIDE_ENTRIES,
    METRIC_HELP,
    MODE_INTRO,
    SECTION_HELP,
)


@dataclass(frozen=True)
class DashboardContext:
    mode: str
    run_dir: Path
    output_dir: Path


def workspace_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def assets_source_dir() -> Path:
    return Path(__file__).resolve().parent / "dashboard_assets"


CHART_JS_VENDOR = "chart.umd.min.js"


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def escape(value: Any) -> str:
    return html.escape(str(value))


def help_text(key: str) -> str:
    return METRIC_HELP.get(key) or SECTION_HELP.get(key, "")


def resolve_help_key(label_or_key: str, explicit: str | None = None) -> str | None:
    if explicit and help_text(explicit):
        return explicit
    if help_text(label_or_key):
        return label_or_key
    for mapping in (CARD_LABEL_HELP, COLUMN_LABEL_HELP, CALLOUT_LABEL_HELP):
        if label_or_key in mapping:
            resolved = mapping[label_or_key]
            if help_text(resolved):
                return resolved
    return None


def render_help_tip(key: str, *, aria_label: str | None = None) -> str:
    text = help_text(key)
    if not text:
        return ""
    return (
        '<span class="help-tip" tabindex="0" data-help-tip>'
        '<span class="help-tip__icon" aria-hidden="true">?</span>'
        f'<span class="help-tip__popup" role="tooltip">{escape(text)}</span>'
        "</span>"
    )


def render_label_with_help(label: str, help_key: str | None = None) -> str:
    key = resolve_help_key(label, help_key)
    tip = render_help_tip(key, aria_label=label) if key else ""
    return f'<span class="label-with-help">{escape(label)}{tip}</span>'


def apply_column_help_keys(columns: list[dict[str, Any]]) -> None:
    for column in columns:
        if column.get("help_key"):
            continue
        resolved = COLUMN_LABEL_HELP.get(column["label"])
        if resolved:
            column["help_key"] = resolved


def render_metrics_guide(mode: str) -> str:
    entries = GUIDE_ENTRIES.get(mode, GUIDE_ENTRIES.get("analysis", []))
    items: list[str] = []
    for title, key in entries:
        text = help_text(key)
        if text:
            items.append(f"<li><strong>{escape(title)}</strong> — {escape(text)}</li>")
    if not items:
        return ""
    return (
        '<details class="metrics-guide">'
        "<summary>How to read this dashboard</summary>"
        f'<ul class="metrics-guide__list">{"".join(items)}</ul>'
        '<p class="metrics-guide__note">Tip: hover or tap the '
        '<span class="help-tip__icon" aria-hidden="true">?</span> next to labels for definitions.</p>'
        "</details>"
    )


def render_comparison_reading_guide() -> str:
    return (
        '<div class="reading-guide">'
        f'<p class="reading-guide__text">{COMPARISON_READING_GUIDE}</p>'
        "</div>"
    )


def render_dashboard_types_help_html() -> str:
    rows = "".join(
        "<tr>"
        f"<td><strong>{row[0]}</strong></td>"
        f"<td>{escape(row[1])}</td>"
        f"<td>{escape(row[2])}</td>"
        f"<td><code>{escape(row[3])}</code></td>"
        "</tr>"
        for row in DASHBOARD_TYPE_ROWS
    )
    return (
        '<section class="dashboard-help__section">'
        "<h3>Dashboard types</h3>"
        '<div class="table-wrap dashboard-help__table-wrap">'
        '<table class="data-table data-table--compact dashboard-help__table">'
        "<thead><tr><th>Type</th><th>Answers</th><th>Needs</th><th>Output</th></tr></thead>"
        f"<tbody>{rows}</tbody>"
        "</table>"
        "</div>"
        '<p class="dashboard-help__note">'
        "<strong>Comparison vs timeline:</strong> comparison is for one change (two runs, deltas). "
        "Timeline is for many checkpoints over time (line charts, first→last movers). "
        "Phase 1 metrics are target-doc pass rate and MRR on links — not AI answer quality."
        "</p>"
        "</section>"
    )


def render_audit_workflow_help_html() -> str:
    steps = "".join(
        "<li>"
        f"<strong>{escape(title)}</strong> — {body}"
        f'<pre class="dashboard-help__cmd"><code>{escape(cmd)}</code></pre>'
        "</li>"
        for title, body, cmd in AUDIT_WORKFLOW_STEPS
    )
    return (
        '<section class="dashboard-help__section">'
        "<h3>How to add a new search audit to the dashboard</h3>"
        f'<ol class="dashboard-help__steps">{steps}</ol>'
        '<p class="dashboard-help__note">'
        "Docs: <code>docs/test-suite/analysis-system.md</code> and "
        "<code>docs/test-suite/analysis-dashboard.md</code>. "
        "Re-render existing HTML after code changes: "
        "<code>--rebuild-all-analysis-dashboards</code> or "
        "<code>--rebuild-all-comparison-dashboards</code>."
        "</p>"
        "</section>"
    )


def render_dashboard_help_panel(
    mode: str,
    *,
    open_by_default: bool = False,
) -> str:
    intro = MODE_INTRO.get(mode, MODE_INTRO["analysis"])
    open_attr = " open" if open_by_default else ""
    return (
        f'<details class="dashboard-help"{open_attr}>'
        "<summary>About dashboards &amp; how to run a new audit</summary>"
        '<div class="dashboard-help__body">'
        f'<p class="dashboard-help__intro"><strong>{escape(intro[0])}</strong> — {escape(intro[1])}</p>'
        f"{render_dashboard_types_help_html()}"
        f"{render_audit_workflow_help_html()}"
        "</div>"
        "</details>"
    )


def relative_display(path: Path) -> str:
    root = workspace_root()
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def percent_text(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value * 100:.2f}%"


def decimal_text(value: float | None) -> str:
    if value is None:
        return "-"
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text or "0"


def int_text(value: int | None) -> str:
    if value is None:
        return "-"
    return f"{value:,}"


def metric_chip(value: float | None, kind: str) -> str:
    if kind == "percent":
        display = percent_text(value)
        css = "metric-chip"
    elif kind == "decimal":
        display = decimal_text(value)
        css = "metric-chip metric-chip--warm"
    else:
        display = escape(value if value is not None else "-")
        css = "metric-chip metric-chip--neutral"
    return f'<span class="{css}">{display}</span>'


def render_card_grid(cards: list[dict[str, str]]) -> str:
    items = []
    for card in cards:
        items.append(
            f"""
            <article class="metric-card">
              <p class="metric-card__label">{render_label_with_help(card["label"], card.get("help_key"))}</p>
              <p class="metric-card__value">{escape(card["value"])}</p>
              <p class="metric-card__note">{escape(card["note"])}</p>
            </article>
            """
        )
    return f'<div class="card-grid">{"".join(items)}</div>'


def render_callouts(callouts: list[dict[str, str]]) -> str:
    if not callouts:
        return ""
    items = []
    for callout in callouts:
        items.append(
            f"""
            <article class="callout-card">
              <p class="callout-card__label">{render_label_with_help(callout["label"])}</p>
              <p class="callout-card__value">{escape(callout["value"])}</p>
              <p class="callout-card__note">{escape(callout["note"])}</p>
            </article>
            """
        )
    return f'<div class="callout-grid">{"".join(items)}</div>'


def render_bullet_list(items: list[str]) -> str:
    if not items:
        return ""
    rows = "".join(f"<li>{escape(item)}</li>" for item in items)
    return f'<ul class="bullet-list">{rows}</ul>'


def sort_button(label: str, help_key: str | None = None) -> str:
    tip = render_help_tip(help_key, aria_label=label) if help_key else ""
    return f'<button class="sort-button" type="button">{escape(label)}</button>{tip}'


def render_table(columns: list[dict[str, Any]], rows: list[dict[str, Any]], compact: bool = False) -> str:
    table_class = "data-table js-sortable"
    if compact:
        table_class += " data-table--compact"

    apply_column_help_keys(columns)
    header = "".join(
        f'<th><span class="th-label">{sort_button(column["label"], column.get("help_key"))}</span></th>'
        for column in columns
    )
    body_rows: list[str] = []
    for row in rows:
        cells: list[str] = []
        for column in columns:
            value = row.get(column["key"])
            sort_value = "" if value is None else value
            kind = column.get("kind", "text")
            if kind == "percent":
                display = metric_chip(float(value) if value is not None else None, "percent")
            elif kind == "decimal":
                display = metric_chip(float(value) if value is not None else None, "decimal")
            elif kind == "int":
                display = int_text(int(value) if value is not None else None)
            else:
                display = escape(value if value not in (None, "") else "-")
            css_class = row.get(column["css_key"], "") if column.get("css_key") else ""
            class_attr = f' class="{escape(css_class)}"' if css_class else ""
            cells.append(f"<td{class_attr} data-sort=\"{escape(sort_value)}\">{display}</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")

    body = "".join(body_rows) or f'<tr><td colspan="{len(columns)}" class="empty-state">No data available.</td></tr>'
    return (
        '<div class="table-wrap">'
        f'<table class="{table_class}"><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>'
        "</div>"
    )


def render_panel(section_id: str, title: str, body_html: str, open_by_default: bool = True) -> str:
    open_attr = " open" if open_by_default else ""
    return (
        f'<details class="panel" id="{escape(section_id)}"{open_attr}>'
        f"<summary>{render_label_with_help(title, section_id)}</summary>"
        f'<div class="panel__body">{body_html}</div>'
        "</details>"
    )


def load_asset(name: str) -> str:
    return (assets_source_dir() / name).read_text(encoding="utf-8")


def chart_js_source_path() -> Path:
    path = assets_source_dir() / CHART_JS_VENDOR
    if not path.exists():
        raise FileNotFoundError(
            f"Missing vendored Chart.js at {path}. "
            f"Download chart.umd.min.js into tools/test-suite/dashboard_assets/."
        )
    return path


def write_dashboard_assets(output_assets_dir: Path, *, include_analysis_css: bool = False) -> None:
    output_assets_dir.mkdir(parents=True, exist_ok=True)
    write_text(output_assets_dir / "dashboard.css", load_asset("dashboard.css"))
    write_text(output_assets_dir / "dashboard_shared.js", load_asset("dashboard_shared.js"))
    write_text(output_assets_dir / CHART_JS_VENDOR, chart_js_source_path().read_text(encoding="utf-8"))
    if include_analysis_css:
        write_text(output_assets_dir / "analysis_dashboard.css", load_asset("analysis_dashboard.css"))
        write_text(output_assets_dir / "dashboard.js", load_asset("analysis_dashboard.js"))


def resolve_dashboard_index(path: Path) -> Path:
    resolved = path.resolve()
    if resolved.is_file():
        return resolved
    index = resolved / "index.html"
    if index.exists():
        return index
    timelines = sorted(resolved.glob("timeline_*.html"), reverse=True)
    if timelines:
        return timelines[0]
    raise FileNotFoundError(f"No dashboard index found under {resolved}")


def dashboard_href(from_dir: Path, target_index: Path) -> str:
    return os.path.relpath(target_index.resolve(), from_dir.resolve()).replace("\\", "/")


def analysis_runs_index_path() -> Path | None:
    index = workspace_root() / "results" / "analysis-system" / "index.html"
    return index if index.exists() else None


def comparisons_index_path() -> Path | None:
    index = workspace_root() / "results" / "analysis-system-comparisons" / "index.html"
    return index if index.exists() else None


def default_comparisons_root() -> Path:
    return workspace_root() / "results" / "analysis-system-comparisons"


def find_latest_timeline_html(analysis_root: Path | None = None) -> Path | None:
    root = analysis_root or (workspace_root() / "results" / "analysis-system")
    timeline_dir = root / "timeline-dashboard"
    if not timeline_dir.is_dir():
        return None
    timelines = sorted(timeline_dir.glob("timeline_*.html"), reverse=True)
    return timelines[0] if timelines else None


def find_timeline_dashboard(analysis_root: Path | None = None) -> Path | None:
    root = analysis_root or (workspace_root() / "results" / "analysis-system")
    timeline_dir = root / "timeline-dashboard"
    if not timeline_dir.is_dir():
        return None
    index = timeline_dir / "index.html"
    if index.exists():
        return index
    return find_latest_timeline_html(analysis_root)


def write_timeline_index_redirect(timeline_dir: Path, latest_filename: str) -> Path:
    """Write stable index.html that redirects to the latest timestamped timeline file."""
    safe_name = Path(latest_filename).name
    html = (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\" />\n"
        f"<meta http-equiv=\"refresh\" content=\"0; url={escape(safe_name)}\" />\n"
        "<title>Timeline Dashboard</title>\n"
        "<link rel=\"stylesheet\" href=\"assets/dashboard.css\" />\n"
        "</head>\n<body>\n"
        "<p class=\"lede\">Redirecting to the latest timeline dashboard: "
        f"<a href=\"{escape(safe_name)}\">{escape(safe_name)}</a></p>\n"
        "</body>\n</html>\n"
    )
    index_path = timeline_dir / "index.html"
    write_text(index_path, html)
    return index_path


def refresh_timeline_index(analysis_root: Path | None = None) -> Path | None:
    latest = find_latest_timeline_html(analysis_root)
    if not latest:
        return None
    return write_timeline_index_redirect(latest.parent, latest.name)


def _nav_href(output_dir: Path, target: Path) -> str:
    try:
        index = resolve_dashboard_index(target)
    except FileNotFoundError:
        index = target
    return dashboard_href(output_dir, index)


def collect_dashboard_nav_crumbs(
    output_dir: Path,
    *,
    mode: str,
    view_model: dict[str, Any] | None = None,
    run_dir: Path | None = None,
) -> list[tuple[str, Path | None]]:
    crumbs: list[tuple[str, Path | None]] = []
    runs_index = analysis_runs_index_path()
    comparisons_index = comparisons_index_path()
    output_file = output_dir / "index.html" if output_dir.is_dir() else output_dir
    output_resolved = output_file.resolve()
    on_runs_index = runs_index and output_resolved == runs_index.resolve()
    on_comparisons_index = comparisons_index and output_resolved == comparisons_index.resolve()

    if mode in ("comparison", "multi_comparison") and comparisons_index and not on_comparisons_index:
        crumbs.append(("All comparisons", comparisons_index))
    elif runs_index and not on_runs_index and not on_comparisons_index:
        crumbs.append(("All analysis runs", runs_index))

    current_label: str | None = None
    if mode == "analysis" and view_model:
        current_label = view_model.get("meta", {}).get("run_id") or run_dir.name if run_dir else "Analysis run"
    elif mode == "comparison":
        current_label = run_dir.name if run_dir else "Comparison"
        if view_model:
            meta = view_model.get("meta", {})
            baseline = Path(meta["baseline_run_dir"]).name if meta.get("baseline_run_dir") else ""
            candidate = Path(meta["candidate_run_dir"]).name if meta.get("candidate_run_dir") else ""
            if baseline and candidate:
                current_label = f"{baseline} vs {candidate}"
    elif mode == "timeline":
        current_label = "Timeline"
    elif mode == "multi_comparison":
        current_label = run_dir.name if run_dir else "Multi-comparison"
    elif mode == "index":
        return []

    if current_label:
        crumbs.append((current_label, None))
    return crumbs


def collect_runs_index_hub_links() -> list[tuple[str, Path]]:
    links: list[tuple[str, Path]] = []
    comparisons_index = comparisons_index_path()
    if comparisons_index:
        links.append(("All comparisons", comparisons_index))
    timeline = find_timeline_dashboard()
    if timeline:
        links.append(("Timeline dashboard", timeline))
    return links


def resolve_analysis_run_path(run_dir_str: str) -> Path | None:
    if not run_dir_str or not str(run_dir_str).strip():
        return None
    path = Path(run_dir_str)
    if not path.is_absolute():
        path = workspace_root() / path
    return path.resolve() if path.is_dir() else None


def render_analysis_run_link(index_dir: Path, run_dir_str: str, fallback_label: str) -> str:
    run_path = resolve_analysis_run_path(run_dir_str)
    label = fallback_label or (run_path.name if run_path else "-")
    if not run_path:
        return escape(label)
    dashboard = run_path / "dashboard" / "index.html"
    if dashboard.exists():
        href = dashboard_href(index_dir, dashboard)
        return f'<a href="{escape(href)}" title="Latest Analysis Run dashboard">{escape(label)}</a>'
    return (
        f'<span class="inline-note" title="py tools/test-suite/render_analysis_dashboard.py '
        f'--analysis-run &quot;{escape(relative_display(run_path))}&quot;">{escape(label)}</span>'
    )


def collect_comparisons_index_hub_links() -> list[tuple[str, Path]]:
    links: list[tuple[str, Path]] = []
    runs_index = analysis_runs_index_path()
    if runs_index:
        links.append(("All analysis runs", runs_index))
    return links


def render_dashboard_nav_html(
    output_dir: Path,
    crumbs: list[tuple[str, Path | None]] | None = None,
    *,
    hub_links: list[tuple[str, Path]] | None = None,
) -> str:
    if hub_links:
        items = "".join(
            f'<a class="dashboard-nav__link" href="{escape(_nav_href(output_dir, target))}">{escape(label)}</a>'
            for label, target in hub_links
        )
        return (
            '<nav class="dashboard-nav" aria-label="Dashboard navigation">'
            '<div class="dashboard-nav__inner">'
            '<span class="dashboard-nav__label">Also open</span>'
            f"{items}"
            "</div></nav>"
        )

    if not crumbs:
        return ""

    link_crumbs = [(label, target) for label, target in crumbs if target is not None]
    current = next((label for label, target in crumbs if target is None), None)

    inner_parts: list[str] = []
    if link_crumbs:
        back_label, back_target = link_crumbs[-1]
        inner_parts.append(
            f'<a class="dashboard-nav__back" href="{escape(_nav_href(output_dir, back_target))}">'
            f"← {escape(back_label)}</a>"
        )
    if current and link_crumbs:
        inner_parts.append('<span class="dashboard-nav__sep" aria-hidden="true">·</span>')
        inner_parts.append(f'<span class="dashboard-nav__current" aria-current="page">{escape(current)}</span>')
    elif current and not link_crumbs:
        inner_parts.append(f'<span class="dashboard-nav__current" aria-current="page">{escape(current)}</span>')

    return (
        '<nav class="dashboard-nav" aria-label="Dashboard navigation">'
        f'<div class="dashboard-nav__inner">{"".join(inner_parts)}</div>'
        "</nav>"
    )


def render_related_links_html(output_dir: Path, links: list[tuple[str, Path]]) -> str:
    if not links:
        return ""
    items: list[str] = []
    for label, target in links:
        try:
            index = resolve_dashboard_index(target)
            href = dashboard_href(output_dir, index)
            items.append(f'<a href="{escape(href)}">{escape(label)}</a>')
        except FileNotFoundError:
            continue
    if not items:
        return ""
    return (
        '<nav class="related-links" aria-label="Related dashboards">'
        '<div class="related-links__inner">'
        '<span class="related-links__label">Related</span>'
        + "".join(items)
        + "</div></nav>"
    )


def collect_related_links(
    context: DashboardContext,
    view_model: dict[str, Any] | None,
    args: argparse.Namespace,
) -> list[tuple[str, Path]]:
    links: list[tuple[str, Path]] = []
    if args.related_timeline:
        links.append(("Timeline", Path(args.related_timeline)))
    if args.related_analysis:
        links.append(("Analysis run", Path(args.related_analysis)))
    if args.related_comparison:
        links.append(("Comparison", Path(args.related_comparison)))

    if view_model and context.mode == "comparison":
        meta = view_model.get("meta", {})
        auto_pairs = [
            ("Baseline dashboard", meta.get("baseline_run_dir")),
            ("Candidate dashboard", meta.get("candidate_run_dir")),
        ]
        for label, run_dir in auto_pairs:
            if not run_dir:
                continue
            dashboard_dir = Path(run_dir) / "dashboard"
            if (dashboard_dir / "index.html").exists():
                links.append((label, dashboard_dir))

    deduped: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for label, path in links:
        key = str(path.resolve())
        if key in seen:
            continue
        seen.add(key)
        deduped.append((label, path))
    return deduped


def first_present(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def derive_issue_summary(issue: dict[str, Any]) -> dict[str, Any]:
    aggregate_rows: list[dict[str, Any]] = []
    tested = 0
    hits = 0
    hits_any_locale = 0

    for path_identifier, aggregate in sorted(issue["aggregates"]["by_path_locale"].items()):
        row = {
            "path_identifier": path_identifier,
            "target_pass_rate": first_present(aggregate, "target_pass_rate", "expected_pass_rate"),
            "target_any_locale_pass_rate": first_present(aggregate, "target_any_locale_pass_rate", "expected_any_locale_pass_rate"),
            "target_mrr": first_present(aggregate, "target_mrr", "expected_mrr"),
            "helpful_pass_rate": aggregate.get("helpful_pass_rate", aggregate.get("any_relevant_any_locale_rate")),
            **aggregate,
        }
        aggregate_rows.append(row)
        if path_identifier.endswith(".markdown") or path_identifier.endswith(".suggested_sources"):
            continue
        tested_styles = int(aggregate.get("n_tested_styles", 0))
        tested += tested_styles
        hits += round(float(first_present(aggregate, "target_pass_rate", "expected_pass_rate") or 0.0) * tested_styles)
        hits_any_locale += round(float(first_present(aggregate, "target_any_locale_pass_rate", "expected_any_locale_pass_rate") or 0.0) * tested_styles)

    misses = tested - hits
    misses_any_locale = tested - hits_any_locale
    hit_rate = (hits / tested) if tested else 0.0
    hit_rate_any_locale = (hits_any_locale / tested) if tested else 0.0

    return {
        "issue_id": issue["issue_id"],
        "persona": issue["persona"],
        "product": issue["product"],
        "user_intent": issue["user_intent"],
        "target_docs": first_present(issue, "target_docs", "expected_docs") or [],
        "other_helpful_docs": issue["other_helpful_docs"],
        "path_style": issue["per_path_style"],
        "aggregate_rows": aggregate_rows,
        "totals": {
            "tested_styles": tested,
            "hits": hits,
            "misses": misses,
            "hit_rate": round(hit_rate, 6),
            "hits_any_locale": hits_any_locale,
            "misses_any_locale": misses_any_locale,
            "hit_rate_any_locale": round(hit_rate_any_locale, 6),
        },
    }


LOCALES_HEATMAP_ORDER = ("en", "pt", "es")


def classify_path_family(path: str) -> str:
    if path.startswith("internal-search."):
        return "Internal search"
    if path.startswith("docs-assistant."):
        return "Docs Assistant"
    if path.startswith("external-search."):
        return "External search"
    if path.startswith("llm."):
        return "External LLMs"
    return "Other"


def aggregate_path_families(path_rows: list[dict[str, Any]], *, comparison: bool = False) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, float | int]] = {}
    for row in path_rows:
        if row.get("link_source"):
            continue
        family = classify_path_family(row["path"])
        tested = int(row.get("n_tested_queries") or row.get("delta_n_tested_queries") or 0)
        if tested <= 0 and not comparison:
            continue
        bucket = buckets.setdefault(
            family,
            {"tested": 0, "pass_weighted": 0.0, "mrr_weighted": 0.0, "delta_weighted": 0.0},
        )
        if comparison:
            delta = first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate")
            delta_mrr = first_present(row, "delta_target_mean_mrr", "delta_expected_mean_mrr")
            n = int(row.get("baseline_n_tested_queries") or row.get("candidate_n_tested_queries") or tested or 1)
            bucket["tested"] += n
            if delta is not None:
                bucket["delta_weighted"] += float(delta) * n
            if delta_mrr is not None:
                bucket["mrr_weighted"] += float(delta_mrr) * n
        else:
            n = int(row.get("n_tested_queries") or 0)
            rate = first_present(row, "target_pass_rate", "expected_pass_rate")
            mrr = first_present(row, "target_mean_mrr", "expected_mean_mrr")
            if n <= 0 or rate is None:
                continue
            bucket["tested"] += n
            bucket["pass_weighted"] += float(rate) * n
            if mrr is not None:
                bucket["mrr_weighted"] += float(mrr) * n

    rows: list[dict[str, Any]] = []
    for family in sorted(buckets):
        bucket = buckets[family]
        tested = int(bucket["tested"])
        if tested <= 0:
            continue
        if comparison:
            rows.append(
                {
                    "family": family,
                    "n_tested_queries": tested,
                    "delta_target_pass_rate": round(bucket["delta_weighted"] / tested, 6),
                    "delta_target_mean_mrr": round(bucket["mrr_weighted"] / tested, 6),
                }
            )
        else:
            rows.append(
                {
                    "family": family,
                    "n_tested_queries": tested,
                    "target_pass_rate": round(bucket["pass_weighted"] / tested, 6),
                    "target_mean_mrr": round(bucket["mrr_weighted"] / tested, 6),
                }
            )
    return rows


def _heatmap_bucket_percent(value: float | None) -> str:
    if value is None:
        return "heat-empty"
    clamped = max(0.0, min(1.0, float(value)))
    return f"heat-p{min(9, int(clamped * 10))}"


def _heatmap_bucket_delta(value: float | None, max_abs: float) -> str:
    if value is None:
        return "heat-empty"
    if max_abs <= 0:
        return "heat-neutral"
    if value > 0:
        intensity = min(9, int(abs(value) / max_abs * 9))
        return f"heat-up-{intensity}"
    if value < 0:
        intensity = min(9, int(abs(value) / max_abs * 9))
        return f"heat-down-{intensity}"
    return "heat-neutral"


def render_path_locale_heatmap(path_rows: list[dict[str, Any]], *, comparison: bool = False) -> str:
    by_path: dict[str, dict[str, dict[str, Any]]] = {}
    for row in path_rows:
        if row.get("link_source"):
            continue
        path = row["path"]
        locale = str(row["locale"]).lower()
        by_path.setdefault(path, {})[locale] = row

    if not by_path:
        return "<p class='inline-note'>No path×locale data available.</p>"

    values: list[float] = []
    if comparison:
        for locales in by_path.values():
            for row in locales.values():
                delta = first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate")
                if delta is not None:
                    values.append(float(delta))
        max_abs = max((abs(value) for value in values), default=0.0)
        metric_label = "Delta target pass"
    else:
        for locales in by_path.values():
            for row in locales.values():
                rate = first_present(row, "target_pass_rate", "expected_pass_rate")
                if rate is not None:
                    values.append(float(rate))

    header = "".join(f"<th>{escape(locale.upper())}</th>" for locale in LOCALES_HEATMAP_ORDER)
    body_rows: list[str] = []
    for path in sorted(by_path):
        cells = [f"<th class='heatmap-row-label'>{escape(path)}</th>"]
        for locale in LOCALES_HEATMAP_ORDER:
            row = by_path[path].get(locale)
            if not row:
                cells.append('<td class="heat-empty">-</td>')
                continue
            if comparison:
                value = first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate")
                css = _heatmap_bucket_delta(float(value) if value is not None else None, max_abs)
                display = percent_text(value) if value is not None else "-"
            else:
                value = first_present(row, "target_pass_rate", "expected_pass_rate")
                css = _heatmap_bucket_percent(float(value) if value is not None else None)
                display = percent_text(value) if value is not None else "-"
            cells.append(f'<td class="{css}" title="{escape(path)} / {locale.upper()}">{display}</td>')
        body_rows.append(f"<tr>{''.join(cells)}</tr>")

    if comparison:
        caption = (
            f"{metric_label} rate by path and locale "
            "(green = improvement, red = regression)."
        )
    else:
        caption = "Target pass rate by path and locale."
    return (
        f"<p class='inline-note'>{escape(caption)}</p>"
        '<div class="table-wrap heatmap-wrap">'
        f'<table class="heatmap-table"><thead><tr><th>Path</th>{header}</tr></thead>'
        f"<tbody>{''.join(body_rows)}</tbody></table></div>"
    )


def render_path_family_rows(family_rows: list[dict[str, Any]], *, comparison: bool = False) -> str:
    if not family_rows:
        return "<p class='inline-note'>No path family data available.</p>"
    if comparison:
        columns = [
            {"key": "family", "label": "Path family"},
            {"key": "delta_target_pass_rate", "label": "Weighted delta pass", "kind": "percent"},
            {"key": "delta_target_mean_mrr", "label": "Weighted delta MRR", "kind": "decimal"},
            {"key": "n_tested_queries", "label": "Tested queries", "kind": "int"},
        ]
    else:
        columns = [
            {"key": "family", "label": "Path family"},
            {"key": "target_pass_rate", "label": "Weighted pass", "kind": "percent"},
            {"key": "target_mean_mrr", "label": "Weighted MRR", "kind": "decimal"},
            {"key": "n_tested_queries", "label": "Tested queries", "kind": "int"},
        ]
    return render_table(columns, family_rows, compact=True)


def analysis_callouts(
    path_rows: list[dict[str, Any]],
    locale_rows: list[dict[str, Any]],
    style_rows: list[dict[str, Any]],
    issue_rows: list[dict[str, Any]],
    path_family_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, str]]:
    best_path = max(path_rows, key=lambda row: first_present(row, "target_pass_rate", "expected_pass_rate"))
    weakest_path = min(path_rows, key=lambda row: first_present(row, "target_pass_rate", "expected_pass_rate"))
    best_locale = max(locale_rows, key=lambda row: first_present(row, "target_pass_rate", "expected_pass_rate"))
    weakest_locale = min(locale_rows, key=lambda row: first_present(row, "target_pass_rate", "expected_pass_rate"))
    strongest_style = max(style_rows, key=lambda row: first_present(row, "target_pass_rate", "expected_pass_rate"))
    hardest_issue = max(issue_rows, key=lambda row: row["totals"]["misses"])

    return [
        {
            "label": "Best path",
            "value": f"{best_path['path']} / {best_path['locale'].upper()}",
            "note": f"{percent_text(first_present(best_path, 'target_pass_rate', 'expected_pass_rate'))} target pass.",
        },
        {
            "label": "Weakest path",
            "value": f"{weakest_path['path']} / {weakest_path['locale'].upper()}",
            "note": f"{percent_text(first_present(weakest_path, 'target_pass_rate', 'expected_pass_rate'))} target pass.",
        },
        {
            "label": "Best locale",
            "value": best_locale["locale"].upper(),
            "note": f"{percent_text(first_present(best_locale, 'target_pass_rate', 'expected_pass_rate'))} target pass and {decimal_text(first_present(best_locale, 'target_mean_mrr', 'expected_mean_mrr'))} MRR.",
        },
        {
            "label": "Weakest locale",
            "value": weakest_locale["locale"].upper(),
            "note": f"{percent_text(first_present(weakest_locale, 'target_pass_rate', 'expected_pass_rate'))} target pass.",
        },
        {
            "label": "Strongest query style",
            "value": strongest_style["style"],
            "note": f"{percent_text(first_present(strongest_style, 'target_pass_rate', 'expected_pass_rate'))} target pass.",
        },
        {
            "label": "Hardest issue",
            "value": hardest_issue["issue_id"],
            "note": f"{int_text(hardest_issue['totals']['misses'])} misses across {int_text(hardest_issue['totals']['tested_styles'])} tested styles.",
        },
    ]
    if path_family_rows:
        best_family = max(path_family_rows, key=lambda row: first_present(row, "target_pass_rate", "expected_pass_rate") or 0)
        weakest_family = min(path_family_rows, key=lambda row: first_present(row, "target_pass_rate", "expected_pass_rate") or 0)
        callouts.extend(
            [
                {
                    "label": "Best path family",
                    "value": best_family["family"],
                    "note": f"{percent_text(first_present(best_family, 'target_pass_rate', 'expected_pass_rate'))} weighted target pass.",
                },
                {
                    "label": "Weakest path family",
                    "value": weakest_family["family"],
                    "note": f"{percent_text(first_present(weakest_family, 'target_pass_rate', 'expected_pass_rate'))} weighted target pass.",
                },
            ]
        )
    return callouts


def resolve_analysis_run_dir(run_dir_value: str) -> Path:
    path = Path(run_dir_value)
    if not path.is_absolute():
        path = workspace_root() / path
    return path.resolve()


def normalize_run_dir(path_value: str) -> str:
    return resolve_analysis_run_dir(path_value).as_posix()


def compute_analysis_warnings(run_summary: dict[str, Any]) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    selected_runs = run_summary.get("selected_runs", {})

    unhealthy = sorted(
        key for key, details in selected_runs.items() if not details.get("is_healthy", True)
    )
    if unhealthy:
        warnings.append(
            {
                "level": "warn",
                "title": "Unhealthy source runs",
                "message": (
                    "One or more underlying collection runs failed health checks. "
                    "Metrics for these sources may be incomplete or misleading."
                ),
                "items": unhealthy,
            }
        )

    not_full = sorted(
        key for key, details in selected_runs.items() if not details.get("is_full", True)
    )
    if not_full:
        warnings.append(
            {
                "level": "warn",
                "title": "Incomplete source runs",
                "message": (
                    "Some collection runs did not reach the expected query count. "
                    "Pass rates may not be comparable to a full run."
                ),
                "items": not_full,
            }
        )

    low_coverage = sorted(
        key
        for key, details in selected_runs.items()
        if float(details.get("nonempty_ratio", 1.0)) < 0.9
    )
    if low_coverage:
        warnings.append(
            {
                "level": "warn",
                "title": "Low nonempty response ratio",
                "message": (
                    "Some sources returned empty results for more than 10% of queries. "
                    "Review collection logs before trusting path-level metrics."
                ),
                "items": [
                    f"{key} ({float(selected_runs[key]['nonempty_ratio']) * 100:.1f}% nonempty)"
                    for key in low_coverage
                ],
            }
        )

    n_not_available = int(run_summary.get("n_not_available", 0) or 0)
    if n_not_available > 0:
        warnings.append(
            {
                "level": "info",
                "title": "Queries marked not available",
                "message": (
                    f"{n_not_available:,} queries were excluded from denominators because the "
                    "path/locale combination does not apply. See the Not available overview card."
                ),
                "items": [],
            }
        )

    return warnings


def compute_comparison_context_warnings(
    baseline_summary: dict[str, Any],
    candidate_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    baseline_runs = baseline_summary.get("selected_runs", {})
    candidate_runs = candidate_summary.get("selected_runs", {})

    baseline_keys = set(baseline_runs)
    candidate_keys = set(candidate_runs)
    only_baseline = sorted(baseline_keys - candidate_keys)
    only_candidate = sorted(candidate_keys - baseline_keys)
    if only_baseline or only_candidate:
        items: list[str] = []
        if only_baseline:
            items.append(f"Only in baseline: {', '.join(only_baseline)}")
        if only_candidate:
            items.append(f"Only in candidate: {', '.join(only_candidate)}")
        warnings.append(
            {
                "level": "warn",
                "title": "Source coverage mismatch",
                "message": (
                    "Baseline and candidate analyses used different source keys. "
                    "Overall deltas may mix incomparable inputs."
                ),
                "items": items,
            }
        )

    mismatched_dirs: list[str] = []
    health_mismatch: list[str] = []
    for key in sorted(baseline_keys & candidate_keys):
        baseline_details = baseline_runs[key]
        candidate_details = candidate_runs[key]
        baseline_dir = normalize_run_dir(baseline_details["run_dir"])
        candidate_dir = normalize_run_dir(candidate_details["run_dir"])
        if baseline_dir != candidate_dir:
            mismatched_dirs.append(
                f"{key}: baseline `{relative_display(Path(baseline_dir))}` "
                f"vs candidate `{relative_display(Path(candidate_dir))}`"
            )
        if baseline_details.get("is_healthy") != candidate_details.get("is_healthy"):
            health_mismatch.append(
                f"{key}: baseline healthy={baseline_details.get('is_healthy')} "
                f"vs candidate healthy={candidate_details.get('is_healthy')}"
            )

    if mismatched_dirs:
        warnings.append(
            {
                "level": "warn",
                "title": "Different collection runs selected",
                "message": (
                    "At least one source used a different underlying collection folder "
                    "between baseline and candidate. Deltas may reflect collection changes, "
                    "not only product behavior."
                ),
                "items": mismatched_dirs,
            }
        )

    if health_mismatch:
        warnings.append(
            {
                "level": "warn",
                "title": "Source health changed between runs",
                "message": "Health status differs for shared sources across baseline and candidate.",
                "items": health_mismatch,
            }
        )

    warnings.extend(compute_analysis_warnings(baseline_summary))
    warnings.extend(compute_analysis_warnings(candidate_summary))

    seen_titles: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for warning in warnings:
        title = warning["title"]
        if title in seen_titles:
            continue
        seen_titles.add(title)
        deduped.append(warning)
    return deduped


def render_warning_banners(warnings: list[dict[str, Any]]) -> str:
    if not warnings:
        return ""
    blocks: list[str] = []
    for warning in warnings:
        level = warning.get("level", "warn")
        items = warning.get("items") or []
        items_html = ""
        if items:
            items_html = (
                "<ul class='warning-banner__list'>"
                + "".join(f"<li>{escape(item)}</li>" for item in items)
                + "</ul>"
            )
        blocks.append(
            f"<div class='warning-banner warning-banner--{escape(level)}'>"
            f"<p class='warning-banner__title'>{escape(warning['title'])}</p>"
            f"<p class='warning-banner__message'>{escape(warning['message'])}</p>"
            f"{items_html}"
            "</div>"
        )
    return f"<div class='warning-banners'>{''.join(blocks)}</div>"


def load_run_summary_if_exists(run_dir_value: str) -> dict[str, Any] | None:
    summary_path = resolve_analysis_run_dir(run_dir_value) / "run_summary.json"
    if not summary_path.exists():
        return None
    return read_json(summary_path)


def build_analysis_view_model(run_dir: Path) -> dict[str, Any]:
    run_summary = read_json(run_dir / "run_summary.json")
    path_rows_all = read_json(run_dir / "aggregates_by_path_locale.json")
    path_rows = [row for row in path_rows_all if row.get("link_source") is None]
    docs_assistant_source_rows = [row for row in path_rows_all if row.get("link_source") is not None]
    locale_rows = read_json(run_dir / "aggregates_by_locale.json")
    style_rows = read_json(run_dir / "aggregates_by_style.json")
    persona_rows = read_json(run_dir / "aggregates_by_persona.json")
    issues_raw = read_json(run_dir / "issues_processed.json")
    failure_rows = read_json(run_dir / "failure_list.json")

    issues = [derive_issue_summary(issue) for issue in issues_raw]
    issues.sort(key=lambda issue: (-issue["totals"]["misses"], issue["issue_id"]))

    style_locale_path = run_dir / "aggregates_by_style_locale.json"
    persona_locale_path = run_dir / "aggregates_by_persona_locale.json"
    style_locale_rows = (
        read_json(style_locale_path) if style_locale_path.exists() else _derive_style_locale_from_issues(issues_raw)
    )
    persona_locale_rows = (
        read_json(persona_locale_path) if persona_locale_path.exists() else _derive_persona_locale_from_issues(issues_raw)
    )
    portal_rows = _derive_portal_locale_from_issues(issues_raw)
    path_family_rows = aggregate_path_families(path_rows)

    selected_runs = []
    for source_key, details in sorted(run_summary["selected_runs"].items()):
        selected_runs.append(
            {
                "source_key": source_key,
                "run_dir": details["run_dir"],
                "timestamp": details["timestamp"],
                "nonempty_ratio": details["nonempty_ratio"],
                "actual_queries": details["actual_queries"],
                "is_full": "Yes" if details["is_full"] else "No",
                "is_healthy": "Yes" if details["is_healthy"] else "No",
            }
        )

    return {
        "mode": "analysis",
        "page_title": f"Analysis Dashboard - {run_summary['run_id']}",
        "dashboard_title": "Latest Analysis Run",
        "dashboard_subtitle": (
            f"Run {run_summary['run_id']} | {run_summary['n_issues']} issues | "
            f"{int_text(run_summary['n_queries_total'])} queries | "
            f"{percent_text(first_present(run_summary, 'overall_target_pass_rate', 'overall_expected_pass_rate'))} target pass"
        ),
        "cards": [
            {
                "label": "Target pass rate",
                "value": percent_text(first_present(run_summary, "overall_target_pass_rate", "overall_expected_pass_rate")),
                "note": "Success rate counting only exact `target_doc` matches.",
            },
            {
                "label": "Target pass any locale",
                "value": percent_text(first_present(run_summary, "overall_target_any_locale_pass_rate", "overall_expected_any_locale_pass_rate")),
                "note": "Target-doc success counting different-locale target docs too.",
            },
            {
                "label": "Target MRR",
                "value": decimal_text(first_present(run_summary, "overall_target_mrr", "overall_expected_mrr")),
                "note": "Reciprocal rank of the best target doc found.",
            },
            {
                "label": "Helpful pass rate",
                "value": percent_text(
                    first_present(run_summary, "overall_helpful_pass_rate", "overall_any_relevant_any_locale_rate")
                ),
                "note": "Success rate counting any relevant non-`unrelated` link type.",
            },
            {
                "label": "Any relevant rate",
                "value": percent_text(run_summary["overall_any_relevant_rate"]),
                "note": "Target or helpful docs appeared in returned links.",
            },
            {
                "label": "Any relevant any locale",
                "value": percent_text(run_summary.get("overall_any_relevant_any_locale_rate")),
                "note": "Target/helpful docs appeared, including different-locale variants.",
            },
            {
                "label": "Not available",
                "value": int_text(run_summary["n_not_available"]),
                "note": "Queries excluded from denominators due to path/locale applicability.",
            },
        ],
        "callouts": analysis_callouts(path_rows, locale_rows, style_rows, issues, path_family_rows),
        "notes": [
            "Phase 1 evaluates link and rank only. Answer quality scoring is intentionally excluded.",
            "Internal search metrics use top 7 links; all other path families use all returned links.",
            "This dashboard is rendered from processed analysis outputs, not runner-level summaries.",
        ],
        "selected_runs": selected_runs,
        "path_rows": path_rows,
        "docs_assistant_source_rows": docs_assistant_source_rows,
        "locale_rows": locale_rows,
        "style_rows": style_rows,
        "persona_rows": persona_rows,
        "worst_issues": issues[:12],
        "issues": issues,
        "failure_rows": failure_rows,
        "locale_gap_rows": compute_locale_gaps(path_rows),
        "style_locale_rows": style_locale_rows,
        "persona_locale_rows": persona_locale_rows,
        "portal_rows": portal_rows,
        "path_family_rows": path_family_rows,
        "meta": {
            "analysis_id": run_summary["analysis_id"],
            "run_id": run_summary["run_id"],
            "timestamp": run_summary["timestamp"],
            "generated_at": utc_now_iso(),
        },
        "warnings": compute_analysis_warnings(run_summary),
    }


def compute_comparison_movers(
    path_rows: list[dict[str, Any]],
    locale_rows: list[dict[str, Any]],
    style_rows: list[dict[str, Any]],
    n: int = 5,
) -> dict[str, list[dict[str, Any]]]:
    """Rank largest target-pass deltas between baseline and candidate across dimensions."""
    deltas: list[dict[str, Any]] = []

    def append_row(label: str, row: dict[str, Any]) -> None:
        delta = first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate")
        if delta is None:
            return
        baseline = first_present(row, "baseline_target_pass_rate", "baseline_expected_pass_rate")
        candidate = first_present(row, "candidate_target_pass_rate", "candidate_expected_pass_rate")
        if baseline is None or candidate is None:
            return
        deltas.append(
            {
                "label": label,
                "first": round(float(baseline), 6),
                "last": round(float(candidate), 6),
                "delta": round(float(delta), 6),
            }
        )

    for row in path_rows:
        if row.get("link_source"):
            continue
        append_row(f"{row['path']} / {row['locale'].upper()}", row)
    for row in locale_rows:
        append_row(f"locale / {row['locale'].upper()}", row)
    for row in style_rows:
        append_row(f"style / {row['style']}", row)

    improvements = sorted(deltas, key=lambda item: item["delta"], reverse=True)[:n]
    regressions = sorted(deltas, key=lambda item: item["delta"])[:n]
    return {"improvements": improvements, "regressions": regressions}


def comparison_callouts(
    path_rows: list[dict[str, Any]],
    locale_rows: list[dict[str, Any]],
    path_family_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, str]]:
    main_rows = [row for row in path_rows if row.get("link_source") is None]
    if not main_rows:
        return []
    best_improvement = max(main_rows, key=lambda row: first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate"))
    worst_regression = min(main_rows, key=lambda row: first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate"))
    best_locale = max(locale_rows, key=lambda row: first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate"))
    worst_locale = min(locale_rows, key=lambda row: first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate"))
    return [
        {
            "label": "Biggest improvement",
            "value": f"{best_improvement['path']} / {best_improvement['locale'].upper()}",
            "note": f"{percent_text(first_present(best_improvement, 'delta_target_pass_rate', 'delta_expected_pass_rate'))} delta target pass.",
        },
        {
            "label": "Biggest regression",
            "value": f"{worst_regression['path']} / {worst_regression['locale'].upper()}",
            "note": f"{percent_text(first_present(worst_regression, 'delta_target_pass_rate', 'delta_expected_pass_rate'))} delta target pass.",
        },
        {
            "label": "Best locale delta",
            "value": best_locale["locale"].upper(),
            "note": f"{percent_text(first_present(best_locale, 'delta_target_pass_rate', 'delta_expected_pass_rate'))} delta target pass.",
        },
        {
            "label": "Weakest locale delta",
            "value": worst_locale["locale"].upper(),
            "note": f"{percent_text(first_present(worst_locale, 'delta_target_pass_rate', 'delta_expected_pass_rate'))} delta target pass.",
        },
    ]
    if path_family_rows:
        best_family = max(
            path_family_rows,
            key=lambda row: first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate") or 0,
        )
        worst_family = min(
            path_family_rows,
            key=lambda row: first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate") or 0,
        )
        callouts.extend(
            [
                {
                    "label": "Best path family delta",
                    "value": best_family["family"],
                    "note": f"{percent_text(first_present(best_family, 'delta_target_pass_rate', 'delta_expected_pass_rate'))} weighted delta pass.",
                },
                {
                    "label": "Weakest path family delta",
                    "value": worst_family["family"],
                    "note": f"{percent_text(first_present(worst_family, 'delta_target_pass_rate', 'delta_expected_pass_rate'))} weighted delta pass.",
                },
            ]
        )
    return callouts


def _read_json_if_exists(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = read_json(path)
    return payload if isinstance(payload, list) else []


def compute_locale_gaps(path_rows: list[dict[str, Any]], *, comparison: bool = False) -> list[dict[str, Any]]:
    by_path: dict[str, dict[str, dict[str, Any]]] = {}
    for row in path_rows:
        if row.get("link_source"):
            continue
        path = row["path"]
        locale = str(row["locale"]).lower()
        by_path.setdefault(path, {})[locale] = row

    gaps: list[dict[str, Any]] = []
    for path in sorted(by_path):
        locales = by_path[path]
        en_row = locales.get("en", {})
        es_row = locales.get("es", {})
        pt_row = locales.get("pt", {})

        if comparison:
            en_baseline = first_present(en_row, "baseline_target_pass_rate", "baseline_expected_pass_rate")
            en_candidate = first_present(en_row, "candidate_target_pass_rate", "candidate_expected_pass_rate")
            es_baseline = first_present(es_row, "baseline_target_pass_rate", "baseline_expected_pass_rate")
            es_candidate = first_present(es_row, "candidate_target_pass_rate", "candidate_expected_pass_rate")
            pt_baseline = first_present(pt_row, "baseline_target_pass_rate", "baseline_expected_pass_rate")
            pt_candidate = first_present(pt_row, "candidate_target_pass_rate", "candidate_expected_pass_rate")

            baseline_es_gap = (
                round(float(es_baseline) - float(en_baseline), 6)
                if es_baseline is not None and en_baseline is not None
                else None
            )
            baseline_pt_gap = (
                round(float(pt_baseline) - float(en_baseline), 6)
                if pt_baseline is not None and en_baseline is not None
                else None
            )
            candidate_es_gap = (
                round(float(es_candidate) - float(en_candidate), 6)
                if es_candidate is not None and en_candidate is not None
                else None
            )
            candidate_pt_gap = (
                round(float(pt_candidate) - float(en_candidate), 6)
                if pt_candidate is not None and en_candidate is not None
                else None
            )
            delta_es_gap = (
                round(candidate_es_gap - baseline_es_gap, 6)
                if candidate_es_gap is not None and baseline_es_gap is not None
                else None
            )
            delta_pt_gap = (
                round(candidate_pt_gap - baseline_pt_gap, 6)
                if candidate_pt_gap is not None and baseline_pt_gap is not None
                else None
            )
            gaps.append(
                {
                    "path": path,
                    "en_pass_rate": en_candidate,
                    "es_pass_rate": es_candidate,
                    "pt_pass_rate": pt_candidate,
                    "es_gap_vs_en": candidate_es_gap,
                    "pt_gap_vs_en": candidate_pt_gap,
                    "baseline_es_gap_vs_en": baseline_es_gap,
                    "baseline_pt_gap_vs_en": baseline_pt_gap,
                    "delta_es_gap_vs_en": delta_es_gap,
                    "delta_pt_gap_vs_en": delta_pt_gap,
                }
            )
        else:
            en_pass = first_present(en_row, "target_pass_rate", "expected_pass_rate")
            es_pass = first_present(es_row, "target_pass_rate", "expected_pass_rate")
            pt_pass = first_present(pt_row, "target_pass_rate", "expected_pass_rate")
            es_gap = round(float(es_pass) - float(en_pass), 6) if es_pass is not None and en_pass is not None else None
            pt_gap = round(float(pt_pass) - float(en_pass), 6) if pt_pass is not None and en_pass is not None else None
            gaps.append(
                {
                    "path": path,
                    "en_pass_rate": en_pass,
                    "es_pass_rate": es_pass,
                    "pt_pass_rate": pt_pass,
                    "es_gap_vs_en": es_gap,
                    "pt_gap_vs_en": pt_gap,
                }
            )
    return gaps


def render_locale_gap_table(gap_rows: list[dict[str, Any]], *, comparison: bool = False) -> str:
    if not gap_rows:
        return "<p class='inline-note'>No locale gap data available.</p>"
    prepared = []
    for row in gap_rows:
        item = dict(row)
        for key in ("es_gap_vs_en", "pt_gap_vs_en", "delta_es_gap_vs_en", "delta_pt_gap_vs_en"):
            value = item.get(key)
            if value is None:
                item[f"{key}_class"] = ""
            elif value < 0:
                item[f"{key}_class"] = "gap-negative"
            elif value > 0:
                item[f"{key}_class"] = "gap-positive"
            else:
                item[f"{key}_class"] = "gap-neutral"
        prepared.append(item)

    if comparison:
        columns = [
            {"key": "path", "label": "Path"},
            {"key": "es_gap_vs_en", "label": "ES − EN (candidate)", "kind": "percent", "css_key": "es_gap_vs_en_class"},
            {"key": "pt_gap_vs_en", "label": "PT − EN (candidate)", "kind": "percent", "css_key": "pt_gap_vs_en_class"},
            {"key": "baseline_es_gap_vs_en", "label": "ES − EN (baseline)", "kind": "percent"},
            {"key": "delta_es_gap_vs_en", "label": "Delta ES gap", "kind": "percent", "css_key": "delta_es_gap_vs_en_class"},
            {"key": "delta_pt_gap_vs_en", "label": "Delta PT gap", "kind": "percent", "css_key": "delta_pt_gap_vs_en_class"},
        ]
    else:
        columns = [
            {"key": "path", "label": "Path"},
            {"key": "en_pass_rate", "label": "EN pass", "kind": "percent"},
            {"key": "es_pass_rate", "label": "ES pass", "kind": "percent"},
            {"key": "pt_pass_rate", "label": "PT pass", "kind": "percent"},
            {"key": "es_gap_vs_en", "label": "ES − EN", "kind": "percent", "css_key": "es_gap_vs_en_class"},
            {"key": "pt_gap_vs_en", "label": "PT − EN", "kind": "percent", "css_key": "pt_gap_vs_en_class"},
        ]
    return render_table(columns, prepared, compact=True)


def render_composite_dimension_rows(
    rows: list[dict[str, Any]],
    label_fn: Any,
    comparison: bool = False,
) -> str:
    prepared = []
    for row in rows:
        prepared.append(
            {
                "label": label_fn(row),
                "target_pass_rate": first_present(row, "target_pass_rate", "expected_pass_rate"),
                "helpful_pass_rate": row.get("helpful_pass_rate", row.get("any_relevant_any_locale_rate")),
                "delta_target_pass_rate": first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate"),
                "delta_helpful_pass_rate": row.get("delta_helpful_pass_rate", row.get("delta_any_relevant_any_locale_rate")),
                **row,
            }
        )
    if comparison:
        columns = [
            {"key": "label", "label": "Segment"},
            {"key": "delta_target_pass_rate", "label": "Delta target pass", "kind": "percent"},
            {"key": "delta_target_mean_mrr", "label": "Delta MRR", "kind": "decimal"},
            {"key": "delta_helpful_pass_rate", "label": "Delta helpful pass", "kind": "percent"},
            {"key": "baseline_target_pass_rate", "label": "Baseline target pass", "kind": "percent"},
            {"key": "candidate_target_pass_rate", "label": "Candidate target pass", "kind": "percent"},
        ]
    else:
        columns = [
            {"key": "label", "label": "Segment"},
            {"key": "target_pass_rate", "label": "Target pass", "kind": "percent"},
            {"key": "target_mean_mrr", "label": "Target MRR", "kind": "decimal"},
            {"key": "helpful_pass_rate", "label": "Helpful pass", "kind": "percent"},
            {"key": "n_tested_queries", "label": "Tested", "kind": "int"},
        ]
    return render_table(columns, prepared, compact=True)


def render_issue_comparison_section(issue_rows: list[dict[str, Any]], limit: int = 12) -> str:
    comparable = [
        row
        for row in issue_rows
        if first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate") is not None
    ]
    if not comparable:
        return "<p class='inline-note'>No issue-level comparison data available.</p>"

    regressions = sorted(
        comparable,
        key=lambda row: first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate"),
    )[:limit]
    improvements = sorted(
        comparable,
        key=lambda row: first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate"),
        reverse=True,
    )[:limit]

    columns = [
        {"key": "issue_id", "label": "Issue"},
        {"key": "product", "label": "Product"},
        {"key": "persona", "label": "Persona"},
        {"key": "baseline_target_pass_rate", "label": "Baseline pass", "kind": "percent"},
        {"key": "candidate_target_pass_rate", "label": "Candidate pass", "kind": "percent"},
        {"key": "delta_target_pass_rate", "label": "Delta target pass", "kind": "percent"},
        {"key": "delta_helpful_pass_rate", "label": "Delta helpful pass", "kind": "percent"},
    ]

    def prepare(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "issue_id": row.get("issue_id"),
                "product": row.get("product") or "-",
                "persona": row.get("persona") or "-",
                "baseline_target_pass_rate": first_present(row, "baseline_target_pass_rate", "baseline_expected_pass_rate"),
                "candidate_target_pass_rate": first_present(row, "candidate_target_pass_rate", "candidate_expected_pass_rate"),
                "delta_target_pass_rate": first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate"),
                "delta_helpful_pass_rate": row.get("delta_helpful_pass_rate", row.get("delta_any_relevant_any_locale_rate")),
            }
            for row in rows
        ]

    return (
        "<div class='movers-grid'>"
        f"<div><h3 class='down'>Top issue regressions</h3>{render_table(columns, prepare(regressions), compact=True)}</div>"
        f"<div><h3 class='up'>Top issue improvements</h3>{render_table(columns, prepare(improvements), compact=True)}</div>"
        "</div>"
    )


def render_failure_delta_shell() -> str:
    return """
    <div id="failure-delta-explorer" class="section-stack">
      <div class="controls-grid">
        <div class="control-field">
          <label for="failure-delta-category">Category</label>
          <select id="failure-delta-category" data-filter="category">
            <option value="new_failures">New failures</option>
            <option value="resolved_failures">Resolved failures</option>
            <option value="still_failing">Still failing</option>
          </select>
        </div>
        <div class="control-field">
          <label for="failure-delta-path">Path</label>
          <select id="failure-delta-path" data-filter="path"></select>
        </div>
        <div class="control-field">
          <label for="failure-delta-locale">Locale</label>
          <select id="failure-delta-locale" data-filter="locale"></select>
        </div>
        <div class="control-field">
          <label for="failure-delta-issue">Issue ID</label>
          <input id="failure-delta-issue" data-filter="issue" type="search" placeholder="Search an issue id" />
        </div>
      </div>
      <p class="inline-note" data-role="failure-delta-count"></p>
      <div class="table-wrap">
        <table class="data-table js-sortable">
          <thead>
            <tr>
              <th><button class="sort-button" type="button">Path</button></th>
              <th><button class="sort-button" type="button">Locale</button></th>
              <th><button class="sort-button" type="button">Style</button></th>
              <th><button class="sort-button" type="button">Issue</button></th>
              <th><button class="sort-button" type="button">Query</button></th>
              <th><button class="sort-button" type="button">Link source</button></th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
    """


def build_comparison_view_model(run_dir: Path) -> dict[str, Any]:
    summary = read_json(run_dir / "comparison_summary.json")
    path_rows_all = read_json(run_dir / "comparison_by_path_locale.json")
    path_rows = [row for row in path_rows_all if row.get("link_source") is None]
    docs_assistant_source_rows = [row for row in path_rows_all if row.get("link_source") is not None]
    locale_rows = read_json(run_dir / "comparison_by_locale.json")
    style_rows = read_json(run_dir / "comparison_by_style.json")
    persona_rows = _read_json_if_exists(run_dir / "comparison_by_persona.json")
    style_locale_rows = _read_json_if_exists(run_dir / "comparison_by_style_locale.json")
    persona_locale_rows = _read_json_if_exists(run_dir / "comparison_by_persona_locale.json")
    issue_rows = _read_json_if_exists(run_dir / "comparison_by_issue.json")
    failure_delta = read_json(run_dir / "failure_delta.json") if (run_dir / "failure_delta.json").exists() else {}
    locale_gap_rows = compute_locale_gaps(path_rows, comparison=True)
    path_family_rows = aggregate_path_families(path_rows, comparison=True)

    baseline_summary = load_run_summary_if_exists(summary["baseline_run_dir"])
    candidate_summary = load_run_summary_if_exists(summary["candidate_run_dir"])
    comparison_warnings: list[dict[str, Any]] = []
    if baseline_summary and candidate_summary:
        comparison_warnings = compute_comparison_context_warnings(baseline_summary, candidate_summary)

    cards = [
        {
            "label": "Delta target pass",
            "value": percent_text(first_present(summary, "delta_overall_target_pass_rate", "delta_overall_expected_pass_rate")),
            "note": "Candidate minus baseline target-doc pass rate.",
        },
        {
            "label": "Delta target MRR",
            "value": decimal_text(first_present(summary, "delta_overall_target_mrr", "delta_overall_expected_mrr")),
            "note": "Candidate minus baseline overall target MRR.",
        },
        {
            "label": "Delta helpful pass",
            "value": percent_text(
                first_present(summary, "delta_overall_helpful_pass_rate", "delta_overall_any_relevant_any_locale_rate")
            ),
            "note": "Candidate minus baseline helpful pass rate.",
        },
        {
            "label": "Delta any relevant",
            "value": percent_text(summary["delta_overall_any_relevant_rate"]),
            "note": "Candidate minus baseline any-relevant rate.",
        },
    ]
    if baseline_summary is not None:
        cards.append(
            {
                "label": "Baseline not available",
                "value": int_text(int(baseline_summary.get("n_not_available", 0) or 0)),
                "note": "Queries excluded at baseline due to path/locale applicability.",
            }
        )
    if candidate_summary is not None:
        cards.append(
            {
                "label": "Candidate not available",
                "value": int_text(int(candidate_summary.get("n_not_available", 0) or 0)),
                "note": "Queries excluded at candidate due to path/locale applicability.",
            }
        )

    return {
        "mode": "comparison",
        "page_title": "Analysis Comparison Dashboard",
        "dashboard_title": "Analysis Comparison",
        "dashboard_subtitle": (
            f"Baseline {summary['baseline_run_dir']} -> candidate {summary['candidate_run_dir']}"
        ),
        "cards": cards,
        "callouts": comparison_callouts(path_rows, locale_rows, path_family_rows),
        "notes": [
            "Comparison dashboards show processed-metric deltas only. They do not rerun collection or analysis.",
            "Positive deltas indicate improvement in the candidate run relative to the baseline.",
        ],
        "path_rows": path_rows,
        "docs_assistant_source_rows": docs_assistant_source_rows,
        "locale_rows": locale_rows,
        "style_rows": style_rows,
        "persona_rows": persona_rows,
        "style_locale_rows": style_locale_rows,
        "persona_locale_rows": persona_locale_rows,
        "issue_comparison_rows": issue_rows,
        "failure_delta": failure_delta,
        "locale_gap_rows": locale_gap_rows,
        "top_movers": compute_comparison_movers(path_rows, locale_rows, style_rows),
        "path_family_rows": path_family_rows,
        "portal_rows": [],
        "issues": [],
        "failure_rows": [],
        "meta": {
            "baseline_analysis_id": summary["baseline_analysis_id"],
            "candidate_analysis_id": summary["candidate_analysis_id"],
            "baseline_run_dir": summary["baseline_run_dir"],
            "candidate_run_dir": summary["candidate_run_dir"],
            "timestamp": summary["timestamp"],
            "generated_at": utc_now_iso(),
        },
        "warnings": comparison_warnings,
        "baseline_selected_runs": (
            [
                {
                    "source_key": key,
                    "run_dir": details["run_dir"],
                    "is_healthy": "Yes" if details.get("is_healthy") else "No",
                    "is_full": "Yes" if details.get("is_full") else "No",
                }
                for key, details in sorted(baseline_summary.get("selected_runs", {}).items())
            ]
            if baseline_summary
            else []
        ),
        "candidate_selected_runs": (
            [
                {
                    "source_key": key,
                    "run_dir": details["run_dir"],
                    "is_healthy": "Yes" if details.get("is_healthy") else "No",
                    "is_full": "Yes" if details.get("is_full") else "No",
                }
                for key, details in sorted(candidate_summary.get("selected_runs", {}).items())
            ]
            if candidate_summary
            else []
        ),
    }


def render_selected_runs_section(selected_runs: list[dict[str, Any]]) -> str:
    columns = [
        {"key": "source_key", "label": "Source"},
        {"key": "run_dir", "label": "Selected run"},
        {"key": "timestamp", "label": "Timestamp"},
        {"key": "actual_queries", "label": "Queries", "kind": "int"},
        {"key": "nonempty_ratio", "label": "Nonempty ratio", "kind": "percent"},
        {"key": "is_full", "label": "Full"},
        {"key": "is_healthy", "label": "Healthy"},
    ]
    rows_html: list[str] = []
    for run in selected_runs:
        row_class = ""
        if run.get("is_healthy") == "No":
            row_class = "row-unhealthy"
        elif run.get("is_full") == "No":
            row_class = "row-not-full"
        class_attr = f' class="{row_class}"' if row_class else ""
        cells = []
        for column in columns:
            value = run.get(column["key"])
            kind = column.get("kind")
            if kind == "percent":
                display = percent_text(value) if isinstance(value, (int, float)) else escape(value)
            elif kind == "int":
                display = int_text(value) if isinstance(value, int) else escape(value)
            else:
                display = escape(value)
            cells.append(f"<td>{display}</td>")
        rows_html.append(f"<tr{class_attr}>{''.join(cells)}</tr>")

    header = "".join(
        f"<th>{escape(column['label'])}</th>" for column in columns
    )
    return (
        f'<div class="table-wrap"><table class="data-table data-table--compact">'
        f"<thead><tr>{header}</tr></thead>"
        f"<tbody>{''.join(rows_html)}</tbody></table></div>"
    )


def render_path_rows(path_rows: list[dict[str, Any]], comparison: bool = False) -> str:
    prepared = []
    for row in path_rows:
        prepared.append(
            {
                "path": row["path"],
                "locale": row["locale"].upper(),
                "link_source": row.get("link_source") or "-",
                "target_pass_rate": first_present(row, "target_pass_rate", "expected_pass_rate"),
                "helpful_pass_rate": row.get("helpful_pass_rate", row.get("any_relevant_any_locale_rate")),
                "delta_target_pass_rate": first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate"),
                "delta_helpful_pass_rate": row.get("delta_helpful_pass_rate", row.get("delta_any_relevant_any_locale_rate")),
                "baseline_target_pass_rate": first_present(row, "baseline_target_pass_rate", "baseline_expected_pass_rate"),
                "candidate_target_pass_rate": first_present(row, "candidate_target_pass_rate", "candidate_expected_pass_rate"),
                **row,
            }
        )
    include_link_source = any(row.get("link_source") not in (None, "", "-") for row in prepared)
    if comparison:
        columns = [
            {"key": "path", "label": "Path"},
            {"key": "locale", "label": "Locale"},
        ]
        if include_link_source:
            columns.append({"key": "link_source", "label": "Link source"})
        columns.extend(
            [
            {"key": "delta_target_pass_rate", "label": "Delta target pass", "kind": "percent"},
            {"key": "delta_target_mean_mrr", "label": "Delta MRR", "kind": "decimal"},
            {"key": "delta_helpful_pass_rate", "label": "Delta helpful pass", "kind": "percent"},
            {"key": "baseline_target_pass_rate", "label": "Baseline target pass", "kind": "percent"},
            {"key": "candidate_target_pass_rate", "label": "Candidate target pass", "kind": "percent"},
            {"key": "delta_n_tested_queries", "label": "Delta tested", "kind": "int"},
            ]
        )
    else:
        columns = [
            {"key": "path", "label": "Path"},
            {"key": "locale", "label": "Locale"},
        ]
        if include_link_source:
            columns.append({"key": "link_source", "label": "Link source"})
        columns.extend(
            [
            {"key": "target_pass_rate", "label": "Target pass", "kind": "percent"},
            {"key": "target_any_locale_pass_rate", "label": "Target pass any locale", "kind": "percent"},
            {"key": "target_mean_mrr", "label": "Target MRR", "kind": "decimal"},
            {"key": "helpful_pass_rate", "label": "Helpful pass", "kind": "percent"},
            {"key": "n_tested_queries", "label": "Tested", "kind": "int"},
            {"key": "n_not_available", "label": "N/A", "kind": "int"},
            ]
        )
    return render_table(columns, prepared)


def render_dimension_rows(rows: list[dict[str, Any]], key: str, comparison: bool = False) -> str:
    prepared = [
        {
            key: row[key],
            "target_pass_rate": first_present(row, "target_pass_rate", "expected_pass_rate"),
            "helpful_pass_rate": row.get("helpful_pass_rate", row.get("any_relevant_any_locale_rate")),
            "delta_target_pass_rate": first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate"),
            "delta_helpful_pass_rate": row.get("delta_helpful_pass_rate", row.get("delta_any_relevant_any_locale_rate")),
            **row,
        }
        for row in rows
    ]
    if comparison:
        columns = [
            {"key": key, "label": key.replace("_", " ").title()},
            {"key": "delta_target_pass_rate", "label": "Delta target pass", "kind": "percent"},
            {"key": "delta_target_mean_mrr", "label": "Delta MRR", "kind": "decimal"},
            {"key": "delta_helpful_pass_rate", "label": "Delta helpful pass", "kind": "percent"},
            {"key": "delta_n_tested_queries", "label": "Delta tested", "kind": "int"},
        ]
    else:
        columns = [
            {"key": key, "label": key.replace("_", " ").title()},
            {"key": "target_pass_rate", "label": "Target pass", "kind": "percent"},
            {"key": "target_any_locale_pass_rate", "label": "Target pass any locale", "kind": "percent"},
            {"key": "target_mean_mrr", "label": "Target MRR", "kind": "decimal"},
            {"key": "helpful_pass_rate", "label": "Helpful pass", "kind": "percent"},
            {"key": "n_tested_queries", "label": "Tested", "kind": "int"},
            {"key": "n_not_available", "label": "N/A", "kind": "int"},
        ]
    return render_table(columns, prepared, compact=True)


def render_worst_issues(issues: list[dict[str, Any]]) -> str:
    rows = []
    for issue in issues:
        rows.append(
            {
                "issue_id": issue["issue_id"],
                "product": issue["product"],
                "persona": issue["persona"],
                "misses": issue["totals"]["misses"],
                "tested_styles": issue["totals"]["tested_styles"],
                "hit_rate": issue["totals"]["hit_rate"],
            }
        )
    columns = [
        {"key": "issue_id", "label": "Issue"},
        {"key": "product", "label": "Product"},
        {"key": "persona", "label": "Persona"},
        {"key": "misses", "label": "Misses", "kind": "int"},
        {"key": "tested_styles", "label": "Tested styles", "kind": "int"},
        {"key": "hit_rate", "label": "Hit rate", "kind": "percent"},
    ]
    return render_table(columns, rows)


def render_overview_section(data: dict[str, Any]) -> str:
    meta = data["meta"]
    mode = data["mode"]
    parts = [
        render_metrics_guide(mode),
        render_comparison_reading_guide() if mode == "comparison" else "",
        render_warning_banners(data.get("warnings", [])),
        render_card_grid(data["cards"]),
        render_callouts(data["callouts"]),
        render_bullet_list(data["notes"]),
    ]
    parts.append(
        f"""
        <p class="footer-note">
          Dashboard generated at {escape(meta['generated_at'])}.
          Source timestamp: {escape(meta['timestamp'])}.
        </p>
        """
    )
    if data["mode"] == "analysis":
        parts.append("<h3>Selected source runs</h3>")
        parts.append(render_selected_runs_section(data["selected_runs"]))
    else:
        parts.append(
            f"""
            <div class="subpanel">
              <h3>Comparison context</h3>
              <p class="lede"><strong>Baseline:</strong> {escape(meta['baseline_run_dir'])}</p>
              <p class="lede"><strong>Candidate:</strong> {escape(meta['candidate_run_dir'])}</p>
            </div>
            """
        )
        if data.get("baseline_selected_runs"):
            parts.append("<h3>Baseline source runs</h3>")
            parts.append(render_selected_runs_section(data["baseline_selected_runs"]))
        if data.get("candidate_selected_runs"):
            parts.append("<h3>Candidate source runs</h3>")
            parts.append(render_selected_runs_section(data["candidate_selected_runs"]))
    return "".join(parts)


def render_failure_explorer_shell() -> str:
    return """
    <div id="failure-explorer" class="section-stack">
      <div class="controls-grid">
        <div class="control-field">
          <label for="failure-path">Path</label>
          <select id="failure-path" data-filter="path"></select>
        </div>
        <div class="control-field">
          <label for="failure-locale">Locale</label>
          <select id="failure-locale" data-filter="locale"></select>
        </div>
        <div class="control-field">
          <label for="failure-style">Style</label>
          <select id="failure-style" data-filter="style"></select>
        </div>
        <div class="control-field">
          <label for="failure-issue">Issue ID</label>
          <input id="failure-issue" data-filter="issue" type="search" placeholder="Search an issue id" />
        </div>
      </div>
      <p class="inline-note" data-role="failure-count"></p>
      <div class="table-wrap">
        <table class="data-table js-sortable">
          <thead>
            <tr>
              <th><button class="sort-button" type="button">Path identifier</button></th>
              <th><button class="sort-button" type="button">Locale</button></th>
              <th><button class="sort-button" type="button">Style</button></th>
              <th><button class="sort-button" type="button">Issue</button></th>
              <th><button class="sort-button" type="button">Query</button></th>
              <th><button class="sort-button" type="button">Helpful found</button></th>
              <th><button class="sort-button" type="button">Link source</button></th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
    """


def render_issue_drilldown_shell() -> str:
    return """
    <div id="issue-drilldown" class="section-stack">
      <div class="controls-grid">
        <div class="control-field">
          <label for="issue-search">Search issue</label>
          <input id="issue-search" data-role="issue-search" type="search" placeholder="Search by issue, product, persona, or intent" />
        </div>
      </div>
      <p class="inline-note" data-role="issue-count"></p>
      <div class="split-layout">
        <div class="issue-list" data-role="issue-list"></div>
        <div class="issue-detail" data-role="issue-detail"></div>
      </div>
    </div>
    """


def _wrap_with_chart_toggle(section_id: str, table_html: str, lede: str = "") -> str:
    lede_html = f"<p class='lede'>{escape(lede)}</p>" if lede else ""
    return (
        f'{lede_html}'
        f'<div class="view-toggle" data-chart-section="{escape(section_id)}">'
        f'<button class="view-toggle__btn active" type="button" data-view="table">'
        f'Table{render_help_tip("view_table", aria_label="Table view")}</button>'
        f'<button class="view-toggle__btn" type="button" data-view="chart">'
        f'Bar chart{render_help_tip("view_bar", aria_label="Bar chart")}</button>'
        f'</div>'
        f'<div class="table-view" data-role="table-view">{table_html}</div>'
        f'<div class="chart-container" data-role="chart-view">'
        f'<canvas id="chart-{escape(section_id)}"></canvas>'
        f'</div>'
    )


def _wrap_with_path_views(section_id: str, table_html: str, heatmap_html: str, lede: str = "") -> str:
    lede_html = f"<p class='lede'>{escape(lede)}</p>" if lede else ""
    return (
        f'{lede_html}'
        f'<div class="view-toggle" data-chart-section="{escape(section_id)}">'
        f'<button class="view-toggle__btn active" type="button" data-view="table">'
        f'Table{render_help_tip("view_table", aria_label="Table view")}</button>'
        f'<button class="view-toggle__btn" type="button" data-view="chart">'
        f'Bar chart{render_help_tip("view_bar", aria_label="Bar chart")}</button>'
        f'<button class="view-toggle__btn" type="button" data-view="heatmap">'
        f'Heatmap{render_help_tip("heatmap", aria_label="Heatmap view")}</button>'
        f'</div>'
        f'<div class="metric-toggle" data-metric-toggle="{escape(section_id)}">'
        f'<button class="metric-toggle__btn active" type="button" data-metric="pass">'
        f'Pass rate{render_help_tip("metric_toggle_pass", aria_label="Pass rate chart")}</button>'
        f'<button class="metric-toggle__btn" type="button" data-metric="mrr">'
        f'MRR{render_help_tip("metric_toggle_mrr", aria_label="MRR chart")}</button>'
        f'</div>'
        f'<div class="table-view" data-role="table-view">{table_html}</div>'
        f'<div class="chart-container" data-role="chart-view">'
        f'<canvas id="chart-{escape(section_id)}"></canvas>'
        f'</div>'
        f'<div class="heatmap-view" data-role="heatmap-view">{heatmap_html}</div>'
    )


def render_sections(data: dict[str, Any]) -> tuple[str, str]:
    sections: list[tuple[str, str, str, bool]] = []
    sections.append(("overview", "Overview", render_overview_section(data), True))

    if data["mode"] == "analysis":
        path_table = render_path_rows(data["path_rows"])
        if data["docs_assistant_source_rows"]:
            path_table += "<h3>Docs Assistant link-source split</h3>"
            path_table += render_path_rows(data["docs_assistant_source_rows"])
        path_body = _wrap_with_path_views(
            "paths",
            path_table,
            render_path_locale_heatmap(data["path_rows"]),
            "Weighted path and locale performance from processed analysis outputs.",
        )
        sections.append(("paths", "Path Performance", path_body, True))
        if data.get("path_family_rows"):
            family_body = _wrap_with_chart_toggle(
                "path-families",
                render_path_family_rows(data["path_family_rows"]),
                "Weighted target pass and MRR grouped by discovery path family.",
            )
            sections.append(("path-families", "Path Families", family_body, True))
        sections.append(
            ("locales", "Locale View", _wrap_with_chart_toggle(
                "locales", render_dimension_rows(data["locale_rows"], "locale"),
            ), True)
        )
        locale_gap_html = render_locale_gap_table(data.get("locale_gap_rows", []))
        sections.append(
            (
                "locale-gaps",
                "Locale Gap vs EN",
                f"<p class='lede'>Pass-rate gap relative to English for each path.</p>{locale_gap_html}",
                True,
            )
        )
        sections.append(("styles", "Style View", _wrap_with_chart_toggle(
            "styles", render_dimension_rows(data["style_rows"], "style"),
        ), True))
        sections.append(
            ("personas", "Persona View", _wrap_with_chart_toggle(
                "personas", render_dimension_rows(data["persona_rows"], "persona"),
            ), False)
        )
        if data.get("style_locale_rows"):
            sections.append(
                (
                    "styles-locale",
                    "Styles per Locale",
                    _wrap_with_chart_toggle(
                        "styles-locale",
                        render_composite_dimension_rows(
                            data["style_locale_rows"],
                            lambda row: f"{row['style']} / {row['locale'].upper()}",
                        ),
                    ),
                    False,
                )
            )
        if data.get("persona_locale_rows"):
            sections.append(
                (
                    "personas-locale",
                    "Personas per Locale",
                    _wrap_with_chart_toggle(
                        "personas-locale",
                        render_composite_dimension_rows(
                            data["persona_locale_rows"],
                            lambda row: f"{row['persona']} / {row['locale'].upper()}",
                        ),
                    ),
                    False,
                )
            )
        if data.get("portal_rows"):
            sections.append(
                (
                    "portals",
                    "Portals by Locale",
                    _wrap_with_chart_toggle(
                        "portals",
                        render_composite_dimension_rows(
                            data["portal_rows"],
                            lambda row: f"{row['portal']} / {row['locale'].upper()}",
                        ),
                    ),
                    False,
                )
            )
        sections.append(("issues", "Worst Issues", render_worst_issues(data["worst_issues"]), False))
        sections.append(("failures", "Failure Explorer", render_failure_explorer_shell(), False))
        sections.append(("issue-detail", "Issue Drilldown", render_issue_drilldown_shell(), False))
    else:
        sections.append(
            (
                "movers",
                "Top Movers",
                render_movers_html(data.get("top_movers", {})),
                True,
            )
        )
        path_table = render_path_rows(data["path_rows"], comparison=True)
        if data["docs_assistant_source_rows"]:
            path_table += "<h3>Docs Assistant link-source deltas</h3>"
            path_table += render_path_rows(data["docs_assistant_source_rows"], comparison=True)
        path_body = _wrap_with_path_views(
            "paths",
            path_table,
            render_path_locale_heatmap(data["path_rows"], comparison=True),
            "Candidate minus baseline deltas by path and locale.",
        )
        sections.append(("paths", "Path Delta View", path_body, True))
        if data.get("path_family_rows"):
            family_body = _wrap_with_chart_toggle(
                "path-families",
                render_path_family_rows(data["path_family_rows"], comparison=True),
                "Weighted delta pass and MRR grouped by discovery path family.",
            )
            sections.append(("path-families", "Path Families", family_body, True))
        sections.append(
            ("locales", "Locale Delta View", _wrap_with_chart_toggle(
                "locales", render_dimension_rows(data["locale_rows"], "locale", comparison=True),
            ), True)
        )
        sections.append(
            ("styles", "Style Delta View", _wrap_with_chart_toggle(
                "styles", render_dimension_rows(data["style_rows"], "style", comparison=True),
            ), True)
        )
        if data.get("persona_rows"):
            sections.append(
                ("personas", "Persona Delta View", _wrap_with_chart_toggle(
                    "personas", render_dimension_rows(data["persona_rows"], "persona", comparison=True),
                ), False)
            )
        if data.get("style_locale_rows"):
            style_locale_body = _wrap_with_chart_toggle(
                "styles-locale",
                render_composite_dimension_rows(
                    data["style_locale_rows"],
                    lambda row: f"{row['style']} / {row['locale'].upper()}",
                    comparison=True,
                ),
            )
            sections.append(("styles-locale", "Style per Locale Deltas", style_locale_body, False))
        if data.get("persona_locale_rows"):
            persona_locale_body = _wrap_with_chart_toggle(
                "personas-locale",
                render_composite_dimension_rows(
                    data["persona_locale_rows"],
                    lambda row: f"{row['persona']} / {row['locale'].upper()}",
                    comparison=True,
                ),
            )
            sections.append(("personas-locale", "Persona per Locale Deltas", persona_locale_body, False))
        locale_gap_html = render_locale_gap_table(data.get("locale_gap_rows", []), comparison=True)
        sections.append(
            (
                "locale-gaps",
                "Locale Gap vs EN",
                f"<p class='lede'>Candidate pass-rate gap relative to English, with baseline and delta-of-gap context.</p>{locale_gap_html}",
                True,
            )
        )
        if data.get("issue_comparison_rows"):
            sections.append(
                (
                    "issue-comparison",
                    "Issue Regressions / Improvements",
                    render_issue_comparison_section(data["issue_comparison_rows"]),
                    False,
                )
            )
        if data.get("failure_delta"):
            counts = data["failure_delta"]
            summary = (
                f"<p class='lede'>New failures: {len(counts.get('new_failures', []))} | "
                f"Resolved: {len(counts.get('resolved_failures', []))} | "
                f"Still failing: {len(counts.get('still_failing', []))}</p>"
            )
            sections.append(
                ("failure-delta", "Failure Changes", summary + render_failure_delta_shell(), False)
            )

    nav = "".join(
        f'<a class="section-nav__link" href="#{escape(section_id)}">'
        f"{render_label_with_help(title, section_id)}</a>"
        for section_id, title, _, _ in sections
    )
    rendered_sections = "".join(
        render_panel(section_id, title, body, open_by_default=open_by_default)
        for section_id, title, body, open_by_default in sections
    )
    return nav, rendered_sections


def render_data_js(data: dict[str, Any]) -> str:
    payload = {
        "mode": data["mode"],
        "issues": data.get("issues", []),
        "failure_rows": data.get("failure_rows", []),
        "path_rows": data.get("path_rows", []),
        "locale_rows": data.get("locale_rows", []),
        "style_rows": data.get("style_rows", []),
        "persona_rows": data.get("persona_rows", []),
        "style_locale_rows": data.get("style_locale_rows", []),
        "persona_locale_rows": data.get("persona_locale_rows", []),
        "issue_comparison_rows": data.get("issue_comparison_rows", []),
        "failure_delta": data.get("failure_delta", {}),
        "locale_gap_rows": data.get("locale_gap_rows", []),
        "portal_rows": data.get("portal_rows", []),
        "path_family_rows": data.get("path_family_rows", []),
        "docs_assistant_source_rows": data.get("docs_assistant_source_rows", []),
    }
    return "window.ANALYSIS_DASHBOARD_DATA = " + json.dumps(payload, ensure_ascii=False) + ";\n"


def _markdown_mover_lines(movers: dict[str, list[dict[str, Any]]], n: int = 5) -> list[str]:
    lines: list[str] = []
    for heading, key in (
        ("### Top improvements", "improvements"),
        ("### Top regressions", "regressions"),
    ):
        items = movers.get(key, [])[:n]
        lines.append(heading)
        if not items:
            lines.append("- No data.")
            continue
        for item in items:
            sign = "+" if item["delta"] >= 0 else ""
            lines.append(
                f"- **{item['label']}**: {sign}{item['delta'] * 100:.2f}pp "
                f"({percent_text(item['first'])} → {percent_text(item['last'])})"
            )
    return lines


def render_markdown_summary(view_model: dict[str, Any]) -> str:
    mode = view_model["mode"]
    meta = view_model["meta"]
    lines = [
        f"# {view_model['dashboard_title']}",
        "",
        view_model["dashboard_subtitle"],
        "",
        f"**Generated:** {meta['generated_at']}",
        "",
        "## Headline metrics",
        "",
    ]
    for card in view_model["cards"]:
        lines.append(f"- **{card['label']}:** {card['value']} — {card['note']}")
    lines.append("")

    if view_model.get("callouts"):
        lines.append("## Highlights")
        lines.append("")
        for callout in view_model["callouts"]:
            lines.append(f"- **{callout['label']}:** {callout['value']} — {callout['note']}")
        lines.append("")

    if mode == "comparison" and view_model.get("top_movers"):
        lines.extend(_markdown_mover_lines(view_model["top_movers"]))
        lines.append("")

    issue_rows = view_model.get("issue_comparison_rows") or []
    if mode == "comparison" and issue_rows:
        comparable = [
            row for row in issue_rows
            if first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate") is not None
        ]
        if comparable:
            worst = min(
                comparable,
                key=lambda row: first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate"),
            )
            best = max(
                comparable,
                key=lambda row: first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate"),
            )
            lines.extend(
                [
                    "## Issue-level changes",
                    "",
                    f"- **Largest issue regression:** {worst.get('issue_id')} "
                    f"({percent_text(first_present(worst, 'delta_target_pass_rate', 'delta_expected_pass_rate'))})",
                    f"- **Largest issue improvement:** {best.get('issue_id')} "
                    f"({percent_text(first_present(best, 'delta_target_pass_rate', 'delta_expected_pass_rate'))})",
                    "",
                ]
            )

    gap_rows = view_model.get("locale_gap_rows") or []
    if gap_rows:
        es_gaps = [row for row in gap_rows if row.get("es_gap_vs_en") is not None]
        if es_gaps:
            weakest = min(es_gaps, key=lambda row: row["es_gap_vs_en"])
            lines.extend(
                [
                    "## Locale gap vs EN",
                    "",
                    f"- **Largest ES gap:** {weakest.get('path')} "
                    f"({percent_text(weakest.get('es_gap_vs_en'))} vs EN)",
                    "",
                ]
            )

    failure_delta = view_model.get("failure_delta") or {}
    if mode == "comparison" and failure_delta:
        lines.extend(
            [
                "## Failure changes",
                "",
                f"- **New failures:** {len(failure_delta.get('new_failures', []))}",
                f"- **Resolved failures:** {len(failure_delta.get('resolved_failures', []))}",
                f"- **Still failing:** {len(failure_delta.get('still_failing', []))}",
                "",
            ]
        )

    warnings = view_model.get("warnings") or []
    if warnings:
        lines.extend(["## Warnings", ""])
        for warning in warnings:
            lines.append(f"- **{warning['title']}:** {warning['message']}")
            for item in warning.get("items") or []:
                lines.append(f"  - {item}")
        lines.append("")

    if mode == "comparison":
        lines.extend(
            [
                "## Comparison context",
                "",
                f"- **Baseline:** `{meta['baseline_run_dir']}`",
                f"- **Candidate:** `{meta['candidate_run_dir']}`",
                "",
            ]
        )
    elif mode == "analysis":
        lines.extend(
            [
                "## Selected source runs",
                "",
            ]
        )
        for run in view_model.get("selected_runs", []):
            lines.append(
                f"- `{run['source_key']}` → `{run['run_dir']}` "
                f"(healthy: {run['is_healthy']}, full: {run['is_full']})"
            )
        lines.append("")

    lines.extend(
        [
            "## Dashboard",
            "",
            "Open `index.html` in this folder for the full interactive dashboard.",
            "",
        ]
    )
    if view_model.get("notes"):
        lines.append("## Notes")
        lines.append("")
        for note in view_model["notes"]:
            lines.append(f"- {note}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def render_timeline_markdown_summary(data: dict[str, Any], timeline_filename: str) -> str:
    runs = data.get("runs", [])
    lines = [
        "# Timeline Dashboard Summary",
        "",
        f"**Runs:** {len(runs)}",
        "",
        f"**Generated:** {utc_now_iso()}",
        "",
    ]
    if len(runs) >= 2:
        first = runs[0]
        last = runs[-1]
        first_pass = first.get("target_pass_rate")
        last_pass = last.get("target_pass_rate")
        if first_pass is not None and last_pass is not None:
            delta = last_pass - first_pass
            sign = "+" if delta >= 0 else ""
            lines.extend(
                [
                    "## Overall change (first → last run)",
                    "",
                    f"- **Target pass rate:** {percent_text(first_pass)} → {percent_text(last_pass)} "
                    f"({sign}{delta * 100:.2f}pp)",
                    "",
                ]
            )

    if data.get("top_movers"):
        lines.extend(_markdown_mover_lines(data["top_movers"]))
        lines.append("")

    lines.extend(
        [
            "## Runs",
            "",
        ]
    )
    for run in runs:
        lines.append(
            f"- `{run['label']}` — {run['run_dir']}: "
            f"{percent_text(run.get('target_pass_rate'))} target pass, "
            f"{decimal_text(run.get('mrr'))} MRR"
        )
    lines.extend(
        [
            "",
            "## Dashboard",
            "",
            f"Open `{timeline_filename}` in this folder for charts and drill-down tables.",
            "",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def write_dashboard(
    context: DashboardContext,
    view_model: dict[str, Any],
    *,
    report_format: str | None = None,
    related_links: list[tuple[str, Path]] | None = None,
) -> None:
    output_assets_dir = context.output_dir / "assets"
    write_dashboard_assets(output_assets_dir, include_analysis_css=True)
    write_text(output_assets_dir / "dashboard-data.js", render_data_js(view_model))

    nav_html, sections_html = render_sections(view_model)
    nav_bar_html = render_dashboard_nav_html(
        context.output_dir,
        collect_dashboard_nav_crumbs(
            context.output_dir,
            mode=context.mode,
            view_model=view_model,
            run_dir=context.run_dir,
        ),
    )
    related_html = render_related_links_html(context.output_dir, related_links or [])
    help_html = render_dashboard_help_panel(view_model["mode"])
    html_template = load_asset("analysis_dashboard.html")
    html_output = (
        html_template.replace("__PAGE_TITLE__", escape(view_model["page_title"]))
        .replace("__MODE__", escape(view_model["mode"]))
        .replace("__DASHBOARD_TITLE__", escape(view_model["dashboard_title"]))
        .replace("__DASHBOARD_SUBTITLE__", escape(view_model["dashboard_subtitle"]))
        .replace("__DASHBOARD_NAV__", nav_bar_html)
        .replace("__DASHBOARD_HELP__", help_html)
        .replace("__RELATED_LINKS__", related_html)
        .replace("__SECTION_NAV__", nav_html)
        .replace("__SECTIONS__", sections_html)
    )
    write_text(context.output_dir / "index.html", html_output)
    if report_format == "markdown":
        write_text(context.output_dir / "summary.md", render_markdown_summary(view_model))


def _collect_timeline_series(
    runs: list[dict[str, Any]],
    rows_key: str,
    group_key: str,
    metric_key: str,
    label_fn: Any = None,
) -> dict[str, list[float | None]]:
    data: dict[str, list[float | None]] = {}
    for idx, run in enumerate(runs):
        seen: set[str] = set()
        for row in run.get(rows_key, []):
            key = label_fn(row) if label_fn else row[group_key]
            seen.add(key)
            data.setdefault(key, [None] * idx)
            data[key].append(row.get(metric_key))
        for key in data:
            if key not in seen:
                if len(data[key]) <= idx:
                    data[key].extend([None] * (idx + 1 - len(data[key])))
                else:
                    data[key].append(None)
    return data


def _compute_issue_trends(runs: list[dict[str, Any]], labels: list[str]) -> list[dict[str, Any]]:
    issue_pass_rates: dict[str, list[float | None]] = {}
    for idx, run in enumerate(runs):
        seen: set[str] = set()
        for issue in run.get("issues_processed", []):
            iid = issue["issue_id"]
            seen.add(iid)
            agg = issue.get("aggregates", {}).get("by_path_locale", {})
            tested = 0
            hits = 0
            for path_id, a in agg.items():
                if path_id.endswith(".markdown") or path_id.endswith(".suggested_sources"):
                    continue
                n = int(a.get("n_tested_styles", 0))
                tested += n
                hits += round(float(first_present(a, "target_pass_rate", "expected_pass_rate") or 0) * n)
            rate = (hits / tested) if tested else None
            issue_pass_rates.setdefault(iid, [None] * idx)
            issue_pass_rates[iid].append(round(rate, 6) if rate is not None else None)
        for iid in issue_pass_rates:
            if iid not in seen:
                if len(issue_pass_rates[iid]) <= idx:
                    issue_pass_rates[iid].extend([None] * (idx + 1 - len(issue_pass_rates[iid])))
                else:
                    issue_pass_rates[iid].append(None)

    result = []
    for iid, rates in sorted(issue_pass_rates.items()):
        first = next((v for v in rates if v is not None), None)
        last = next((v for v in reversed(rates) if v is not None), None)
        delta = round(last - first, 6) if first is not None and last is not None else None
        result.append({"issue_id": iid, "pass_rates": rates, "first": first, "last": last, "delta": delta})
    return result


def _compute_top_movers(
    runs: list[dict[str, Any]],
    rows_key: str,
    label_fn: Any,
    metric_key: str = "target_pass_rate",
    n: int = 5,
) -> dict[str, list[dict[str, Any]]]:
    first_run = runs[0]
    last_run = runs[-1]
    first_index: dict[str, float] = {}
    for row in first_run.get(rows_key, []):
        key = label_fn(row)
        val = row.get(metric_key)
        if val is not None:
            first_index[key] = val
    last_index: dict[str, float] = {}
    for row in last_run.get(rows_key, []):
        key = label_fn(row)
        val = row.get(metric_key)
        if val is not None:
            last_index[key] = val

    deltas = []
    for key in set(first_index) | set(last_index):
        first_val = first_index.get(key)
        last_val = last_index.get(key)
        if first_val is not None and last_val is not None:
            deltas.append({"label": key, "first": round(first_val, 6), "last": round(last_val, 6), "delta": round(last_val - first_val, 6)})

    improvements = sorted(deltas, key=lambda d: d["delta"], reverse=True)[:n]
    regressions = sorted(deltas, key=lambda d: d["delta"])[:n]
    return {"improvements": improvements, "regressions": regressions}


def _classify_issue_portal(target_docs: list[str]) -> str:
    has_hc = any("help.vtex.com" in url for url in target_docs)
    has_dp = any("developers.vtex.com" in url for url in target_docs)
    if has_hc and has_dp:
        return "Both"
    if has_dp:
        return "Developer Portal"
    return "Help Center"


def _derive_portal_locale_from_issues(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Derive portal×locale pass-rate aggregation from issues_processed.json.

    Classifies each issue as Help Center or Developer Portal based on its
    target_docs URLs, then aggregates all query results across every
    discovery path for each (portal, locale) pair.
    """
    from collections import defaultdict
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for issue in issues:
        portal = _classify_issue_portal(first_present(issue, "target_docs", "expected_docs") or [])
        per_path_style = issue.get("per_path_style", {})
        for _path_key, variants in per_path_style.items():
            if not isinstance(variants, list):
                continue
            for variant_dict in variants:
                for _variant_key, locale_dict in variant_dict.items():
                    if not isinstance(locale_dict, dict):
                        continue
                    for locale, style_dict in locale_dict.items():
                        if not isinstance(style_dict, dict):
                            continue
                        for _style, query_data in style_dict.items():
                            if not isinstance(query_data, dict):
                                continue
                            combined = query_data.get("combined_ranked_list", query_data)
                            if combined.get("coverage_status") == "tested":
                                buckets[(portal, locale)].append(combined)

    rows: list[dict[str, Any]] = []
    for (portal, locale), records in sorted(buckets.items()):
        n = len(records)
        if n == 0:
            continue
        pass_count = sum(1 for r in records if first_present(r, "target_found", "expected_found"))
        mrr_sum = sum(first_present(r, "target_mrr", "expected_mrr",) or 0 for r in records)
        rows.append({
            "portal": portal,
            "locale": locale,
            "n_tested_queries": n,
            "target_pass_rate": round(pass_count / n, 6) if n else None,
            "target_mean_mrr": round(mrr_sum / n, 6) if n else None,
        })
    return rows


def _read_json_optional(path: Path) -> list[dict[str, Any]]:
    return read_json(path) if path.exists() else []


def _derive_style_locale_from_issues(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Derive style×locale pass-rate aggregation from issues_processed.json."""
    from collections import defaultdict
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for issue in issues:
        per_path_style = issue.get("per_path_style", {})
        for _path_key, variants in per_path_style.items():
            if not isinstance(variants, list):
                continue
            for variant_dict in variants:
                for _variant_key, locale_dict in variant_dict.items():
                    if not isinstance(locale_dict, dict):
                        continue
                    for locale, style_dict in locale_dict.items():
                        if not isinstance(style_dict, dict):
                            continue
                        for style, query_data in style_dict.items():
                            if not isinstance(query_data, dict):
                                continue
                            combined = query_data.get("combined_ranked_list", query_data)
                            if combined.get("coverage_status") == "tested":
                                buckets[(style, locale)].append(combined)

    rows: list[dict[str, Any]] = []
    for (style, locale), records in sorted(buckets.items()):
        n = len(records)
        if n == 0:
            continue
        pass_count = sum(1 for r in records if first_present(r, "target_found", "expected_found"))
        mrr_sum = sum(first_present(r, "target_mrr", "expected_mrr") or 0 for r in records)
        rows.append({
            "style": style,
            "locale": locale,
            "n_tested_queries": n,
            "target_pass_rate": round(pass_count / n, 6) if n else None,
            "target_mean_mrr": round(mrr_sum / n, 6) if n else None,
        })
    return rows


def _derive_persona_locale_from_issues(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Derive persona×locale pass-rate aggregation from issues_processed.json."""
    from collections import defaultdict
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for issue in issues:
        persona = issue.get("persona", "Unknown")
        per_path_style = issue.get("per_path_style", {})
        for _path_key, variants in per_path_style.items():
            if not isinstance(variants, list):
                continue
            for variant_dict in variants:
                for _variant_key, locale_dict in variant_dict.items():
                    if not isinstance(locale_dict, dict):
                        continue
                    for locale, style_dict in locale_dict.items():
                        if not isinstance(style_dict, dict):
                            continue
                        for _style, query_data in style_dict.items():
                            if not isinstance(query_data, dict):
                                continue
                            combined = query_data.get("combined_ranked_list", query_data)
                            if combined.get("coverage_status") == "tested":
                                buckets[(persona, locale)].append(combined)

    rows: list[dict[str, Any]] = []
    for (persona, locale), records in sorted(buckets.items()):
        n = len(records)
        if n == 0:
            continue
        pass_count = sum(1 for r in records if first_present(r, "target_found", "expected_found"))
        mrr_sum = sum(first_present(r, "target_mrr", "expected_mrr") or 0 for r in records)
        rows.append({
            "persona": persona,
            "locale": locale,
            "n_tested_queries": n,
            "target_pass_rate": round(pass_count / n, 6) if n else None,
            "target_mean_mrr": round(mrr_sum / n, 6) if n else None,
        })
    return rows


def build_timeline_data(run_dirs: list[Path]) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    for run_dir in run_dirs:
        summary = read_json(run_dir / "run_summary.json")
        path_locale_rows = read_json(run_dir / "aggregates_by_path_locale.json")
        locale_rows = read_json(run_dir / "aggregates_by_locale.json")
        style_rows = read_json(run_dir / "aggregates_by_style.json")
        issues_file = run_dir / "issues_processed.json"
        issues_processed = read_json(issues_file) if issues_file.exists() else []
        sl_file = run_dir / "aggregates_by_style_locale.json"
        pl_file = run_dir / "aggregates_by_persona_locale.json"
        style_locale_rows = read_json(sl_file) if sl_file.exists() else _derive_style_locale_from_issues(issues_processed)
        persona_locale_rows = read_json(pl_file) if pl_file.exists() else _derive_persona_locale_from_issues(issues_processed)
        runs.append({
            "run_dir": run_dir,
            "summary": summary,
            "path_locale_rows": [r for r in path_locale_rows if r.get("link_source") is None],
            "portal_rows": _derive_portal_locale_from_issues(issues_processed),
            "locale_rows": locale_rows,
            "style_rows": style_rows,
            "style_locale_rows": style_locale_rows,
            "persona_locale_rows": persona_locale_rows,
            "issues_processed": issues_processed,
        })
    runs.sort(key=lambda r: r["summary"].get("timestamp", ""))

    labels = []
    overall_target_pass_rate = []
    overall_mrr = []
    overall_helpful_pass_rate = []

    for run in runs:
        s = run["summary"]
        ts = s.get("timestamp", s.get("run_id", "?"))
        labels.append(ts[:10] if len(ts) >= 10 else ts)
        overall_target_pass_rate.append(first_present(s, "overall_target_pass_rate", "overall_expected_pass_rate"))
        overall_mrr.append(first_present(s, "overall_target_mrr", "overall_expected_mrr"))
        overall_helpful_pass_rate.append(s.get("overall_helpful_pass_rate", s.get("overall_any_relevant_any_locale_rate")))

    path_label = lambda r: f"{r['path']} / {r['locale'].upper()}"
    path_pass = _collect_timeline_series(runs, "path_locale_rows", "path", "target_pass_rate", path_label)
    path_mrr = _collect_timeline_series(runs, "path_locale_rows", "path", "target_mean_mrr", path_label)
    locale_pass = _collect_timeline_series(runs, "locale_rows", "locale", "target_pass_rate")
    style_pass = _collect_timeline_series(runs, "style_rows", "style", "target_pass_rate")

    style_locale_label = lambda r: f"{r['style']} / {r['locale'].upper()}"
    style_locale_pass = _collect_timeline_series(runs, "style_locale_rows", "style", "target_pass_rate", style_locale_label)

    persona_locale_label = lambda r: f"{r['persona']} / {r['locale'].upper()}"
    persona_locale_pass = _collect_timeline_series(runs, "persona_locale_rows", "persona", "target_pass_rate", persona_locale_label)

    portal_label_fn = lambda r: f"{r['portal']} / {r['locale'].upper()}"
    portal_pass = _collect_timeline_series(runs, "portal_rows", "portal", "target_pass_rate", portal_label_fn)

    paths_list = [{"path": k, "pass_rates": path_pass[k], "mrr": path_mrr.get(k, [])} for k in sorted(path_pass)]
    locales_list = [{"locale": k, "pass_rates": v} for k, v in sorted(locale_pass.items())]
    styles_list = [{"style": k, "pass_rates": v} for k, v in sorted(style_pass.items())]
    styles_locale_list = [{"label": k, "pass_rates": v} for k, v in sorted(style_locale_pass.items())]
    personas_locale_list = [{"label": k, "pass_rates": v} for k, v in sorted(persona_locale_pass.items())]
    portals_list = [{"label": k, "pass_rates": v} for k, v in sorted(portal_pass.items())]
    issue_trends = _compute_issue_trends(runs, labels)
    top_movers = _compute_top_movers(runs, "path_locale_rows", path_label)

    return {
        "labels": labels,
        "overall_target_pass_rate": overall_target_pass_rate,
        "overall_mrr": overall_mrr,
        "overall_helpful_pass_rate": overall_helpful_pass_rate,
        "paths": paths_list,
        "locales": locales_list,
        "styles": styles_list,
        "styles_locale": styles_locale_list,
        "personas_locale": personas_locale_list,
        "portals": portals_list,
        "issue_trends": issue_trends,
        "top_movers": top_movers,
        "runs": [
            {
                "label": labels[i],
                "run_dir": relative_display(runs[i]["run_dir"]),
                "analysis_id": runs[i]["summary"].get("analysis_id", "-"),
                "total_queries": runs[i]["summary"].get("total_queries"),
                "target_pass_rate": first_present(runs[i]["summary"], "overall_target_pass_rate", "overall_expected_pass_rate"),
                "mrr": first_present(runs[i]["summary"], "overall_target_mrr", "overall_expected_mrr"),
                "helpful_pass_rate": runs[i]["summary"].get("overall_helpful_pass_rate", runs[i]["summary"].get("overall_any_relevant_any_locale_rate")),
            }
            for i in range(len(runs))
        ],
    }


def render_timeline_summary_cards(data: dict[str, Any]) -> str:
    runs = data["runs"]
    if not runs:
        return ""
    first = runs[0]
    last = runs[-1]

    def _delta_html(first_val: float | None, last_val: float | None) -> str:
        if first_val is None or last_val is None:
            return '<span class="neutral">-</span>'
        delta = last_val - first_val
        sign = "+" if delta >= 0 else ""
        css = "up" if delta >= 0 else "down"
        return f'<span class="{css}">{sign}{delta * 100:.2f}pp</span>'

    cards = [
        {
            "label": "Total Runs",
            "value": str(len(runs)),
            "note": f"{first['label']} to {last['label']}",
        },
        {
            "label": "Target Pass (latest)",
            "value": percent_text(last["target_pass_rate"]),
            "note_html": _delta_html(first["target_pass_rate"], last["target_pass_rate"]) + " vs first run",
        },
        {
            "label": "MRR (latest)",
            "value": decimal_text(last["mrr"]),
            "note_html": _delta_html(first["mrr"], last["mrr"]) + " vs first run",
        },
        {
            "label": "Helpful Pass (latest)",
            "value": percent_text(last["helpful_pass_rate"]),
            "note_html": _delta_html(first["helpful_pass_rate"], last["helpful_pass_rate"]) + " vs first run",
        },
    ]
    items = []
    for card in cards:
        note_html = card.get("note_html", escape(card.get("note", "")))
        items.append(
            f'<article class="metric-card">'
            f'<p class="metric-card__label">{render_label_with_help(card["label"])}</p>'
            f'<p class="metric-card__value">{escape(card["value"])}</p>'
            f'<p class="metric-card__note">{note_html}</p>'
            f'</article>'
        )
    return f'<div class="card-grid">{"".join(items)}</div>'


def _delta_cell(prev: float | None, curr: float | None) -> str:
    if prev is None or curr is None:
        return ""
    delta = curr - prev
    return f' data-delta="{delta:.6f}"'


def render_timeline_runs_table(data: dict[str, Any]) -> str:
    if not data["runs"]:
        return "<p>No runs found.</p>"
    header = (
        "<tr><th>#</th><th>Date</th><th>Analysis ID</th>"
        "<th>Queries</th><th>Target Pass</th><th>MRR</th>"
        "<th>Helpful Pass</th></tr>"
    )
    rows_html = []
    for i, run in enumerate(data["runs"]):
        prev = data["runs"][i - 1] if i > 0 else None
        pr_delta = _delta_cell(prev["target_pass_rate"] if prev else None, run["target_pass_rate"])
        mrr_delta = _delta_cell(prev["mrr"] if prev else None, run["mrr"])
        hp_delta = _delta_cell(prev["helpful_pass_rate"] if prev else None, run["helpful_pass_rate"])
        rows_html.append(
            f"<tr><td>{i + 1}</td>"
            f"<td>{escape(run['label'])}</td>"
            f"<td>{escape(run['analysis_id'])}</td>"
            f"<td>{int_text(run['total_queries'])}</td>"
            f'<td class="runs-delta-cell"{pr_delta}>{percent_text(run["target_pass_rate"])}</td>'
            f'<td class="runs-delta-cell"{mrr_delta}>{decimal_text(run["mrr"])}</td>'
            f'<td class="runs-delta-cell"{hp_delta}>{percent_text(run["helpful_pass_rate"])}</td></tr>'
        )
    return f'<div class="table-wrap"><table class="data-table"><thead>{header}</thead><tbody>{"".join(rows_html)}</tbody></table></div>'


def render_movers_html(movers: dict[str, Any]) -> str:
    improvements = movers.get("improvements", [])
    regressions = movers.get("regressions", [])

    def _mover_list(items: list[dict[str, Any]], is_improvement: bool) -> str:
        if not items:
            return "<p>No data.</p>"
        rows = []
        for item in items:
            sign = "+" if item["delta"] >= 0 else ""
            css = "up" if is_improvement else "down"
            rows.append(
                f'<li><span>{escape(item["label"])}</span>'
                f'<span class="{css}">{sign}{item["delta"] * 100:.2f}pp '
                f'({percent_text(item["first"])} → {percent_text(item["last"])})</span></li>'
            )
        return f'<ul class="movers-list">{"".join(rows)}</ul>'

    return (
        '<div class="movers-grid">'
        f'<div><h3 class="up">Top Improvements</h3>{_mover_list(improvements, True)}</div>'
        f'<div><h3 class="down">Top Regressions</h3>{_mover_list(regressions, False)}</div>'
        '</div>'
    )



def _timeline_filename() -> str:
    now = datetime.now(timezone.utc)
    return f"timeline_{now:%Y-%m-%d_%H-%M}.html"


def write_timeline_dashboard(
    run_dirs: list[Path],
    output_dir: Path,
    *,
    report_format: str | None = None,
    related_links: list[tuple[str, Path]] | None = None,
) -> str:
    data = build_timeline_data(run_dirs)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_dashboard_assets(output_dir / "assets")

    template = load_asset("timeline_dashboard.html")
    nav_bar_html = render_dashboard_nav_html(
        output_dir,
        collect_dashboard_nav_crumbs(output_dir, mode="timeline"),
    )
    related_html = render_related_links_html(output_dir, related_links or [])
    summary_cards = render_timeline_summary_cards(data)
    runs_table = render_timeline_runs_table(data)
    movers_html = render_movers_html(data.get("top_movers", {}))

    chart_data = {
        "labels": data["labels"],
        "overall_target_pass_rate": data["overall_target_pass_rate"],
        "overall_mrr": data["overall_mrr"],
        "overall_helpful_pass_rate": data["overall_helpful_pass_rate"],
        "paths": data["paths"],
        "locales": data["locales"],
        "styles": data["styles"],
        "styles_locale": data["styles_locale"],
        "personas_locale": data["personas_locale"],
        "portals": data["portals"],
        "issue_trends": data["issue_trends"],
    }

    n_runs = len(data["runs"])
    first_label = data["runs"][0]["label"] if data["runs"] else "?"
    last_label = data["runs"][-1]["label"] if data["runs"] else "?"

    html_output = (
        template
        .replace("__PAGE_TITLE__", "Timeline Dashboard")
        .replace("__DASHBOARD_TITLE__", "Timeline Dashboard")
        .replace("__DASHBOARD_SUBTITLE__", f"{n_runs} runs from {first_label} to {last_label}")
        .replace("__DASHBOARD_NAV__", nav_bar_html)
        .replace("__DASHBOARD_HELP__", render_dashboard_help_panel("timeline"))
        .replace("__RELATED_LINKS__", related_html)
        .replace("__METRICS_GUIDE__", render_metrics_guide("timeline"))
        .replace("__SUMMARY_CARDS__", summary_cards)
        .replace("__RUNS_TABLE__", runs_table)
        .replace("__MOVERS_HTML__", movers_html)
        .replace("__ISSUE_TABLE__", "")
        .replace("__TIMELINE_DATA_JSON__", json.dumps(chart_data, ensure_ascii=False))
    )
    filename = _timeline_filename()
    write_text(output_dir / filename, html_output)
    write_timeline_index_redirect(output_dir, filename)
    if report_format == "markdown":
        write_text(output_dir / "summary.md", render_timeline_markdown_summary(data, filename))
    return filename


def _short_run_label(run_dir: str | Path) -> str:
    path = Path(run_dir)
    return path.name or str(run_dir)


def _comparison_step_label(summary: dict[str, Any], mode: str) -> str:
    baseline = _short_run_label(summary.get("baseline_run_dir", "?"))
    candidate = _short_run_label(summary.get("candidate_run_dir", "?"))
    if mode == "fan":
        return candidate
    return f"{baseline} → {candidate}"


def _delta_from_summary(summary: dict[str, Any], metric: str) -> float | None:
    if metric == "pass":
        return first_present(
            summary,
            "delta_overall_target_pass_rate",
            "delta_overall_expected_pass_rate",
        )
    if metric == "mrr":
        return first_present(
            summary,
            "delta_overall_target_mrr",
            "delta_overall_expected_mrr",
        )
    return first_present(
        summary,
        "delta_overall_helpful_pass_rate",
        "delta_overall_helpful_found_rate",
        "delta_overall_any_relevant_any_locale_rate",
    )


def _row_delta(row: dict[str, Any], metric: str) -> float | None:
    if metric == "pass":
        return first_present(row, "delta_target_pass_rate", "delta_expected_pass_rate")
    return first_present(row, "delta_target_mean_mrr", "delta_expected_mean_mrr")


def _path_locale_label(row: dict[str, Any]) -> str | None:
    if row.get("link_source"):
        return None
    locale = str(row.get("locale", "")).upper()
    return f"{row['path']} / {locale}"


def _cumulative_deltas(step_values: list[float | None], *, fan_mode: bool) -> list[float | None]:
    if fan_mode:
        return list(step_values)
    total = 0.0
    has_value = False
    cumulative: list[float | None] = []
    for value in step_values:
        if value is None:
            cumulative.append(round(total, 6) if has_value else None)
            continue
        has_value = True
        total += float(value)
        cumulative.append(round(total, 6))
    return cumulative


def _collect_multi_metric_series(
    comparisons: list[dict[str, Any]],
    rows_key: str,
    label_fn: Any,
    metric: str,
) -> dict[str, list[float | None]]:
    keys: set[str] = set()
    per_comparison: list[dict[str, float]] = []
    for comparison in comparisons:
        index: dict[str, float] = {}
        for row in comparison.get(rows_key, []):
            label = label_fn(row)
            if not label:
                continue
            delta = _row_delta(row, metric)
            if delta is not None:
                index[label] = float(delta)
                keys.add(label)
        per_comparison.append(index)

    series: dict[str, list[float | None]] = {key: [] for key in keys}
    for index in per_comparison:
        for key in keys:
            series[key].append(index.get(key))
    return series


def build_multi_comparison_data(multi_path: Path) -> dict[str, Any]:
    payload = read_json(multi_path)
    mode = payload.get("mode", "chain")
    comparisons = payload.get("comparisons", [])
    fan_mode = mode == "fan"

    labels = [
        _comparison_step_label(comp["summary"], mode)
        for comp in comparisons
    ]

    overall_step = {
        "target_pass_rate": [_delta_from_summary(c["summary"], "pass") for c in comparisons],
        "mrr": [_delta_from_summary(c["summary"], "mrr") for c in comparisons],
        "helpful": [_delta_from_summary(c["summary"], "helpful") for c in comparisons],
    }
    overall_cumulative = {
        key: _cumulative_deltas(values, fan_mode=fan_mode)
        for key, values in overall_step.items()
    }

    path_pass = _collect_multi_metric_series(
        comparisons,
        "by_path_locale",
        _path_locale_label,
        "pass",
    )
    path_variance = sorted(
        path_pass.items(),
        key=lambda item: max((abs(v) for v in item[1] if v is not None), default=0),
        reverse=True,
    )[:12]
    paths_list = [
        {
            "label": label,
            "step_deltas": step,
            "cumulative_deltas": _cumulative_deltas(step, fan_mode=fan_mode),
        }
        for label, step in path_variance
    ]

    locale_pass = _collect_multi_metric_series(
        comparisons,
        "by_locale",
        lambda row: str(row.get("locale", "")).lower(),
        "pass",
    )
    locales_list = [
        {"locale": locale, "step_deltas": values, "cumulative_deltas": _cumulative_deltas(values, fan_mode=fan_mode)}
        for locale, values in sorted(locale_pass.items())
    ]

    comparison_rows = []
    for comp in comparisons:
        summary = comp["summary"]
        comparison_rows.append(
            {
                "label": _comparison_step_label(summary, mode),
                "baseline": _short_run_label(summary.get("baseline_run_dir", "")),
                "candidate": _short_run_label(summary.get("candidate_run_dir", "")),
                "delta_pass": _delta_from_summary(summary, "pass"),
                "delta_mrr": _delta_from_summary(summary, "mrr"),
                "delta_helpful": _delta_from_summary(summary, "helpful"),
            }
        )

    runs = payload.get("runs", [])
    if fan_mode and payload.get("baseline"):
        baseline_label = _short_run_label(payload["baseline"]["run_dir"])
    else:
        baseline_label = _short_run_label(runs[0]["run_dir"]) if runs else "?"

    return {
        "mode": mode,
        "fan_mode": fan_mode,
        "labels": labels,
        "overall_step": overall_step,
        "overall_cumulative": overall_cumulative,
        "paths": paths_list,
        "locales": locales_list,
        "comparison_rows": comparison_rows,
        "baseline_label": baseline_label,
        "n_comparisons": len(comparisons),
        "timestamp": payload.get("timestamp", ""),
    }


def render_multi_comparison_summary_cards(data: dict[str, Any]) -> str:
    mode_label = "Fan (vs baseline)" if data["fan_mode"] else "Chain (consecutive pairs)"
    cards = [
        {
            "label": "Mode",
            "value": mode_label,
            "note": f"{data['n_comparisons']} comparison(s)",
        },
        {
            "label": "Baseline / anchor",
            "value": data["baseline_label"],
            "note": "Reference run for fan mode; first run in chain mode",
        },
    ]
    if data["labels"]:
        last = data["labels"][-1]
        last_pass = data["overall_step"]["target_pass_rate"][-1]
        sign = "+" if (last_pass or 0) >= 0 else ""
        cards.append(
            {
                "label": "Latest step delta",
                "value": f"{sign}{(last_pass or 0) * 100:.2f}pp" if last_pass is not None else "-",
                "note": last,
            }
        )
    return render_card_grid(cards)


def render_multi_comparison_comparisons_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<p class='inline-note'>No comparisons in this run.</p>"

    def _delta_cell(value: float | None) -> str:
        if value is None:
            return "<td>-</td>"
        sign = "+" if value >= 0 else ""
        css = "up" if value > 0 else "down" if value < 0 else "neutral"
        return f'<td class="{css}">{sign}{value * 100:.2f}pp</td>'

    def _mrr_delta_cell(value: float | None) -> str:
        if value is None:
            return "<td>-</td>"
        sign = "+" if value >= 0 else ""
        css = "up" if value > 0 else "down" if value < 0 else "neutral"
        return f'<td class="{css}">{sign}{decimal_text(value)}</td>'

    body_rows = []
    for row in rows:
        body_rows.append(
            "<tr>"
            f"<td>{escape(row['label'])}</td>"
            f"<td>{escape(row['baseline'])}</td>"
            f"<td>{escape(row['candidate'])}</td>"
            f"{_delta_cell(row['delta_pass'])}"
            f"{_mrr_delta_cell(row['delta_mrr'])}"
            f"{_delta_cell(row['delta_helpful'])}"
            "</tr>"
        )
    return (
        '<div class="table-wrap"><table class="data-table data-table--compact">'
        "<thead><tr><th>Comparison</th><th>Baseline</th><th>Candidate</th>"
        "<th>Δ pass</th><th>Δ MRR</th><th>Δ helpful</th></tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody></table></div>"
    )


def write_multi_comparison_dashboard(
    run_dir: Path,
    *,
    report_format: str | None = None,
    related_links: list[tuple[str, Path]] | None = None,
) -> None:
    multi_path = run_dir / "multi_comparison.json"
    if not multi_path.exists():
        raise FileNotFoundError(f"multi_comparison.json not found in {run_dir}")

    data = build_multi_comparison_data(multi_path)
    output_dir = run_dir / "dashboard"
    output_assets_dir = output_dir / "assets"
    write_dashboard_assets(output_assets_dir)

    mode_desc = (
        "Fan mode: each bar is the candidate delta versus the shared baseline."
        if data["fan_mode"]
        else "Chain mode: step bars are consecutive pair deltas; cumulative bars sum those steps from the first pair."
    )

    template = load_asset("multi_comparison_dashboard.html")
    nav_bar_html = render_dashboard_nav_html(
        output_dir,
        collect_dashboard_nav_crumbs(
            output_dir,
            mode="multi_comparison",
            run_dir=run_dir,
        ),
    )
    related_html = render_related_links_html(output_dir, related_links or [])
    html_output = (
        template.replace("__PAGE_TITLE__", "Multi-Comparison Dashboard")
        .replace("__DASHBOARD_TITLE__", "Multi-Comparison Dashboard")
        .replace(
            "__DASHBOARD_SUBTITLE__",
            f"{data['mode'].title()} mode — {data['n_comparisons']} comparison(s)",
        )
        .replace("__DASHBOARD_NAV__", nav_bar_html)
        .replace("__DASHBOARD_HELP__", render_dashboard_help_panel("multi_comparison"))
        .replace("__RELATED_LINKS__", related_html)
        .replace("__METRICS_GUIDE__", render_metrics_guide("multi_comparison"))
        .replace("__SUMMARY_CARDS__", render_multi_comparison_summary_cards(data))
        .replace("__MODE_DESCRIPTION__", escape(mode_desc))
        .replace("__COMPARISONS_TABLE__", render_multi_comparison_comparisons_table(data["comparison_rows"]))
        .replace("__MULTI_DATA_JSON__", json.dumps(
            {
                "labels": data["labels"],
                "overall_step": data["overall_step"],
                "overall_cumulative": data["overall_cumulative"],
                "paths": data["paths"],
                "locales": data["locales"],
            },
            ensure_ascii=False,
        ))
    )
    write_text(output_dir / "index.html", html_output)
    if report_format == "markdown":
        lines = [
            "# Multi-Comparison Summary",
            "",
            f"- **Mode:** {data['mode']}",
            f"- **Comparisons:** {data['n_comparisons']}",
            f"- **Baseline / anchor:** {data['baseline_label']}",
            "",
            "## Step deltas (target pass)",
            "",
        ]
        for label, delta in zip(data["labels"], data["overall_step"]["target_pass_rate"], strict=False):
            sign = "+" if (delta or 0) >= 0 else ""
            lines.append(f"- {label}: {sign}{(delta or 0) * 100:.2f}pp")
        lines.extend(["", f"Open `{output_dir.name}/index.html` for charts.", ""])
        write_text(output_dir / "summary.md", "\n".join(lines))


def scan_analysis_runs_for_index(analysis_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not analysis_root.is_dir():
        return rows

    for run_dir in analysis_root.iterdir():
        if not run_dir.is_dir():
            continue
        summary_path = run_dir / "run_summary.json"
        if not summary_path.exists():
            continue
        summary = read_json(summary_path)
        dashboard_index = run_dir / "dashboard" / "index.html"
        rows.append(
            {
                "run_id": summary.get("run_id", run_dir.name),
                "run_dir": run_dir,
                "analysis_id": summary.get("analysis_id", "-"),
                "timestamp": summary.get("timestamp", ""),
                "total_queries": summary.get("total_queries"),
                "target_pass_rate": first_present(
                    summary,
                    "overall_target_pass_rate",
                    "overall_expected_pass_rate",
                ),
                "mrr": first_present(summary, "overall_target_mrr", "overall_expected_mrr"),
                "has_dashboard": dashboard_index.exists(),
            }
        )

    rows.sort(key=lambda row: row.get("timestamp", ""), reverse=True)
    return rows


def render_runs_index_rows(rows: list[dict[str, Any]], index_dir: Path) -> str:
    html_rows: list[str] = []
    for row in rows:
        rel_run = os.path.relpath(row["run_dir"].resolve(), index_dir.resolve()).replace("\\", "/")
        dashboard_href = f"{rel_run}/dashboard/index.html"
        ts = row.get("timestamp", "")
        date_display = ts[:10] if len(ts) >= 10 else ts or "-"
        if row["has_dashboard"]:
            dashboard_cell = f'<a href="{escape(dashboard_href)}">Open dashboard</a>'
        else:
            dashboard_cell = (
                f'<span class="inline-note" title="py tools/test-suite/render_analysis_dashboard.py '
                f'--analysis-run &quot;{escape(rel_run)}&quot;">Not generated</span>'
            )
        pass_val = row["target_pass_rate"]
        mrr_val = row["mrr"]
        html_rows.append(
            "<tr"
            f' data-run_id="{escape(row["run_id"])}"'
            f' data-timestamp="{escape(ts)}"'
            f' data-target_pass_rate="{pass_val if pass_val is not None else ""}"'
            f' data-mrr="{mrr_val if mrr_val is not None else ""}"'
            f' data-total_queries="{row.get("total_queries") or ""}"'
            ">"
            f"<td>{escape(row['run_id'])}</td>"
            f"<td>{escape(date_display)}</td>"
            f"<td>{percent_text(pass_val)}</td>"
            f"<td>{decimal_text(mrr_val)}</td>"
            f"<td>{int_text(row.get('total_queries'))}</td>"
            f"<td>{dashboard_cell}</td>"
            "</tr>"
        )
    return "\n".join(html_rows)


def scan_comparisons_for_index(comparisons_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not comparisons_root.is_dir():
        return rows

    for run_dir in comparisons_root.iterdir():
        if not run_dir.is_dir():
            continue
        comparison_summary_path = run_dir / "comparison_summary.json"
        multi_path = run_dir / "multi_comparison.json"
        dashboard_index = run_dir / "dashboard" / "index.html"

        if comparison_summary_path.exists():
            summary = read_json(comparison_summary_path)
            baseline_dir = summary.get("baseline_run_dir", "")
            candidate_dir = summary.get("candidate_run_dir", "")
            rows.append(
                {
                    "run_id": run_dir.name,
                    "run_dir": run_dir,
                    "kind": "pairwise",
                    "kind_label": "Pairwise",
                    "timestamp": summary.get("timestamp", ""),
                    "baseline_label": Path(baseline_dir).name if baseline_dir else "-",
                    "candidate_label": Path(candidate_dir).name if candidate_dir else "-",
                    "baseline_run_dir": baseline_dir,
                    "candidate_run_dir": candidate_dir,
                    "delta_target_pass": first_present(
                        summary,
                        "delta_overall_target_pass_rate",
                        "delta_overall_expected_pass_rate",
                    ),
                    "has_dashboard": dashboard_index.exists(),
                    "render_hint": f'--comparison-run "{relative_display(run_dir)}"',
                }
            )
        elif multi_path.exists():
            payload = read_json(multi_path)
            mode = payload.get("mode", "chain")
            runs = payload.get("runs", [])
            baseline_label = Path(runs[0]["run_dir"]).name if runs else "-"
            candidate_label = (
                f"{payload.get('n_comparisons', 0)} comparison(s)"
                if payload.get("n_comparisons")
                else (Path(runs[-1]["run_dir"]).name if len(runs) > 1 else "-")
            )
            rows.append(
                {
                    "run_id": run_dir.name,
                    "run_dir": run_dir,
                    "kind": f"multi-{mode}",
                    "kind_label": f"Multi ({mode})",
                    "timestamp": payload.get("timestamp", ""),
                    "baseline_label": baseline_label,
                    "candidate_label": candidate_label,
                    "delta_target_pass": None,
                    "has_dashboard": dashboard_index.exists(),
                    "render_hint": f'--multi-comparison-run "{relative_display(run_dir)}"',
                }
            )

    rows.sort(key=lambda row: row.get("timestamp", ""), reverse=True)
    return rows


def signed_pp_text(value: float | None) -> str:
    if value is None:
        return "-"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 100:.2f}pp"


def render_comparisons_index_rows(rows: list[dict[str, Any]], index_dir: Path) -> str:
    html_rows: list[str] = []
    for row in rows:
        rel_run = os.path.relpath(row["run_dir"].resolve(), index_dir.resolve()).replace("\\", "/")
        dashboard_href = f"{rel_run}/dashboard/index.html"
        ts = row.get("timestamp", "")
        date_display = ts[:10] if len(ts) >= 10 else ts or "-"
        if row["has_dashboard"]:
            dashboard_cell = f'<a href="{escape(dashboard_href)}">Open dashboard</a>'
        else:
            dashboard_cell = (
                f'<span class="inline-note" title="py tools/test-suite/render_analysis_dashboard.py '
                f'{escape(row["render_hint"])}">Not generated</span>'
            )
        delta_val = row.get("delta_target_pass")
        html_rows.append(
            "<tr"
            f' data-run_id="{escape(row["run_id"])}"'
            f' data-timestamp="{escape(ts)}"'
            f' data-kind="{escape(row["kind"])}"'
            f' data-delta_target_pass="{delta_val if delta_val is not None else ""}"'
            ">"
            f"<td>{escape(row['run_id'])}</td>"
            f"<td>{escape(date_display)}</td>"
            f"<td>{escape(row['kind_label'])}</td>"
            f"<td>{render_analysis_run_link(index_dir, row.get('baseline_run_dir', ''), row['baseline_label'])}</td>"
            f"<td>{render_analysis_run_link(index_dir, row.get('candidate_run_dir', ''), row['candidate_label'])}</td>"
            f"<td>{signed_pp_text(delta_val)}</td>"
            f"<td>{dashboard_cell}</td>"
            "</tr>"
        )
    return "\n".join(html_rows)


def rebuild_all_analysis_dashboards(analysis_root: Path | None = None) -> list[Path]:
    """Re-render every single-run analysis dashboard (adds nav back buttons)."""
    root = workspace_root()
    analysis_root = analysis_root or (root / "results" / "analysis-system")
    empty_args = argparse.Namespace(
        related_timeline=None,
        related_analysis=None,
        related_comparison=None,
    )
    written: list[Path] = []
    for row in scan_analysis_runs_for_index(analysis_root):
        run_dir = row["run_dir"]
        try:
            context = DashboardContext(
                mode="analysis",
                run_dir=run_dir,
                output_dir=run_dir / "dashboard",
            )
            view_model = build_analysis_view_model(run_dir)
            write_dashboard(
                context,
                view_model,
                related_links=collect_related_links(context, view_model, empty_args),
            )
            written.append(run_dir / "dashboard" / "index.html")
        except Exception as error:
            print(f"Skipped {run_dir.name}: {error}")
    return written


def rebuild_all_comparison_dashboards(comparisons_root: Path | None = None) -> list[Path]:
    """Re-render every comparison dashboard under comparisons_root (adds nav back buttons)."""
    comparisons_root = comparisons_root or default_comparisons_root()
    empty_args = argparse.Namespace(
        related_timeline=None,
        related_analysis=None,
        related_comparison=None,
    )
    written: list[Path] = []
    for row in scan_comparisons_for_index(comparisons_root):
        run_dir = row["run_dir"]
        try:
            if (run_dir / "comparison_summary.json").exists():
                context = DashboardContext(
                    mode="comparison",
                    run_dir=run_dir,
                    output_dir=run_dir / "dashboard",
                )
                view_model = build_comparison_view_model(run_dir)
                write_dashboard(
                    context,
                    view_model,
                    related_links=collect_related_links(context, view_model, empty_args),
                )
            elif (run_dir / "multi_comparison.json").exists():
                context = DashboardContext(
                    mode="multi_comparison",
                    run_dir=run_dir,
                    output_dir=run_dir / "dashboard",
                )
                write_multi_comparison_dashboard(
                    run_dir,
                    related_links=collect_related_links(context, None, empty_args),
                )
            else:
                continue
            written.append(run_dir / "dashboard" / "index.html")
        except Exception as error:
            print(f"Skipped {run_dir.name}: {error}")
    return written


def write_comparisons_index(
    comparisons_root: Path | None = None,
    *,
    output_path: Path | None = None,
) -> Path:
    root = workspace_root()
    comparisons_root = comparisons_root or default_comparisons_root()
    output_path = output_path or (comparisons_root / "index.html")
    rows = scan_comparisons_for_index(comparisons_root)

    template = load_asset("comparisons_index.html")
    index_note = (
        f"{len(rows)} processed comparison run(s). "
        "Pairwise runs use <code>comparison_summary.json</code>; multi-comparison runs use "
        "<code>multi_comparison.json</code>."
    )
    footer_note = (
        'Generate a missing dashboard: '
        '<code>py tools/test-suite/render_analysis_dashboard.py --comparison-run '
        '"results/analysis-system-comparisons/&lt;run-folder&gt;"</code> or '
        '<code>--multi-comparison-run "results/analysis-system-comparisons/&lt;run-folder&gt;"</code>'
    )
    nav_bar_html = render_dashboard_nav_html(
        output_path.parent,
        hub_links=collect_comparisons_index_hub_links(),
    )
    html_output = (
        template.replace("__PAGE_TITLE__", "Comparison Runs Index")
        .replace("__DASHBOARD_TITLE__", "Comparison Runs")
        .replace("__DASHBOARD_SUBTITLE__", relative_display(comparisons_root))
        .replace("__DASHBOARD_NAV__", nav_bar_html)
        .replace("__DASHBOARD_HELP__", render_dashboard_help_panel("hub_comparisons", open_by_default=True))
        .replace("__INDEX_NOTE__", index_note)
        .replace("__ROWS__", render_comparisons_index_rows(rows, output_path.parent))
        .replace("__FOOTER_NOTE__", footer_note)
    )
    write_text(output_path, html_output)
    write_text(output_path.parent / "dashboard.css", load_asset("dashboard.css"))
    return output_path


def write_runs_index(
    analysis_root: Path | None = None,
    *,
    output_path: Path | None = None,
) -> Path:
    root = workspace_root()
    analysis_root = analysis_root or (root / "results" / "analysis-system")
    output_path = output_path or (analysis_root / "index.html")
    rows = scan_analysis_runs_for_index(analysis_root)

    template = load_asset("runs_index.html")
    index_note = (
        f"{len(rows)} processed analysis run(s). "
        "Rows without a dashboard link can be rendered with "
        "<code>py tools/test-suite/render_analysis_dashboard.py --analysis-run &lt;run-folder&gt;</code>."
    )
    nav_bar_html = render_dashboard_nav_html(
        output_path.parent,
        hub_links=collect_runs_index_hub_links(),
    )
    html_output = (
        template.replace("__PAGE_TITLE__", "Analysis Runs Index")
        .replace("__DASHBOARD_TITLE__", "Analysis Runs")
        .replace("__DASHBOARD_SUBTITLE__", relative_display(analysis_root))
        .replace("__DASHBOARD_NAV__", nav_bar_html)
        .replace("__DASHBOARD_HELP__", render_dashboard_help_panel("hub_analysis", open_by_default=True))
        .replace("__INDEX_NOTE__", index_note)
        .replace("__ROWS__", render_runs_index_rows(rows, output_path.parent))
    )
    write_text(output_path, html_output)
    write_text(output_path.parent / "dashboard.css", load_asset("dashboard.css"))
    refresh_timeline_index(analysis_root)
    return output_path


def resolve_context(args: argparse.Namespace) -> DashboardContext:
    mode_count = sum(
        1
        for value in (
            args.analysis_run,
            args.comparison_run,
            args.timeline_runs,
            args.multi_comparison_run,
        )
        if value
    )
    if mode_count != 1:
        raise ValueError(
            "Provide exactly one of --analysis-run, --comparison-run, "
            "--timeline-runs, or --multi-comparison-run."
        )

    if args.timeline_runs:
        if len(args.timeline_runs) < 2:
            raise ValueError("--timeline-runs requires at least 2 run directories.")
        output_dir = Path(args.output_dir) if args.output_dir else (workspace_root() / "results" / "analysis-system" / "timeline-dashboard")
        return DashboardContext(mode="timeline", run_dir=Path(args.timeline_runs[0]), output_dir=output_dir)

    if args.analysis_run:
        run_dir = Path(args.analysis_run)
        output_dir = Path(args.output_dir) if args.output_dir else run_dir / "dashboard"
        return DashboardContext(mode="analysis", run_dir=run_dir, output_dir=output_dir)

    run_dir = Path(args.comparison_run)
    output_dir = Path(args.output_dir) if args.output_dir else run_dir / "dashboard"
    return DashboardContext(mode="comparison", run_dir=run_dir, output_dir=output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a static dashboard from analysis-system outputs.")
    parser.add_argument("--analysis-run", help="Path to a processed analysis run directory.")
    parser.add_argument("--comparison-run", help="Path to a processed comparison run directory.")
    parser.add_argument(
        "--timeline-runs",
        nargs="+",
        help="Paths to 2 or more analysis run directories. Renders a timeline dashboard showing metrics across runs.",
    )
    parser.add_argument("--output-dir", help="Optional explicit output directory for the dashboard.")
    parser.add_argument(
        "--report",
        choices=["markdown"],
        help="Also write an executive summary report (dashboard/summary.md or timeline-dashboard/summary.md).",
    )
    parser.add_argument(
        "--related-timeline",
        help="Path to a timeline dashboard directory or HTML file for cross-linking.",
    )
    parser.add_argument(
        "--related-analysis",
        help="Path to an analysis run dashboard directory for cross-linking.",
    )
    parser.add_argument(
        "--related-comparison",
        help="Path to a comparison dashboard directory for cross-linking.",
    )
    parser.add_argument(
        "--multi-comparison-run",
        help="Path to a compare-chain or compare-all directory containing multi_comparison.json.",
    )
    parser.add_argument(
        "--build-index",
        action="store_true",
        help="Build analysis and comparison run indexes (results/analysis-system/index.html and results/analysis-system-comparisons/index.html).",
    )
    parser.add_argument(
        "--build-comparisons-index",
        action="store_true",
        help="Build only results/analysis-system-comparisons/index.html.",
    )
    parser.add_argument(
        "--rebuild-all-analysis-dashboards",
        action="store_true",
        help="Re-render dashboard/index.html for every analysis run (Latest Analysis Run dashboards).",
    )
    parser.add_argument(
        "--rebuild-all-comparison-dashboards",
        action="store_true",
        help="Re-render dashboard/index.html for every comparison run (pairwise and multi).",
    )
    parser.add_argument(
        "--index-root",
        help="Root directory to scan for --build-index (default: results/analysis-system).",
    )
    parser.add_argument(
        "--index-output",
        help="Output path for analysis runs index (default: <index-root>/index.html).",
    )
    parser.add_argument(
        "--comparisons-index-root",
        help="Root directory to scan for comparisons index (default: results/analysis-system-comparisons).",
    )
    parser.add_argument(
        "--comparisons-index-output",
        help="Output path for comparisons index (default: <comparisons-index-root>/index.html).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.rebuild_all_analysis_dashboards:
        index_root = Path(args.index_root) if args.index_root else workspace_root() / "results" / "analysis-system"
        written = rebuild_all_analysis_dashboards(index_root)
        for path in written:
            print(f"Dashboard written to: {relative_display(path)}")
        print(f"Rebuilt {len(written)} analysis dashboard(s).")
        return

    if args.rebuild_all_comparison_dashboards:
        comparisons_root = (
            Path(args.comparisons_index_root)
            if args.comparisons_index_root
            else default_comparisons_root()
        )
        written = rebuild_all_comparison_dashboards(comparisons_root)
        for path in written:
            print(f"Dashboard written to: {relative_display(path)}")
        print(f"Rebuilt {len(written)} comparison dashboard(s).")
        return

    if args.build_index or args.build_comparisons_index:
        comparisons_root = (
            Path(args.comparisons_index_root)
            if args.comparisons_index_root
            else default_comparisons_root()
        )
        comparisons_output = (
            Path(args.comparisons_index_output)
            if args.comparisons_index_output
            else comparisons_root / "index.html"
        )
        if args.build_index or args.build_comparisons_index:
            comp_output = write_comparisons_index(comparisons_root, output_path=comparisons_output)
            print(f"Comparisons index written to: {relative_display(comp_output)}")
        if args.build_index:
            index_root = Path(args.index_root) if args.index_root else workspace_root() / "results" / "analysis-system"
            index_output = Path(args.index_output) if args.index_output else index_root / "index.html"
            output = write_runs_index(index_root, output_path=index_output)
            print(f"Analysis runs index written to: {relative_display(output)}")
        else:
            index_root = Path(args.index_root) if args.index_root else workspace_root() / "results" / "analysis-system"
            timeline_index = refresh_timeline_index(index_root)
            if timeline_index:
                print(f"Timeline index written to: {relative_display(timeline_index)}")
        return

    if args.multi_comparison_run:
        run_dir = Path(args.multi_comparison_run)
        write_multi_comparison_dashboard(
            run_dir,
            report_format=args.report,
            related_links=collect_related_links(
                DashboardContext(mode="multi_comparison", run_dir=run_dir, output_dir=run_dir / "dashboard"),
                None,
                args,
            ),
        )
        print(f"Dashboard written to: {relative_display(run_dir / 'dashboard' / 'index.html')}")
        if args.report == "markdown":
            print(f"Summary written to: {relative_display(run_dir / 'dashboard' / 'summary.md')}")
        return

    context = resolve_context(args)
    if context.mode == "timeline":
        filename = write_timeline_dashboard(
            [Path(p) for p in args.timeline_runs],
            context.output_dir,
            report_format=args.report,
            related_links=collect_related_links(context, None, args),
        )
        print(f"Dashboard written to: {relative_display(context.output_dir / filename)}")
        if args.report == "markdown":
            print(f"Summary written to: {relative_display(context.output_dir / 'summary.md')}")
        return
    if context.mode == "analysis":
        view_model = build_analysis_view_model(context.run_dir)
    else:
        view_model = build_comparison_view_model(context.run_dir)
    write_dashboard(
        context,
        view_model,
        report_format=args.report,
        related_links=collect_related_links(context, view_model, args),
    )
    print(f"Dashboard written to: {relative_display(context.output_dir / 'index.html')}")
    if args.report == "markdown":
        print(f"Summary written to: {relative_display(context.output_dir / 'summary.md')}")


if __name__ == "__main__":
    main()
