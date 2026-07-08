# Issue: Manage sales associates in VTEX Sales App

| Field | Value |
|-------|--------|
| **issue_id** | sales-associates-salesapp-01 |
| **persona** | Store operator |
| **product** | VTEX Sales App / Omnichannel |
| **user_intent** | How to manage sales associates in VTEX Sales App (add, edit, inactivate) |
| **target_doc_url** | https://help.vtex.com/en/docs/tracks/managing-sales-associates-in-vtex-sales-app |
| **surface** | help-center |
| **target_docs** | ["https://help.vtex.com/pt/tutorial/gerenciar-vendedores-no-vtex-sales-app", "https://help.vtex.com/docs/tutorials/managing-sales-associates-in-vtex-sales-app", "https://help.vtex.com/es/tutorial/gestionar-vendedores-en-vtex-sales-app", "https://help.vtex.com/pt/docs/tracks/vtex-sales-app-configuracoes-basicas", "https://help.vtex.com/docs/tracks/vtex-sales-app-basic-settings", "https://help.vtex.com/es/docs/tracks/vtex-sales-app-configuracion-basica", "https://help.vtex.com/en/docs/tracks/managing-sales-associates-in-vtex-sales-app", "https://help.vtex.com/pt/docs/tracks/gerenciar-vendedores-no-vtex-sales-app", "https://help.vtex.com/es/docs/tracks/gestionar-vendedores-en-vtex-sales-app", "https://help.vtex.com/en/docs/tracks/vtex-sales-app-basic-settings"] |
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
| en | naive | how to add store employees to my VTEX point of sale app |
| en | familiar | VTEX Sales App add sales associates |
| en | expert | managing sales associates in VTEX Sales App |
| pt | naive | como adicionar funcionários da loja ao meu aplicativo VTEX de ponto de venda |
| pt | familiar | VTEX Sales App adicionar vendedores |
| pt | expert | gerenciar vendedores no VTEX Sales App |
| es | naive | cómo agregar empleados de tienda a mi app de punto de venta VTEX |
| es | familiar | VTEX Sales App agregar vendedores |
| es | expert | gestionar vendedores en VTEX Sales App |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to add store employees to my VTEX point of sale app" },
  { "locale": "en", "style": "familiar", "query": "VTEX Sales App add sales associates" },
  { "locale": "en", "style": "expert", "query": "managing sales associates in VTEX Sales App" },
  { "locale": "pt", "style": "naive", "query": "como adicionar funcionários da loja ao meu aplicativo VTEX de ponto de venda" },
  { "locale": "pt", "style": "familiar", "query": "VTEX Sales App adicionar vendedores" },
  { "locale": "pt", "style": "expert", "query": "gerenciar vendedores no VTEX Sales App" },
  { "locale": "es", "style": "naive", "query": "cómo agregar empleados de tienda a mi app de punto de venta VTEX" },
  { "locale": "es", "style": "familiar", "query": "VTEX Sales App agregar vendedores" },
  { "locale": "es", "style": "expert", "query": "gestionar vendedores en VTEX Sales App" }
]
```

### B — Internal search (Algolia/Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | add employees store app |
| en | familiar | sales associates Sales App |
| en | expert | managing sales associates VTEX Sales App |
| pt | naive | adicionar funcionários aplicativo loja |
| pt | familiar | vendedores Sales App |
| pt | expert | gerenciar vendedores VTEX Sales App |
| es | naive | agregar empleados app tienda |
| es | familiar | vendedores Sales App |
| es | expert | gestionar vendedores VTEX Sales App |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "add employees store app" },
  { "locale": "en", "style": "familiar", "query": "sales associates Sales App" },
  { "locale": "en", "style": "expert", "query": "managing sales associates VTEX Sales App" },
  { "locale": "pt", "style": "naive", "query": "adicionar funcionários aplicativo loja" },
  { "locale": "pt", "style": "familiar", "query": "vendedores Sales App" },
  { "locale": "pt", "style": "expert", "query": "gerenciar vendedores VTEX Sales App" },
  { "locale": "es", "style": "naive", "query": "agregar empleados app tienda" },
  { "locale": "es", "style": "familiar", "query": "vendedores Sales App" },
  { "locale": "es", "style": "expert", "query": "gestionar vendedores VTEX Sales App" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | how to register store staff in the sales app |
| en | familiar | add sales associate to VTEX Sales App |
| en | expert | managing sales associates in VTEX Sales App |
| pt | naive | como cadastrar funcionários da loja no sales app |
| pt | familiar | adicionar vendedor ao VTEX Sales App |
| pt | expert | gerenciar vendedores no VTEX Sales App |
| es | naive | cómo registrar personal de tienda en la sales app |
| es | familiar | agregar vendedor al VTEX Sales App |
| es | expert | gestionar vendedores en VTEX Sales App |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to register store staff in the sales app" },
  { "locale": "en", "style": "familiar", "query": "add sales associate to VTEX Sales App" },
  { "locale": "en", "style": "expert", "query": "managing sales associates in VTEX Sales App" },
  { "locale": "pt", "style": "naive", "query": "como cadastrar funcionários da loja no sales app" },
  { "locale": "pt", "style": "familiar", "query": "adicionar vendedor ao VTEX Sales App" },
  { "locale": "pt", "style": "expert", "query": "gerenciar vendedores no VTEX Sales App" },
  { "locale": "es", "style": "naive", "query": "cómo registrar personal de tienda en la sales app" },
  { "locale": "es", "style": "familiar", "query": "agregar vendedor al VTEX Sales App" },
  { "locale": "es", "style": "expert", "query": "gestionar vendedores en VTEX Sales App" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | How do I add my store employees to the VTEX Sales App so they can use it? |
| en | familiar | How do I add and manage sales associates in VTEX Sales App? |
| en | expert | How do I manage sales associates in VTEX Sales App? |
| pt | naive | Como adiciono os funcionários da minha loja ao VTEX Sales App para que possam usá-lo? |
| pt | familiar | Como adiciono e gerencio vendedores no VTEX Sales App? |
| pt | expert | Como gerencio vendedores no VTEX Sales App? |
| es | naive | ¿Cómo agrego los empleados de mi tienda al VTEX Sales App para que puedan usarlo? |
| es | familiar | ¿Cómo agrego y gestiono vendedores en VTEX Sales App? |
| es | expert | ¿Cómo gestiono vendedores en VTEX Sales App? |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "How do I add my store employees to the VTEX Sales App so they can use it?" },
  { "locale": "en", "style": "familiar", "query": "How do I add and manage sales associates in VTEX Sales App?" },
  { "locale": "en", "style": "expert", "query": "How do I manage sales associates in VTEX Sales App?" },
  { "locale": "pt", "style": "naive", "query": "Como adiciono os funcionários da minha loja ao VTEX Sales App para que possam usá-lo?" },
  { "locale": "pt", "style": "familiar", "query": "Como adiciono e gerencio vendedores no VTEX Sales App?" },
  { "locale": "pt", "style": "expert", "query": "Como gerencio vendedores no VTEX Sales App?" },
  { "locale": "es", "style": "naive", "query": "¿Cómo agrego los empleados de mi tienda al VTEX Sales App para que puedan usarlo?" },
  { "locale": "es", "style": "familiar", "query": "¿Cómo agrego y gestiono vendedores en VTEX Sales App?" },
  { "locale": "es", "style": "expert", "query": "¿Cómo gestiono vendedores en VTEX Sales App?" }
]
```


