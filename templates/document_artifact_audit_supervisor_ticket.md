# Strict Document Artifact Audit Supervisor Ticket

Marker: `${MARKER}`

Execute this ticket exactly. This is a bounded Agent Workbench supervisor job.

## Required Reads

- `${CONTRACT_PATH}`
- `${SOURCE_SUMMARY_PATH}`

## Allowed Actions

- Read the required files.
- Invoke the `${AUDITOR_SUBAGENT_NAME}` subagent once.
- Write exactly one JSON report file: `${SUPERVISOR_REPORT_PATH}`
- Do not edit tracked files unless a separate coordinator ticket explicitly
  authorizes tracked edits.
- Do not create commits, branches, GitHub issues, GitHub comments, or pull
  requests.

## Auditor Payload

Pass the auditor only the extracted source facts named by the coordinator
ticket. For P55-style disagreement-verification summaries, the default facts
are:

- `summary_id`
- `document_id`
- `gate_result`
- `recommended_next_move`
- `totals.needs_supervisor_fields`
- `totals.quote_over_limit_fields`
- `totals.resolved_fields`

Allowed `auditor_decision` values:

- `paid_supervisor_audit_required`
- `quote_repair_required`
- `ready_to_scale`
- `needs_coordinator_review`

Decision rules:

- If `gate_result` contains `quote-repair-needed`, `auditor_decision` must be
  `quote_repair_required`.
- If `gate_result` or `recommended_next_move` says a paid supervisor audit is
  required, `auditor_decision` must be `paid_supervisor_audit_required` unless
  a higher-priority repair gate applies.
- Use `ready_to_scale` only when no explicit repair, audit, blocker, or
  missing-evidence gate remains.
- If the artifact is unreadable, internally inconsistent, or the auditor
  payload contradicts these rules, set `final_signal` to
  `needs_coordinator_review`.

## Required Report JSON Fields

- `verification.subagent_payload_excerpt`
- `verification.auditor_decision`
- `verification.source_gate_result`
- `verification.source_recommended_next_move`
- `verification.decision_consistent_with_gate`

## Stop Condition

After the JSON report file exists, reply exactly:

`${MARKER} done`
