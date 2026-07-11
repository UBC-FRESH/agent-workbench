# Phase 90 Full-Document Candidate Packet Plan

## Purpose

P90.2-P90.4 turns the P89 full-document materialization into one complete
candidate packet for source audit. The unit of work is the complete selected
`tsa23_2012_23tsdp12` data package document, not another model comparison or a
production index.

## Execution Lane

- Primary worker lane: `qwen3.6:35b-a3b-q8_0`.
- Reason: P90.1 showed the q8 lane had lower candidate yield than bf16 but
  better protocol validity over the side-by-side `structure` batch.
- Scope: all 120 P89 tickets, covering 60 section units and two ticket types:
  `structure` and `content_metadata`.
- Runtime output: ignored
  `runtime/document_library/tsa23_tsr/p90_full_document_candidate_packet/`.
- Tracked output: sanitized summaries and manifests only under
  `benchmarks/document_library/`.

## P90.2 Full-Document Extraction Execution

1. Add a resumable full-document runner that:
   - selects P89 tickets by ticket type;
   - runs the primary q8 model lane;
   - reruns only missing or non-completed raw probes when `--resume` is used;
   - extracts candidate JSONL from fenced JSONL, bare JSONL, and deterministic
     key/value blocks;
   - calls the P89 deterministic validator after every ticket; and
   - writes a sanitized tracked summary.
2. Run all 120 tickets unless a hard stop triggers.
3. Preserve raw worker output, candidate JSONL, repaired JSONL, and validation
   reports under ignored runtime paths.

## P90.3 Validation, Repair, And Stop Decision

The tracked summary must report:

- attempted, completed, blocked, valid, and invalid run counts;
- counts by ticket type;
- repaired record totals by ticket type;
- fatal validation error classes;
- extraction modes observed;
- tickets with zero repaired records;
- the stop decision.

Stop decisions:

- `ready_for_source_audit` when both ticket types have completed coverage and
  enough schema-valid candidates to support a bounded audit sample;
- `repair_protocol_first` when repeated format defects dominate and repaired
  records are too sparse for useful audit;
- `provider_or_runtime_blocked` when the local model lane cannot complete the
  selected document; or
- `manual_review_needed` when summary evidence is mixed.

## P90.4 Candidate Packet Handoff

The handoff is not an accepted index. It is a source-audit input packet with:

- the full-document summary path;
- ignored runtime packet path;
- candidate JSONL and repaired JSONL path inventory;
- validation-report path inventory;
- source-audit sampling recommendation;
- clear statement that all records remain candidate records until source audit.

## Acceptance

- The selected full document has candidate extraction attempted for all 120 P89
  tickets or a hard stop is recorded with exact evidence.
- Tracked artifacts contain no raw PDF text, raw worker prose, provider URLs,
  provider headers, credentials, or personal paths.
- `ROADMAP.md`, `CHANGE_LOG.md`, issue #554, and the PR body agree.
- Validation gates pass:
  - `ruff format src tests scripts\build_p89_document_indexing_recipe_v2.py scripts\run_p90_qwen36_comparison_batch.py scripts\run_p90_full_document_candidate_packet.py`
  - `ruff check src tests scripts\build_p89_document_indexing_recipe_v2.py scripts\run_p90_qwen36_comparison_batch.py scripts\run_p90_full_document_candidate_packet.py`
  - `mypy src`
  - `pytest tests -q`
  - `pre-commit run --all-files`
  - `git diff --check`
