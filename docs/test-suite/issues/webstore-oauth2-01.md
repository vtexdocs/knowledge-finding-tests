# Issue: Webstore (OAuth 2.0) — Custom login integration

| Field | Value |
|-------|--------|
| **issue_id** | webstore-oauth2-01 |
| **persona** | Developer |
| **product** | Login / Authentication / Webstore |
| **user_intent** | How to set up or integrate a custom OAuth identity provider for webstore login so customers can log in with an external IdP (e.g. company SSO, loyalty club). |
| **target_doc_url** | https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2 |
| **surface** | developers-portal |
| **target_docs** | ["https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2"] |
| **other_helpful_docs** | ["https://help.vtex.com/en/docs/tutorials/creating-an-oauth2-authentication", "https://help.vtex.com/pt/docs/tutorials/criar-autenticacao-oauth2", "https://help.vtex.com/es/docs/tutorials/crear-autenticacion-oauth2"] |
| **source** | Target document (command input) |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | let customers log in with our company login instead of creating a new account in VTEX |
| en | familiar | custom OAuth login for webstore VTEX identity provider |
| en | expert | VTEX webstore custom OAuth 2.0 integration guide |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "let customers log in with our company login instead of creating a new account in VTEX" },
  { "locale": "en", "style": "familiar", "query": "custom OAuth login for webstore VTEX identity provider" },
  { "locale": "en", "style": "expert", "query": "VTEX webstore custom OAuth 2.0 integration guide" }
]
```

### B — Internal search (Algolia/Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | custom login external identity |
| en | familiar | OAuth webstore identity provider configure |
| en | expert | login integration guide webstore OAuth2 |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "custom login external identity" },
  { "locale": "en", "style": "familiar", "query": "OAuth webstore identity provider configure" },
  { "locale": "en", "style": "expert", "query": "login integration guide webstore OAuth2" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | how can customers log in with our own login system |
| en | familiar | custom OAuth identity provider webstore setup |
| en | expert | webstore OAuth 2.0 login integration guide |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "how can customers log in with our own login system" },
  { "locale": "en", "style": "familiar", "query": "custom OAuth identity provider webstore setup" },
  { "locale": "en", "style": "expert", "query": "webstore OAuth 2.0 login integration guide" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | How do I let my VTEX store customers sign in with our existing user database? |
| en | familiar | How do I configure a custom OAuth provider for VTEX webstore login? |
| en | expert | How do I set up My Custom OAuth for the VTEX webstore following the OAuth2 flow? |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "How do I let my VTEX store customers sign in with our existing user database?" },
  { "locale": "en", "style": "familiar", "query": "How do I configure a custom OAuth provider for VTEX webstore login?" },
  { "locale": "en", "style": "expert", "query": "How do I set up My Custom OAuth for the VTEX webstore following the OAuth2 flow?" }
]
```


