# Memory Vault AI

A minimal, local-first vault for notes and learnings organised by **category → topic**. No build step, no framework — edit one Markdown file and refresh.

## Running locally

```bash
cd MyLearningJourney
python3 server.py
```

Open **http://localhost:8000/index.html** in your browser.

> **Note:** Always use `server.py` — not `python3 -m http.server` and not `file://`. The server serves static files and exposes the write API that powers in-browser edits and deletes.

---

## Data format (`vault.md`)

Entries are organised in two levels: **categories** (e.g. Learning, Ideas, ToDos) and **topics** within each category.

```markdown
## Category: Learning

### Topic: AI
- **YYYY-MM-DD** — One or two sentence summary.
  - Optional detail line one.
  - Optional detail line two.
- **YYYY-MM-DD** — Another entry (newest first).

### Topic: Cloud
- **YYYY-MM-DD** — Summary here.
```

| Element | Format |
|---|---|
| Category | `## Category: <name>` |
| Topic | `### Topic: <name>` (under a category) |
| Entry | `- **YYYY-MM-DD** — summary` |
| Detail | Indented lines beneath an entry |

---

## Adding content

### New entry in an existing topic

Find the `### Topic:` heading and add a bullet at the **top** (newest first):

```markdown
### Topic: AI
- **2026-06-04** — Discovered the --lock flag prevents accidental pruning.
- **2026-06-01** — Worktrees let multiple branches be checked out in parallel.
```

### New topic under an existing category

Add a `### Topic:` heading inside the relevant `## Category:` section:

```markdown
## Category: Learning
### Topic: Terraform
- **2026-06-04** — `terraform plan` previews changes without applying them.
```

### New category

Add a `## Category:` heading anywhere in the file:

```markdown
## Category: Security
### Topic: Zero Trust
- **2026-06-04** — Never trust, always verify — even inside the network perimeter.
```

Refresh the browser — the new category and topic appear automatically.

---

## Browser features

| Feature | How |
|---|---|
| Fold / unfold category | Click the category header — state persists across refreshes |
| Select topic | Click topic name in the left panel |
| Expand entry detail | Click the entry row (entries with detail have a ▼ chevron) |
| Reorder categories | Drag by the ⠿ handle in the left panel |
| Reorder topics | Drag by the ⠿ handle within a category |
| Rename category | Hover category → `✏` → type → Enter |
| Rename topic | Hover topic → `✏`, or click `✏` next to the topic title in the right panel |
| Edit entry | Hover entry → `✏` → edit summary / detail → Save (or Cmd+Enter) |
| Delete entry | Hover entry → `−` → confirm |
| Delete topic | Hover topic → `−` → confirm |
| Delete category | Hover category → `−` → confirm |
| Add category | Click `+ Category` at the bottom of the left panel |
| Add topic | Click `+` next to a category header, or `+ Topic` in the right panel header |
| Add entry | Click `+ Entry` in the right panel header |

All edits write through to `vault.md` immediately.

---

## File structure

```
MyLearningJourney/
├── index.html   # UI + parser + all browser logic (vanilla JS, no dependencies)
├── vault.md     # Source of truth — edit this directly or via the browser
├── server.py    # Static file server + write API (Python stdlib only)
└── README.md    # This file
```
