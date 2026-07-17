# Superseded P107.2 Retail Codex vs Agent Workbench Pilot Protocol

> Superseded by [P107 Configuration Economics Research Program](p107_economics_research_program.md).
> Do not materialize or launch its Retail-baseline run packet.

## Status and authority

This protocol supersedes the earlier P107.2 one-shot native measurement
description. The prior "one initial attempt, zero repair attempts" design is
not an A/B test of Agent Workbench behavior; it is retained only as historical
preflight evidence.

This file and
[the research objective and coordination protocol](p107_2_ab_research_objective_and_coordination_protocol.md)
are the governing design for the next P107.2 pilot. The pilot remains
preflight-only until a materialized run packet supplies the frozen identifiers
listed below and the deterministic contract validator accepts it.

## Research question

Does the complete Agent Workbench treatment produce an equally useful bounded
software feature with lower paid coordination cost and lower maintainer
steering burden than one fresh standard retail Codex agent?

The treatment is the complete hierarchy:

~~~text
Coordinator -> Luna Supervisor -> local Qwen Coder Worker
~~~

Active Coordinator verification and repair management are measured treatment
costs. They are not an external intervention or an excluded third lane.

## Pilot design

### Common frozen baseline

Before either lane starts, the Coordinator must materialize an ignored run
packet from the tracked P107.2 A/B run-packet template, then validate it with
the tracked run-packet validator. The materialized packet contains all of the
following:

- one exact clean starting commit;
- two newly created clean worktrees at that commit;
- one self-contained implementation ticket;
- a fixed list of files the implementation may change;
- a frozen acceptance-fixture directory outside both lane worktrees;
- SHA-256 hashes for the ticket, acceptance fixture, and usability rubric;
- the exact acceptance command; and
- a contamination manifest initialized before the lanes begin.

Neither lane may edit the acceptance fixture, ticket, or rubric. A changed
fixture hash, shared mutable checkout, cross-lane context leak, or Coordinator
implementation edit invalidates the affected lane. The only valid remedy is a
fresh lane from the common baseline; do not retrospectively combine or
"unmix" artifacts.

### Retail lane

One fresh standard retail Codex session receives the common ticket. It has no
conversation history from setup, the other lane, or any prior repair.

### Workbench lane

One fresh Coordinator session starts the native chain:

~~~text
Coordinator -> gpt_luna_supervisor -> ollama_qwen_coder_worker
~~~

Every spawn uses fork_context false and no model, reasoning, provider, or
service-tier override. Because the roles have no inherited context, every
Coordinator-to-Supervisor and Supervisor-to-Worker message must be
self-contained.

The Worker may make only the tracked-file changes and run only the commands
named in the ticket. The Coordinator may inspect worktrees, raw logs, diffs,
and acceptance output, but may not implement, patch, or otherwise perform a
Worker-owned change.

### Advisor review

The Advisor is the external lane-neutral reviewer. It is not the maintainer,
the Coordinator, or the Supervisor.

For each review, start a new Advisor Codex session. The Advisor receives only
the frozen baseline identifiers, lane worktree, common acceptance command,
rubric, and required review-result schema. It must not edit either lane or
manage a repair.

Advisor-review depth is a declared, measured soft stop condition, not a
model-exogenous constraint. The current P107 block sets each lane to at most
eight completed Advisor reviews: initial review plus up to seven repair cycles.
Every additional review and repair must record its incremental token classes,
catalog-backed USD, elapsed time, and Coordinator intervention. The Coordinator
may end early only for acceptance, a verified non-recoverable blocker, or a
documented economic stop decision. Extending beyond eight requires an explicit
maintainer authorization and a new declared cap epoch.

## Required control loop

For each lane, use this exact state machine:

~~~text
implement
  -> Supervisor artifact verification (Workbench only)
  -> fresh Advisor review
  -> accept | defect packet | verified blocker
  -> bounded repair, if a round remains
  -> fresh Advisor review
~~~

A Worker final message never ends the Workbench lane. The Supervisor must
inspect the actual changed files, diff, and required command output before
reporting to the Coordinator. The Coordinator must independently inspect the
same evidence before requesting Advisor review.

For an Advisor rejection, create a defect packet containing:

- review number and remaining review count;
- exact failed command and output;
- affected behavior and path;
- required acceptance condition;
- allowed files and commands; and
- contamination status.

The Retail packet goes directly to the fresh Retail session selected for its
repair. The Workbench packet goes to the Coordinator, which directs Luna; Luna
may spawn one fresh exact-role Worker for that repair and must verify the
artifact before returning. The maintainer is not the routine relay or
reviewer.

## Liveness

The Coordinator must not passively wait on a Worker or Supervisor. The run
packet must declare a liveness interval and an action for a missed interval:

- inspect the raw session log, worktree status, and heartbeat/artifact path;
- issue one bounded status nudge through the responsible parent role; or
- record a verified non-recoverable blocker.

Any nudge, defect packet, repair, or escalation is recorded as a named
intervention. A replacement Worker consumes one of the two available repair
cycles and must carry a complete self-contained correction.

## Evidence and economics

Record separately for each lane:

- fresh-session identifiers and raw-log paths;
- start/end token checkpoints for every paid role;
- elapsed time for implementation and each review/repair interval;
- local Worker runtime and model identity evidence;
- immutable fixture/ticket/rubric hashes;
- Advisor review records and defect packets;
- Coordinator, Supervisor, Advisor, Retail, and maintainer intervention
  counts by type;
- exact test output, diff output, and final worktree state; and
- pricing provenance when known.

The maintainer-steering metric is the count of maintainer-authored substantive
messages after the initial authorization. Routine session launch approvals are
recorded separately. Any maintainer-authored repair instruction, acceptance
judgment, or implementation change is an unplanned steering intervention.

## Verdict rules

- Useful completion requires frozen acceptance-command success and an Advisor
  practical-usability acceptance.
- If both lanes fail, the result is "no winner".
- A contaminated lane has no comparative verdict.
- A lane that is not useful cannot win by being cheaper.
- If both lanes are useful, compare paid token/cash cost, elapsed time, and
  maintainer steering burden. Include all Workbench Coordinator and Supervisor
  cost; do not count local Worker runtime as paid-model cost.
- One matched pair is a pilot signal only. It is not sufficient evidence for a
  project-wide economics claim.
