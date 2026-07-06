# Phase 55 Codex vs Copilot Supervisor A/B

- generated_utc: `2026-07-06T00:24:57Z`
- benchmark_scope: Four-field Wave 10 quote/value repair supervisor task over tsa23_2012_23ts13ra.
- quote_word_limit: `25`
- raw_output_policy: Raw supervisor outputs remain ignored under runtime/; tracked summary stores hashes, counts, model evidence, and defect classes only.

## Bridge Evidence

- bridge_report_path: `runtime/agent_jobs/p55_ab_copilot_supervisor_repair_retry_bridge_report.md`
- status: `accepted-candidate`
- resolved_model: `qwen3.6:35b-a3b-bf16`
- permission_levels: `autopilot`
- completed: `true`
- final_marker_present: `true`
- numeric_token_status: `unavailable_from_vscode_chat_session`
- supervisor_token_price_per_1m_usd: `0.0`
- supervisor_cash_cost_usd: `0.0`

## Lane Quality

| Lane | Reported Model | Authoritative Model | Score | Hard Penalty | Soft Penalty | Clean Fields | Needs Supervisor | Quote Defects | Status/Value Defects |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| codex_supervisor_direct | `codex-supervisor` | `codex-supervisor` | 85.00 | 0.00 | 15.00 | 3 | 1 | 0 | 0 |
| copilot_free_supervisor | `qwen3-coder-next:latest` | `qwen3.6:35b-a3b-bf16` | 58.99 | 0.00 | 41.01 | 2 | 1 | 1 | 0 |

## Model Provenance

| Lane | Reported Model | Observed Model | Authoritative Model | Status | Penalty |
| --- | --- | --- | --- | --- | ---: |
| codex_supervisor_direct | `codex-supervisor` | `` | `codex-supervisor` | `self_reported_only` | 0.00 |
| copilot_free_supervisor | `qwen3-coder-next:latest` | `qwen3.6:35b-a3b-bf16` | `qwen3.6:35b-a3b-bf16` | `mismatch` | 25.00 |

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
| `model_provenance_mismatch` | 25.0 |
| `needs_supervisor` | 15.0 |
| `quote_excess` | 1.0 |
| `value_type_mismatch` | 120.0 |

## Field-Level Quality

| Lane | Field | Action | Status | Value Type | Quote Words | Defects |
| --- | --- | --- | --- | --- | ---: | --- |
| codex_supervisor_direct | `aac_value` | `repaired` | `found` | `list` | 17 | `none` |
| codex_supervisor_direct | `base_case_harvest_forecast` | `repaired` | `found` | `dict` | 19 | `none` |
| codex_supervisor_direct | `decision_rationale` | `needs_supervisor` | `uncertain` | `null` | 0 | `none` |
| codex_supervisor_direct | `inventory_reference_year` | `repaired` | `found` | `int` | 11 | `none` |
| copilot_free_supervisor | `aac_value` | `repaired` | `found` | `list` | 17 | `none` |
| copilot_free_supervisor | `base_case_harvest_forecast` | `repaired` | `found` | `dict` | 32 | `quote_over_limit` |
| copilot_free_supervisor | `decision_rationale` | `needs_supervisor` | `uncertain` | `null` | 13 | `none` |
| copilot_free_supervisor | `inventory_reference_year` | `repaired` | `found` | `int` | 8 | `none` |

## Field-Level Penalties

| Lane | Field | Hard Penalty | Soft Penalty | Total Penalty | Terms |
| --- | --- | ---: | ---: | ---: | --- |
| codex_supervisor_direct | `aac_value` | 0.00 | 0.00 | 0.00 | `{}` |
| codex_supervisor_direct | `base_case_harvest_forecast` | 0.00 | 0.00 | 0.00 | `{}` |
| codex_supervisor_direct | `decision_rationale` | 0.00 | 15.00 | 15.00 | `{"needs_supervisor": 15.0}` |
| codex_supervisor_direct | `inventory_reference_year` | 0.00 | 0.00 | 0.00 | `{}` |
| copilot_free_supervisor | `aac_value` | 0.00 | 0.00 | 0.00 | `{}` |
| copilot_free_supervisor | `base_case_harvest_forecast` | 0.00 | 1.01 | 1.01 | `{"quote_excess": 1.013753}` |
| copilot_free_supervisor | `decision_rationale` | 0.00 | 15.00 | 15.00 | `{"needs_supervisor": 15.0}` |
| copilot_free_supervisor | `inventory_reference_year` | 0.00 | 0.00 | 0.00 | `{}` |

## Supervisor Token/Cost Line Items

| Span | Kind | Fresh Input | Cached Input | Output | Reasoning Output | Cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `p55-ab-codex-supervisor-extraction` | `codex_supervisor_extraction` | 24351 | 385664 | 2553 | 837 | $0.157565 |
| `p55-ab-copilot-supervisor-delegation` | `copilot_supervisor_delegation` | 6487 | 869632 | 3118 | 433 | $0.213252 |
| `p55-ab-result-audit-and-summary` | `result_audit_and_summary` | 1420 | 340736 | 450 | 115 | $0.070024 |
| `p55-ab-setup` | `setup` | 10497 | 108416 | 948 | 662 | $0.059883 |

## Cost Delta

- shared_setup_codex_supervisor_cost_usd: `$0.059883`
- codex_direct_paid_supervisor_cost_usd: `$0.157565`
- copilot_lane_paid_codex_delegation_cost_usd: `$0.213252`
- copilot_lane_failed_retry_paid_codex_cost_usd: `$0.000000`
- copilot_lane_paid_codex_delegation_cost_usd_including_retries: `$0.213252`
- copilot_lane_local_supervisor_cost_usd: `$0.000000`
- copilot_lane_total_cash_cost_usd_excluding_shared_setup: `$0.213252`
- copilot_lane_total_cash_cost_usd_including_retries_excluding_shared_setup: `$0.213252`
- codex_lane_total_cash_cost_usd_excluding_shared_setup: `$0.157565`
- copilot_minus_codex_cash_delta_usd_excluding_shared_setup: `$0.055686`
- copilot_minus_codex_cash_delta_including_retries_usd_excluding_shared_setup: `$0.055686`
- codex_clean_repaired_or_unchanged_fields: `3`
- copilot_clean_repaired_or_unchanged_fields: `2`
- codex_needs_supervisor_fields: `1`
- copilot_needs_supervisor_fields: `1`
- codex_quote_over_limit_fields: `0`
- copilot_quote_over_limit_fields: `1`
- codex_status_value_inconsistency_fields: `0`
- copilot_status_value_inconsistency_fields: `0`

## Interpretation

Scoped Copilot supervisor followed the process, but its self-reported model identity disagreed with bridge evidence. Treat bridge-observed model identity as authoritative before comparing model performance.
