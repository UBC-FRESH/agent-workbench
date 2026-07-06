# Phase 63 Bounded TSA23 Recipe Pilot Execution Results

Raw worker records, source quotes, prompts, provider details, and transcripts remain ignored.

## Attempt Status

- model: `qwen3.6:35b-a3b-q8_0`
- harness_status: `blocked`
- harness_blocker: `model-call-failure`
- harness_classification: `model-call-failure`
- observed_error_kinds: `provider_524_model_call_failure`
- fenced_output_detected: `True`
- preamble_detected: `True`

## Candidate Metrics

- parseable_json_records: `40`
- malformed_lines: `2`
- valid_chunk_records: `39`
- invalid_chunk_id_records: `1`
- missing_chunks: `none`
- source_quote_over_target_records: `0`
- source_quote_max_words: `24`

## Fact Review Counts

- accepted: `0`
- repaired: `0`
- rejected: `1`
- escalated: `0`
- unresolved: `39`
- basis: No source audit or repair pass was run after the single-attempt stop rule. Valid raw records remain unresolved; invalid chunk-ID records are rejected by deterministic validation.

## Token And Cost Lines

| Lane | Fresh Input | Cached Input | Output | Reasoning Output | Worker Input | Worker Output | Cash Cost USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| supervisor `ticket_build` | 15038 | 1298176 | 6364 | 1431 | 0 | 0 | 0.362627 |
| supervisor `worker_run_orchestration` | 984 | 270080 | 219 | 0 | 0 | 0 | 0.052052 |
| supervisor `worker_output_summarize` | 7129 | 603776 | 2079 | 749 | 0 | 0 | 0.157729 |
| supervisor `tracked_update` | 9459 | 1053568 | 2226 | 530 | 0 | 0 | 0.239512 |
| local worker | 0 | 0 | 0 | 0 | 15432 | 10886 | 0.000000 |
| supervisor total | 32610 | 3225600 | 10888 | 2710 | 0 | 0 | 0.811920 |

## Outcome

- quality_validated_candidate: `False`
- protocol_accepted_candidate: `False`
- economics_usable: `False`
- final_decision: `stop_after_single_attempt_model_call_failure`
- rejection_reasons: `invalid_chunk_id, malformed_or_truncated_jsonl, model-call-failure, provider_524_model_call_failure`
- maintainer_checkpoint_required: `True`

## Baseline Comparison

- direct_supervisor_baseline_status: `not_run_stop_rule_triggered`
- comparison_decision: `not_comparable`
- reason: P63.2 produced diagnostic evidence rather than an accepted delegated candidate. Running a direct-supervisor baseline now would answer a different question and spend additional paid tokens after the declared maintainer checkpoint.

## Interpretation

The single allowed live attempt produced partial parseable JSONL but did not complete cleanly. Because the attempt hit a model-call failure and produced protocol-noisy fenced output with an invalid chunk ID, P63 must stop at the maintainer checkpoint before any retry, repair expansion, broader slice, or model-lane change.
