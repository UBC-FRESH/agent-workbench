# Phase 55 TSA23 Indexing Battery

P55 is not a quick closeout phase. It is the first real multi-run
document-indexing experiment over the TSA23 corpus prepared in P53. The phase
should stay open until the maintainer decides that enough evidence has been
collected.

## Why This Needs A Battery

P53 proved reproducible corpus materialization, not indexing performance. A
single worker run would be too easy to misread. The useful question is how
document-library delegation behaves across:

- more than one document;
- more than one chunk size;
- more than one local model;
- at least one repeatability check; and
- at least one measured supervisor audit slice.

The tracked battery definition is
`benchmarks/document_library/tsa23_tsr/p55_test_battery.json`.

Generated extraction tickets must not impose a hidden maximum record count.
Output verbosity, malformed JSONL, repetitive records, quote-length defects,
and low-value filler are validator/audit outcomes to measure, not invisible
ticket-generation guardrails that distort coverage.

## Test Documents

Use the three most recent public TSA23 TSR documents from the P53 corpus:

- `tsa23_2012_23tsdp12`: most recent data package;
- `tsa23_2012_23ts13pdp`: most recent public discussion paper;
- `tsa23_2012_23ts13ra`: most recent rationale.

This gives us the most relevant and most text-extraction-friendly slice before
touching older documents that are more likely to require OCR or special
handling. The 1995 rationale remains useful as a later extractor/OCR test lane,
but it should not dominate the first local-worker indexing signal.

## Model Lanes

Initial local-worker model lanes:

- `qwen3.6:35b-a3b-bf16`: primary document-understanding extractor candidate;
- `qwen3-coder-next:latest`: primary extractor candidate;
- `qwen3-coder:latest`: within-family baseline;
- `gpt-oss:120b`: large local comparison candidate.

Model identity must be recorded from runtime/eval evidence. A configured model
name alone is not enough.

## Battery Waves

### Wave 0: Materialization And Chunking

Extract page-window text chunks for the three selected PDFs into ignored
runtime storage and write sanitized tracked chunk manifests.

Stop gate: do not contact worker models until manifests validate and no raw text
is tracked.

### Wave 1: Single-Model Smoke

Run `qwen3-coder-next:latest` on `structure_x2` for each selected document.

Stop gate: continue only if outputs are parseable and preserve required
document/record IDs.

### Wave 1.1: Full-Document Single-Model Smoke

Run `qwen3-coder-next:latest` on `structure_full` for each selected document so
the first indexing signal covers the full extracted page range instead of only
the opening chunks.

Stop gate: continue only if full-document outputs remain parseable and do not
show worse looping or format drift than Wave 1.

### Wave 2: Model A/B

Run `qwen3-coder:latest`, `qwen3-coder-next:latest`, and `gpt-oss:120b` on
identical `structure_x4` tickets for one document.

Stop gate: continue only if at least one model produces source-anchored
parseable records without looping or tool confounds.

### Wave 3: Size Scale

Run `qwen3-coder:latest`, the best Wave 2 coverage candidate, on
`structure_x2`, `structure_x4`, and `structure_x8` for one document.

Stop gate: compare marginal record yield, malformed-output risk, and worker
token growth before scaling further.

### Wave 3.1: Chunk-Orchestrated Coverage

Run `qwen3-coder:latest` once per rationale chunk so coverage is deterministic
rather than dependent on one broad ticket reaching later chunks.

Stop gate: continue only if every chunk returns parseable records with valid
chunk IDs and repairable quote-length defects.

### Wave 3.2: Qwen3.6 BF16 Chunk A/B

Run `qwen3.6:35b-a3b-bf16` once per rationale chunk on the same seven chunk
inputs used by Wave 3.1, then compare document-understanding extraction
behavior against the `qwen3-coder:latest` baseline.

Stop gate: continue only if BF16 outputs are parseable and improve or clearly
characterize chunk-ID fidelity, quote discipline, and repair burden relative to
Wave 3.1.

### Wave 4: Repeatability

Repeat the best current Wave 3 cell, `qwen3-coder:latest` on `structure_x4`,
three times to measure within-model consistency.

Stop gate: continue only if record counts, ID preservation, and parseability are
stable enough for supervisor audit.

### Wave 5: Content Metadata Probe

Run one `content_x4` ticket after structure extraction succeeds.

Stop gate: do not scale content metadata if source quotes, page anchors, or
claim specificity are weak.

### Wave 6: Supervisor Audit Calibration

Supervisor audits a stratified sample of records with token checkpoints.

Stop gate: do not claim economics unless supervisor-token spans and worker token
records are present.

## Minimum Useful Battery

Minimum useful evidence before considering phase closeout:

- at least 6 worker runs;
- all 3 pilot documents touched;
- at least 2 model lanes touched;
- at least one supervisor audit calibration slice;
- missing evidence recorded explicitly.

The full battery is 33 planned worker runs plus supervisor audit calibration.

## Workflow Pivot

P55 should move away from one generic "structure metadata" pass as the main
indexing workflow. The next design target is a document-intelligence pipeline:

1. section-map extraction for headings, page spans, tables, appendices, and
   acronym/definition zones;
2. typed TSR fact extraction for AAC, THLB/land-base, inventory,
   growth/yield, management assumptions, harvest flow, sensitivity/scenario,
   and non-timber constraints;
3. repair/normalization for chunk IDs, quote length, units, and schema shape;
4. verification against page/quote evidence before paid supervisor audit.

## Metrics

Each worker run should record:

- worker status;
- model identity;
- ticket shape;
- document ID;
- chunk count;
- input and output token counts when available;
- parseable JSONL record count;
- malformed record count;
- record ID preservation rate;
- source anchor and source quote presence;
- loop or tool confounds;
- supervisor accepted, repairable, and rejected counts when audited;
- supervisor token cost when audited.

## Pause Policy

Do not close P55 after the first successful run. Report each wave result to the
maintainer and wait for direction before moving to the next wave or closeout.
