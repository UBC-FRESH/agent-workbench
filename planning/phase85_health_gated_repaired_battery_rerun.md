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
- Two source result strata:
  - `accepted-candidate`;
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
