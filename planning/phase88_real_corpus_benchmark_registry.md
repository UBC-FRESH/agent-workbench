# Phase 88: Real-Corpus Benchmark Registry

Phase 88 selects the first bounded real corpus slice for the P87-P92
real-project ROI tranche. It is a planning and registry phase only.

## Decision

P88 selects `p88_tsa23_2012_data_package_pages_001_022` for P89-P92 follow-on
work.

The selected slice is the 2012 100 Mile House TSA data package
`tsa23_2012_23tsdp12`, pages 1-22, represented by three tracked chunk records:

- `tsa23_2012_23tsdp12::pages_001_008`;
- `tsa23_2012_23tsdp12::pages_008_015`; and
- `tsa23_2012_23tsdp12::pages_015_022`.

This keeps the P63 source scope stable while changing the execution shape in
P89. The next repeat should test smaller section-level tickets, explicit
chunk-ID enums, deterministic JSONL validation, and deterministic repair before
any live worker call.

## Candidate Registry

Tracked registry artifacts:

- `benchmarks/document_library/p88_candidate_corpus_registry.json`;
- `benchmarks/document_library/p88_selected_corpus_slice.json`;
- `benchmarks/document_library/tsa23_tsr/corpus_registry.json`; and
- `benchmarks/document_library/tsa23_tsr/chunk_manifests/tsa23_2012_23tsdp12.json`.

P88 compared four candidates:

1. the P63 repeat slice, selected for P89-P92;
2. the full 2012 TSA23 cycle mini-corpus, deferred until recipe v2 works on the
   repeat slice;
3. the full 1995-present TSA23 corpus registry, deferred until scale and
   index-usability phases; and
4. an MP11-style repair-prepass seed, retained as design pressure but not
   selected because it is not represented as a complete tracked Agent Workbench
   corpus registry.

## Selection Rationale

The selected P63 repeat slice is the best next corpus unit because it has:

- tracked source provenance and chunk metadata;
- known P63 diagnostic evidence;
- known failure modes: provider 524, fenced output, malformed JSONL, and one
  invalid chunk ID;
- enough density to test document-indexing recipe v2; and
- a bounded scope small enough for a strict one-attempt future live gate.

The selected scope is deliberately not the full 2012 cycle or full TSA23
registry. Those would create scale noise before P89 repairs the recipe shape.

## Budget Boundary

P88 does not authorize live model execution.

P89 also remains dry-run/materialization only. The first possible live phase is
P92, and only after P89-P91 gates have produced:

- recipe-v2 dry-run manifests;
- section-level worker tickets;
- an explicit chunk-ID enum;
- deterministic JSONL validation and repair paths;
- a source-anchored repair/audit packet;
- a reporting-worker decision packet;
- a new or amended budget declaration; and
- one named model/provider lane.

The default maximum live attempts remains one. A second attempt, broader page
span, added model lane, direct-supervisor baseline, or budget increase requires
maintainer approval.

No direct-supervisor baseline is allowed until a quality-valid delegated
candidate exists.

## P89 Handoff

P89 should consume `benchmarks/document_library/p88_selected_corpus_slice.json`
as the source-of-truth scope.

P89 must not widen the document scope. Its job is to repair the execution
shape:

- section-level tickets rather than the P63 all-in-one shape;
- explicit chunk-ID enum validation;
- deterministic JSONL validation;
- deterministic repair where possible; and
- public-safe dry-run materialization.

P89 closeout should leave P90 with candidate validation/repair artifacts ready
for source-anchored repair and audit design.

## Public-Safety Boundary

P88 tracks metadata only. Raw PDFs, raw chunk text, prompts, worker outputs,
provider URLs, headers, credentials, and personal paths remain out of tracked
files.
