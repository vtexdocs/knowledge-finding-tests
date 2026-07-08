# Issue: Implement Live Shopping for FastStore

| Field | Value |
|-------|--------|
| **issue_id** | live-shopping-faststore-01 |
| **persona** | Developer |
| **product** | FastStore / Live Shopping |
| **user_intent** | How to implement Live Shopping on a FastStore storefront |
| **target_doc_url** | https://developers.vtex.com/docs/guides/faststore/storefront-features-implementing-live-shopping-for-faststore |
| **surface** | developers-portal |
| **target_docs** | ["https://developers.vtex.com/docs/guides/faststore/storefront-features-implementing-live-shopping-for-faststore", "https://developers.vtex.com/docs/guides/faststore/storefront-features-implementing-live-shopping-for-faststore-previous-versions", "https://help.vtex.com/es/docs/tracks/instalar-live-shopping", "https://help.vtex.com/en/docs/tracks/installing-live-shopping", "https://help.vtex.com/es/docs/tracks/instalar-live-shopping", "https://help.vtex.com/pt/docs/tracks/instalar-live-shopping"] |
| **other_helpful_docs** | ["https://help.vtex.com/pt/docs/tracks/adicionar-componente-do-live-shopping", "https://help.vtex.com/en/docs/tracks/placing-the-live-shopping-component", "https://help.vtex.com/es/docs/tracks/insertar-componente-de-live-shopping"] |
| **source** | Command input (target document URL) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | how to add live video streaming to my VTEX online store |
| en | familiar | VTEX FastStore live shopping setup |
| en | expert | implementing live shopping for FastStore VTEX |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to add live video streaming to my VTEX online store" },
  { "locale": "en", "style": "familiar", "query": "VTEX FastStore live shopping setup" },
  { "locale": "en", "style": "expert", "query": "implementing live shopping for FastStore VTEX" }
]
```

### B — Internal search (Algolia/Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | live video streaming store |
| en | familiar | FastStore live shopping |
| en | expert | live shopping FastStore implementation |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "live video streaming store" },
  { "locale": "en", "style": "familiar", "query": "FastStore live shopping" },
  { "locale": "en", "style": "expert", "query": "live shopping FastStore implementation" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | how to stream live video on my store website |
| en | familiar | add live shopping player to FastStore |
| en | expert | implementing Live Shopping for FastStore |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to stream live video on my store website" },
  { "locale": "en", "style": "familiar", "query": "add live shopping player to FastStore" },
  { "locale": "en", "style": "expert", "query": "implementing Live Shopping for FastStore" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | How can I add a live streaming feature to my VTEX FastStore ecommerce website? |
| en | familiar | How do I set up live shopping on my VTEX FastStore site? |
| en | expert | How do I implement Live Shopping for FastStore in VTEX? |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "How can I add a live streaming feature to my VTEX FastStore ecommerce website?" },
  { "locale": "en", "style": "familiar", "query": "How do I set up live shopping on my VTEX FastStore site?" },
  { "locale": "en", "style": "expert", "query": "How do I implement Live Shopping for FastStore in VTEX?" }
]
```


