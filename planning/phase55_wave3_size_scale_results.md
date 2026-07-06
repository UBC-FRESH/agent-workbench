# Phase 55 Wave 3 Size-Scale Results

Wave 3 ran `qwen3-coder:latest`, the best Wave 2 coverage candidate, on
`structure_x2`, `structure_x4`, and `structure_x8` tickets for the 2012 TSA23
rationale.

Raw worker outputs remain ignored under
`runtime/document_library/tsa23_tsr/p55/eval/`.

Tracked aggregate metrics are in
`benchmarks/document_library/tsa23_tsr/p55_wave3_size_scale_summary.json`.

## Framework Fix Before Run

Before running Wave 3, the ticket framework was tightened again:

- removed the literal model name from the example output;
- added an explicit allowed `chunk_id` list to generated tickets;
- switched Wave 3 from `qwen3-coder-next:latest` to `qwen3-coder:latest` based
  on the Wave 2 coverage result.

## Result

| Shape | Requested Chunks | Covered Chunks | JSON Records | Duplicate IDs | Invalid Chunk IDs | Worker-Model Matches | Quote-Length Violations | Input Tokens | Output Tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `structure_x2` | 2 | 2 | 24 | 0 | 0 | 24 | 3 | 13,422 | 6,418 |
| `structure_x4` | 4 | 4 | 24 | 0 | 0 | 24 | 23 | 26,763 | 7,382 |
| `structure_x8` | 7 | 4 | 24 | 0 | 0 | 24 | 23 | 39,896 | 7,705 |

## Interpretation

The framework fix worked on the two defects it targeted. All Wave 3 outputs
used valid chunk IDs and correctly populated `worker_model` with
`qwen3-coder:latest`.

The size-scale result is not monotonic in useful coverage. All three runs hit
the 24-record cap. `structure_x4` covered all four requested chunks and looks
like the best current ticket size. `structure_x8` consumed substantially more
input than `structure_x4` but still covered only four of seven chunks, so the
extra context did not translate into full-document coverage.

The remaining systematic defect is quote length. The model still tends to
include long source quotes even when asked for short quotes.

## Recommendation

Do not scale by making larger single tickets. Use `structure_x4` or smaller
bundles as the current default, then add either:

- per-chunk quotas so every chunk receives coverage before the record cap is
  exhausted; or
- deterministic per-chunk orchestration plus delegated normalization/repair.

Wave 4 repeatability should use `structure_x4` with `qwen3-coder:latest`, not
the old `qwen3-coder-next:latest` plan.
