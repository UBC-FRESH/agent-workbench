# Phase 55 Wave 2 Model A/B Results

Wave 2 ran one identical `structure_x4` ticket for
`tsa23_2012_23ts13ra` across three local Ollama model lanes:

- `qwen3-coder:latest`;
- `qwen3-coder-next:latest`;
- `gpt-oss:120b`.

Raw worker outputs remain ignored under
`runtime/document_library/tsa23_tsr/p55/eval/`.

Tracked aggregate metrics are in
`benchmarks/document_library/tsa23_tsr/p55_wave2_model_ab_summary.json`.

## Ticket Coverage

The A/B ticket included four rationale chunks:

- `tsa23_2012_23ts13ra::pages_001_008`;
- `tsa23_2012_23ts13ra::pages_008_015`;
- `tsa23_2012_23ts13ra::pages_015_022`;
- `tsa23_2012_23ts13ra::pages_022_029`.

## Result

| Model | Status | JSON Records | Duplicate IDs | Invalid Chunk IDs | Worker-Model Field Matches | Quote-Length Violations | Input Tokens | Output Tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `qwen3-coder:latest` | completed | 24 | 0 | 0 | 0 | 24 | 26,579 | 8,999 |
| `qwen3-coder-next:latest` | completed | 9 | 1 | 0 | 9 | 6 | 26,585 | 2,741 |
| `gpt-oss:120b` | completed | 13 | 0 | 2 | 0 | 0 | 27,094 | 3,451 |

All three models produced parseable JSON records and the eval classifier now
reports `freeform-output` instead of the earlier misleading `duplicate-marker`.

## Interpretation

`qwen3-coder:latest` produced the best coverage signal: 24 records across all
four chunks with no duplicate record IDs and no invalid chunk IDs. Its defects
are systematic and likely repairable: it copied the example `worker_model`
value and ignored the 25-word source-quote limit.

`qwen3-coder-next:latest` was cleaner on self-identification, but it under-
covered the ticket badly: all nine records came from the first chunk, and one
record ID was duplicated.

`gpt-oss:120b` was concise and obeyed source-quote length better, but it
invented two chunk IDs and copied the example `worker_model` value. That makes
it risky as an extractor without a stricter allowed-chunk validator.

## Recommendation

Do not scale Wave 2 unchanged. The next framework fix should remove the
literal model value from the example and provide an explicit allowed `chunk_id`
list that the validator can check. For Wave 3 size-scale testing, the best
coverage candidate is currently `qwen3-coder:latest`, but it needs deterministic
validation/repair before paid supervisor audit.
