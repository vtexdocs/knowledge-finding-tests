# Issue: Search and investigate audit events

| Field | Value |
|-------|--------|
| **issue_id** | audit-search-01 |
| **persona** | Decision maker |
| **product** | Audit / Storage |
| **user_intent** | Evaluate VTEX platform audit capabilities for security and compliance requirements. |
| **target_doc_url** | https://help.vtex.com/pt/docs/tutorials/audit |
| **surface** | help-center |
| **target_docs** | ["https://help.vtex.com/pt/tutorial/audit", "https://help.vtex.com/docs/tutorials/audit", "https://help.vtex.com/es/tutorial/audit", "https://developers.vtex.com/docs/guides/security", "https://help.vtex.com/en/docs/tutorials/audit", "https://help.vtex.com/pt/docs/tutorials/audit", "https://help.vtex.com/es/docs/tutorials/audit"] |
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
| en | naive | does vtex have audit logging capabilities |
| en | familiar | vtex audit trail security compliance |
| en | expert | vtex audit platform security features |
| pt | naive | o vtex tem recursos de registro de auditoria |
| pt | familiar | vtex trilha de auditoria segurança conformidade |
| pt | expert | vtex plataforma de auditoria recursos de segurança |
| es | naive | vtex tiene capacidades de registro de auditoría |
| es | familiar | vtex rastro de auditoría seguridad cumplimiento |
| es | expert | vtex plataforma de auditoría características de seguridad |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "does vtex have audit logging capabilities" },
  { "locale": "en", "style": "familiar", "query": "vtex audit trail security compliance" },
  { "locale": "en", "style": "expert", "query": "vtex audit platform security features" },
  { "locale": "pt", "style": "naive", "query": "o vtex tem recursos de registro de auditoria" },
  { "locale": "pt", "style": "familiar", "query": "vtex trilha de auditoria segurança conformidade" },
  { "locale": "pt", "style": "expert", "query": "vtex plataforma de auditoria recursos de segurança" },
  { "locale": "es", "style": "naive", "query": "vtex tiene capacidades de registro de auditoría" },
  { "locale": "es", "style": "familiar", "query": "vtex rastro de auditoría seguridad cumplimiento" },
  { "locale": "es", "style": "expert", "query": "vtex plataforma de auditoría características de seguridad" }
]
```

### B — Internal search (Algolia / Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | audit capabilities security |
| en | familiar | audit trail compliance |
| en | expert | audit |
| pt | naive | recursos de auditoria segurança |
| pt | familiar | trilha de auditoria conformidade |
| pt | expert | auditoria |
| es | naive | capacidades de auditoría seguridad |
| es | familiar | rastro de auditoría cumplimiento |
| es | expert | auditoría |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "audit capabilities security" },
  { "locale": "en", "style": "familiar", "query": "audit trail compliance" },
  { "locale": "en", "style": "expert", "query": "audit" },
  { "locale": "pt", "style": "naive", "query": "recursos de auditoria segurança" },
  { "locale": "pt", "style": "familiar", "query": "trilha de auditoria conformidade" },
  { "locale": "pt", "style": "expert", "query": "auditoria" },
  { "locale": "es", "style": "naive", "query": "capacidades de auditoría seguridad" },
  { "locale": "es", "style": "familiar", "query": "rastro de auditoría cumplimiento" },
  { "locale": "es", "style": "expert", "query": "auditoría" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | vtex docs on audit capabilities and security |
| en | familiar | vtex audit trail features |
| en | expert | audit |
| pt | naive | vtex docs sobre recursos de auditoria e segurança |
| pt | familiar | vtex recursos de trilha de auditoria |
| pt | expert | auditoria |
| es | naive | vtex docs sobre capacidades de auditoría y seguridad |
| es | familiar | vtex características de rastro de auditoría |
| es | expert | auditoría |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "vtex docs on audit capabilities and security" },
  { "locale": "en", "style": "familiar", "query": "vtex audit trail features" },
  { "locale": "en", "style": "expert", "query": "audit" },
  { "locale": "pt", "style": "naive", "query": "vtex docs sobre recursos de auditoria e segurança" },
  { "locale": "pt", "style": "familiar", "query": "vtex recursos de trilha de auditoria" },
  { "locale": "pt", "style": "expert", "query": "auditoria" },
  { "locale": "es", "style": "naive", "query": "vtex docs sobre capacidades de auditoría y seguridad" },
  { "locale": "es", "style": "familiar", "query": "vtex características de rastro de auditoría" },
  { "locale": "es", "style": "expert", "query": "auditoría" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | what audit capabilities does vtex provide |
| en | familiar | how does vtex handle audit trails and compliance |
| en | expert | what audit and security features are available in vtex |
| pt | naive | quais recursos de auditoria o vtex oferece |
| pt | familiar | como o vtex gerencia trilhas de auditoria e conformidade |
| pt | expert | quais recursos de auditoria e segurança estão disponíveis no vtex |
| es | naive | qué capacidades de auditoría ofrece vtex |
| es | familiar | cómo maneja vtex los rastros de auditoría y el cumplimiento |
| es | expert | qué características de auditoría y seguridad están disponibles en vtex |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "what audit capabilities does vtex provide" },
  { "locale": "en", "style": "familiar", "query": "how does vtex handle audit trails and compliance" },
  { "locale": "en", "style": "expert", "query": "what audit and security features are available in vtex" },
  { "locale": "pt", "style": "naive", "query": "quais recursos de auditoria o vtex oferece" },
  { "locale": "pt", "style": "familiar", "query": "como o vtex gerencia trilhas de auditoria e conformidade" },
  { "locale": "pt", "style": "expert", "query": "quais recursos de auditoria e segurança estão disponíveis no vtex" },
  { "locale": "es", "style": "naive", "query": "qué capacidades de auditoría ofrece vtex" },
  { "locale": "es", "style": "familiar", "query": "cómo maneja vtex los rastros de auditoría y el cumplimiento" },
  { "locale": "es", "style": "expert", "query": "qué características de auditoría y seguridad están disponibles en vtex" }
]
```


