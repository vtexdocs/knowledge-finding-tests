# Cursor Skills Reference

Complete guide to the quality-scoring workflows.

> **These workflows ship as Cursor _skills_, not `/` commands.** Each `/<name>` below
> corresponds to the skill in [`.cursor/skills/<name>/`](../../.cursor/skills/). To run one,
> ask the Cursor agent for the task (e.g. _"run the quality-scoring-workflow skill"_) — the
> agent loads the matching `SKILL.md`. The `/<name>` shorthand is kept here only as a stable
> label for each workflow; the parameters and behavior described below are unchanged.

---

## Commands Overview

### Primary Workflow
| Command | Purpose | Output |
|---------|---------|--------|
| **`/quality-scoring-workflow`** | **Complete end-to-end pipeline (6 steps)** | All outputs (scores, samples, report) |

### Component Commands (use individually or via workflow)
| Command | Purpose | Output |
|---------|---------|--------|
| `/generate-review-tool` | Interactive HTML review interface (single or batched) | `review.html` (browser-based scoring) |

### Batch Review Commands (distributed human scoring)
| Command | Purpose | Output |
|---------|---------|--------|
| `/batch-status` | Report scoring progress across review batches | Status table (per-batch + overall %) |
| `/merge-batches` | Consolidate scored batches back into the sample file | updated `sampled_for_review.json` |

### Supporting Tools
| Tool | Purpose | Output |
|------|---------|--------|
| `/generate-quality-report` | Auto-generate analysis report | `QUALITY_REPORT.md` |

---

## 1. `/quality-scoring-workflow` (PRIMARY COMMAND)

Complete end-to-end pipeline with 6 interactive steps. **Start here for most use cases.**

### Usage
```bash
/quality-scoring-workflow
```

### What It Does

**Phase A (Automated):** Steps 1-4 (~5-10 minutes)
1. **Ask** — Agent asks for the test results directory (always required — no auto-detect)
2. **Extract** — Prepare responses for scoring
3. **Score** — AI scoring with Claude
4. **Sample** — Select 10% of items for human review (50% random + 50% lowest-scoring; all style variants kept per issue; backfills after pool overlap so the full 10% target is reached)

**→ Workflow pauses here for manual work ←**

**Phase B (Manual Review + Report):** Steps 5-6 (~10-15 minutes)
5. **Manual Scoring** — You review sampled items (choose your method):
   - Option A: Use `/generate-review-tool` for interactive HTML interface (recommended)
   - Option B: Edit `sampled_for_review.json` directly in your text editor
   - After completing manual scores, proceed to generate the report

6. **Report Generation** — Generate report by running `/generate-quality-report` (~1 minute)
   - User runs: `/generate-quality-report --run-dir "quality-scoring-YYYY-MM-DDTHH-MM-SSZ"`
   - Merge AI and human scores
   - Generate quality report with metrics
   - Compare AI vs human agreement

### Outputs
- `quality_scores_ai.json` — All AI scores
- `sampled_for_review.json` — Sample prepared for human review (human_score values added during Step 5)
- `QUALITY_REPORT.md` — Final analysis report (AI vs Human comparison, created by `/generate-quality-report`)

**Note:** Human scores are added directly to `sampled_for_review.json` during Step 5 (when you review using `/generate-review-tool`).

### Interactive Steps
Follow prompts for Steps 1-4. At Step 5, the workflow pauses and guides you to review sampled items manually.

### Parameters
The agent always asks for the test results directory interactively. No flags are needed for the basic workflow.

```bash
# Change sampling percentage (default: 10%)
/quality-scoring-workflow --percent 20
```

---

## 2. `/generate-review-tool`

Generate interactive HTML review tool for scoring sampled responses in your browser. **Best option for human review.**

### Required Inputs

The agent always asks for these three things before doing anything:

1. **Path to `sampled_for_review.json`** — no auto-detect
2. **Number of batches** — use 1 for a single reviewer, higher to distribute across multiple reviewers
3. **Port** — the port the review server will run on (e.g. `8000`)

### Parameters
- `--input FILE` — Path to `sampled_for_review.json` (**required** — agent asks if not provided)
- `--num-batches N` — Number of equal batches to split into (**required** — agent asks if not provided)
- `--port N` — Port for the review server (**required** — agent asks if not provided)
- `--batch-size N` — Alternative to `--num-batches`: split into batches of N items each
- `--reviewer NAME` — Assign a reviewer to a batch (repeat in order, one per batch)
- `--batch-id N` — Launch the review server for a specific, already-generated batch
- `--output FILE` — Output HTML file (default: `review.html`)
- `--no-server` — Generate HTML only, don't start server

### Key Features
- **Browser-based interface** - Works offline
- **Full content visibility** - Response text, links, query visible together
- **Radio button scoring** - Interactive 1-4 scoring
- **Optional notes** - Add context for edge cases
- **Auto-save with server** - Click "Export Data" → scores saved to disk ("Download Progress" saves a local backup copy)
- **Browser backup** - localStorage preserves progress in case of crashes
- **Progress tracking** - Progress bar and item counter
- **Navigation** - Previous/Next buttons, skip around freely
- **Form validation** - Can't submit without selecting a score

### Auto-Save Workflow (Recommended)

1. **Start the review** (agent asks for path, batches, and port):
   ```bash
   /generate-review-tool
   ```
   
2. **Browser opens at localhost:8000** with review interface

3. **Score each item:**
   - Read the AI response
   - Consider the AI score and reasoning
   - Click your score (1-4)
   - Optionally add notes
   - Proceed to next item

4. **Save scores:**
   - When done, click the "Export Data" button
   - Server automatically saves scores to `sampled_for_review.json`
   - Browser shows: "sampled_for_review.json updated successfully"
   - **No manual download/upload needed!**

5. **Stop server:**
   ```bash
   Ctrl+C
   # Scores are already saved
   ```

### Manual Workflow (No Server)

If you can't run the server, add `--no-server` when the agent asks for inputs (or pass it as a flag):

```bash
/generate-review-tool --input sampled_for_review.json --num-batches 1 --port 8000 --no-server
# Opens review.html only
```

1. Double-click `review.html` to open in browser
2. Score each item (1-4)
3. Click "Download Progress" to download file
4. Browser downloads `sampled_for_review.json`
5. Replace the original file with downloaded copy

### Troubleshooting

**"Cannot connect to server"**
- Verify `/generate-review-tool` is running
- Check terminal for error messages
- Try different port: Edit `review-server.py` line with `PORT = 8000` to `PORT = 8001`

**"Port 8000 already in use"**
- Another process is using the port
- Find: `netstat -ano | findstr :8000` (Windows) or `lsof -i :8000` (Mac/Linux)
- Use different port or stop the other process

**"Scores not saving"**
- Check browser console (F12) for network errors
- Verify `sampled_for_review.json` is writable (not locked)
- Try manual mode: Use "Download Progress" and upload manually

**"Browser didn't open"**
- Server is running but browser didn't launch
- Manually go to: `http://localhost:8000`

**"I closed browser, want to resume"**
- Run command again - scores are restored from localStorage
- If using server, scores were saved to disk already

### Output
- `review.html` — Browser UI with embedded scoring interface
- Scores saved to `sampled_for_review.json` (via server) or downloaded manually

### Batch Mode (distributed human scoring)

For large reviews, split the work across multiple reviewers so each can score
their portion independently and in parallel.

**1. Generate batches** — Splits `sampled_for_review.json` into per-batch
subdirectories, each with its own data file and HTML interface, plus a
`batches_manifest.json` that tracks assignments and progress. The agent will ask
for path, num-batches, and port if not provided as flags:
```bash
# Batches of 10 items each, assigned to reviewers in order
/generate-review-tool \
  --input "results/.../quality-scoring-YYYY-MM-DDTHH-MM-SSZ/sampled_for_review.json" \
  --batch-size 10 --port 8001 \
  --reviewer Alice --reviewer Bob

# Or split into a fixed number of equal batches
/generate-review-tool \
  --input "results/.../quality-scoring-YYYY-MM-DDTHH-MM-SSZ/sampled_for_review.json" \
  --num-batches 5 --port 8001
```
This creates:
```
quality-scoring-YYYY-MM-DDTHH-MM-SSZ/
├── batches_manifest.json
├── batch-1/
│   ├── sampled_for_review_batch_1.json
│   └── review_batch_1.html
├── batch-2/
│   ├── sampled_for_review_batch_2.json
│   └── review_batch_2.html
└── ...
```

**2. Launch a batch for review** — Each reviewer launches their batch on a
distinct port. The UI header shows "Batch X of N" and the reviewer name; scores
auto-save to that batch's own data file:
```bash
/generate-review-tool --batch-id 1 --port 8001   # Alice
/generate-review-tool --batch-id 2 --port 8002   # Bob
```

**3. Track progress** — See per-batch and overall completion at any time with
[`/batch-status`](#4-batch-status).

**4. Consolidate results** — Merge all scored batches with
[`/merge-batches`](#5-merge-batches) back into the run's `sampled_for_review.json`,
which plugs directly into `/generate-quality-report`.

**Notes:**
- `--num-batches`, `--input`, and `--port` are always required — agent asks if not provided as flags.
- Item assignment is sequential, so no item is duplicated or omitted by default.
- Each batch is self-contained: full query, response text, links, AI reference, and scoring UI.

---

## 3. `/generate-quality-report`

Automatically generate comprehensive analysis reports from AI and human scores.

### Required Input

The agent always asks for the quality-scoring run directory before doing anything — no auto-detect.

```bash
/generate-quality-report
# → Agent asks: "Which quality-scoring directory should I use?"
# → User: results/docs-assistant/api/docs-assistant 2026-03-17 16-23/quality-scoring-2026-06-23T12-52-44Z
```

The run directory infers all three paths automatically:
- `--ai-scores` → `<run-dir>/quality_scores_ai.json`
- `--human-scores` → `<run-dir>/sampled_for_review.json` (batch reviews are merged back into this file by `/merge-batches`)
- `--output` → `<run-dir>/QUALITY_REPORT.md`

### Parameters
- `--run-dir DIR` — Run directory (**required** — agent asks if not provided as a flag)
- `--ai-scores FILE` — Override inferred AI scores path
- `--human-scores FILE` — Override inferred human scores path
- `--output FILE` — Override inferred output path

### Report Includes
- Executive summary (dates, counts, averages)
- Score distributions (1-4 breakdown)
- Human-AI agreement metrics
- Bias detection between scorers
- Key findings & recommendations
- Estimated full batch quality

### Examples
```bash
# Standard: provide the run directory (agent asks if not given as flag)
/generate-quality-report --run-dir "results/docs-assistant/api/docs-assistant 2026-03-17 16-23/quality-scoring-2026-06-23T12-52-44Z"

# Batch review: /merge-batches writes scores into sampled_for_review.json, so --run-dir just works
/generate-quality-report --run-dir "results/.../quality-scoring-YYYY-MM-DDTHH-MM-SSZ"
```

---

## 4. `/batch-status`

Report scoring progress across review batches created by `/generate-review-tool`
in batch mode. Shows per-batch and overall completion so coordinators can see
what work remains and who is responsible for it.

### Usage
```bash
# Auto-detect latest manifest
/batch-status

# Specific manifest
/batch-status --manifest "results/.../quality-scoring-YYYY-MM-DDTHH-MM-SSZ/batches_manifest.json"
```

### Parameters
- `--manifest FILE` — Path to `batches_manifest.json` (auto-detects latest if omitted)

### Batch Classification
- **COMPLETE** — all items scored
- **IN PROGRESS** — some items scored
- **PENDING** — no items scored
- **MISSING** — batch data file not found

### Example Output
```
============================================================
BATCH STATUS REPORT
============================================================
Batch 1/3 (Alice)               :   2/2   items ✓ COMPLETE
Batch 2/3 (Bob)                 :   0/2   items ⏸ PENDING
Batch 3/3 (Charlie)             :   0/1   items ⏸ PENDING
------------------------------------------------------------
Overall Progress                :   2/5   items (40%)
============================================================
```

---

## 5. `/merge-batches`

Consolidate scored review batches back into the run's existing
`sampled_for_review.json`, ready for `/generate-quality-report`. Validates that no
items are duplicated or missing and warns about incomplete scoring.

### Usage
```bash
# Auto-detect latest manifest, write back to its sampled_for_review.json
/merge-batches

# Specific manifest (writes back to the run's sampled_for_review.json)
/merge-batches --manifest "results/.../batches_manifest.json"
```

### Parameters
- `--manifest FILE` — Path to `batches_manifest.json` (auto-detects latest if omitted)
- `--output FILE` — Custom output path (default: the run's existing `sampled_for_review.json` next to manifest)

### Validation & Exit Codes
- Detects duplicate `issue_id` entries across batches (skipped + warned)
- Warns about missing batch data files and items without a `human_score`
- Compares merged count against the manifest's `total_items`

| Exit code | Meaning |
|-----------|---------|
| `0` | Merge succeeded with no blocking issues |
| `2` | Merge completed but found duplicates or missing batch files (review warnings) |
| `1` | Could not read the manifest or no batches found |

---

## Scoring Scale

The authoritative rubric (decision tree, edge cases, and examples) lives in
[quality-scoring.md](quality-scoring.md#scoring-scale-1-4). Assume the user will
not click links and score how well the text alone solves the task.

Quick reference:

| Score | Label | One-line definition |
|-------|-------|---------------------|
| **1** | Useless | Wrong/off-topic/misleading, or links don't help |
| **2** | Link-dependent | Text is navigation only; answer lives behind links |
| **3** | Partially direct | Text correct but a required step/value needs a link |
| **4** | Fully direct | Text alone fully solves the problem; links optional |

---

## Common Workflows

### Full: Complete End-to-End Pipeline
```bash
# Each command asks for required inputs before acting — no auto-detect at any step.
/quality-scoring-workflow          # → asks: test results directory?
/generate-review-tool              # → asks: sampled_for_review.json path? batches? port?
/generate-quality-report           # → asks: quality-scoring run directory?
# Total: ~15-25 min
```

### Just Review: Use Pre-Scored Data
```bash
/generate-review-tool \
  --input "results/.../quality-scoring-YYYY-MM-DDTHH-MM-SSZ/sampled_for_review.json" \
  --num-batches 1 --port 8000
# 8-12 min: Interactive HTML review
```

### Distributed: Split Review Across Reviewers
```bash
# 1. Generate batches assigned to reviewers (agent asks for path, batches, port)
/generate-review-tool \
  --input "results/.../quality-scoring-YYYY-MM-DDTHH-MM-SSZ/sampled_for_review.json" \
  --batch-size 10 --port 8001 \
  --reviewer Alice --reviewer Bob

# 2. Each reviewer launches their batch on a distinct port
/generate-review-tool --batch-id 1 --port 8001   # Alice
/generate-review-tool --batch-id 2 --port 8002   # Bob

# 3. Track progress at any time
/batch-status

# 4. Merge completed batches into one file
/merge-batches

# 5. Generate the final report (run-dir uses the updated sampled_for_review.json)
/generate-quality-report --run-dir "results/.../quality-scoring-YYYY-MM-DDTHH-MM-SSZ"
```

---

## Error Handling

| Error | Solution |
|-------|----------|
| "File not found" | Check file path, use absolute path if needed |
| "Invalid JSON" | Validate JSON format (use online validator) |
| "Skill didn't run" | Ask the agent to run the skill by name; check it exists under `.cursor/skills/` |
| "Claude not responding" | Retry in a moment, Cursor Agent may be busy |

---

## Tips & Tricks

- **Sampling strategies:**
  - Random: General calibration
  - Low-scoring: Find AI mistakes
  - Combined (default): Balanced approach

- **Quantity control:**
  - Use `--limit` for quick tests on small subsets
  - Use `--percent` for representative random sampling
  - Use `--offset + --limit` to process large datasets in chunks
  - Use `--issues` for focused analysis on specific cases

- **Issue selection:**
  - Create issue file with one ID per line: `echo "issue1" > issues.txt`
  - Export from Jira/spreadsheet as CSV, extract ID column
  - Use `--exclude-issues` to skip known problematic cases during testing

- **Efficient workflows:**
  - Test filtering with `--limit 5` first to verify query
  - Use `--percent 10` for statistical sampling
  - Combine `--issues-file` with `--sample-percent 50` for focused review

- **Performance:**
  - Typical: 300 responses in 5-10 minutes
  - Speed depends on Cursor Agent responsiveness
  - No API rate limits (using built-in Claude)
  - Filtering happens before scoring (faster for large datasets)

---

## Advanced Usage Examples

### Using Pre-Extracted Responses
If you already have responses extracted, use them directly:
```bash
/quality-scoring-workflow --input "responses.json"
# Uses your pre-extracted responses for scoring
```

### Customizing the Review Process
After the workflow completes scoring (Step 4), you can choose your review method:

**Interactive HTML Review (Recommended):**
```bash
/generate-review-tool --input sampled_for_review.json
# Browser-based review with auto-save (8-12 minutes)
```

**Manual JSON Edit:**
```
Edit sampled_for_review.json directly in your text editor
Set 'human_score' (1-4) for each item, save the file
```

### Create Issue File for Selection

If you want to prepare a file with specific issues to focus on (for future analysis), you can create one:

**File format (one ID per line):**
```
budgets-api-01
orders-api-01
audit-search-01
shopee-integration-01
```

**From command line:**
```bash
echo "budgets-api-01" > priority-issues.txt
echo "orders-api-01" >> priority-issues.txt
```

**From CSV:**
```bash
cut -d',' -f1 issues.csv | tail -n +2 > issues.txt
```

**From JSON:**
```bash
jq -r '.[].issue_id' responses.json > issues.txt
```

---

## Workflow Notes

### For `/quality-scoring-workflow`

The agent asks for the test results directory before starting. No flags are required.

### For `/generate-review-tool`

The agent always asks for three required inputs before doing anything:
- Path to `sampled_for_review.json`
- Number of batches (`1` for single reviewer)
- Port (e.g. `8000`)

### For `/generate-quality-report`

The agent asks for the quality-scoring run directory before starting. The command infers all file paths from it.

---

## Directory Versioning

Each `/quality-scoring-workflow` run writes its outputs to a unique timestamped
directory (`quality-scoring-YYYY-MM-DDTHH-MM-SSZ`, UTC). For the full versioning
scheme, directory layout, and best practices, see
[quality-scoring.md](quality-scoring.md#directory-versioning).

**Command-specific note:** when you use `/generate-review-tool` directly (not via
the workflow), files are saved to your current working directory with no
automatic versioning — move them into a timestamped directory to preserve them.

---

## See Also

- [README.md](README.md) — Overview & quick start
- [quality-scoring.md](quality-scoring.md) — Technical details & scoring guide
- [`generate-review-tool`](../../.cursor/skills/generate-review-tool/SKILL.md) — Review tool (single & batch mode)
- [`batch-status`](../../.cursor/skills/batch-status/SKILL.md) — Track progress across review batches
- [`merge-batches`](../../.cursor/skills/merge-batches/SKILL.md) — Consolidate scored batches into one file
- All quality-scoring skills live in the [`.cursor/skills/`](../../.cursor/skills/) directory

---

**Last Updated:** Jun 23, 2026  
**Primary Command:** `/quality-scoring-workflow`  
**Component Commands:** `/generate-review-tool` (single & batch), `/batch-status`, `/merge-batches`, `/generate-quality-report`  
**Cost:** $0
