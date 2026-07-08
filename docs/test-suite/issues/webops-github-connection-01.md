# Issue: WebOps GitHub Connection

| Field | Value |
|-------|--------|
| **issue_id** | webops-github-connection-01 |
| **persona** | Developer |
| **product** | WebOps |
| **user_intent** | Learn how to connect WebOps to GitHub for version control and deployment |
| **target_doc_url** | https://developers.vtex.com/docs/guides/faststore/getting-started-2-starting-the-project |
| **surface** | developers-portal |
| **target_docs** | ["https://developers.vtex.com/docs/guides/faststore/getting-started-2-starting-the-project", "https://developers.vtex.com/docs/faststore/2-starting-the-project"] |
| **other_helpful_docs** | ["https://developers.vtex.com/docs/faststore/overview", "https://developers.vtex.com/docs/faststore/moving-your-faststore-project-to-a-new-github-repository", "https://developers.vtex.com/updates/release-notes/2024-09-09-updates-webops-permissions"] |
| **source** | Dev Portal |

> **Field descriptions:**
> - **target_docs**: All target-doc URLs that effectively solve the user issue (array of strings).
> - **other_helpful_docs**: Doc URLs that partially address the issue, or contain helpful information AND point to a target doc (array of strings).

---

## Queries by path

### A — External search (Google)

| locale | style | query |
|--------|-------|-------|
| en | naive | how do I link my VTEX website deployment tool to github |
| en | familiar | connect WebOps to GitHub repository |
| en | expert | VTEX WebOps GitHub integration setup guide |

**Array (query_external):**
```json
[
  { "locale": "en", "style": "naive", "query": "how do I link my VTEX website deployment tool to github" },
  { "locale": "en", "style": "familiar", "query": "connect WebOps to GitHub repository" },
  { "locale": "en", "style": "expert", "query": "VTEX WebOps GitHub integration setup guide" }
]
```

### B — Internal search (Algolia / Proprietary API)

| locale | style | query |
|--------|-------|-------|
| en | naive | github connect deployment |
| en | familiar | WebOps GitHub integration |
| en | expert | WebOps GitHub repository connection |

**Array (query_internal):**
```json
[
  { "locale": "en", "style": "naive", "query": "github connect deployment" },
  { "locale": "en", "style": "familiar", "query": "WebOps GitHub integration" },
  { "locale": "en", "style": "expert", "query": "WebOps GitHub repository connection" }
]
```

### C — Docs assistant API (MCP-backed)

| locale | style | query |
|--------|-------|-------|
| en | naive | How do I set up GitHub with my WebOps account? |
| en | familiar | What are the steps to integrate GitHub with WebOps? |
| en | expert | How to configure GitHub repository connection in VTEX WebOps? |

**Array (query_mcp):**
```json
[
  { "locale": "en", "style": "naive", "query": "How do I set up GitHub with my WebOps account?" },
  { "locale": "en", "style": "familiar", "query": "What are the steps to integrate GitHub with WebOps?" },
  { "locale": "en", "style": "expert", "query": "How to configure GitHub repository connection in VTEX WebOps?" }
]
```

### D — External LLMs

| locale | style | query |
|--------|-------|-------|
| en | naive | I'm using VTEX WebOps for my website and want to connect it to GitHub so I can manage my code there. How do I do that? |
| en | familiar | What's the process for connecting a VTEX WebOps project to a GitHub repository for version control? |
| en | expert | How do I configure GitHub integration in VTEX WebOps to enable repository-based deployments? |

**Array (query_llm):**
```json
[
  { "locale": "en", "style": "naive", "query": "I'm using VTEX WebOps for my website and want to connect it to GitHub so I can manage my code there. How do I do that?" },
  { "locale": "en", "style": "familiar", "query": "What's the process for connecting a VTEX WebOps project to a GitHub repository for version control?" },
  { "locale": "en", "style": "expert", "query": "How do I configure GitHub integration in VTEX WebOps to enable repository-based deployments?" }
]
```

## Notes

- These queries test knowledge retrieval across different query styles and channels for WebOps-GitHub integration
- Target documentation should cover authentication setup, repository linking, deployment configuration, and permissions
- Consider cross-referencing with WebOps CLI documentation and GitHub app installation guides


