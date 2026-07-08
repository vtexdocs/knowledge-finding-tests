#!/usr/bin/env python3
"""
Standardize historical test-suite result folders into the canonical layout.

Canonical layout:
    results/<path-family>/<variant>/<run-folder>/...

Examples:
    results/internal-search/algolia-helpcenter/algolia-helpcenter 2026-03-17 14-49/
    results/docs-assistant/api/docs-assistant 2026-03-17 16-23/
    results/external-search/google-search-playwright/google-search-playwright 2026-03-24 15-37/
    results/external-llms/chatgpt/external-llms-chatgpt 2026-03-04 22-26/

The script is intentionally idempotent: once files are already in the canonical
layout, running it again should perform no work.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
RESULTS_DIR = REPO_ROOT / "results"

INTERNAL_VARIANTS = (
    "algolia-helpcenter",
    "algolia-devportal",
    "hybrid-search",
)


@dataclass
class MigrationAction:
    description: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reorganize historical test-suite results into the canonical layout."
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Apply the filesystem changes. Without this flag, the script only reports what would change.",
    )
    return parser.parse_args()


def ensure_dir(path: Path, write: bool) -> None:
    if write:
        path.mkdir(parents=True, exist_ok=True)


def remove_empty_parent_dirs(path: Path, stop_at: Path, write: bool) -> None:
    current = path
    while current != stop_at and current.exists():
        try:
            if any(current.iterdir()):
                break
        except OSError:
            break
        if write:
            current.rmdir()
        current = current.parent


def move_path(src: Path, dst: Path, write: bool) -> None:
    ensure_dir(dst.parent, write)
    if dst.exists():
        if src.resolve() == dst.resolve():
            return
        raise FileExistsError(f"Destination already exists: {dst}")
    if write:
        shutil.move(str(src), str(dst))


def write_json(path: Path, payload: dict, write: bool) -> None:
    if write:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def format_run_folder(prefix: str, dt: datetime) -> str:
    return f"{prefix} {dt.strftime('%Y-%m-%d %H-%M')}"


def parse_run_id_timestamp(run_id: str) -> datetime | None:
    match = re.search(r"(\d{4}-\d{2}-\d{2})-(\d{6})$", run_id)
    if not match:
        return None
    return datetime.strptime(f"{match.group(1)} {match.group(2)}", "%Y-%m-%d %H%M%S")


def parse_embedded_timestamp(text: str) -> datetime | None:
    patterns = (
        r"(\d{4}-\d{2}-\d{2})[T_-](\d{2})-(\d{2})-(\d{2})",
        r"(\d{4}-\d{2}-\d{2})[T_-](\d{2})[:_-](\d{2})[:_-](\d{2})",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            date_part, hour, minute, second = match.groups()
            return datetime.strptime(
                f"{date_part} {hour}:{minute}:{second}",
                "%Y-%m-%d %H:%M:%S",
            )
    return None


def unique_run_dir(parent: Path, base_name: str) -> Path:
    candidate = parent / base_name
    if not candidate.exists():
        return candidate

    suffix = 2
    while True:
        candidate = parent / f"{base_name} ({suffix})"
        if not candidate.exists():
            return candidate
        suffix += 1


def move_existing_run_dirs_into_variant_subdirs(actions: list[MigrationAction], write: bool) -> None:
    internal_root = RESULTS_DIR / "internal-search"
    for variant in INTERNAL_VARIANTS:
        variant_root = internal_root / variant
        ensure_dir(variant_root, write)

        for child in sorted(internal_root.iterdir()) if internal_root.exists() else []:
            if not child.is_dir():
                continue
            if child == variant_root:
                continue
            if child.parent != internal_root:
                continue
            if child.name.startswith(f"{variant} "):
                dst = variant_root / child.name
                actions.append(MigrationAction(f"Move {child} -> {dst}"))
                move_path(child, dst, write)

    docs_root = RESULTS_DIR / "docs-assistant"
    docs_api_root = docs_root / "api"
    ensure_dir(docs_api_root, write)
    for child in sorted(docs_root.iterdir()) if docs_root.exists() else []:
        if child.is_dir() and child.parent == docs_root and child.name.startswith("docs-assistant "):
            dst = docs_api_root / child.name
            actions.append(MigrationAction(f"Move {child} -> {dst}"))
            move_path(child, dst, write)

    llm_root = RESULTS_DIR / "external-llms"
    if llm_root.exists():
        for child in sorted(llm_root.iterdir()):
            if not child.is_dir():
                continue
            if child.name in {"chatgpt", "gemini"}:
                continue
            meta_path = child / "run_metadata.json"
            if not meta_path.exists():
                continue
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue

            provider = str(meta.get("provider", "")).strip().lower()
            if not provider:
                continue

            started_at = str(meta.get("started_at", "")).strip()
            dt = None
            if started_at:
                dt = datetime.fromisoformat(started_at.replace("Z", "+00:00")).replace(tzinfo=None)
            if dt is None:
                dt = parse_embedded_timestamp(child.name) or datetime.fromtimestamp(child.stat().st_mtime)

            provider_root = llm_root / provider
            ensure_dir(provider_root, write)
            desired_name = format_run_folder(f"external-llms-{provider}", dt)
            dst = provider_root / desired_name
            if child == dst:
                continue
            if dst.exists():
                dst = unique_run_dir(provider_root, desired_name)

            actions.append(MigrationAction(f"Move {child} -> {dst}"))
            move_path(child, dst, write)


def migrate_legacy_internal_search(actions: list[MigrationAction], write: bool) -> None:
    legacy_root = RESULTS_DIR / "internal-search" / "internal-search-2026-03-12"
    if not legacy_root.exists():
        return

    internal_root = RESULTS_DIR / "internal-search"
    hybrid_target_dir: Path | None = None

    for variant in INTERNAL_VARIANTS:
        legacy_variant_dir = legacy_root / variant
        if not legacy_variant_dir.exists():
            continue

        json_files = sorted(legacy_variant_dir.glob("*.json"))
        if not json_files:
            continue

        json_path = json_files[0]
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        run_id = str(payload.get("run_id", "")).strip()
        dt = parse_run_id_timestamp(run_id) or parse_embedded_timestamp(json_path.name)
        if dt is None:
            dt = datetime.fromtimestamp(json_path.stat().st_mtime)

        variant_root = internal_root / variant
        ensure_dir(variant_root, write)
        target_dir = variant_root / format_run_folder(variant, dt)
        ensure_dir(target_dir, write)

        for child in sorted(legacy_variant_dir.iterdir()):
            dst = target_dir / child.name
            actions.append(MigrationAction(f"Move {child} -> {dst}"))
            move_path(child, dst, write)

        if variant == "hybrid-search":
            hybrid_target_dir = target_dir

        remove_empty_parent_dirs(legacy_variant_dir, legacy_root, write)

    comparison_files = sorted(legacy_root.glob("internal-search-comparison-*.md"))
    if hybrid_target_dir:
        for comparison_file in comparison_files:
            dst = hybrid_target_dir / comparison_file.name
            actions.append(MigrationAction(f"Move {comparison_file} -> {dst}"))
            move_path(comparison_file, dst, write)

    remove_empty_parent_dirs(legacy_root, RESULTS_DIR / "internal-search", write)


def migrate_loose_docs_assistant_files(actions: list[MigrationAction], write: bool) -> None:
    docs_root = RESULTS_DIR / "docs-assistant"
    api_root = docs_root / "api"
    ensure_dir(api_root, write)
    remaining_analysis_files = {
        analysis_path
        for analysis_path in sorted(docs_root.glob("analysis-docs-assistant-run-*.md"))
    }

    loose_json_files = sorted(docs_root.glob("docs-assistant-run-*.json"))
    for json_path in loose_json_files:
        dt = parse_embedded_timestamp(json_path.name) or datetime.fromtimestamp(json_path.stat().st_mtime)
        run_dir = api_root / format_run_folder("docs-assistant", dt)
        ensure_dir(run_dir, write)

        json_dst = run_dir / json_path.name
        actions.append(MigrationAction(f"Move {json_path} -> {json_dst}"))
        move_path(json_path, json_dst, write)

        analysis_src = None
        exact_analysis_name = f"analysis-{json_path.stem}.md"
        exact_analysis_path = docs_root / exact_analysis_name
        if exact_analysis_path in remaining_analysis_files:
            analysis_src = exact_analysis_path
        else:
            for candidate in sorted(remaining_analysis_files):
                candidate_dt = parse_embedded_timestamp(candidate.name)
                if candidate_dt == dt:
                    analysis_src = candidate
                    break

        if analysis_src is not None:
            analysis_dst = run_dir / analysis_src.name
            actions.append(MigrationAction(f"Move {analysis_src} -> {analysis_dst}"))
            move_path(analysis_src, analysis_dst, write)
            remaining_analysis_files.remove(analysis_src)


def normalize_google_results_json(path: Path, run_dir: Path, write: bool) -> bool:
    if not path.exists():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False

    expected_run_dir = str(run_dir.resolve())
    if str(payload.get("run_directory", "")).strip() == expected_run_dir:
        return False

    payload["run_directory"] = expected_run_dir
    write_json(path, payload, write)
    return True


def migrate_legacy_google_runs(actions: list[MigrationAction], write: bool) -> None:
    search_root = RESULTS_DIR / "external-search"
    google_root = search_root / "google-search-playwright"
    ensure_dir(google_root, write)

    # Normalize already-standardized folders.
    for run_dir in sorted(p for p in google_root.glob("*") if p.is_dir()):
        results_path = run_dir / "results.json"
        if results_path.exists() and normalize_google_results_json(results_path, run_dir, write):
            actions.append(MigrationAction(f"Normalize run_directory in {results_path}"))

    legacy_root = search_root / "google-search-2026-03-06"
    if not legacy_root.exists():
        return

    for json_path in sorted(legacy_root.rglob("*.json")):
        dt = parse_embedded_timestamp(json_path.name) or datetime.fromtimestamp(json_path.stat().st_mtime)
        target_name = format_run_folder("google-search-playwright", dt)
        target_dir = unique_run_dir(google_root, target_name)
        ensure_dir(target_dir, write)

        dst = target_dir / "results.json"
        actions.append(MigrationAction(f"Move {json_path} -> {dst}"))
        move_path(json_path, dst, write)
        if normalize_google_results_json(dst, target_dir, write):
            actions.append(MigrationAction(f"Normalize run_directory in {dst}"))

    if write and legacy_root.exists():
        shutil.rmtree(legacy_root)
    elif legacy_root.exists():
        actions.append(MigrationAction(f"Remove empty legacy tree {legacy_root}"))


def main() -> int:
    args = parse_args()
    actions: list[MigrationAction] = []

    move_existing_run_dirs_into_variant_subdirs(actions, args.write)
    migrate_legacy_internal_search(actions, args.write)
    migrate_loose_docs_assistant_files(actions, args.write)
    migrate_legacy_google_runs(actions, args.write)

    if not actions:
        print("No result-layout changes were needed.")
        return 0

    for action in actions:
        print(action.description)

    if not args.write:
        print("\nDry run only. Re-run with --write to apply these changes.")
    else:
        print("\nResults layout standardized.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
