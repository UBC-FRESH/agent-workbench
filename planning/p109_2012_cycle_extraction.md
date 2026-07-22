# P109: 2012 Cycle Extraction and Audit

## Phase Context

P109 is the first active extraction phase after P118 (native Agent Hub with
vLLM provider). It targets the most recent TSA23 cycle (2012), which is the
primary target for initial FEMIC use.

## Corpus

Three 2012-cycle documents:
- `tsa23_2012_23tsdp12` (Data Package): 11 chunks, 139 records
- `tsa23_2012_23ts13ra` (Rationale): 6 chunks, 75 records
- `tsa23_2012_23ts13pdp` (Discussion Paper): 3 chunks, 36 records

Total: 20 chunks across 106 pages, 250 candidate records.

## GitHub Structure

- Parent issue: [#741](https://github.com/UBC-FRESH/agent-workbench/issues/741)
- Branch: `feature/p109-2012-cycle-extraction`
- Child issues:
  - [#742](https://github.com/UBC-FRESH/agent-workbench/issues/742) — P109.1 (closed, 250 records extracted)
  - [#744](https://github.com/UBC-FRESH/agent-workbench/issues/744) — P109.2 (audit, open)
  - [#745](https://github.com/UBC-FRESH/agent-workbench/issues/745) — P109.3 (90% yield gate, open)
  - [#746](https://github.com/UBC-FRESH/agent-workbench/issues/746) — P109.4 (stop on gate failure, open)

## Status

- P109.1: Complete — 250 candidate records extracted via P118 native Agent Hub
- P109.2-P109.4: Pending — audit and gate evaluation not yet started

## Key Decisions

1. **Single vLLM provider**: All roles (Coordinator, Supervisor, Worker, Advisor)
   use the same Qwen 3.6 27B model via vLLM endpoint. Role separation comes from
   bounded instructions, not model identity.

2. **Concurrent extraction**: P109.1 used 2-4 parallel workers for independent
   chunk processing, following P115-P118 concurrency conventions.

3. **Yield gate at 90%**: P109.3 requires ≥90% useful yield (225/250) with zero
   critical source-anchor defects before promotion.

## Notes

- P89 schema naming mismatch (chunk IDs use `p114_N_1` vs expected `N_1` pattern)
  exists but is not a blocking defect per maintainer direction.
- Document-type metadata (rationale/discussion/data) must be preserved in accepted
  records for downstream FEMIC use.