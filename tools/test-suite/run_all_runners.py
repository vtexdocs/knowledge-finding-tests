#!/usr/bin/env python3
"""
Parent runner for the Phase 1 test suite.

Runs the test-suite scripts in the recommended order:
1. extract_queries_by_path.py
2. run-algolia-path.py (DEPRECATED — off by default; Hybrid Search supersedes it)
3. run-hybrid-search-path.py
4. run-docs-assistant-path.js
5. run_google_search_playwright.py
6. llm_runner.py (one or more providers)
7. analysis_system.py (optional, with interactive confirmation)

This wrapper is intentionally orchestration-only: it does not replace the child
scripts' own validation. If credentials, auth state, or dependencies are missing,
the corresponding child command will fail with its original error.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent

PATH_CHOICES = {
    "extract",
    "algolia",
    "hybrid",
    "docs-assistant",
    "external-search",
    "external-llms",
    "analysis",
}

# Deprecated paths stay valid for opt-in via --include but are excluded from the
# default run set. Algolia is superseded by Hybrid Search as the internal-search path.
DEPRECATED_PATHS = {"algolia"}

# Paths executed when neither --include nor --skip narrows the selection.
DEFAULT_PATHS = PATH_CHOICES - DEPRECATED_PATHS

DEPRECATION_NOTICES = {
    "algolia": "[deprecated] Algolia path is deprecated; Hybrid Search supersedes it.",
}

LLM_PROVIDER_CHOICES = {"chatgpt", "gemini"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run all Phase 1 data-collection runners in sequence."
    )
    parser.add_argument(
        "--include",
        nargs="+",
        choices=sorted(PATH_CHOICES),
        default=None,
        help=(
            "Only run the selected paths. Default: run all non-deprecated paths "
            "(Algolia is deprecated and off by default; pass --include algolia to run it)."
        ),
    )
    parser.add_argument(
        "--skip",
        nargs="+",
        choices=sorted(PATH_CHOICES),
        default=[],
        help="Skip one or more paths.",
    )
    parser.add_argument(
        "--issues",
        nargs="+",
        default=None,
        help="Filter to specific issue IDs where supported.",
    )
    parser.add_argument(
        "--locale",
        default="all",
        help="Locale passed to supported runners. Default: all.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Top N results passed to supported runners. Default: 10.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=None,
        help="Shared delay override passed to supported runners. Units depend on the child script.",
    )
    parser.add_argument(
        "--llm-providers",
        nargs="+",
        choices=sorted(LLM_PROVIDER_CHOICES),
        default=["chatgpt", "gemini"],
        help="External LLM providers to run when external-llms is enabled. Default: chatgpt gemini.",
    )
    parser.add_argument(
        "--llm-limit",
        type=int,
        default=None,
        help="Limit passed only to llm_runner.py.",
    )
    parser.add_argument(
        "--llm-headless",
        action="store_true",
        help="Pass --headless to llm_runner.py.",
    )
    parser.add_argument(
        "--external-search-no-headless",
        action="store_true",
        help="Pass --no-headless to the Google Search Playwright runner.",
    )
    parser.add_argument(
        "--external-search-wait-for-captcha",
        action="store_true",
        help="Pass --wait-for-captcha to the Google Search Playwright runner.",
    )
    parser.add_argument(
        "--external-search-debug-save-html",
        action="store_true",
        help="Pass --debug-save-html to the Google Search Playwright runner.",
    )
    parser.add_argument(
        "--run-id-prefix",
        default=None,
        help="Prefix used when generating child run IDs for supported runners.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the commands without executing them.",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Keep running later steps even if one step fails.",
    )
    parser.add_argument(
        "--analysis-id",
        default=None,
        help="Explicit analysis ID passed to analysis_system.py. Default: auto-generated.",
    )
    parser.add_argument(
        "--no-confirm-analysis",
        action="store_true",
        help="Skip the interactive confirmation prompt before running the analysis step.",
    )
    parser.add_argument(
        "--render-dashboard",
        action="store_true",
        help="Render the analysis dashboard after a successful analysis step.",
    )
    parser.add_argument(
        "--no-render-dashboard",
        action="store_true",
        help="Skip dashboard rendering and the interactive dashboard prompt.",
    )
    parser.add_argument(
        "--render-dashboard-report",
        action="store_true",
        help="Also write dashboard/summary.md when rendering the dashboard.",
    )
    return parser.parse_args()


def should_run(step: str, include: set[str], skip: set[str]) -> bool:
    return step in include and step not in skip


def make_run_id(prefix: str | None, suffix: str) -> str | None:
    if not prefix:
        return None
    return f"{prefix}-{suffix}"


def format_command(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


def run_step(name: str, cmd: list[str], dry_run: bool) -> int:
    print(f"\n[{name}]")
    print(format_command(cmd))
    if dry_run:
        return 0
    completed = subprocess.run(cmd, cwd=WORKSPACE_ROOT)
    return completed.returncode


def main() -> int:
    args = parse_args()

    include = set(args.include) if args.include else set(DEFAULT_PATHS)
    skip = set(args.skip)

    for path, notice in DEPRECATION_NOTICES.items():
        if should_run(path, include, skip):
            print(notice)

    steps: list[tuple[str, list[str]]] = []

    if should_run("extract", include, skip):
        cmd = [sys.executable, str(SCRIPT_DIR / "extract_queries_by_path.py")]
        steps.append(("extract", cmd))

    if should_run("algolia", include, skip):
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "internal-search" / "run-algolia-path.py"),
            "--path",
            "both",
            "--locale",
            args.locale,
            "--top-n",
            str(args.top_n),
        ]
        if args.issues:
            cmd.extend(["--issues", *args.issues])
        if args.delay is not None:
            cmd.extend(["--delay", str(args.delay)])
        run_id = make_run_id(args.run_id_prefix, "algolia")
        if run_id:
            cmd.extend(["--run-id", run_id])
        steps.append(("algolia", cmd))

    if should_run("hybrid", include, skip):
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "internal-search" / "run-hybrid-search-path.py"),
            "--locale",
            args.locale,
            "--top-n",
            str(args.top_n),
            "--generate-api-call-results",
        ]
        if args.issues:
            cmd.extend(["--issues", *args.issues])
        if args.delay is not None:
            cmd.extend(["--delay", str(args.delay)])
        run_id = make_run_id(args.run_id_prefix, "hybrid")
        if run_id:
            cmd.extend(["--run-id", run_id])
        steps.append(("hybrid", cmd))

    if should_run("docs-assistant", include, skip):
        cmd = [
            "node",
            str(SCRIPT_DIR / "docs-assistant" / "run-docs-assistant-path.js"),
            "--top-n",
            str(args.top_n),
        ]
        if args.issues:
            cmd.extend(["--issues", ",".join(args.issues)])
        if args.delay is not None:
            cmd.extend(["--delay", str(int(args.delay))])
        run_id = make_run_id(args.run_id_prefix, "docs-assistant")
        if run_id:
            cmd.extend(["--run-id", run_id])
        steps.append(("docs-assistant", cmd))

    if should_run("external-search", include, skip):
        cmd = [
            sys.executable,
            str(
                SCRIPT_DIR
                / "external-search"
                / "google-search-playwright"
                / "run_google_search_playwright.py"
            ),
            "run",
        ]
        if args.issues and len(args.issues) == 1:
            cmd.extend(["--issue", args.issues[0]])
        if args.locale != "all":
            cmd.extend(["--locale", args.locale])
        if args.delay is not None:
            cmd.extend(["--delay", str(args.delay)])
        if args.external_search_no_headless:
            cmd.append("--no-headless")
        if args.external_search_wait_for_captcha:
            cmd.append("--wait-for-captcha")
        if args.external_search_debug_save_html:
            cmd.append("--debug-save-html")
        steps.append(("external-search", cmd))

    if should_run("external-llms", include, skip):
        for provider in args.llm_providers:
            cmd = [
                sys.executable,
                str(SCRIPT_DIR / "external-llms" / "llm_runner.py"),
                "run",
                "--provider",
                provider,
                "--locale",
                args.locale,
            ]
            if args.llm_limit is not None:
                cmd.extend(["--limit", str(args.llm_limit)])
            if args.delay is not None:
                cmd.extend(["--delay", str(args.delay)])
            if args.llm_headless:
                cmd.append("--headless")
            steps.append((f"external-llms:{provider}", cmd))

    run_analysis = should_run("analysis", include, skip)
    analysis_cmd: list[str] | None = None
    if run_analysis:
        analysis_cmd = [
            sys.executable,
            str(SCRIPT_DIR / "analysis_system.py"),
            "run",
        ]
        if args.analysis_id:
            analysis_cmd.extend(["--analysis-id", args.analysis_id])
        if args.render_dashboard_report:
            analysis_cmd.append("--render-dashboard-report")

    if not steps and not run_analysis:
        print("No steps selected.")
        return 0

    print("Phase 1 parent runner")
    print(f"Workspace: {WORKSPACE_ROOT}")
    print(f"Dry run: {args.dry_run}")
    print(f"Continue on error: {args.continue_on_error}")

    failures: list[tuple[str, int]] = []

    for name, cmd in steps:
        exit_code = run_step(name, cmd, args.dry_run)
        if exit_code != 0:
            failures.append((name, exit_code))
            print(f"Step failed: {name} (exit code {exit_code})")
            if not args.continue_on_error:
                break

    if failures and not args.continue_on_error:
        print("\nFailures:")
        for name, exit_code in failures:
            print(f"- {name}: exit code {exit_code}")
        return 1

    if steps:
        print("\nAll data-collection steps completed.")

    if run_analysis and analysis_cmd:
        if not args.dry_run and not args.no_confirm_analysis:
            print("\n" + "=" * 60)
            print("Data collection finished. Ready to generate the analysis report.")
            print("=" * 60)
            answer = input("\nProceed with the analysis report? [y/N] ").strip().lower()
            if answer not in ("y", "yes"):
                print("Analysis step skipped.")
                return 1 if failures else 0

        render_dashboard = args.render_dashboard
        if (
            not args.dry_run
            and not args.no_render_dashboard
            and not render_dashboard
        ):
            print("\n" + "=" * 60)
            print("Optional: HTML dashboard for the new analysis run.")
            print("=" * 60)
            answer = input(
                "\nRender the dashboard automatically after analysis? [Y/n] "
            ).strip().lower()
            render_dashboard = answer in ("", "y", "yes")

        if render_dashboard and not args.no_render_dashboard:
            analysis_cmd.append("--render-dashboard")

        exit_code = run_step("analysis", analysis_cmd, args.dry_run)
        if exit_code != 0:
            failures.append(("analysis", exit_code))
            print(f"Step failed: analysis (exit code {exit_code})")

    if failures:
        print("\nFailures:")
        for name, exit_code in failures:
            print(f"- {name}: exit code {exit_code}")
        return 1

    print("\nAll selected steps completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
