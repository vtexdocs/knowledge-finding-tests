# Issue: FastStore Dynamic Routes for PLPs

| Field | Value |
|-------|--------|
| **issue_id** | faststore-dynamic-routes-plp-01 |
| **persona** | Developer |
| **product** | FastStore |
| **user_intent** | How to use dynamic routes for PLPs (Product Listing Pages) in a FastStore website |
| **target_doc_url** | https://developers.vtex.com/docs/guides/faststore/routing-managing-urls-with-redirects-and-rewrite-paths |
| **surface** | developers-portal |
| **target_docs** | ["https://developers.vtex.com/docs/guides/faststore/routing-managing-urls-with-redirects-and-rewrite-paths", "https://developers.vtex.com/docs/faststore/managing-urls-with-redirects-and-rewrite-paths", "https://developers.vtex.com/docs/faststore/configuring-seo-for-plp-and-pdp", "https://developers.vtex.com/docs/faststore/multiple-page-template", "https://developers.vtex.com/docs/guides/faststore/dynamic-content-overview"] |
| **other_helpful_docs** | ["https://developers.vtex.com/updates/release-notes/2024-06-18-faststore-dynamic-content"] |
| **source** | Dev Portal |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | how to make product category pages load different URLs in VTEX FastStore |
| en | familiar | FastStore product listing page routing configuration |
| en | expert | how to implement dynamic routes for PLPs in FastStore |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to make product category pages load different URLs in VTEX FastStore" },
  { "locale": "en", "style": "familiar", "query": "FastStore product listing page routing configuration" },
  { "locale": "en", "style": "expert", "query": "how to implement dynamic routes for PLPs in FastStore" }
]
```

### B — Internal search (Algolia / Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | FastStore category page URL structure |
| en | familiar | FastStore PLP routing |
| en | expert | FastStore dynamic routes product listing pages |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "FastStore category page URL structure" },
  { "locale": "en", "style": "familiar", "query": "FastStore PLP routing" },
  { "locale": "en", "style": "expert", "query": "FastStore dynamic routes product listing pages" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | How do I set up different URLs for product category pages in FastStore? |
| en | familiar | Configure routing for product listing pages in FastStore |
| en | expert | Implement dynamic routes for PLPs in FastStore project |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "How do I set up different URLs for product category pages in FastStore?" },
  { "locale": "en", "style": "familiar", "query": "Configure routing for product listing pages in FastStore" },
  { "locale": "en", "style": "expert", "query": "Implement dynamic routes for PLPs in FastStore project" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | I'm using VTEX FastStore and need to create custom URLs for my product category pages. How do I do this? |
| en | familiar | What's the best way to set up dynamic routing for product listing pages in a VTEX FastStore project? |
| en | expert | How can I implement dynamic routes for PLPs in FastStore following VTEX best practices? |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "I'm using VTEX FastStore and need to create custom URLs for my product category pages. How do I do this?" },
  { "locale": "en", "style": "familiar", "query": "What's the best way to set up dynamic routing for product listing pages in a VTEX FastStore project?" },
  { "locale": "en", "style": "expert", "query": "How can I implement dynamic routes for PLPs in FastStore following VTEX best practices?" }
]
```

## Notes

- All four query types (A, B, C, D) have been generated with exactly 3 queries each (naive, familiar, expert)
- Query wording varies by type per §2 of Planning phase 1 (tests).md
- Expected doc URL: https://developers.vtex.com/docs/guides/faststore/routing-managing-urls-with-redirects-and-rewrite-paths
- Ready to be added to test suite spreadsheet


