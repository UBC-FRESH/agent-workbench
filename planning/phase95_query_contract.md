# P95.2 — Query Contract Planning Note

**Date:** 2026-07-11  
**Task:** Define query contract for two retrieval use cases scoped to P94 promoted index format  
**Status:** complete (schemas created, planning note written)

---

## Source of Truth: P94 Promoted Index Schema

The P94 promoted index decision packet (`benchmarks/document_library/p94_project_owned_index_decision_packet.json`) establishes the schema contract. Key fields confirmed from 47 promoted records across 3x 2012-cycle documents:

| Field | Type | Present in all 47 records? | Source |
|-------|------|---------------------------|--------|
| `source_hash` | string (SHA-256) | Yes — hash_coverage_percent: 100% | P94 protocol_outcome |
| `document_id` | string | Yes — from chunk manifests | P89/P90 pipeline |
| `page_anchor` | integer | Yes — page_anchors_present: 47 | P94 protocol_outcome |
| `chunk_id` | string | Yes — chunk_anchors_present: 47 | P94 protocol_outcome |
| `model_lane` | string | Yes — all from qwen3.6:35b-a3b-bf16 | P94 quality_outcome |
| `audit_status` | enum | Yes — accepted: 30, accepted_pending_dedup: 17 | P94 quality_outcome |
| `fact_content` | object | Yes — per chunk type (structure vs content_metadata) | P89 extraction pipeline |

Provenance chain fields (from P94 protocol_outcome):
- `phase_extracted`, `run_id`, `report_path`, `promoted_by_phase`, `promotion_utc`

Dedup flags: 17 records flagged as dedup duplicates from the same source chunk (all from `tsa23_2012_23tsdp12`).

---

## Use Case 1: Page/Chunk Anchor Lookup — Schema Decisions

### Input (`use_case_1_page_chunk_anchor_lookup_input.json`)
- **document_id**: Required string. Must match one of the 3x 2012 document IDs in P94. No validation against index at schema level — implementation validates at query time.
- **page_range.start/end**: Required integers, start >= 1, end >= start. Inclusive range. Page numbers are derived from `[PDF page N]` headers in extracted text (chunk format).
- **include_source_hashes / include_model_lane**: Optional booleans, default true. Allows downstream consumers to request minimal records when they already know the model lane or hash.

### Output (`use_case_1_page_chunk_anchor_lookup_output.json`)
- JSON array sorted by `page_anchor` ascending.
- Each record includes: `source_hash`, `document_id`, `page_anchor`, `chunk_id`, `model_lane`, `audit_status`, `fact_content`.
- Dedup-flagged records are included (17 from tsdp12) — filtering to non-dedup is a downstream concern, not part of this query.

### Validation Against P94 Data
- All 3x 2012 documents have page_anchors present: tsa23_2012_23tsdp12 (17 records), tsa23_2012_23ts13ra (16 records), tsa23_2012_23ts13pdp (14 records).
- Page numbers are expected to be small integers (PDF page 1, 2, 3... up to ~41 for the largest document).
- No synthetic test queries written yet — this is P95.3's responsibility.

---

## Use Case 2: Full-Document Provenance Trace — Schema Decisions

### Input (`use_case_2_full_document_provenance_trace_input.json`)
- **document_id**: Required string. Same as use case 1.
- **group_by**: Optional enum [audit_status, model_lane, none]. Default "none".
  - If "none": flat JSON array (same output format as use case 1).
  - If "audit_status" or "model_lane": grouped object keyed by that field's value.

### Output (`use_case_2_full_document_provenance_trace_output.json`)
- Uses `oneOf` to allow either flat_array, grouped_by_audit_status, or grouped_by_model_lane depending on group_by parameter.
- Each record in the array must include provenance chain fields: `phase_extracted`, `run_id`, `report_path`, `promoted_by_phase`, `promotion_utc` (from P94 protocol_outcome).
- Summary metadata included: document_id, total_record_count, group_by value, returned_at timestamp.

### Validation Against P94 Data
- P94 has audit_status values: "accepted" (30), "accepted_pending_dedup" (17) — both are covered by the enum.
- P94 records are all from `qwen3.6:35b-a3b-bf16` model lane — so grouping by model_lane would return a single key in current data, but the schema supports multiple lanes for future use (2006 cycle, q8 variant).
- The 17 dedup-flagged records from tsdp12 have no explicit dedup flag in P94's record schema — the decision packet tracks them separately. **Decision:** add `is_dedup` boolean field to query output for records known to be duplicates, even if not in the raw P94 index. This is a new field for P95, not present in P94.

---

## Schema Differences from P94 (New Fields)

The query schemas introduce one new field not present in P94's promoted index:

| Field | Type | Reason |
|-------|------|--------|
| `is_dedup` | boolean (optional, default false) | Marks records known to be dedup duplicates. P94 tracks this in the decision packet metadata but not at record level. Query output should reflect it for downstream consumers. |

This is intentional — the query layer adds denormalized convenience fields on top of the stable P94 schema contract. Any new field must remain optional and default-friendly so existing consumers don't break.

---

## Files Created

| File | Description |
|------|-------------|
| `templates/query_schemas/use_case_1_page_chunk_anchor_lookup_input.json` | JSON schema for page/chunk lookup input query |
| `templates/query_schemas/use_case_1_page_chunk_anchor_lookup_output.json` | JSON schema for page/chunk lookup output records |
| `templates/query_schemas/use_case_2_full_document_provenance_trace_input.json` | JSON schema for provenance trace input query |
| `templates/query_schemas/use_case_2_full_document_provenance_trace_output.json` | JSON schema for provenance trace output (flat or grouped) |

---

## Next Steps

1. **P95.3** — Implement retrieval functions that:
   - Read the P94 promoted index from `benchmarks/document_library/`
   - Validate input queries against the JSON schemas above
   - Return records matching the output schemas
   - Include synthetic known-answer test queries for deterministic verification

2. **P95.4** — Write usage example demonstrating both use cases end-to-end

---

*DO NOT MODIFY THIS FILE WITHOUT EXPLICIT MAINTAINER DIRECTION.*
