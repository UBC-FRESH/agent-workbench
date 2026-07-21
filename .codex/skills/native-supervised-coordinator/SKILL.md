---
name: native-supervised-coordinator
description: Run a bounded Worker task through live native Agent Hub supervision in the current VS Code Coordinator session.
---

# Native supervised Coordinator

Use this skill only from the native Codex Coordinator session that will spawn
the Worker. Do not launch a CLI Coordinator, SDK, app-server, or external
controller.

## Mission invariant

Finish the developer's requested work. Delegation, supervision, validation,
and cost tracking support delivery; they do not replace it. A failed Worker
attempt is diagnostic input to a proportionate recovery decision, not a reason
to declare the job finished or make the developer manage internal workflow.
Report completion only when the requested working outcome exists, or name the
specific blocker that prevents it. For an explicitly frozen measurement run,
preserve and report a failed candidate at its declared no-repair boundary.

1. Default to the direct Coordinator-to-Worker topology: spawn exactly one
   Worker with `fork_context:false`; the Coordinator is the supervising
   authority and records its own native session ID as `supervisor_session_id`.
   Spawn an advisory Supervisor only when the user explicitly requests that
   three-agent topology. Do not infer an Advisor or Supervisor from an older
   plan, a role name, or a related task.
   The first spawned Worker consumes the run's only child slot. A transport,
   provider, or terminal failure before its first tool call does not authorize
   a replacement Worker or a new run ID. Inspect and report that same child's
   failure; use same-Worker input only while it remains active. Close the run
   as rejected when the child is terminal. Never manufacture parallel demand
   through automatic respawn.
2. Call `supervision_start_run` with only the current workspace root, exact
   Worker/supervising-authority session IDs, and an optional safe run ID before
   the Worker uses tools. Do not supply a `diagnostic_policy`: classifier
   configuration is not Coordinator-authored run intent.
3. Use the user's named task and acceptance inputs as the task boundary. Do not
   substitute a related workload, fixture, or validator from repository history.
   Give the Worker its bounded ticket. The default economic behavior is
   delegation, one actionable supervision check, then a single long Worker
   wait for terminal delivery. Do not turn normal `tool_completed` progress
   into a paid Coordinator conversation or a polling loop. If the actionable
   check returns ordinary progress, acknowledge it once and wait for the
   Worker; do not call `supervision_wait_delta` again unless a real failure,
   material repeat, directive deviation, or terminal condition is observed.
   If the supervision read itself fails or cannot provide a usable delta, do
   not treat that as permission for blind waiting: inspect the same Worker's
   actual command/result evidence and allowed-file diff. Continue waiting only
   while that evidence shows concrete forward work toward the named acceptance
   check. A repeated failed command, malformed or invalid allowed-file change,
   or scope drift requires a concise same-Worker correction; stop the Worker
   when its state worsens rather than consuming another unbounded wait.
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
P107 economics. Do not ask the Worker or Coordinator to calculate, price, or
assess economics. Their only economics handoff is the exact Coordinator and
Worker session IDs in the terminal report. The outer controller captures the
raw token checkpoints and invokes the established `agent-workbench
supervisor-tokens` ledger procedure after the run. Report that handoff as
`economics_pending_outer_controller`, never as “unavailable” or “unassessed.”
