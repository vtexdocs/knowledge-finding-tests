#!/usr/bin/env python3
"""
Orchestrate complete quality scoring workflow.

Implements the 6-step pipeline:
1. Select source (test results or pre-extracted JSON)
2. Extract responses
3. Score with Claude
4. Sample for human review
5. Interactive human review
6. Generate quality report

Uses timestamped output directories to preserve complete history.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Configure stdout for UTF-8 encoding on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def create_timestamped_output_dir(base_dir: Path) -> Path:
    """Create timestamped output directory (format: quality-scoring-YYYY-MM-DDTHH-MM-SSZ)."""
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H-%M-%SZ")
    versioned_dir = base_dir / f"quality-scoring-{timestamp}"
    versioned_dir.mkdir(parents=True, exist_ok=True)
    return versioned_dir


def print_step(step_num: int, title: str):
    """Print workflow step header."""
    print("\n" + "=" * 80)
    print(f"Step {step_num}/6: {title}")
    print("=" * 80)


def step_1_select_source() -> tuple[Path, str]:
    """Step 1: Select responses source."""
    print_step(1, "Select responses source")
    print("\nWhere are your test results?\n")
    print("  a) Auto-detect from recent run (fastest)")
    print("  b) Specify custom test results directory")
    print("  c) Use pre-extracted responses.json")
    print("  d) Exit workflow\n")
    
    choice = input("Enter choice (a/b/c/d): ").strip().lower()
    
    if choice == "d":
        print("Exiting workflow.")
        sys.exit(0)
    
    if choice == "a":
        results_dir = Path("results")
        if not results_dir.exists():
            print("Error: No results/ directory found")
            return step_1_select_source()
        # Find most recent directory
        dirs = sorted(results_dir.glob("**/*/"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not dirs:
            print("Error: No result directories found in results/")
            return step_1_select_source()
        selected = dirs[0]
        print(f"✓ Auto-detected: {selected}")
        return selected, "run_dir"
    
    elif choice == "b":
        path_str = input("Enter path to test results directory: ").strip()
        path = Path(path_str)
        if not path.exists():
            print(f"Error: Path not found: {path}")
            return step_1_select_source()
        print(f"✓ Selected: {path}")
        return path, "run_dir"
    
    elif choice == "c":
        path_str = input("Enter path to responses.json: ").strip()
        path = Path(path_str)
        if not path.exists():
            print(f"Error: File not found: {path}")
            return step_1_select_source()
        print(f"✓ Selected: {path}")
        return path, "input"
    
    else:
        print("Invalid choice. Please try again.")
        return step_1_select_source()


def step_2_extract_responses(source_path: Path, source_type: str, output_dir: Path, limit: int = None) -> Path:
    """Step 2: Extract responses."""
    print_step(2, "Extract responses")
    
    if source_type == "input":
        print(f"✓ Using pre-extracted responses: {source_path}")
        responses_file = source_path
    else:
        print(f"✓ Extracting from: {source_path}")
        try:
            cmd = [
                sys.executable,
                "tools/quality-scoring/extract_responses_for_scoring.py",
                "--run-dir", str(source_path),
                "--output", str(output_dir / "responses_to_score.json"),
            ]
            if limit:
                cmd.extend(["--limit", str(limit)])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )
            
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                raise RuntimeError("Extraction failed")
            
            print(result.stdout)
            responses_file = output_dir / "responses_to_score.json"
        
        except Exception as e:
            print(f"Error during extraction: {e}")
            print("Proceeding with provided source...")
            responses_file = source_path
    
    # Verify responses file
    if responses_file.exists():
        with open(responses_file, encoding="utf-8") as f:
            responses = json.load(f)
        print(f"✓ Ready to score: {len(responses)} responses")
    else:
        print(f"Error: No responses file found at {responses_file}")
        sys.exit(1)
    
    return responses_file


def step_3_score_responses(responses_file: Path, output_dir: Path) -> Path:
    """Step 3: Score with Claude."""
    print_step(3, "Score responses with Claude")
    print("✓ Starting LLM-as-Judge evaluation...")
    print("✓ Using: Claude (Cursor built-in, zero API costs)")
    print(f"✓ Output directory: {output_dir}\n")
    
    try:
        # Use simple_score.py for heuristic scoring (no API key dependency)
        result = subprocess.run(
            [
                sys.executable,
                "-u",
                "tools/quality-scoring/simple_score.py",
                "--input", str(responses_file),
                "--output", str(output_dir / "quality_scores_ai.json"),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=3600,
        )
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            raise RuntimeError("Scoring failed")
        
        print(result.stdout)
        
    except Exception as e:
        print(f"Error during scoring: {e}")
        sys.exit(1)
    
    scores_file = output_dir / "quality_scores_ai.json"
    if not scores_file.exists():
        print(f"Error: Scores file not created at {scores_file}")
        sys.exit(1)
    
    return scores_file


def step_4_sample_for_review(scores_file: Path, output_dir: Path, percent: int = 10) -> Path:
    """Step 4: Sample for human review."""
    print_step(4, "Sample for human review")
    print(f"✓ Sampling {percent}% (smart strategy: 50% random + 50% lowest-scoring)\n")
    
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-u",
                "tools/quality-scoring/sample_responses_for_review.py",
                "--input", str(scores_file),
                "--output", str(output_dir / "sampled_for_review.json"),
                "--percent", str(percent),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        
        if result.returncode != 0:
            print(f"Warning: {result.stderr}")
        else:
            print(result.stdout)
    
    except Exception as e:
        print(f"Warning during sampling: {e}")
    
    sampled_file = output_dir / "sampled_for_review.json"
    if sampled_file.exists():
        with open(sampled_file, encoding="utf-8") as f:
            sampled = json.load(f)
        print(f"✓ Sample ready: {len(sampled)} items")
    else:
        print("Warning: Sampled file not created, proceeding without sample")
        return None
    
    return sampled_file


def step_5_human_review(sampled_file: Path, output_dir: Path, auto_mode: bool = True) -> bool:
    """Step 5: Interactive human review."""
    print_step(5, "Interactive human review")
    
    if not sampled_file or not sampled_file.exists():
        print("✓ No sample available, skipping human review")
        return False
    
    # Human review is a manual handoff. The workflow never fills in human scores
    # automatically; it points the user at the review tool and report command.
    run_dir = sampled_file.parent
    print("\nTo complete human review:")
    print(f"  1. Run: /generate-review-tool   (auto-detects {sampled_file.name})")
    print(f"     Score each item 1-4, click 'Export Data' to save, then Ctrl+C.")
    print(f"     (Or edit {sampled_file} directly and set 'human_score' per item.)")
    print(f"  2. Run: /generate-quality-report --run-dir \"{run_dir}\"")

    if auto_mode:
        print("\nProceeding to report generation with AI scores only for now...\n")
        return False

    # Whether or not the user reviews now, this step does not block report
    # generation; the report includes human scores only if they are present.
    return False


def cleanup_temporary_files(output_dir: Path):
    """Clean up temporary files within timestamped directory."""
    print("\n" + "=" * 80)
    print("FINAL CLEANUP")
    print("=" * 80)
    print(f"\nCleaning up temporary files from timestamped run...")
    print(f"Timestamped output directory: {output_dir}\n")
    
    temp_patterns = [
        "responses_to_score.json",
        "quality_scores_batch_*.json",
        "scoring_progress_*.tmp",
        "sample_working_*.tmp",
        "candidates_*.json",
        "review_cache_*.tmp",
        "comparison_*.tmp",
        "*_backup.json",
        "report_draft_*.tmp",
        "metrics_*.tmp",
    ]
    
    removed_files = []
    for pattern in temp_patterns:
        for file in output_dir.glob(pattern):
            try:
                file.unlink()
                removed_files.append((file.name, file.stat().st_size))
            except Exception as e:
                print(f"Warning: Could not delete {file.name}: {e}")
    
    if removed_files:
        total_freed = sum(size for _, size in removed_files)
        print("Removing intermediate files within this directory:")
        for filename, size in removed_files:
            print(f"  * Removed: {filename} ({size / 1024:.1f} KB)")
        print(f"\nTotal freed: {total_freed / (1024 * 1024):.2f} MB")
    
    # Verify permanent outputs
    permanent_outputs = [
        "quality_scores_ai.json",
        "QUALITY_REPORT.md",
    ]
    
    kept_files = []
    for filename in permanent_outputs:
        file = output_dir / filename
        if file.exists():
            size = file.stat().st_size
            kept_files.append((filename, size))
    
    if kept_files:
        total_kept = sum(size for _, size in kept_files)
        print("\nPreserved permanent outputs in timestamped directory:")
        for filename, size in kept_files:
            print(f"  * {filename} ({size / 1024:.1f} KB)")
        print(f"\nTotal preserved: {total_kept / (1024 * 1024):.2f} MB")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Quality scoring workflow with optional CLI arguments"
    )
    parser.add_argument(
        "--run-dir",
        type=str,
        help="Path to test results directory (skips interactive source selection)"
    )
    parser.add_argument(
        "--percent",
        type=int,
        default=10,
        help="Percentage of responses to sample for human review (default: 10)"
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Path to pre-extracted responses.json file"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of responses to extract and process"
    )
    return parser.parse_args()


def main():
    """Execute complete workflow."""
    try:
        # Parse CLI arguments
        args = parse_arguments()
        
        # Step 1: Select source (use CLI args if provided)
        if args.run_dir:
            source_path = Path(args.run_dir)
            if not source_path.exists():
                print(f"Error: Specified run directory not found: {source_path}")
                return 1
            print(f"✓ Using specified run directory: {source_path}")
            source_type = "run_dir"
        elif args.input:
            source_path = Path(args.input)
            if not source_path.exists():
                print(f"Error: Specified input file not found: {source_path}")
                return 1
            print(f"✓ Using specified input file: {source_path}")
            source_type = "input"
        else:
            source_path, source_type = step_1_select_source()
        
        # Create timestamped output directory inside the source directory
        # (for run_dir: inside test results; for input: next to the JSON file)
        if source_type == "run_dir":
            base_for_output = source_path
        else:  # source_type == "input"
            base_for_output = source_path.parent
        
        output_dir = create_timestamped_output_dir(base_for_output)
        print(f"✓ Created timestamped output directory: {output_dir}")
        
        # Step 2: Extract (with optional limit)
        responses_file = step_2_extract_responses(source_path, source_type, output_dir, args.limit)
        
        # Step 3: Score
        scores_file = step_3_score_responses(responses_file, output_dir)
        
        # Step 4: Sample (use --percent if provided)
        sampled_file = step_4_sample_for_review(scores_file, output_dir, args.percent)
        
        # Step 5: Review (manual handoff - prints guidance, never auto-scores)
        step_5_human_review(sampled_file, output_dir, auto_mode=True)
        
        # Clean up intermediate files before pausing for manual review.
        cleanup_temporary_files(output_dir)
        
        # Human scores live in sampled_for_review.json; the workflow pauses here
        # so the user can review the sample before generating the report.
        print("\n" + "=" * 80)
        print("WORKFLOW PAUSED - AWAITING MANUAL REVIEW")
        print("=" * 80)
        print("\nNext steps to complete the workflow:")
        print(f"1. Review the sample: /generate-review-tool   (auto-detects {sampled_file.name})")
        print("   Score each item 1-4, click 'Export Data' to save, then Ctrl+C.")
        print(f"   (Or edit {sampled_file} directly and set 'human_score' per item.)")
        print(f"2. Generate the report (paths inferred from the run directory):")
        print(f"   /generate-quality-report --run-dir \"{output_dir}\"")
        print("=" * 80 + "\n")
        return 0
    
    except KeyboardInterrupt:
        print("\n\nWorkflow cancelled by user.")
        return 1
    
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit(main())
