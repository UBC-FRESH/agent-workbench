# Phase 91 Source-Audit Decision Packet Plan

## Purpose

P91 answers the first post-extraction ROI question for the P90 full-document
candidate packet: did the worker produce source-backed records useful enough to
justify scaling audit, repairing the protocol, or promoting a small accepted
seed?

The reporting-worker role is deliberately secondary. The paid supervisor must
own source audit and final acceptance decisions; the reporting worker may only
draft sanitized summaries from already-audited rows.

## Inputs

- P90 summary:
  `benchmarks/document_library/p90_full_document_candidate_packet_summary.json`.
- P90 packet manifest:
  `benchmarks/document_library/p90_full_document_candidate_packet_manifest.json`.
- Ignored runtime candidate packet:
  `runtime/document_library/tsa23_tsr/p90_full_document_candidate_packet/`.
- P89 worker tickets with source excerpts:
  `runtime/document_library/tsa23_tsr/p89_document_indexing_recipe_v2/tickets/`.

## Audit Sample

Select a bounded mixed sample, favoring breadth over volume:

- 6 valid `structure` records;
- 6 valid `content_metadata` records;
- 4 invalid-run records with emitted repaired candidates;
- all zero-record runs as run-level defect rows.

The tracked sample manifest must contain record IDs, ticket IDs, ticket types,
validation statuses, runtime source paths, and audit prompts, but not raw source
text or raw worker prose.

## Audit Statuses

Record-level audit statuses:

- `accepted`: source-backed, correctly typed, useful, and specific enough for
  downstream retrieval.
- `repairable`: source-backed but needs bounded field, typing, page, quote, or
  duplicate cleanup.
- `rejected`: not source-backed, materially wrong, uselessly vague, or not a
  valid index record.
- `needs_review`: cannot be decided from the bounded audit packet.

Run-level defect statuses:

- `zero_record_defect`: worker completed but emitted no repaired candidates.
- `protocol_defect`: output format or schema behavior blocks confident audit.

## Supervisor Audit

For each sampled record, the supervisor checks the candidate against the source
excerpt in the ignored P89 ticket. The tracked audit result may quote short
field values from candidate metadata, but must not include source excerpts or
raw worker prose.

The audit row must include:

- sample ID;
- record ID or run ID;
- ticket ID and ticket type;
- validation status;
- audit status;
- defect class;
- source-anchor verdict;
- usefulness verdict;
- short public-safe rationale.

## Reporting-Worker Draft Packet

After the supervisor audit rows exist, generate a non-authoritative reporting
draft from sanitized rows only. It may summarize counts and recurring patterns,
but it must state that the supervisor audit rows are the authority.

## Decision

The final decision packet must choose one:

- `scale_audit`: accepted plus repairable yield is high enough to audit more;
- `repair_protocol`: useful signal exists but protocol defects dominate;
- `promote_seed`: accepted records are good enough to promote a small seed in a
  later phase;
- `switch_model_or_prompt`: audit failures are mainly lane/prompt behavior;
- `stop`: candidates are not useful enough to justify more investment.

## Acceptance

- A tracked sample manifest exists and is public-safe.
- A tracked supervisor audit packet exists and includes accepted, repairable,
  rejected, or defect classifications.
- A tracked non-authoritative reporting-worker draft exists.
- The decision packet separates quality, protocol, and economics/governance
  implications.
- Accepted record count is reported only for audited sample rows, not the whole
  P90 packet.
- `ROADMAP.md`, `CHANGE_LOG.md`, issue #555, and the PR body agree.
- Validation gates pass:
  - `ruff format src tests scripts\build_p89_document_indexing_recipe_v2.py scripts\run_p90_qwen36_comparison_batch.py scripts\run_p90_full_document_candidate_packet.py scripts\build_p91_source_audit_packet.py`
  - `ruff check src tests scripts\build_p89_document_indexing_recipe_v2.py scripts\run_p90_qwen36_comparison_batch.py scripts\run_p90_full_document_candidate_packet.py scripts\build_p91_source_audit_packet.py`
  - `mypy src`
  - `pytest tests -q`
  - `pre-commit run --all-files`
  - `git diff --check`
