# Phase 28 Claim Review Aids

Phase 28 adds a small supervisor-owned claim-review layer to evidence
summaries. The FreshForge pilot showed that a worker can return a useful
proposal while also inventing unsupported evidence. Claim review makes that
failure mode explicit.

## Claim Buckets

Evidence summaries may include:

- `accepted_claims`: claims the supervisor accepts as evidence-supported;
- `rejected_claims`: unsupported, contradicted, invented, or out-of-scope
  claims; and
- `needs_evidence_claims`: potentially useful claims that require another
  evidence-gathering step.

These fields are optional so older evidence summaries remain valid. When
present, each field must be a list of strings or claim objects with a `text`
field.

## Packet Behavior

`agent-workbench evidence render` and `agent-workbench evidence synthesize`
show claim review sections when claim fields are present. Decision packets also
count claim dispositions across all synthesized evidence summaries.

## Boundary

This is not automated fact-checking. The supervisor still decides claim
disposition and must verify claims before promotion.
