---
name: native-supervised-coordinator
description: Run a bounded Worker task through live native Agent Hub supervision in the current VS Code Coordinator session.
---

# Native supervised Coordinator

Use this skill only from the native Codex Coordinator session that will spawn
the Worker. Do not launch a CLI Coordinator, SDK, app-server, or external
controller.

1. Default to the direct Coordinator-to-Worker topology: spawn exactly one
   Worker with `fork_context:false`; the Coordinator is the supervising
   authority and records its own native session ID as `supervisor_session_id`.
   Spawn an advisory Supervisor only when the user explicitly requests that
   three-agent topology. Do not infer an Advisor or Supervisor from an older
   plan, a role name, or a related task.
2. Call `supervision_start_run` with the current workspace root and the exact
   Worker/supervising-authority session IDs before the Worker uses tools.
3. Use the user's named task and acceptance inputs as the task boundary. Do not
   substitute a related workload, fixture, or validator from repository history.
   Give the Worker its bounded ticket. The default economic behavior is
   delegation, one actionable supervision check, then a single long Worker
   wait for terminal delivery. Do not turn normal `tool_completed` progress
   into a paid Coordinator conversation or a polling loop. If the actionable
   check returns ordinary progress, acknowledge it once and wait for the
   Worker; do not call `supervision_wait_delta` again unless a real failure,
   material repeat, directive deviation, or terminal condition is observed.
4. In a three-agent run, resume the same Supervisor when needed and supply
   only the sanitized delta plus the fixed ticket boundary. In a direct run,
   the Coordinator performs that review itself. Neither route edits or messages
   the Worker except through the Coordinator's approved native delivery.
5. The Coordinator independently decides whether a cue is warranted. For a
   nudge, validate and record the packet/action, then use the Coordinator's
   own native same-Worker `send_input` capability.
6. Do not interrupt ordinary productive repair. At delivery, inspect the
   Worker diff, run the frozen validation, make the acceptance decision, and
   close the run. Stop there. Do not add exploratory reviews, repeated event
   acknowledgements, or extra evidence work unless a concrete acceptance or
   control-layer defect requires it.

Keep quality, protocol, and economics separate. This skill does not establish
P107 economics.
