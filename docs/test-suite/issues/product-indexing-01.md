# Issue: Solve product indexing problems

| Field | Value |
|-------|--------|
| **issue_id** | product-indexing-01 |
| **persona** | Store operator |
| **product** | Catalog / Search |
| **user_intent** | How to solve product indexing problems |
| **target_doc_url** | https://help.vtex.com/en/tutorial/understanding-how-indexation-works |
| **surface** | help-center |
| **target_docs** | ["https://help.vtex.com/pt/tutorial/entendendo-o-funcionamento-da-indexacao", "https://help.vtex.com/docs/tutorials/understanding-how-indexation-works", "https://help.vtex.com/es/tutorial/entendiendo-el-funcionamento-de-la-indexacion", "https://help.vtex.com/pt/troubleshooting/nao-consigo-indexar-um-produto-do-catalogo", "https://help.vtex.com/troubleshooting/i-cant-index-a-product-in-the-catalog", "https://help.vtex.com/es/troubleshooting/no-logro-indexar-un-producto-del-catalogo", "https://help.vtex.com/pt/docs/tutorials/utilizar-o-relatorio-de-indexacao", "https://help.vtex.com/docs/tutorials/how-to-use-the-index-report", "https://help.vtex.com/es/docs/tutorials/utilizando-el-informe-de-indexacion", "https://help.vtex.com/en/docs/tutorials/understanding-how-indexation-works", "https://help.vtex.com/pt/docs/tutorials/entendendo-o-funcionamento-da-indexacao", "https://help.vtex.com/es/docs/tutorials/entendiendo-el-funcionamento-de-la-indexacion", "https://help.vtex.com/en/troubleshooting/i-cant-index-a-product-in-the-catalog", "https://help.vtex.com/en/docs/tutorials/how-to-use-the-index-report"] |
| **other_helpful_docs** | ["https://help.vtex.com/pt/faq/por-que-o-produto-nao-aparece-no-site", "https://help.vtex.com/en/faq/why-is-the-product-not-visible-on-the-website", "https://help.vtex.com/es/faq/por-que-el-producto-no-aparece-en-el-sitio-web"] |
| **source** | Command input (user issue) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | my products are not updating in search results on my VTEX store |
| en | familiar | VTEX product indexing issues troubleshooting |
| en | expert | VTEX catalog indexing problems solution |
| pt | naive | meus produtos não estão sendo atualizados nos resultados de busca da minha loja VTEX |
| pt | familiar | problemas de indexação de produtos VTEX solução de problemas |
| pt | expert | solução de problemas de indexação do catálogo VTEX |
| es | naive | mis productos no se actualizan en los resultados de búsqueda de mi tienda VTEX |
| es | familiar | problemas de indexación de productos VTEX solución de problemas |
| es | expert | solución de problemas de indexación del catálogo VTEX |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "my products are not updating in search results on my VTEX store" },
  { "locale": "en", "style": "familiar", "query": "VTEX product indexing issues troubleshooting" },
  { "locale": "en", "style": "expert", "query": "VTEX catalog indexing problems solution" },
  { "locale": "pt", "style": "naive", "query": "meus produtos não estão sendo atualizados nos resultados de busca da minha loja VTEX" },
  { "locale": "pt", "style": "familiar", "query": "problemas de indexação de produtos VTEX solução de problemas" },
  { "locale": "pt", "style": "expert", "query": "solução de problemas de indexação do catálogo VTEX" },
  { "locale": "es", "style": "naive", "query": "mis productos no se actualizan en los resultados de búsqueda de mi tienda VTEX" },
  { "locale": "es", "style": "familiar", "query": "problemas de indexación de productos VTEX solución de problemas" },
  { "locale": "es", "style": "expert", "query": "solución de problemas de indexación del catálogo VTEX" }
]
```

### B — Internal search (Algolia/Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | products not updating search |
| en | familiar | product indexing issues |
| en | expert | catalog indexing troubleshooting |
| pt | naive | produtos não atualizando busca |
| pt | familiar | problemas de indexação de produtos |
| pt | expert | solução de problemas de indexação do catálogo |
| es | naive | productos sin actualizar búsqueda |
| es | familiar | problemas de indexación de productos |
| es | expert | solución de problemas de indexación del catálogo |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "products not updating search" },
  { "locale": "en", "style": "familiar", "query": "product indexing issues" },
  { "locale": "en", "style": "expert", "query": "catalog indexing troubleshooting" },
  { "locale": "pt", "style": "naive", "query": "produtos não atualizando busca" },
  { "locale": "pt", "style": "familiar", "query": "problemas de indexação de produtos" },
  { "locale": "pt", "style": "expert", "query": "solução de problemas de indexação do catálogo" },
  { "locale": "es", "style": "naive", "query": "productos sin actualizar búsqueda" },
  { "locale": "es", "style": "familiar", "query": "problemas de indexación de productos" },
  { "locale": "es", "style": "expert", "query": "solución de problemas de indexación del catálogo" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | why are my product changes not showing up in search |
| en | familiar | troubleshoot product indexing VTEX |
| en | expert | solve product indexing problems VTEX catalog |
| pt | naive | por que as alterações nos meus produtos não aparecem na busca |
| pt | familiar | solucionar problemas de indexação de produtos VTEX |
| pt | expert | resolver problemas de indexação de produtos no catálogo VTEX |
| es | naive | por qué los cambios de mis productos no aparecen en la búsqueda |
| es | familiar | solucionar problemas de indexación de productos VTEX |
| es | expert | resolver problemas de indexación de productos en el catálogo VTEX |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "why are my product changes not showing up in search" },
  { "locale": "en", "style": "familiar", "query": "troubleshoot product indexing VTEX" },
  { "locale": "en", "style": "expert", "query": "solve product indexing problems VTEX catalog" },
  { "locale": "pt", "style": "naive", "query": "por que as alterações nos meus produtos não aparecem na busca" },
  { "locale": "pt", "style": "familiar", "query": "solucionar problemas de indexação de produtos VTEX" },
  { "locale": "pt", "style": "expert", "query": "resolver problemas de indexação de produtos no catálogo VTEX" },
  { "locale": "es", "style": "naive", "query": "por qué los cambios de mis productos no aparecen en la búsqueda" },
  { "locale": "es", "style": "familiar", "query": "solucionar problemas de indexación de productos VTEX" },
  { "locale": "es", "style": "expert", "query": "resolver problemas de indexación de productos en el catálogo VTEX" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | Why aren't my product updates appearing when customers search my VTEX store? |
| en | familiar | How do I fix product indexing issues in VTEX? |
| en | expert | How do I solve product indexing problems in VTEX? |
| pt | naive | Por que as atualizações dos meus produtos não aparecem quando os clientes pesquisam na minha loja VTEX? |
| pt | familiar | Como corrijo problemas de indexação de produtos no VTEX? |
| pt | expert | Como resolvo problemas de indexação de produtos no VTEX? |
| es | naive | ¿Por qué las actualizaciones de mis productos no aparecen cuando los clientes buscan en mi tienda VTEX? |
| es | familiar | ¿Cómo corrijo problemas de indexación de productos en VTEX? |
| es | expert | ¿Cómo resuelvo problemas de indexación de productos en VTEX? |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "Why aren't my product updates appearing when customers search my VTEX store?" },
  { "locale": "en", "style": "familiar", "query": "How do I fix product indexing issues in VTEX?" },
  { "locale": "en", "style": "expert", "query": "How do I solve product indexing problems in VTEX?" },
  { "locale": "pt", "style": "naive", "query": "Por que as atualizações dos meus produtos não aparecem quando os clientes pesquisam na minha loja VTEX?" },
  { "locale": "pt", "style": "familiar", "query": "Como corrijo problemas de indexação de produtos no VTEX?" },
  { "locale": "pt", "style": "expert", "query": "Como resolvo problemas de indexação de produtos no VTEX?" },
  { "locale": "es", "style": "naive", "query": "¿Por qué las actualizaciones de mis productos no aparecen cuando los clientes buscan en mi tienda VTEX?" },
  { "locale": "es", "style": "familiar", "query": "¿Cómo corrijo problemas de indexación de productos en VTEX?" },
  { "locale": "es", "style": "expert", "query": "¿Cómo resuelvo problemas de indexación de productos en VTEX?" }
]
```


