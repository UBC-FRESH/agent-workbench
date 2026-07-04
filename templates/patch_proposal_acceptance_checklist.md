# Patch Proposal Acceptance Checklist

Use this checklist before a supervisor applies any worker-generated patch
proposal.

## Required Checks

- [ ] The worker output contains the required rationale, patch, and verification
      sections.
- [ ] The patch is a proposal only; the worker did not claim to apply it.
- [ ] Every proposed file path is explicitly allowed by the ticket.
- [ ] The patch is small enough for direct supervisor review.
- [ ] The patch is relevant to the assigned task boundary.
- [ ] The patch contains no unrelated formatting or metadata churn.
- [ ] The supervisor can apply the patch independently in a controlled follow-up
      step.

## Decision Mapping

| Classification | Supervisor decision |
| --- | --- |
| `patch-proposal` | Review manually; accept only after independent inspection. |
| `missing-patch` | Retry with a narrower ticket. |
| `malformed-patch` | Retry or reject depending on surrounding evidence. |
| `wrong-file` | Reject unless the ticket allowed the observed file. |
| `extra-prose` | Retry unless the patch is otherwise exact and harmless. |
| `refusal-or-forbidden-phrase` | Retry or mark blocked depending on cause. |
| `loop-like-repetition` | Reject. |

