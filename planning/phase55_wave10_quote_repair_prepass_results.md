# Phase 55 Wave 10 Quote Repair Results

Raw repair values and source quotes remain ignored under runtime paths.

- generated_utc: `2026-07-05T09:16:54Z`
- gate_result: `wave10-quote-limit-failed`
- repair_model: `qwen3-coder-next:latest`
- parse_status: `parsed`

## Aggregate Totals

- action_counts: `{"needs_supervisor": 1, "repaired": 2, "unchanged": 1}`
- repaired_or_unchanged_fields: `3`
- needs_verifier_fields: `0`
- needs_supervisor_fields: `1`
- invalid_action_fields: `0`
- quote_over_limit_fields: `1`
- invalid_chunk_id_fields: `0`
- worker_input_tokens: `15224`
- worker_output_tokens: `949`
- worker_cash_cost_usd: `0.0`

## Field Repairs

| Field | Action | Status | Quote Words | Reason Code |
| --- | --- | --- | ---: | --- |
| aac_value | `repaired` | `found` | 17 | `left_correct` |
| base_case_harvest_forecast | `repaired` | `found` | 32 | `left_correct` |
| decision_rationale | `needs_supervisor` | `uncertain` | 0 | `out_of_range` |
| inventory_reference_year | `unchanged` | `found` | 11 | `right_correct` |

## Recommendation

Keep these fields in supervisor lane: decision_rationale
