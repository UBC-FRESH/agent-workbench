# P95.1 — Retrieval Use Case Selection

**Date:** 2026-07-11  
**Task:** Select 1-2 concrete retrieval use cases scoped to the P94 index format  
**Status:** selection done; scoping note written  

---

## Selected Document Corpus Target

Two viable targets were considered; both are acceptable for initial P95.1 work:

### Option A (initial): Re-process the existing 2012 TSA 23 TSR document bundle
- The most recent TSA 23 data package (`tsa23_2012_23tsdp12`) is already available in `benchmarks/document_library/tsa23_tsr/` as a 41-page PDF (`23tsdp12.pdf`).
- This bundle was previously chunked and indexed by the P90-P92 pipeline using `qwen3.6:35b-a3b-q8_0`.
- **Reuse approach:** re-process from scratch using the new custom-agent role hierarchy (supervisor + paid Advisor) rather than the old section-ticket battery. This tests whether the fresh role-hierarchy framework produces better yields or cheaper coordination overhead.
- **FEMIC leveraged:** `femic tsr fetch` and `femic tsr index` handle document resolution and materialization; no need to re-invent these functions. The P95 retrieval layer queries against the promoted index format, not the raw PDFs.

### Option B (subsequent): Fetch circa-2006 TSR cycle for TSA 23
- FEMIC also carries the capability to fetch older TSA 23 cycles (circa 2006), which would provide a temporally distinct corpus for testing cross-cycle retrieval.
- This is scoped as **out of scope** for P95.1 but explicitly noted as the natural next corpus target for P95.3/P95.4 if the initial use cases succeed with the 2012 bundle.

**Decision:** Start with Option A (2012 re-process) to keep P95.1 fast and bounded. The 2006 cycle fetch is a future task.

---

## Use Case 1: Page/Chunk Anchor Lookup by Document and Page Range

**Description:** Given a document identifier (e.g., `tsa23_2012_23tsdp12`) and a page range (e.g., pages 5-12), return all promoted index records whose page/chunk anchors fall within that range, ordered by page number.

**Example query:**  
"Find all source-backed facts about pages 8-15 of the TSA 23 2012 TSR document bundle."

**P94 schema fields used:**
- `source_hash` / `document_id` — identifies the document (e.g., from `tsa_documents.json`)
- `page_anchor` / `chunk_id` — enables page-range filtering
- `model_lane` — tracks which worker lane produced this record
- `audit_status` — filters to only accepted/repaired records

**Why this use case:** It directly supports downstream modelling agents that need to cite specific sections of a known document. This is the most natural "lookup by anchor" pattern for technical documents with numbered pages.

**Relevance to 2006 cycle:** If the 2006 cycle exists, the same query pattern works — just substitute `tsa23_2006_*` as the document identifier. The schema contract from P94 ensures format compatibility across cycles.

---

## Use Case 2: Full-Document Provenance Trace

**Description:** Given a document identifier, return all promoted records derived from that single document, with complete provenance chain from source hash through model lane to final audit status. Sortable by audit status or model lane.

**Example query:**  
"Show every record in the project-owned index that came from the TSA 23 2012 data package, grouped by model lane and audit status."

**P94 schema fields used:**
- `source_hash` — groups records to their source document
- `model_lane` — groups by which worker lane produced them
- `audit_status` — shows acceptance level
- `page_anchor` / `chunk_id` — preserves ordering within the document

**Why this use case:** It supports quality review and audit tracing. A modelling agent or supervisor needs to know: "how many records did we extract from this source, how were they validated, and what's the overall confidence?" This is a higher-level aggregate query rather than a page-level lookup.

---

## Scope Boundaries

### In scope for P95.1
- Define these two use cases with concrete input/output examples
- Document scope/out-of-scope in this planning note
- Survey existing CLI surfaces to confirm no command already serves these use cases

### Out of scope for P95.1
- Implementing the retrieval functions (P95.3)
- Designing the query contract schema (P95.2)
- Fetching or processing the 2006 TSR cycle documents (future phase)
- Writing the usage example walkthrough (P95.4)

### Related but separate decisions
- Whether to commit document-metadata-extraction-and-index work to `femic/external/femic-tsa23-instance` is a P108/FEMIC concern — this planning note does not make that decision; it only notes that the custom-agent supervisor role (from P92) could be reused for any fresh processing
- The paid Advisor budget: one invocation used this session for roadmap critique. No Advisor needed for P95.1 unless the use case selection stalls

---

## CLI Surface Survey Summary

Before finalizing, a survey of existing `agent-workbench` subcommands was conducted (see `src/agent_workbench/cli.py`). Key findings:

| Subcommand | Function | Relevant to Use Case 1 or 2? |
|-----------|----------|------------------------------|
| `evidence render` | Render markdown from summary JSON | No — rendering, not querying |
| `evidence synthesize` | Synthesize summaries from raw data | No — aggregation, not retrieval |
| `foundrytk profile-evaluation-aggregate` | Aggregate model evaluation metrics | No — different domain |
| `graph render/validate` | Render workflow graphs | No — graph ops, not document retrieval |
| `smoke` | Command-surface smoke checks | No — infra health check |

**Conclusion:** No existing `agent-workbench` subcommand provides document/index retrieval queries against the P94 promoted index format. A new CLI subcommand (or module-level function) is needed for P95.2/P95.3.

---

## Next Steps

1. **P95.2** — Design the query contract: JSON schema for inputs/outputs, provenance inclusion rules
2. **P95.3** — Implement retrieval functions against the P94 index (using `femic` for fetch/materialization if needed)
3. **P95.4** — Write a usage example demonstrating both use cases

---

*DO NOT MODIFY THIS FILE WITHOUT EXPLICIT MAINTAINER DIRECTION.*
