# Phase 62 Document-Indexing Workflow Recipe V1

## Purpose

P62 converts the P55 document-indexing experiments and P57 packaged-supervisor
lessons into a reusable recipe for public technical PDF corpora.

This phase is deliberately non-live. It creates the durable recipe contract that
P63 can instantiate under a P59 budget gate.

## Evidence Carried Forward

- P55 showed that document extraction quality depends strongly on ticket shape,
  model role, and repair/verification stages.
- P58 reconciled P55-P57 evidence and moved further indexing work into P62/P63.
- P59 made budget declarations and stop rules mandatory for economics claims.
- P60 separated artifact quality, protocol acceptance, and economics usability.
- P61 packaged the pre-materialized local-supervisor workflow boundary.

## Recipe Decisions

The recipe uses a staged workflow:

1. corpus resolution and materialization;
2. deterministic chunk manifest generation;
3. budget gate and run envelope;
4. section-map extraction;
5. typed fact extraction;
6. local self-audit and repair;
7. disagreement and verification pass;
8. deterministic validation;
9. paid supervisor sample audit; and
10. promoted index assembly.

The stages preserve a strict authority boundary. Local workers may produce,
audit, and repair candidates. Deterministic validators may reject invalid
artifacts. The paid supervisor owns final labels, economics interpretation, and
scale-or-stop decisions.

## Task-Size Defaults

The recipe recommends page-window and record-batch defaults, but it does not
hide record caps inside templates or tooling. If a ticket uses a record cap, the
ticket must say so directly and explain how the cap affects coverage metrics.

## Model Role Defaults

The recipe distinguishes role categories from model names:

- general document-understanding models for section-map and typed extraction;
- coding-oriented models for strict JSON repair;
- verifier/critic roles only when corpus-specific evidence supports them; and
- paid supervisor audit for final acceptance and economics decisions.

Installed model names remain deployment-specific and must come from the
configured Ollama inventory at run time.

## Public-Safety Boundary

Tracked P62 artifacts are recipe docs and templates only. Raw PDFs, raw
extracted text, prompts, worker outputs, provider details, transcripts, and
private endpoint information stay in target-project ignored runtime or data
management paths.

## P63 Handoff

P63 should instantiate this recipe on one bounded TSA23 slice. Before any live
worker call, P63 must declare:

- the experiment question;
- the maximum paid-supervisor cost;
- the maximum attempts;
- checkpoint spans;
- stop conditions;
- maintainer checkpoint trigger; and
- expected outcome fields.

P63 should report quality, protocol, and economics outcomes separately rather
than collapsing them into a single success/failure claim.
