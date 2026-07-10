# Phase 79: Repaired Profile Evidence Review Battery

Phase 79 designs and scaffolds the repaired profile-evidence-review live
battery after P78 removed the self-referential review-subject defect. P79 is a
pre-execution phase: it prepares the matrix, manifests, and tickets so the
next live run starts from a declared empirical design rather than an ad hoc
smoke.

## Evidence From P78

P78 added a repaired `profile-evidence-review` ticket contract that requires a
pre-existing review subject artifact. It also updated
`agent-workbench-result-auditor` for selected-primary operation. The dogfood
ticket was valid, but P78 did not execute a live replicated battery. The next
empirical question is whether repaired tickets improve live result validity in
the weak P75 cells.

## Goal

Prepare a sufficiently replicated repaired-cell battery for live SDK execution.

## Design

Target matrix: 48 rows.

Fixed factors:

- selected profile:
  - `agent-workbench-local-supervisor`;
  - `agent-workbench-result-auditor`;
- task overlay:
  - `existing-code-debugging`;
  - `release-readiness-review`;
- task family:
  - `profile-evidence-review`;
- model lane:
  - `operator-configured-copilot-sdk`.

Review-subject factor:

- source result stratum:
  - `accepted-candidate`;
  - `needs-supervisor-review`;
  - `blocked`;
- four pre-existing public-safe P75 profile-run summary subjects per stratum.

The crossed design is:

`2 profiles * 2 overlays * 3 source-result strata * 4 matched subjects = 48 rows`.

The source subject is a matched blocking variable. Each selected
profile/overlay pair should review the same source subjects so downstream
comparison can separate profile/overlay behavior from subject difficulty.

Minimum analyzable sample:

- target: 48 analyzable rows;
- minimum for a useful repaired-cell decision: 36 analyzable rows, preserving
  at least 3 source subjects per stratum for every profile/overlay pair;
- below 36 rows, report infrastructure/design evidence only, not repaired
  profile behavior.

## Randomization And Blocking

Runtime order should rotate by:

1. source-result stratum;
2. source subject;
3. selected profile;
4. overlay.

The scaffold should write a randomized or rotated order explicitly. If runtime
budget forces narrowing, preserve source-subject replication before dropping
profiles or overlays. Do not drop the blocked source stratum first; it is the
highest-risk evidence lane from P75.

## Stop Rules

- Run an initial 12-row smoke gate: one source subject from each stratum across
  all four profile/overlay pairs.
- Continue only if at least 10 of 12 smoke rows produce valid result or blocker
  artifacts and the renderer/manifest contract remains valid.
- Pause after two consecutive controller/provider failures with the same root
  cause in the same profile/overlay/stratum lane.
- Pause if more than 25 percent of rows are invalid for reasons unrelated to
  worker answer quality.
- Allow one bounded repair/retry only when the failure identifies a concrete
  manifest, ticket, profile, or controller defect.
- Do not claim repaired profile behavior from fewer than 36 analyzable rows.

## Runtime Evidence Paths

Ignored runtime scaffold:

- matrix JSON: `runtime/p79_repaired_profile_review_battery/p79_run_matrix.json`;
- matrix preview:
  `runtime/p79_repaired_profile_review_battery/p79_run_matrix.md`;
- manifests:
  `runtime/p79_repaired_profile_review_battery/manifests/{run_id}.json`;
- tickets:
  `runtime/p79_repaired_profile_review_battery/tickets/{run_id}.md`;
- contracts:
  `runtime/p79_repaired_profile_review_battery/contracts/{run_id}.json`;
- future results:
  `runtime/p79_repaired_profile_review_battery/results/{run_id}.md`;
- future blockers:
  `runtime/p79_repaired_profile_review_battery/blockers/{run_id}.md`.

## Planned Tasks

- P79.1: Activate roadmap and planning surfaces (#508).
- P79.2: Define repaired-cell factorial design (#509).
- P79.3: Scaffold repaired battery artifacts (#510).

## Validation Boundary

P79 can prove that the repaired live-battery artifacts are internally
consistent, public-safe, and sufficiently replicated on paper. It cannot prove
improved profile behavior until the 48-row battery, or at least the 36-row
minimum, is executed and aggregated.

## P79 Outcome

P79 scaffolded the repaired battery under ignored runtime storage:

- matrix JSON:
  `runtime/p79_repaired_profile_review_battery/p79_run_matrix.json`;
- matrix preview:
  `runtime/p79_repaired_profile_review_battery/p79_run_matrix.md`;
- 48 manifests under
  `runtime/p79_repaired_profile_review_battery/manifests/`;
- 48 repaired tickets under
  `runtime/p79_repaired_profile_review_battery/tickets/`;
- 48 contract JSON files under
  `runtime/p79_repaired_profile_review_battery/contracts/`.

The generated matrix is balanced:

- profiles:
  - `agent-workbench-local-supervisor`: 24 rows;
  - `agent-workbench-result-auditor`: 24 rows;
- overlays:
  - `existing-code-debugging`: 24 rows;
  - `release-readiness-review`: 24 rows;
- source-result strata:
  - `accepted-candidate`: 16 rows;
  - `needs-supervisor-review`: 16 rows;
  - `blocked`: 16 rows;
- 12 profile/overlay/stratum cells, each with 4 matched source subjects.

The scaffold uses existing P75 public-safe profile-run summaries as
pre-existing review subjects. Public-safety inspection found no personal paths,
provider URLs, or token-like values in the generated matrix, tickets, or
contracts.

The next phase should execute the repaired 48-row battery. If execution limits
force narrowing, the minimum meaningful result remains 36 analyzable rows with
at least three matched source subjects per stratum for every profile/overlay
pair.
