# Phase 89 Document-Indexing Recipe V2

## Purpose

P89 repairs the document-indexing recipe shape before any new live worker call.
The phase now consumes the full selected TSA23 data package document so the next
live gate can aim at one complete useful unit of work rather than another
partial-slice diagnostic.

## Full-Document Scope

P89 uses `benchmarks/document_library/p88_selected_corpus_slice.json` as the
source of truth. P89.0 amended that record to select
`p88_tsa23_2012_data_package_full_document_pages_001_041`:

- document: `tsa23_2012_23tsdp12`;
- page span: pages 1-41;
- selected chunks: all six tracked chunks in
  `benchmarks/document_library/tsa23_tsr/chunk_manifests/tsa23_2012_23tsdp12.json`;
- tracked text character count: 106,859; and
- raw text policy: raw extracted text and rendered worker tickets remain under
  ignored `runtime/`.

This expands from the original three-chunk P63 repeat slice, but it does not
expand to a second document or the full TSA23 corpus.

## Recipe V2 Shape

The P89 materializer is
`scripts/build_p89_document_indexing_recipe_v2.py`.

It has two deterministic commands:

- `materialize`: reads the selected slice, verifies ignored runtime chunk text
  against tracked hashes, deduplicates overlapping chunk pages, splits the full
  document into smaller section-level tickets, writes raw-text tickets and empty
  candidate JSONL placeholders under ignored `runtime/`, and writes sanitized
  tracked manifests.
- `validate-jsonl`: validates candidate JSONL against the generated contract and
  applies only safe mechanical repairs: strip Markdown fences, drop non-JSON
  preamble/trailing prose, trim whitespace, and remove one trailing comma before
  a JSON object close.

The materialized full-document packet contains:

- 60 unique page/section units;
- two record passes per section: `structure` and `content_metadata`;
- 120 ignored runtime worker tickets;
- 120 ignored empty candidate JSONL placeholders;
- one explicit six-value chunk-ID enum; and
- one deterministic JSONL validation contract.

## Tracked Artifacts

P89 tracks only sanitized metadata:

- `benchmarks/document_library/p89_chunk_id_enum.json`;
- `benchmarks/document_library/p89_jsonl_validation_contract.json`;
- `benchmarks/document_library/p89_validation_input_manifest.json`;
- `benchmarks/document_library/p89_recipe_v2_materialization_manifest.json`; and
- `benchmarks/document_library/p89_dry_run_materialization_summary.json`.

These artifacts contain chunk IDs, page ranges, synthetic section labels,
hashes, runtime paths, counts, and policy flags. They do not contain raw source
text, source section titles, raw worker outputs, provider headers, provider
URLs, credentials, or personal paths.

## P90 Handoff

P90 should use the P89 validation contract and empty candidate placeholders as
the source-anchored repair/audit design surface. P90 should not run a live
model by default. If a live gate is later approved, the live run must name one
model/provider lane, preserve a hard budget/attempt boundary, and produce
candidate records that can be validated by the P89 contract before supervisor
audit.

The immediate product target is no longer "prove the toy slice can be
processed." It is "produce one complete source-backed index candidate for one
public technical document, then audit whether that candidate is worth scaling."
