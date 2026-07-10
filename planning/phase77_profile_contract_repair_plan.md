# Phase 77: Profile Contract Repair Plan

Phase 77 converts the P75/P76 aggregate evidence into a deterministic repair
plan before spending on another live SDK battery. P75 showed that controller
health was stable enough for replicated collection, while P76 showed that
result validity is concentrated in weak task/profile cells.

## Evidence From P75 And P76

P75 produced 24 analyzable rows with healthy controller status for every row.
Result validity was mixed:

- 9 accepted-candidate rows;
- 11 needs-supervisor-review rows;
- 4 blocked rows.

P76 aggregated those rows and identified the strongest repair signal:

- `manifest-contract-audit`: 7 accepted-candidate, 5 needs-supervisor-review,
  0 blocked;
- `profile-evidence-review`: 2 accepted-candidate, 6
  needs-supervisor-review, 4 blocked;
- `agent-workbench-local-supervisor`: 7 accepted-candidate, 4
  needs-supervisor-review, 1 blocked;
- `agent-workbench-result-auditor`: 2 accepted-candidate, 7
  needs-supervisor-review, 3 blocked.

The practical lesson is that the SDK controller is not the first bottleneck.
The next development lane should repair task/profile contracts, especially
profile-evidence-review and result-auditor-as-primary behavior, before another
factorial live run, model-lane expansion, or FoundryTK runtime integration.

## Goal

Add a public-safe repair-plan surface that consumes P76 aggregate JSON and
produces ranked weak cells plus concrete repair recommendations.

The plan should answer:

- which task/profile/overlay cells failed or required review most often;
- whether controller health or result validity is the governing issue;
- which contract repair should happen before the next live battery; and
- what evidence should be collected after repair.

## Input Contract

The input is JSON from `agent-workbench foundrytk profile-evaluation-aggregate`.
It must include public-safe counts and treatment cells. It must not require raw
transcripts, full prompts, private paths, credentials, provider endpoints, or
machine-specific values.

## Output Contract

The command should write:

- Markdown repair plan for coordinator review;
- JSON repair plan for machine-readable follow-on automation.

Required outputs:

- row count and controller-health summary;
- top-level result-validity counts;
- ranked weak treatment cells;
- task-family and selected-profile repair targets;
- recommendation for the next implementation lane;
- validation boundary for the next evidence collection pass.

## Public-Safety Boundary

P77 must not promote raw transcript text, prompts, worker answers, personal
absolute paths, provider endpoints, credentials, tokens, or machine-specific
values. Private-looking values in copied aggregate fields should fail closed.

## Planned Tasks

- P77.1: Activate the roadmap and repair-plan contract (#497).
- P77.2: Implement the repair-plan CLI and tests (#498).
- P77.3: Dogfood the plan on the P75 aggregate summary and record the next
  implementation lane (#499).

