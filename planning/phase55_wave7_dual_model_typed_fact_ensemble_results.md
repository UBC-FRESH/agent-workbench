# Phase 55 wave7_dual_model_typed_fact_ensemble Comparison

Raw candidate values and source quotes remain ignored under runtime paths.

- generated_utc: `2026-07-05T09:01:18Z`
- packet_id: `wave7_dual_model_typed_fact_ensemble__tsa23_2012_23ts13ra__typed_fact_x2__qwen3-6-35b-a3b-bf16-gpt-oss-120b`
- gate_result: `wave7-ready-for-disagreement-verification`
- models: `qwen3.6:35b-a3b-bf16, gpt-oss:120b`

## Candidate Summaries

| Model | Status | Parse | Fields | Input Tokens | Output Tokens |
| --- | --- | --- | ---: | ---: | ---: |
| qwen3.6:35b-a3b-bf16 | `completed` | `parsed` | 15 | 14013 | 4910 |
| gpt-oss:120b | `completed` | `parsed` | 15 | 14881 | 2641 |

## Aggregate Totals

- candidate_count: `2`
- parsed_candidates: `2`
- field_count: `15`
- agreement_counts: `{"both_not_found": 2, "status_disagreement": 4, "value_agreement": 6, "value_disagreement": 3}`
- fields_requiring_verification: `7`
- quote_over_limit_fields: `2`
- invalid_chunk_id_fields: `0`
- schema_issue_fields: `1`
- worker_input_tokens: `28894`
- worker_output_tokens: `7551`
- worker_cash_cost_usd: `0.0`

## Field Comparison

| Field | Agreement Class | Left Status | Right Status | Left Quote Words | Right Quote Words | Schema Issue |
| --- | --- | --- | --- | ---: | ---: | --- |
| aac_effective_date | `value_agreement` | `found` | `found` | 12 | 4 | `False` |
| aac_units | `value_agreement` | `found` | `found` | 9 | 11 | `False` |
| aac_value | `value_disagreement` | `found` | `found` | 17 | 17 | `False` |
| base_case_harvest_forecast | `value_disagreement` | `found` | `found` | 32 | 17 | `False` |
| decision_rationale | `status_disagreement` | `uncertain` | `not_found` | 13 | 0 | `False` |
| determination_year | `value_agreement` | `found` | `found` | 17 | 8 | `False` |
| document_title | `value_disagreement` | `found` | `found` | 7 | 11 | `False` |
| inventory_reference_year | `status_disagreement` | `uncertain` | `found` | 33 | 11 | `True` |
| major_land_base_constraints | `status_disagreement` | `uncertain` | `not_found` | 16 | 0 | `False` |
| major_management_assumptions | `status_disagreement` | `uncertain` | `not_found` | 19 | 0 | `False` |
| sensitivity_cases | `both_not_found` | `not_found` | `not_found` | 0 | 0 | `False` |
| thlb_area | `value_agreement` | `found` | `found` | 9 | 12 | `False` |
| total_area | `value_agreement` | `found` | `found` | 20 | 14 | `False` |
| tsa_name | `value_agreement` | `found` | `found` | 12 | 10 | `False` |
| tsa_number | `both_not_found` | `not_found` | `not_found` | 0 | 0 | `False` |

## Recommendation

Build a verifier ticket for 7 disagreement or weak-evidence fields; do not send both full raw candidates to the paid supervisor unless the verifier fails.
