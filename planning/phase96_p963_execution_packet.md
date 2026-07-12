# Phase 96.3 Execution Packet

This packet turns P96.1/P96.2 planning into a concrete bounded run definition
for issue #588.

## Scope

- Parent issue: #585
- Child issue: #588
- Branch: feature/p96-yield-audit-cost-model-comparison
- Run id: `p96-3-lane-compare-tsa23-2012-23ts13ra-a`
- Corpus/document: `bc_tsr_tsa23_public_1995_present` / `tsa23_2012_23ts13ra`
- Chunk set: pages 1-22 (3 chunks)

## Tracked Manifest

- Manifest: `benchmarks/document_library/tsa23_tsr/p96_model_lane_comparison_manifest.json`

The manifest pins the comparison boundary for one document and one chunk set,
including:

- baseline lane: `qwen3.6:35b-a3b-bf16`
- candidate lane: `qwen3.6:35b-a3b-q8_0`
- fixed variables and thresholds (5% yield delta, 15% audit-cost delta)
- expected runtime evidence paths
- required P60 outcome-semantics fields

## Remote Ollama Verification Rule

Model availability must be verified in the VS Code Copilot Chat model picker
under provider `ollama`, not via local `localhost:11434` calls.

Required evidence artifact for P96.3:

- `runtime/agent_jobs/p96_3_model_inventory_snapshot.md`

The snapshot should include the visible ollama model list from the picker and
explicitly confirm whether both baseline and candidate lanes are available.

## Runtime Ticket And Result Paths

The delegated run should use:

- ticket: `runtime/agent_jobs/p96_3_lane_comparison_ticket.md`
- result: `runtime/agent_jobs/p96_3_lane_comparison_result.md`
- blocker: `runtime/agent_jobs/p96_3_lane_comparison_blocker.md`
- heartbeat: `runtime/agent_jobs/p96_3_lane_comparison.heartbeat.jsonl`

## Comparison Outputs Expected

P96.3 should produce a sanitized summary at:

- `benchmarks/document_library/tsa23_tsr/p96_model_lane_comparison_execution_summary.json`

Minimum summary fields:

- lane-level accepted/repairable/rejected counts and percentages
- lane-level supervisor audit-token spans
- `quality_validated_candidate`
- `protocol_accepted_candidate`
- `economics_usable`
- preliminary verdict suggestion for P96.4

## Stop Conditions

Stop and write blocker when:

- either lane is missing from Copilot Chat ollama provider list;
- model identity cannot be independently verified;
- selected chunk set cannot be processed with deterministic validation;
- token ledger cannot be captured at lane boundary.
