# Issue: GitHub Repository Migration Between Organizations

| Field | Value |
|-------|--------|
| **issue_id** | github-repository-migration-01 |
| **persona** | Developer |
| **product** | WebOps / GitHub |
| **user_intent** | Learn how to migrate a repository from one GitHub organization to another |
| **target_doc_url** | https://developers.vtex.com/docs/guides/faststore/webops-moving-your-faststore-project-to-a-new-github-repository |
| **surface** | developers-portal |
| **target_docs** | ["https://developers.vtex.com/docs/faststore/moving-your-faststore-project-to-a-new-github-repository"] |
| **other_helpful_docs** | ["https://developers.vtex.com/docs/guides/faststore/monorepo-overview"] |
| **source** | Dev Portal |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | how to move a VTEX code repository to a different company account |
| en | familiar | migrate GitHub repository to another organization |
| en | expert | transfer GitHub repository ownership between organizations |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "how to move a VTEX code repository to a different company account" },
  { "locale": "en", "style": "familiar", "query": "migrate GitHub repository to another organization" },
  { "locale": "en", "style": "expert", "query": "transfer GitHub repository ownership between organizations" }
]
```

### B — Internal search (Algolia / Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | move repository organization |
| en | familiar | GitHub repo migration transfer |
| en | expert | repository organization transfer |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "move repository organization" },
  { "locale": "en", "style": "familiar", "query": "GitHub repo migration transfer" },
  { "locale": "en", "style": "expert", "query": "repository organization transfer" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | How do I move my repository to a different organization account? |
| en | familiar | What are the steps to transfer a GitHub repository between organizations? |
| en | expert | How to migrate GitHub repository ownership from one organization to another? |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "How do I move my repository to a different organization account?" },
  { "locale": "en", "style": "familiar", "query": "What are the steps to transfer a GitHub repository between organizations?" },
  { "locale": "en", "style": "expert", "query": "How to migrate GitHub repository ownership from one organization to another?" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | I need to move my GitHub repository from one company's GitHub account to another company's account in VTEX. How can I do this? |
| en | familiar | What's the process for migrating a GitHub repository from one organization to another organization while keeping all the history and issues? |
| en | expert | How do I transfer repository ownership between GitHub organizations and what are the implications for access controls, webhooks, and integrations? |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "I need to move my GitHub repository from one company's GitHub account to another company's account in VTEX. How can I do this?" },
  { "locale": "en", "style": "familiar", "query": "What's the process for migrating a GitHub repository from one organization to another organization while keeping all the history and issues?" },
  { "locale": "en", "style": "expert", "query": "How do I transfer repository ownership between GitHub organizations and what are the implications for access controls, webhooks, and integrations?" }
]
```

## Notes

- These queries test knowledge retrieval across different query styles and channels for GitHub repository migration between organizations
- Target documentation should cover the transfer process, permissions requirements, what gets transferred (history, issues, PRs), and what might be affected (webhooks, integrations, access controls)
- Consider cross-referencing with GitHub organization administration guides and repository settings documentation


