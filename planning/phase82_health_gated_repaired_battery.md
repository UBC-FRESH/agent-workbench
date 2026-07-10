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
