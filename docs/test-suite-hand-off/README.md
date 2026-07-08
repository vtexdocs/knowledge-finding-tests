# Documentation discoverability toolkit — Hand-off guide

This folder contains the hand-off documentation for the tools that measure and improve VTEX documentation discoverability. Start here if you have no previous context.

---

## What is this?

We built a toolkit to answer one question: **"When users search for help, do they find our documentation?"**

The toolkit has two main tools and a set of dashboards:

| Component | Purpose | Guide |
| :--- | :--- | :--- |
| **Test Suite** | Simulates user searches across 5 channels and checks if the right articles appear in results | [test-suite.md](test-suite.md) |
| **Quality Scoring** | Evaluates how well AI-generated answers actually solve the user's problem (scored 1–4) | [quality-scoring.md](quality-scoring.md) |
| **Dashboards** | Visual reports showing pass rates, rankings, trends, and comparisons over time | [dashboards.md](dashboards.md) |
| **Workflow Guide** | When to run tests, what metrics mean for users, and how to improve them | [workflow-guide.md](workflow-guide.md) |

---

## How they fit together

```
┌─────────────────────────────────────────────────────────────────┐
│                            TEST SUITE                             │
│                                                                   │
│   Issue definitions   →   Runners collect data   →   Analysis     │
│   (what to test)          (from 5 channels)          (metrics)    │
└─────────────────────────────────┬─────────────────────────────────┘
                                  │  collected data + metrics
              ┌───────────────────┴───────────────────┐
              ▼                                         ▼
   ┌─────────────────────┐                   ┌──────────────────────┐
   │   QUALITY SCORING   │                   │      DASHBOARDS      │
   │  (score AI answers) │                   │  per run · timeline  │
   │  part of analysis   │                   │    · comparisons     │
   └─────────────────────┘                   └──────────────────────┘
```

1. The **Test Suite** collects search results from all channels and computes whether target articles were found.
2. **Quality Scoring** is part of the data analysis: it scores whether the collected AI *text answers* (Docs Assistant, ChatGPT, Gemini) solve the user's problem. It runs on the collected data and does **not** depend on the dashboards.
3. The **Dashboards** are a separate, optional layer that visualizes the discoverability metrics — per run, over time, or as before/after comparisons.

---

## What each tool measures

| Tool | What it measures | What it does NOT measure |
| :--- | :--- | :--- |
| **Test Suite** | Whether the correct documentation link appears in search results, and at what rank | Whether the AI text answer itself is good |
| **Quality Scoring** | Whether the AI text answer directly solves the user's problem (1–4 scale) | Link discoverability (that's the test suite's job) |

---

## Quick-start reading order

1. Read [test-suite.md](test-suite.md) to understand the core measurement system.
2. Read [dashboards.md](dashboards.md) to learn how to navigate the visual reports.
3. Read [quality-scoring.md](quality-scoring.md) when you need to evaluate AI answer quality.
4. Read [workflow-guide.md](workflow-guide.md) for practical guidance on running tests and improving each metric.

---

## Where things live in the repository

| Path | Contents |
| :--- | :--- |
| `docs/test-suite/issues/` | Test case definitions (35 issues with queries and target URLs) |
| `tools/test-suite/` | Runnable scripts for data collection and analysis |
| `tools/quality-scoring/` | Quality scoring scripts |
| `data/test-suite/` | Generated query JSON files and LLM auth state |
| `results/analysis-system/` | Analysis run outputs + **Analysis Runs dashboard (index)** |
| `results/analysis-system-comparisons/` | Comparison outputs + **Comparison Runs dashboard (index)** |
| `results/analysis-system/timeline-dashboard/` | **Timeline Dashboard (index)** |
| `.env` (repo root) | Credentials — never committed |
