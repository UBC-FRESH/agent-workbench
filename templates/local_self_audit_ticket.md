# Local Self-Audit Ticket

## Mission

Audit supplied candidate records against supplied source excerpts. Return JSONL
only. This is defect reduction for supervisor review, not validation.

## Current State

- corpus_id:
- document_id:
- source_sample_id:
- candidate_record_count:
- output_path:
- worker_model:

## Inputs

For each candidate, the supervisor supplies:

- candidate identifier;
- page and chunk anchor;
- object type;
- title;
- section path;
- candidate summary; and
- source excerpt.

Use only the supplied candidate and source excerpt.

## Output Format

Return JSONL only. Each line must be one JSON object.

Required fields:

- `candidate_record_id`
- `draft_label`
- `defect_categories`
- `supported_by_excerpt`
- `page_anchor_ok`
- `object_type_ok`
- `title_ok`
- `summary_ok`
- `repair_instruction`
- `evidence_quote`
- `rationale`
- `worker_model`

Allowed `draft_label` values:

- `accepted_candidate`
- `needs_repair`
- `likely_reject`

Allowed `defect_categories` values:

- `none`
- `unsupported_summary`
- `wrong_page_anchor`
- `wrong_object_type`
- `overbroad_title`
- `overbroad_summary`
- `duplicate_only`
- `too_vague`
- `outside_schema`
- `other`

## Rules

- Do not approve or validate the final record.
- Do not add facts that are not in the source excerpt.
- Mark `accepted_candidate` only when the candidate is source-supported and
  materially useful as written.
- Mark `needs_repair` when the source supports the idea but the page anchor,
  object type, title, or summary needs cleanup.
- Mark `likely_reject` when the source excerpt does not support the candidate,
  the record is duplicate-only, or the record is too vague to use.
- Keep `repair_instruction` concise and actionable.
- Stop after the JSONL records.

## Failure Conditions

Return one JSON object with `draft_label` set to `likely_reject` and a clear
`rationale` if:

- the supplied source excerpt is missing;
- the candidate identifier is missing; or
- the task asks for facts outside the supplied excerpts.

## Supervisor Boundary

Local self-audit is not validation. The paid supervisor owns final labels,
promotion decisions, scale decisions, and scientific acceptance.
