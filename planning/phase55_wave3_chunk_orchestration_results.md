# Phase 55 wave3_chunk_orchestration Results

Raw worker outputs and source quotes remain ignored under runtime paths.

- generated_utc: `2026-07-05T04:06:27Z`
- gate_result: `wave3_chunk_orchestration-needs-repair-before-scaling`

## Aggregate Totals

- worker_runs: `7`
- completed_runs: `7`
- parseable_json_records: `95`
- malformed_lines: `0`
- requested_chunks: `7`
- covered_valid_chunks: `7`
- invalid_chunk_id_records: `9`
- source_quote_over_25_words: `22`
- worker_input_tokens: `57657`
- worker_output_tokens: `25514`
- worker_cash_cost_usd: `0.0`

## Runs

| Packet | Status | Shape | Requested Chunks | Covered Chunks | Records | Bad Lines | Invalid Chunk IDs | Quote Violations | Input Tokens | Output Tokens |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| wave3_chunk_orchestration__tsa23_2012_23ts13ra__chunk01__qwen3-coder-latest | `completed` | `structure_chunk` | 1 | 1 | 40 | 0 | 0 | 3 | 7668 | 10247 |
| wave3_chunk_orchestration__tsa23_2012_23ts13ra__chunk02__qwen3-coder-latest | `completed` | `structure_chunk` | 1 | 1 | 8 | 0 | 6 | 6 | 8732 | 2243 |
| wave3_chunk_orchestration__tsa23_2012_23ts13ra__chunk03__qwen3-coder-latest | `completed` | `structure_chunk` | 1 | 1 | 13 | 0 | 0 | 5 | 9311 | 3827 |
| wave3_chunk_orchestration__tsa23_2012_23ts13ra__chunk04__qwen3-coder-latest | `completed` | `structure_chunk` | 1 | 1 | 11 | 0 | 0 | 1 | 9942 | 2963 |
| wave3_chunk_orchestration__tsa23_2012_23ts13ra__chunk05__qwen3-coder-latest | `completed` | `structure_chunk` | 1 | 1 | 9 | 0 | 0 | 2 | 9580 | 2424 |
| wave3_chunk_orchestration__tsa23_2012_23ts13ra__chunk06__qwen3-coder-latest | `completed` | `structure_chunk` | 1 | 1 | 9 | 0 | 0 | 5 | 8501 | 2475 |
| wave3_chunk_orchestration__tsa23_2012_23ts13ra__chunk07__qwen3-coder-latest | `completed` | `structure_chunk` | 1 | 1 | 5 | 0 | 3 | 0 | 3923 | 1335 |

## Recommendation

Use chunk-orchestrated tickets as the next extraction default if coverage improves; follow with a delegated quote-normalization repair pass before paid supervisor source audit.

## Interpretation

This run removed the hidden 24-record cap from generated tickets and split the
2012 rationale into seven single-chunk worker calls. Compared with the earlier
single `structure_x8` ticket, coverage improved from four of seven chunks to
seven of seven chunks. Total parseable records increased from 24 to 95.

The tradeoff is higher total output volume and two deterministic format defects:

- chunk 2 returned six records with `tsa2012_23ts13ra::pages_008_015` instead
  of the allowed `tsa23_2012_23ts13ra::pages_008_015`;
- chunk 7 returned three records with `tsa2012_23ts13ra::pages_043_048` instead
  of the allowed `tsa23_2012_23ts13ra::pages_043_048`.

These are repairable identifier-copy errors, not source-understanding failures.
They should be handled by a deterministic validator/repair prepass or a cheap
local repair worker before any paid supervisor source audit.

The quote-length defect also improved relative to the old x8 run: 22 of 95
records exceeded the 25-word quote guideline, versus 23 of 24 records in the
old capped x8 run. It is still a repair target, but it is no longer dominating
almost every record.
