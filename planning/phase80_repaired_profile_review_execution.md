# Phase 80: Repaired Profile Evidence Review Execution

Phase 80 executes the repaired profile-evidence-review live SDK battery
scaffolded by P79. The goal is to collect enough matched empirical evidence to
decide whether the P78/P79 repairs improved the weak P75 profile-evidence
review cells.

## Evidence From P79

P79 scaffolded a balanced 48-row matrix:

- two selected profiles;
- two overlays;
- three source-result strata;
- four matched public-safe P75 profile-run summary subjects per stratum.

The minimum meaningful repaired-cell decision threshold is 36 analyzable rows
with at least three matched source subjects per stratum for every
profile/overlay pair.

## Goal

Execute and aggregate the repaired 48-row battery.

## Smoke Gate

The first gate is 12 rows: one source subject per stratum across all four
profile/overlay pairs.

The smoke gate may authorize continuation only if:

- at least 10 of 12 rows produce a valid result or blocker artifact;
- the P78 profile-evidence-review contract remains valid;
- no repeated controller/provider blocker fires; and
- generated runtime evidence remains public-safe.

The smoke gate is not sufficient repaired-profile evidence by itself.

## Full Execution Boundary

Continue toward the full 48-row matrix only after the smoke gate passes.

If execution stops before 36 analyzable rows, report infrastructure/design
evidence only. If execution reaches at least 36 analyzable rows but not 48,
preserve at least three matched source subjects per stratum for every
profile/overlay pair before making any repaired-cell decision.

## Evidence Outputs

Expected ignored runtime outputs:

- SDK event logs;
- status summaries;
- result or blocker files;
- monitor summaries;
- compact transcripts;
- profile-run summaries;
- P74-compatible profile-evaluation dataset;
- P76 aggregate report;
- P77 repair-plan report.

Tracked closeout should promote only sanitized counts, recommendations, and
paths, not raw transcripts or worker outputs.

## Planned Tasks

- P80.1: Run execution readiness checks (#513).
- P80.2: Execute the 12-row smoke gate (#514).
- P80.3: Execute the remaining repaired-cell battery when the gate passes
  (#515).
- P80.4: Aggregate P80 evidence and decide the next lane (#516).

## Stop Rules

- Pause after two consecutive controller/provider failures with the same root
  cause in the same profile/overlay/stratum lane.
- Pause if more than 25 percent of rows are invalid for reasons unrelated to
  worker answer quality.
- Allow one bounded repair/retry only when the failure identifies a concrete
  manifest, ticket, profile, or controller defect.
- Do not claim repaired profile behavior from fewer than 36 analyzable rows.

