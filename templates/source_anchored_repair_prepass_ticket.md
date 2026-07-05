# Source-Anchored Repair Prepass Ticket

## Mission

Review candidate document-index records against supplied source excerpts and
propose repair labels. This is a local-worker draft for supervisor review, not
final approval.

## Current State

- corpus_id:
- document_id:
- source_sha256:
- candidate_record_count:
- audit_sample_id:
- output_path:

## Inputs

For each candidate, the supervisor will provide:

- candidate record metadata;
- candidate title and summary;
- page/chunk anchor;
- object_type;
- source excerpt; and
- allowed schema vocabulary.

Use only the supplied candidate and source excerpt.

## Output Format

Return JSONL only. Each line must be one JSON object.

Required fields:

- `candidate_record_id`
- `draft_label`
- `repair_priority`
- `supported_by_excerpt`
- `page_anchor_ok`
- `object_type_ok`
- `title_ok`
- `summary_ok`
- `proposed_object_type`
- `proposed_title`
- `proposed_summary`
- `evidence_quote`
- `rationale`
- `worker_model`

Allowed `draft_label` values:

- `accepted_candidate`
- `needs_repair`
- `likely_reject`

Allowed `repair_priority` values:

- `none`
- `low`
- `medium`
- `high`

## Review Rules

- Mark `accepted_candidate` only when the candidate is source-supported and
  materially useful as written.
- Mark `needs_repair` when the source supports the idea but page anchor,
  object type, title, or summary needs cleanup.
- Mark `likely_reject` when the source excerpt does not support the candidate,
  the candidate is duplicate-only, or the candidate is too vague to use.
- Keep repair text concise.
- Do not add facts not visible in the supplied excerpt.
- Stop after the JSONL records.

## Supervisor Boundary

The paid supervisor owns final labels. This prepass exists to reduce the
supervisor's first-pass classification and repair-writing burden.
