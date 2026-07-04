# Claim Review Checklist

Use this checklist before promoting worker output into tracked code, planning
notes, issue comments, or PR descriptions.

## Claim Disposition

Record worker claims in one of three buckets:

- `accepted_claims`: evidence-supported claims that the supervisor has
  independently verified or supplied as ticket context.
- `rejected_claims`: unsupported, contradicted, invented, or out-of-scope
  claims.
- `needs_evidence_claims`: potentially useful claims that require another
  ticket, command, source inspection, or maintainer decision before promotion.

## Review Questions

- Did the ticket provide the evidence, or did the worker infer it?
- Is the claim supported by a file, command output, issue URL, PR URL, rendered
  artifact, or other inspectable source?
- Does the claim overstate what the evidence proves?
- Does the claim introduce a project-specific assumption into generic Agent
  Workbench guidance?
- Should the claim be rejected, deferred for evidence, or promoted?

## Promotion Rule

Only `accepted_claims` may be promoted. `rejected_claims` and
`needs_evidence_claims` may be mentioned in sanitized planning notes only as
review findings, not as facts.
