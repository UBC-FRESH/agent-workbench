# Phase 82: Health-Gated Repaired Battery Execution

Phase 82 executes the repaired profile-evidence-review battery under the P81
controller/session health gate.

P82 exists because P80 stopped on repeated provider quota/controller errors and
P81 added a deterministic health-gate report. The next empirical spend should
be the full repaired battery only after live health preflight evidence is green.

## Goal

Execute the full repaired 48-row profile-evidence-review battery when the
controller/session health gate passes.

## Design Boundary

P82 preserves the P79/P80 matrix:

- two selected profiles;
- two overlays;
- three source-result strata;
- four matched source subjects per stratum; and
- 48 total repaired profile-evidence-review rows.

The minimum meaningful repaired-cell decision threshold remains 36 analyzable
rows with balanced stratum coverage. P82 must not replace the full battery with
another underpowered smoke.

## Health Preflight

P82 starts with a dedicated live SDK health probe. The probe is execution
readiness evidence only and is not repaired profile-evidence-review behavior
evidence.

Continue to the full 48-row battery only if:

- the probe creates readable SDK status and event evidence;
- `agent-workbench copilot-sdk health-gate` returns `go` for the probe; and
- the rendered probe evidence remains public-safe.

If the health gate returns `no-go`, stop before full battery execution and
record controller/session health evidence without weakening the design.

## Planned Tasks

- P82.1: Scaffold and validate the P82 execution runtime (#525).
- P82.2: Run the live health preflight (#526).
- P82.3: Execute the full repaired 48-row battery when health-gated (#527).
- P82.4: Aggregate evidence and decide the next lane (#528).

## Evidence Outputs

Expected ignored runtime outputs live under
`runtime/p82_health_gated_repaired_battery/`:

- fresh P82 matrix, manifests, tickets, and contracts;
- live health probe manifest, ticket, status, event, monitor, transcript, and
  profile-summary artifacts;
- health-gate JSON/Markdown reports;
- 48-row SDK event logs, status summaries, result/blocker files, monitor
  summaries, compact transcripts, and profile summaries if the health preflight
  passes;
- P74/P76-compatible profile-evaluation dataset;
- aggregate summary/report; and
- P77-style repair plan.

Tracked closeout should promote only sanitized counts, classifications,
recommendations, and repo-relative artifact paths.

## Stop Rules

- Stop before the full battery when the live health gate returns `no-go`.
- Stop after repeated controller/provider failures with the same sanitized root
  signature during full execution.
- Do not claim repaired profile-evidence-review behavior from fewer than 36
  analyzable rows.
- Do not silently narrow the matrix after controller/session health failures.

## Outcome

P82 scaffolded and validated a fresh ignored runtime under
`runtime/p82_health_gated_repaired_battery/`.

Scaffold validation:

- generated 48 repaired matrix manifests, tickets, and contracts;
- preserved all 12 profile/overlay/source-stratum cells with 4 rows per cell;
- validated all 48 matrix manifests before live execution;
- validated the separate live health-probe manifest; and
- confirmed the declared review-subject artifacts resolve from each generated
  manifest's base path.

The live health preflight passed:

- health-gate decision: `go`;
- controller health: 1 healthy probe row;
- repeated error signatures: none; and
- result status: `accepted-candidate`.

P82 then attempted all 48 repaired battery rows. Full-battery evidence showed:

- attempted rows: 48;
- analyzable result/blocker artifacts: 40;
- missing result/blocker artifacts: 8;
- controller health: 40 healthy, 8 unknown;
- repeated controller/provider error signatures: none;
- final status counts: 40 blocked, 8 missing; and
- balanced 3-per-cell threshold: not met, with minimum cell coverage of 2.

The rendered P82 aggregate and repair plan recommend repair before model-lane
expansion. The dominant finding is not provider quota exhaustion: P82's full
battery reached the provider, but the repaired profile-evidence-review task
still failed because workers could not reliably use the declared review-subject
artifact path through the SDK run context. The source artifacts exist from
manifest-relative resolution, so the next lane should repair review-subject
path/materialization or tool-access semantics before another repaired battery.

P82 does not support a repaired profile-evidence-review behavior claim because
the balanced analyzable threshold failed and every analyzable row wrote a
blocked artifact.
