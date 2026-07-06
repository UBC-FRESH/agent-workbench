# P58 Active Phase Reconciliation

## Summary

P58 consolidates the P55-P57 evidence after the P57 overrun. The main decision
is to stop treating outstanding roadmap checkboxes as implicit permission to
launch more live Copilot/Ollama jobs. The useful evidence is now sufficient to
plan the next engineering tranche: budget gates, outcome semantics, packaged
local-supervisor workflow, and a document-indexing recipe.

No new live worker, Copilot Chat, or Ollama runs were launched for this memo.

## Evidence Categories

Use these categories for current P55-P57 evidence until P60 standardizes the
summary schema:

- `accepted`: protocol and deterministic validators passed.
- `quality-valid`: deterministic validators passed, but the intended authority
  or workflow boundary was noisy.
- `diagnostic`: useful failure or overhead evidence, but not a success signal.
- `stale`: run evidence was contaminated by reused suffixes or stale chat
  session context.
- `historical`: older benchmark evidence that explains direction but should
  not drive new execution.
- `deferred`: work intentionally moved to P59-P64 instead of continuing inside
  the active phase.

## P55 Evidence Register

P55 established that raw document extraction quality depends heavily on ticket
shape, model role, and downstream repair/verification stages.

| Artifact or wave | Category | Use going forward |
| --- | --- | --- |
| Wave 1 and Wave 1.1 smoke/full-document runs | historical | Proved single huge tickets and early prompts should not be scaled unchanged. |
| Wave 2 model A/B | historical | Shows baseline model comparison, but not the final recipe path. |
| Wave 3 size and chunk orchestration runs | historical | Shows chunking/orchestration helps, but hidden caps and ticket defects distorted results. |
| Wave 3.2 Qwen3.6 BF16 A/B | historical | Supports using a general document model rather than a coding model for extraction. |
| Wave 7 dual-model typed fact ensemble | usable recipe evidence | Supports multi-candidate typed extraction with field-level comparison. |
| Wave 8 Qwen3.6 disagreement verification | usable recipe evidence | Produced parsed verifier output with six resolved fields and one `needs_supervisor` field. |
| Wave 8 DeepSeek-R1 verifier | diagnostic | Parse failure means it should not be promoted without a narrower validation role. |
| Wave 9 JSON repair | usable recipe evidence | Supports delegating structured JSON repair to a coding-oriented local model. |
| Wave 10 quote repair prepass | usable recipe evidence | Supports quote length as a soft scoring penalty and repair target, not a hard overall failure. |
| Codex-vs-Copilot supervisor A/B summaries | diagnostic | Useful for free-supervisor behavior, but future comparisons need P59 budget gates and P60 outcome fields. |

P55 close/defer decision:

- Do not run Wave 4 repeatability or Wave 5 content probes inside P55.
- Defer further indexing work to P62 and P63, where the recipe and budget gates
  will be explicit.
- Treat P55 as evidence-complete once accepted/repairable/rejected/escalated
  counts are summarized through the P58/P60 surfaces.

## P56 Evidence Register

P56 produced useful authority-contract scaffolding before it had a GitHub issue
or standalone branch.

Usable evidence:

- `src/agent_workbench/authority.py`
- `templates/supervisor_job_contract.json`
- `templates/supervisor_job_report.json`
- `templates/document_artifact_audit_supervisor_contract.json`
- `templates/document_artifact_audit_supervisor_ticket.md`
- `templates/workbench_templates/document_artifact_audit_supervisor_graph.json`
- `planning/phase56_authority_contracts.md`

P56 close/defer decision:

- The authority roles, final signals, workspace-root rules, and public-safety
  contract are implemented enough for the P57 evidence.
- Coordinator-review versus developer-decision policy should be finished in
  P60/P61 outcome semantics and packaged workflow documentation.
- GitHub closeout and tracked phase closure remain nondelegable; no evidence
  supports promoting them to local supervisors.

## P57 Evidence Register

P57 established that VS Code custom agents and subagents can be used as a local
supervisor-worker surface, but only under narrow workflow boundaries.

| Artifact or result | Category | Use going forward |
| --- | --- | --- |
| `p57_subagent_spike_v2_summary.json` | accepted | Proves the subagent payload handshake is possible. |
| `p57_document_artifact_audit_strict_repeat_summary.json` | accepted | Proves strict gate-to-decision vocabulary improves judgment preservation. |
| `p57_document_artifact_audit_batch4_summary.json` | accepted | Supports batched document-artifact audit with source-fact preservation. |
| `p57_document_artifact_audit_self_materialized_v2_summary.json` | diagnostic | Shows self-materialization works but increases wrong-root and repair risk. |
| `p57_graph_derived_document_audit_batch4_v4_summary.json` | accepted | Proves graph-derived local-supervisor jobs can pass validators. |
| `p57_graph_derived_mixed_schema_split_a_v3_summary.json` | accepted | Supports mixed-schema split batches with deterministic verification. |
| `p57_graph_batch_all_p55_summaries_v1_split_01_02_v1_summary.json` | accepted economics | Best accepted 10-artifact package cost signal: `$0.109171` total, `$0.010917` per source artifact. |
| `p57_graph_batch_all_p55_summaries_v1_full_14_v1_summary.json` | accepted economics | Full 14-artifact coverage from summed accepted spans: `$0.190046` total, `$0.013575` per source artifact. |
| `p57_graph_batch_all_p55_summaries_v1_full_14_v11_summary.json` | quality-valid diagnostic | All 14 artifacts validated, but one child reran a setup/materializer command. |
| `p57_graph_batch_all_p55_summaries_v1_split_02_v13_internal_summary.json` | accepted boundary proof | Clean proof that the pre-materialized boundary can hold for the formerly problematic split. |
| `p57_graph_batch_all_p55_summaries_v1_full_14_v14_summary.json` | stale diagnostic | Quality-valid but suffix/session contamination makes it unsuitable as clean evidence. |
| full-batch aborted v2/v3 and high-entropy aborted retry | diagnostic | Proves unbounded live retries are the cost failure mode P59 must prevent. |

P57 close/defer decision:

- Do not chase another clean full-batch live acceptance inside P57.
- Defer further live full-batch execution until P59 budget gates and P60
  outcome semantics are implemented.
- Move the successful pre-materialized graph-ticket pattern into P61.

## Historical Evidence

P50 and earlier FreshForge A/B work remains useful historical context for why
phase-scale broad-context delegation is not the best first profitable lane.
Those artifacts should not drive new execution until the P59/P60 accounting and
outcome layers exist.

## Active Phase Reconciliation

P55:

- Evidence-complete for the current experimental slice.
- Further extraction work is deferred to P62/P63.
- Remaining closeout work is summary/count normalization, not more model runs.

P56:

- Contract scaffold is usable.
- Remaining policy precision is deferred to P60/P61.
- Nondelegable closeout authority remains with coordinator/developer.

P57:

- Subagent/local-supervisor surface is proven enough to package.
- Further live execution is deferred until P59/P60 gates exist.
- The clean boundary proof is split_02 v13; the best quality-valid scale signal
  is full_14 v11; the high-cost overrun is diagnostic only.

## Next Actions

1. Implement P59 budget records and stop-rule enforcement before any new live
   economics run.
2. Implement P60 outcome semantics so current evidence can be summarized
   without collapsing quality-valid/protocol-rejected/economics-diagnostic
   states.
3. Package the pre-materialized local-supervisor workflow in P61.
4. Resume document-indexing work through P62/P63 only after budget and outcome
   gates are active.
