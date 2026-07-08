# Run API paths — reference

Detailed material for the `run-api-paths` skill: API details, output JSON shape, report structure, path comparison, script behavior, error handling, and full examples.

## Script behavior (both runners)

1. **Load environment variables** — from `.env` at project root, falling back to system env.
2. **Load test suite queries** — primary `data/test-suite/internal-search/all_queries.json`; fallback: individual `.md` files in `docs/test-suite/issues/`. Extract `issue_id`, `target_doc_url`, and queries; apply the issue filter.
3. **Run queries against the API** — for each issue and each `query_internal` query: call the API, take top N results, map to `{ rank, url, title }`, check whether `target_doc_url` appears, record rank if found.
4. **Progress tracking** — `[Issue X/Y] issue_id`; per query `[Z/3 (style)] query_text → N results | Target doc: [found at rank R | not found]`.

## Output JSON (unified format)

```json
{
  "run_id": "hybrid-search-run-2026-03-06-153045",
  "path": "hybrid-search",
  "timestamp": "2026-03-06T15:30:45Z",
  "config": { "api_url": "http://localhost:3000", "locale": "en", "top_n": 10, "issues_count": 29, "queries_count": 87 },
  "summary_by_issue": [
    {
      "issue_id": "conditions-payment-01",
      "target_doc_url": "https://help.vtex.com/en/tutorial/special-conditions",
      "results_by_style": {
        "naive": { "found": false, "rank": null },
        "familiar": { "found": true, "rank": 3 },
        "expert": { "found": true, "rank": 1 }
      },
      "best_rank": 1, "worst_rank": 3, "pass": true
    }
  ],
  "errors": [],
  "results": []
}
```

File locations:
- Algolia Help Center: `results/internal-search/algolia-helpcenter/{run_id}.json`
- Algolia Dev Portal: `results/internal-search/algolia-devportal/{run_id}.json`
- Hybrid Search: `results/internal-search/hybrid-search/{run_id}.json`

## Report structure

### Per-index analysis reports (Algolia & Hybrid Search)
- **Header:** run ID, date, path, API endpoint/index, issues/queries count, top N.
- **Overall performance:** pass rate, average rank when found, issues with ≥1 style found, issues fully failing.
- **Performance by query style:** table (style, found, not found, avg rank, pass rate).
- **Issues requiring attention:** failed all styles; best performers.
- **Errors encountered:** table or "No errors".
- **Detailed results by issue:** table (issue ID, target doc, naive, familiar, expert, best rank) with ✓/✗.

### Internal-search comparison report (Algolia + Hybrid Search combined)
- **Header:** report date, issues tested, top N.
- **Executive summary:** test configuration table (APIs, query counts, styles, locales, issues).
- **Detailed performance analysis:** per API — overall metrics, performance by style, performance by locale (EN/ES/PT), sample top results (with locale), key findings, issues identified.
- **Cross-API comparison:** success-rate bar chart, query-style performance across APIs, ranking performance when found.
- Data-driven, locale-aware; sample results include a locale column. Header lists issue IDs for ≤5 issues, count only for larger runs.

## API details

### Algolia Search API (deprecated)
- **Endpoint:** `https://{app_id}-dsn.algolia.net/1/indexes/{index_name}/query`
- **Indexes:** Help Center `helpcenter-docs`, Dev Portal `devportal-docs`
- **Auth:** headers `X-Algolia-Application-Id`, `X-Algolia-API-Key`
- **Request:** `{ "query": "search text", "hitsPerPage": 10 }`
- **Response:** `{ "hits": [ { "url": "...", "doctitle": "...", "content": "...", "hierarchy": { "lvl0": "..." } } ] }`

### VTEX Docs Hybrid Search API
- **Endpoint:** `GET /api/hybrid-search?q={query}&limit={limit}&locale={locale}`
- **Auth:** header `x-internal-access-key`
- **Example cURL:** `curl -X GET "https://vtexdocs-edge.vtex.com/api/hybrid-search?q=API&limit=50&locale=en" -H "x-internal-access-key: YOUR_KEY"` (local dev: `http://localhost:3000`)
- **Response:** `{ "results": [ { "id": 123, "title": "...", "filePath": "...", "repository": "...", "content": "...", "score": 0.95, "metadata": { "frontmatter": { "locale": "en" } } } ] }`

## Path comparison

| Aspect | Algolia Search (deprecated) | Hybrid Search |
|--------|----------------|---------------|
| API | Algolia REST API | VTEX Docs Hybrid Search API |
| Endpoint | `https://{app_id}-dsn.algolia.net/1/indexes/{index}/query` | `GET /api/hybrid-search` |
| Auth | API key via headers | Internal access key |
| Search method | Keyword-based | Hybrid (BM25 + vector + reranking) |
| Sources | helpcenter-docs, devportal-docs | Single unified index |
| Locale handling | helpcenter en/pt/es, devportal en only | all locales by default |
| Query source | `query_internal` | `query_internal` |
| Output path | `results/internal-search/algolia-{path}/` | `results/internal-search/hybrid-search/` |

## Error handling

- Missing `.env` → fall back to system env; missing credentials → exit with error.
- Unparseable issue file → warn, skip, continue.
- Missing/empty `query_internal` → warn with issue_id, skip.
- API call failure → log with issue_id/query/error, record in `errors`, set `found:false, found_at_rank:null, top_results:[]`, continue.
- Output directory created automatically.

## Full examples

```bash
# All API paths (with analysis reports)
python tools/test-suite/internal-search/run-algolia-path.py --path both
python tools/test-suite/internal-search/run-hybrid-search-path.py --generate-api-call-results

# JSON only (no analysis reports)
python tools/test-suite/internal-search/run-hybrid-search-path.py --no-analysis

# Hybrid Search, Spanish locale
python tools/test-suite/internal-search/run-hybrid-search-path.py --locale es

# Hybrid Search, all locales (default)
python tools/test-suite/internal-search/run-hybrid-search-path.py

# Specific issues only
python tools/test-suite/internal-search/run-hybrid-search-path.py --issues conditions-payment-01 refund-payment-01

# Custom run ID
python tools/test-suite/internal-search/run-hybrid-search-path.py --run-id baseline-2026-03

# Algolia (deprecated): helpcenter runs all locales, devportal always en
python tools/test-suite/internal-search/run-algolia-path.py --path both
```

## Post-run analysis

1. Review JSON results at `results/internal-search/{path}/{run_id}.json`.
2. Analyze pass rates in `summary_by_issue`.
3. Review `best_rank`/`worst_rank` for passing issues.
4. Compare Hybrid Search vs (deprecated) Algolia when both were run.
5. Cross-path comparison with Docs Assistant / LLM / external-search results.
6. Error analysis via the `errors` array.
7. Query-style analysis (naive/familiar/expert).
