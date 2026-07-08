# Issue: Update orders via Checkout API

| Field | Value |
|-------|--------|
| **issue_id** | checkout-api-orders-01 |
| **persona** | Developer |
| **product** | Checkout API / Orders |
| **user_intent** | How to place orders via Checkout API. |
| **target_doc_url** | https://developers.vtex.com/docs/api-reference/checkout-api#put-/api/checkout/pub/orders |
| **surface** | developers-portal |
| **target_docs** | ["https://developers.vtex.com/docs/api-reference/checkout-api#put-/api/checkout/pub/orders"] |
| **other_helpful_docs** | ["https://developers.vtex.com/docs/guides/checkout-api-overview","https://developers.vtex.com/docs/guides/create-a-regular-order-using-the-checkout-api"] |
| **source** | Command input (target document URL) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | how to send order data in vtex checkout api what format |
| en | familiar | checkout api update order request body format vtex |
| en | expert | checkout api put orders json payload structure vtex |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to send order data in vtex checkout api what format" },
  { "locale": "en", "style": "familiar", "query": "checkout api update order request body format vtex" },
  { "locale": "en", "style": "expert", "query": "checkout api put orders json payload structure vtex" }
]
```

### B — Internal search (Algolia / Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | checkout api order request body format |
| en | familiar | put orders checkout json structure |
| en | expert | checkout api orders payload |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "checkout api order request body format" },
  { "locale": "en", "style": "familiar", "query": "put orders checkout json structure" },
  { "locale": "en", "style": "expert", "query": "checkout api orders payload" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | vtex docs checkout api update order request body data format |
| en | familiar | vtex checkout api put orders json payload |
| en | expert | checkout api put orders request body |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "vtex docs checkout api update order request body data format" },
  { "locale": "en", "style": "familiar", "query": "vtex checkout api put orders json payload" },
  { "locale": "en", "style": "expert", "query": "checkout api put orders request body" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | what data format do i need to send when updating an order in vtex checkout api |
| en | familiar | what is the request body structure for updating orders in vtex checkout api |
| en | expert | how to format json payload for vtex checkout api put orders endpoint |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "what data format do i need to send when updating an order in vtex checkout api" },
  { "locale": "en", "style": "familiar", "query": "what is the request body structure for updating orders in vtex checkout api" },
  { "locale": "en", "style": "expert", "query": "how to format json payload for vtex checkout api put orders endpoint" }
]
```


