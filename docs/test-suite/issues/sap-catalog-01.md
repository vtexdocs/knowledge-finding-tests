# Issue: Integrate catalog from SAP

| Field | Value |
|-------|--------|
| **issue_id** | sap-catalog-01 |
| **persona** | Developer |
| **product** | Catalog / Backend integrations |
| **user_intent** | How to integrate product catalog from SAP (ERP) with VTEX. |
| **target_doc_url** | https://developers.vtex.com/docs/guides/erp-integration-guide |
| **surface** | help-center |
| **target_docs** | ["https://developers.vtex.com/docs/guides/catalog-overview","https://developers.vtex.com/docs/guides/erp-integration-import-products"] |
| **other_helpful_docs** | ["https://developers.vtex.com/docs/guides/erp-integration-guide"] |
| **source** | Command input (user issue) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | bring my product catalog from my business software into my VTEX online store |
| en | familiar | sync SAP product catalog to VTEX store |
| en | expert | integrate catalog from SAP ERP to VTEX |
| pt | naive | trazer o catálogo de produtos do meu software empresarial para a minha loja VTEX |
| pt | familiar | sincronizar catálogo de produtos SAP com a loja VTEX |
| pt | expert | integrar catálogo do SAP ERP ao VTEX |
| es | naive | llevar el catálogo de productos de mi software empresarial a mi tienda VTEX |
| es | familiar | sincronizar catálogo de productos SAP con la tienda VTEX |
| es | expert | integrar catálogo de SAP ERP a VTEX |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "bring my product catalog from my business software into my VTEX online store" },
  { "locale": "en", "style": "familiar", "query": "sync SAP product catalog to VTEX store" },
  { "locale": "en", "style": "expert", "query": "integrate catalog from SAP ERP to VTEX" },
  { "locale": "pt", "style": "naive", "query": "trazer o catálogo de produtos do meu software empresarial para a minha loja VTEX" },
  { "locale": "pt", "style": "familiar", "query": "sincronizar catálogo de produtos SAP com a loja VTEX" },
  { "locale": "pt", "style": "expert", "query": "integrar catálogo do SAP ERP ao VTEX" },
  { "locale": "es", "style": "naive", "query": "llevar el catálogo de productos de mi software empresarial a mi tienda VTEX" },
  { "locale": "es", "style": "familiar", "query": "sincronizar catálogo de productos SAP con la tienda VTEX" },
  { "locale": "es", "style": "expert", "query": "integrar catálogo de SAP ERP a VTEX" }
]
```

### B — Internal search (Algolia/Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | product catalog business software online store |
| en | familiar | SAP catalog VTEX sync integration |
| en | expert | integrate catalog SAP ERP VTEX backend |
| pt | naive | catálogo de produtos software empresarial loja online |
| pt | familiar | SAP catálogo VTEX sincronização integração |
| pt | expert | integrar catálogo SAP ERP VTEX backend |
| es | naive | catálogo de productos software empresarial tienda online |
| es | familiar | SAP catálogo VTEX sincronización integración |
| es | expert | integrar catálogo SAP ERP VTEX backend |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "product catalog business software online store" },
  { "locale": "en", "style": "familiar", "query": "SAP catalog VTEX sync integration" },
  { "locale": "en", "style": "expert", "query": "integrate catalog SAP ERP VTEX backend" },
  { "locale": "pt", "style": "naive", "query": "catálogo de produtos software empresarial loja online" },
  { "locale": "pt", "style": "familiar", "query": "SAP catálogo VTEX sincronização integração" },
  { "locale": "pt", "style": "expert", "query": "integrar catálogo SAP ERP VTEX backend" },
  { "locale": "es", "style": "naive", "query": "catálogo de productos software empresarial tienda online" },
  { "locale": "es", "style": "familiar", "query": "SAP catálogo VTEX sincronización integración" },
  { "locale": "es", "style": "expert", "query": "integrar catálogo SAP ERP VTEX backend" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | how to get product catalog from my ERP into VTEX |
| en | familiar | SAP catalog integration with VTEX backend |
| en | expert | integrate catalog from SAP VTEX backend integrations |
| pt | naive | como trazer o catálogo de produtos do meu ERP para o VTEX |
| pt | familiar | integração do catálogo SAP com o backend VTEX |
| pt | expert | integrar catálogo do SAP VTEX integrações de backend |
| es | naive | cómo llevar el catálogo de productos de mi ERP a VTEX |
| es | familiar | integración del catálogo SAP con el backend VTEX |
| es | expert | integrar catálogo de SAP VTEX integraciones de backend |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to get product catalog from my ERP into VTEX" },
  { "locale": "en", "style": "familiar", "query": "SAP catalog integration with VTEX backend" },
  { "locale": "en", "style": "expert", "query": "integrate catalog from SAP VTEX backend integrations" },
  { "locale": "pt", "style": "naive", "query": "como trazer o catálogo de produtos do meu ERP para o VTEX" },
  { "locale": "pt", "style": "familiar", "query": "integração do catálogo SAP com o backend VTEX" },
  { "locale": "pt", "style": "expert", "query": "integrar catálogo do SAP VTEX integrações de backend" },
  { "locale": "es", "style": "naive", "query": "cómo llevar el catálogo de productos de mi ERP a VTEX" },
  { "locale": "es", "style": "familiar", "query": "integración del catálogo SAP con el backend VTEX" },
  { "locale": "es", "style": "expert", "query": "integrar catálogo de SAP VTEX integraciones de backend" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | How do I get my product catalog from SAP into my VTEX store? |
| en | familiar | How do I sync my SAP product catalog with VTEX? |
| en | expert | How do I integrate the catalog from SAP ERP to VTEX? |
| pt | naive | Como transfiro o catálogo de produtos do SAP para a minha loja VTEX? |
| pt | familiar | Como sincronizo o catálogo de produtos SAP com o VTEX? |
| pt | expert | Como integro o catálogo do SAP ERP ao VTEX? |
| es | naive | ¿Cómo llevo mi catálogo de productos de SAP a mi tienda VTEX? |
| es | familiar | ¿Cómo sincronizo mi catálogo de productos SAP con VTEX? |
| es | expert | ¿Cómo integro el catálogo de SAP ERP a VTEX? |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "How do I get my product catalog from SAP into my VTEX store?" },
  { "locale": "en", "style": "familiar", "query": "How do I sync my SAP product catalog with VTEX?" },
  { "locale": "en", "style": "expert", "query": "How do I integrate the catalog from SAP ERP to VTEX?" },
  { "locale": "pt", "style": "naive", "query": "Como transfiro o catálogo de produtos do SAP para a minha loja VTEX?" },
  { "locale": "pt", "style": "familiar", "query": "Como sincronizo o catálogo de produtos SAP com o VTEX?" },
  { "locale": "pt", "style": "expert", "query": "Como integro o catálogo do SAP ERP ao VTEX?" },
  { "locale": "es", "style": "naive", "query": "¿Cómo llevo mi catálogo de productos de SAP a mi tienda VTEX?" },
  { "locale": "es", "style": "familiar", "query": "¿Cómo sincronizo mi catálogo de productos SAP con VTEX?" },
  { "locale": "es", "style": "expert", "query": "¿Cómo integro el catálogo de SAP ERP a VTEX?" }
]
```


