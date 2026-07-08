# Runner parameters (Playwright — user search simulation)

1. Retrieve the information for the queries indicated in the all_queries.json file in the External Search folder.
2. Simulate a user search on Google (Playwright opens google.com/search?q=…), collect only the **first 7 results** per query from the SERP.
3. Generate a new `results.json` file inside a per-run folder under **`results/external-search/google-search-playwright/`**. Each run folder is named like `google-search-playwright YYYY-MM-DD HH-MM`. The file has one structured section:

## Session 1

Show the search results for each query (same format as Google Search API runner): issue_id, source_file, queries with query, style, output_urls [{ url_address, url_description }], ai_overview_content (AI Overview when present).

Note: First test with the three queries in the first .md file (e.g. --limit-issues 1), then run with all queries.
