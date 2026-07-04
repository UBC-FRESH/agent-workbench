# Phase 13 GitHub Workflow Microtrial Notes

## Purpose

Phase 13 tests a narrow GitHub workflow boundary: workers may prepare a bounded
comment body, but the supervisor performs and verifies the actual GitHub
mutation.

This phase does not delegate issue closure, PR creation, PR merge, or broad
phase closeout to a worker.

## Protocol

- Read-only audit comes first.
- Worker-prepared content remains ignored until reviewed.
- Supervisor mutation uses file-backed `gh` commands.
- Verification uses read-only `gh issue view` or `gh pr view`.

## Read-Only Audit

The P13 parent issue and child issue state were inspected with read-only `gh`
commands before mutation.

## File-Backed Comment Trial

The worker-preparation trial will generate a bounded comment body candidate.
The supervisor will review and post one concise file-backed progress comment to
the P13 comment-preparation child issue.

Sanitized findings will be recorded here after the trial.

### Result

The P13 GitHub workflow microtrial completed with a useful partial worker
result and a successful supervisor-owned GitHub mutation.

Sanitized sequence:

1. Supervisor ran read-only `gh issue view` checks for the parent and target
   child issue.
2. Worker generated an ignored comment-body candidate through the SDK harness.
3. Candidate classification was `missing-section`; it included
   `## Comment Body` but omitted `## Boundaries`.
4. Supervisor wrote a reviewed file-backed comment body.
5. Supervisor posted the comment with `gh issue comment`.
6. Supervisor verified the comment with read-only `gh issue view`.

Interpretation:

- Worker-prepared GitHub text is useful but still requires supervisor review.
- Missing required sections should prevent direct use of worker-prepared bodies.
- Supervisor-owned `gh` mutation and read-only verification is the right
  boundary for now.
- P14 can include this as evidence against delegating issue closure or PR merge
  to worker agents.
