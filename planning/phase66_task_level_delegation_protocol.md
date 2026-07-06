# Phase 66: Task-Level Delegation Protocol

Phase 66 converts the P108 whole-phase delegation lesson into a stricter default
protocol: delegate one child task at a time, not an entire phase.

## Issue And Branch

- Parent issue: #431
- Child issues: #432, #433, #434, #435
- Branch: `feature/p66-task-level-delegation-protocol`

## Protocol Position

The coordinator owns the roadmap phase. The delegated local supervisor or worker
owns one named child task inside that phase.

Coordinator-owned responsibilities:

- create or verify the parent issue, child issues, branch, and roadmap section;
- choose the next child task and write the ticket;
- define allowed files, commands, model, permission mode, budget, heartbeat,
  result, blocker, archive, and token-ledger paths;
- inspect the worker result, filesystem, Git state, archive manifest, heartbeat
  file, and validation output;
- decide accept, reject, repair, escalate, or abandon;
- create commits, push branches, open PRs, merge PRs, close parent issues, and
  make final phase-completion claims.

Delegated-run responsibilities:

- execute only the assigned child task;
- append heartbeat records during work;
- write the requested result or blocker file;
- stop at the requested task boundary;
- avoid sibling tasks, parent closeout, and final completion claims unless they
  are the explicit assigned child task.

Whole-phase delegation remains experimental. It can be used only when the ticket
states that whole-phase behavior is the measured subject, and the coordinator
must still retain final acceptance, issue closure, PR merge, and parent-phase
completion authority.

## Artifacts Added

- `templates/task_delegation_ticket.md`
- `templates/task_result.schema.json`
- `templates/coordinator_decision_packet.schema.json`
- `templates/repair_ticket.md`

These files turn delegation into a repeatable task packet rather than a broad
chat request.

## Decision States

Coordinator decisions use five states:

- `accept`: the result satisfies the child task and may be integrated.
- `reject`: the result is not worth repairing for this lane.
- `repair`: a bounded repair ticket should be issued for exact defects.
- `escalate`: coordinator or maintainer attention is required before further
  delegation.
- `abandon`: the child task or lane should stop because the goal no longer
  justifies more work.

## P108 Retrospective

The P108 whole-phase delegated run showed that local Copilot/Ollama supervision
can complete meaningful work across a real development phase, but the broad
delegation unit created avoidable control-loop problems.

Success signals:

- the delegated agent performed substantial repository work;
- it could make progress after human nudges;
- the output was reviewable enough to reveal real implementation value rather
  than only chat behavior;
- the run produced a useful test case for local-supervisor delegation.

Control-loop failures:

- the delegated agent stalled and needed repeated `keep going` style nudges;
- housekeeping claims were weaker than the actual work performed;
- GitHub availability and closeout authority were confused despite `gh` being
  available;
- broad phase scope made it harder to tell when the agent should stop, repair,
  or report a blocker.

Implication:

Future default delegation should target one child task, with a fresh ticket,
heartbeat, result file, blocker file, archive manifest, and coordinator decision
packet for each run. Larger workflows can still be assembled, but they should
be assembled from auditable child-task runs.
