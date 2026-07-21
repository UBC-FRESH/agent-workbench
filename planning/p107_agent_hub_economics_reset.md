# P107 Agent Hub economics reset

## Thesis

P107 tests whether an Agent Hub can complete ordinary development work with
acceptable quality while materially reducing paid OpenAI lifecycle cost. It is
not a test of ceremonial coordination or agent-generated accounting.

## Common team mission

Every configuration receives only this operating mission:

> Complete the assigned development task to an acceptance-ready state. Inspect
> the workspace, implement the smallest correct change, run relevant checks,
> and fix defects you discover. Be honest about unresolved failures. Ask the
> developer only for product judgment or authority. Do not create reports,
> evidence packets, token accounting, commits, pushes, or GitHub changes.

The outer controller, not the team, captures raw sessions, provider/model
lineage, token/USD spans, elapsed time, initial/final workspace state,
deterministic validation, developer interventions, and rework.

## Mission guardrail: observe Agent Hub behavior; do not manufacture it

P107 evaluates whether a native Agent Hub configuration is useful in realistic
development work. The fixed ticket and its deterministic acceptance checks
measure the resulting repository artifact; they do **not** make the LLM team a
deterministic program, and they are not a demand that every configuration
produce the same implementation or pass on every run.

Once an evaluation block is frozen, treat model variance, incomplete work,
incorrect interpretations, failed checks, honest blockers, and rework as
quality observations. Do not respond by tightening the workload, adding
model-specific guardrails, repairing the candidate outside that configuration's
own ordinary task loop, or inventing a new proof ritual merely to obtain a
passing result. Those actions would destroy the comparison.

Repair only the outer control layer when it prevented the intended topology,
authority boundary, native-session observation, or accounting capture. Record
that as a protocol/instrumentation defect. Keep that repair separate from the
configuration's task-quality outcome, then start a new frozen block if the
repair changes the comparison conditions.

For a delegated configuration, record the actual control-plane route separately
from team behavior. Event-driven supervision is claimable only when the active
host provides both an evidenced Worker-event subscription and a supported
re-entry path to the exact Coordinator session. The current bounded P117
lease/journal/adapter proof is not itself that live attachment. Repeated paid
polling is a diagnostic transport, not evidence of event-driven supervision.

## Configurations

| ID | Team | Question |
| --- | --- | --- |
| C0 | Terra alone | Direct paid lifecycle baseline. |
| C1 | Terra Coordinator + Luna Worker, with Coordinator-owned P116 supervision | Does Luna displace Terra implementation work in a usable native Agent Hub workflow? |
| C2 | Terra Coordinator + Ollama Worker, with Coordinator-owned P116 supervision | Can zero-marginal-cost execution displace Terra work in a usable native Agent Hub workflow? |
| C3 | Luna alone | Is cheap direct execution sufficient for this task class? |
| C4 | Luna Coordinator + Ollama Worker | Can a mostly-free team complete work autonomously? |

Sol is not a routine execution reviewer. It is consulted only for a concrete
ambiguity or failed verification whose expected decision value justifies cost.

## Workloads and measures

Use ordinary, bounded, objective tasks: bug fixes, focused features, tests,
documentation corrections, and contained refactors. Exclude work requiring
credentials, GitHub authority, broad architecture choices, or product judgment.

For each matched task/topology, measure full lifecycle through accepted outcome:

- quality, protocol, and economics separately;
- total OpenAI USD/tokens and local-worker cost;
- time to accepted outcome;
- developer interventions and reasons;
- rework and failed-run spend;
- completion and honest-blocker rate.

Report mean and median lifecycle economics by workload type as observations
accumulate. No automatic run/retry cap applies.

## Immediate sequence

1. Preserve prior C0/C1 observations as diagnostics, not comparative evidence.
2. Select one ordinary task with deterministic acceptance and run a clean C0
   under the common mission.
3. Run matched C1 with one Luna Worker under the same mission and the active
   Coordinator-owned P116 control layer.
4. Run matched C2 with one Ollama Worker and the same control layer; inspect
   whether the Coordinator delegates substantive work without recreating it.
5. Compare accepted lifecycle outcomes; then extend to C3/C4 when those first
   delegation results show a useful direction.

The already-recorded C1 and C2 runs predate this correction and are retained as
unsupervised baseline observations. They do not demonstrate the usable native
control layer. A supervised C2 rerun is the immediate integration check; a
supervised C1 rerun is required before treating C1-versus-C2 cost or quality as
a matched comparison in this corrected epoch.

## Current execution state

C2 r7 completed the supervised integration check with accepted quality and
protocol. Its outer-controller ledger records a `$0.413974` paid-Coordinator
estimate and separate local-Worker usage. The developer has authorized C3 next:
one Luna/medium agent alone on the frozen V3 workload. C3 receives only the
common mission; the outer controller captures sessions, validation, and
economics. The remaining C1 rerun is still required before making any matched
C1-versus-C2 claim.
