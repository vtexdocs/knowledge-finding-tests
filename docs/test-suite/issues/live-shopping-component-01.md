# Issue: Place Live Shopping component on storefront

| Field | Value |
|-------|--------|
| **issue_id** | live-shopping-component-01 |
| **persona** | Store operator |
| **product** | Live Shopping / Storefront |
| **user_intent** | How to place the Live Shopping component on the storefront |
| **target_doc_url** | https://help.vtex.com/en/docs/tracks/placing-the-live-shopping-component |
| **surface** | help-center |
| **target_docs** | ["https://help.vtex.com/pt/tutorial/adicionar-componente-do-live-shopping", "https://help.vtex.com/docs/tutorials/placing-the-live-shopping-component", "https://help.vtex.com/es/tutorial/insertar-componente-de-live-shopping", "https://developers.vtex.com/docs/apps/vtexventures.livestreaming", "https://help.vtex.com/en/docs/tracks/placing-the-live-shopping-component", "https://help.vtex.com/pt/docs/tracks/adicionar-componente-do-live-shopping", "https://help.vtex.com/es/docs/tracks/insertar-componente-de-live-shopping"] |
| **other_helpful_docs** | ["https://developers.vtex.com/docs/guides/faststore/storefront-features-implementing-live-shopping-for-faststore", "https://developers.vtex.com/docs/guides/faststore/storefront-features-implementing-live-shopping-for-faststore-previous-versions"] |
| **source** | Command input (target document URL) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | how to add live video player to my VTEX ecommerce website |
| en | familiar | VTEX Live Shopping component setup storefront |
| en | expert | placing the Live Shopping component VTEX |
| pt | naive | como adicionar player de vídeo ao vivo no meu site de ecommerce VTEX |
| pt | familiar | configuração do componente Live Shopping VTEX storefront |
| pt | expert | inserir componente Live Shopping VTEX |
| es | naive | cómo agregar reproductor de video en vivo a mi sitio de ecommerce VTEX |
| es | familiar | configuración del componente Live Shopping VTEX storefront |
| es | expert | insertar componente Live Shopping VTEX |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to add live video player to my VTEX ecommerce website" },
  { "locale": "en", "style": "familiar", "query": "VTEX Live Shopping component setup storefront" },
  { "locale": "en", "style": "expert", "query": "placing the Live Shopping component VTEX" },
  { "locale": "pt", "style": "naive", "query": "como adicionar player de vídeo ao vivo no meu site de ecommerce VTEX" },
  { "locale": "pt", "style": "familiar", "query": "configuração do componente Live Shopping VTEX storefront" },
  { "locale": "pt", "style": "expert", "query": "inserir componente Live Shopping VTEX" },
  { "locale": "es", "style": "naive", "query": "cómo agregar reproductor de video en vivo a mi sitio de ecommerce VTEX" },
  { "locale": "es", "style": "familiar", "query": "configuración del componente Live Shopping VTEX storefront" },
  { "locale": "es", "style": "expert", "query": "insertar componente Live Shopping VTEX" }
]
```

### B — Internal search (Algolia/Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | add video player store |
| en | familiar | Live Shopping component storefront |
| en | expert | placing Live Shopping component |
| pt | naive | adicionar player de vídeo loja |
| pt | familiar | componente Live Shopping storefront |
| pt | expert | inserir componente Live Shopping |
| es | naive | agregar reproductor de video tienda |
| es | familiar | componente Live Shopping storefront |
| es | expert | insertar componente Live Shopping |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "add video player store" },
  { "locale": "en", "style": "familiar", "query": "Live Shopping component storefront" },
  { "locale": "en", "style": "expert", "query": "placing Live Shopping component" },
  { "locale": "pt", "style": "naive", "query": "adicionar player de vídeo loja" },
  { "locale": "pt", "style": "familiar", "query": "componente Live Shopping storefront" },
  { "locale": "pt", "style": "expert", "query": "inserir componente Live Shopping" },
  { "locale": "es", "style": "naive", "query": "agregar reproductor de video tienda" },
  { "locale": "es", "style": "familiar", "query": "componente Live Shopping storefront" },
  { "locale": "es", "style": "expert", "query": "insertar componente Live Shopping" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | how to put a live streaming player on my store page |
| en | familiar | add Live Shopping component to storefront VTEX |
| en | expert | placing the Live Shopping component |
| pt | naive | como colocar um player de transmissão ao vivo na minha página de loja |
| pt | familiar | adicionar componente Live Shopping ao storefront VTEX |
| pt | expert | inserir o componente Live Shopping |
| es | naive | cómo colocar un reproductor de transmisión en vivo en mi página de tienda |
| es | familiar | agregar componente Live Shopping al storefront VTEX |
| es | expert | insertar el componente Live Shopping |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to put a live streaming player on my store page" },
  { "locale": "en", "style": "familiar", "query": "add Live Shopping component to storefront VTEX" },
  { "locale": "en", "style": "expert", "query": "placing the Live Shopping component" },
  { "locale": "pt", "style": "naive", "query": "como colocar um player de transmissão ao vivo na minha página de loja" },
  { "locale": "pt", "style": "familiar", "query": "adicionar componente Live Shopping ao storefront VTEX" },
  { "locale": "pt", "style": "expert", "query": "inserir o componente Live Shopping" },
  { "locale": "es", "style": "naive", "query": "cómo colocar un reproductor de transmisión en vivo en mi página de tienda" },
  { "locale": "es", "style": "familiar", "query": "agregar componente Live Shopping al storefront VTEX" },
  { "locale": "es", "style": "expert", "query": "insertar el componente Live Shopping" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | How do I add a live video player to my VTEX online store homepage? |
| en | familiar | How do I add the Live Shopping component to my VTEX store? |
| en | expert | How do I place the Live Shopping component on my VTEX storefront? |
| pt | naive | Como adiciono um player de vídeo ao vivo à página inicial da minha loja VTEX? |
| pt | familiar | Como adiciono o componente Live Shopping à minha loja VTEX? |
| pt | expert | Como insiro o componente Live Shopping no meu storefront VTEX? |
| es | naive | ¿Cómo agrego un reproductor de video en vivo a la página de inicio de mi tienda VTEX? |
| es | familiar | ¿Cómo agrego el componente Live Shopping a mi tienda VTEX? |
| es | expert | ¿Cómo coloco el componente Live Shopping en mi storefront VTEX? |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "How do I add a live video player to my VTEX online store homepage?" },
  { "locale": "en", "style": "familiar", "query": "How do I add the Live Shopping component to my VTEX store?" },
  { "locale": "en", "style": "expert", "query": "How do I place the Live Shopping component on my VTEX storefront?" },
  { "locale": "pt", "style": "naive", "query": "Como adiciono um player de vídeo ao vivo à página inicial da minha loja VTEX?" },
  { "locale": "pt", "style": "familiar", "query": "Como adiciono o componente Live Shopping à minha loja VTEX?" },
  { "locale": "pt", "style": "expert", "query": "Como insiro o componente Live Shopping no meu storefront VTEX?" },
  { "locale": "es", "style": "naive", "query": "¿Cómo agrego un reproductor de video en vivo a la página de inicio de mi tienda VTEX?" },
  { "locale": "es", "style": "familiar", "query": "¿Cómo agrego el componente Live Shopping a mi tienda VTEX?" },
  { "locale": "es", "style": "expert", "query": "¿Cómo coloco el componente Live Shopping en mi storefront VTEX?" }
]
```


