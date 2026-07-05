# Delegated Repair Iteration Ticket

## Mission

Repair candidate records using supplied source excerpts and local self-audit
labels. Return JSONL only. These repaired records remain candidates for
supervisor review.

## Current State

- corpus_id:
- document_id:
- source_sample_id:
- candidate_record_count:
- self_audit_record_count:
- output_path:
- worker_model:

## Inputs

For each candidate, the supervisor supplies:

- original candidate record;
- source excerpt;
- local self-audit label;
- defect categories; and
- repair instruction.

Use only the supplied source excerpt and audit label.

## Output Format

Return JSONL only. Each line must be one JSON object.

Required fields:

- `candidate_record_id`
- `repair_action`
- `repaired_object_type`
- `repaired_title`
- `repaired_section_path`
- `repaired_summary`
- `source_quote`
- `remaining_defects`
- `ready_for_supervisor_delta_review`
- `rationale`
- `worker_model`

Allowed `repair_action` values:

- `unchanged_supported`
- `repaired_candidate`
- `unrepairable`

Allowed `remaining_defects` values:

- `none`
- `needs_supervisor_judgment`
- `missing_source_support`
- `ambiguous_page_anchor`
- `schema_mapping_unclear`
- `other`

## Rules

- Do not invent source support.
- Do not broaden a record beyond the supplied source excerpt.
- If the original candidate is already supported, use `unchanged_supported`.
- If the self-audit identifies a source-supported defect, repair only that
  defect.
- If the defect cannot be repaired from the excerpt, use `unrepairable`.
- Stop after the JSONL records.

## Supervisor Boundary

Repaired records are still local-worker candidates. The paid supervisor owns
acceptance, rejection, scale decisions, and any promoted index updates.
