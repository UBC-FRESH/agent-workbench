# Phase 61 Packaged Local-Supervisor Workflow V1

## Purpose

P61 promotes the P57 pre-materialized graph-ticket pattern into the default
packaged local-supervisor workflow. The goal is to stop spending paid
coordinator attention on ad hoc setup rituals and to keep the local supervisor
focused on bounded audit, repair, validation, and compact reporting.

## Workflow Contract

The packaged workflow separates ownership by node type:

- coordinator-owned setup:
  - budget gate;
  - token checkpoint boundary;
  - graph ticket materialization;
  - audit-ticket pre-materialization;
- local-supervisor work:
  - artifact audit;
  - optional auditor subagent use when the ticket requires it;
  - compact report writing;
  - report repair using approved helpers only;
- deterministic validators:
  - authority validation;
  - document-artifact audit verification;
  - graph-report verification;
- paid-coordinator review:
  - inspect split outcome fields;
  - inspect escalation summaries;
  - decide whether to scale, repair, or stop.

## Default Launcher Posture

P61 makes pre-materialized audit tickets the default. In the default packaged
path, setup and materializer commands are coordinator-owned and are not part of
the local supervisor's action surface.

Legacy self-materialized mode remains available only through explicit opt-out
flags for debugging or controlled experiments.

## Run-ID Discipline

Live packaged bridge jobs require high-entropy job IDs. This protects evidence
from stale Copilot-session contamination and accidental reuse of generic run
labels such as `v1`.

Dry-runs and summary replays do not require high-entropy IDs because they do not
launch a live bridge session.

## Evidence Replay

P61 uses existing P57 summaries for replay coverage. It does not launch new
Copilot/Ollama jobs. Replayed P57 evidence must preserve the P60 distinction
between:

- accepted economics evidence;
- quality-valid protocol rejection;
- rejected output; and
- diagnostic-only economics records.

## Subagent Boundary

Subagent use remains advisory by default. A packaged ticket may require a
subagent for a specific node, but acceptance depends on deterministic artifacts
and validators, not on a model's prose claim that a subagent was used.
