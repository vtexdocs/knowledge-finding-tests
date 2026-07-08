---
name: register-issues-to-spreadsheet
description: >-
  Parses every issue markdown file in docs/test-suite/issues and registers each
  not-yet-present issue as a row in the test suite spreadsheet via the sheets
  MCP. Use when the user asks to register, sync, or bulk-upload issue docs to
  the test suite spreadsheet.
disable-model-invocation: true
---

# Register all issue docs to the test suite spreadsheet

Read all issue markdown files from `docs/test-suite/issues/`, parse their content, and register each issue as a new row in the test suite spreadsheet using the sheets MCP tool. Only register issues not already present (check by `issue_id`).

## Actions

### 1. Read all issue files

- List all `.md` files in `docs/test-suite/issues/`.
- Read each file to extract issue data and query arrays.

### 2. Parse each issue file

Each file has issue metadata in a markdown table at the top, and query arrays in JSON code blocks.

#### 2.1 Extract issue metadata from the table

Table format:
```
| Field | Value |
|-------|--------|
| **issue_id** | conditions-payment-01 |
| **persona** | Store operator |
| **product** | Payments |
| **user_intent** | How to configure special conditions... |
| **target_doc_url** | https://help.vtex.com/... |
```

- Find the table (starts with `| Field | Value |`).
- For each row, extract the value from the **second column**.
- Map `**issue_id**`, `**persona**`, `**product**`, `**user_intent**`, `**target_doc_url**` to variables.
- Extract the actual text value, not the markdown formatting. Strip whitespace.

#### 2.2 Extract query arrays from JSON code blocks

Each query type has a section like:
```
**Array (query_external):**
​```json
[
  { "query": "...", "style": "naive" },
  { "query": "...", "style": "familiar" },
  { "query": "...", "style": "expert" }
]
​```
```

- Search for patterns `**Array (query_external):**`, `**Array (query_internal):**`, `**Array (query_mcp):**`, `**Array (query_llm):**`.
- After each pattern, locate the next JSON code block and extract the entire array.
- Validate it's a valid array with exactly 3 objects (`query` + `style`).
- **Convert to a stringified single-line string** for the spreadsheet: `[{"query":"...","style":"naive"},{"query":"...","style":"familiar"},{"query":"...","style":"expert"}]`.
- If a query type is missing, use an empty string `""` for that column.

#### 2.3 Validate parsed data

- All required fields extracted: `issue_id`, `persona`, `product`, `user_intent`, `target_doc_url`.
- Each present query array is a valid JSON string with exactly 3 objects.
- Persona matches exactly: `Store operator`, `Developer`, or `Decision maker` (case-sensitive).

### 3. Check existing spreadsheet entries

- Use the sheets MCP to read existing `issue_id` values.
- **Spreadsheet ID:** `1PbbIDcIhRnBQJPQzA-N-lifxURH_ywohXUqd9nAldZg`
- **Worksheet:** `Issues and queries`
- Filter out issues already present (match by `issue_id`).

### 4. Register new issues

For each issue NOT already in the spreadsheet, use the sheets MCP tool `google_sheets_create_spreadsheet_row` with columns in this order:

1. `issue_id` — plain text
2. `persona` — plain text (`Store operator` | `Developer` | `Decision maker`)
3. `product` — plain text
4. `user_intent` — full description text
5. `target_doc_url` — full URL
6. `query_external` — stringified JSON array (or `""`)
7. `query_internal` — stringified JSON array (or `""`)
8. `query_mcp` — stringified JSON array (or `""`)
9. `query_llm` — stringified JSON array (or `""`)

**Critical:**
- Query columns must contain the actual stringified JSON array, never placeholder text like "arrays".
- Single-line string (no newlines; spaces OK), starting with `[` and ending with `]`, exactly 3 objects.
- Missing query type → empty string `""` (not `null`/`undefined`).
- Include an **output_hint**: "confirmation that the row was created with all 9 columns filled correctly, showing the row number".
- Process issues one at a time to avoid rate limiting.

### 5. Report results

- How many issues found.
- How many already in the spreadsheet (skipped).
- How many successfully added.
- Any issues that failed to parse or register (with error details).

## Reference

- Test suite spreadsheet ID: `1PbbIDcIhRnBQJPQzA-N-lifxURH_ywohXUqd9nAldZg`, worksheet `Issues and queries`.
- Issue files: `docs/test-suite/issues/*.md`
- Spreadsheet data format: [Phase 1 Overview](https://github.com/vtexdocs/education-26h1-kr1/blob/main/docs/Planning/Phase%201/Phase%201%20Overview.md) (§3.4.1), in the source KR project repo.
- Related skill: `generate-knowledge-queries`
