# My Learning Journal

## Category: Cloud
### Topic: Git Worktrees
- **2026-06-01** — Worktrees let multiple branches be checked out in parallel folders.
  - Run `git worktree add ../feature-branch feature-branch` to create one.
  - Each worktree shares the same `.git` history but has an independent working tree.
  - Clean up with `git worktree remove <path>` when done.
- **2026-05-30** — Worktrees are useful in CI to avoid stashing or switching branches mid-pipeline.

### Topic: Docker Networking
- **2026-06-01** — Bridge networks allow containers on the same host to communicate by name.
  - Use `docker network create mynet` and `--network mynet` on `docker run`.
- **2026-05-28** — Host networking (`--network host`) removes isolation; use only for performance-critical services.

## Category: AI
### Topic: Cursor Agent Skills
- **2026-06-03** — Skills are invoked on-demand; the agent reads the SKILL.md file only when relevant.
  - Skills are authored as markdown with frontmatter (name, description, trigger).
  - Rules differ: they are always-on context injected into every prompt.
- **2026-06-02** — Rules vs skills: rules are always-on; skills are on-demand.
  - Rules live in `.cursor/rules/` or `.cursorrules`.
  - Skills live in a skills directory and are loaded selectively.

### Topic: Claude Code
- **2026-06-03** — Claude Code is Anthropic's official CLI for agentic coding tasks.
  - Supports hooks for automated behaviours (pre/post tool-call shell commands).
  - MCP servers extend its capabilities with custom tools.
- **2026-06-02** — The /init skill generates a CLAUDE.md to onboard future Claude instances to a repo.
- **2026-05-29** — Prompt caching in the Claude API reduces latency and cost for repeated context.
  - Use `cache_control: { type: "ephemeral" }` on large static blocks (system prompt, docs).

## Category: Banking
### Topic: Core Banking Systems
- **2026-06-02** — Core banking systems process daily transactions and update accounts in real time.
  - Major vendors: Temenos T24, Oracle FLEXCUBE, FIS Profile.
  - APIs typically expose REST or ISO 20022 message formats.
- **2026-06-01** — ISO 20022 is the global standard for financial messaging, replacing SWIFT MT formats.

### Topic: Payment Rails
- **2026-06-03** — SWIFT gpi tracks cross-border payments end-to-end with a unique transaction reference (UETR).
- **2026-05-31** — Faster Payments (UK) and FedNow (US) enable near-instant domestic transfers under defined limits.
  - FedNow launched July 2023; participation is opt-in for US banks.
