# Prompt: My Learning Journey Portal

## Goal

Build a **minimal, local-first learning portal** that displays daily learnings **by topic**. Data lives in a **single Markdown file**; the HTML page **loads that file on every refresh** (no backend). The layout must stay simple as entries grow over time.

## Project structure (start here)

```
MyLearningJourney/
├── index.html          # UI + client-side load/parse/render
└── learnings.md        # Source of truth for all learnings
```

No build step, no framework, no database. Optional: a tiny `README.md` with how to add entries.

---

## Data format (`learnings.md`)

Use a **predictable, human-editable** structure. Example:

```markdown
# My Learning Journey

## Topic: Cursor Agent Skills
- **2025-06-03** — Skills are markdown files the agent reads when relevant.
  - Full notes: How to author SKILL.md, frontmatter, when to invoke.
- **2025-06-02** — Rules vs skills: rules are always-on; skills are on-demand.

## Topic: Git Worktrees
- **2025-06-01** — Worktrees let multiple branches checked out in parallel folders.
  - Full notes: `git worktree add`, cleanup, CI patterns.
```

**Rules for the MD schema:**

| Rule | Detail |
|------|--------|
| Topics | Second-level headings: `## Topic: <name>` |
| Entries | Bullet per learning; date in bold `**YYYY-MM-DD**` |
| Summary | First line after date (1–2 sentences max) — shown collapsed in UI |
| Detail | Optional indented bullets or text after summary — shown when expanded |
| Growth | New topics = new `## Topic:`; new days = new bullets under existing topic |
| Order | Newest entry first within a topic (recommended) |

Parser must tolerate: extra blank lines, topics with one entry, topics with no detail block.

---

## UI requirements (`index.html`)

### Layout

- Two columns: **left ~30%**, **right ~70%** (responsive: stack on narrow screens).
- **Left panel:** scrollable list of topic names from `learnings.md`.
- **Right panel:** content for **selected topic only**.

### Right panel behavior

- Default: placeholder (“Select a topic”) when none selected.
- For selected topic:
  - List each learning entry.
  - **Collapsed:** show only **1–2 line summary** (text before detail / first bullet body).
  - **Expandable:** click row or chevron to reveal full notes/detail.
  - Only one entry expanded at a time OR multiple — pick one behavior and document in HTML comment (prefer **multiple expand** for daily review).

### Left panel behavior

- Click topic → updates right panel; highlight active topic.
- First topic auto-selected on load if any exist.

### Load on refresh

- On `DOMContentLoaded`, `fetch('learnings.md')` (same directory).
- Handle errors: show friendly message if file missing or fetch blocked (note `file://` may block fetch — document **local server** in README: `python3 -m http.server`).

### Styling

- Clean, readable typography; subtle borders; no external CDN required (inline or `<style>` only).
- Accessible: keyboard focus on topics; `aria-expanded` on expandable rows.

### Implementation constraints

- Vanilla HTML, CSS, JavaScript only.
- Do not require Node/npm for v1.
- Parsing logic in one clear function, e.g. `parseLearnings(markdown) → { topics: [{ name, entries: [{ date, summary, detail }] }] }`.
- Keep parser **documented** with 2–3 example strings in a comment.

---

## Validation checklist (agent must verify)

### Functional

- [ ] With sample `learnings.md` (≥2 topics, ≥2 entries each, some with detail): left lists all topics.
- [ ] Selecting a topic shows only that topic’s entries in the right panel.
- [ ] Each entry shows 1–2 line summary when collapsed.
- [ ] Expand reveals full detail where present; entries without detail still work.
- [ ] Adding a new `## Topic:` and refreshing updates the UI.
- [ ] Adding a new dated bullet under existing topic and refreshing shows it.
- [ ] Empty `learnings.md` or no topics: empty state, no JS errors.

### Technical

- [ ] Page works when served via `python3 -m http.server` from project root.
- [ ] Console has no errors on load and on topic/expand interactions.
- [ ] `fetch` path is relative (`learnings.md`), not absolute.

### UX

- [ ] Active topic visually distinct.
- [ ] Long topic list scrolls in left panel only.
- [ ] Readable on mobile (stacked layout).

### Maintainability

- [ ] README explains: MD format, how to add daily learning, how to run local server.
- [ ] Comment in HTML points to MD schema section.

---

## Sample acceptance test (manual)

1. Start server in project root.
2. Open `http://localhost:8000/index.html`.
3. Confirm 2+ topics in left rail.
4. Click second topic — right panel updates.
5. Expand one entry — detail visible; collapse — summary only.
6. Edit `learnings.md`: add `## Topic: Test Topic` with one bullet; hard refresh — new topic appears.

---

## Out of scope (v1)

- Auth, cloud sync, search, tags, edit-in-browser, build pipelines.
- Git commit automation (user adds MD manually each day).

---

## Deliverables

1. `index.html` — complete UI + parser + fetch.
2. `learnings.md` — seed data (3 topics, 4–6 entries total).
3. `README.md` — run instructions + MD authoring guide.

Implement, then run through the validation checklist and fix any failing item before marking done.

---

## Optional follow-ups (do not implement unless asked)

- Search/filter by date or keyword.
- Sort topics A–Z vs last-updated.
- Import from daily note template.
- Dark mode toggle.
