# Issue: Product not visible on website

| Field | Value |
|-------|--------|
| **issue_id** | product-not-visible-01 |
| **persona** | Store operator |
| **product** | Catalog / Products |
| **user_intent** | Why is the product not visible on the website / troubleshoot product visibility |
| **target_doc_url** | https://help.vtex.com/faq/why-is-the-product-not-visible-on-the-website |
| **surface** | help-center |
| **target_docs** | ["https://help.vtex.com/pt/faq/por-que-o-produto-nao-aparece-no-site", "https://help.vtex.com/faq/why-is-the-product-not-visible-on-the-website", "https://help.vtex.com/es/faq/por-que-el-producto-no-aparece-en-el-sitio-web", "https://help.vtex.com/en/faq/why-is-the-product-not-visible-on-the-website"] |
| **other_helpful_docs** | ["https://help.vtex.com/pt/docs/tutorials/adicionar-ou-editar-produto", "https://help.vtex.com/docs/tutorials/adding-or-editing-products", "https://help.vtex.com/es/docs/tutorials/agregar-o-editar-productos", "https://help.vtex.com/pt/docs/tutorials/adicionar-ou-editar-sku", "https://help.vtex.com/docs/tutorials/adding-or-editing-skus", "https://help.vtex.com/es/docs/tutorials/agregar-o-editar-skus", "https://help.vtex.com/pt/docs/tutorials/produtos-e-skus", "https://help.vtex.com/docs/tutorials/products-and-skus", "https://help.vtex.com/es/docs/tutorials/productos-y-skus", "https://help.vtex.com/en/docs/tutorials/adding-or-editing-products", "https://help.vtex.com/en/docs/tutorials/adding-or-editing-skus", "https://help.vtex.com/en/docs/tutorials/products-and-skus"] |
| **source** | Command input (target document URL) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | my products are not showing on my VTEX online store |
| en | familiar | VTEX product not visible on website |
| en | expert | why is the product not visible on the website VTEX |
| pt | naive | meus produtos não estão aparecendo na minha loja VTEX |
| pt | familiar | VTEX produto não visível no site |
| pt | expert | por que o produto não está visível no site VTEX |
| es | naive | mis productos no aparecen en mi tienda VTEX |
| es | familiar | VTEX producto no visible en el sitio web |
| es | expert | por qué el producto no está visible en el sitio web VTEX |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "my products are not showing on my VTEX online store" },
  { "locale": "en", "style": "familiar", "query": "VTEX product not visible on website" },
  { "locale": "en", "style": "expert", "query": "why is the product not visible on the website VTEX" },
  { "locale": "pt", "style": "naive", "query": "meus produtos não estão aparecendo na minha loja VTEX" },
  { "locale": "pt", "style": "familiar", "query": "VTEX produto não visível no site" },
  { "locale": "pt", "style": "expert", "query": "por que o produto não está visível no site VTEX" },
  { "locale": "es", "style": "naive", "query": "mis productos no aparecen en mi tienda VTEX" },
  { "locale": "es", "style": "familiar", "query": "VTEX producto no visible en el sitio web" },
  { "locale": "es", "style": "expert", "query": "por qué el producto no está visible en el sitio web VTEX" }
]
```

### B — Internal search (Algolia/Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | products not showing |
| en | familiar | product not visible website |
| en | expert | product not visible site FAQ |
| pt | naive | produtos não aparecendo |
| pt | familiar | produto não visível no site |
| pt | expert | produto não visível site FAQ |
| es | naive | productos no aparecen |
| es | familiar | producto no visible en el sitio |
| es | expert | producto no visible sitio FAQ |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "products not showing" },
  { "locale": "en", "style": "familiar", "query": "product not visible website" },
  { "locale": "en", "style": "expert", "query": "product not visible site FAQ" },
  { "locale": "pt", "style": "naive", "query": "produtos não aparecendo" },
  { "locale": "pt", "style": "familiar", "query": "produto não visível no site" },
  { "locale": "pt", "style": "expert", "query": "produto não visível site FAQ" },
  { "locale": "es", "style": "naive", "query": "productos no aparecen" },
  { "locale": "es", "style": "familiar", "query": "producto no visible en el sitio" },
  { "locale": "es", "style": "expert", "query": "producto no visible sitio FAQ" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | why can't customers see my products |
| en | familiar | troubleshoot product not showing on storefront |
| en | expert | why is the product not visible on the website |
| pt | naive | por que os clientes não conseguem ver meus produtos |
| pt | familiar | solucionar problema de produto não aparecendo no storefront |
| pt | expert | por que o produto não está visível no site |
| es | naive | por qué los clientes no pueden ver mis productos |
| es | familiar | solucionar problema de producto que no aparece en el storefront |
| es | expert | por qué el producto no está visible en el sitio web |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "why can't customers see my products" },
  { "locale": "en", "style": "familiar", "query": "troubleshoot product not showing on storefront" },
  { "locale": "en", "style": "expert", "query": "why is the product not visible on the website" },
  { "locale": "pt", "style": "naive", "query": "por que os clientes não conseguem ver meus produtos" },
  { "locale": "pt", "style": "familiar", "query": "solucionar problema de produto não aparecendo no storefront" },
  { "locale": "pt", "style": "expert", "query": "por que o produto não está visível no site" },
  { "locale": "es", "style": "naive", "query": "por qué los clientes no pueden ver mis productos" },
  { "locale": "es", "style": "familiar", "query": "solucionar problema de producto que no aparece en el storefront" },
  { "locale": "es", "style": "expert", "query": "por qué el producto no está visible en el sitio web" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | Why can't my customers see the products I added to my VTEX store? |
| en | familiar | Why is my VTEX product not showing on the website? |
| en | expert | Why is the product not visible on the website in VTEX? |
| pt | naive | Por que os meus clientes não conseguem ver os produtos que adicionei à minha loja VTEX? |
| pt | familiar | Por que o meu produto VTEX não está aparecendo no site? |
| pt | expert | Por que o produto não está visível no site no VTEX? |
| es | naive | ¿Por qué mis clientes no pueden ver los productos que agregué a mi tienda VTEX? |
| es | familiar | ¿Por qué mi producto VTEX no aparece en el sitio web? |
| es | expert | ¿Por qué el producto no está visible en el sitio web en VTEX? |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "Why can't my customers see the products I added to my VTEX store?" },
  { "locale": "en", "style": "familiar", "query": "Why is my VTEX product not showing on the website?" },
  { "locale": "en", "style": "expert", "query": "Why is the product not visible on the website in VTEX?" },
  { "locale": "pt", "style": "naive", "query": "Por que os meus clientes não conseguem ver os produtos que adicionei à minha loja VTEX?" },
  { "locale": "pt", "style": "familiar", "query": "Por que o meu produto VTEX não está aparecendo no site?" },
  { "locale": "pt", "style": "expert", "query": "Por que o produto não está visível no site no VTEX?" },
  { "locale": "es", "style": "naive", "query": "¿Por qué mis clientes no pueden ver los productos que agregué a mi tienda VTEX?" },
  { "locale": "es", "style": "familiar", "query": "¿Por qué mi producto VTEX no aparece en el sitio web?" },
  { "locale": "es", "style": "expert", "query": "¿Por qué el producto no está visible en el sitio web en VTEX?" }
]
```


