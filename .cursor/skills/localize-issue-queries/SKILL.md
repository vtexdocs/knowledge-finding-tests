---
name: localize-issue-queries
description: >-
  Rewrites the query blocks in test-suite issue files into locale-aware blocks,
  translating help-center queries into pt and es and wrapping developers-portal
  queries as en-only. Use when the user asks to localize, translate, or make
  issue query blocks locale-aware in docs/test-suite/issues.
disable-model-invocation: true
---

# Localize Issue Query Blocks

For each issue file in scope, replace the existing query blocks (which have `{ "query", "style" }` objects) with locale-aware blocks that include `"locale"` as a key. For `help-center` issues, translate the English queries into Brazilian Portuguese (`pt`) and Spanish (`es`). For `developers-portal` issues, wrap the English queries in locale-aware objects with `"locale": "en"`.

Both the markdown table and the JSON array are updated in place. All other content (metadata, headings, separators) is left unchanged.

## Input

1. **Files to process** (optional, default: all)
   - One or more filenames from `docs/test-suite/issues/`. Filenames only — no path needed.
   - Example: `conciliations-payment-01.md checkout-api-orders-01.md`
   - If not provided, process **all** `.md` files in `docs/test-suite/issues/`.

## Actions

### 1. Collect files

- If filenames were provided: use those files from `docs/test-suite/issues/`.
- If none provided: list all `.md` files in `docs/test-suite/issues/` and process all.

### 2. For each file

#### 2.1 Read and detect surface

Read the file. Find the `surface` field in the metadata table or bullet list:
- `| **surface** | help-center |` (table format)
- `- **Surface:** help-center` (bullet format)

Locale coverage:
- `developers-portal` → `en` only
- `help-center` → `en`, `pt`, `es`

#### 2.2 Find query blocks

A **query block** is:
1. A markdown table with `style` and `query` columns.
2. Followed by a bold label ending with `:` on the next non-blank line.
3. Followed immediately by a fenced ```` ```json ```` code block.

There are exactly 4 query blocks per file. Identify each by its label or the nearest section heading:

| Path type | Label pattern | Heading keyword |
|-----------|---------------|-----------------|
| External search | `**Array (query_external):**` | "External Search" / "Google" |
| Internal search | `**Array (query_internal):**` | "Internal Search" / "Algolia" |
| MCP | `**Array (query_mcp):**` | "Docs assistant" / "MCP" |
| External LLMs | `**Array (query_llm):**` | "External LLMs" / "LLM" |

Some files use `**JSON Array:**` or `**Array format:**` as the label — identify the path type from the section heading above.

**Skip any block whose JSON already contains a `"locale"` key.** If all 4 blocks are already locale-aware, mark the file as `skipped` and move on.

#### 2.3 For each block that needs updating

**Extract EN queries:** parse the JSON array, extract the 3 objects in `naive → familiar → expert` order.

**Translate** (help-center only): using your own knowledge, translate the 3 EN queries into `pt` (Brazilian Portuguese) and `es` (Spanish).

Translation rules:
- Keep these terms in English: `VTEX`, `FastStore`, `WebOps`, `Algolia`, `API`, `PWA`, `CMS`, `SKU`, `OAuth`, `Shopee`, `SAP`, `boleto`.
- Preserve the style:
  - `naive` — casual, conversational, non-technical
  - `familiar` — semi-technical, knows the product
  - `expert` — concise, keyword-dense, technical
- Do not add punctuation or sentence structure not present in the original.

**Build the replacement block** with three parts in this exact order:

**Part 1 — Markdown table:**
```
| locale | style | query |
|--------|-------|-------|
| en | naive | <en naive query> |
| en | familiar | <en familiar query> |
| en | expert | <en expert query> |
| pt | naive | <pt naive query> |
| pt | familiar | <pt familiar query> |
| pt | expert | <pt expert query> |
| es | naive | <es naive query> |
| es | familiar | <es familiar query> |
| es | expert | <es expert query> |
```
For `developers-portal`: include only the 3 `en` rows.

**Part 2 — One blank line.**

**Part 3 — Original label + JSON code block:**
```json
[
  { "locale": "en", "style": "naive", "query": "<en naive query>" },
  { "locale": "en", "style": "familiar", "query": "<en familiar query>" },
  { "locale": "en", "style": "expert", "query": "<en expert query>" },
  { "locale": "pt", "style": "naive", "query": "<pt naive query>" },
  { "locale": "pt", "style": "familiar", "query": "<pt familiar query>" },
  { "locale": "pt", "style": "expert", "query": "<pt expert query>" },
  { "locale": "es", "style": "naive", "query": "<es naive query>" },
  { "locale": "es", "style": "familiar", "query": "<es familiar query>" },
  { "locale": "es", "style": "expert", "query": "<es expert query>" }
]
```
For `developers-portal`: include only the 3 `en` objects.

Object order: all `en` first, then `pt`, then `es`. Within each locale: `naive`, `familiar`, `expert`.

#### 2.4 Write back

Write the updated file to disk at the same path. Do not modify anything outside the query blocks.

### 3. Output summary

After processing all files, print:

| file | surface | status | notes |
|------|---------|--------|-------|
| conciliations-payment-01.md | help-center | updated | 4 blocks localized (pt + es) |
| checkout-api-orders-01.md | developers-portal | updated | 4 blocks wrapped (en only) |
| split-payment-01.md | help-center | skipped | already locale-aware |

Valid status values:
- `updated` — file was changed and written
- `skipped` — all blocks already had `"locale"` key
- `error` — describe what went wrong

## Error handling

- If a block's JSON cannot be parsed: skip that block, note it in the summary.
- If the `surface` field is missing: skip the file, mark as `error`.
- Do not halt on a single file failure — continue processing remaining files.

## Reference

- Issue files: `docs/test-suite/issues/`
- Surface + locale matrix: `developers-portal` → `en` only; `help-center` → `en`, `pt`, `es`
- Related skill: `generate-knowledge-queries`
