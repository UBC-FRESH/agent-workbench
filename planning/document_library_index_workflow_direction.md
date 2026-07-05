# Document Library Index Workflow Direction

## Purpose

Agent Workbench should treat public technical-document library indexing as a
first-class high-potential delegation lane.

The MP11 benchmark is one test case, but the broader workflow target is a
repeatable way to turn hard-to-use public document corpora into structured,
source-anchored metadata indexes that downstream scientific modelling projects
can search, mine, and cite.

This lane is promising because it has the economic shape Agent Workbench is
designed to exploit:

- large input-token volume;
- public but under-indexed source material;
- repeated structure/content extraction work;
- clear provenance and source-anchor requirements;
- high downstream value for modelling and coding agents; and
- supervisor work that can be reduced to audit, calibration, and acceptance
  decisions instead of reading every page directly.

## Case Study Motivation

The immediate motivating case is the BC forest-management public-document
archive collected around FEMIC work: TSR, TFL, management-plan, analysis,
information-package, rationale, and related documents that are technically
public but often hard to rediscover or use at scale.

The strategic goal is not just to summarize documents. The goal is to build a
living, machine-readable library of planning evidence that can help future
forest estate modelling work:

- find comparable management-unit precedents;
- recover historical assumptions, constraints, AAC decisions, and sensitivity
  scenarios;
- locate tables, figures, maps, appendices, and policy references;
- seed FEMIC model-input planning with source-backed facts;
- support LLM coding agents with reliable retrieval surfaces; and
- preserve public planning knowledge that may otherwise become functionally
  lost.

Agent Workbench should keep the workflow generic. The same recipe should apply
to other scientific, technical, regulatory, and project-document collections.

## Workflow Shape

The reusable document-library workflow has seven stages.

1. Corpus registry
   - Assign stable document IDs.
   - Record source URL or acquisition provenance.
   - Record SHA256, byte size, publication date, document type, jurisdiction,
     management unit, and extraction status.
   - Keep raw documents and extracted text under project-owned ignored or data
     paths, not in Agent Workbench.

2. Text extraction and chunk manifest
   - Export page- or section-level text chunks.
   - Record chunk IDs, page ranges, source hashes, word counts, character
     counts, component hints, and runtime text paths.
   - Track sanitized manifests, not raw page text.

3. Structure pass
   - Use local workers to extract component boundaries, headings, appendices,
     tables, figures, maps, acronyms, definitions, and cross-references.
   - Require JSONL or JSON records with source and page anchors.

4. Content metadata pass
   - Extract claims, assumptions, model-input hints, constraints, values,
     scenarios, sensitivity tests, policy references, and decision rationales.
   - Keep record types explicit and stable enough for later indexing.

5. Source-anchored repair prepass
   - Give a local worker candidate records plus compact source excerpts.
   - Ask it to propose `accepted_candidate`, `needs_repair`, or
     `likely_reject` labels and structured repair fields.
   - Treat this as a draft only.

6. Supervisor audit and calibration
   - Paid supervisor audits a stratified sample or high-value subset.
   - Measure supervisor audit tokens.
   - Estimate accepted, repairable, rejected, and audit-cost-per-record rates.
   - Decide whether to scale, retune, split, or stop.

7. Index assembly
   - Promote accepted and repaired records into a project-owned index:
     JSONL, SQLite, Parquet, or another target-project storage surface.
   - Preserve source document ID, SHA256, page/chunk anchor, extraction model,
     audit status, and provenance.

## Reusable Template Assets

This direction adds starter assets:

- `templates/document_library_corpus_record.json`
- `templates/document_index_worker_ticket.md`
- `templates/source_anchored_repair_prepass_ticket.md`
- `templates/workbench_templates/document_library_index_graph.json`

These are generic Agent Workbench templates. Target projects copy or render
them into ignored runtime paths and customize them for the actual corpus.

## Delegation Economics Hypotheses

The first MP11 runs suggest:

- 24-page worker tickets are a strong starting point for long technical PDFs.
- Single large prompts can collapse even when the same content succeeds as a
  sequence of smaller tickets.
- Quiet batch orchestration and scripted summaries materially reduce paid
  supervisor mechanics cost.
- Source-level audit cost is real and can thin the apparent margin.
- A local repair prepass may reduce supervisor audit cost if it improves page
  anchors, record types, and duplicate handling before paid review.

The next economics question is therefore:

```text
Does a source-anchored local repair prepass reduce paid supervisor audit cost
per accepted or repairable record enough to increase net delegation margin?
```

## Tuning Metadata To Preserve

Future document-library runs should record:

- source document ID and SHA256;
- document type, management unit, date, and corpus collection;
- page range, chunk count, word count, and character count;
- ticket shape and chunk size;
- model ID and provider;
- execution order and retry count;
- timeout, keep-alive context, and cold/warm timing when available;
- worker input/output tokens;
- supervisor fresh input, cached input, output, and reasoning tokens;
- candidate record counts by object type;
- parse/format error counts;
- duplicate and source-mismatch counts;
- accepted, repairable, rejected, and needs-review counts;
- audit cost per sampled record;
- audit cost per accepted or repairable record; and
- final promoted index record count.

## Near-Term Implementation Direction

The next concrete step should be a repair-prepass experiment:

1. Use the MP11 qwen x16 audit sample as the seed.
2. Build a local-worker repair-prepass ticket from candidate records plus source
   excerpts.
3. Run `gpt-oss:20b` or another installed local Ollama model.
4. Measure local worker tokens and paid supervisor review tokens.
5. Compare supervisor audit cost with and without the repair-prepass.
6. Promote the result into the benchmark registry as another audit-calibration
   observation.

If this succeeds, the document-library workflow becomes a reusable high-ROI
recipe for broader public technical-document corpora.
