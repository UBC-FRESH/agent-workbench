# Phase 55 Codex vs Copilot Supervisor A/B

- generated_utc: `2026-07-05T18:33:18Z`
- benchmark_scope: Seven-field Wave 8 adjudication supervisor task over tsa23_2012_23ts13ra.
- quote_word_limit: `25`
- raw_output_policy: Raw supervisor outputs remain ignored under runtime/; tracked summary stores hashes, counts, model evidence, and defect classes only.

## Bridge Evidence

- bridge_report_path: `runtime/agent_jobs/p55_ab_large_copilot_supervisor_bridge_report_v2.md`
- status: `accepted-candidate`
- resolved_model: `qwen3.6:35b-a3b-bf16`
- permission_levels: `autopilot`
- completed: `true`
- final_marker_present: `true`
- numeric_token_status: `unavailable_from_vscode_chat_session`
- supervisor_token_price_per_1m_usd: `0.0`
- supervisor_cash_cost_usd: `0.0`

## Lane Quality

| Lane | Model | Score | Hard Penalty | Soft Penalty | Clean Fields | Needs Supervisor | Quote Defects | Status/Value Defects |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| codex_supervisor_direct | `codex-supervisor` | 85.00 | 0.00 | 15.00 | 6 | 1 | 0 | 0 |
| copilot_free_supervisor | `qwen3.6:35b-a3b-bf16` | 87.31 | 0.00 | 12.69 | 5 | 0 | 2 | 0 |

## Scoring Rubric

- max_score: `100.0`
- quote_word_target: `25`
- quote_penalty: `weight * (exp((words - target) / scale) - 1)` for words over target
- quote_penalty_scale: `10.0`

| Penalty Term | Weight |
| --- | ---: |
| `extra_field` | 40.0 |
| `found_null_value` | 120.0 |
| `invalid_action` | 100.0 |
| `invalid_chunk_id` | 80.0 |
| `low_confidence_repaired` | 10.0 |
| `missing_chunk_id_on_found` | 30.0 |
| `missing_quote_on_found` | 20.0 |
| `missing_required_field` | 200.0 |
| `needs_supervisor` | 15.0 |
| `quote_excess` | 1.0 |
| `value_type_mismatch` | 120.0 |

## Field-Level Quality

| Lane | Field | Action | Status | Value Type | Quote Words | Defects |
| --- | --- | --- | --- | --- | ---: | --- |
| codex_supervisor_direct | `aac_value` | `repaired` | `found` | `list` | 17 | `none` |
| codex_supervisor_direct | `base_case_harvest_forecast` | `repaired` | `found` | `dict` | 19 | `none` |
| codex_supervisor_direct | `decision_rationale` | `needs_supervisor` | `uncertain` | `null` | 0 | `none` |
| codex_supervisor_direct | `document_title` | `unchanged` | `found` | `str` | 13 | `none` |
| codex_supervisor_direct | `inventory_reference_year` | `repaired` | `found` | `int` | 11 | `none` |
| codex_supervisor_direct | `major_land_base_constraints` | `unchanged` | `found` | `list` | 16 | `none` |
| codex_supervisor_direct | `major_management_assumptions` | `unchanged` | `found` | `list` | 10 | `none` |
| copilot_free_supervisor | `aac_value` | `repaired` | `found` | `list` | 34 | `quote_over_limit` |
| copilot_free_supervisor | `base_case_harvest_forecast` | `repaired` | `found` | `dict` | 33 | `quote_over_limit` |
| copilot_free_supervisor | `decision_rationale` | `unchanged` | `uncertain` | `null` | 17 | `none` |
| copilot_free_supervisor | `document_title` | `repaired` | `found` | `str` | 11 | `none` |
| copilot_free_supervisor | `inventory_reference_year` | `repaired` | `found` | `int` | 11 | `none` |
| copilot_free_supervisor | `major_land_base_constraints` | `repaired` | `found` | `list` | 18 | `none` |
| copilot_free_supervisor | `major_management_assumptions` | `repaired` | `found` | `list` | 21 | `none` |

## Field-Level Penalties

| Lane | Field | Hard Penalty | Soft Penalty | Total Penalty | Terms |
| --- | --- | ---: | ---: | ---: | --- |
| codex_supervisor_direct | `aac_value` | 0.00 | 0.00 | 0.00 | `{}` |
| codex_supervisor_direct | `base_case_harvest_forecast` | 0.00 | 0.00 | 0.00 | `{}` |
| codex_supervisor_direct | `decision_rationale` | 0.00 | 15.00 | 15.00 | `{"needs_supervisor": 15.0}` |
| codex_supervisor_direct | `document_title` | 0.00 | 0.00 | 0.00 | `{}` |
| codex_supervisor_direct | `inventory_reference_year` | 0.00 | 0.00 | 0.00 | `{}` |
| codex_supervisor_direct | `major_land_base_constraints` | 0.00 | 0.00 | 0.00 | `{}` |
| codex_supervisor_direct | `major_management_assumptions` | 0.00 | 0.00 | 0.00 | `{}` |
| copilot_free_supervisor | `aac_value` | 0.00 | 1.46 | 1.46 | `{"quote_excess": 1.459603}` |
| copilot_free_supervisor | `base_case_harvest_forecast` | 0.00 | 1.23 | 1.23 | `{"quote_excess": 1.225541}` |
| copilot_free_supervisor | `decision_rationale` | 0.00 | 10.00 | 10.00 | `{"low_confidence_repaired": 10.0}` |
| copilot_free_supervisor | `document_title` | 0.00 | 0.00 | 0.00 | `{}` |
| copilot_free_supervisor | `inventory_reference_year` | 0.00 | 0.00 | 0.00 | `{}` |
| copilot_free_supervisor | `major_land_base_constraints` | 0.00 | 0.00 | 0.00 | `{}` |
| copilot_free_supervisor | `major_management_assumptions` | 0.00 | 0.00 | 0.00 | `{}` |

## Supervisor Token/Cost Line Items

| Span | Kind | Fresh Input | Cached Input | Output | Reasoning Output | Cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `p55-large-ab-codex-adjudication` | `codex_supervisor_adjudication` | 1875 | 373504 | 1742 | 119 | $0.094698 |
| `p55-large-ab-copilot-delegation-v2` | `copilot_supervisor_delegation_v2` | 2079 | 416512 | 300 | 0 | $0.080728 |
| `p55-large-ab-copilot-delegation` | `copilot_supervisor_delegation_failed` | 4967 | 757248 | 1293 | 94 | $0.160629 |
| `p55-large-ab-result-audit-and-summary` | `result_audit_and_summary` | 1970 | 424704 | 563 | 0 | $0.085653 |

## Cost Delta

- shared_setup_codex_supervisor_cost_usd: `$0.000000`
- codex_direct_paid_supervisor_cost_usd: `$0.094698`
- copilot_lane_paid_codex_delegation_cost_usd: `$0.080728`
- copilot_lane_failed_retry_paid_codex_cost_usd: `$0.160629`
- copilot_lane_paid_codex_delegation_cost_usd_including_retries: `$0.241357`
- copilot_lane_local_supervisor_cost_usd: `$0.000000`
- copilot_lane_total_cash_cost_usd_excluding_shared_setup: `$0.080728`
- copilot_lane_total_cash_cost_usd_including_retries_excluding_shared_setup: `$0.241357`
- codex_lane_total_cash_cost_usd_excluding_shared_setup: `$0.094698`
- copilot_minus_codex_cash_delta_usd_excluding_shared_setup: `$-0.013971`
- copilot_minus_codex_cash_delta_including_retries_usd_excluding_shared_setup: `$0.146658`
- codex_clean_repaired_or_unchanged_fields: `6`
- copilot_clean_repaired_or_unchanged_fields: `5`
- codex_needs_supervisor_fields: `1`
- copilot_needs_supervisor_fields: `0`
- codex_quote_over_limit_fields: `0`
- copilot_quote_over_limit_fields: `2`
- codex_status_value_inconsistency_fields: `0`
- copilot_status_value_inconsistency_fields: `0`

## Interpretation

Scoped Copilot supervisor followed the process but did not meet repair-quality criteria. This supports tighter role prompts and/or a separate local audit node before allowing free-supervisor output to replace paid supervision.
