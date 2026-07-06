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

## Token And Cost Lines

| Lane | Fresh Input | Cached Input | Output | Reasoning Output | Worker Input | Worker Output | Cash Cost USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| supervisor `ticket_build` | 15038 | 1298176 | 6364 | 1431 | 0 | 0 | 0.362627 |
| supervisor `worker_run_orchestration` | 984 | 270080 | 219 | 0 | 0 | 0 | 0.052052 |
| local worker | 0 | 0 | 0 | 0 | 15432 | 10886 | 0.000000 |
| supervisor total | 16022 | 1568256 | 6583 | 1431 | 0 | 0 | 0.414679 |

## Outcome

- quality_validated_candidate: `False`
- protocol_accepted_candidate: `False`
- economics_usable: `False`
- final_decision: `stop_after_single_attempt_model_call_failure`
- rejection_reasons: `invalid_chunk_id, malformed_or_truncated_jsonl, model-call-failure, provider_524_model_call_failure`
- maintainer_checkpoint_required: `True`

## Interpretation

The single allowed live attempt produced partial parseable JSONL but did not complete cleanly. Because the attempt hit a model-call failure and produced protocol-noisy fenced output with an invalid chunk ID, P63 must stop at the maintainer checkpoint before any retry, repair expansion, broader slice, or model-lane change.
