# Quality Scoring - Technical Details

Technical architecture and advanced reference.

---

## System Overview

**Three-tier approach:**
1. **LLM-as-Judge** — Automated scoring using Claude (Cursor's built-in model, zero cost)
2. **Human Validation** — Optional manual review of sample subset
3. **Automated Reporting** — Generate comprehensive analysis with metrics

**Effective Score:** `human_score` (if available) OR `ai_score`

---

## Scoring Scale (1-4)

This is the single authoritative rubric. The AI scorer and human reviewers apply
the **same decision tree** so their scores are comparable.

**Guiding principle:** assume the user cannot or will not click any links. Score
the response on how well the **text alone** solves the user's problem, and judge
links only by whether they would close the remaining gap.

### Decision tree (ask in order; stop at the first match)

1. **Is the response wrong, off-topic, or misleading — OR are the links
   irrelevant/broken so they would not help even if clicked?**
   → **Score 1 (Useless)**
2. **Is the text essentially just navigation ("see [link]") with no real answer,
   so the user must click to get anything useful?**
   → **Score 2 (Link-dependent)**
3. **Does the text give correct, useful content but still require clicking a link
   to finish the task (a required step or value lives only behind the link)?**
   → **Score 3 (Partially direct)**
4. **Can the user fully complete the task from the text alone, with links being
   optional extras?**
   → **Score 4 (Fully direct)**

| Score | Label | One-line definition |
|-------|-------|---------------------|
| **1** | Useless | Wrong/off-topic/misleading, or links don't help. |
| **2** | Link-dependent | Text is navigation only; the answer lives behind links. |
| **3** | Partially direct | Text is correct but a required step/value needs a link. |
| **4** | Fully direct | Text alone fully solves the problem; links are optional. |

### Edge cases (these trip people up)

- **Correct but link-heavy → 3, not 4.** If the content is right but the user
  still must open a link to complete the task, it is *Partially direct*.
- **Wrong but self-contained → 1, not 4.** Confidence and completeness don't earn
  points if the answer is incorrect or off-topic. Correctness gates everything.
- **Lots of links + a complete explanation → 4.** Extra reference links don't drop
  the score if the text already solves the problem on its own.
- **A little text + mostly links → 2.** If the text only points at links rather
  than explaining, it's *Link-dependent*.

---

## Detailed Scoring Guide

### Per-score detail

#### Score 1: Useless
- **Use when:** the response is irrelevant, off-topic, or factually wrong, or the
  links provided would not help even if the user clicked them.
- **Example:** User asks "How do I create a budget?" and the AI explains account deletion.

#### Score 2: Link-Dependent
- **Use when:** the text is navigation rather than explanation — the real answer
  only exists behind the links.
- **Real example:** "For comprehensive budget information, visit [link]. For API details, see [link]."

#### Score 3: Partially Direct
- **Use when:** the text is correct and useful but a required step or value is only
  available by clicking a link.
- **Real example:** "Budgets let you set spending limits. To configure over-budget alerts, visit [Settings Page]. For detailed options, see [API Reference]."

#### Score 4: Fully Direct
- **Use when:** the user can complete the task from the text alone; links (if any)
  are optional extras.
- **Real example:** "To create a budget: 1) Click Settings, 2) Select Budgets, 3) Enter name and limit, 4) Choose categories, 5) Click Save. Budgets alert at 80% spent and block transactions at 100%."

### Best practices for manual scoring

- Apply the decision tree in order on every item; don't score on overall "vibe".
- Re-read the guiding principle (assume no clicks) whenever you feel unsure.
- Spend ~1-2 minutes per item (target: 8-12 minutes for a 22-item sample — 10% of 225 scored entries, all style variants preserved).
- Add a brief note when a score is borderline or surprising — especially when you
  land on 3 because of the correct-but-link-heavy edge case.
- Take short breaks every 15-20 items to stay calibrated.

### Real Review Examples

**Example 1: "How do I add a team member?"** → **Score: 4** ✅

AI Response:
```
To add a team member, navigate to your Settings page and click the "Team" tab. 
Click "Add Member" and enter their email address. You can assign roles such as 
Admin, Editor, or Viewer. Each role has different permissions:

- Admin: Can manage billing and team settings
- Editor: Can create and modify content
- Viewer: Can only view content

After assigning a role, click "Send Invite". The new member will receive an 
email with their invitation link.
```

*User has everything needed in text alone*

---

**Example 2: "What are the API rate limits?"** → **Score: 2** ✅

AI Response:
```
API rate limits depend on your plan. Free plan users get 100 requests per minute, 
while Pro and Enterprise plans have higher limits. For detailed information on all 
plans and limit calculations, see [Rate Limits Documentation]. For more advanced 
options, consult [API Reference].
```

*Basic info in text, but user needs links for actual limits and details*

---

**Example 3: "How do I reset my password?"** → **Score: 4** ✅

AI Response:
```
Click "Forgot Password" on the login page, then check your email for a reset link. 
Click the link and enter a new password. The link expires after 24 hours. If you 
don't see the email, check your spam folder or request another reset link.
```

*Complete step-by-step with no link dependencies*

---

**Example 4: "How do I enable two-factor authentication?"** → **Score: 3** ✅

AI Response:
```
Two-factor authentication (2FA) adds extra security to your account. Go to 
Settings and click "Security". There you'll find options for 2FA. See [2FA Setup] 
for specific instructions on setting up Google Authenticator or SMS.
```

*Explains concept and where to find settings, but needs link for actual setup steps*

---

## Data Flow Architecture

```
┌─ STEPS 1-4: AUTOMATED AI PHASE ─┐

Agent asks: "Which test results directory?" [REQUIRED — no auto-detect]
  ↓
Extract responses
  ↓
Score with Claude (1-4 + reasoning)  [AI SCORING]
  ↓
Sample for human review (10%; 50% random + 50% lowest-scoring;
  deduplication by (issue_id, style) so all style variants are kept;
  backfills after pool overlap so the full 10% target is reached)
  ↓
Output: quality_scores_ai.json, sampled_for_review.json

└───────────────────────────────────┘
           ✋ WORKFLOW PAUSES HERE
     User must complete Step 5 manually

┌─ STEP 5: MANUAL REVIEW PHASE ─────┐

Agent asks: path to sampled_for_review.json? [REQUIRED — no auto-detect]
Agent asks: how many batches? [REQUIRED]
Agent asks: which port? [REQUIRED]
  ↓
User opens HTML in browser
  ↓
User reviews each sampled item  [HUMAN REVIEW]
  ↓
User sets human_score (1-4) + optional notes
  ↓
User clicks "Export Data" to save scores to disk
  ↓
Output: sampled_for_review.json (with human_score filled)

└───────────────────────────────────┘
        ⚠️ REQUIRES EXPLICIT COMMAND
    User MUST run: /generate-quality-report
         (Report does NOT auto-generate)

┌─ STEP 6: REPORT GENERATION ───────┐

Agent asks: "Which quality-scoring directory?" [REQUIRED — no auto-detect]
  ↓
User runs: /generate-quality-report
  ↓
Load quality_scores_ai.json + sampled_for_review.json
  ↓
Validate human scores are present
  ↓
Merge AI + human scores by issue ID
  ↓
Calculate agreement metrics & bias detection
  ↓
Generate comprehensive markdown report
  ↓
Output: QUALITY_REPORT.md

└───────────────────────────────────┘
```

---

## Input/Output Formats

### Input: `responses.json`
```json
[
  {
    "issue_id": "budgets-api-01",
    "response_text": "To create budgets via API...",
    "user_intent": "How do I create budgets?",
    "expected_docs": ["https://docs/budgets"],
    "provided_links": [{"title": "Budgets", "url": "https://..."}],
    "path_variant": "docs-assistant.api",
    "locale": "en",
    "style": "naive"
  }
]
```

### Output: `quality_scores_ai.json`
```json
[
  {
    "issue_id": "budgets-api-01",
    "ai_score": 4,
    "human_score": null,
    "ai_reasoning": "Response directly explains API usage with examples...",
    "found_expected_doc": true,
    "timestamp": "2026-04-22T14:30:00+00:00"
  }
]
```

### Output: `QUALITY_REPORT.md`
Auto-generated markdown with:
- Executive summary
- Score distributions
- Agreement metrics
- Bias detection
- Key findings
- Calibration insights

---

## Filtering Strategies

### Quantity Control

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `--limit N` | Score first N responses | `--limit 50` → score 0-50 |
| `--offset N` | Skip first N responses | `--offset 100 --limit 50` → score 100-150 |
| `--percent N` | Random N% sample | `--percent 25` → ~25% random |

**Combined example:** Use the workflow to score responses with custom parameters, or use `/quality-scoring-workflow` to run the full pipeline.

### Issue Selection

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `--issues "id1,id2"` | Specific issues | `--issues "issue1,issue2,issue3"` |
| `--issues-file FILE` | Load from file | `--issues-file priority-issues.txt` |
| `--exclude-issues "id1,id2"` | Skip specific issues | `--exclude-issues "broken-01,debug-02"` |

**File format (one ID per line):**
```
budgets-api-01
orders-api-01
audit-search-01
```

### Sampling for Review

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `--sample-percent N` | Sample N% for human review | `--sample-percent 10` → review ~10% |

---

## Directory Versioning

Workflow outputs organized in timestamped subdirectories to preserve history.

### Directory Format
```
quality-scoring-YYYY-MM-DDTHH-MM-SSZ
```

**Example:** `quality-scoring-2026-04-22T10-30-45Z`
- Year: 2026, Month: 04, Day: 22
- Hour: 10 UTC, Minute: 30, Second: 45
- Timezone: Z (always UTC)

### Multiple Runs (Preserved)
```
results/test-dir/
├── quality-scoring-2026-04-22T08-00-55Z/   ← Run 1 (earliest)
│   ├── quality_scores_ai.json
│   └── QUALITY_REPORT.md
├── quality-scoring-2026-04-22T10-30-45Z/   ← Run 2
│   ├── quality_scores_ai.json
│   └── QUALITY_REPORT.md
└── quality-scoring-2026-04-22T12-00-50Z/   ← Run 3 (latest)
    ├── quality_scores_ai.json
    └── QUALITY_REPORT.md
```

### Accessing Previous Results
```bash
# List all runs (chronologically sorted)
ls -1 results/test-dir/quality-scoring-*/

# Get specific run
cat quality-scoring-2026-04-22T10-30-45Z/quality_scores_ai.json

# Compare reports
diff quality-scoring-2026-04-22T08-00-55Z/QUALITY_REPORT.md \
     quality-scoring-2026-04-22T10-30-45Z/QUALITY_REPORT.md
```

**Best practices:**
- Never delete timestamped directories (preserve history)
- Keep 3-5 most recent runs for comparison
- Archive old runs if >20 accumulate

---

## Cost & Performance

| Metric | Value |
|--------|-------|
| **Cost** | $0 (Cursor's built-in Claude) |
| **Speed** | 5-10 minutes for 300 responses |
| **Model** | Claude 3.5 Haiku class |
| **Accuracy** | High (LLM-based evaluation) |
| **Batch size** | No limit (local processing) |
| **Rate limits** | None (built-in Claude) |

**Performance tips:**
- Filtering applied before scoring (faster for large datasets)
- Statistical sampling (`--percent`) faster than scoring all
- Pagination (`--offset + --limit`) efficient for 1000+ items
- Typical: 300 responses in 5-10 minutes

---

## Implementation Approaches

### Cursor Agent Workflow (Recommended - 2 Phases)

**Phase A: Automated**
- Agent asks for the test results directory (always required — no auto-detect)
- Uses Cursor's built-in Claude model for scoring (zero API costs)
- Samples 10% for human review; all style variants (`naive`, `familiar`, `expert`) per issue are kept — deduplication is by `(issue_id, style)` so the full target count is reached
- Generates interactive HTML review tool

**Phase B: Manual + Automated Report**
- Agent asks for path, number of batches, and port before launching (all required — no auto-detect)
- User opens HTML review tool in browser
- Browser-based form interface with scoring controls
- Interactive tool auto-saves progress via "Export Data" button
- Agent asks for the quality-scoring run directory before generating the report (always required — no auto-detect)
- Run `/generate-quality-report` to produce the final report after human scores are complete
- Compares AI vs human agreement

### HTML Review Tool

- **Browser-based interface** - Works offline
- **Full content visibility** - Response text, links, query visible together
- **Interactive form** - Radio button scoring (1-4)
- **Auto-save with server** - Scores saved to disk when clicking "Export Data" ("Download Progress" saves a local backup copy)
- **Browser localStorage** - Auto-backup of progress in case of crashes
- **Download/upload fallback** - Manual JSON download if server unavailable
- **Progress bar and navigation** - Skip around or proceed linearly
- **No technical knowledge required** - Just click scores, no JSON editing

### Report Generation (Helper Script)

- Python 3.6+ required (no dependencies)
- Automates final report creation after human scoring
- Merges AI and human scores (from Phase B)
- Calculates all metrics
- Zero external dependencies

---

## Distributed Batch Review

For large samples, the human review (Step 5) can be split across multiple
reviewers who score in parallel. This is layered on top of the existing review
tool and is fully backward compatible — without batch arguments, review behaves
exactly as a single-reviewer session.

### Architecture

```
sampled_for_review.json
  ↓  /generate-review-tool --batch-size N (or --num-batches N)
  ↓  (sequential, non-overlapping assignment)
batches_manifest.json + batch-1/ … batch-K/
  ↓  /generate-review-tool --batch-id i --port 800i   (one server per reviewer)
batch-i/sampled_for_review_batch_i.json   [human_score filled per batch]
  ↓  /merge-batches   (dedupe + validation, writes back to sampled_for_review.json)
sampled_for_review.json   [now contains every batch's human_score]
  ↓  /generate-quality-report --run-dir <run-dir>
QUALITY_REPORT.md
```

`/merge-batches` writes the consolidated scores back into the run's
`sampled_for_review.json`, so `/generate-quality-report --run-dir <run-dir>` picks
it up with no extra flags. You can still pass `--human-scores <file>` explicitly to
override.

### `batches_manifest.json`

The manifest is the source of truth for batch assignments and is consumed by
`/batch-status` and `/merge-batches`:

```json
{
  "total_items": 5,
  "batches": [
    {
      "batch_id": 1,
      "reviewer": "Alice",
      "item_count": 2,
      "data_file": "batch-1/sampled_for_review_batch_1.json"
    }
  ]
}
```

### Status & Merge

- **`batch_status.py`** — Reads the manifest, counts items with a `human_score`
  in each batch data file, and classifies each batch as COMPLETE / IN PROGRESS /
  PENDING / MISSING, plus an overall progress percentage.
- **`merge_batches.py`** — Loads every batch data file, merges items into a
  single list, and validates against duplicate `issue_id`s, missing batch files,
  and unscored items. Exit code `0` (clean), `2` (duplicates/missing files), or
  `1` (manifest unreadable). It writes the consolidated scores back into the run's
  `sampled_for_review.json`, which is drop-in compatible with
  `generate_quality_report.py`.

### Concurrency

Each reviewer runs their own `review-server.py` instance on a distinct `--port`,
writing only to their batch's data file. Because assignment is sequential and
per-batch files are isolated, parallel scoring never conflicts.

---

## Report Metrics

Auto-generated `QUALITY_REPORT.md` includes:

### Executive Summary
- Report date & timestamp
- Total responses scored
- Count of human reviews (%)
- AI average score
- Human average score (if available)

### Distributions
- AI score breakdown (1-4) with percentages
- Human score breakdown (if available)

### Agreement Analysis
- Exact match percentage
- Within ±1 point percentage
- Disagreements (with details)

### Calibration Insights
- Scorer bias detection (AI vs Human)
- Average score difference
- Recommendations for recalibration

### Estimated Quality
- Extrapolated percentages for full batch
- Estimated average score

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "No issues found" | Wrong issue ID format | Check case sensitivity, exact spelling |
| "Invalid --limit value" | Non-integer value | Use positive integers (e.g., 50) |
| "File not found" | Wrong path | Use absolute path or verify relative path |
| "Invalid JSON" | Malformed file | Validate with online JSON validator |
| "Python error" | Missing package | Set `ANTHROPIC_API_KEY` for Python API |
| "Cannot connect to server" | Port 8000 in use | Try different port or use manual HTML mode |
| "Scores not saving" | File permissions | Verify write access to directory |

---

## Creating Issue Files

### From command line:
```bash
echo "issue-1" > issues.txt
echo "issue-2" >> issues.txt
echo "issue-3" >> issues.txt
```

### From CSV export:
```bash
cut -d',' -f1 issues.csv | tail -n +2 > issues.txt
```

### From JSON responses:
```bash
jq -r '.[].issue_id' responses.json > issues.txt
```

---

## Project Structure

```
.cursor/skills/
├── generate-review-tool/SKILL.md      [HTML review skill (single & batch)]
├── batch-status/SKILL.md              [Batch progress reporting]
├── merge-batches/SKILL.md             [Batch consolidation]
└── quality-scoring-workflow/SKILL.md  [Complete pipeline]

docs/quality-scoring/
├── README.md                       [Start here]
├── CURSOR_COMMANDS.md              [Skills reference]
└── quality-scoring.md              [This file - technical details]

tools/quality-scoring/
├── generate_review_html.py         [HTML review tool generator (batch banner)]
├── generate_quality_report.py      [Report automation]
├── sample_responses_for_review.py  [Sampling strategy — dedup by (issue_id, style), not issue_id alone]
├── launch-review.py                [Review server launcher (single & batch)]
├── review-server.py                [HTTP server for auto-save (--port)]
├── batch_status.py                 [Batch progress reporting]
├── merge_batches.py                [Batch consolidation]
└── ...                             [Other scripts]

results/
└── <test-dir>/
    └── quality-scoring-YYYY-MM-DDTHH-MM-SSZ/
        ├── quality_scores_ai.json
        ├── review.html
        ├── sampled_for_review.json             [batch reviews merged back here]
        ├── QUALITY_REPORT.md
        ├── batches_manifest.json               [batch mode only]
        └── batch-N/                            [batch mode only]
            ├── sampled_for_review_batch_N.json
            └── review_batch_N.html
```

---

## Environment Variables

**For Python API only:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**For Cursor skills:** No setup needed (uses built-in Claude)

---

## See Also

- [README.md](README.md) — Quick start & common workflows
- [CURSOR_COMMANDS.md](CURSOR_COMMANDS.md) — Complete skills reference
- [`batch-status`](../../.cursor/skills/batch-status/SKILL.md) — Track progress across review batches
- [`merge-batches`](../../.cursor/skills/merge-batches/SKILL.md) — Consolidate scored batches into one file

---

**Status:** Production-ready  
**Last Updated:** Jun 23, 2026  
**Approach:** Cursor Agent + Built-in Claude + Interactive HTML Reviewer (single & distributed batch) + Automated Reporting
