# Phase 55 wave9_json_repair Results

Raw verifier values and source quotes remain ignored under runtime paths.

- generated_utc: `2026-07-05T07:45:24Z`
- gate_result: `wave8-ready-for-supervisor-audit-sampling`
- verifier_model: `qwen3-coder-next:latest`
- parse_status: `parsed`

## Aggregate Totals

- verdict_counts: `{"both_correct_equivalent": 1, "needs_supervisor": 8}`
- resolved_fields: `1`
- needs_supervisor_fields: `8`
- invalid_verdict_fields: `0`
- quote_over_limit_fields: `0`
- invalid_chunk_id_fields: `0`
- worker_input_tokens: `18691`
- worker_output_tokens: `935`
- worker_cash_cost_usd: `0.0`

## Verdicts

| Field | Verdict | Final Status | Quote Words | Reason Code |
| --- | --- | --- | ---: | --- |
| aac_effective_date | `both_correct_equivalent` | `found` | 4 | `source_quotes_applicable` |
| aac_value | `needs_supervisor` | `uncertain` | 0 | `unreviewed` |
| base_case_harvest_forecast | `needs_supervisor` | `uncertain` | 0 | `unreviewed` |
| decision_rationale | `needs_supervisor` | `uncertain` | 0 | `unreviewed` |
| document_title | `needs_supervisor` | `uncertain` | 0 | `unreviewed` |
| inventory_reference_year | `needs_supervisor` | `uncertain` | 0 | `unreviewed` |
| major_land_base_constraints | `needs_supervisor` | `uncertain` | 0 | `unreviewed` |
| major_management_assumptions | `needs_supervisor` | `uncertain` | 0 | `unreviewed` |
| sensitivity_cases | `needs_supervisor` | `uncertain` | 0 | `unreviewed` |

## Recommendation

Send only unresolved verifier fields to paid supervisor audit: aac_value, base_case_harvest_forecast, decision_rationale, document_title, inventory_reference_year, major_land_base_constraints, major_management_assumptions, sensitivity_cases
