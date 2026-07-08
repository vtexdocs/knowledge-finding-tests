# Results Layout

All test-suite runners now use the same directory convention for persisted outputs:

```text
results/<path-family>/<variant>/<run-folder>/...
```

## Canonical layout

| Path family | Variant | Example run folder |
|---|---|---|
| `internal-search/` | `algolia-helpcenter/` | `algolia-helpcenter 2026-03-17 14-49/` |
| `internal-search/` | `algolia-devportal/` | `algolia-devportal 2026-03-17 14-49/` |
| `internal-search/` | `hybrid-search/` | `hybrid-search 2026-03-17 14-53/` |
| `docs-assistant/` | `api/` | `docs-assistant 2026-03-17 16-23/` |
| `external-search/` | `google-search-playwright/` | `google-search-playwright 2026-03-24 15-37/` |
| `external-llms/` | `chatgpt/` | `external-llms-chatgpt 2026-03-04 22-26/` |
| `external-llms/` | `gemini/` | `external-llms-gemini 2026-03-05 19-39/` |

The run folder keeps the human-readable timestamp used by the collection scripts. The parent `variant` folder is the stable location the analysis system can target.

## Files inside each run folder

The exact artifacts still depend on the runner:

- Internal search: `<run-id>.json`, optional `analysis-<run-id>.md`, and for Hybrid Search optionally `internal-search-comparison-*.md`
- Docs Assistant: `<run-id>.json` and optional `analysis-<run-id>.md`
- External search: `results.json`
- External LLMs: `run_metadata.json` plus one markdown file per `(issue, locale, style)`

## Migration tool

Historical runs were not all written in this structure. To normalize the existing repository contents, use:

```powershell
python "tools/test-suite/standardize_results_layout.py" --write
```

Without `--write`, the script runs in dry-run mode and prints the planned moves.

## Notes

- The migration tool reorganizes folders only inside `results/`.
- Existing standardized folders are left in place.
- Legacy files are moved into the canonical layout so future analysis code can resolve runs consistently.
