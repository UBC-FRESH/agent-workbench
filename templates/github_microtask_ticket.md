# GitHub Microtask Ticket Template

Use this template for bounded GitHub workflow trials where the worker prepares
content but the supervisor performs any mutation.

## Worker Boundary

- Do not run `gh`.
- Do not claim to post, close, merge, label, or edit anything on GitHub.
- Do not perform issue closure, PR creation, PR merge, or release actions.
- Produce only the requested file-backed body or structured response.

## Supervisor Boundary

- The supervisor performs read-only `gh` audits.
- The supervisor reviews any worker-prepared body.
- The supervisor performs the actual `gh issue comment`, `gh pr create`, or
  other mutation when appropriate.
- The supervisor verifies mutations with read-only `gh` commands.

## Required Evidence

- read-only audit command and result;
- prepared body path;
- exact mutation command run by the supervisor; and
- read-only verification command and result.

