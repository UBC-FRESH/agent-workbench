# Phase 55 wave8_disagreement_verification Results

Raw verifier values and source quotes remain ignored under runtime paths.

- generated_utc: `2026-07-05T07:48:39Z`
- gate_result: `wave8-quote-repair-needed`
- verifier_model: `qwen3.6:35b-a3b-q8_0`
- parse_status: `parsed`

## Aggregate Totals

- verdict_counts: `{"both_correct_equivalent": 1, "both_wrong": 1, "insufficient_evidence": 1, "left_correct": 6}`
- resolved_fields: `8`
- needs_supervisor_fields: `1`
- invalid_verdict_fields: `0`
- quote_over_limit_fields: `3`
- invalid_chunk_id_fields: `0`
- worker_input_tokens: `17564`
- worker_output_tokens: `3190`
- worker_cash_cost_usd: `0.0`

## Verdicts

| Field | Verdict | Final Status | Quote Words | Reason Code |
| --- | --- | --- | ---: | --- |
| aac_effective_date | `both_correct_equivalent` | `found` | 17 | `source_supported` |
| aac_value | `left_correct` | `found` | 17 | `source_supported` |
| base_case_harvest_forecast | `left_correct` | `found` | 27 | `source_supported` |
| decision_rationale | `both_wrong` | `found` | 17 | `source_available` |
| document_title | `left_correct` | `found` | 11 | `source_supported` |
| inventory_reference_year | `left_correct` | `found` | 27 | `source_supported` |
| major_land_base_constraints | `left_correct` | `found` | 27 | `source_supported` |
| major_management_assumptions | `left_correct` | `found` | 23 | `source_supported` |
| sensitivity_cases | `insufficient_evidence` | `uncertain` | 12 | `mentions_but_no_values` |

## Recommendation

Send only unresolved verifier fields to paid supervisor audit: sensitivity_cases
