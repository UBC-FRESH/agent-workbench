# Phase 55 Wave 8 Disagreement Verification Results

Raw verifier values and source quotes remain ignored under runtime paths.

- generated_utc: `2026-07-05T07:37:35Z`
- gate_result: `wave8-ready-for-supervisor-audit-sampling`
- verifier_model: `qwen3.6:35b-a3b-bf16`
- parse_status: `parsed`

## Aggregate Totals

- verdict_counts: `{"both_correct_equivalent": 3, "left_correct": 6}`
- resolved_fields: `9`
- needs_supervisor_fields: `0`
- quote_over_limit_fields: `0`
- invalid_chunk_id_fields: `0`
- worker_input_tokens: `17554`
- worker_output_tokens: `4072`
- worker_cash_cost_usd: `0.0`

## Verdicts

| Field | Verdict | Final Status | Quote Words | Reason Code |
| --- | --- | --- | ---: | --- |
| aac_effective_date | `both_correct_equivalent` | `found` | 17 | `source_supported` |
| aac_value | `left_correct` | `found` | 21 | `source_supported` |
| base_case_harvest_forecast | `left_correct` | `found` | 20 | `source_supported` |
| decision_rationale | `left_correct` | `found` | 17 | `source_supported` |
| document_title | `both_correct_equivalent` | `found` | 7 | `source_supported` |
| inventory_reference_year | `left_correct` | `found` | 18 | `source_supported` |
| major_land_base_constraints | `left_correct` | `found` | 16 | `source_supported` |
| major_management_assumptions | `left_correct` | `found` | 22 | `source_supported` |
| sensitivity_cases | `both_correct_equivalent` | `not_found` | 14 | `mentioned_without_detail` |

## Recommendation

Use supervisor audit sampling to check verifier correctness before final JSON normalization.
