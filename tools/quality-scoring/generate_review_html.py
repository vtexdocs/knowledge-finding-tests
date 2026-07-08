#!/usr/bin/env python3
"""
Generate an interactive HTML review interface for quality scoring.

This script creates a browser-based review tool that allows technical writers
to review AI responses and assign quality scores without editing JSON files.

The HTML tool:
- Displays full response content, links, and metadata
- Provides radio button scoring (1-4)
- Auto-saves progress to sampled_for_review.json
- Tracks progress across page reloads
- Works offline with embedded data

Usage:
    python generate_review_html.py --input quality_scores_ai.json --output review.html
    python generate_review_html.py --input quality_scores_ai.json --existing-review sampled_for_review.json
"""

from __future__ import annotations

import argparse
import json
import sys
import io
from pathlib import Path
from typing import Any
from datetime import datetime, timezone

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def load_scores(scores_file: Path) -> list[dict[str, Any]]:
    """Load quality_scores_ai.json or sampled_for_review.json."""
    if not scores_file.exists():
        raise FileNotFoundError(f"Scores file not found: {scores_file}")
    
    with open(scores_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_full_responses(base_dir: Path) -> dict[str, dict[str, Any]]:
    """Load responses_to_score.json to get full query and response_text data."""
    responses_file = base_dir / "responses_to_score.json"
    if not responses_file.exists():
        # Try parent directory if not found
        responses_file = base_dir.parent / "responses_to_score.json"
    
    if not responses_file.exists():
        return {}
    
    try:
        with open(responses_file, 'r', encoding='utf-8') as f:
            responses = json.load(f)
        # Create lookup by (issue_id, style) composite key to handle multiple variants
        lookup = {}
        for item in responses:
            issue_id = item.get('issue_id')
            style = item.get('style', 'unknown')
            key = f"{issue_id}||{style}"  # Composite key
            lookup[key] = item
        return lookup
    except (json.JSONDecodeError, IOError):
        return {}


def load_existing_review(review_file: Path) -> dict[str, Any]:
    """Load existing sampled_for_review.json to preserve progress."""
    if not review_file.exists():
        return {}
    
    try:
        with open(review_file, 'r', encoding='utf-8') as f:
            items = json.load(f)
        # Create lookup by issue_id
        return {item.get('issue_id'): item for item in items}
    except (json.JSONDecodeError, IOError):
        return {}


def merge_with_existing(scores: list[dict[str, Any]], existing_review: dict[str, Any]) -> list[dict[str, Any]]:
    """Merge AI scores with existing human scores if available."""
    for item in scores:
        issue_id = item.get('issue_id')
        if issue_id in existing_review:
            existing = existing_review[issue_id]
            item['human_score'] = existing.get('human_score')
            item['human_notes'] = existing.get('human_notes')
            item['human_review_timestamp'] = existing.get('human_review_timestamp')
    return scores


def _resolve_query_from_response(response_data: dict[str, Any]) -> str:
    """Pick the best available query text from a full response record."""
    query = (response_data.get('query') or '').strip()
    if query:
        return query
    user_intent = (response_data.get('user_intent') or '').strip()
    if user_intent and user_intent != '**user_intent**':
        return user_intent
    return 'N/A'


def _find_response_data(
    full_responses: dict[str, dict[str, Any]],
    issue_id: str,
    style: str,
) -> dict[str, Any] | None:
    """Match full response by (issue_id, style), falling back to issue_id only."""
    key = f"{issue_id}||{style}"
    if key in full_responses:
        return full_responses[key]
    for candidate_key, data in full_responses.items():
        if candidate_key.startswith(f"{issue_id}||"):
            return data
    return None


def enrich_with_response_data(scores: list[dict[str, Any]], full_responses: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Enrich scores with query and response_text from full_responses using (issue_id, style) matching."""
    for item in scores:
        issue_id = item.get('issue_id')
        style = item.get('style', 'unknown')
        response_data = _find_response_data(full_responses, issue_id, style)

        if response_data:
            if not item.get('query'):
                item['query'] = _resolve_query_from_response(response_data)
            if not item.get('response_text'):
                item['response_text'] = response_data.get('response_text', '')
            if not item.get('provided_links'):
                item['provided_links'] = response_data.get('provided_links', [])
            if not item.get('locale'):
                item['locale'] = response_data.get('locale', 'en')
    
    return scores


def escape_js_string(s: str) -> str:
    """Escape string for safe embedding in JavaScript."""
    if not isinstance(s, str):
        return str(s)
    return (s
        .replace('\\', '\\\\')
        .replace('"', '\\"')
        .replace('\n', '\\n')
        .replace('\r', '\\r')
        .replace('\t', '\\t')
        .replace('</', '<\\/'))


def format_links_html(links: list[dict[str, str]]) -> str:
    """Format links as HTML list."""
    if not links:
        return '<p class="no-links">No links found</p>'
    
    html = '<ul class="links-list">\n'
    for link in links:
        url = link.get('url', '#')
        title = link.get('title', 'Link')
        html += f'  <li><a href="{url}" target="_blank">{title}</a></li>\n'
    html += '</ul>\n'
    return html


def generate_html(
    scores: list[dict[str, Any]],
    output_file: Path,
    batch_id: int | None = None,
    total_batches: int | None = None,
    reviewer: str | None = None,
) -> None:
    """Generate the interactive review HTML file.

    When batch_id/total_batches are provided, a batch banner is shown in the
    header so the reviewer always knows which batch they are working on and who
    is responsible for it.
    """
    
    # CACHE-BUSTING: Add generation timestamp for debugging freshness issues
    timestamp = datetime.now(timezone.utc).isoformat()

    # Build the batch banner HTML (empty string when not batching).
    if batch_id is not None and total_batches is not None:
        reviewer_html = (
            f'<span class="batch-reviewer">Reviewer: {reviewer}</span>'
            if reviewer else
            '<span class="batch-reviewer batch-unassigned">Unassigned</span>'
        )
        batch_banner = (
            '<div class="batch-banner">'
            f'<span class="batch-label">Batch {batch_id} of {total_batches}</span>'
            f'{reviewer_html}'
            '</div>'
        )
    else:
        batch_banner = ''
    
    # Prepare data as JSON - NO indentation to keep it on one line for safe embedding
    # Then escape for safe inclusion in JavaScript template literal
    scores_json = json.dumps(scores, ensure_ascii=False)
    # Escape backticks and backslashes for template literal
    scores_json = scores_json.replace('\\', '\\\\')  # Escape backslashes first
    scores_json = scores_json.replace('`', '\\`')    # Escape backticks
    
    # Create the HTML template (NOT an f-string to avoid escaping braces for JavaScript/CSS)
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quality Score Review</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .batch-banner {{
            display: inline-flex;
            align-items: center;
            gap: 12px;
            background: rgba(255, 255, 255, 0.18);
            border: 1px solid rgba(255, 255, 255, 0.35);
            border-radius: 999px;
            padding: 6px 18px;
            margin: 6px 0 4px;
            font-size: 14px;
        }}
        
        .batch-label {{
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        
        .batch-reviewer {{
            font-weight: 500;
            opacity: 0.95;
        }}
        
        .batch-unassigned {{
            font-style: italic;
            opacity: 0.8;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 4px;
            margin-top: 15px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            background: rgba(255, 255, 255, 0.8);
            transition: width 0.3s ease;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .navigation {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}
        
        .item-counter {{
            font-size: 18px;
            font-weight: 600;
            color: #667eea;
        }}
        
        .nav-buttons {{
            display: flex;
            gap: 10px;
        }}
        
        button {{
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        
        .btn-nav {{
            background: #f0f0f0;
            color: #333;
        }}
        
        .btn-nav:hover:not(:disabled) {{
            background: #e0e0e0;
        }}
        
        .btn-nav:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        
        .metadata {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .metadata-item {{
            font-size: 13px;
        }}
        
        .metadata-label {{
            font-weight: 600;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .metadata-value {{
            color: #333;
            margin-top: 4px;
            font-size: 14px;
        }}
        
        .query {{
            background: #e8f0fe;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 25px;
            border-radius: 4px;
        }}
        
        .query-label {{
            font-weight: 600;
            color: #667eea;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        
        .query-text {{
            color: #333;
            font-size: 16px;
            line-height: 1.5;
        }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section-title {{
            font-size: 14px;
            font-weight: 700;
            color: #667eea;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
        }}
        
        .section-title::before {{
            content: '';
            width: 4px;
            height: 16px;
            background: #667eea;
            border-radius: 2px;
            margin-right: 10px;
        }}
        
        .response-text {{
            background: #fafafa;
            padding: 20px;
            border-radius: 8px;
            line-height: 1.8;
            color: #333;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #eee;
        }}
        
        .links-list {{
            list-style: none;
        }}
        
        .links-list li {{
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .links-list li:last-child {{
            border-bottom: none;
        }}
        
        .links-list a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            word-break: break-word;
        }}
        
        .links-list a:hover {{
            text-decoration: underline;
        }}
        
        .no-links {{
            color: #999;
            font-style: italic;
        }}
        
        .ai-reference {{
            background: #f0f7ff;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin-bottom: 25px;
        }}
        
        .ai-score {{
            font-weight: 600;
            color: #667eea;
        }}
        
        .ai-reasoning {{
            color: #666;
            margin-top: 8px;
            font-size: 14px;
        }}
        
        .scoring-section {{
            background: #fafafa;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 25px;
        }}
        
        .scoring-label {{
            font-size: 14px;
            font-weight: 700;
            color: #667eea;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 15px;
            display: block;
        }}
        
        .score-options {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }}
        
        .score-option {{
            display: flex;
            align-items: center;
        }}
        
        .score-option input[type="radio"] {{
            margin-right: 10px;
            cursor: pointer;
            width: 18px;
            height: 18px;
        }}
        
        .score-option label {{
            cursor: pointer;
            flex: 1;
        }}
        
        .score-description {{
            font-size: 13px;
            color: #666;
        }}
        
        .score-number {{
            font-weight: 700;
            color: #667eea;
            margin-right: 5px;
        }}
        
        .notes-section {{
            margin-top: 15px;
        }}
        
        .notes-section label {{
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #666;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .notes-section textarea {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-family: inherit;
            font-size: 14px;
            resize: vertical;
            min-height: 80px;
        }}
        
        .notes-section textarea:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        
        .action-buttons {{
            display: flex;
            gap: 10px;
            justify-content: flex-start;
            padding-top: 20px;
            border-top: 1px solid #eee;
            flex-wrap: wrap;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            flex: 0 1 auto;
        }}
        
        .btn-primary:hover {{
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }}
        
        .btn-secondary {{
            background: #f0f0f0;
            color: #333;
        }}
        
        .btn-secondary:hover {{
            background: #e0e0e0;
        }}
        
        .completion-message {{
            text-align: center;
            padding: 40px;
            background: #f0fdf4;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        .completion-message h2 {{
            color: #22c55e;
            margin-bottom: 10px;
        }}
        
        .completion-message p {{
            color: #666;
        }}
        
        .score-definitions {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            font-size: 13px;
        }}
        
        .score-def {{
            display: flex;
            margin-bottom: 10px;
        }}
        
        .score-def:last-child {{
            margin-bottom: 0;
        }}
        
        .score-def-num {{
            font-weight: 700;
            color: #667eea;
            min-width: 30px;
            margin-right: 15px;
        }}
        
        .score-def-text {{
            color: #666;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #999;
            border-top: 1px solid #eee;
        }}
        
        /* Toast notification styles */
        .toast-container {{
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            pointer-events: none;
        }}
        
        .toast {{
            background: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 300px;
            pointer-events: auto;
            animation: slideIn 0.3s ease-out, slideOut 0.3s ease-in 2.7s forwards;
        }}
        
        .toast.success {{
            border-left: 4px solid #22c55e;
        }}
        
        .toast.error {{
            border-left: 4px solid #ef4444;
        }}
        
        .toast-icon {{
            font-size: 20px;
            font-weight: bold;
        }}
        
        .toast.success .toast-icon {{
            color: #22c55e;
        }}
        
        .toast.error .toast-icon {{
            color: #ef4444;
        }}
        
        .toast-message {{
            color: #333;
            font-size: 14px;
            flex: 1;
        }}
        
        @keyframes slideIn {{
            from {{
                transform: translateX(400px);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}
        
        @keyframes slideOut {{
            from {{
                transform: translateX(0);
                opacity: 1;
            }}
            to {{
                transform: translateX(400px);
                opacity: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Quality Score Review</h1>
            __BATCH_BANNER_PLACEHOLDER__
            <p id="subtitle">Loading review items...</p>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
        </div>
        
        <div class="content" id="content">
            <!-- Content will be inserted here by JavaScript -->
        </div>
        
        <div class="footer">
            <p>Review Tool • All data saved locally • No automatic submissions</p>
        </div>
    </div>
    
    <!-- Toast notification container -->
    <div id="toast-container" class="toast-container"></div>
    
    <script>
        // Cache-busting: Timestamp when this HTML was generated
        const htmlGeneratedAt = new Date().toISOString();
        const embeddedTimestamp = '__TIMESTAMP_PLACEHOLDER__';
        
        // Embedded scores data
        const scoresData = JSON.parse(`{scores_json}`);
        
        // Scoring definitions (assume the user will not click links)
        const scoreDefinitions = {{
            1: "Useless - Wrong/off-topic, or links don't help",
            2: "Link-dependent - Text is navigation only; answer lives behind links",
            3: "Partially direct - Text correct but a required step/value needs a link",
            4: "Fully direct - Text alone fully solves it; links optional"
        }};
        
        let currentIndex = 0;
        
        // CACHE-BUSTING: Verify data freshness on page load
        function validateDataFreshness() {{
            // Check if embedded data exists and is non-empty
            if (!scoresData || scoresData.length === 0) {{
                console.warn('⚠ WARNING: No embedded data found. Data may be stale.');
                showToast('⚠ WARNING: Review data appears to be stale. Please refresh the page.', 'warning');
                return false;
            }}
            
            // Log data freshness info
            console.log('✓ Data loaded successfully');
            console.log(`  Items in current HTML: ${scoresData.length}`);
            console.log(`  Generated at: ${embeddedTimestamp}`);
            return true;
        }}
        
        // Initialize
        function init() {{
            // Validate data before proceeding
            if (!validateDataFreshness()) {{
                document.getElementById('content').innerHTML = '<p class="error">Error: Review data not found. Please refresh the page or restart the review server.</p>';
                return;
            }}
            
            if (scoresData.length === 0) {{
                document.getElementById('content').innerHTML = '<p>No items to review.</p>';
                return;
            }}
            
            loadFromLocalStorage();
            renderCurrentItem();
            updateProgress();
        }}
        
        function loadFromLocalStorage() {{
            const saved = localStorage.getItem('reviewProgress');
            if (saved) {{
                const progress = JSON.parse(saved);
                scoresData.forEach((item, idx) => {{
                    if (progress[item.issue_id]) {{
                        scoresData[idx].human_score = progress[item.issue_id].human_score;
                        scoresData[idx].human_notes = progress[item.issue_id].human_notes;
                        scoresData[idx].human_review_timestamp = progress[item.issue_id].human_review_timestamp;
                    }}
                }});
            }}
        }}
        
        function saveToLocalStorage() {{
            const progress = {{}};
            scoresData.forEach(item => {{
                if (item.human_score !== null && item.human_score !== undefined) {{
                    progress[item.issue_id] = {{
                        human_score: item.human_score,
                        human_notes: item.human_notes,
                        human_review_timestamp: item.human_review_timestamp
                    }};
                }}
            }});
            localStorage.setItem('reviewProgress', JSON.stringify(progress));
        }}
        
        function updateProgress() {{
            const total = scoresData.length;
            const reviewed = scoresData.filter(item => item.human_score !== null && item.human_score !== undefined).length;
            const percent = (reviewed / total) * 100;
            
            document.getElementById('progressFill').style.width = percent + '%';
            document.getElementById('subtitle').textContent = `${{reviewed}} of ${{total}} items scored`;
        }}
        
        function renderCurrentItem() {{
            const item = scoresData[currentIndex];
            if (!item) return;
            
            const links = item.links_found || item.provided_links || [];
            const linksHtml = links.length > 0
                ? '<ul class="links-list">' + links.map(l => 
                    `<li><a href="${{l.url}}" target="_blank">${{l.title || l.url}}</a></li>`
                ).join('') + '</ul>'
                : '<p class="no-links">No links found</p>';
            
            const responseText = item.response_text || 'No response text available';
            const humanScore = item.human_score;
            const humanNotes = item.human_notes || '';
            const allReviewed = scoresData.every(i => i.human_score !== null && i.human_score !== undefined);
            
            const html = `
                <div class="navigation">
                    <div class="item-counter">Item ${{currentIndex + 1}} of ${{scoresData.length}}</div>
                    <div class="nav-buttons">
                        <button class="btn-nav" onclick="previousItem()" ${{currentIndex === 0 ? 'disabled' : ''}}>
                            ◀ Previous
                        </button>
                        <button class="btn-nav" onclick="nextItem()" ${{currentIndex === scoresData.length - 1 ? 'disabled' : ''}}>
                            Next ▶
                        </button>
                    </div>
                </div>
                
                ${{allReviewed ? '<div class="completion-message"><h2>✓ All items scored!</h2><p>All items in this batch have been reviewed.</p></div>' : ''}}
                
                <div class="metadata">
                    <div class="metadata-item">
                        <div class="metadata-label">Issue ID</div>
                        <div class="metadata-value">${{item.issue_id}}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Style</div>
                        <div class="metadata-value">${{item.style || 'N/A'}}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Locale</div>
                        <div class="metadata-value">${{item.locale || 'en'}}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Links Found</div>
                        <div class="metadata-value">${{links.length}}</div>
                    </div>
                </div>
                
                <div class="query">
                    <div class="query-label">Query</div>
                    <div class="query-text">${{item.query || 'N/A'}}</div>
                </div>
                
                <div class="section">
                    <div class="section-title">AI Response</div>
                    <div class="response-text">${{responseText.replace(/</g, '&lt;').replace(/>/g, '&gt;')}}</div>
                </div>
                
                <div class="section">
                    <div class="section-title">Links Found</div>
                    ${{linksHtml}}
                </div>
                
                <div class="ai-reference">
                    <div class="ai-score">AI Score: ${{item.ai_score}} (${{scoreDefinitions[item.ai_score]}})</div>
                    <div class="ai-reasoning">Reasoning: ${{item.reasoning || 'N/A'}}</div>
                </div>
                
                <div class="scoring-section">
                    <label class="scoring-label">Your Score</label>
                    
                    <div class="score-definitions">
                        <div class="score-def">
                            <div class="score-def-num">1</div>
                            <div class="score-def-text">Useless - Wrong/off-topic, or links don't help</div>
                        </div>
                        <div class="score-def">
                            <div class="score-def-num">2</div>
                            <div class="score-def-text">Link-dependent - Text is navigation only; answer lives behind links</div>
                        </div>
                        <div class="score-def">
                            <div class="score-def-num">3</div>
                            <div class="score-def-text">Partially direct - Text correct but a required step/value needs a link</div>
                        </div>
                        <div class="score-def">
                            <div class="score-def-num">4</div>
                            <div class="score-def-text">Fully direct - Text alone fully solves it; links optional</div>
                        </div>
                    </div>
                    
                    <div class="score-options">
                        <div class="score-option">
                            <input type="radio" id="score1" name="human_score" value="1" 
                                   ${{humanScore === 1 ? 'checked' : ''}} onchange="updateScore()">
                            <label for="score1"><span class="score-number">1</span>Useless</label>
                        </div>
                        <div class="score-option">
                            <input type="radio" id="score2" name="human_score" value="2" 
                                   ${{humanScore === 2 ? 'checked' : ''}} onchange="updateScore()">
                            <label for="score2"><span class="score-number">2</span>Link-dependent</label>
                        </div>
                        <div class="score-option">
                            <input type="radio" id="score3" name="human_score" value="3" 
                                   ${{humanScore === 3 ? 'checked' : ''}} onchange="updateScore()">
                            <label for="score3"><span class="score-number">3</span>Partially direct</label>
                        </div>
                        <div class="score-option">
                            <input type="radio" id="score4" name="human_score" value="4" 
                                   ${{humanScore === 4 ? 'checked' : ''}} onchange="updateScore()">
                            <label for="score4"><span class="score-number">4</span>Fully direct</label>
                        </div>
                    </div>
                    
                    <div class="notes-section">
                        <label for="notes">Optional Notes</label>
                        <textarea id="notes" placeholder="Add any observations or reasoning for your score...">${{humanNotes}}</textarea>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <button class="btn-secondary" onclick="downloadProgress()">📥 Download Progress</button>
                    <button class="btn-primary" onclick="exportData()">💾 Export Data</button>
                    <button class="btn-nav" onclick="saveAndNext()">Save & Next ▶</button>
                </div>
            `;
            
            document.getElementById('content').innerHTML = html;
        }}
        
        function updateScore() {{
            const selected = document.querySelector('input[name="human_score"]:checked');
            if (selected) {{
                scoresData[currentIndex].human_score = parseInt(selected.value);
                scoresData[currentIndex].human_review_timestamp = new Date().toISOString();
            }}
        }}
        
        function saveAndNext() {{
            const score = document.querySelector('input[name="human_score"]:checked');
            if (!score) {{
                alert('Please select a score before saving.');
                return;
            }}
            
            scoresData[currentIndex].human_score = parseInt(score.value);
            scoresData[currentIndex].human_notes = document.getElementById('notes').value;
            scoresData[currentIndex].human_review_timestamp = new Date().toISOString();
            
            saveToLocalStorage();
            saveToJsonFile();
            updateProgress();
            
            if (currentIndex < scoresData.length - 1) {{
                currentIndex++;
                renderCurrentItem();
            }}
        }}
        
        function nextItem() {{
            if (currentIndex < scoresData.length - 1) {{
                currentIndex++;
                renderCurrentItem();
            }}
        }}
        
        function previousItem() {{
            if (currentIndex > 0) {{
                currentIndex--;
                renderCurrentItem();
            }}
        }}
        
        function saveToJsonFile() {{
            const dataStr = JSON.stringify(scoresData, null, 2);
            const dataBlob = new Blob([dataStr], {{ type: 'application/json' }});
            
            // Try to save using fetch (requires server)
            fetch('save-review.json', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: dataStr
            }}).catch(() => {{
                console.log('Note: Could not save to server. Use Download Progress button to save.');
            }});
        }}
        
        function downloadProgress() {{
            const dataStr = JSON.stringify(scoresData, null, 2);
            const dataBlob = new Blob([dataStr], {{ type: 'application/json' }});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'sampled_for_review.json';
            link.click();
            URL.revokeObjectURL(url);
        }}
        
        function exportData() {{
            const score = document.querySelector('input[name="human_score"]:checked');
            if (!score) {{
                showToast('Please select a score before exporting.', 'error');
                return;
            }}
            
            // Save current item
            scoresData[currentIndex].human_score = parseInt(score.value);
            scoresData[currentIndex].human_notes = document.getElementById('notes').value;
            scoresData[currentIndex].human_review_timestamp = new Date().toISOString();
            
            saveToLocalStorage();
            
            // Send to server
            const dataStr = JSON.stringify(scoresData, null, 2);
            fetch('/export-data', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: dataStr
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    showToast('✓ sampled_for_review.json updated successfully', 'success');
                }} else {{
                    showToast('Export failed: ' + data.error, 'error');
                }}
            }})
            .catch(error => {{
                console.error('Export error:', error);
                showToast('Export failed: ' + error.message, 'error');
            }});
        }}
        
        // Initialize on load
        window.addEventListener('load', init);
        
        function showToast(message, type = 'success') {{
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = `toast ${{type}}`;
            
            const icon = type === 'success' ? '✓' : '✕';
            toast.innerHTML = `
                <span class="toast-icon">${{icon}}</span>
                <span class="toast-message">${{message}}</span>
            `;
            
            container.appendChild(toast);
            
            // Auto-remove after 3 seconds
            setTimeout(() => {{
                toast.remove();
            }}, 3000);
        }}
    </script>
</body>
</html>
"""
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        # Use replace() instead of format() to avoid conflicts with {varNames} in JavaScript
        # Since we're not using .format(), unescape the double braces from the template
        html = html_content
        html = html.replace('{scores_json}', scores_json)
        html = html.replace('__TIMESTAMP_PLACEHOLDER__', timestamp)
        html = html.replace('__BATCH_BANNER_PLACEHOLDER__', batch_banner)
        # Unescape the double braces that were escaped for .format()
        html = html.replace('{{', '{').replace('}}', '}')
        f.write(html)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate interactive HTML review tool for quality scoring"
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to quality_scores_ai.json or sampled_for_review.json"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output HTML file (default: review.html in same directory as input)"
    )
    parser.add_argument(
        "--existing-review",
        type=Path,
        default=None,
        help="Path to existing sampled_for_review.json to preserve progress"
    )
    parser.add_argument(
        "--batch-id",
        type=int,
        default=None,
        help="Batch number this HTML represents (for the batch banner)"
    )
    parser.add_argument(
        "--total-batches",
        type=int,
        default=None,
        help="Total number of batches (for the batch banner)"
    )
    parser.add_argument(
        "--reviewer",
        type=str,
        default=None,
        help="Reviewer assigned to this batch (shown in the batch banner)"
    )
    
    args = parser.parse_args()
    
    try:
        # Load scores
        scores = load_scores(args.input)
        print(f"[OK] Loaded {len(scores)} scores from {args.input}")
        
        # Load full responses data to enrich with query and response_text
        full_responses = load_full_responses(args.input.parent)
        if full_responses:
            scores = enrich_with_response_data(scores, full_responses)
            print(f"[OK] Enriched with {len(full_responses)} full response entries")
        else:
            print(f"[WARNING] Could not find responses_to_score.json for enrichment")
        
        # Load existing review if provided
        existing_review = {}
        if args.existing_review:
            existing_review = load_existing_review(args.existing_review)
            print(f"[OK] Loaded {len(existing_review)} existing reviews")
            scores = merge_with_existing(scores, existing_review)
        
        # Determine output file
        if args.output is None:
            args.output = args.input.parent / "review.html"
        
        # Generate HTML
        generate_html(
            scores,
            args.output,
            batch_id=args.batch_id,
            total_batches=args.total_batches,
            reviewer=args.reviewer,
        )
        print(f"[OK] Generated review HTML: {args.output}")
        print(f"\nNext steps:")
        print(f"  1. Right-click {args.output} → Open in Browser")
        print(f"  2. Review each item and assign scores")
        print(f"  3. Click 'Export Data' to save scores to sampled_for_review.json on disk")
        print(f"     (no server? click 'Download Progress' and replace sampled_for_review.json with the downloaded file)")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
