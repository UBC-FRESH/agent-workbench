# Phase 60 Outcome Semantics And Scoring Split

## Purpose

P60 standardizes how Agent Workbench distinguishes three different claims that
were too easy to collapse during P55-P57:

- artifact quality: did the produced artifact validate and appear usable?
- protocol compliance: did the run respect the intended authority and workflow
  boundary?
- economics usability: was the paid-supervisor token/cost measurement captured
  at a credible boundary?

The key requirement is that a useful local-supervisor result can be recorded as
quality-valid but protocol-rejected or economics-diagnostic without becoming a
vague failure.

## Outcome Fields

- `quality_validated_candidate`: deterministic validators and hard quality
  constraints accepted the artifact.
- `protocol_accepted_candidate`: the run followed the requested execution and
  authority boundary.
- `economics_usable`: token/cost evidence is measured at the right boundary and
  the run is not stale, aborted, or protocol rejected.
- `final_decision`: compact decision label for maintainer-facing comparison.
- `rejection_reasons`: explicit reasons for rejection, diagnostic-only status,
  or escalation.

## Hard Constraints

Hard constraints represent trust, schema, or authority failures. Examples:

- invalid schema shape;
- wrong source identity or invalid source IDs;
- authority-boundary violations;
- stale-session contamination;
- aborted runs; and
- model-provenance mismatch when the task depends on model identity.

## Soft Scoring

Soft scoring represents objective-function misses. Quote length is the main
example from P55: going a few words over a target should guide repair/scoring,
not dominate whether the artifact is usable.

P60 keeps quote length as a soft penalty by default. Future recipes can opt into
hard excerpt limits only when a downstream consumer requires that strict
contract.

## Boundary

P60 uses existing artifacts and tests only. It launches no live Copilot/Ollama
jobs. Production document-indexing recipes remain P62/P63 work.
