#!/usr/bin/env python3
"""
Generate Quality Report from AI and Human Scores

This script automates the creation of quality reports by merging AI-generated scores
with human review scores, calculating agreement metrics, and generating a formatted
markdown report.

Usage:
    python generate_quality_report.py \\
        --ai-scores quality_scores_ai.json \\
        --human-scores sampled_for_review.json \\
        --output QUALITY_REPORT.md
"""

import json
import sys
import io
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import argparse

# Handle Windows encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class QualityReportGenerator:
    """Generate quality reports from AI and human scores."""
    
    def __init__(self, ai_scores_path: str, human_scores_path: Optional[str] = None):
        """Initialize with score files."""
        self.ai_scores_path = Path(ai_scores_path)
        self.human_scores_path = Path(human_scores_path) if human_scores_path else None
        self.ai_scores = []
        self.human_scores: dict[tuple[Any, Any], dict[str, Any]] = {}
        self.human_review_items: list[dict[str, Any]] = []
        self.merged_data = []
        
    def load_files(self) -> bool:
        """Load and validate score files."""
        # Load AI scores
        if not self.ai_scores_path.exists():
            print(f"Error: AI scores file not found: {self.ai_scores_path}")
            return False
        
        try:
            with open(self.ai_scores_path, 'r', encoding='utf-8') as f:
                self.ai_scores = json.load(f)
            print(f"[OK] Loaded {len(self.ai_scores)} AI scores")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in AI scores file: {e}")
            return False
        
        # Load human scores if provided
        if self.human_scores_path:
            if not self.human_scores_path.exists():
                print(f"Error: Human scores file not found: {self.human_scores_path}")
                return False
            
            try:
                with open(self.human_scores_path, 'r', encoding='utf-8') as f:
                    human_list = json.load(f)
                self.human_review_items = human_list
                # Create lookup by (issue_id, style) so variants stay distinct
                for item in human_list:
                    key = (item.get('issue_id'), item.get('style', 'unknown'))
                    self.human_scores[key] = item
                print(f"[OK] Loaded {len(human_list)} human reviews ({len(self.human_scores)} unique variants)")
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in human scores file: {e}")
                return False
        
        return True
    
    def merge_scores(self) -> bool:
        """Merge AI and human scores."""
        for ai_item in self.ai_scores:
            issue_id = ai_item.get('issue_id')
            style = ai_item.get('style', 'unknown')
            key = (issue_id, style)
            
            merged = ai_item.copy()
            
            # Add human score if available
            if key in self.human_scores:
                human_item = self.human_scores[key]
                merged['human_score'] = human_item.get('human_score')
                merged['human_review_timestamp'] = human_item.get('human_review_timestamp')
            
            self.merged_data.append(merged)
        
        return True
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate quality metrics."""
        metrics = {
            'total_responses': len(self.ai_scores),
            'ai_distribution': {1: 0, 2: 0, 3: 0, 4: 0},
            'human_distribution': {1: 0, 2: 0, 3: 0, 4: 0},
            'ai_average': 0,
            'human_average': 0,
            'reviewed_count': 0,
            'agreement_exact': 0,
            'agreement_within_1': 0,
            'disagreements': []
        }
        
        ai_total = 0
        human_total = 0

        for item in self.ai_scores:
            ai_score = item.get('ai_score')
            if ai_score:
                metrics['ai_distribution'][ai_score] += 1
                ai_total += ai_score

        ai_by_key: dict[tuple[Any, Any], dict[str, Any]] = {}
        for item in self.ai_scores:
            key = (item.get('issue_id'), item.get('style', 'unknown'))
            if key not in ai_by_key:
                ai_by_key[key] = item

        for human_item in self.human_review_items:
            human_score = human_item.get('human_score')
            if human_score is None:
                continue

            key = (human_item.get('issue_id'), human_item.get('style', 'unknown'))
            ai_item = ai_by_key.get(key)
            ai_score = ai_item.get('ai_score') if ai_item else None

            metrics['reviewed_count'] += 1
            metrics['human_distribution'][human_score] += 1
            human_total += human_score

            if ai_score is None:
                continue

            if ai_score == human_score:
                metrics['agreement_exact'] += 1

            if abs(ai_score - human_score) <= 1:
                metrics['agreement_within_1'] += 1
            else:
                metrics['disagreements'].append({
                    'issue_id': human_item.get('issue_id'),
                    'style': human_item.get('style', 'unknown'),
                    'ai_score': ai_score,
                    'human_score': human_score,
                    'diff': human_score - ai_score
                })
        
        # Calculate averages
        if metrics['total_responses'] > 0:
            metrics['ai_average'] = ai_total / metrics['total_responses']
        
        if metrics['reviewed_count'] > 0:
            metrics['human_average'] = human_total / metrics['reviewed_count']
        
        return metrics
    
    def _report_title(self) -> str:
        """Derive a human-friendly report title from the run directory name.

        Falls back to a generic title when the directory name is not
        informative (e.g. a bare timestamped quality-scoring-* folder).
        """
        try:
            run_dir = self.ai_scores_path.resolve().parent.name
        except (OSError, AttributeError):
            run_dir = ""

        if run_dir and not run_dir.startswith("quality-scoring-"):
            return f"Quality Report - {run_dir}"
        return "Quality Report"

    def generate_report(self, metrics: Dict[str, Any]) -> str:
        """Generate markdown report."""
        report = f"# {self._report_title()}\n\n"
        
        # Header with timestamp
        report += "## Executive Summary\n\n"
        report += f"**Report Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n"
        report += f"**Total Responses Scored:** {metrics['total_responses']}\n"
        report += f"**Human Sample Reviewed:** {metrics['reviewed_count']} items"
        
        if metrics['total_responses'] > 0:
            review_percent = (metrics['reviewed_count'] / metrics['total_responses']) * 100
            report += f" ({review_percent:.1f}%)\n\n"
        else:
            report += "\n\n"
        
        # AI Scoring Results
        report += "### AI Scoring Results\n"
        report += f"- **AI Average Score:** {metrics['ai_average']:.2f} / 4.0\n"
        
        score_4_pct = (metrics['ai_distribution'][4] / metrics['total_responses'] * 100) if metrics['total_responses'] > 0 else 0
        report += f"- **Excellent (Score 4):** {metrics['ai_distribution'][4]} responses ({score_4_pct:.1f}%)\n\n"
        
        # Human Review Results (if available)
        if metrics['reviewed_count'] > 0:
            report += "### Human Review Results (Sample)\n"
            report += f"- **Human Average Score:** {metrics['human_average']:.2f} / 4.0\n"
            
            if metrics['total_responses'] > 0:
                agreement_exact_pct = (metrics['agreement_exact'] / metrics['reviewed_count']) * 100
                agreement_within_pct = (metrics['agreement_within_1'] / metrics['reviewed_count']) * 100
            else:
                agreement_exact_pct = agreement_within_pct = 0
            
            report += f"- **Agreement with AI:** {agreement_exact_pct:.1f}% exact match, {agreement_within_pct:.1f}% within ±1 point\n\n"
        
        # AI Score Distribution
        report += "## AI Score Distribution\n\n"
        report += "| Score | Label | Count | Percentage |\n"
        report += "|-------|-------|-------|------------|\n"
        
        labels = {1: "Useless", 2: "Link-dependent", 3: "Partially direct", 4: "Fully direct"}
        for score in [1, 2, 3, 4]:
            count = metrics['ai_distribution'][score]
            pct = (count / metrics['total_responses'] * 100) if metrics['total_responses'] > 0 else 0
            report += f"| {score} | {labels[score]} | {count} | {pct:.1f}% |\n"
        
        # Human Review Analysis (if available)
        if metrics['reviewed_count'] > 0:
            report += "\n---\n\n"
            report += "## Human Review Analysis (Sample)\n\n"
            report += "| Score | Label | Count | Percentage |\n"
            report += "|-------|-------|-------|------------|\n"
            
            for score in [1, 2, 3, 4]:
                count = metrics['human_distribution'][score]
                pct = (count / metrics['reviewed_count'] * 100) if metrics['reviewed_count'] > 0 else 0
                report += f"| {score} | {labels[score]} | {count} | {pct:.1f}% |\n"
            
            # Disagreements section
            if metrics['disagreements']:
                report += "\n---\n\n"
                report += "## Score Disagreements\n\n"
                report += "| Issue ID | Style | AI Score | Human Score | Difference |\n"
                report += "|----------|-------|----------|-------------|------------|\n"
                
                for disagreement in metrics['disagreements']:
                    issue_id = disagreement['issue_id']
                    style = disagreement.get('style', 'unknown')
                    ai_score = disagreement['ai_score']
                    human_score = disagreement['human_score']
                    diff = disagreement['diff']
                    
                    report += f"| {issue_id} | {style} | {ai_score} | {human_score} | {diff:+d} |\n"
        
        # Key Findings
        report += "\n---\n\n"
        report += "## Key Findings\n\n"
        
        report += "✅ **Strengths:**\n"
        report += "- Comprehensive response coverage\n"
        report += "- Well-structured explanations\n"
        report += "- Relevant references provided\n\n"
        
        if metrics['disagreements']:
            report += "⚠ **Areas for Improvement:**\n"
            report += f"- {len(metrics['disagreements'])} disagreement(s) between AI and human scores\n"
            report += "- Some responses may require additional context for full understanding\n\n"
        
        # Calibration Insights
        if metrics['reviewed_count'] > 0:
            avg_diff = sum([d['diff'] for d in metrics['disagreements']]) / len(metrics['disagreements']) if metrics['disagreements'] else 0
            
            report += "## Calibration Insights\n\n"
            
            if avg_diff < 0:
                report += "- **Scorer Bias:** AI tends to score higher than human reviewers\n"
            elif avg_diff > 0:
                report += "- **Scorer Bias:** Human reviewers tend to score higher than AI\n"
            else:
                report += "- **Scorer Bias:** Balanced scoring between AI and human reviewers\n"
            
            report += f"- **Average Difference:** {avg_diff:.2f} points\n"
            report += "- **Recommendation:** Review scoring criteria for calibration\n\n"
        
        # Estimated Full Batch Quality
        if metrics['reviewed_count'] > 0 and metrics['human_average'] > 0:
            estimated_4 = (metrics['human_distribution'][4] / metrics['reviewed_count']) * 100
            estimated_3 = (metrics['human_distribution'][3] / metrics['reviewed_count']) * 100
            
            report += "## Estimated Full Batch Quality (Based on Sample)\n\n"
            report += "| Category | Estimated % |\n"
            report += "|----------|-------------|\n"
            report += f"| Score 4 (Fully direct) | {estimated_4:.1f}% |\n"
            report += f"| Score 3 (Partially direct) | {estimated_3:.1f}% |\n"
            report += f"| **Estimated Average Score** | **{metrics['human_average']:.2f} / 4.0** |\n\n"
        
        # Output Files
        report += "---\n\n"
        report += "## Output Files\n\n"
        report += "- `quality_scores_ai.json` — All AI scores\n"
        report += "- `sampled_for_review.json` — Sample reviewed (includes human scores)\n"
        report += "- `QUALITY_REPORT.md` — This report\n\n"
        
        # Footer
        report += "---\n\n"
        report += f"**Report Generated:** {datetime.now(timezone.utc).isoformat()}\n"
        
        if metrics['reviewed_count'] > 0:
            report += f"**Human Review Completed:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n"
        
        return report
    
    def generate(self, output_path: str) -> bool:
        """Generate report and save to file."""
        if not self.load_files():
            return False
        
        if not self.merge_scores():
            return False
        
        metrics = self.calculate_metrics()
        report = self.generate_report(metrics)
        
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"[OK] Report generated: {output_file}")
            print(f"\nReport Summary:")
            print(f"  • Total responses: {metrics['total_responses']}")
            print(f"  • Human reviewed: {metrics['reviewed_count']}")
            
            if metrics['reviewed_count'] > 0:
                print(f"  • AI average: {metrics['ai_average']:.2f} / 4.0")
                print(f"  • Human average: {metrics['human_average']:.2f} / 4.0")
                print(f"  • Exact agreement: {(metrics['agreement_exact'] / metrics['reviewed_count'] * 100):.1f}%")
                print(f"  • Disagreements: {len(metrics['disagreements'])}")
            
            return True
        except IOError as e:
            print(f"Error: Could not write report file: {e}")
            return False


def resolve_paths_from_run_dir(run_dir: str) -> Tuple[str, Optional[str], str]:
    """Infer ai-scores, human-scores, and output paths from a run directory.

    Looks for the standard file names produced by the workflow:
    - quality_scores_ai.json (AI scores, required)
    - sampled_for_review.json (human scores; batch reviews are merged back into
      this same file by merge_batches.py)
    - QUALITY_REPORT.md (output)
    """
    base = Path(run_dir)
    ai = base / "quality_scores_ai.json"

    single = base / "sampled_for_review.json"
    human = single if single.exists() else None

    output = base / "QUALITY_REPORT.md"
    return str(ai), (str(human) if human else None), str(output)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate quality report from AI and human scores"
    )
    parser.add_argument(
        "--run-dir",
        help=(
            "Timestamped run directory; infers --ai-scores, --human-scores, "
            "and --output from its standard file names (overridden by explicit flags)"
        )
    )
    parser.add_argument(
        "--ai-scores",
        help="Path to AI scores JSON file (required unless --run-dir is given)"
    )
    parser.add_argument(
        "--human-scores",
        help="Path to human scores JSON file (optional)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output report path (default: QUALITY_REPORT.md, or <run-dir>/QUALITY_REPORT.md)"
    )
    
    args = parser.parse_args()

    ai_scores = args.ai_scores
    human_scores = args.human_scores
    output = args.output

    # Fill any unset paths from --run-dir.
    if args.run_dir:
        inferred_ai, inferred_human, inferred_output = resolve_paths_from_run_dir(args.run_dir)
        ai_scores = ai_scores or inferred_ai
        human_scores = human_scores or inferred_human
        output = output or inferred_output

    if not ai_scores:
        parser.error("either --ai-scores or --run-dir is required")

    if output is None:
        output = "QUALITY_REPORT.md"

    generator = QualityReportGenerator(ai_scores, human_scores)
    
    if generator.generate(output):
        print(f"\n[OK] Report available at: {output}")
        sys.exit(0)
    else:
        print("\n[ERROR] Report generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
