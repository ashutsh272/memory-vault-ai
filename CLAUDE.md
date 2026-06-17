# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**My Memory Vault** — a minimal, local-first personal knowledge management app. No build step, no framework. Three core files:

- `index.html` — all UI, parser, and API logic (vanilla JS, no dependencies)
- `vault.md` — single source of truth for all entries
- `server.py` — static file server + write API (Python stdlib only)

## Running locally

```bash
python3 server.py          # default port 8000
python3 server.py 9000     # optional custom port
# Then open http://localhost:8000/index.html
```

Always use `server.py`, not `python3 -m http.server` or `file://`. The server exposes the POST API that powers in-browser edits.

## Data format (`vault.md`)

```markdown
## Category: Learning
### Topic: AI
- **YYYY-MM-DD** — 1–2 line summary.
  - Optional detail bullets shown when expanded.
```

Rules:
- Two-level hierarchy: `## Category: <name>` → `### Topic: <name>` → dated entries.
- Entries are bullets; date is bold `**YYYY-MM-DD**`.
- Newest entry first within a topic.
- Each topic name must be unique across all categories (the API identifies topics by name only, not by category+name).

## Architecture

**`index.html`** — contains all UI + parser + fetch logic.
- `parseLearnings(markdown)` — pure function returning `{ categories: [{ name, topics: [{ name, entries: [{ date, summary, detail }] }] }] }`. Topics without a `## Category:` parent are assigned to a synthetic `'General'` category.
- `data` — module-level variable holding the last parsed result; `selectedTopic` holds the currently active topic name string.
- Fetches `vault.md` on `DOMContentLoaded`, parses into `data`, then calls `renderTopicList` (left panel) and `renderEntries` (right panel).
- Two-panel layout: left panel (category/topic list with drag-and-drop reordering), right panel (entries for selected topic).
- Category fold state persisted in `localStorage` under `cat-collapsed:<name>`.
- `makeEntryCard(topic, entry)` — builds the DOM for a single entry card including inline edit/delete controls.
- `apiPost(path, body)` — thin wrapper around `fetch` used by all mutation operations; always POSTs JSON.

**`server.py`** — extends `SimpleHTTPRequestHandler`.
- POST API routes: `/api/add-category`, `/api/add-topic`, `/api/add-entry`, `/api/delete-entry`, `/api/delete-topic`, `/api/delete-category`, `/api/rename-topic`, `/api/rename-category`, `/api/update-entry`, `/api/reorder-categories`, `/api/reorder-topics`
- Parses `vault.md` with four compiled regexes at module level: `IS_CATEGORY`, `IS_TOPIC`, `IS_ENTRY`, `IS_H2`.
- All mutations read-modify-write the file atomically via `_read()` / `_write()`.
- `add-entry` inserts the new bullet at `start + 1` (immediately after the `### Topic:` line), so new entries always appear first regardless of existing content.
- `delete-entry` cascades: auto-deletes the parent topic if it has no remaining entries, then the parent category if it has no remaining topics.
- Safety: reorder functions always append unlisted items at the end — never silently drop data.
- `add-entry` rejects duplicate dates for the same topic (returns HTTP 404 with `error: 'an entry for this date already exists'`).

## Other files

- `learnings.md` — legacy data file from the original single-topic version of the app; not served or used by the current UI.
- `prompts/PROMPT.md` — original product spec used to bootstrap the project; not relevant to ongoing development.
