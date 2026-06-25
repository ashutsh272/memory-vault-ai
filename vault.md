# My Memory Vault

## Category: Learning
### Topic: AI
#### Subtopic: Claude Code
- **2026-06-17T21:25:53** — Ralph loop allows to execute the agent loop in loop untill the goal is met or max iteration recahed- /plugin install ralph-loop@claude-plugins-official
  /ralph-loop - Keep working until a specific completion promise is output
  /goal - Keep working until a condition is verified (tests pass, lint clean)
  /loop - Repeat on a time interval (every 5 min, etc.)
  /batch - Spread one large task across parallel agents
- **2026-06-17T21:13:20** — claude --dangerously-skip-permissions — Runs Claude Code with all permission prompts disabled, letting it execute any action without asking for approval.
- **2026-06-17T20:53:02** — Open code and Open Router
  revisit later
- **2026-06-17T20:12:44** — Claude code commands like /init and /login /context all
  /login — Authenticates your session so Claude Code can access your account and begin working.
  Connects Claude Code to your Anthropic account via browser-based OAuth flow
  Only needs to be done once; credentials are stored securely for future sessions
  Required before any other Claude Code commands will work
  /init — Scans your codebase and generates a CLAUDE.md file that gives Claude persistent context about your project.
  Analyzes your project structure, dependencies, and key files automatically
  The generated CLAUDE.md acts as a memory file — Claude Code reads it at the start of every session
  Eliminates the need to re-explain your codebase each time you start a new conversation
  You can manually edit CLAUDE.md to add conventions, architecture notes, or anything Claude should always know
  /context — Shows a real-time visual breakdown of how much of Claude's context window is being used. Note - /context in GitHub Copilot CLI — Shows a visual breakdown of how much of the context window is being consumed, just like in Claude Code.
  /compact -  compact the context window
  /status - Show Claude codes version, model etc
  /model - Shows the model being used and allows to swtch between them.
  /rewind - Your session-level undo button that rolls back both code and conversation to any earlier checkpoint.
  /loop - Schedules a prompt or command to run automatically on a repeating interval within your current session.
#### Subtopic: MCP
#### Subtopic: Claude Agents SDK
#### Subtopic: Github Copilot

## Category: Ideas
### Topic: Jira Estimation Agent
#### Subtopic: Ideation
#### Subtopic: Planning
#### Subtopic: Architecture
#### Subtopic: Build
#### Subtopic: Evaluation
#### Subtopic: Deployment
#### Subtopic: Monitor
### Topic: MCP servres enablement
### Topic: Agentic Scrum team
### Topic: Digital Tech Lead

## Category: TODOs
### Topic: verify /conrtext for the governance agent
