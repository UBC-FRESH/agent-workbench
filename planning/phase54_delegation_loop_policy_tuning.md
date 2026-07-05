# Phase 54 Delegation Loop Policy Tuning

P54 converts recent benchmark and workflow evidence into conservative policy
rules for managed local-worker loops. The goal is not to rank models globally.
The goal is to decide which task shapes are worth another delegated iteration,
which ones need a different ticket/model/lane, and which ones must remain
supervisor-owned.

## Evidence Inputs

| Phase | Evidence | Policy consequence |
| --- | --- | --- |
| P50 | Sanitized reporting delegation with `gpt-oss:20b` produced a small positive paid-token delta after supervisor review. | Reporting over sanitized summaries is a promising local-worker lane, but margins are narrow and source-level audit remains separate. |
| P51 | Managed role vocabulary and graph templates separated extractor, self-auditor, repairer, convergence checker, and supervisor auditor. | Agent Workbench should route work through explicit role/node boundaries instead of ad hoc supervisor reinvention. |
| P52 | Local self-audit/repair on MP11 failed to preserve identifiers, missed known repairables, repaired zero records, and produced a negative supervisor delta-review result. | Do not scale that self-audit/repair shape. Add hard bailout rules for identifier loss and missed calibration defects. |
| P52 | A Copilot SDK repair attempt surfaced invalid tool-call behavior before useful assistant output. | SDK tool behavior must be an explicit restricted-tool lane, not an accidental feature of a no-tool benchmark. |
| P53 | TSA23 corpus materialization produced a reproducible 18-document public TSR mini-corpus and scaffolded cross-document extraction/audit metadata. | Document-library extraction is the next promising high-volume test lane, but quality and economics still need measured worker runs and supervisor calibration. |

## Policy Decisions

P54 adds `templates/delegation_loop_policy_v0.json` as the first
machine-readable policy surface. It complements
`templates/managed_iteration_stop_rules.json`, which now includes bailout rules
for:

- missing supervisor token spans;
- missing worker token records;
- primary identifier loss;
- known repairable calibration misses;
- tool calls in no-tool lanes;
- absent source anchors or source chunks.

The default worker lane remains no-tool L0/L1. Restricted tool use is allowed
only as an explicitly configured L3 experiment with:

- an allowed tool list;
- allowed ignored filesystem roots;
- permission-handler policy;
- captured tool-event evidence; and
- a discard or rollback boundary.

## Recommended Next Experiments

Highest-return next experiments should use the TSA23 mini-corpus prepared in
P53:

1. Build page/chunk extraction for the three selected pilot documents.
2. Run bounded no-tool structure/content extraction with stable record IDs.
3. Measure worker tokens and supervisor audit tokens at document and chunk
   granularity.
4. Use a small calibration sample with known repairable records before running
   local self-audit or repair.
5. Try a restricted-tool lane only after the no-tool lane has a clean baseline.

## Missing Evidence That Must Stay Visible

Agent Workbench should report these as missing, not infer them:

- supervisor token spans for setup, orchestration, audit, repair, reporting, and
  tracked update subtasks;
- worker input/output tokens;
- exact model identity and provider lane;
- source SHA, page anchor, document ID, and chunk ID;
- parseability status and malformed-output counts;
- tool-call event evidence when a tool lane is used;
- accepted, repairable, rejected, and needs-review counts from supervisor
  source audit.

## Boundaries

Local self-audit is defect reduction only. Local repair is candidate repair
only. Neither can approve records or claim source-level quality. The paid
supervisor owns final acceptance, scale decisions, economics interpretation,
tracked-file mutation, GitHub mutation, and phase closeout.
