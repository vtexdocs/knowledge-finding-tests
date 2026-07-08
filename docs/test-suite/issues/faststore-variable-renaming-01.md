# Issue: FastStore Variable Renaming

| Field | Value |
|-------|--------|
| **issue_id** | faststore-variable-renaming-01 |
| **persona** | Developer |
| **product** | FastStore |
| **user_intent** | Learn how to rename variables in a FastStore project |
| **target_doc_url** | https://developers.vtex.com/docs/guides/faststore/webops-managing-variables-and-secrets |
| **surface** | developers-portal |
| **target_docs** | ["https://developers.vtex.com/docs/guides/faststore/webops-managing-variables-and-secrets"] |
| **other_helpful_docs** | ["https://developers.vtex.com/docs/guides/faststore/1-onboarding-dashboard", "https://developers.vtex.com/updates/release-notes/2026-01-12-faststore-webops-enhanced-security-for-variables-and-secrets"] |
| **source** | Dev Portal |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | how do I change variable names in my VTEX faststore site |
| en | familiar | renaming variables faststore project |
| en | expert | FastStore variable renaming configuration |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "how do I change variable names in my VTEX faststore site" },
  { "locale": "en", "style": "familiar", "query": "renaming variables faststore project" },
  { "locale": "en", "style": "expert", "query": "FastStore variable renaming configuration" }
]
```

### B — Internal search (Algolia / Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | change variable names |
| en | familiar | rename variables faststore |
| en | expert | variable renaming faststore |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "change variable names" },
  { "locale": "en", "style": "familiar", "query": "rename variables faststore" },
  { "locale": "en", "style": "expert", "query": "variable renaming faststore" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | How can I change the names of variables in my FastStore project? |
| en | familiar | What's the process for renaming variables in FastStore? |
| en | expert | How do I rename FastStore project variables? |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "How can I change the names of variables in my FastStore project?" },
  { "locale": "en", "style": "familiar", "query": "What's the process for renaming variables in FastStore?" },
  { "locale": "en", "style": "expert", "query": "How do I rename FastStore project variables?" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | I need to change some variable names in my VTEX FastStore website, how do I do that? |
| en | familiar | What's the best way to rename variables in a FastStore project? |
| en | expert | How do I properly rename variables in FastStore while maintaining functionality? |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "I need to change some variable names in my VTEX FastStore website, how do I do that?" },
  { "locale": "en", "style": "familiar", "query": "What's the best way to rename variables in a FastStore project?" },
  { "locale": "en", "style": "expert", "query": "How do I properly rename variables in FastStore while maintaining functionality?" }
]
```

## Notes

- This issue focuses on variable renaming within FastStore projects, which may involve configuration files, component variables, or environment variables.
- Queries are designed to test whether different information retrieval systems can surface relevant documentation about FastStore's variable management and customization.


