# Phase 85: Health-Gated Repaired Profile-Evidence-Review Battery Rerun

Phase 85 returns to the full repaired profile-evidence-review battery after the
P83/P84 review-subject access repair.

P82 proved that the 48-row battery could reach the live SDK provider, but the
worker outputs were dominated by blocked final statuses because the declared
review-subject access path was not usable enough in live runs. P83 added
`agent_workbench_review_subject`, and P84 proved one live
profile-evidence-review worker requested and executed that tool successfully.

## Goal

Run the full health-gated repaired profile-evidence-review battery with the
P83/P84 declared review-subject access repair included.

## Scope

- Preserve the P79/P80/P82 48-row repaired battery design.
- Regenerate P85 runtime manifests, tickets, and contracts with
  `agent_workbench_review_subject` declared in custom tools.
- Run a live P81 health preflight before spending the 48-row battery.
- Execute all 48 rows only if the health gate returns `go`.
- Render ignored public-safe monitor, summary, aggregate, and evaluation
  evidence.
- Require at least 36 analyzable rows and balanced minimum cell coverage before
  making repaired profile-evidence-review behavior claims.

## Out Of Scope

- Reducing the matrix because the run is expensive.
- Model-lane expansion.
- Publishing raw transcripts, provider URLs, headers, credentials, personal
  paths, provider-side identifier strings, or raw worker blocker text.
- Treating the health probe as empirical profile-evidence-review behavior
  evidence.

## Design Requirements

P85 must preserve the empirical design rather than collapse it into another
smoke:

- 48 total repaired profile-evidence-review rows.
- Two selected profiles:
  - `agent-workbench-result-auditor`;
  - `agent-workbench-local-supervisor`.
- Two task overlays:
  - `release-readiness-review`;
  - `existing-code-debugging`.
- Three source result strata:
  - `accepted-candidate`;
  - `needs-supervisor-review`;
  - `blocked`.
- At least three rows per balanced cell.
- Fixed model lane: `operator-configured-copilot-sdk`.

## Stop Rules

- Do not start the 48-row battery unless the live health preflight gate returns
  `go`.
- If the health gate returns `no-go`, record the provider/controller-health
  evidence and stop before battery execution.
- If the health gate passes, attempt all 48 rows; do not silently narrow the
  sample after partial failures.
- Do not claim repaired profile-evidence-review behavior unless at least 36
  rows are analyzable and the balanced minimum cell coverage threshold is met.

## Planned Tasks

- P85.1: Define and activate the full repaired battery rerun (#544).
- P85.2: Generate the P85 runtime matrix, manifests, tickets, and contracts
  (#545).
- P85.3: Run the live health preflight (#546).
- P85.4: Execute and monitor the full repaired battery if the health gate
  passes (#547).
- P85.5: Evaluate and close out P85 (#543).

## Scaffold Status

P85.2 generated ignored runtime artifacts under
`runtime/p85_health_gated_repaired_battery_rerun/`.

Scaffold validation:

- row count: 48;
- manifest count: 48;
- profile counts: 24 `agent-workbench-local-supervisor`, 24
  `agent-workbench-result-auditor`;
- overlay counts: 24 `existing-code-debugging`, 24
  `release-readiness-review`;
- source-result stratum counts: 16 `accepted-candidate`, 16
  `needs-supervisor-review`, 16 `blocked`;
- balanced cells: 12;
- rows per cell: 4 minimum, 4 maximum;
- all 48 manifests validated;
- all 48 profile declarations validated; and
- every manifest declares `agent_workbench_review_subject`.

P85.2 also generated and validated the separate live health-probe manifest,
ticket, and contract under the same ignored runtime root. The health probe is
readiness evidence only and remains outside the 48-row empirical sample.

## Health Preflight Status

P85.3 ran the separate live health probe before the 48-row battery.

Health preflight evidence:

- probe run id: `p85_live_health_probe`;
- latest SDK status: `completion_candidate`;
- event count: 70;
- result artifact: present;
- blocker artifact: absent;
- final status: `accepted-candidate`;
- profile summary controller health: `healthy`;
- health-gate decision: `go`;
- healthy probe rows: 1; and
- repeated error signatures: none.

The full 48-row repaired battery is therefore allowed to start under the P85
stop rules.

## Execution Outcome

P85.4 executed all 48 repaired battery rows after the health gate passed.

Full-battery evidence:

- planned rows: 48;
- attempted rows: 48;
- start exit failures: 0;
- analyzable rows: 48;
- result artifacts: 48;
- blocker artifacts: 0;
- full-battery health-gate decision: `go`;
- controller health: 48 `healthy`;
- repeated error signatures: none;
- final status counts: 47 `accepted-candidate`, 1
  `needs-supervisor-review`, 0 `blocked`;
- accepted rate: 0.9792;
- source-balanced cells: 12;
- source-cell coverage: 4 rows minimum, 4 rows maximum;
- minimum analyzable threshold: met; and
- balanced cell threshold: met.

P85 therefore supports a repaired profile-evidence-review behavior claim for
the P83/P84 access-repaired contract. Compared with the P75
profile-evidence-review baseline, accepted rows increased from 2 to 47,
blocked rows decreased from 4 to 0, and needs-supervisor-review rows decreased
from 6 to 1.

The remaining needs-supervisor-review row should be audited as targeted
follow-up, not treated as a reason to rerun another contract-repair battery.

## Next Lane

The next development lane should move from contract repair back to replicated
comparison or model-lane evaluation using the repaired profile-evidence-review
contract. P85 remains a profile/task-contract battery and does not by itself
claim model superiority.
