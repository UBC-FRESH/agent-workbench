# P57 Full-Batch Uninterrupted Span Retry Results

## Summary

Two attempts were made to run full-14 coverage as one uninterrupted external-span sequence starting from split_01. Both attempts failed before completing the full sequence, but they failed in different and useful ways.

## Attempt v2: final-marker-only early stop

- Job: `p57_graph_batch_all_p55_summaries_v1_split_01_v7`
- External span: `runtime/supervisor_tokens/p57_graph_batch_all_p55_summaries_v1_full_14_v2_external/external.tokens.json`
- Model matched expected `qwen3.6:35b-a3b-bf16`.
- Copilot emitted the final marker without running expected commands and without creating the audit or graph report.
- External span cost: `$0.129425`.
- Result: rejected protocol failure.

## Attempt v3: destructive repair loop

- Job: `p57_graph_batch_all_p55_summaries_v1_split_01_v8`
- External span: `runtime/supervisor_tokens/p57_graph_batch_all_p55_summaries_v1_full_14_v3_external/external.tokens.json`
- Model matched expected `qwen3.6:35b-a3b-bf16`.
- Copilot created valid reports and all deterministic validators passed.
- The bridge rejected the run because Copilot used `Remove-Item` on the assigned audit report during repair before recreating it.
- External span cost is recorded in the aborted v3 summary.
- Result: rejected protocol failure, despite valid final artifacts.

## Interpretation

The coordinator-owned pre-materialized setup boundary is still supported by the accepted v4, v5, split_01+02, split_03, and full-14 aggregate evidence. The weak point is full-batch uninterrupted execution stability, not the graph shape itself.

The next contract improvement should make repair tooling safer and more mechanical:

- Explicitly forbid `Remove-Item`, `del`, and `rm` for report repair.
- Prefer generated repair helper commands over ad hoc inline repair scripts.
- Consider adding a bridge-level hard stop or rejection reason category for destructive repair commands.
- Consider running a single batch-level supervisor ticket only after the no-delete repair contract is stable.

## Repair-helper retry

After the destructive-repair failure, the ticket framework was hardened with a generated overwrite-only repair helper:

- Helper: `scripts/repair_document_artifact_graph_reports.py`
- Retry job: `p57_graph_batch_all_p55_summaries_v1_split_01_v9`
- Summary: `benchmarks/vscode_subagent_spike/p57_graph_batch_all_p55_summaries_v1_split_01_v9_internal_summary.json`
- Result: accepted candidate after bridge reparse.

The v9 retry used the same five split_01 source summaries as v8. Copilot ran in autopilot mode with observed model `qwen3.6:35b-a3b-bf16`, observed the subagent tool, wrote both runtime reports, ran the deterministic validators, and passed authority, audit-report, and graph-report verification. The report was initially classified as needing review only because the bridge treated the conditional repair helper as a mandatory command even though no repair helper was needed. The bridge now treats the repair helper as conditional expected behavior.

This means the immediate "bad ticket" surface was a bridge/ticket-policy issue, not a failed Copilot work product. The next larger experiment should be a full batch-level supervisor ticket or an uninterrupted multi-split run with external token checkpoints, using the repair-helper ticket shape as the baseline.
