# Phase 55 wave8_disagreement_verification Results

Raw verifier values and source quotes remain ignored under runtime paths.

- generated_utc: `2026-07-05T09:02:35Z`
- gate_result: `wave8-quote-repair-needed`
- verifier_model: `qwen3.6:35b-a3b-bf16`
- parse_status: `parsed`

## Aggregate Totals

- verdict_counts: `{"both_correct_equivalent": 1, "left_correct": 4, "needs_supervisor": 1, "right_correct": 1}`
- resolved_fields: `6`
- needs_supervisor_fields: `1`
- invalid_verdict_fields: `0`
- quote_over_limit_fields: `1`
- invalid_chunk_id_fields: `0`
- worker_input_tokens: `17030`
- worker_output_tokens: `4619`
- worker_cash_cost_usd: `0.0`

## Verdicts

| Field | Verdict | Final Status | Quote Words | Reason Code |
| --- | --- | --- | ---: | --- |
| aac_value | `left_correct` | `found` | 27 | `source_supported` |
| base_case_harvest_forecast | `left_correct` | `found` | 18 | `source_supported` |
| decision_rationale | `needs_supervisor` | `uncertain` | 15 | `out_of_range` |
| document_title | `both_correct_equivalent` | `found` | 18 | `source_supported` |
| inventory_reference_year | `right_correct` | `found` | 11 | `source_supported` |
| major_land_base_constraints | `left_correct` | `uncertain` | 12 | `partial_source_match` |
| major_management_assumptions | `left_correct` | `found` | 24 | `source_supported` |

## Recommendation

Send only unresolved verifier fields to paid supervisor audit: decision_rationale
