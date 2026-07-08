# External Search

This folder holds **shared input** for External Search test runs and **project subfolders** for each search method.

## Contents

- **`all_queries.json`** — Canonical list of issues and queries for External Search. Used by runners in subfolders (e.g. Google Search API reads it from here).
- **`all_queries-*.json`** — Example or legacy output files (optional; new runs can write output into each project subfolder).

## Project subfolders

- **`Google Search API/`** — Runner that uses the Google Custom Search JSON API. See `Google Search API/README.md` for usage, credentials, and cost.
- **`Google Search Playwright/`** — Runner that simulates a user search on Google via Playwright (browser), no API key. See `Google Search Playwright/README.md`.

## Files that do **not** need to be inside a project folder to run

- **`all_queries.json`** — Stays here (External search). Runners reference it from the parent (e.g. `../all_queries.json` or default in script).
- **`all_queries-2026-03-04.json`**, **`all_queries-2026-03-05.json`** — Generated output; not required to run. They can stay here as history or be removed; new output is written inside each runner’s folder (e.g. `Google Search API/all_queries-{date}.json`).

To run the Google Search API runner, use the **`/run-google-search`** Cursor command or run the script from `Google Search API/` (see that folder’s README).
