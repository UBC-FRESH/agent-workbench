# Phase 55 wave3_qwen36_bf16_chunk_ab Results

Raw worker outputs and source quotes remain ignored under runtime paths.

- generated_utc: `2026-07-05T07:05:23Z`
- gate_result: `wave3_qwen36_bf16_chunk_ab-needs-repair-before-scaling`

## Aggregate Totals

- worker_runs: `7`
- completed_runs: `7`
- parseable_json_records: `123`
- malformed_lines: `1`
- requested_chunks: `7`
- covered_valid_chunks: `7`
- invalid_chunk_id_records: `14`
- source_quote_over_25_words: `22`
- worker_input_tokens: `58945`
- worker_output_tokens: `40422`
- worker_cash_cost_usd: `0.0`

## Runs

| Packet | Status | Shape | Requested Chunks | Covered Chunks | Records | Bad Lines | Invalid Chunk IDs | Quote Violations | Input Tokens | Output Tokens |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| wave3_qwen36_bf16_chunk_ab__tsa23_2012_23ts13ra__chunk01__qwen3-6-35b-a3b-bf16 | `completed` | `structure_chunk` | 1 | 1 | 29 | 0 | 0 | 0 | 7847 | 9078 |
| wave3_qwen36_bf16_chunk_ab__tsa23_2012_23ts13ra__chunk02__qwen3-6-35b-a3b-bf16 | `completed` | `structure_chunk` | 1 | 1 | 20 | 0 | 0 | 0 | 8918 | 6616 |
| wave3_qwen36_bf16_chunk_ab__tsa23_2012_23ts13ra__chunk03__qwen3-6-35b-a3b-bf16 | `completed` | `structure_chunk` | 1 | 1 | 17 | 0 | 0 | 6 | 9495 | 5707 |
| wave3_qwen36_bf16_chunk_ab__tsa23_2012_23ts13ra__chunk04__qwen3-6-35b-a3b-bf16 | `completed` | `structure_chunk` | 1 | 1 | 16 | 1 | 14 | 6 | 10117 | 5523 |
| wave3_qwen36_bf16_chunk_ab__tsa23_2012_23ts13ra__chunk05__qwen3-6-35b-a3b-bf16 | `completed` | `structure_chunk` | 1 | 1 | 27 | 0 | 0 | 2 | 9772 | 8506 |
| wave3_qwen36_bf16_chunk_ab__tsa23_2012_23ts13ra__chunk06__qwen3-6-35b-a3b-bf16 | `completed` | `structure_chunk` | 1 | 1 | 11 | 0 | 0 | 8 | 8691 | 3897 |
| wave3_qwen36_bf16_chunk_ab__tsa23_2012_23ts13ra__chunk07__qwen3-6-35b-a3b-bf16 | `completed` | `structure_chunk` | 1 | 1 | 3 | 0 | 0 | 0 | 4105 | 1095 |

## Recommendation

Classify this wave as **comparable but different defects**, not a clean win.
Qwen3.6 BF16 is worth keeping in the candidate set because it produced broader
record coverage than the coding baseline and had much better quote discipline
on the first two chunks. It is not ready to scale without validator/repair,
because chunk 04 introduced invalid sub-page chunk IDs and one malformed JSONL
line.

## Comparison Against Wave 3.1

Wave 3.1 used `qwen3-coder:latest` on the same seven rationale chunks with
the same uncapped single-chunk ticket shape. Wave 3.2 changed only the worker
model to `qwen3.6:35b-a3b-bf16`.

| Metric | Wave 3.1 qwen3-coder | Wave 3.2 qwen3.6 BF16 | Delta |
| --- | ---: | ---: | ---: |
| worker_runs | 7 | 7 | 0 |
| completed_runs | 7 | 7 | 0 |
| parseable_json_records | 95 | 123 | 28 |
| malformed_lines | 0 | 1 | 1 |
| requested_chunks | 7 | 7 | 0 |
| covered_valid_chunks | 7 | 7 | 0 |
| invalid_chunk_id_records | 9 | 14 | 5 |
| source_quote_over_25_words | 22 | 22 | 0 |
| worker_input_tokens | 57657 | 58945 | 1288 |
| worker_output_tokens | 25514 | 40422 | 14908 |
| worker_cash_cost_usd | 0.0 | 0.0 | 0.0 |

## Defect Pattern

- BF16 produced 123 parseable records versus 95 for the coding baseline.
- BF16 preserved valid chunk coverage across all seven chunks.
- BF16 used substantially more output tokens, so the local-token burden is
  higher even though cash cost remains zero.
- BF16 improved quote discipline on chunks 01 and 02, where the coding
  baseline had 9 combined quote-length violations and BF16 had none.
- BF16 still had 22 quote-length violations overall, matching the baseline
  total.
- BF16 concentrated chunk-ID failure in chunk 04 by inventing sub-page IDs
  such as `tsa23_2012_23ts13ra::pages_025` instead of reusing the allowed
  chunk ID exactly.

## Next Design Implication

The model comparison supports the current workflow pivot: generic structure
metadata tickets should be replaced by staged section-map extraction, typed
TSR fact extraction, repair/normalization, and quote verification. The next
ticket design should make `chunk_id` a copied constant instead of a generated
field, move quote verification into a separate validator/repair step, and
measure whether BF16's higher record coverage survives typed extraction.
