# Issue: My store order was not created

| Field | Value |
|-------|--------|
| **issue_id** | store-order-not-created-01 |
| **persona** | Store operator |
| **product** | Orders / Post-purchase / Store operations |
| **user_intent** | Troubleshoot why orders are not being created in the store |
| **target_doc_url** | https://help.vtex.com/en/troubleshooting/my-store-order-was-not-created |
| **surface** | help-center |
| **target_docs** | ["https://help.vtex.com/en/troubleshooting/my-store-order-was-not-created", "https://help.vtex.com/pt/troubleshooting/o-pedido-da-minha-loja-nao-foi-criado", "https://help.vtex.com/es/troubleshooting/no-se-ha-creado-el-pedido-de-mi-tienda"] |
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
| en | naive | VTEX order not created troubleshooting |
| en | familiar | VTEX store order creation error inventory |
| en | expert | my store order was not created VTEX |
| pt | naive | solução de problemas de pedido VTEX não criado |
| pt | familiar | erro de criação de pedido VTEX inventário |
| pt | expert | o pedido da minha loja não foi criado VTEX |
| es | naive | solución de problemas de pedido VTEX no creado |
| es | familiar | error de creación de pedido VTEX inventario |
| es | expert | el pedido de mi tienda no fue creado VTEX |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "VTEX order not created troubleshooting" },
  { "locale": "en", "style": "familiar", "query": "VTEX store order creation error inventory" },
  { "locale": "en", "style": "expert", "query": "my store order was not created VTEX" },
  { "locale": "pt", "style": "naive", "query": "solução de problemas de pedido VTEX não criado" },
  { "locale": "pt", "style": "familiar", "query": "erro de criação de pedido VTEX inventário" },
  { "locale": "pt", "style": "expert", "query": "o pedido da minha loja não foi criado VTEX" },
  { "locale": "es", "style": "naive", "query": "solución de problemas de pedido VTEX no creado" },
  { "locale": "es", "style": "familiar", "query": "error de creación de pedido VTEX inventario" },
  { "locale": "es", "style": "expert", "query": "el pedido de mi tienda no fue creado VTEX" }
]
```

### B — Internal search (Algolia / Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | order not created |
| en | familiar | order creation error inventory out of stock |
| en | expert | store order not created troubleshooting |
| pt | naive | pedido não criado |
| pt | familiar | erro de criação de pedido inventário sem estoque |
| pt | expert | pedido da loja não criado solução de problemas |
| es | naive | pedido no creado |
| es | familiar | error de creación de pedido inventario sin stock |
| es | expert | pedido de tienda no creado solución de problemas |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "order not created" },
  { "locale": "en", "style": "familiar", "query": "order creation error inventory out of stock" },
  { "locale": "en", "style": "expert", "query": "store order not created troubleshooting" },
  { "locale": "pt", "style": "naive", "query": "pedido não criado" },
  { "locale": "pt", "style": "familiar", "query": "erro de criação de pedido inventário sem estoque" },
  { "locale": "pt", "style": "expert", "query": "pedido da loja não criado solução de problemas" },
  { "locale": "es", "style": "naive", "query": "pedido no creado" },
  { "locale": "es", "style": "familiar", "query": "error de creación de pedido inventario sin stock" },
  { "locale": "es", "style": "expert", "query": "pedido de tienda no creado solución de problemas" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | vtex docs order not created troubleshooting |
| en | familiar | vtex store order creation error |
| en | expert | my store order was not created |
| pt | naive | vtex docs solução de problemas de pedido não criado |
| pt | familiar | vtex erro de criação de pedido na loja |
| pt | expert | o pedido da minha loja não foi criado |
| es | naive | vtex docs solución de problemas de pedido no creado |
| es | familiar | vtex error de creación de pedido en tienda |
| es | expert | el pedido de mi tienda no fue creado |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "vtex docs order not created troubleshooting" },
  { "locale": "en", "style": "familiar", "query": "vtex store order creation error" },
  { "locale": "en", "style": "expert", "query": "my store order was not created" },
  { "locale": "pt", "style": "naive", "query": "vtex docs solução de problemas de pedido não criado" },
  { "locale": "pt", "style": "familiar", "query": "vtex erro de criação de pedido na loja" },
  { "locale": "pt", "style": "expert", "query": "o pedido da minha loja não foi criado" },
  { "locale": "es", "style": "naive", "query": "vtex docs solución de problemas de pedido no creado" },
  { "locale": "es", "style": "familiar", "query": "vtex error de creación de pedido en tienda" },
  { "locale": "es", "style": "expert", "query": "el pedido de mi tienda no fue creado" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | why aren't orders being created in my VTEX store |
| en | familiar | how to fix order creation errors in VTEX when inventory is out of stock |
| en | expert | my VTEX store order was not created what should I check |
| pt | naive | por que os pedidos não estão sendo criados na minha loja VTEX |
| pt | familiar | como corrigir erros de criação de pedidos no VTEX quando o inventário está sem estoque |
| pt | expert | o pedido da minha loja VTEX não foi criado o que devo verificar |
| es | naive | por qué no se crean pedidos en mi tienda VTEX |
| es | familiar | cómo corregir errores de creación de pedidos en VTEX cuando el inventario está sin stock |
| es | expert | el pedido de mi tienda VTEX no fue creado qué debo verificar |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "why aren't orders being created in my VTEX store" },
  { "locale": "en", "style": "familiar", "query": "how to fix order creation errors in VTEX when inventory is out of stock" },
  { "locale": "en", "style": "expert", "query": "my VTEX store order was not created what should I check" },
  { "locale": "pt", "style": "naive", "query": "por que os pedidos não estão sendo criados na minha loja VTEX" },
  { "locale": "pt", "style": "familiar", "query": "como corrigir erros de criação de pedidos no VTEX quando o inventário está sem estoque" },
  { "locale": "pt", "style": "expert", "query": "o pedido da minha loja VTEX não foi criado o que devo verificar" },
  { "locale": "es", "style": "naive", "query": "por qué no se crean pedidos en mi tienda VTEX" },
  { "locale": "es", "style": "familiar", "query": "cómo corregir errores de creación de pedidos en VTEX cuando el inventario está sin stock" },
  { "locale": "es", "style": "expert", "query": "el pedido de mi tienda VTEX no fue creado qué debo verificar" }
]
```


