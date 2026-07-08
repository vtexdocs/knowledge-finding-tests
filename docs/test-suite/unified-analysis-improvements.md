# Unified Analysis Improvements

| Field | Value |
| :---- | :---- |
| Created | Mar 24, 2026 |
| Updated | Mar 25, 2026 |
| Status | Informational |

This document lists improvements that would make the test suite better aligned with the unified analysis system proposed for Phase 1.

The main direction is simple:

1. Runners should collect **raw observable output**.
2. Issue docs should hold the **ground truth**.
3. The analysis system should compute **all evaluation logic**.

## 1. Design principles

Recommended principles for the whole test suite:

1. Keep runners dumb.
2. Keep issue metadata authoritative.
3. Keep raw outputs rich enough for later reprocessing.
4. Avoid duplicate evaluation logic across runners.
5. Prefer stable machine-readable fields over path-specific summaries.

In practice, that means runners should record what they saw, not what they think success means.

## 2. High-priority improvements

### 2.1 Remove legacy success evaluation from runners

Recommended changes:

1. Stop computing runner-side `found`, `rank`, `target_doc_url_found`, and similar fields.
2. Stop generating path-specific pass/fail conclusions from a legacy single target URL.
3. Treat any such fields as temporary compatibility data until they can be removed.

Why:

- Those fields duplicate logic that belongs in the analysis system.
- They are already inconsistent with `target_docs` and `other_helpful_docs`.
- They make it easier for future tooling to accidentally consume the wrong source of truth.

### 2.2 Deprecate `target_doc_url`

Recommended changes:

1. Remove `target_doc_url` from issue docs once dependent tooling is migrated.
2. Use only `target_docs` and `other_helpful_docs` as analysis inputs.
3. Update all runner docs to stop describing `target_doc_url` as the main evaluation field.

Why:

- The repo now has multiple confirmed cases where `target_doc_url` is not in `target_docs`.
- It encourages single-link thinking in a system that is explicitly multi-link and locale-aware.

### 2.3 Standardize around raw outputs

Each runner should preserve:

1. `issue_id`
2. `query`
3. `style`
4. `locale`
5. raw answer text when applicable
6. the exact ordered list of surfaced links
7. source context for links when applicable

Why:

- That gives the analysis system everything it needs.
- It avoids reruns when evaluation rules evolve.
- It supports reclassification, debugging, and cross-run comparison.

## 3. Runner-specific improvements

### 3.1 Internal search runners

Recommended changes:

1. Keep only the raw ranked search results and query metadata as authoritative output.
2. Drop or de-emphasize runner-side `summary_by_issue` success fields.
3. Preserve the full returned top list, even if the analysis system only evaluates top 7.
4. Keep variant identity explicit: `hybrid-search`, `algolia-helpcenter`, `algolia-devportal`.

Nice-to-have:

1. Add a stable query identifier per `(issue_id, locale, style)`.
2. Add a normalized result URL field if needed for debugging, but keep the original URL too.

### 3.2 Docs Assistant runner

Recommended changes:

1. Keep `answer_markdown` and the raw surfaced links.
2. Preserve link source explicitly as `markdown` vs `suggested_sources`.
3. Stop computing `target_doc_url_found` and `target_doc_url_rank`.
4. Keep ranks source-scoped and let the analysis system decide whether a combined ranking is also useful.

Nice-to-have:

1. Store the raw streamed event payload in a sidecar file for deep debugging.
2. Store locale and confidence exactly as returned by the product, without analysis interpretation.

### 3.3 External search runners

Recommended changes:

1. Store locale explicitly in each query result.
2. Keep style and query text with each returned result set.
3. Preserve the exact returned ordering and descriptions from the SERP.
4. Do not attempt runner-side matching against target docs.

Nice-to-have:

1. Record whether the result page was blocked by captcha or consent.
2. Distinguish empty results from blocked sessions in a structured field instead of burying it only in free text.

### 3.4 External LLM runners

Recommended changes:

1. Keep the raw answer markdown as the main artifact.
2. Keep extracted URLs, but treat them as extraction output rather than evaluation output.
3. Keep metadata counters based on final case outcomes, not attempt-level counts.
4. Do not compute success against `target_doc_url`.

Nice-to-have:

1. Write a machine-readable JSON sidecar per case in addition to markdown.
2. Store extraction provenance, such as `markdown_urls` vs `dom_urls`.
3. Record whether a case failed because of empty answer, no URLs, navigation error, auth issue, or timeout.

## 4. Issue metadata improvements

### 4.1 Make issue docs the single metadata authority

Recommended changes:

1. Treat issue markdown files as the canonical source for ground truth.
2. Keep `target_docs` and `other_helpful_docs` deduplicated.
3. Keep localized variants complete and consistent.
4. Remove legacy fields once migration is done.

### 4.2 Improve URL normalization readiness

Recommended changes:

1. Ensure the same document is represented consistently across localized variants.
2. Keep portal identity clear, especially between Help Center and Dev Portal.
3. Avoid mixing unrelated documents that happen to share similar slugs.
4. Define URL equivalence narrowly: same portal, same doctype, same exact slug, with locale segment treated as optional only when the slug itself is unchanged.

Nice-to-have:

1. Add a future `doc_family_id` or equivalent canonical document identifier.
2. Add an optional `surface` field if cross-portal grouping becomes important.

That would reduce reliance on URL heuristics in the analysis layer. Until then, the analysis system should not use broad "document family" matching across translated slugs. `https://help.vtex.com/docs/tracks/visao-geral-da-integracao-shopee` may match `https://help.vtex.com/pt/docs/tracks/visao-geral-da-integracao-shopee`, but it should not match the English or Spanish variants whose slugs are different, and a `tracks` URL must not match a `tutorials` URL with the same slug text.

## 5. Query data improvements

Recommended changes:

1. Keep `all_queries.json` focused on query workload definition.
2. Document clearly whether analysis should read ground truth from issue docs or from generated query files.
3. Add stable query identifiers if the team expects long-term baseline comparisons.

Avoid:

1. Packing partial evaluation metadata into generated query files.
2. Letting query generation become a second source of truth for target docs.

## 6. Documentation improvements

Recommended changes:

1. Update all test-suite docs to describe `target_docs` and `other_helpful_docs` as the legacy field names behind the target-doc and helpful-doc analysis model.
2. Mark `target_doc_url` as legacy anywhere it still appears.
3. State clearly that runner outputs are raw collection artifacts and the analysis system owns evaluation.
4. Keep one central reference for result layout and one central reference for normalized analysis concepts.

Nice-to-have:

1. Add a small glossary for terms like `target_doc`, `other_helpful_doc`, `link_source`, `variant`, and `coverage_status`.
2. Add an ingestion-contract doc for each path family.

## 7. Analysis-facing output improvements

Recommended changes:

1. Preserve raw output files as immutable collection artifacts.
2. Write analysis outputs to a separate processed area rather than back into raw run files.
3. Make the normalized analysis dataset reproducible from raw artifacts plus issue metadata.

Why:

- That keeps collection and evaluation cleanly separated.
- It makes changes to evaluation logic safe and auditable.
- It supports reprocessing historical runs without data loss.

## 8. Suggested implementation priority

If the team wants to improve alignment incrementally, this is the recommended order:

1. Stop depending on `target_doc_url` in analysis.
2. Remove runner-side success logic from new implementations.
3. Add locale explicitly to external-search raw outputs.
4. Fix metadata bookkeeping in the external LLM runner.
5. Standardize machine-readable raw output contracts across paths.
6. Deprecate and remove legacy issue metadata fields.

## 9. Final recommendation

The best long-term shape for the test suite is:

1. Issue docs define the problem and the ground truth.
2. Runners only collect what the user would see.
3. The analysis system computes all rankings, matches, pass rates, and classifications.

That separation will make the suite easier to evolve, easier to debug, and much more reliable for baseline comparisons.