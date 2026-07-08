# Issue: Content delivery optimization

| Field | Value |
|-------|--------|
| **issue_id** | content-delivery-optimization-01 |
| **persona** | Decision maker |
| **product** | Cloud Infrastructure / Platform |
| **user_intent** | how does vtex handle content delivery optimization? |
| **target_doc_url** | https://developers.vtex.com/docs/guides/cloud-infrastructure |
| **surface** | developers-portal |
| **target_docs** | ["https://developers.vtex.com/docs/guides/cloud-infrastructure"] |
| **other_helpful_docs** | ["https://help.vtex.com/en/docs/tutorials/how-dns-configuration-works-on-vtex", "https://help.vtex.com/pt/docs/tutorials/como-funciona-a-configuracao-de-dns-na-vtex", "https://help.vtex.com/es/docs/tutorials/como-funciona-la-configuracion-de-dns-en-vtex"] |
| **source** | Command input (user issue + target document URL) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | how does VTEX handle content delivery optimization |
| en | familiar | VTEX CDN content delivery network performance |
| en | expert | VTEX cloud infrastructure content delivery optimization |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "how does VTEX handle content delivery optimization" },
  { "locale": "en", "style": "familiar", "query": "VTEX CDN content delivery network performance" },
  { "locale": "en", "style": "expert", "query": "VTEX cloud infrastructure content delivery optimization" }
]
```

### B — Internal search (Algolia / Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | content delivery optimization |
| en | familiar | CDN caching content delivery |
| en | expert | cloud infrastructure content delivery optimization |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "content delivery optimization" },
  { "locale": "en", "style": "familiar", "query": "CDN caching content delivery" },
  { "locale": "en", "style": "expert", "query": "cloud infrastructure content delivery optimization" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | vtex docs how does content delivery optimization work |
| en | familiar | vtex content delivery CDN |
| en | expert | cloud infrastructure content delivery |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "vtex docs how does content delivery optimization work" },
  { "locale": "en", "style": "familiar", "query": "vtex content delivery CDN" },
  { "locale": "en", "style": "expert", "query": "cloud infrastructure content delivery" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | how does VTEX optimize content delivery |
| en | familiar | how does VTEX handle CDN and content caching |
| en | expert | what is VTEX's content delivery optimization strategy including CDN router and cache layers |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "how does VTEX optimize content delivery" },
  { "locale": "en", "style": "familiar", "query": "how does VTEX handle CDN and content caching" },
  { "locale": "en", "style": "expert", "query": "what is VTEX's content delivery optimization strategy including CDN router and cache layers" }
]
```


