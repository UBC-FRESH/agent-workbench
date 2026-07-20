---
name: native-supervised-coordinator
description: Run a bounded Worker task through live native Agent Hub supervision in the current VS Code Coordinator session.
---

# Native supervised Coordinator

Use this skill only from the native Codex Coordinator session that will spawn
the Worker. Do not launch a CLI Coordinator, SDK, app-server, or external
controller.

1. Spawn exactly one Worker and one advisory Supervisor with `fork_context:false`.
2. Call `supervision_start_run` with the current workspace root and the exact
   Worker/Supervisor session IDs before the Worker uses tools.
3. Give the Worker its bounded ticket. While it works, call
   `supervision_wait_delta` for meaningful new evidence. Do not wait for a
   terminal report before reviewing a failure, validation result, material
   repeat, directive deviation, or terminal event.
4. Resume the same Supervisor when needed and supply only the sanitized delta
   plus the fixed ticket boundary. The Supervisor advises; it does not edit or
   message the Worker.
5. The Coordinator independently decides whether a cue is warranted. For a
   nudge, validate and record the packet/action, then use the Coordinator's
   own native same-Worker `send_input` capability.
6. Do not interrupt ordinary productive repair. Close the run with
   `supervision_close_run` after the Worker reaches its ticket stop condition.

Keep quality, protocol, and economics separate. This skill does not establish
P107 economics.
