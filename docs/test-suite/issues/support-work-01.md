# Issue: How does VTEX support work

| Field | Value |
|-------|--------|
| **issue_id** | support-work-01 |
| **persona** | Decision maker |
| **product** | Support / Operational |
| **user_intent** | How does VTEX support work? |
| **target_doc_url** | https://help.vtex.com/docs/tutorials/how-does-vtex-support-work |
| **surface** | help-center |
| **target_docs** | ["https://help.vtex.com/pt/tutorial/como-funciona-o-suporte-da-vtex", "https://help.vtex.com/docs/tutorials/how-does-vtex-support-work", "https://help.vtex.com/es/tutorial/como-funciona-el-soporte-de-vtex", "https://help.vtex.com/en/docs/tracks/how-vtex-support-works", "https://help.vtex.com/docs/tracks/vtex-support", "https://help.vtex.com/en/docs/tutorials/how-does-vtex-support-work", "https://help.vtex.com/pt/docs/tutorials/como-funciona-o-suporte-da-vtex", "https://help.vtex.com/es/docs/tutorials/como-funciona-el-soporte-de-vtex", "https://help.vtex.com/pt/docs/tracks/funcionamento-do-suporte-vtex", "https://help.vtex.com/es/docs/tracks/funcionamiento-del-soporte-vtex", "https://help.vtex.com/en/docs/tracks/vtex-support", "https://help.vtex.com/pt/docs/tracks/suporte-na-vtex", "https://help.vtex.com/es/docs/tracks/soporte-vtex"] |
| **other_helpful_docs** | ["https://help.vtex.com/en/docs/tutorials/opening-tickets-to-vtex-support", "https://help.vtex.com/en/docs/tutorials/opening-tickets-to-vtex-support", "https://help.vtex.com/pt/docs/tutorials/abrir-chamados-para-o-suporte-vtex", "https://help.vtex.com/es/docs/tutorials/abrir-tickets-para-el-soporte-vtex"] |
| **source** | Command input (target document URL) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | how does VTEX support work |
| en | familiar | VTEX support system how to get help |
| en | expert | VTEX support plans ticket system |
| pt | naive | como funciona o suporte da VTEX |
| pt | familiar | sistema de suporte VTEX como obter ajuda |
| pt | expert | planos de suporte VTEX sistema de tickets |
| es | naive | cómo funciona el soporte de VTEX |
| es | familiar | sistema de soporte VTEX cómo obtener ayuda |
| es | expert | planes de soporte VTEX sistema de tickets |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "how does VTEX support work" },
  { "locale": "en", "style": "familiar", "query": "VTEX support system how to get help" },
  { "locale": "en", "style": "expert", "query": "VTEX support plans ticket system" },
  { "locale": "pt", "style": "naive", "query": "como funciona o suporte da VTEX" },
  { "locale": "pt", "style": "familiar", "query": "sistema de suporte VTEX como obter ajuda" },
  { "locale": "pt", "style": "expert", "query": "planos de suporte VTEX sistema de tickets" },
  { "locale": "es", "style": "naive", "query": "cómo funciona el soporte de VTEX" },
  { "locale": "es", "style": "familiar", "query": "sistema de soporte VTEX cómo obtener ayuda" },
  { "locale": "es", "style": "expert", "query": "planes de soporte VTEX sistema de tickets" }
]
```

### B — Internal search (Algolia / Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | support help |
| en | familiar | VTEX support ticket |
| en | expert | support plans ticket system |
| pt | naive | suporte ajuda |
| pt | familiar | ticket de suporte VTEX |
| pt | expert | planos de suporte sistema de tickets |
| es | naive | soporte ayuda |
| es | familiar | ticket de soporte VTEX |
| es | expert | planes de soporte sistema de tickets |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "support help" },
  { "locale": "en", "style": "familiar", "query": "VTEX support ticket" },
  { "locale": "en", "style": "expert", "query": "support plans ticket system" },
  { "locale": "pt", "style": "naive", "query": "suporte ajuda" },
  { "locale": "pt", "style": "familiar", "query": "ticket de suporte VTEX" },
  { "locale": "pt", "style": "expert", "query": "planos de suporte sistema de tickets" },
  { "locale": "es", "style": "naive", "query": "soporte ayuda" },
  { "locale": "es", "style": "familiar", "query": "ticket de soporte VTEX" },
  { "locale": "es", "style": "expert", "query": "planes de soporte sistema de tickets" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | vtex docs how does support work |
| en | familiar | vtex support |
| en | expert | support work |
| pt | naive | vtex docs como funciona o suporte |
| pt | familiar | vtex suporte |
| pt | expert | suporte funciona |
| es | naive | vtex docs cómo funciona el soporte |
| es | familiar | vtex soporte |
| es | expert | soporte funciona |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "vtex docs how does support work" },
  { "locale": "en", "style": "familiar", "query": "vtex support" },
  { "locale": "en", "style": "expert", "query": "support work" },
  { "locale": "pt", "style": "naive", "query": "vtex docs como funciona o suporte" },
  { "locale": "pt", "style": "familiar", "query": "vtex suporte" },
  { "locale": "pt", "style": "expert", "query": "suporte funciona" },
  { "locale": "es", "style": "naive", "query": "vtex docs cómo funciona el soporte" },
  { "locale": "es", "style": "familiar", "query": "vtex soporte" },
  { "locale": "es", "style": "expert", "query": "soporte funciona" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | how do I get support from VTEX |
| en | familiar | how does VTEX support system work |
| en | expert | what are VTEX support plans and how do tickets work |
| pt | naive | como obtenho suporte da VTEX |
| pt | familiar | como funciona o sistema de suporte da VTEX |
| pt | expert | quais são os planos de suporte da VTEX e como funcionam os tickets |
| es | naive | cómo obtengo soporte de VTEX |
| es | familiar | cómo funciona el sistema de soporte de VTEX |
| es | expert | cuáles son los planes de soporte de VTEX y cómo funcionan los tickets |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "how do I get support from VTEX" },
  { "locale": "en", "style": "familiar", "query": "how does VTEX support system work" },
  { "locale": "en", "style": "expert", "query": "what are VTEX support plans and how do tickets work" },
  { "locale": "pt", "style": "naive", "query": "como obtenho suporte da VTEX" },
  { "locale": "pt", "style": "familiar", "query": "como funciona o sistema de suporte da VTEX" },
  { "locale": "pt", "style": "expert", "query": "quais são os planos de suporte da VTEX e como funcionam os tickets" },
  { "locale": "es", "style": "naive", "query": "cómo obtengo soporte de VTEX" },
  { "locale": "es", "style": "familiar", "query": "cómo funciona el sistema de soporte de VTEX" },
  { "locale": "es", "style": "expert", "query": "cuáles son los planes de soporte de VTEX y cómo funcionan los tickets" }
]
```


