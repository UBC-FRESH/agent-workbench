# P57 Packaged Launcher Economics Decision Packet

## Decision Signal

- Local Copilot supervision is working for this five-artifact graph audit task.
- External coordinator checkpoints are required for credible packaged-run economics.
- The latest external-checkpoint summary records expected model `qwen3.6:35b-a3b-bf16` and observed model `qwen3.6:35b-a3b-bf16` with match status `matched`.
- The cheapest accepted usable span is `p57_graph_batch_all_p55_summaries_v1_split_01_02_v1_summary` at `$0.109171` total and `$0.010917` per source artifact.
- The cheapest usable external-checkpoint packaged span is `p57_graph_batch_all_p55_summaries_v1_split_01_02_v1_summary` at `$0.109171` total and `$0.010917` per source artifact.
- The latest external-checkpoint packaged span is `p57_graph_batch_all_p55_summaries_v1_split_03_v1_summary` at `$0.080875` total and `$0.020219` per source artifact.

## Recommended Next Experiment

Treat pre-materialized graph tickets and quiet runtime output as the default packaged-launcher path. Before another full-batch run, stabilize mechanical repair behavior by replacing ad hoc delete/recreate repair loops with generated overwrite-only repair helpers. After that, test one batch-level supervisor ticket with external-token accounting.

Success criterion: accepted-candidate validation with external-checkpoint cost per source artifact at or below the quiet-output repeat band observed in v13-v14. Secondary criterion: document whether subagent repair frequency stays low as the work package grows.

## Split 01 Scale Probe

The expected-model gated split_01 v1 run matched `qwen3.6:35b-a3b-bf16` but stopped after the materializer command, leaving both required reports missing. The split_01 v2 retry used a stronger full-graph bridge prompt. That moved the local supervisor further: it invoked the subagent, wrote both runtime reports, and all deterministic validators passed. The bridge still rejected the run because the materializer command was executed twice, which remains a protocol deviation. The split_01 v3 pre-materialized retry fixed the materializer boundary but stopped after the first failed validator. The split_01 v4 pre-materialized retry accepted: model provenance matched, no materializer commands were run by Copilot, the subagent was invoked, both reports were written, all expected validators ran, and the bridge reported no deviations. The split_01 v5 external-checkpoint rerun accepted with usable economics and no Copilot-side materializer commands, but no subagent tool invocation was observed; the local supervisor appears to have completed the bounded repair/report task directly.

Interpretation: coordinator-owned deterministic setup is the better boundary. The free local supervisor should receive a pre-materialized runtime ticket and own audit, repair, validation, and graph reporting. This removes a repeatable setup-command failure mode while preserving the useful local-supervisor/subagent behavior.

## Multi-Split Scale Probe

The split_01+split_02 v1 package ran two five-artifact pre-materialized child graph jobs under one external coordinator-token span. Both child runs accepted after deterministic verification, both matched the expected `qwen3.6:35b-a3b-bf16` model, both observed the subagent tool, and Copilot ran zero materializer commands across the package. The external span cost was `$0.109171` total, or `$0.010917` per source artifact, improving on the previous five-artifact v5 cost of `$0.013057` per source artifact.

Interpretation: the coordinator-owned setup boundary amortizes in the expected direction as package size grows. The next question is whether the same pattern holds for full 14-artifact coverage or whether a single batch-level supervisor ticket reduces coordination overhead further.

## Full 14-Artifact Coverage

The full-coverage v1 aggregate combines the accepted split_01+split_02 package with accepted split_03 v1 for all fourteen source summaries in the batch manifest. All child packages matched expected model `qwen3.6:35b-a3b-bf16`, used pre-materialized audit tickets, observed subagent tool use, ran zero Copilot-side materializer commands, and passed deterministic validation. The summed external-span cost was `$0.190046` total, or `$0.013575` per source artifact.

Interpretation: full coverage stayed accepted, but summed-span cost is higher than the 10-artifact package because split_03 was measured in a separate external span. The next optimization target is reducing span/session overhead, not changing the coordinator-owned setup boundary.

## Failed Uninterrupted Full-Batch Retries

Two uninterrupted full-batch retries failed before completing all splits. The first failed by emitting the final marker without creating reports or running validators. The second created valid reports but used a destructive `Remove-Item` repair loop against the assigned audit report, which the bridge correctly rejected. These failures indicate that the next optimization should harden mechanical repair tooling before a single batch-level supervisor ticket is treated as a reliable economics experiment.

## Comparison Table

| Record | Model | Accepted | Economics | Cost | Cost/source | Boundary | Subagent tool | Subagent status |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| p57_graph_batch_all_p55_summaries_v1_full_14_v1_summary | `qwen3.6:35b-a3b-bf16` | yes | yes | $0.190046 | $0.013575 | summed_external_coordinator_spans | yes | accepted_child_packages |
| p57_graph_batch_all_p55_summaries_v1_full_14_v10_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.000000 | $0.000000 | legacy | yes | needs_review |
| p57_graph_batch_all_p55_summaries_v1_full_14_v11_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.071044 | $0.005075 | external_coordinator_span | yes | needs_review |
| p57_graph_batch_all_p55_summaries_v1_full_14_v14_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.084697 | $0.006050 | external_coordinator_span | yes | needs_review |
| p57_graph_batch_all_p55_summaries_v1_full_14_v2_aborted_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.129425 | $0.025885 | external_coordinator_span | no | n/a |
| p57_graph_batch_all_p55_summaries_v1_full_14_v3_aborted_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.136821 | $0.027364 | external_coordinator_span | yes | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_01_02_v1_summary | `qwen3.6:35b-a3b-bf16` | yes | yes | $0.109171 | $0.010917 | external_coordinator_span | yes | accepted_child_runs |
| p57_graph_batch_all_p55_summaries_v1_split_01_v1_internal_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.000000 | $0.000000 | legacy | no | n/a |
| p57_graph_batch_all_p55_summaries_v1_split_01_v10_internal_summary | `qwen3.6:35b-a3b-bf16` | yes | no | $0.000000 | $0.000000 | legacy | yes | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_01_v11_internal_summary | `qwen3.6:35b-a3b-bf16` | yes | no | $0.000000 | $0.000000 | legacy | yes | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_01_v14_internal_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.000000 | $0.000000 | legacy | yes | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_01_v2_internal_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.000000 | $0.000000 | legacy | yes | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_01_v3_internal_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.000000 | $0.000000 | legacy | yes | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_01_v4_internal_summary | `qwen3.6:35b-a3b-bf16` | yes | no | $0.000000 | $0.000000 | legacy | yes | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_01_v5_internal_summary | `qwen3.6:35b-a3b-bf16` | yes | no | $0.000000 | $0.000000 | legacy | no | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_01_v5_summary | `qwen3.6:35b-a3b-bf16` | yes | yes | $0.065285 | $0.013057 | external_coordinator_span | no | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_01_v6_internal_summary | `qwen3.6:35b-a3b-bf16` | yes | no | $0.000000 | $0.000000 | legacy | yes | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_01_v7_internal_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.000000 | $0.000000 | legacy | no | n/a |
| p57_graph_batch_all_p55_summaries_v1_split_01_v8_internal_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.000000 | $0.000000 | legacy | yes | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_01_v9_internal_summary | `qwen3.6:35b-a3b-bf16` | yes | no | $0.000000 | $0.000000 | legacy | yes | unavailable_supervisor_completed |
| p57_graph_batch_all_p55_summaries_v1_split_02_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.092546 | $0.018509 | legacy | yes | n/a |
| p57_graph_batch_all_p55_summaries_v1_split_02_v10_internal_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.000000 | $0.000000 | legacy | yes | accepted_without_repair |
| p57_graph_batch_all_p55_summaries_v1_split_02_v10_summary | `qwen3.6:35b-a3b-bf16` | yes | no | $0.000000 | $0.000000 | legacy | yes | accepted_without_repair |
| p57_graph_batch_all_p55_summaries_v1_split_02_v11_internal_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.000000 | $0.000000 | legacy | yes | accepted_without_repair |
| p57_graph_batch_all_p55_summaries_v1_split_02_v11_summary | `qwen3.6:35b-a3b-bf16` | yes | yes | $0.138710 | $0.027742 | external_coordinator_span | yes | accepted_without_repair |
| p57_graph_batch_all_p55_summaries_v1_split_02_v12_internal_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.000000 | $0.000000 | legacy | yes | accepted_without_repair |
| p57_graph_batch_all_p55_summaries_v1_split_02_v12_summary | `qwen3.6:35b-a3b-bf16` | yes | yes | $0.162815 | $0.032563 | external_coordinator_span | yes | accepted_without_repair |
| p57_graph_batch_all_p55_summaries_v1_split_02_v13_internal_summary | `qwen3.6:35b-a3b-bf16` | yes | no | $0.000000 | $0.000000 | legacy | yes | accepted_without_repair |
| p57_graph_batch_all_p55_summaries_v1_split_02_v13_summary | `qwen3.6:35b-a3b-bf16` | yes | yes | $0.088970 | $0.017794 | external_coordinator_span | yes | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_02_v14_internal_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.000000 | $0.000000 | legacy | yes | accepted_without_repair |
| p57_graph_batch_all_p55_summaries_v1_split_02_v14_summary | `qwen3.6:35b-a3b-bf16` | yes | yes | $0.091294 | $0.018259 | external_coordinator_span | yes | accepted_without_repair |
| p57_graph_batch_all_p55_summaries_v1_split_02_v15_internal_summary | `qwen3.6:35b-a3b-bf16` | yes | no | $0.000000 | $0.000000 | legacy | yes | accepted_without_repair |
| p57_graph_batch_all_p55_summaries_v1_split_02_v3_summary | `qwen3.6:35b-a3b-bf16` | yes | no | n/a | n/a | legacy | yes | n/a |
| p57_graph_batch_all_p55_summaries_v1_split_02_v4_summary | `qwen3.6:35b-a3b-bf16` | yes | yes | $0.146603 | $0.029321 | legacy | yes | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_02_v5_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.542613 | $0.108523 | legacy | yes | rejected_supervisor_replaced |
| p57_graph_batch_all_p55_summaries_v1_split_02_v6_summary | `qwen3.6:35b-a3b-bf16` | yes | no | n/a | n/a | legacy | yes | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_02_v7_summary | `qwen3.6:35b-a3b-bf16` | yes | yes | $0.120379 | $0.024076 | legacy | yes | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_02_v8_summary | `qwen3.6:35b-a3b-bf16` | yes | yes | $0.092783 | $0.018557 | legacy | yes | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_02_v9_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.000000 | $0.000000 | legacy | yes | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_03_v1_internal_summary | `qwen3.6:35b-a3b-bf16` | yes | no | $0.000000 | $0.000000 | legacy | yes | accepted_without_repair |
| p57_graph_batch_all_p55_summaries_v1_split_03_v1_summary | `qwen3.6:35b-a3b-bf16` | yes | yes | $0.080875 | $0.020219 | external_coordinator_span | yes | accepted_without_repair |
| p57_graph_batch_all_p55_summaries_v1_split_03_v11_internal_summary | `qwen3.6:35b-a3b-bf16` | yes | no | $0.000000 | $0.000000 | legacy | yes | accepted_after_supervisor_repair |
| p57_graph_batch_all_p55_summaries_v1_split_03_v14_internal_summary | `qwen3.6:35b-a3b-bf16` | no | no | $0.000000 | $0.000000 | legacy | no | accepted_after_supervisor_repair |
