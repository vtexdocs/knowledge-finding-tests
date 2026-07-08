# How to use the discoverability toolkit in your work

This guide covers when to run tests, what the metrics mean for your readers, and what actions improve each metric.

For setup and commands, see [test-suite.md](test-suite.md).
For dashboard navigation, see [dashboards.md](dashboards.md).
For quality scoring, see [quality-scoring.md](quality-scoring.md).

---

## Why use this

Publishing documentation is only half the job — if users can't find it through search, it might as well not exist. The toolkit gives you evidence to prioritize content work, prove the impact of rewrites, and catch regressions caused by platform changes outside your control.

---

## When to run tests

| Trigger | What to run | Time | Why |
| :--- | :--- | :--- | :--- |
| **After a content change** | Smoke test for the affected issue(s) | ~5 min | Confirm discoverability improved |
| **Periodic baseline** (monthly) | Full suite (all 35 issues) | 2–4 hours | Catch silent regressions from platform changes |
| **After a known infrastructure change** | Full suite + comparison | Two runs | Quantify impact of Algolia/SEO/URL changes |

**Practical tips:**

- Run single-issue smoke tests frequently — they take minutes and give immediate feedback.
- Reserve full runs for monthly baselines; they require monitoring browser windows and coordinating who runs them.
- Wait for indexing (minutes to hours) before testing a newly published change.
- If a platform change is announced (search reconfig, URL migration), run a baseline before and after — don't wait for the monthly cadence.

See [test-suite.md — How to use](test-suite.md#how-to-use) for exact commands.

> **Internal search path:** Hybrid Search is the current internal-search path used by default. The older **Algolia path is deprecated and off by default** — run it on demand with `run_all_runners.py --include algolia` only when you specifically need Algolia numbers.

---

## What each metric means for users

### Target pass rate

**In plain language:** "X% of the time, someone searching for this topic will find the right article."

A pass rate of 70% means 3 in 10 users won't find your article at all. Below 40% means the article is effectively invisible.

### MRR (Mean Reciprocal Rank)

**In plain language:** "How far down does the user scroll to find my article?"

MRR of 0.5 = typically at position 2. MRR of 0.14 = buried around position 7, where most users never look.

### Helpful pass rate

**In plain language:** "Even when users don't find THE answer, do they find something useful?"

If helpful pass is high but target pass is low, users find related content but must piece together the answer from multiple articles — a signal you need a single comprehensive article or better cross-linking.

### Locale gap (EN vs. PT vs. ES)

**In plain language:** "Is the Portuguese/Spanish experience significantly worse?"

A 20-point gap means non-English users are substantially less likely to find the documentation. Gaps above 20 points usually signal missing translations, broken URLs, or indexing issues.

### Style gap (naive vs. expert)

**In plain language:** "Are beginners struggling more to find content than power users?"

A large gap means your headings and opening content don't match the vocabulary of someone encountering the topic for the first time.

### Quality score (1–4)

**In plain language:** "Does the AI answer solve the problem without requiring the user to click links?"

Score 4 = problem solved inline. Score 1 = completely unhelpful. Average above 3.0 means AI is providing genuine value. See [quality-scoring.md](quality-scoring.md) for the full scoring methodology.

---

## How to affect each metric

### Target pass rate is low

Your article isn't appearing in results.

| Action | Why it helps |
| :--- | :--- |
| Check if your article title contains the terms users search for | Search engines match on titles and headings first |
| Verify all locale variants exist and are published | Missing translations = 0% pass for that locale |
| Confirm the URL in `target_docs` is correct and accessible | A wrong URL in ground truth creates false failures |
| Check if the article is indexed (search for it manually on the portal) | Indexing delays can make published articles invisible |

### MRR is low (article found but ranked poorly)

Your article appears but far down the list.

| Action | Why it helps |
| :--- | :--- |
| Put the direct answer in the first paragraph | Search engines weight early content more heavily |
| Use exact search terms in H2/H3 headings | Heading matches boost rank significantly |
| Check if other articles compete for the same terms | Merge overlapping content or differentiate headings |
| Add a clear meta description | Helps Google rank and display your article |

### Locale gap is large

PT or ES performs much worse than EN.

| Action | Why it helps |
| :--- | :--- |
| Verify the translated article exists and is published | Often overlooked |
| Check that the translated URL is indexed by Algolia | New translations may take days to appear |
| Compare translated headings with query terms | Different terminology won't match search queries |
| Verify navigation includes the translated version | Articles not in navigation get deprioritized |

### Style gap is large (naive queries underperform)

Experts find the article but beginners don't.

| Action | Why it helps |
| :--- | :--- |
| Use natural-language headings ("How to refund a payment" not just "Refund") | Matches how beginners search |
| Add a FAQ section with beginner-phrased questions | Direct hits on conversational queries |
| Include synonyms in the first paragraph ("refund, reversal, chargeback") | Catches vocabulary beginners use |
| Write an introductory sentence stating what the article helps you do | Gives search engines and AI context |

### Quality score is low

AI answers aren't solving the problem directly.

| Action | Why it helps |
| :--- | :--- |
| Put a direct answer in the first 2–3 sentences | AI assistants extract from the top of the article |
| Add explicit step-by-step instructions | AI models surface numbered steps reliably |
| Structure with clear sections (prerequisites, steps, result) | Helps AI compose coherent answers |
| Remove ambiguity — state things directly | Vague content produces vague AI answers |

---

## What "good" looks like

| Metric | Needs attention | Acceptable | Good |
| :--- | :--- | :--- | :--- |
| Target pass rate | Below 40% | 40–70% | Above 70% |
| MRR | Below 0.2 | 0.2–0.5 | Above 0.5 |
| Locale gap (vs. EN) | Above 20 pts | 10–20 pts | Under 10 pts |
| Style gap (naive vs. expert) | Above 20 pts | 10–20 pts | Under 10 pts |
| Quality score (avg) | Below 2.5 | 2.5–3.0 | Above 3.0 |

These benchmarks will shift as the toolkit and content mature. Use them as orientation and calibrate based on your team's goals.
