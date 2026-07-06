# Phase 55 Wave 10 Quote Repair Economics

- generated_utc: `2026-07-05T09:16:58Z`
- baseline_gate_result: `wave8-quote-repair-needed`
- repair_gate_result: `wave10-quote-limit-failed`

## Line Items

| Lane | Node | Owner | Model | Worker Input | Worker Output | Worker Cost | Quality |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| baseline_two_pass | `wave7_candidate_generation` | `local_ollama` | `qwen3.6:35b-a3b-bf16, gpt-oss:120b` | 28894 | 7551 | $0.000000 | `{"candidate_count": 2, "fields": 15, "invalid_chunk_id_fields": 0, "needs_supervisor_fields": 0, "quote_over_limit_fields": 2}` |
| baseline_two_pass | `wave8_disagreement_verification` | `local_ollama` | `qwen3.6:35b-a3b-bf16` | 17030 | 4619 | $0.000000 | `{"invalid_chunk_id_fields": 0, "needs_supervisor_fields": 1, "quote_over_limit_fields": 1, "resolved_fields": 6}` |
| baseline_two_pass | `paid_supervisor_audit` | `paid_supervisor` | `codex` | 0 | 0 | $0.000000 | `{"needs_supervisor_fields": 1, "required_measurement": "wrap actual supervisor audit with supervisor-token checkpoints", "token_cost_status": "not_measured_in_this_worker_trial"}` |
| repair_prepass_trial | `wave7_candidate_generation_reused` | `local_ollama` | `qwen3.6:35b-a3b-bf16, gpt-oss:120b` | 28894 | 7551 | $0.000000 | `{"candidate_count": 2, "fields": 15, "invalid_chunk_id_fields": 0, "needs_supervisor_fields": 0, "quote_over_limit_fields": 2}` |
| repair_prepass_trial | `wave10_quote_repair_prepass` | `local_ollama` | `qwen3-coder-next:latest` | 15224 | 949 | $0.000000 | `{"invalid_chunk_id_fields": 0, "needs_supervisor_fields": 1, "needs_verifier_fields": 0, "quote_over_limit_fields": 1, "repaired_or_unchanged_fields": 3, "target_fields": 4}` |
| repair_prepass_trial | `post_repair_verifier` | `not_run` | `not_run` | 0 | 0 | $0.000000 | `{"note": "Run required before claiming full three-pass workflow economics.", "status": "not_run"}` |
| repair_prepass_trial | `paid_supervisor_audit` | `paid_supervisor` | `codex` | 0 | 0 | $0.000000 | `{"needs_supervisor_fields": 1, "required_measurement": "wrap actual supervisor audit with supervisor-token checkpoints", "token_cost_status": "not_measured_in_this_worker_trial"}` |

## Totals

### baseline_two_pass

- worker_input_tokens: `45924`
- worker_output_tokens: `12170`
- worker_cash_cost_usd: `0.0`

### repair_prepass_trial

- worker_input_tokens: `44118`
- worker_output_tokens: `8500`
- worker_cash_cost_usd: `0.0`

### delta_repair_minus_baseline

- worker_input_tokens: `-1806`
- worker_output_tokens: `-3670`
- worker_cash_cost_usd: `0.0`

## Interpretation

Repair prepass is not ready for post-repair verification; inspect gate result before scaling.
