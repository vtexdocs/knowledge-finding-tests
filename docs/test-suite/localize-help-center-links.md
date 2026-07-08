# Localize Help Center links in issue docs

Issue markdown files under [issues](./issues/) store `target_docs` and `other_helpful_docs` as JSON arrays in the metadata table. This script ensures every **Help Center** URL in those arrays has matching **en**, **pt**, and **es** variants, using slug data from the Help Center repo's `public/navigation.json`.

Developer Portal links (`developers.vtex.com`) are left unchanged.

## Requirements

- Python 3.10+
- A clone of [help-center-content](https://github.com/vtex-apps/help-center-content) (or equivalent) with `public/navigation.json`

## What it does

1. Scans all `*.md` files in the Issues directory.
2. For each `target_docs` and `other_helpful_docs` array entry:
   - Skips non-Help Center URLs (e.g. Developer Portal).
   - Parses Help Center URLs, including legacy shapes such as `/pt/tutorial/...`, paths without a locale prefix, and `docs/troubleshooting/...` (normalized to the `troubleshooting` prefix from navigation).
3. Looks up the article in `navigation.json` and builds canonical URLs:

   `https://help.vtex.com/{locale}/{slugPrefix}/{slugForLocale}`

   where `slugPrefix` comes from navigation (`docs/tutorials`, `docs/tracks`, `faq`, `troubleshooting`, `announcements`, `known-issues`). Tutorials and tracks use a `docs/...` prefix; other types do not.

4. Appends any missing localized URLs. Existing strings are kept (including alternate URL shapes).

## Usage

From the repository root (or any directory), with paths adjusted for your machine:

```bash
# Preview changes (default: no writes)
python "tools/test-suite/localize_help_center_links.py" \
  --navigation "/path/to/help-center-content/public/navigation.json"

# Apply updates to the issue markdown files
python "tools/test-suite/localize_help_center_links.py" \
  --navigation "/path/to/help-center-content/public/navigation.json" \
  --write
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--issues-dir` | `docs/test-suite/issues` (repository default) | Folder containing issue `.md` files |
| `--navigation` | `../help-center-content/public/navigation.json` relative to this **repository** root | Path to `navigation.json` |
| `--write` | off | When set, rewrites issue files; otherwise only prints planned additions |

If `--navigation` is omitted, the script assumes the Help Center repo sits beside this repo under the same parent folder (e.g. `Workspace/knowledge-finding-tests` and `Workspace/help-center-content`).

## Output and exit code

- Prints a **Changes** block: one line per event, `filename | field | added: <url>` or `filename | field | warn: <details>`.
- Prints **Unchanged files**: issue `.md` files where neither `target_docs` nor `other_helpful_docs` needed new URLs.
- **Summary** line: files scanned, URL additions count, unchanged file count.
- Exit code **1** if any warning occurred; **0** if all Help Center URLs resolved.

## Review

After `--write`, review the diffs: arrays may contain both legacy URLs (e.g. `/pt/tutorial/...`) and canonical ones (`/pt/docs/tutorials/...`). Remove duplicates manually if you want a minimal list.