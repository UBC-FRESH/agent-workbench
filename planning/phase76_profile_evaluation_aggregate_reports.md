# Phase 76: Profile Evaluation Aggregate Comparison Reports

Phase 76 turns P75-style public-safe profile evaluation datasets into
aggregate comparison reports. P75 proved the SDK bridge can collect replicated
live evidence, but the dataset still needs a reproducible summary layer before
the roadmap can choose between task/profile contract repair, another live
battery, model-lane expansion, or deeper FoundryTK integration.

## Evidence From P75

P75 produced 24 analyzable rows with healthy controller status for every row.
Result validity was mixed:

- 9 accepted-candidate rows;
- 11 needs-supervisor-review rows;
- 4 blocked rows.

The model lane was fixed as `operator-configured-copilot-sdk`, so P75 does not
support model-selection claims. FoundryTK remains external guidance.

## Goal

Add a public-safe aggregate report layer for P74/P75-compatible profile
evaluation JSONL rows.

The report should make these questions answerable without reading raw
transcripts:

- Which profile/overlay/task-family cells produce accepted, review, or blocked
  results?
- Are controller/session failures distinct from worker result-quality failures?
- Which cells are stable enough for another replicated run?
- Which cells need task/profile contract repair before additional live
  spending?

## Input Contract

The input is JSONL from `agent-workbench foundrytk profile-evaluation-dataset`.
Rows are public-safe and include:

- `run_id`;
- `phase`;
- `selected_agent`;
- `task_overlays`;
- `custom_tools`;
- `latest_status`;
- `controller_health`;
- `result_status`;
- nested `reliability`, `work_quality`, `efficiency`, and
  `conversation_shape` mappings;
- `errors`;
- `warnings`.

P76 must not require raw transcript text, full prompts, private paths,
provider endpoints, credentials, or machine-specific values.

## Output Contract

The aggregate command should write:

- Markdown report for human review;
- JSON summary for machine-readable follow-on planning.

Required summaries:

- total rows;
- controller-health counts;
- result-status counts;
- selected-profile counts;
- overlay counts;
- task-family counts inferred from `run_id` when no explicit task-family field
  exists;
- profile by result-status counts;
- overlay by result-status counts;
- task-family by result-status counts;
- profile/overlay/task-family treatment-cell counts;
- simple conversation-shape totals or averages for event, assistant-message,
  tool-event, permission-event, custom-agent-event, and subagent-event counts.

## Public-Safety Boundary

The report must not promote:

- raw transcript text;
- prompts or full worker answers;
- personal absolute paths;
- provider endpoints;
- credentials or access tokens;
- machine-specific values.

If a row includes private-looking values in fields that would be copied to an
output, the command should either fail closed or omit the unsafe value. P76.2
tests should cover this boundary.

## Follow-On Decision Boundary

P76 should recommend one of these lanes:

- task/profile contract repair;
- another replicated live SDK battery;
- model-lane expansion after live inventory is verified;
- FoundryTK runtime integration;
- no further work.

The default expected decision from P75 evidence is task/profile contract repair
plus aggregate-comparison tooling. P76 should not recommend model selection
unless the input includes multiple verified model lanes. It should not
recommend FoundryTK runtime integration unless local aggregate reports are
insufficient for the next planning decision.

## Planned Tasks

- P76.1: Activate the roadmap and report contract.
- P76.2: Implement the aggregate comparison CLI and tests.
- P76.3: Dogfood the report on the P75 dataset and record the next-lane
  decision.

## P76 Outcome

P76 added `agent-workbench foundrytk profile-evaluation-aggregate`. The command
reads public-safe profile evaluation JSONL rows and writes:

- a Markdown aggregate report;
- a JSON aggregate summary.

The report includes row counts, controller-health counts, result-status counts,
profile counts, overlay counts, inferred task-family counts, grouped
result-status tables, treatment-cell summaries, and conversation-shape totals
and averages.

Dogfooding on the P75 24-row dataset produced:

- controller health: 24 healthy rows;
- result status: 9 accepted-candidate, 11 needs-supervisor-review, 4 blocked;
- profile split:
  - `agent-workbench-local-supervisor`: 7 accepted-candidate, 4
    needs-supervisor-review, 1 blocked;
  - `agent-workbench-result-auditor`: 2 accepted-candidate, 7
    needs-supervisor-review, 3 blocked;
- task-family split:
  - `manifest-contract-audit`: 7 accepted-candidate, 5
    needs-supervisor-review, 0 blocked;
  - `profile-evidence-review`: 2 accepted-candidate, 6
    needs-supervisor-review, 4 blocked.

The next lane should prioritize task/profile contract repair before another
live battery, model-lane expansion, or FoundryTK runtime integration. The
highest-value repair target is the profile-evidence-review task family,
especially result-auditor-as-primary behavior and fixtures that make the
evidence artifact explicit enough to score without review/blocker fallback.
