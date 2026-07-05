# Document Index Worker Ticket

## Mission

Extract source-anchored document metadata records from the supplied chunks only.
Return machine-readable records only. Do not summarize the task in prose.

## Current State

- corpus_id:
- document_id:
- source_sha256:
- page_range:
- chunk_count:
- chunk_manifest:
- output_record_type: `structure` or `content_metadata`

## Inputs

The supervisor will provide one or more source chunks with:

- chunk_id
- pdf_page or page_range
- document_component
- text_sha256
- chunk text

Use only those supplied chunks.

## Output Format

Return JSONL only. Each line must be one JSON object.

Required fields:

- `record_id`
- `corpus_id`
- `document_id`
- `source_sha256`
- `chunk_id`
- `page_anchor`
- `document_component`
- `section_path`
- `object_type`
- `title`
- `summary`
- `source_quote`
- `confidence`
- `worker_model`
- `review_status`

Set `review_status` to `raw_worker_candidate`.

## Allowed Object Types

Structure pass:

- `component_boundary`
- `heading`
- `appendix`
- `table`
- `figure`
- `map`
- `acronym`
- `definition`
- `cross_reference`
- `other`

Content metadata pass:

- `claim`
- `assumption`
- `constraint`
- `policy_reference`
- `model_input`
- `numeric_value`
- `scenario`
- `sensitivity_test`
- `decision_rationale`
- `other`

## Rules

- Do not invent pages, sections, titles, values, definitions, or citations.
- Prefer fewer, stronger records over many vague records.
- Include a short source quote that directly supports the record.
- If a record is useful but uncertain, lower `confidence`.
- If a chunk has no useful metadata, output no records for that chunk.
- Stop after the JSONL records.

## Failure Conditions

Stop and report no records if:

- the supplied text is missing;
- the source SHA does not match the ticket metadata;
- the requested output type is unclear; or
- the task asks for information outside the supplied chunks.
