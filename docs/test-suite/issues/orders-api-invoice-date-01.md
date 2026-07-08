# Issue: Lookup orders by invoice creation date

| Field | Value |
|-------|--------|
| **issue_id** | orders-api-invoice-date-01 |
| **persona** | Developer |
| **product** | Orders API |
| **user_intent** | How to lookup/filter orders by the date of invoice creation. |
| **target_doc_url** | https://developers.vtex.com/docs/api-reference/orders-api#get-/api/oms/pvt/orders |
| **surface** | developers-portal |
| **target_docs** | ["https://developers.vtex.com/docs/api-reference/orders-api#get-/api/oms/pvt/orders", "https://help.vtex.com/docs/tutorials/filtering-all-orders", "https://help.vtex.com/en/docs/tutorials/filtering-all-orders", "https://help.vtex.com/pt/docs/tutorials/filtrar-todos-pedidos", "https://help.vtex.com/es/docs/tutorials/filtrar-todos-los-pedidos"] |
| **other_helpful_docs** | [] |
| **source** | Command input (target document URL) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | how to find orders by invoice date in VTEX |
| en | familiar | VTEX orders api filter by invoice creation date |
| en | expert | VTEX orders api get orders by invoice date |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to find orders by invoice date in VTEX" },
  { "locale": "en", "style": "familiar", "query": "VTEX orders api filter by invoice creation date" },
  { "locale": "en", "style": "expert", "query": "VTEX orders api get orders by invoice date" }
]
```

### B — Internal search (Algolia / Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | orders invoice date filter |
| en | familiar | get orders by invoice creation date |
| en | expert | orders api invoice date |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "orders invoice date filter" },
  { "locale": "en", "style": "familiar", "query": "get orders by invoice creation date" },
  { "locale": "en", "style": "expert", "query": "orders api invoice date" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | vtex docs orders api filter by invoice creation date |
| en | familiar | vtex orders api invoice date filter |
| en | expert | orders api get orders invoice date |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "vtex docs orders api filter by invoice creation date" },
  { "locale": "en", "style": "familiar", "query": "vtex orders api invoice date filter" },
  { "locale": "en", "style": "expert", "query": "orders api get orders invoice date" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | how do i find orders created on a specific invoice date in vtex |
| en | familiar | what api endpoint lets me filter orders by invoice creation date in vtex |
| en | expert | how to query orders by invoice date using vtex orders api |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "how do i find orders created on a specific invoice date in vtex" },
  { "locale": "en", "style": "familiar", "query": "what api endpoint lets me filter orders by invoice creation date in vtex" },
  { "locale": "en", "style": "expert", "query": "how to query orders by invoice date using vtex orders api" }
]
```


