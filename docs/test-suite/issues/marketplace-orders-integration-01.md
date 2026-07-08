# Issue: Why don't marketplace orders integrate with my store?

| Field | Value |
|-------|--------|
| **issue_id** | marketplace-orders-integration-01 |
| **persona** | Store operator |
| **product** | Marketplace / Orders / Integration |
| **user_intent** | Troubleshoot why marketplace orders don't integrate with the store |
| **target_doc_url** | https://help.vtex.com/en/troubleshooting/why-dont-marketplace-orders-integrate-with-my-store |
| **surface** | help-center |
| **target_docs** | ["https://help.vtex.com/pt/troubleshooting/por-que-os-pedidos-do-marketplace-nao-integram-com-minha-loja", "https://help.vtex.com/docs/troubleshooting/why-dont-marketplace-orders-integrate-with-my-store", "https://help.vtex.com/es/troubleshooting/por-que-los-pedidos-del-marketplace-no-se-integran-con-mi-tienda", "https://help.vtex.com/en/troubleshooting/why-dont-marketplace-orders-integrate-with-my-store"] |
| **other_helpful_docs** | ["https://help.vtex.com/docs/tutorials/out-of-stock-errors-in-marketplace-integration-orders", "https://help.vtex.com/docs/tutorials/sla-errors-in-marketplace-integration-orders", "https://help.vtex.com/docs/tutorials/order-errors-in-the-amazon-integration", "https://help.vtex.com/en/docs/tutorials/out-of-stock-errors-in-marketplace-integration-orders", "https://help.vtex.com/pt/docs/tutorials/erros-de-falta-de-estoque-na-integracao-de-pedidos-de-marketplace", "https://help.vtex.com/es/docs/tutorials/errores-de-falta-de-stock-en-la-integracion-de-pedidos-de-marketplace", "https://help.vtex.com/en/docs/tutorials/sla-errors-in-marketplace-integration-orders", "https://help.vtex.com/pt/docs/tutorials/erros-de-sla-na-integracao-de-pedidos-de-marketplace", "https://help.vtex.com/es/docs/tutorials/errores-de-sla-en-la-integracion-de-pedidos-de-marketplace", "https://help.vtex.com/en/docs/tutorials/order-errors-in-the-amazon-integration", "https://help.vtex.com/pt/docs/tutorials/erros-de-integracao-de-pedidos-da-amazon", "https://help.vtex.com/es/docs/tutorials/errores-de-integracion-de-pedidos-de-amazon"] |
| **source** | Command input (target document URL) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | VTEX marketplace orders not integrating |
| en | familiar | VTEX marketplace order integration errors troubleshooting |
| en | expert | why don't marketplace orders integrate with VTEX store |
| pt | naive | pedidos do marketplace VTEX não integrando |
| pt | familiar | erros de integração de pedidos do marketplace VTEX solução de problemas |
| pt | expert | por que os pedidos do marketplace não integram com a loja VTEX |
| es | naive | pedidos del marketplace VTEX sin integrar |
| es | familiar | errores de integración de pedidos del marketplace VTEX solución de problemas |
| es | expert | por qué los pedidos del marketplace no se integran con la tienda VTEX |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "VTEX marketplace orders not integrating" },
  { "locale": "en", "style": "familiar", "query": "VTEX marketplace order integration errors troubleshooting" },
  { "locale": "en", "style": "expert", "query": "why don't marketplace orders integrate with VTEX store" },
  { "locale": "pt", "style": "naive", "query": "pedidos do marketplace VTEX não integrando" },
  { "locale": "pt", "style": "familiar", "query": "erros de integração de pedidos do marketplace VTEX solução de problemas" },
  { "locale": "pt", "style": "expert", "query": "por que os pedidos do marketplace não integram com a loja VTEX" },
  { "locale": "es", "style": "naive", "query": "pedidos del marketplace VTEX sin integrar" },
  { "locale": "es", "style": "familiar", "query": "errores de integración de pedidos del marketplace VTEX solución de problemas" },
  { "locale": "es", "style": "expert", "query": "por qué los pedidos del marketplace no se integran con la tienda VTEX" }
]
```

### B — Internal search (Algolia / Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | marketplace orders integration |
| en | familiar | marketplace order integration errors |
| en | expert | marketplace orders integrate store troubleshooting |
| pt | naive | integração de pedidos do marketplace |
| pt | familiar | erros de integração de pedidos do marketplace |
| pt | expert | pedidos do marketplace integrar loja solução de problemas |
| es | naive | integración de pedidos del marketplace |
| es | familiar | errores de integración de pedidos del marketplace |
| es | expert | pedidos del marketplace integrar tienda solución de problemas |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "marketplace orders integration" },
  { "locale": "en", "style": "familiar", "query": "marketplace order integration errors" },
  { "locale": "en", "style": "expert", "query": "marketplace orders integrate store troubleshooting" },
  { "locale": "pt", "style": "naive", "query": "integração de pedidos do marketplace" },
  { "locale": "pt", "style": "familiar", "query": "erros de integração de pedidos do marketplace" },
  { "locale": "pt", "style": "expert", "query": "pedidos do marketplace integrar loja solução de problemas" },
  { "locale": "es", "style": "naive", "query": "integración de pedidos del marketplace" },
  { "locale": "es", "style": "familiar", "query": "errores de integración de pedidos del marketplace" },
  { "locale": "es", "style": "expert", "query": "pedidos del marketplace integrar tienda solución de problemas" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | vtex docs marketplace orders integration errors |
| en | familiar | vtex marketplace order integration |
| en | expert | marketplace orders integrate store |
| pt | naive | vtex docs erros de integração de pedidos do marketplace |
| pt | familiar | vtex integração de pedidos do marketplace |
| pt | expert | pedidos do marketplace integrar loja |
| es | naive | vtex docs errores de integración de pedidos del marketplace |
| es | familiar | vtex integración de pedidos del marketplace |
| es | expert | pedidos del marketplace integrar tienda |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "vtex docs marketplace orders integration errors" },
  { "locale": "en", "style": "familiar", "query": "vtex marketplace order integration" },
  { "locale": "en", "style": "expert", "query": "marketplace orders integrate store" },
  { "locale": "pt", "style": "naive", "query": "vtex docs erros de integração de pedidos do marketplace" },
  { "locale": "pt", "style": "familiar", "query": "vtex integração de pedidos do marketplace" },
  { "locale": "pt", "style": "expert", "query": "pedidos do marketplace integrar loja" },
  { "locale": "es", "style": "naive", "query": "vtex docs errores de integración de pedidos del marketplace" },
  { "locale": "es", "style": "familiar", "query": "vtex integración de pedidos del marketplace" },
  { "locale": "es", "style": "expert", "query": "pedidos del marketplace integrar tienda" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | why aren't my marketplace orders showing up in VTEX |
| en | familiar | how to fix marketplace order integration errors in VTEX |
| en | expert | why don't marketplace orders integrate with my VTEX store |
| pt | naive | por que os meus pedidos do marketplace não aparecem no VTEX |
| pt | familiar | como corrigir erros de integração de pedidos do marketplace no VTEX |
| pt | expert | por que os pedidos do marketplace não integram com a minha loja VTEX |
| es | naive | por qué mis pedidos del marketplace no aparecen en VTEX |
| es | familiar | cómo corregir errores de integración de pedidos del marketplace en VTEX |
| es | expert | por qué los pedidos del marketplace no se integran con mi tienda VTEX |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "why aren't my marketplace orders showing up in VTEX" },
  { "locale": "en", "style": "familiar", "query": "how to fix marketplace order integration errors in VTEX" },
  { "locale": "en", "style": "expert", "query": "why don't marketplace orders integrate with my VTEX store" },
  { "locale": "pt", "style": "naive", "query": "por que os meus pedidos do marketplace não aparecem no VTEX" },
  { "locale": "pt", "style": "familiar", "query": "como corrigir erros de integração de pedidos do marketplace no VTEX" },
  { "locale": "pt", "style": "expert", "query": "por que os pedidos do marketplace não integram com a minha loja VTEX" },
  { "locale": "es", "style": "naive", "query": "por qué mis pedidos del marketplace no aparecen en VTEX" },
  { "locale": "es", "style": "familiar", "query": "cómo corregir errores de integración de pedidos del marketplace en VTEX" },
  { "locale": "es", "style": "expert", "query": "por qué los pedidos del marketplace no se integran con mi tienda VTEX" }
]
```


