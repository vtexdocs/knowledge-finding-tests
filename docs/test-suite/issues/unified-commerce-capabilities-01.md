# Issue: VTEX omnichannel capabilities

| Field | Value |
|-------|--------|
| **issue_id** | unified-commerce-capabilities-01 |
| **persona** | Decision maker |
| **product** | Unified Commerce |
| **user_intent** | What are VTEX's omnichannel capabilities? |
| **target_doc_url** | https://help.vtex.com/en/docs/tracks/unified-commerce |
| **surface** | help-center |
| **target_docs** | ["https://help.vtex.com/en/docs/tracks/unified-commerce-101", "https://help.vtex.com/docs/tracks/unified-commerce", "https://help.vtex.com/pt/docs/tracks/comercio-unificado-101", "https://help.vtex.com/es/docs/tracks/comercio-unificado-101", "https://help.vtex.com/en/docs/tracks/unified-commerce", "https://help.vtex.com/pt/docs/tracks/comercio-unificado", "https://help.vtex.com/es/docs/tracks/comercio-unificado"] |
| **other_helpful_docs** | ["https://help.vtex.com/en/docs/tracks/what-is-vtex-sales-app", "https://help.vtex.com/en/docs/tutorials/multilevel-omnichannel-inventory", "https://help.vtex.com/pt/docs/tracks/o-que-e-o-vtex-sales-app", "https://help.vtex.com/es/docs/tracks/que-es-vtex-sales-app", "https://help.vtex.com/pt/docs/tutorials/multilevel-omnichannel-inventory", "https://help.vtex.com/es/docs/tutorials/multilevel-omnichannel-inventory"] |
| **source** | Command input (user issue + target document URL) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | what are VTEX's omnichannel capabilities |
| en | familiar | VTEX unified commerce features |
| en | expert | VTEX unified commerce strategy |
| pt | naive | quais são as capacidades omnichannel da VTEX |
| pt | familiar | recursos de comércio unificado VTEX |
| pt | expert | estratégia de comércio unificado VTEX |
| es | naive | cuáles son las capacidades omnichannel de VTEX |
| es | familiar | características de comercio unificado VTEX |
| es | expert | estrategia de comercio unificado VTEX |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "what are VTEX's omnichannel capabilities" },
  { "locale": "en", "style": "familiar", "query": "VTEX unified commerce features" },
  { "locale": "en", "style": "expert", "query": "VTEX unified commerce strategy" },
  { "locale": "pt", "style": "naive", "query": "quais são as capacidades omnichannel da VTEX" },
  { "locale": "pt", "style": "familiar", "query": "recursos de comércio unificado VTEX" },
  { "locale": "pt", "style": "expert", "query": "estratégia de comércio unificado VTEX" },
  { "locale": "es", "style": "naive", "query": "cuáles son las capacidades omnichannel de VTEX" },
  { "locale": "es", "style": "familiar", "query": "características de comercio unificado VTEX" },
  { "locale": "es", "style": "expert", "query": "estrategia de comercio unificado VTEX" }
]
```

### B — Internal search (Algolia / Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | omnichannel capabilities |
| en | familiar | unified commerce |
| en | expert | unified commerce strategy |
| pt | naive | capacidades omnichannel |
| pt | familiar | comércio unificado |
| pt | expert | estratégia de comércio unificado |
| es | naive | capacidades omnichannel |
| es | familiar | comercio unificado |
| es | expert | estrategia de comercio unificado |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "omnichannel capabilities" },
  { "locale": "en", "style": "familiar", "query": "unified commerce" },
  { "locale": "en", "style": "expert", "query": "unified commerce strategy" },
  { "locale": "pt", "style": "naive", "query": "capacidades omnichannel" },
  { "locale": "pt", "style": "familiar", "query": "comércio unificado" },
  { "locale": "pt", "style": "expert", "query": "estratégia de comércio unificado" },
  { "locale": "es", "style": "naive", "query": "capacidades omnichannel" },
  { "locale": "es", "style": "familiar", "query": "comercio unificado" },
  { "locale": "es", "style": "expert", "query": "estrategia de comercio unificado" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | vtex docs what are omnichannel capabilities |
| en | familiar | vtex unified commerce |
| en | expert | unified commerce |
| pt | naive | vtex docs quais são as capacidades omnichannel |
| pt | familiar | vtex comércio unificado |
| pt | expert | comércio unificado |
| es | naive | vtex docs cuáles son las capacidades omnichannel |
| es | familiar | vtex comercio unificado |
| es | expert | comercio unificado |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "vtex docs what are omnichannel capabilities" },
  { "locale": "en", "style": "familiar", "query": "vtex unified commerce" },
  { "locale": "en", "style": "expert", "query": "unified commerce" },
  { "locale": "pt", "style": "naive", "query": "vtex docs quais são as capacidades omnichannel" },
  { "locale": "pt", "style": "familiar", "query": "vtex comércio unificado" },
  { "locale": "pt", "style": "expert", "query": "comércio unificado" },
  { "locale": "es", "style": "naive", "query": "vtex docs cuáles son las capacidades omnichannel" },
  { "locale": "es", "style": "familiar", "query": "vtex comercio unificado" },
  { "locale": "es", "style": "expert", "query": "comercio unificado" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | what omnichannel features does VTEX offer |
| en | familiar | what is unified commerce in VTEX |
| en | expert | how does VTEX unified commerce work |
| pt | naive | quais recursos omnichannel a VTEX oferece |
| pt | familiar | o que é comércio unificado no VTEX |
| pt | expert | como funciona o comércio unificado da VTEX |
| es | naive | qué características omnichannel ofrece VTEX |
| es | familiar | qué es el comercio unificado en VTEX |
| es | expert | cómo funciona el comercio unificado de VTEX |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "what omnichannel features does VTEX offer" },
  { "locale": "en", "style": "familiar", "query": "what is unified commerce in VTEX" },
  { "locale": "en", "style": "expert", "query": "how does VTEX unified commerce work" },
  { "locale": "pt", "style": "naive", "query": "quais recursos omnichannel a VTEX oferece" },
  { "locale": "pt", "style": "familiar", "query": "o que é comércio unificado no VTEX" },
  { "locale": "pt", "style": "expert", "query": "como funciona o comércio unificado da VTEX" },
  { "locale": "es", "style": "naive", "query": "qué características omnichannel ofrece VTEX" },
  { "locale": "es", "style": "familiar", "query": "qué es el comercio unificado en VTEX" },
  { "locale": "es", "style": "expert", "query": "cómo funciona el comercio unificado de VTEX" }
]
```


