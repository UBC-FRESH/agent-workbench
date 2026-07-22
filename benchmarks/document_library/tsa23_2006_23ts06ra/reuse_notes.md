# P108.3: P89/P91/P107 Reuse Notes for tsa23_2006_23ts06ra

## P89 Validation Input Manifest Compatibility

**Schema:** `benchmarks/document_library/p89_validation_input_manifest.json`

The P89 manifest uses a `candidate_inputs` array where each entry has:
- `ticket_id`: string identifier for the validation ticket
- `candidate_input_path`: runtime path to the JSONL candidate file
- `expected_initial_state`: placeholder state descriptor
- `record_pass`: pass type ("structure", "content_metadata", etc.)

**Compatibility:** The new document `tsa23_2006_23ts06ra` can be accommodated by adding
new entries to the `candidate_inputs` array with ticket IDs following the pattern:
`p89_tsa23-2006-23ts06ra-pages-001-008-p001-s01_structure` etc.

No schema modification is required. The P89 manifest is append-only for new documents.

**Gaps:**
- The existing P89 manifest currently only contains entries for `tsa23-2012-23tsdp12`.
- A new section or updated `candidate_input_count` will be needed when P109 generates
  validation inputs for this document.

## P91 Audit Schema Compatibility

**Schema:** `benchmarks/document_library/p91_source_audit_decision_packet.json`

The P91 audit packet uses a fixed schema with:
- `packet_id`, `phase`, `decision`, `schema_version`
- `quality_outcome` with accepted/rejected/repairable counts
- `protocol_outcome` with defect class counts
- `economics_governance_outcome`
- `public_safety` flags

**Compatibility:** The P91 schema is a per-audit decision packet, not a per-document registry.
Each audit run produces one packet. A P109 audit of `tsa23_2006_23ts06ra` should produce
a new packet with `packet_id: "p109_tsa23_2006_23ts06ra_audit"` and `phase: "P109"`.

No schema modification is required.

**Gaps:**
- The P91 packet references `reporting_worker_draft_path` and `supervisor_authority_path`
  which will need new values for P109.
- The `public_safety` flags should be verified again for the 2006 rationale document type.

## P107 Economics Contract Compatibility

The P107 economics research program established:
- Per-task budget gates ($0.125 threshold for pilot slices)
- Token cost accounting models
- One-run/one-repair delegation economics

**Compatibility:** The budget gate computed in `budget_gate.json` for this document
uses the same token-rate model and $0.125 threshold from P107.

**Gaps:**
- The P107 economics were computed against gpt-4-mini rates. P109 should use
  gpt-5.6-luna rates from `model_profiles/pricing_catalog.json`.
- The $0.125 threshold was set for 8-page slices. This document is exactly 8 pages,
  so the threshold applies directly.

## Summary

All three existing contracts (P89, P91, P107) can accommodate the new document without
schema modification. The document just needs new entries meeting the same schema patterns.
No changes to the registry, P89 manifest, P91 schema, or P107 contracts are required.

**Note:** The manifest is currently single-chunk for P108's scope. P109 or later may
refine chunk granularity. The raw text slice remains under `runtime/` (ignored);
the tracked `chunk_manifest.json` references it via `runtime_text_path`.