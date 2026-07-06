# P57 Batch Runner v11 Results

## Summary

The v11 run tested a first-class split-batch wrapper over the 14-artifact P57 document-artifact audit package. The batch runner launched three pre-materialized child graph jobs under one external coordinator-token span and attached the measured token record to the aggregate summary.

This was not a fully accepted protocol run, but it was a useful result:

- All 14 source artifacts received deterministic audit reports.
- All child reports passed authority validation, document-audit verification, and graph-report verification.
- The aggregate `quality_validated_candidate` field is `true`.
- The aggregate `accepted_candidate` field is `false` because split_02 reran the lower-level materializer despite the pre-materialized ticket boundary.

## Artifacts

- Batch runner: `scripts/run_document_artifact_graph_batch.py`
- Aggregate summary: `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_full_14_v11_summary.json`
- External token record: `runtime/supervisor_tokens/p57_graph_batch_all_p55_summaries_v1_full_14_v11_external/external.tokens.json`
- Child summaries:
  - `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_split_01_v11_internal_summary.json`
  - `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_split_02_v11_internal_summary.json`
  - `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_split_03_v11_internal_summary.json`

## Token Economics

The external coordinator span measured:

- Fresh supervisor input tokens: `846`
- Cached supervisor input tokens: `365824`
- Supervisor output tokens: `396`
- Total Codex token delta: `367066`
- Estimated paid coordinator cost: `$0.071044`
- Estimated paid coordinator cost per source artifact: `$0.005075`

Because the batch was not protocol-accepted, the summary marks `economics_usable` as `false`. The measured cost is still useful diagnostic evidence for the coordinator overhead of a full 14-artifact batch attempt.

## Child Results

| Child | Sources | Accepted | Quality Validators | Subagent Tool | Materializer Commands |
| --- | ---: | --- | --- | --- | ---: |
| split_01 v11 | 5 | yes | pass | yes | 0 |
| split_02 v11 | 5 | no | pass | yes | 1 |
| split_03 v11 | 4 | yes | pass | yes | 0 |

Split_02 was rejected only because Copilot ran `materialize_document_artifact_audit.py` after the coordinator had already pre-materialized the audit ticket. The command was safe and runtime-only, and the final reports were valid, but it remains a protocol deviation because the supervisor boundary is supposed to start from the existing audit ticket.

## Interpretation

The free Copilot/Ollama supervisor can now carry a 14-artifact package to quality-valid runtime reports with subagent use observed in every child run. The remaining engineering problem is not semantic audit quality in this test; it is enforcing or reframing the setup boundary.

There are two plausible next moves:

- Keep the strict boundary and harden the bridge/ticket so any materializer command is impossible or immediately blocked.
- Reclassify a single idempotent runtime-only materializer rerun as a tolerated setup refresh when the final reports validate, while still tracking it as protocol overhead.

For the developer goal, the second option may be more pragmatic: it preserves the economic and quality signal while still making the boundary deviation explicit. The first option is cleaner if the goal is a strict role-hierarchy proof.

## Follow-up: clean pre-materialized split_02 retry

The generated graph ticket was tightened after v11 so pre-materialized jobs no longer list `materialize_runtime_job` in the supervisor action list. The setup node remains only as a graph-report record that must be marked completed because the coordinator already completed setup. The ticket also removes repeated "materializer command" warning text from the pre-materialized path, which was likely acting as an attractive nuisance for the local supervisor.

Follow-up run:

- Job: `p57_graph_batch_all_p55_summaries_v1_split_02_v13`
- Marker: `P57_GRAPH_BATCH_ALL_P55_SUMMARIES_V1_SPLIT_02_V13_CLEAN`
- Summary: `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_split_02_v13_internal_summary.json`

Result:

- Accepted candidate: `true`
- Materializer command count: `0`
- Subagent tool observed: `true`
- Authority validation: pass
- Document-audit verifier: pass
- Graph-report verifier: pass
- Supervisor score: `1.0`

This proves that the strict pre-materialized boundary can be enforced for the formerly problematic split_02 work package when the setup node is removed from the action list and the bridge accepts bounded report writes produced with `System.IO.File.WriteAllText`.

## Follow-up: v14 suffix caveat

A later `v14` full-batch attempt produced quality-valid child summaries but is not a clean protocol experiment because `v14` markers had already appeared in prior Copilot history. The bridge evidence included stale-looking titles and extra diagnostic commands. Keep the measured external token span as diagnostic overhead evidence only; do not treat it as the clean full-batch acceptance test.

The next full-batch acceptance test should use a high-entropy suffix that has never appeared in the VS Code chat session store.
