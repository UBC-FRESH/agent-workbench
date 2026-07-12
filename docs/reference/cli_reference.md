CLI Reference
============

Agent Workbench provides a command-line interface for evidence validation, heartbeat management, and task orchestration.

**Installation**: `pip install -e ".[dev]"`

**Main entry point**: ``agent-workbench``

The CLI includes subcommands for:

- Evidence summary validation and rendering (from Phase 23+)
- Heartbeat and nudge protocol management (from Phase 67+)
- Copilot session archive operations (from Phase 65+)
- Task validation, prompt generation, and review (from Phase 68+)

**Subcommand summary**: The CLI provides these main groups:

- **Evidence** (`validate`, `render`) — evidence summary validation and rendering (Phase 23+)
- **Heartbeat** (`heartbeat validate`, `heartbeat summarize`, `nudge suggest`) — heartbeat/nudge protocol management (Phase 67+)
- **Archive** (`copilot archive`) — Copilot session archive operations (Phase 65+)
- **Task** (`task-validate`, `task-prompt`, `task-review`) — task validation and prompt generation (Phase 68+)

For usage guides see the [guides](../guides/index) section.
