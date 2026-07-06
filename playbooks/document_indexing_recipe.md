# Document Indexing Workflow Recipe

This playbook defines the default Agent Workbench recipe for turning public
technical PDF corpora into source-anchored metadata indexes.

The recipe is designed for high-input-volume work where local Ollama workers can
grind through public document text while the paid supervisor stays focused on
calibration, audit, economics, and scale-or-stop decisions.

## Operating Boundary

Use this recipe for public technical documents when the target project can keep
raw PDFs, extracted text, prompts, worker outputs, provider details, and runtime
logs out of tracked Agent Workbench files.

P62 is a recipe and template phase only. It does not authorize live worker runs.
Live execution belongs in a later pilot phase with a budget declaration,
checkpoint spans, and a maintainer-visible stop rule.

## Stage Model

1. Corpus resolution and materialization
   - Owner: target-project tooling or coordinator.
   - Output: tracked sanitized corpus registry plus ignored or data-managed raw
     document files.
   - Rule: record stable document IDs, source provenance, hashes, page counts,
     document type, date, jurisdiction, and status.

2. Deterministic chunk manifest generation
   - Owner: target-project tooling.
   - Output: tracked sanitized chunk/page manifest plus ignored raw text chunks.
   - Rule: store chunk IDs, page ranges, source hashes, word/character counts,
     and runtime text references. Do not track raw extracted text.

3. Budget gate and run envelope
   - Owner: paid supervisor or coordinator.
   - Output: budget declaration and stop-rule record.
   - Rule: any live run that will support economics claims must declare maximum
     paid-supervisor cost, maximum attempts, checkpoint spans, stop conditions,
     and the maintainer checkpoint before worker contact.

4. Section-map extraction
   - Owner: local document-understanding worker.
   - Output: ignored candidate section-map JSONL.
   - Rule: identify document components, headings, appendices, tables, figures,
     maps, definitions, acronyms, and cross-references using supplied chunks
     only.

5. Typed fact extraction
   - Owner: local document-understanding worker.
   - Output: ignored typed fact candidate JSONL.
   - Rule: extract explicitly typed claims, assumptions, constraints, policy
     references, numeric values, scenarios, sensitivity tests, decision
     rationales, and modelling inputs with source anchors.

6. Local self-audit and repair
   - Owner: local audit and repair workers.
   - Output: ignored defect labels and repaired candidate drafts.
   - Rule: local workers may classify, normalize, and repair candidates, but
     they cannot approve or promote records.

7. Disagreement and verification pass
   - Owner: deterministic comparison plus optional local verifier.
   - Output: ignored disagreement records and verifier drafts.
   - Rule: compare candidate fields record-by-record. Send only disagreements,
     low-confidence fields, or high-value facts to verifier roles.

8. Deterministic validation
   - Owner: script or validator.
   - Output: validation report with schema, source identity, duplicate, and
     authority-boundary checks.
   - Rule: invalid schema, wrong source identity, and authority violations are
     hard defects. Quote length and wording preferences are soft penalties by
     default.

9. Paid supervisor sample audit
   - Owner: paid supervisor.
   - Output: tracked sanitized audit and economics summary.
   - Rule: audit a stratified or high-value sample. Record accepted, repaired,
     rejected, escalated, and needs-review counts with paid token spans.

10. Promoted index assembly
    - Owner: target-project tooling with supervisor approval.
    - Output: target-project index or data-managed output.
    - Rule: promote only source-anchored records that passed deterministic
      validation and supervisor-approved acceptance criteria.

## Task Sizing Defaults

Default page-window sizes are starting points, not hidden limits.

| Task shape | Default size | Notes |
| --- | --- | --- |
| Section-map chunk | 12-24 PDF pages | Prefer smaller windows when headings are dense or OCR is weak. |
| Typed fact extraction chunk | 8-16 PDF pages | Use smaller windows for table-heavy, numeric, or policy-dense pages. |
| Repair batch | 25-75 candidate records | Provide source excerpts and validation defects, not raw whole-document text. |
| Disagreement verification batch | 10-40 disputed fields | Include only candidate fields and compact source evidence. |
| Paid supervisor audit sample | 10-30 records | Stratify by object type, confidence, document section, and worker model. |

No Agent Workbench recipe may impose a hidden record cap. If a cap is useful for
a specific ticket, the ticket must state it explicitly, explain why it exists,
and record whether the cap could distort coverage metrics.

## Split Strategy

For one long document:

- split by table of contents, appendix boundaries, or stable page windows;
- keep each chunk's page and source-hash anchors stable;
- run section-map extraction before typed facts when document structure is
  unknown; and
- avoid single huge prompts when a sequence of smaller tickets can cover the
  same source material.

For a mini-corpus:

- process the most recent or highest-value documents first;
- keep one corpus registry across all documents;
- run one bounded calibration slice before scaling; and
- compare quality, protocol, and economics outcomes before adding more
  documents.

For scanned or OCR-poor inputs:

- stop early if text extraction quality prevents source-anchored records;
- classify the document as needing OCR/materialization repair;
- do not ask local workers to infer facts from unreadable text; and
- escalate materialization quality before semantic extraction.

## Model Role Defaults

Model names are deployment-specific and must come from the configured Ollama
inventory. The recipe uses role categories rather than hard-coded requirements.

| Role | Default model family | Evidence posture |
| --- | --- | --- |
| Section-map extraction | General document-understanding model | Preferred over coding-specialized models for broad document comprehension. |
| Typed fact extraction | General document-understanding model | Use bounded chunks and typed output contracts. |
| JSON repair | Coding-oriented model | Useful when the mission is strict syntax/schema repair. |
| Self-audit | General or reasoning-oriented local model | Optional until a given model proves useful on the corpus. |
| Disagreement verifier | Evidence-supported verifier only | Use on disagreements or high-value fields, not as a broad default. |
| Paid sample auditor | Paid supervisor | Owns final labels, economics interpretation, and scale/stop decision. |

## Outcome And Scoring

Every summarized run should distinguish:

- `quality_validated_candidate`
- `protocol_accepted_candidate`
- `economics_usable`
- `final_decision`
- `rejection_reasons`

Quote length is a soft weighted penalty by default. It becomes a hard failure
only when a downstream consumer explicitly requires strict excerpt limits.

Hard defects include invalid schema, wrong document or chunk identity,
fabricated source anchors, tracked raw source leakage, authority-boundary
violations, and missing budget records for economics claims.

## Public-Safety Rules

Tracked Agent Workbench artifacts may contain:

- recipe docs;
- sanitized corpus registry records;
- sanitized chunk manifests;
- schema or ticket templates;
- aggregate counts and economics summaries; and
- source identifiers and hashes.

Tracked Agent Workbench artifacts must not contain:

- raw PDF text;
- raw prompts;
- raw worker outputs;
- raw Copilot/Ollama transcripts;
- provider URLs, headers, or credentials;
- private endpoint details; or
- personal machine paths.

## Scale Decision

After one bounded pilot, decide explicitly:

- scale the recipe unchanged;
- retune task size or model role defaults;
- add a repair or verifier stage;
- pause the lane because quality or economics are not good enough; or
- escalate to paid-supervisor direct work for selected high-value records.
