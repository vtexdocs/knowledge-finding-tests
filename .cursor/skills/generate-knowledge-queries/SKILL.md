---
name: generate-knowledge-queries
description: >-
  Generates naive/familiar/expert test-suite queries per query type (External
  search, Internal search, MCP, External LLMs) for a user issue or target doc,
  writes an issue markdown file, and optionally adds a spreadsheet row. Use when
  the user asks to generate knowledge-finding queries or create a new test-suite
  issue from a topic or documentation URL.
disable-model-invocation: true
---

# Generate knowledge-finding queries for the test suite

Generate query arrays for the testing phase: one **naive**, one **familiar**, and one **expert** query per **query type** (External search, Internal search, MCP, External LLMs), then optionally add the issue as a row to the test suite spreadsheet. Follow the structure in the source KR project's [Phase 1 Overview](https://github.com/vtexdocs/education-26h1-kr1/blob/main/docs/Planning/Phase%201/Phase%201%20Overview.md) (§3.3–§3.4).

## Input

The user may append parameters after invoking the skill (e.g. `guest checkout https://help.vtex.com/.../guest-checkout A B`).

1. **User issue OR target document** (required)
   - **User issue:** short description of the user intent (e.g. "How to enable guest checkout").
   - **Target document:** markdown content or URL of the doc that should be found. Use it to infer the user issue and generate queries that should surface this doc. If only a topic/description is provided without a URL, use the **vtexdocs MCP** to search for and retrieve the relevant VTEX documentation URL.

2. **Query type(s)** (optional, default: all)
   - One or more query types. If not provided, generate for **all** (A, B, C, D). To restrict, append letters (e.g. "A B C"):

   **A** — External search (Google)
   **B** — Internal search (Algolia/Proprietary API)
   **C** — MCP (proprietary docs)
   **D** — External LLMs

   Each maps to one array: `query_external`, `query_internal`, `query_mcp`, `query_llm`.

## Actions

### 1. Collect missing params

- If **user issue / target document** is missing: ask for a short user intent description or a target doc (markdown or URL).
- If **query type(s)** not provided: treat as **all** (A, B, C, D). Do not ask.

### 2. Generate queries

- If the user gave a **target document** (URL or markdown): infer the user issue (product, user intent, `target_doc_url`) from the doc; you may ask for `issue_id`, `persona`, and `product` if not inferrable.
- **target_doc_url:** if the user provided a topic/description but not a URL, use the **vtexdocs MCP** (`search_endpoints`/`get_endpoint_details` and `fetch_document`) to find and retrieve the relevant VTEX documentation URL. Use this URL as `target_doc_url`.
- **persona:** must be one of `'Developer'`, `'Store operator'`, `'Decision maker'`:
  - **`'Store operator'`** — admin panel tasks, catalog/payment/inventory/order management, configuration in the VTEX admin. E.g. "How to configure payment methods".
  - **`'Developer'`** — storefront customization, backoffice integration, APIs, technical implementation. E.g. "API integration".
  - **`'Decision maker'`** — platform capabilities, security, compliance, strategic evaluation. E.g. "VTEX security features".
  - If it cannot be inferred, ask the user which persona applies.
- For **each selected query type**, generate **exactly three queries**, one per style:
  - **naive** — plain-language goal; no product jargon. For external search (A) and external LLMs (D), even naive queries must include 'VTEX' explicitly.
  - **familiar** — some product/domain terms; not the exact feature name.
  - **expert** — official/canonical phrasing; close to doc/feature name.
- **Wording by query type:**
  - **External search (A):** natural-language. All A queries (naive, familiar, expert) must include 'VTEX' explicitly.
  - **Internal search (B):** short, keyword-style.
  - **MCP (C):** MCP-appropriate phrasing.
  - **External LLMs (D):** user-style questions. All D queries must include 'VTEX' explicitly.
- Output format per query type: array of objects `[{ "query": "...", "style": "naive"|"familiar"|"expert" }, ...]` with exactly 3 elements.

### 3. Create markdown document

- Create a new `.md` file (e.g. in `docs/test-suite/issues/`) containing:
  - **Issue:** `issue_id`, `persona`, `product`, `user_intent`, `target_doc_url` (and optional `source`).
  - **Queries:** for each selected query type, the type name and the three queries in a clear table or list.
- Save the file and tell the user where it is.

### 4. Ask about the spreadsheet

Ask: **Do you want this issue added as a new row in the test suite spreadsheet?**
- **Y** — yes, add a row (via the sheets MCP).
- **N** — no, only the Markdown doc.
- **L** — yes, but first show the row data so the user can paste it elsewhere.

### 5. If user said Y (add row)

- Use the sheets MCP tool `google_sheets_create_spreadsheet_row` to add one row with columns matching the data format (Phase 1 §3.4.1):
  - **Issue columns:** issue_id, persona, product, user_intent, target_doc_url (plain text).
  - **Query columns:** query_external, query_internal, query_mcp, query_llm. For each query type in scope, put the **stringified JSON array** of exactly 3 objects. Leave out-of-scope columns empty.
- **Spreadsheet:** pass `1PbbIDcIhRnBQJPQzA-N-lifxURH_ywohXUqd9nAldZg` (or the full URL). Default worksheet name = `Issues and queries`. Only ask for a different target if needed.
- In **instructions**, describe the row (issue fields + query arrays). Include **output_hint** (e.g. "confirmation that the row was created and its row number").

## Output

- **Always:** Markdown document with the issue and all generated queries for the selected query types.
- **If Y:** one new row in the test suite spreadsheet.
- **If L:** the row data shown in chat to copy.

## Reference

- Test suite spreadsheet ID: `1PbbIDcIhRnBQJPQzA-N-lifxURH_ywohXUqd9nAldZg`
- Query structure and types: [Phase 1 Overview](https://github.com/vtexdocs/education-26h1-kr1/blob/main/docs/Planning/Phase%201/Phase%201%20Overview.md) (§2, §3.3, §3.4, Appendix A), in the source KR project repo.
- Persona definitions and target proportions: [Phase 1 Overview](https://github.com/vtexdocs/education-26h1-kr1/blob/main/docs/Planning/Phase%201/Phase%201%20Overview.md) (§3.1), in the source KR project repo.
- Related skill: `localize-issue-queries`
