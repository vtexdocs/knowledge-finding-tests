# Issue: Product information in Excel

| Field | Value |
|-------|--------|
| **issue_id** | product-excel-01 |
| **persona** | Store operator |
| **product** | Catalog / Products |
| **user_intent** | The user needs to obtain all product information in Excel. |
| **target_doc_url** | https://help.vtex.com/docs/tutorials/importing-and-exporting-product-and-sku-images-using-a-spreadsheet-beta |
| **surface** | help-center |
| **target_docs** | ["https://help.vtex.com/pt/tutorial/importar-e-exportar-imagens-de-produtos-e-skus-via-planilha-beta", "https://help.vtex.com/docs/tutorials/importing-and-exporting-product-and-sku-images-using-a-spreadsheet-beta", "https://help.vtex.com/es/tutorial/importar-y-exportar-imagenes-de-productos-y-skus-mediante-plantilla-beta", "https://help.vtex.com/en/docs/tutorials/importing-and-exporting-product-and-sku-images-using-a-spreadsheet-beta", "https://help.vtex.com/pt/docs/tutorials/importar-e-exportar-imagens-de-produtos-e-skus-via-planilha-beta", "https://help.vtex.com/es/docs/tutorials/importar-y-exportar-imagenes-de-productos-y-skus-mediante-plantilla-beta"] |
| **other_helpful_docs** | [] |
| **source** | Command input (user issue) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | get all my VTEX products in a spreadsheet |
| en | familiar | VTEX export catalog to Excel |
| en | expert | export all product information to Excel VTEX |
| pt | naive | obter todos os meus produtos VTEX em uma planilha |
| pt | familiar | VTEX exportar catálogo para Excel |
| pt | expert | exportar todas as informações de produtos para Excel VTEX |
| es | naive | obtener todos mis productos VTEX en una hoja de cálculo |
| es | familiar | VTEX exportar catálogo a Excel |
| es | expert | exportar toda la información de productos a Excel VTEX |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "get all my VTEX products in a spreadsheet" },
  { "locale": "en", "style": "familiar", "query": "VTEX export catalog to Excel" },
  { "locale": "en", "style": "expert", "query": "export all product information to Excel VTEX" },
  { "locale": "pt", "style": "naive", "query": "obter todos os meus produtos VTEX em uma planilha" },
  { "locale": "pt", "style": "familiar", "query": "VTEX exportar catálogo para Excel" },
  { "locale": "pt", "style": "expert", "query": "exportar todas as informações de produtos para Excel VTEX" },
  { "locale": "es", "style": "naive", "query": "obtener todos mis productos VTEX en una hoja de cálculo" },
  { "locale": "es", "style": "familiar", "query": "VTEX exportar catálogo a Excel" },
  { "locale": "es", "style": "expert", "query": "exportar toda la información de productos a Excel VTEX" }
]
```

### B — Internal search (Algolia / Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | product export excel spreadsheet |
| en | familiar | catalog export Excel download |
| en | expert | export products Excel VTEX catalog |
| pt | naive | exportar produto excel planilha |
| pt | familiar | exportar catálogo Excel download |
| pt | expert | exportar produtos Excel VTEX catálogo |
| es | naive | exportar producto excel hoja de cálculo |
| es | familiar | exportar catálogo Excel descarga |
| es | expert | exportar productos Excel VTEX catálogo |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "product export excel spreadsheet" },
  { "locale": "en", "style": "familiar", "query": "catalog export Excel download" },
  { "locale": "en", "style": "expert", "query": "export products Excel VTEX catalog" },
  { "locale": "pt", "style": "naive", "query": "exportar produto excel planilha" },
  { "locale": "pt", "style": "familiar", "query": "exportar catálogo Excel download" },
  { "locale": "pt", "style": "expert", "query": "exportar produtos Excel VTEX catálogo" },
  { "locale": "es", "style": "naive", "query": "exportar producto excel hoja de cálculo" },
  { "locale": "es", "style": "familiar", "query": "exportar catálogo Excel descarga" },
  { "locale": "es", "style": "expert", "query": "exportar productos Excel VTEX catálogo" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | how to get product data in excel |
| en | familiar | VTEX catalog export to spreadsheet |
| en | expert | export product information to Excel VTEX |
| pt | naive | como obter dados de produtos em excel |
| pt | familiar | VTEX exportar catálogo para planilha |
| pt | expert | exportar informações de produtos para Excel VTEX |
| es | naive | cómo obtener datos de productos en excel |
| es | familiar | VTEX exportar catálogo a hoja de cálculo |
| es | expert | exportar información de productos a Excel VTEX |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to get product data in excel" },
  { "locale": "en", "style": "familiar", "query": "VTEX catalog export to spreadsheet" },
  { "locale": "en", "style": "expert", "query": "export product information to Excel VTEX" },
  { "locale": "pt", "style": "naive", "query": "como obter dados de produtos em excel" },
  { "locale": "pt", "style": "familiar", "query": "VTEX exportar catálogo para planilha" },
  { "locale": "pt", "style": "expert", "query": "exportar informações de produtos para Excel VTEX" },
  { "locale": "es", "style": "naive", "query": "cómo obtener datos de productos en excel" },
  { "locale": "es", "style": "familiar", "query": "VTEX exportar catálogo a hoja de cálculo" },
  { "locale": "es", "style": "expert", "query": "exportar información de productos a Excel VTEX" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | How can I get a list of all my products in Excel from my VTEX store? |
| en | familiar | How do I export my VTEX product catalog to Excel? |
| en | expert | What's the way to export all product information to Excel in VTEX? |
| pt | naive | Como posso obter uma lista de todos os meus produtos em Excel da minha loja VTEX? |
| pt | familiar | Como exporto o catálogo de produtos VTEX para Excel? |
| pt | expert | Qual é a forma de exportar todas as informações de produtos para Excel no VTEX? |
| es | naive | ¿Cómo puedo obtener una lista de todos mis productos en Excel de mi tienda VTEX? |
| es | familiar | ¿Cómo exporto mi catálogo de productos VTEX a Excel? |
| es | expert | ¿Cuál es la manera de exportar toda la información de productos a Excel en VTEX? |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "How can I get a list of all my products in Excel from my VTEX store?" },
  { "locale": "en", "style": "familiar", "query": "How do I export my VTEX product catalog to Excel?" },
  { "locale": "en", "style": "expert", "query": "What's the way to export all product information to Excel in VTEX?" },
  { "locale": "pt", "style": "naive", "query": "Como posso obter uma lista de todos os meus produtos em Excel da minha loja VTEX?" },
  { "locale": "pt", "style": "familiar", "query": "Como exporto o catálogo de produtos VTEX para Excel?" },
  { "locale": "pt", "style": "expert", "query": "Qual é a forma de exportar todas as informações de produtos para Excel no VTEX?" },
  { "locale": "es", "style": "naive", "query": "¿Cómo puedo obtener una lista de todos mis productos en Excel de mi tienda VTEX?" },
  { "locale": "es", "style": "familiar", "query": "¿Cómo exporto mi catálogo de productos VTEX a Excel?" },
  { "locale": "es", "style": "expert", "query": "¿Cuál es la manera de exportar toda la información de productos a Excel en VTEX?" }
]
```


