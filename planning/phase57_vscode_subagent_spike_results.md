# Phase 57 VS Code Subagent Spike Results

This note records the first live P57 custom-supervisor/subagent experiment.
Raw tickets, contracts, reports, and chat artifacts remain under ignored
runtime storage. This note tracks only sanitized evidence.

## Setup

Tracked custom agents:

- `.github/agents/agent-workbench-local-supervisor.agent.md`
- `.github/agents/agent-workbench-result-auditor.agent.md`

Runtime-only artifacts:

- `runtime/agent_jobs/p57_subagent_spike_contract.json`
- `runtime/agent_jobs/p57_subagent_spike_ticket.md`
- `runtime/agent_jobs/p57_subagent_spike_report.json`
- `runtime/agent_jobs/p57_subagent_spike_bridge_report.md`

The supervisor contract validated successfully with:

```powershell
agent-workbench authority validate --kind contract --input runtime\agent_jobs\p57_subagent_spike_contract.json
```

The supervisor report validated successfully with:

```powershell
agent-workbench authority validate --kind report --input runtime\agent_jobs\p57_subagent_spike_report.json
```

## Bridge Evidence

The bridge launched the custom supervisor agent without maximizing the VS Code
pane.

Observed sanitized bridge fields:

- status: `accepted-candidate`
- resolved model: `qwen3.6:35b-a3b-bf16`
- permission level: `autopilot`
- completed: `true`
- final marker present: `true`
- expected command observed: `true`
- expected output file observed: `true`
- deviations: none

Observed tool names:

- `agent`
- `read_file`
- `runSubagent`
- `create_file`
- `run_in_terminal`

This is the first positive evidence that the VS Code custom-supervisor lane can
reach the subagent invocation surface from the local bridge.

## Supervisor Report Evidence

The generated supervisor report used final signal:

- `needs_coordinator_review`

It recorded:

- subagent invocation attempted: `true`
- subagent invocation observed by supervisor: `false`
- subagent name: `agent-workbench-result-auditor`

Interpretation: the bridge observed a `runSubagent` tool call, but the
supervisor did not receive or did not preserve a usable auditor payload in its
own report. That is a good first spike result: the surface exists, but the
handshake/report contract needs tightening before this can replace the current
bridge-ticket pattern.

## Next Test

The next P57 test should make the subagent return payload impossible to ignore:

1. Give the auditor subagent a tiny literal input table inside the prompt,
   not a repo file.
2. Require the supervisor report to include a `subagent_payload_excerpt` field.
3. Require the supervisor to set `final_signal` to `job_failed` if the payload
   excerpt is missing.
4. Make the bridge verify the report contains that field.
5. Compare paid coordinator cost against the previous bridge-ticket flow.

Do not broaden to a full P55 indexing workflow until this handshake is proven.

## V2 Payload Handshake

The v2 spike tightened the ticket and validator:

- `agent-workbench authority validate --kind report` now requires
  `verification.subagent_payload_excerpt` whenever a report says
  `verification.subagent_invocation_attempted` is `true`.
- The bridge now reads the output JSON and reports missing fields listed under
  a ticket's `Required Report JSON Fields` section.
- The v2 ticket passed the auditor a literal payload rather than asking the
  subagent to inspect repo files.

Runtime-only artifacts:

- `runtime/agent_jobs/p57_subagent_spike_v2_contract.json`
- `runtime/agent_jobs/p57_subagent_spike_v2_ticket.md`
- `runtime/agent_jobs/p57_subagent_spike_v2_report.json`
- `runtime/agent_jobs/p57_subagent_spike_v2_bridge_report.md`

Tracked sanitized summary:

- `benchmarks/vscode_subagent_spike/p57_subagent_spike_v2_summary.json`

Observed bridge fields:

- status: `accepted-candidate`
- resolved model: `qwen3.6:35b-a3b-bf16`
- permission level: `autopilot`
- completed: `true`
- final marker present: `true`
- expected command observed: `true`
- expected output file observed: `true`
- required JSON fields present: `true`
- deviations: none

Observed tool names:

- `agent`
- `read_file`
- `runSubagent`
- `create_file`
- `run_in_terminal`

The supervisor report validated successfully and recorded:

- final signal: `job_complete_with_caveats`
- subagent invocation attempted: `true`
- subagent invocation observed by supervisor: `true`
- subagent name: `agent-workbench-result-auditor`
- subagent payload excerpt status: present
- subagent payload classification: `accepted-candidate`

Interpretation: P57 now has positive evidence for the supervisor-worker
handshake, not just the raw subagent tool surface. The next useful test is a
small runtime artifact audit or repair loop with the same payload-excerpt
requirement and paid coordinator token accounting.

## Repair-Loop Trial

The next trial used an intentionally invalid runtime supervisor report:

- seed report: `runtime/agent_jobs/p57_repair_loop_seed_report.json`
- defect: `verification.subagent_invocation_attempted` was `true`, but
  `verification.subagent_payload_excerpt` was missing.

The seed report failed validation as expected:

```powershell
agent-workbench authority validate --kind report --input runtime\agent_jobs\p57_repair_loop_seed_report.json
```

The custom supervisor then ran a bounded repair-loop ticket:

- contract: `runtime/agent_jobs/p57_subagent_repair_loop_contract.json`
- ticket: `runtime/agent_jobs/p57_subagent_repair_loop_ticket.md`
- repaired report: `runtime/agent_jobs/p57_subagent_repair_loop_report.json`
- bridge report: `runtime/agent_jobs/p57_subagent_repair_loop_bridge_report.md`

Observed bridge fields:

- status: `accepted-candidate`
- resolved model: `qwen3.6:35b-a3b-bf16`
- permission level: `autopilot`
- completed: `true`
- final marker present: `true`
- expected command observed: `true`
- expected output file observed: `true`
- required JSON fields present: `true`
- deviations: none

Observed tool names:

- `agent`
- `read_file`
- `runSubagent`
- `create_file`
- `run_in_terminal`

The repaired report validated successfully and recorded:

- final signal: `job_complete_with_caveats`
- subagent invocation attempted: `true`
- subagent invocation observed by supervisor: `true`
- subagent name: `agent-workbench-result-auditor`
- subagent payload excerpt status: present
- subagent payload classification: `needs-repair`

Tracked sanitized summary:

- `benchmarks/vscode_subagent_spike/p57_subagent_repair_loop_summary.json`

Coordinator token span:

- runtime span record:
  `runtime/supervisor_tokens/p57_subagent_repair_loop/p57-subagent-repair-loop.tokens.json`
- fresh input tokens: `7679`
- cached input tokens: `1678336`
- output tokens: `3379`
- reasoning output tokens: `45`
- estimated paid coordinator cost: `$0.355083`

The cost span is intentionally broad: it includes coordinator harness creation,
launch, validation, and reporting for this experimental iteration. It should
not be treated as steady-state repair-loop overhead yet.

Interpretation: P57 now has positive evidence for a real repair-loop shape. The
custom supervisor used a named auditor subagent to identify a missing required
field, wrote a repaired report, and the repaired report passed the authority
validator. The next scale-up should use the same pattern on a small
document-indexing artifact instead of a synthetic report.

## Document-Indexing Artifact Audit

The next scale-up used a real P55 document-indexing summary:

- source artifact:
  `benchmarks/document_library/tsa23_tsr/p55_wave8_disagreement_verification_qwen36_summary.json`
- source summary: `p55_wave8_disagreement_verification`
- document: `tsa23_2012_23ts13ra`
- gate result: `wave8-quote-repair-needed`
- recommended next move:
  `Send only unresolved verifier fields to paid supervisor audit: decision_rationale`
- unresolved fields: `1`
- quote-over-limit fields: `1`
- resolved fields: `6`

Runtime-only artifacts:

- contract: `runtime/agent_jobs/p57_document_artifact_audit_contract.json`
- ticket: `runtime/agent_jobs/p57_document_artifact_audit_ticket.md`
- audit report: `runtime/agent_jobs/p57_document_artifact_audit_report.json`
- bridge report: `runtime/agent_jobs/p57_document_artifact_audit_bridge_report.md`

Tracked sanitized summary:

- `benchmarks/vscode_subagent_spike/p57_document_artifact_audit_summary.json`

Observed bridge fields:

- status: `accepted-candidate`
- resolved model: `qwen3.6:35b-a3b-bf16`
- permission level: `autopilot`
- completed: `true`
- final marker present: `true`
- expected command observed: `true`
- expected output file observed: `true`
- required JSON fields present: `true`
- deviations: none

## Paid-Supervisor Cost Postmortem

The later P57 scale-up produced useful evidence but overran the experiment's
economic purpose. The broad goal window was consistent with roughly `$130` of
`gpt-5.5`-scale paid supervisor account impact. That is not acceptable as a
normal iteration cost for this project.

Useful evidence from the overrun:

- `p57_graph_batch_all_p55_summaries_v1_split_02_v13` accepted with expected
  model `qwen3.6:35b-a3b-bf16`, subagent use observed, zero materializer
  commands, and deterministic validators passing.
- `p57_graph_batch_all_p55_summaries_v1_full_14_v11` reached
  `quality_validated_candidate: true` for all 14 source artifacts, but remained
  protocol-rejected because one child reran a safe runtime-only materializer
  command.
- The final high-entropy full-batch retry was aborted and should be treated as
  wasteful diagnostic evidence, not progress.

Planning consequence: future live benchmark work must start with an explicit
paid-supervisor token/cash budget, one or two bounded attempts, and a mandatory
stop-and-report checkpoint. If a run already proves the core learning signal,
the supervisor should consolidate rather than chase a cleaner acceptance result
through additional paid-token retries.

Scoring consequence: future summaries must distinguish:

- `quality_validated_candidate`: deterministic artifact validators passed;
- `protocol_accepted_candidate`: the intended role and authority boundary held;
  and
- `economics_usable`: the paid-token span is measured at the right boundary and
  the run is not stale, aborted, or otherwise contaminated.

Observed tool names:

- `agent`
- `read_file`
- `runSubagent`
- `create_file`
- `run_in_terminal`

The audit report validated successfully and matched the source artifact for:

- summary ID;
- document ID;
- gate result;
- recommended next move;
- needs-supervisor count;
- quote-over-limit count; and
- resolved-field count.

The auditor payload was preserved, but it contained one judgment defect: it
said no quote repair was required even though the source artifact's gate result
was `wave8-quote-repair-needed`. This is not a process failure, but it is a
quality signal. The subagent can follow the workflow and preserve evidence, but
the next prompt must make the allowed decision categories stricter so the
auditor cannot wave away a gate result.

Coordinator token span:

- runtime span record:
  `runtime/supervisor_tokens/p57_document_artifact_audit/p57-document-artifact-audit.tokens.json`
- fresh input tokens: `235138`
- cached input tokens: `1370240`
- output tokens: `3508`
- reasoning output tokens: `225`
- estimated paid coordinator cost: `$0.703546`

This cost span is broad. It includes coordinator artifact selection, contract
and ticket creation, bridge launch, validation, and reporting. It is useful as
current experimental overhead, but not as a steady-state cost estimate.

Interpretation: this is positive process evidence with mixed judgment quality.
The next useful move is a lean repeat using a reusable document-audit ticket
template and stricter auditor choices:

- `paid_supervisor_audit_required`;
- `quote_repair_required`;
- `ready_to_scale`;
- `needs_coordinator_review`.

## Strict Document-Artifact Audit Repeat

The strict repeat targeted the same P55 source artifact but hardened the auditor
decision vocabulary and the gate-to-decision invariant before launch.

Runtime-only artifacts:

- contract: `runtime/agent_jobs/p57_document_artifact_audit_strict_contract.json`
- ticket: `runtime/agent_jobs/p57_document_artifact_audit_strict_ticket.md`
- audit report: `runtime/agent_jobs/p57_document_artifact_audit_strict_report.json`
- bridge report:
  `runtime/agent_jobs/p57_document_artifact_audit_strict_bridge_report.md`

Tracked sanitized summary:

- `benchmarks/vscode_subagent_spike/p57_document_artifact_audit_strict_repeat_summary.json`

Observed bridge fields:

- status: `accepted-candidate`
- resolved model: `qwen3.6:35b-a3b-bf16`
- permission level: `autopilot`
- completed: `true`
- final marker present: `true`
- expected output file observed: `true`
- required JSON fields present: `true`
- deviations: none

Observed tool names:

- `agent`
- `read_file`
- `runSubagent`
- `create_file`

The strict audit report validated successfully and matched the source artifact
for:

- summary ID;
- document ID;
- gate result;
- recommended next move;
- needs-supervisor count;
- quote-over-limit count; and
- resolved-field count.

The hardened auditor decision preserved the source gate result correctly:

- source gate result: `wave8-quote-repair-needed`
- auditor decision: `quote_repair_required`
- decision consistent with gate: `true`

Coordinator token span:

- runtime span record:
  `runtime/supervisor_tokens/p57_document_artifact_audit_strict_repeat/p57-document-artifact-audit-strict-repeat.tokens.json`
- fresh input tokens: `1000`
- cached input tokens: `204032`
- output tokens: `297`
- reasoning output tokens: `0`
- estimated paid coordinator cost: `$0.041614`

Interpretation: the strict-repeat result fixed the previous auditor judgment
defect and cut coordinator cost sharply relative to the broad first
document-artifact audit. The difference is not only model behavior; it also
reflects a cleaner reusable ticket, narrower validation surface, and less
coordinator-side artifact design during the measured span. This is evidence in
favor of moving high-frequency supervisor tasks into reusable role/workflow
contracts with explicit gate-to-decision invariants.

## Template Promotion

The strict document-artifact audit pattern has been promoted into tracked,
public-safe templates:

- `templates/document_artifact_audit_supervisor_contract.json`
- `templates/document_artifact_audit_supervisor_ticket.md`

The contract template validates with:

```powershell
python -m agent_workbench authority validate --kind contract --input templates\document_artifact_audit_supervisor_contract.json
```

This matters for the economics target: the sharp cost drop in the strict repeat
came partly from no longer asking the paid coordinator to invent the audit
ritual in the measured span. Future tests should materialize from this template
and measure only the remaining coordinator work needed to choose the source
artifact, launch the local supervisor, and inspect compact evidence.

## Materialized Batch Audit

The next test used the reusable template pattern through a tracked materializer:

- materializer: `scripts/materialize_document_artifact_audit.py`
- runtime contract:
  `runtime/agent_jobs/p57_document_artifact_audit_batch4_contract.json`
- runtime ticket:
  `runtime/agent_jobs/p57_document_artifact_audit_batch4_ticket.md`
- runtime report:
  `runtime/agent_jobs/p57_document_artifact_audit_batch4_report.json`
- bridge report:
  `runtime/agent_jobs/p57_document_artifact_audit_batch4_bridge_report.md`
- tracked sanitized summary:
  `benchmarks/vscode_subagent_spike/p57_document_artifact_audit_batch4_summary.json`

The batch covered four P55 document-indexing summaries:

- DeepSeek-R1 Wave 8 verifier parse failure;
- Qwen3.6 Q8 Wave 8 quote-repair-needed gate;
- Qwen3.6 BF16 Wave 8 quote-repair-needed gate; and
- Wave 9 repaired JSON ready-for-supervisor-audit-sampling gate.

Observed bridge fields:

- status: `accepted-candidate`
- resolved model: `qwen3.6:35b-a3b-bf16`
- permission level: `autopilot`
- completed: `true`
- final marker present: `true`
- output file observed: `true`
- required JSON fields present: `true`
- deviations: none

Observed tool names:

- `agent`
- `read_file`
- `runSubagent`
- `create_file`

Independent source-fact checks found zero defects across all four artifacts.
Decision counts:

- `needs_coordinator_review`: `1`
- `quote_repair_required`: `2`
- `paid_supervisor_audit_required`: `1`

The supervisor preserved the intended decision for each gate class:

- `wave8-verifier-parse-failed` -> `needs_coordinator_review`
- `wave8-quote-repair-needed` -> `quote_repair_required`
- `wave8-ready-for-supervisor-audit-sampling` ->
  `paid_supervisor_audit_required`

Coordinator token span:

- runtime span record:
  `runtime/supervisor_tokens/p57_document_artifact_audit_batch4/p57-document-artifact-audit-batch4.tokens.json`
- fresh input tokens: `1700`
- cached input tokens: `292608`
- output tokens: `328`
- reasoning output tokens: `34`
- estimated paid coordinator cost: `$0.059249`
- approximate cost per source artifact: `$0.014812`

Interpretation: this is stronger evidence than the single strict repeat. The
local Copilot supervisor handled a small batch with multiple gate classes,
invoked the auditor subagent, wrote one structured report, and preserved all
source facts under independent checking. The coordinator cost increased only
modestly relative to the one-artifact strict repeat, so batching appears to be
a promising way to thicken the delegation economics margin.

## Self-Materialized Batch Audit

The next test moved one level up the hierarchy. Instead of having the Codex
coordinator materialize the runtime audit job, the Copilot supervisor received a
meta-ticket requiring it to run the materializer first and then execute the
generated audit.

The first self-materialized attempt exposed a real workflow defect:

- the VS Code chat session started from the adjacent FEMIC root;
- the supervisor searched for the Agent Workbench script and retried several
  commands;
- it eventually wrote the final report under `femic/runtime/agent_jobs`
  instead of the Agent Workbench runtime path; and
- the bridge correctly rejected the run because the expected output did not
  exist under Agent Workbench.

Fix applied:

- `scripts/materialize_document_artifact_audit.py` now accepts
  `--project-root`;
- relative source, template, and output paths resolve from that root; and
- generated contract/ticket paths remain repo-relative when the output lives
  under the assigned project root.

The V2 self-materialized ticket used:

- absolute materializer script path;
- explicit `--project-root`;
- one exact required command;
- no command retries; and
- an absolute report write target under Agent Workbench.

Runtime-only artifacts:

- ticket:
  `runtime/agent_jobs/p57_document_artifact_audit_self_materialized_v2_ticket.md`
- generated contract:
  `runtime/agent_jobs/p57_document_artifact_audit_self_materialized_v2_batch4_contract.json`
- generated report:
  `runtime/agent_jobs/p57_document_artifact_audit_self_materialized_v2_batch4_report.json`
- bridge report:
  `runtime/agent_jobs/p57_document_artifact_audit_self_materialized_v2_bridge_report.md`
- repair bridge report:
  `runtime/agent_jobs/p57_document_artifact_audit_self_materialized_v2_repair_bridge_report.md`

Tracked sanitized summary:

- `benchmarks/vscode_subagent_spike/p57_document_artifact_audit_self_materialized_v2_summary.json`

Observed initial V2 bridge fields:

- status: `accepted-candidate`
- resolved model: `qwen3.6:35b-a3b-bf16`
- permission level: `autopilot`
- required command observed exactly once: `true`
- `runSubagent` observed: `true`
- output file observed: `true`
- required JSON fields present: `true`
- deviations: none

The initial V2 report preserved the source decisions correctly, but failed the
authority validator because `verification.subagent_payload_excerpt` exceeded
the 1000-character limit. A bounded repair ticket delegated the fix back to the
Copilot supervisor. The repair:

- shortened the excerpt to 752 characters;
- corrected the Source 4 wording to 8 unresolved fields and 1 resolved field;
- preserved all audit item facts; and
- passed `agent-workbench authority validate --kind report`.

Independent source-fact checks after repair found zero defects across all four
artifacts. Decision counts remained:

- `needs_coordinator_review`: `1`
- `quote_repair_required`: `2`
- `paid_supervisor_audit_required`: `1`

Coordinator token spans:

- initial self-materialized run:
  `runtime/supervisor_tokens/p57_document_artifact_audit_self_materialized_v2/p57-document-artifact-audit-self-materialized-v2.tokens.json`
  - fresh input tokens: `2414`
  - cached input tokens: `392448`
  - output tokens: `634`
  - reasoning output tokens: `45`
  - estimated paid coordinator cost: `$0.082409`
- delegated repair:
  `runtime/supervisor_tokens/p57_document_artifact_audit_self_materialized_v2_repair/p57-document-artifact-audit-self-materialized-v2-repair.tokens.json`
  - fresh input tokens: `1780`
  - cached input tokens: `402176`
  - output tokens: `297`
  - reasoning output tokens: `0`
  - estimated paid coordinator cost: `$0.077654`
- combined cost: `$0.160063`
- combined cost per source artifact: `$0.040016`

Interpretation: this is the first positive evidence that the local supervisor
can run an Agent Workbench workflow tool, use a subagent, produce a structured
report, and repair a validator failure. The main remaining weakness is not the
gate decision logic; it is root control in multi-root VS Code sessions. Future
supervisor tickets should always name the assigned root explicitly and use
project-root-aware scripts or absolute write targets for runtime artifacts.

## Supervisor Workflow Graph

The successful document-artifact audit pattern has been encoded as a
FreshForge-compatible workflow graph:

- `templates/workbench_templates/document_artifact_audit_supervisor_graph.json`

Rendered runtime reports:

- `runtime/graphs/document_artifact_audit_supervisor_graph.md`
- `runtime/graphs/document_artifact_audit_supervisor_graph_decisions.md`

Graph validation result:

- workflow ID: `document_artifact_audit_supervisor_graph`
- node count: `6`
- Agent Workbench metadata diagnostics: none

The graph nodes encode the tested hierarchy:

- coordinator prepares the supervisor ticket;
- supervisor runs the materializer with explicit `--project-root`;
- worker subagent audits source artifact gates;
- supervisor writes the structured report;
- coordinator or deterministic validator routes validation and repair; and
- coordinator prepares the sanitized developer review packet.

The graph decision report correctly keeps coordinator/supervisor nodes outside
the worker delegation boundary and marks the worker-owned subagent audit node as
delegable (`L1`). This is an important distinction: the P57 evidence does not
mean the free worker owns the whole workflow. It means the free local
supervisor can run supervisor-owned nodes, while worker-owned subnodes can be
delegated to subagents under that supervisor.

## Graph-Derived Supervisor Job Iteration

The document-artifact audit graph was next used as an executable ticket source,
not only as a descriptive artifact.

Added:

- `scripts/materialize_document_artifact_graph_job.py`
- `tests/test_document_artifact_graph_materializer.py`
- `benchmarks/vscode_subagent_spike/p57_graph_derived_document_audit_batch4_v4_summary.json`

The graph materializer validates
`templates/workbench_templates/document_artifact_audit_supervisor_graph.json`,
separates full graph context from executable supervisor/worker nodes, and emits
a runtime Copilot ticket plus manifest under `runtime/agent_jobs/`.

Four graph-derived iterations were informative:

- v1 proved the supervisor could run the graph-shaped job, but the parse-failed
  source was misclassified as `paid_supervisor_audit_required`.
- v2 fixed the parse-failed decision rule, but the supervisor copied one source
  summary incorrectly.
- v3 introduced deterministic pre-extracted source facts in the generated audit
  ticket; this eliminated the source-copy defect and produced correct gate
  decisions.
- v4 hardened the validation command with an explicit `PYTHONPATH` and
  `python -m agent_workbench.cli`, producing a graph report where authority
  validation passed after a bounded repair.

The v4 sanitized result:

- model: `qwen3.6:35b-a3b-bf16`
- permission level: `autopilot`
- source artifacts: `4`
- `runSubagent` observed: yes
- materializer command observed: yes
- authority validation passed after repair: yes
- all source facts copied correctly: yes
- all decisions consistent with gate: yes
- estimated paid coordinator cost: `$0.049161`
- estimated paid coordinator cost per source artifact: `$0.01229`

The initial v4 bridge report still returned `needs-supervisor-review` because
the verifier compared commands too literally. That verifier has now been
hardened:

- repo-root-equivalent script paths compare as equivalent;
- repeated expected validation commands are allowed as repair-loop evidence;
- benign runtime `Test-Path` output checks are reported separately from
  deviations; and
- named graph command blocks are parsed from `Exact Materializer Command` and
  `Graph Execution Requirements`.

Reparsing the existing v4 session without relaunching Copilot produced:

- status: `accepted-candidate`
- completed: `true`
- final marker present: `true`
- `runSubagent` observed: yes
- deviations: none

This makes v4 the first graph-derived supervisor/subagent run where both the
runtime artifacts and the bridge verifier agree that the workflow execution is
an accepted candidate.

## Mixed-Schema Scale-Up Test

The next scale-up tried to audit all available P55 summary artifacts as one
mixed-schema graph job. That single 14-artifact audit node failed early:

- the supervisor ran the materializer command twice;
- the generated audit ticket was created;
- no audit report or graph report was written; and
- the supervisor still emitted the outer done marker.

This failure is useful. It indicates that the current local supervisor can
handle graph-shaped jobs, but not arbitrary expansion of a single audit node.
Large mixed-schema work should be split into smaller graph nodes or batches.

The graph ticket was hardened so materializer success is explicitly not
completion. The workflow then moved to a five-artifact split batch:

- two summaries with blank gate results;
- two summaries with older non-vocabulary gate results; and
- one `wave10-quote-limit-failed` summary.

Split-A v1 completed at the bridge level, but omitted
`verification.all_decisions_consistent_with_gate`. This showed that generic
authority validation is too weak for document-audit artifacts.

Added:

- `scripts/verify_document_artifact_audit_report.py`
- `tests/test_document_artifact_audit_verifier.py`

The document-specific verifier checks source-fact copying, expected
gate-to-decision mappings, `source_fact_copy_ok`, per-item
`decision_consistent_with_gate`, and the aggregate
`verification.all_decisions_consistent_with_gate` field.

Split-A v2 ran with the new verifier, but exposed two policy bugs:

- `quote-limit-failed` was incorrectly treated as generic `failed`; and
- generic wording such as "before supervisor audit" was too weak to imply
  `paid_supervisor_audit_required`.

The verifier, generated ticket rules, and auditor subagent instructions were
corrected. Split-A v3 then produced the first clean mixed-schema split result:

- bridge status: `accepted-candidate`
- source artifacts: `5`
- `runSubagent` observed: yes
- authority validation: passed
- document-audit verifier: passed
- all source facts copied correctly: yes
- all decisions consistent with gate: yes
- estimated paid coordinator cost: `$0.082281`
- estimated paid coordinator cost per source artifact: `$0.016456`

Tracked summary:

- `benchmarks/vscode_subagent_spike/p57_graph_derived_mixed_schema_split_a_v3_summary.json`

Interpretation: the immediate scale path is split-node graph orchestration, not
one huge audit node. The local supervisor behaves much better when deterministic
source facts and deterministic artifact-specific validators constrain the job.

## Graph Batch Planner And Split 02 Result

The next hardening step turned the five-artifact split lesson into a
reproducible batch planner:

- `scripts/materialize_document_artifact_graph_batch.py`
- `tests/test_document_artifact_graph_batch_materializer.py`

The planner materializes graph-derived supervisor tickets in stable input order
with a default batch size of five source artifacts. For the current P55 summary
corpus it produced three runtime splits: two five-artifact jobs and one
four-artifact job.

The second split contained:

- `p55_wave2_model_ab_summary.json`
- `p55_wave3_chunk_orchestration_summary.json`
- `p55_wave3_qwen36_bf16_chunk_ab_summary.json`
- `p55_wave3_size_scale_summary.json`
- `p55_wave8_disagreement_verification_deepseek_r1_summary.json`

The local Copilot supervisor completed the second split and produced final
runtime audit and graph reports. The final artifacts passed both generic
authority validation and the document-artifact verifier:

- source artifacts: `5`
- `runSubagent` observed: yes
- authority validation: passed
- document-audit verifier: passed
- all source facts copied correctly: yes
- all decisions consistent with gate: yes
- decisions: `5` `needs_coordinator_review`

However, the bridge correctly classified the run as
`needs-supervisor-review`, not `accepted-candidate`, because the supervisor
deleted the runtime audit report twice during repair before recreating it. That
is a real process deviation. The artifact is valid, but the execution protocol
is not acceptable for a reusable supervisor workflow.

Tracked summary:

- `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_split_02_summary.json`

Measured paid coordinator token span:

- estimated paid coordinator cost: `$0.092546`
- estimated paid coordinator cost per source artifact: `$0.018509`
- fresh input tokens: `2,728`
- cached input tokens: `477,952`
- output tokens: `295`

Follow-up hardening:

- generated graph tickets now explicitly forbid deleting or removing runtime
  files;
- repair instructions require overwriting only the assigned audit report or
  graph report path; and
- the materializer test asserts that the no-delete repair rule is present in
  generated tickets.

Interpretation: split-node graph orchestration is still the right scale path,
but the supervisor needs explicit mutation guardrails even for ignored runtime
files. The next evidence-producing move is to rerun the same split after the
no-delete hardening and check whether the process deviation disappears.

## Split 02 V3 Accepted Candidate

After adding the no-delete repair rule and a stronger mandatory graph-report
stop condition, the same second split was rerun as `split_02_v3`.

Result:

- bridge status after reparse: `accepted-candidate`
- final marker present: yes
- `runSubagent` observed: yes
- materializer command observed: yes
- audit report written: yes
- graph report written: yes
- runtime delete command observed: no
- authority validation: passed
- document-audit verifier: passed
- all source facts copied correctly: yes
- all decisions consistent with gate: yes

Tracked summary:

- `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_split_02_v3_summary.json`

Important caveat: this is an accepted bridge/protocol candidate, not a perfect
supervisor-worker quality win. The run still needed deterministic verifier
feedback to repair initially wrong decisions, and the graph report states that
the supervisor effectively corrected or determined decisions after the auditor
subagent output was insufficient. This strengthens the case for deterministic
validators and compact coordinator review packets around local-supervisor
workflows.

Cost accounting caveat: this rerun was not wrapped in a dedicated
supervisor-token start/end checkpoint, so it must not be used as a cost
economics datapoint.

## Subagent Outcome Contract Hardening

The v3 accepted candidate exposed a useful but important weakness in the
verification surface: bridge evidence proved that `runSubagent` was invoked,
but invocation alone did not prove that the subagent result was useful.

The authority contract was hardened so supervisor reports must now record a
structured subagent outcome whenever a subagent is attempted:

- `accepted_without_repair`
- `accepted_after_supervisor_repair`
- `rejected_supervisor_replaced`
- `unavailable_supervisor_completed`

When the status is anything other than `accepted_without_repair`, the report
must include a `subagent_repair_summary`. This turns the v3 caveat into a
first-class evidence field instead of a note buried in prose.

Updated surfaces:

- `src/agent_workbench/authority.py`
- `templates/supervisor_job_report.json`
- `scripts/materialize_document_artifact_audit.py`
- `scripts/materialize_document_artifact_graph_job.py`
- `tests/test_authority.py`
- `tests/test_document_artifact_materializer.py`
- `tests/test_document_artifact_graph_materializer.py`

Validation:

- `python -m py_compile src\agent_workbench\authority.py scripts\materialize_document_artifact_audit.py scripts\materialize_document_artifact_graph_job.py scripts\copilot_chat_bridge.py`
- `PYTHONPATH=src python -m pytest tests`

Result: `30` tests passed.

Next test implication: the next Copilot graph run should be judged on three
separate axes:

- bridge/protocol acceptance;
- deterministic validator acceptance; and
- subagent outcome status.

A run where the local supervisor repairs bad subagent output may still be
valuable, but it should no longer be confused with a clean supervisor-worker
delegation win.

## Split 02 V4 Under Subagent Outcome Contract

The same second five-artifact split was rerun after adding the structured
subagent outcome contract. This run was wrapped in a supervisor-token checkpoint
so it can be used as economics evidence.

Result:

- bridge status: `accepted-candidate`
- final marker present: yes
- `runSubagent` observed: yes
- audit report written: yes
- graph report written: yes
- runtime delete command observed: no
- authority validation: passed
- document-audit verifier: passed
- all source facts copied correctly: yes
- all final decisions consistent with gate: yes
- subagent outcome: `accepted_after_supervisor_repair`

Tracked summary:

- `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_split_02_v4_summary.json`

Measured paid coordinator token span:

- estimated paid coordinator cost: `$0.146603`
- estimated paid coordinator cost per source artifact: `$0.029321`
- fresh input tokens: `3,725`
- cached input tokens: `711,680`
- output tokens: `989`
- reasoning output tokens: `121`

Interpretation: the local Copilot supervisor can now complete this
graph-derived five-artifact audit protocol without bridge deviations, and the
run produces enough structured evidence to distinguish protocol success from
subagent quality. The quality result is still weak: all five decisions needed
supervisor repair before deterministic validators passed. This is useful
evidence for the overall authority model, because it shows that cheap local
supervision can run the workflow, but clean subagent delegation remains
unproven for this audit node class.

## Graph Report Verifier

The v4 run made the graph report the coordinator-facing evidence packet for
subagent outcome quality. A new deterministic verifier now checks that packet:

- `scripts/verify_document_artifact_graph_report.py`
- `tests/test_document_artifact_graph_report_verifier.py`

The verifier requires:

- standard graph report identity fields;
- all required graph nodes marked `completed`;
- bounded `authority_validation` evidence;
- `subagent_invocation_observed_by_supervisor: true`;
- a structured `subagent_result` object with an allowed status;
- `repair_required` consistent with the status; and
- matching `subagent_result.status` and
  `audit_report.verification.subagent_result_status` when an audit report is
  supplied.

The graph-derived job materializer now includes this verifier command in future
Copilot supervisor tickets and manifests. Existing v4 runtime evidence passes
the new verifier:

```powershell
python scripts\verify_document_artifact_graph_report.py --project-root . --graph-report runtime\agent_jobs\p57_graph_batch_all_p55_summaries_v1_split_02_v4_graph_report.json --audit-report runtime\agent_jobs\p57_graph_batch_all_p55_summaries_v1_split_02_v4_audit_report.json
```

This closes another false-positive path: future runs cannot be accepted merely
because they wrote a graph report. The report must also state a coherent
subagent outcome that agrees with the validated audit report.

## Split 02 V5 With Graph-Report Verifier In The Loop

The same five-artifact split was rerun after wiring the graph-report verifier
into the generated Copilot supervisor ticket. This tested whether the local
supervisor would execute all three deterministic gates during the job:

- bridge protocol verifier;
- authority plus document-artifact audit verifiers; and
- graph-report verifier.

Runtime result:

- bridge status: `needs-supervisor-review`
- final marker present: yes
- `runSubagent` observed: yes
- audit report written: yes
- graph report written: yes
- authority validation: passed
- document-audit verifier: passed
- graph-report verifier: passed
- runtime delete command observed: no
- materializer command count: `2`

Tracked summary:

- `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_split_02_v5_summary.json`

The final artifacts are coherent, but the process is not acceptable because the
supervisor reran the one-shot materializer command. The bridge was hardened so
repeated validators remain benign repair-loop evidence while repeated
materializers are protocol deviations.

The subagent outcome also worsened relative to v4:

- audit report status: `rejected_supervisor_replaced`
- graph report status: `rejected_supervisor_replaced`
- reason: wrong item IDs plus incorrect `quote_repair_required` decisions for
  two items.

The token span was captured, but it is not valid economics evidence because
the end checkpoint was taken after post-run bridge hardening and reparsing:

- recorded span cost: `$0.542613`
- economics usable: no

Follow-up hardening:

- generated tickets now explicitly prohibit rerunning the materializer for
  repair, confirmation, uncertainty, or recovery;
- if the materializer already ran and the generated audit ticket is missing or
  unusable, the supervisor must write a blocked graph report and stop.

Interpretation: v5 is highly useful negative evidence. The local supervisor can
execute all deterministic validators and produce coherent reports, but still
needs stronger one-shot command discipline. The subagent role is also not yet
proving useful on this audit task because the supervisor had to replace its
output.

## Split 02 V6 With No-Rerun Guardrail

The same second five-artifact split was rerun after adding an explicit
materializer no-rerun guardrail to the generated graph-derived ticket.

Runtime result:

- bridge status after reparse: `accepted-candidate`
- final marker present: yes
- `runSubagent` observed: yes
- audit report written: yes
- graph report written: yes
- materializer command count: `1`
- runtime delete command observed: no
- authority validation: passed
- document-audit verifier: passed
- graph-report verifier: passed
- all source facts copied correctly: yes
- all final decisions consistent with gate: yes
- subagent outcome: `accepted_after_supervisor_repair`

Tracked summary:

- `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_split_02_v6_summary.json`

The initial bridge report classified the run as `needs-supervisor-review`
because the local supervisor wrote the assigned runtime JSON report files with
PowerShell `Set-Content` commands. That was not a real workflow deviation: the
ticket explicitly allowed writing exactly those two runtime report files. The
bridge verifier was hardened so assigned report writes and runtime `Test-Path`
existence checks are treated as benign, while repeated materializer commands,
delete commands, and writes outside assigned runtime report paths remain
deviations.

Validation:

- `PYTHONPATH=src python -m pytest tests\test_copilot_chat_bridge.py`
- `agent-workbench authority validate --kind report`
- `scripts\verify_document_artifact_audit_report.py`
- `scripts\verify_document_artifact_graph_report.py`

Result: the run is a protocol accepted candidate. It is not clean economics
evidence because the token end checkpoint was taken after post-run bridge
hardening and reparse work. The recorded paid coordinator span is retained as a
broad trace only:

- recorded paid coordinator cost: `$0.286656`
- recorded paid coordinator cost per source artifact: `$0.057331`
- fresh input tokens: `64,997`
- cached input tokens: `859,904`
- output tokens: `1,527`
- reasoning output tokens: `75`

Interpretation: v6 is the best process evidence for this split so far. The
local Copilot supervisor ran the one-shot materializer once, invoked the
subagent, wrote both required reports, ran all deterministic validators, avoided
delete commands, and produced a bridge-accepted candidate after verifier
hardening. The quality caveat remains unchanged: the subagent result still
needed supervisor repair, so this is evidence for local-supervisor
orchestration, not yet evidence for clean subagent audit quality.

## Split 02 V7 Clean Token Span

The same five-artifact split was rerun once more after the bridge report-write
hardening was in place. The v7 token checkpoint span was started before runtime
ticket materialization and closed immediately after the live Copilot supervisor
bridge run, before any further verifier hardening or tracked summary work.

Runtime result:

- bridge status after no-launch reparse: `accepted-candidate`
- final marker present: yes
- `runSubagent` observed: yes
- audit report written: yes
- graph report written: yes
- materializer command count: `1`
- runtime delete command observed: no
- authority validation: passed
- document-audit verifier: passed
- graph-report verifier: passed
- all source facts copied correctly: yes
- all final decisions consistent with gate: yes
- subagent outcome: `accepted_after_supervisor_repair`

Tracked summary:

- `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_split_02_v7_summary.json`

Measured paid coordinator token span:

- estimated paid coordinator cost: `$0.120379`
- estimated paid coordinator cost per source artifact: `$0.024076`
- fresh input tokens: `5,065`
- cached input tokens: `535,552`
- output tokens: `1,032`
- reasoning output tokens: `239`

Compared with v4, v7 reduced measured paid coordinator cost from `$0.146603`
to `$0.120379`, about `17.9%` lower, while preserving bridge acceptance and
deterministic validation.

The initial v7 bridge report returned `needs-supervisor-review` because
Copilot quoted runtime path arguments in verifier commands. This was a bridge
normalization false positive, not a Copilot run defect. The token span was
closed before fixing that bridge normalization rule, so the economics record is
not contaminated by the post-run hardening.

Remaining quality caveats:

- The subagent result still required supervisor repair.
- The report `score` field stayed at `0.0` despite deterministic validators
  passing, so score consistency should become a future verifier rule or a
  deterministic postprocessor.

Interpretation: v7 is the first clean economics datapoint after the no-rerun
and bridge-verifier hardening. The hierarchy pattern is working for
local-supervisor orchestration. It is not yet a clean win for subagent audit
quality, because the supervisor still needed to repair subagent-derived output.

## Split 02 V8 Score-Consistency Gate

The document-artifact verifier was hardened after v7 so report score is no
longer a model-authored loose field. For a valid document-audit report, the
verifier now requires `verification.score` to be `1.0` when all source facts are
copied correctly and all gate decisions are consistent. A report like v7, where
source facts and decisions passed but `score` stayed `0.0`, would now fail.

Validation hardening:

- `scripts\verify_document_artifact_audit_report.py`
- `tests\test_document_artifact_audit_verifier.py`

The same five-artifact split was rerun as v8 under this stricter verifier.

Runtime result:

- bridge status: `accepted-candidate` on first parse
- final marker present: yes
- `runSubagent` observed: yes
- audit report written: yes
- graph report written: yes
- materializer command count: `1`
- runtime delete command observed: no
- authority validation: passed
- document-audit verifier: passed
- graph-report verifier: passed
- score consistency: passed
- all source facts copied correctly: yes
- all final decisions consistent with gate: yes
- final score: `1.0`
- subagent outcome: `accepted_after_supervisor_repair`

Tracked summary:

- `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_split_02_v8_summary.json`

Measured paid coordinator token span:

- estimated paid coordinator cost: `$0.092783`
- estimated paid coordinator cost per source artifact: `$0.018557`
- fresh input tokens: `1,638`
- cached input tokens: `471,168`
- output tokens: `533`
- reasoning output tokens: `0`

Compared with prior accepted economics datapoints:

- v4: `$0.146603`
- v7: `$0.120379`
- v8: `$0.092783`

The v8 span is about `36.7%` lower than v4 and about `22.9%` lower than v7.

The quality caveat is still important. The subagent returned `ready_to_scale`
for four items where deterministic gate rules required
`needs_coordinator_review`. The local supervisor repaired those decisions,
updated aggregate consistency, set score to `1.0`, and passed all validators.

Interpretation: v8 is the strongest current evidence for local-supervisor
orchestration. It does not prove the subagent is good at this audit node. It
does show that a free Copilot/Ollama supervisor wrapped in deterministic
workflow gates can contain weak subagent output and return a usable
coordinator-facing artifact at declining paid coordinator cost.

## Packaged Supervisor Graph Launcher

The repeated v4-v8 orchestration pattern has now been promoted into a reusable
command:

```powershell
agent-workbench supervisor run-document-audit-graph
```

The command can run in `--dry-run` mode to print the exact plan without opening
Copilot Chat, or in execution mode to run the whole packaged graph ritual:

- materialize the graph-derived runtime ticket;
- launch the local Copilot supervisor through the bridge;
- wrap the supervisor launch in start/end token checkpoints;
- run authority, document-audit, and graph-report validators; and
- write a sanitized benchmark summary.

This matters for the goal objective because manual coordinator choreography was
becoming a paid-token overhead source. The launcher turns that recurring ritual
into script-owned behavior, leaving the coordinator to choose the work package
and inspect compact evidence rather than reconstructing the same command chain
for every run.

## Packaged Launcher V9 Negative Datapoint

The first live run through the packaged launcher was:

```powershell
agent-workbench supervisor run-document-audit-graph
```

Runtime result:

- launcher executed ticket materialization;
- launcher opened the Copilot supervisor through the bridge;
- bridge observed `runSubagent`;
- bridge observed the final marker;
- bridge classified the run as `needs-supervisor-review`;
- the local supervisor wrote the audit report but did not write the required
  graph report;
- the local supervisor did not run the document-audit or graph-report
  verifiers; and
- authority validation failed because required report fields were missing.

Tracked summary:

- `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_split_02_v9_summary.json`

This was useful negative evidence. It showed that the launcher needs to record
failed supervisor jobs as first-class benchmark artifacts instead of returning
only a nonzero exit code. The launcher was hardened accordingly:

- failed runs now write a sanitized summary before returning nonzero;
- validation stdout/stderr are compacted and private paths are redacted;
- missing graph reports are summarized rather than crashing summary generation;
  and
- zero-token in-command spans are marked `economics_usable: false`.

The token caveat matters. When Codex invokes the whole launcher as one blocking
shell command, Codex session `token_count` events may not advance during the
process, yielding a zero token delta. That is not a real zero-cost proof. Future
paid-coordinator economics benchmarks should wrap the launcher with external
start/end checkpoints taken from separate coordinator actions.

## Packaged Launcher V10 Hardened Retry

The next retry used the same packaged launcher after two hardening changes:

- missing graph reports now fail as clean verifier output instead of traceback
  noise; and
- `ready_to_scale` is only allowed when `gate_result` explicitly contains a
  ready-scale trigger.

Runtime result:

- launcher executed ticket materialization once;
- bridge observed `runSubagent`;
- bridge observed the final marker;
- bridge classified the run as `accepted-candidate`;
- the local supervisor wrote both required runtime reports;
- authority validation passed;
- document-audit validation passed;
- graph-report validation passed; and
- the subagent outcome was recorded as `accepted_without_repair`.

Tracked summary:

- `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_split_02_v10_summary.json`

The five audited P55 source artifacts all had nonstandard or blocker-like gate
vocabulary, so the deterministic verifier required `needs_coordinator_review`
for every item. The v10 supervisor followed that rule, set score to `1.0`, and
returned a coherent graph report.

Economics caveat: the launcher-contained checkpoint span again produced a zero
Codex token delta and is marked `economics_usable: false`. This is not a
claim that the paid coordinator spent zero tokens. It confirms that
launcher-contained spans are the wrong measurement boundary for paid
coordinator economics; external checkpoints around launcher invocation are
needed.

Interpretation: v10 is the first positive end-to-end packaged-launcher result.
It supports continuing with the custom Copilot local-supervisor surface, but
paid-token economics for packaged runs still require external coordinator
checkpointing.

## External Coordinator Checkpoint Protocol

The packaged launcher now has a companion summarizer:

```powershell
agent-workbench supervisor summarize-document-audit-graph
```

The summarizer validates existing runtime artifacts and rewrites the sanitized
benchmark summary. It can take `--token-record` so the summary economics use an
externally captured coordinator span instead of the launcher-contained span.

The next paid-coordinator benchmark should use this protocol:

1. Run `agent-workbench supervisor-tokens checkpoint --event start` as a
   separate coordinator action.
2. Run `agent-workbench supervisor run-document-audit-graph` for the local
   Copilot supervisor job.
3. Run `agent-workbench supervisor-tokens checkpoint --event end` as a separate
   coordinator action.
4. Run `agent-workbench supervisor-tokens span` to create the external token
   record.
5. Run `agent-workbench supervisor summarize-document-audit-graph --token-record`
   to attach that external token record to the validated graph-run summary.

This keeps the free local supervisor work inside the packaged graph launcher,
but moves paid-coordinator token measurement outside the blocking shell command.
That boundary is required for credible economics evidence.

## Packaged Launcher V11 External-Token Benchmark

The v11 run executed the external checkpoint protocol:

1. external coordinator start checkpoint;
2. packaged local Copilot supervisor graph launcher;
3. external coordinator end checkpoint;
4. external token span record; and
5. graph summary regenerated with `--token-record`.

Runtime result:

- bridge status: `accepted-candidate`;
- Copilot model: `qwen3.6:35b-a3b-bf16`;
- permission level: `autopilot`;
- `runSubagent` observed;
- final marker observed;
- authority validation passed;
- document-audit validation passed;
- graph-report validation passed;
- audit decision breakdown: `needs_coordinator_review = 5`; and
- subagent outcome: `accepted_without_repair`.

Tracked summaries:

- internal launcher-token summary:
  `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_split_02_v11_internal_summary.json`
- external coordinator-token summary:
  `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_split_02_v11_summary.json`

The internal launcher-contained token span again produced zero token delta and
is not usable economics evidence. The external coordinator span was usable:

- fresh supervisor input tokens: `4,226`;
- cached supervisor input tokens: `690,688`;
- supervisor output tokens: `746`;
- reasoning output tokens: `0`;
- total Codex token delta: `695,660`;
- estimated paid coordinator cost: `$0.138710`; and
- estimated paid coordinator cost per source artifact: `$0.027742`.

Interpretation: v11 proves that the external checkpoint protocol fixes the
fake-zero economics problem for packaged graph runs. The current measured cost
is higher than the earlier v8 hand-orchestrated accepted run because the v11
measurement includes the broader coordinator boundary around launcher
invocation and result handling. That is acceptable: v11 is the first credible
packaged-run cost datapoint, not yet an optimized one.

## Packaged Launcher Economics Comparison

Added a reproducible comparison artifact:

- `benchmarks/vscode_subagent_spike/p57_packaged_launcher_economics_comparison.json`
- `planning/phase57_packaged_launcher_economics_decision_packet.md`

The comparison normalizes the mixed v4-v11 summary shapes and marks whether
each economics datapoint is usable. It distinguishes accepted runtime quality
from credible paid-token measurement.

Key comparison:

- usable economics records: `4`;
- accepted records in the comparison set: `6`;
- cheapest usable accepted legacy run: v8 at `$0.092783` total, or `$0.018557`
  per source artifact;
- first usable external-checkpoint packaged run: v11 at `$0.138710` total, or
  `$0.027742` per source artifact; and
- internal packaged launcher spans for v10/v11 still show fake-zero token
  deltas and remain unusable for economics.

Interpretation: local Copilot supervision is working on this graph-shaped
audit task, but packaged-run economics are not yet optimized. The next useful
optimization target is coordinator overhead around launch/result inspection,
not worker task quality for this particular five-artifact audit node.

The decision packet is intentionally compact so future coordinator review can
start from one deterministic Markdown artifact instead of rereading raw JSON
summaries or chat history.

## Packaged Launcher V12 Decision-Packet Overhead Test

The v12 run used the same five source artifacts and the same external-token
measurement boundary as v11. The coordinator intentionally avoided manual JSON
inspection until after the deterministic summary and comparison artifacts were
regenerated.

Runtime result:

- bridge status: `accepted-candidate`;
- Copilot model: `qwen3.6:35b-a3b-bf16`;
- permission level: `autopilot`;
- `runSubagent` observed;
- final marker observed;
- authority validation passed;
- document-audit validation passed;
- graph-report validation passed;
- audit decision breakdown: `needs_coordinator_review = 5`; and
- subagent outcome: `accepted_without_repair`.

Economics result:

- fresh supervisor input tokens: `3,191`;
- cached supervisor input tokens: `838,144`;
- supervisor output tokens: `732`;
- reasoning output tokens: `22`;
- total Codex token delta: `842,067`;
- estimated paid coordinator cost: `$0.162815`; and
- estimated paid coordinator cost per source artifact: `$0.032563`.

Interpretation: v12 was runtime-clean but economically worse than v11. The
decision-packet pattern reduced manual inspection behavior, but the broader
Codex context/cache boundary still grew enough to increase measured cost. The
next useful experiment should not be another identical rerun. It should first
change the workflow surface to reduce paid coordinator cache/context churn.

## Packaged Launcher V13 Quiet-Output Overhead Test

The v13 run used the same five source artifacts and external-token measurement
boundary as v11 and v12, but added `--quiet-runtime-output` so the materializer
and Copilot bridge stdout/stderr were captured by the launcher instead of being
printed into the paid coordinator shell output.

Runtime result:

- bridge status: `accepted-candidate`;
- Copilot model: `qwen3.6:35b-a3b-bf16`;
- permission level: `autopilot`;
- `runSubagent` observed;
- final marker observed;
- authority validation passed;
- document-audit validation passed;
- graph-report validation passed;
- audit decision breakdown: `needs_coordinator_review = 5`; and
- subagent outcome: `accepted_after_supervisor_repair`.

Economics result:

- fresh supervisor input tokens: `1,077`;
- cached supervisor input tokens: `462,592`;
- supervisor output tokens: `438`;
- reasoning output tokens: `0`;
- total Codex token delta: `464,107`;
- estimated paid coordinator cost: `$0.088970`; and
- estimated paid coordinator cost per source artifact: `$0.017794`.

Interpretation: v13 is the first packaged external-checkpoint run to beat the
previous v8 legacy cost per source artifact. Quiet launcher output appears to
remove a real paid-token leak. The remaining quality caveat is that the
subagent still needed supervisor repair for item IDs and source paths, so the
next run should repeat quiet mode once to test cost stability and repair
frequency.

## Packaged Launcher V14 Quiet-Output Repeat

The v14 run repeated v13 with the same five source artifacts, quiet runtime
output, and external-token measurement boundary.

Runtime result:

- bridge status: `accepted-candidate`;
- Copilot model: `qwen3.6:35b-a3b-bf16`;
- permission level: `autopilot`;
- `runSubagent` observed;
- final marker observed;
- authority validation passed;
- document-audit validation passed;
- graph-report validation passed;
- audit decision breakdown: `needs_coordinator_review = 5`; and
- subagent outcome: `accepted_without_repair`.

Economics result:

- fresh supervisor input tokens: `877`;
- cached supervisor input tokens: `477,952`;
- supervisor output tokens: `437`;
- reasoning output tokens: `0`;
- total Codex token delta: `479,266`;
- estimated paid coordinator cost: `$0.091294`; and
- estimated paid coordinator cost per source artifact: `$0.018259`.

Interpretation: v14 confirms the quiet-output improvement is not a one-off.
The cost is slightly above v13 but still below v11 and v12, and near the v8
legacy cost. The subagent also reached `accepted_without_repair`, which removes
the main v13 quality caveat. The next experiment should treat quiet output as
the default packaged-launcher path and scale the work package rather than
repeat the same five-artifact job again.
