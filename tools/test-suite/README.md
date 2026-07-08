# Test suite tools

Phase 1 path runners and helpers. Run them from the **repository root** so they resolve `docs/`, `data/`, and `results/` consistently.

| Script | Role |
|--------|------|
| `extract_queries_by_path.py` | Build `data/test-suite/*/all_queries.json` from issue markdown |
| `run_all_runners.py` | Orchestrate extraction, path runners, and analysis in sequence |
| `standardize_results_layout.py` | Normalize historical `results/` folders to the canonical layout |
| `analysis_system.py` | Build processed analysis artifacts and compare analysis runs |
| `render_analysis_dashboard.py` | Render the current WIP static HTML dashboards from processed analysis outputs |
| `localize_help_center_links.py` | Optional: normalize Help Center URLs in issue files |
| `internal-search/run-algolia-path.py` | Algolia Help Center / Dev Portal API |
| `internal-search/run-hybrid-search-path.py` | Hybrid Search API |
| `docs-assistant/run-docs-assistant-path.js` | Docs Assistant SSE API |
| `external-search/google-search-playwright/run_google_search_playwright.py` | Google SERP via Playwright |
| `external-llms/llm_runner.py` | ChatGPT / Gemini via Playwright |

Methodology and command examples: [docs/test-suite/README.md](../../docs/test-suite/README.md).
Results layout reference: [docs/test-suite/results-layout.md](../../docs/test-suite/results-layout.md).
Analysis system reference: [docs/test-suite/analysis-system.md](../../docs/test-suite/analysis-system.md).
Analysis dashboard reference: [docs/test-suite/analysis-dashboard.md](../../docs/test-suite/analysis-dashboard.md).
