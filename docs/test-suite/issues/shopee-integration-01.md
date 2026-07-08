# Issue: Shopee — Integrate store with Shopee

| Field | Value |
|-------|--------|
| **issue_id** | shopee-integration-01 |
| **persona** | Store operator |
| **product** | Marketplace / Integrations |
| **user_intent** | How to integrate my VTEX store with Shopee so I can sell on the Shopee marketplace. |
| **target_doc_url** | https://help.vtex.com/en/docs/tracks/install-and-configure-shopee-connector |
| **surface** | help-center |
| **target_docs** | ["https://help.vtex.com/pt/docs/tracks/visao-geral-da-integracao-shopee", "https://help.vtex.com/en/docs/tracks/integration-overview-shopee", "https://help.vtex.com/es/docs/tracks/resumen-de-integracion-shopee"] |
| **other_helpful_docs** | ["https://help.vtex.com/pt/docs/tracks/instalar-e-configurar-conector-shopee", "https://help.vtex.com/pt/docs/tracks/configuracoes-na-plataforma-vtex-shopee", "https://help.vtex.com/pt/docs/tracks/configurar-regra-de-divergencia-de-valores-shopee", "https://help.vtex.com/pt/docs/tracks/mapeamento-de-categorias-e-atributos-dos-produtos-para-a-shopee", "https://help.vtex.com/en/docs/tracks/install-and-configure-shopee-connector", "https://help.vtex.com/es/docs/tracks/instalar-y-configurar-el-conector-shopee", "https://help.vtex.com/en/docs/tracks/settings-on-the-vtex-platform-shopee", "https://help.vtex.com/es/docs/tracks/configuracion-en-la-plataforma-vtex-shopee", "https://help.vtex.com/en/docs/tracks/configuring-price-divergence-rule-shopee", "https://help.vtex.com/es/docs/tracks/configuracion-de-regla-de-divergencia-de-precios-shopee", "https://help.vtex.com/en/docs/tracks/mapping-product-categories-and-attributes-to-shopee", "https://help.vtex.com/es/docs/tracks/mapear-categorias-y-atributos-de-los-productos-para-shopee"] |
| **source** | Command input (user issue) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | connect my VTEX online store to Shopee so I can sell there |
| en | familiar | VTEX Shopee marketplace connector setup |
| en | expert | install and configure Shopee connector VTEX |
| pt | naive | conectar minha loja VTEX ao Shopee para vender lá |
| pt | familiar | configuração do conector de marketplace VTEX Shopee |
| pt | expert | instalar e configurar conector Shopee VTEX |
| es | naive | conectar mi tienda VTEX a Shopee para vender allí |
| es | familiar | configuración del conector de marketplace VTEX Shopee |
| es | expert | instalar y configurar conector Shopee VTEX |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "connect my VTEX online store to Shopee so I can sell there" },
  { "locale": "en", "style": "familiar", "query": "VTEX Shopee marketplace connector setup" },
  { "locale": "en", "style": "expert", "query": "install and configure Shopee connector VTEX" },
  { "locale": "pt", "style": "naive", "query": "conectar minha loja VTEX ao Shopee para vender lá" },
  { "locale": "pt", "style": "familiar", "query": "configuração do conector de marketplace VTEX Shopee" },
  { "locale": "pt", "style": "expert", "query": "instalar e configurar conector Shopee VTEX" },
  { "locale": "es", "style": "naive", "query": "conectar mi tienda VTEX a Shopee para vender allí" },
  { "locale": "es", "style": "familiar", "query": "configuración del conector de marketplace VTEX Shopee" },
  { "locale": "es", "style": "expert", "query": "instalar y configurar conector Shopee VTEX" }
]
```

### B — Internal search (Algolia/Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | connect store Shopee sell |
| en | familiar | Shopee connector configure marketplace |
| en | expert | install configure Shopee connector VTEX |
| pt | naive | conectar loja Shopee vender |
| pt | familiar | Shopee conector configurar marketplace |
| pt | expert | instalar configurar conector Shopee VTEX |
| es | naive | conectar tienda Shopee vender |
| es | familiar | Shopee conector configurar marketplace |
| es | expert | instalar configurar conector Shopee VTEX |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "connect store Shopee sell" },
  { "locale": "en", "style": "familiar", "query": "Shopee connector configure marketplace" },
  { "locale": "en", "style": "expert", "query": "install configure Shopee connector VTEX" },
  { "locale": "pt", "style": "naive", "query": "conectar loja Shopee vender" },
  { "locale": "pt", "style": "familiar", "query": "Shopee conector configurar marketplace" },
  { "locale": "pt", "style": "expert", "query": "instalar configurar conector Shopee VTEX" },
  { "locale": "es", "style": "naive", "query": "conectar tienda Shopee vender" },
  { "locale": "es", "style": "familiar", "query": "Shopee conector configurar marketplace" },
  { "locale": "es", "style": "expert", "query": "instalar configurar conector Shopee VTEX" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | how to connect my store to Shopee |
| en | familiar | configure Shopee connector marketplace integration |
| en | expert | install and configure Shopee connector |
| pt | naive | como conectar minha loja ao Shopee |
| pt | familiar | configurar conector Shopee integração de marketplace |
| pt | expert | instalar e configurar conector Shopee |
| es | naive | cómo conectar mi tienda a Shopee |
| es | familiar | configurar conector Shopee integración de marketplace |
| es | expert | instalar y configurar conector Shopee |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to connect my store to Shopee" },
  { "locale": "en", "style": "familiar", "query": "configure Shopee connector marketplace integration" },
  { "locale": "en", "style": "expert", "query": "install and configure Shopee connector" },
  { "locale": "pt", "style": "naive", "query": "como conectar minha loja ao Shopee" },
  { "locale": "pt", "style": "familiar", "query": "configurar conector Shopee integração de marketplace" },
  { "locale": "pt", "style": "expert", "query": "instalar e configurar conector Shopee" },
  { "locale": "es", "style": "naive", "query": "cómo conectar mi tienda a Shopee" },
  { "locale": "es", "style": "familiar", "query": "configurar conector Shopee integración de marketplace" },
  { "locale": "es", "style": "expert", "query": "instalar y configurar conector Shopee" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | How can I sell on Shopee with my VTEX store? |
| en | familiar | How do I set up the VTEX Shopee connector in Admin? |
| en | expert | How do I install and configure the Shopee connector for VTEX? |
| pt | naive | Como posso vender no Shopee com a minha loja VTEX? |
| pt | familiar | Como configuro o conector VTEX Shopee no Admin? |
| pt | expert | Como instalo e configuro o conector Shopee para VTEX? |
| es | naive | ¿Cómo puedo vender en Shopee con mi tienda VTEX? |
| es | familiar | ¿Cómo configuro el conector VTEX Shopee en Admin? |
| es | expert | ¿Cómo instalo y configuro el conector Shopee para VTEX? |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "How can I sell on Shopee with my VTEX store?" },
  { "locale": "en", "style": "familiar", "query": "How do I set up the VTEX Shopee connector in Admin?" },
  { "locale": "en", "style": "expert", "query": "How do I install and configure the Shopee connector for VTEX?" },
  { "locale": "pt", "style": "naive", "query": "Como posso vender no Shopee com a minha loja VTEX?" },
  { "locale": "pt", "style": "familiar", "query": "Como configuro o conector VTEX Shopee no Admin?" },
  { "locale": "pt", "style": "expert", "query": "Como instalo e configuro o conector Shopee para VTEX?" },
  { "locale": "es", "style": "naive", "query": "¿Cómo puedo vender en Shopee con mi tienda VTEX?" },
  { "locale": "es", "style": "familiar", "query": "¿Cómo configuro el conector VTEX Shopee en Admin?" },
  { "locale": "es", "style": "expert", "query": "¿Cómo instalo y configuro el conector Shopee para VTEX?" }
]
```


