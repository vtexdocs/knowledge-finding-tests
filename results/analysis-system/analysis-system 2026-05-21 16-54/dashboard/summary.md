# Latest Analysis Run

Run analysis-system 2026-05-21 16-54 | 35 issues | 1,455 queries | 56.03% target pass

**Generated:** 2026-05-27T18:43:29.101382+00:00

## Headline metrics

- **Target pass rate:** 56.03% — Success rate counting only exact `target_doc` matches.
- **Target pass any locale:** 60.86% — Target-doc success counting different-locale target docs too.
- **Target MRR:** 0.390777 — Reciprocal rank of the best target doc found.
- **Helpful pass rate:** 70.89% — Success rate counting any relevant non-`unrelated` link type.
- **Any relevant rate:** 65.31% — Target or helpful docs appeared in returned links.
- **Any relevant any locale:** 70.89% — Target/helpful docs appeared, including different-locale variants.
- **Not available:** 129 — Queries excluded from denominators due to path/locale applicability.

## Highlights

- **Best path:** internal-search.hybrid-search / PT — 84.21% target pass.
- **Weakest path:** internal-search.algolia-helpcenter / ES — 21.05% target pass.
- **Best locale:** PT — 65.79% target pass and 0.472386 MRR.
- **Weakest locale:** ES — 47.95% target pass.
- **Strongest query style:** familiar — 57.69% target pass.
- **Hardest issue:** product-excel-01 — 53 misses across 54 tested styles.

## Locale gap vs EN

- **Largest ES gap:** llm.chatgpt (-27.62% vs EN)

## Warnings

- **Low nonempty response ratio:** Some sources returned empty results for more than 10% of queries. Review collection logs before trusting path-level metrics.
  - internal-search.algolia-devportal (52.4% nonempty)
- **Queries marked not available:** 129 queries were excluded from denominators because the path/locale combination does not apply. See the Not available overview card.

## Selected source runs

- `docs-assistant.api` → `results\docs-assistant\api\docs-assistant 2026-05-20 10-56` (healthy: Yes, full: Yes)
- `external-search.google-search-playwright` → `results\external-search\google-search-playwright\google-search-playwright 2026-05-20 10-56` (healthy: Yes, full: Yes)
- `internal-search.algolia-devportal` → `results\internal-search\algolia-devportal\algolia-devportal 2026-05-19 15-54` (healthy: Yes, full: Yes)
- `internal-search.algolia-helpcenter` → `results\internal-search\algolia-helpcenter\algolia-helpcenter 2026-05-19 15-54` (healthy: Yes, full: Yes)
- `internal-search.hybrid-search` → `results\internal-search\hybrid-search\hybrid-search 2026-05-19 15-57` (healthy: Yes, full: Yes)
- `llm.chatgpt` → `results\external-llms\chatgpt\external-llms-chatgpt 2026-05-20 14-31` (healthy: Yes, full: Yes)
- `llm.gemini` → `results\external-llms\gemini\external-llms-gemini 2026-05-20 20-28` (healthy: Yes, full: Yes)

## Dashboard

Open `index.html` in this folder for the full interactive dashboard.

## Notes

- Phase 1 evaluates link and rank only. Answer quality scoring is intentionally excluded.
- Internal search metrics use top 7 links; all other path families use all returned links.
- This dashboard is rendered from processed analysis outputs, not runner-level summaries.
