#!/usr/bin/env python3
"""Re-run analysis and comparisons in place using pinned source runs, then rebuild dashboards."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from analysis_system import (  # noqa: E402
    ARTIFACT_FILENAMES,
    analyze_source,
    build_aggregates_by_locale,
    build_aggregates_by_path_locale,
    build_aggregates_by_persona,
    build_aggregates_by_persona_locale,
    build_aggregates_by_style,
    build_aggregates_by_style_locale,
    build_failure_list,
    build_issue_outputs,
    build_run_summary,
    build_source_configs,
    compute_pairwise_comparison,
    inspect_run,
    load_analysis_dir,
    load_issue_catalog,
    load_query_definitions,
    load_selected_runs,
    query_lookup_map,
    read_json,
    utc_now,
    workspace_root,
    write_json,
)


def source_overrides_from_summary(
    summary: dict[str, object],
    root: Path,
    *,
    substitute_from: dict[str, object] | None = None,
) -> tuple[dict[str, Path], list[str]]:
    overrides: dict[str, Path] = {}
    substituted: list[str] = []
    for source_key, info in summary.get("selected_runs", {}).items():
        run_dir = root / str(info["run_dir"]).replace("\\", "/")
        if run_dir.exists():
            overrides[source_key] = run_dir
            continue
        if substitute_from and source_key in substitute_from:
            fallback_dir = root / str(substitute_from[source_key]["run_dir"]).replace("\\", "/")
            if fallback_dir.exists():
                overrides[source_key] = fallback_dir
                substituted.append(source_key)
                continue
        raise FileNotFoundError(f"Missing source run: {source_key} ({info['run_dir']})")
    return overrides, substituted


def reprocess_analysis_run(
    run_dir: Path,
    *,
    dry_run: bool = False,
    substitute_sources_from: Path | None = None,
) -> None:
    root = workspace_root()
    summary_path = run_dir / ARTIFACT_FILENAMES["run_summary"]
    if not summary_path.exists():
        raise FileNotFoundError(f"No run_summary.json in {run_dir}")

    summary = read_json(summary_path)
    substitute_summary = None
    if substitute_sources_from is not None:
        substitute_path = substitute_sources_from / ARTIFACT_FILENAMES["run_summary"]
        if not substitute_path.exists():
            raise FileNotFoundError(f"No run_summary.json in substitute run: {substitute_sources_from}")
        substitute_summary = read_json(substitute_path).get("selected_runs", {})
    overrides, substituted_sources = source_overrides_from_summary(
        summary,
        root,
        substitute_from=substitute_summary,
    )

    issue_catalog = load_issue_catalog(root / "docs" / "test-suite" / "issues")
    source_configs = build_source_configs(root)
    query_records_by_file = {
        config.query_file: load_query_definitions(config.query_file)
        for config in source_configs
        if config.query_file is not None
    }
    external_search_lookup = query_lookup_map(
        query_records_by_file[root / "data" / "test-suite" / "external-search" / "all_queries.json"]
    )

    selected_runs = load_selected_runs(source_configs, query_records_by_file, overrides)

    all_evaluations = []
    for config in source_configs:
        all_evaluations.extend(
            analyze_source(config, selected_runs[config.key], issue_catalog, external_search_lookup)
        )

    issues_processed = build_issue_outputs(issue_catalog, all_evaluations, source_configs)
    aggregates_by_path_locale = build_aggregates_by_path_locale(all_evaluations)
    aggregates_by_locale = build_aggregates_by_locale(all_evaluations)
    aggregates_by_style = build_aggregates_by_style(all_evaluations)
    aggregates_by_persona = build_aggregates_by_persona(all_evaluations, issue_catalog)
    aggregates_by_style_locale = build_aggregates_by_style_locale(all_evaluations)
    aggregates_by_persona_locale = build_aggregates_by_persona_locale(all_evaluations, issue_catalog)
    failure_list = build_failure_list(all_evaluations)
    run_summary = build_run_summary(
        analysis_id=str(summary.get("analysis_id", run_dir.name)),
        run_dir=run_dir,
        selected_runs=selected_runs,
        evaluations=all_evaluations,
        issues=issue_catalog,
        aggregates_by_path_locale=aggregates_by_path_locale,
    )
    run_summary["run_id"] = run_dir.name
    run_summary["reprocessed_at"] = utc_now().isoformat()
    run_summary["url_matcher_version"] = "help-center-query-locale-v2"
    if substituted_sources:
        run_summary["substituted_source_runs"] = substituted_sources
        run_summary["substituted_source_runs_from"] = substitute_sources_from.name if substitute_sources_from else None

    if dry_run:
        suffix = f" (substitute {len(substituted_sources)} sources)" if substituted_sources else ""
        print(f"[dry-run] Would reprocess: {run_dir.name}{suffix}")
        return

    write_json(run_dir / ARTIFACT_FILENAMES["issues_processed"], issues_processed)
    write_json(run_dir / ARTIFACT_FILENAMES["aggregates_by_path_locale"], aggregates_by_path_locale)
    write_json(run_dir / ARTIFACT_FILENAMES["aggregates_by_locale"], aggregates_by_locale)
    write_json(run_dir / ARTIFACT_FILENAMES["aggregates_by_style"], aggregates_by_style)
    write_json(run_dir / ARTIFACT_FILENAMES["aggregates_by_persona"], aggregates_by_persona)
    write_json(run_dir / ARTIFACT_FILENAMES["aggregates_by_style_locale"], aggregates_by_style_locale)
    write_json(run_dir / ARTIFACT_FILENAMES["aggregates_by_persona_locale"], aggregates_by_persona_locale)
    write_json(run_dir / ARTIFACT_FILENAMES["failure_list"], failure_list)
    write_json(run_dir / ARTIFACT_FILENAMES["run_summary"], run_summary)
    suffix = f" (substituted {len(substituted_sources)} missing sources)" if substituted_sources else ""
    print(f"Reprocessed analysis: {run_dir.name}{suffix}")


def reprocess_comparison_run(comparison_dir: Path, *, dry_run: bool = False) -> None:
    root = workspace_root()
    multi_path = comparison_dir / "multi_comparison.json"
    summary_path = comparison_dir / ARTIFACT_FILENAMES["comparison_summary"]

    if multi_path.exists():
        payload = read_json(multi_path)
        comparisons = payload.get("comparisons", [])
        if dry_run:
            print(f"[dry-run] Would reprocess multi-comparison: {comparison_dir.name} ({len(comparisons)} pairs)")
            return
        updated_pairs = []
        for pair in comparisons:
            pair_summary = pair.get("summary", pair)
            baseline_dir = root / str(pair_summary["baseline_run_dir"]).replace("\\", "/")
            candidate_dir = root / str(pair_summary["candidate_run_dir"]).replace("\\", "/")
            baseline_data = load_analysis_dir(baseline_dir)
            candidate_data = load_analysis_dir(candidate_dir)
            updated_pairs.append(
                compute_pairwise_comparison(baseline_data, candidate_data, baseline_dir, candidate_dir)
            )
        payload["comparisons"] = updated_pairs
        payload["reprocessed_at"] = utc_now().isoformat()
        payload["url_matcher_version"] = "help-center-query-locale-v2"
        write_json(multi_path, payload)
        print(f"Reprocessed multi-comparison: {comparison_dir.name}")
        return

    if not summary_path.exists():
        raise FileNotFoundError(f"No comparison artifacts in {comparison_dir}")

    summary = read_json(summary_path)
    baseline_dir = root / str(summary["baseline_run_dir"]).replace("\\", "/")
    candidate_dir = root / str(summary["candidate_run_dir"]).replace("\\", "/")
    if dry_run:
        print(f"[dry-run] Would reprocess comparison: {comparison_dir.name}")
        return

    comparison = compute_pairwise_comparison(
        load_analysis_dir(baseline_dir),
        load_analysis_dir(candidate_dir),
        baseline_dir,
        candidate_dir,
    )
    write_json(comparison_dir / ARTIFACT_FILENAMES["comparison_summary"], comparison["summary"])
    write_json(comparison_dir / ARTIFACT_FILENAMES["comparison_by_path_locale"], comparison["by_path_locale"])
    write_json(comparison_dir / ARTIFACT_FILENAMES["comparison_by_locale"], comparison["by_locale"])
    write_json(comparison_dir / ARTIFACT_FILENAMES["comparison_by_style"], comparison["by_style"])
    write_json(comparison_dir / ARTIFACT_FILENAMES["comparison_by_persona"], comparison["by_persona"])
    write_json(comparison_dir / ARTIFACT_FILENAMES["comparison_by_style_locale"], comparison["by_style_locale"])
    write_json(comparison_dir / ARTIFACT_FILENAMES["comparison_by_persona_locale"], comparison["by_persona_locale"])
    write_json(comparison_dir / ARTIFACT_FILENAMES["comparison_by_issue"], comparison["by_issue"])
    write_json(comparison_dir / ARTIFACT_FILENAMES["failure_delta"], comparison["failure_delta"])
    marker = comparison_dir / "reprocessed.json"
    write_json(
        marker,
        {
            "reprocessed_at": utc_now().isoformat(),
            "url_matcher_version": "help-center-query-locale-v2",
        },
    )
    print(f"Reprocessed comparison: {comparison_dir.name}")


def rebuild_dashboards(*, with_reports: bool) -> None:
    script = Path(__file__).resolve().parent / "render_analysis_dashboard.py"
    commands = [
        [sys.executable, str(script), "--rebuild-all-analysis-dashboards"],
        [sys.executable, str(script), "--rebuild-all-comparison-dashboards"],
        [sys.executable, str(script), "--build-index"],
    ]
    for cmd in commands:
        print("Running:", " ".join(cmd))
        result = subprocess.run(cmd, cwd=workspace_root())
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {' '.join(cmd)}")

    if with_reports:
        analysis_root = workspace_root() / "results" / "analysis-system"
        for run_dir in sorted(analysis_root.iterdir()):
            if not run_dir.is_dir() or not run_dir.name.startswith("analysis-system "):
                continue
            if not (run_dir / ARTIFACT_FILENAMES["run_summary"]).exists():
                continue
            cmd = [
                sys.executable,
                str(script),
                "--analysis-run",
                str(run_dir),
                "--report",
                "markdown",
            ]
            subprocess.run(cmd, cwd=workspace_root(), check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Only print what would run.")
    parser.add_argument("--skip-dashboards", action="store_true", help="Skip dashboard/index rebuild.")
    parser.add_argument("--with-reports", action="store_true", help="Regenerate markdown dashboard reports.")
    parser.add_argument(
        "--only-analysis",
        nargs="*",
        help="Optional analysis run directory names to reprocess (default: all).",
    )
    parser.add_argument(
        "--substitute-missing-sources-from",
        help="Analysis run directory name whose selected_runs fill gaps (e.g. when Apr 29 raw runs are missing).",
    )
    args = parser.parse_args()

    root = workspace_root()
    analysis_root = root / "results" / "analysis-system"
    comparisons_root = root / "results" / "analysis-system-comparisons"

    analysis_dirs = [
        path
        for path in sorted(analysis_root.iterdir())
        if path.is_dir() and path.name.startswith("analysis-system ")
    ]
    if args.only_analysis:
        wanted = set(args.only_analysis)
        analysis_dirs = [path for path in analysis_dirs if path.name in wanted]

    substitute_dir = None
    if args.substitute_missing_sources_from:
        substitute_dir = analysis_root / args.substitute_missing_sources_from
        if not substitute_dir.is_dir():
            raise FileNotFoundError(f"Substitute analysis run not found: {substitute_dir}")

    failed_analysis: list[str] = []
    for run_dir in analysis_dirs:
        try:
            use_substitute = substitute_dir if run_dir.name == "analysis-system 2026-04-30 15-00" else None
            reprocess_analysis_run(
                run_dir,
                dry_run=args.dry_run,
                substitute_sources_from=use_substitute,
            )
        except Exception as error:
            failed_analysis.append(f"{run_dir.name}: {error}")
            print(f"SKIP analysis {run_dir.name}: {error}", file=sys.stderr)

    failed_comparisons: list[str] = []
    if comparisons_root.exists():
        comparison_dirs = [path for path in sorted(comparisons_root.iterdir()) if path.is_dir()]
        for comparison_dir in comparison_dirs:
            if comparison_dir.name == "timeline-dashboard":
                continue
            try:
                if (comparison_dir / ARTIFACT_FILENAMES["comparison_summary"]).exists() or (
                    comparison_dir / "multi_comparison.json"
                ).exists():
                    reprocess_comparison_run(comparison_dir, dry_run=args.dry_run)
            except Exception as error:
                failed_comparisons.append(f"{comparison_dir.name}: {error}")
                print(f"SKIP comparison {comparison_dir.name}: {error}", file=sys.stderr)

    if not args.dry_run and not args.skip_dashboards:
        rebuild_dashboards(with_reports=args.with_reports)

    print("")
    print(f"Analysis reprocessed: {len(analysis_dirs) - len(failed_analysis)}/{len(analysis_dirs)}")
    if failed_analysis:
        print("Analysis failures:")
        for item in failed_analysis:
            print(f"  - {item}")
    if comparisons_root.exists():
        print(f"Comparison failures: {len(failed_comparisons)}")
        for item in failed_comparisons:
            print(f"  - {item}")

    return 1 if failed_analysis else 0


if __name__ == "__main__":
    raise SystemExit(main())
