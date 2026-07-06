# Phase 69: Behavior Analytics From Archives

Phase 69 turns P65 Copilot archive manifests into reusable behavior metrics for
delegation-policy tuning.

## Issue And Branch

- Parent issue: #454
- Child issues: #455, #456, #457, #459
- Branch: `feature/p69-behavior-analytics-from-archives`

## Metrics

Per-run behavior summaries include:

- stall count;
- nudge count;
- tool-call count;
- command-failure count;
- shell-mismatch count;
- repeated-summary count;
- premature-completion claim count;
- user-intervention burden; and
- coordinator-review burden.

Behavior outcome classes:

- `smooth`;
- `nudged-success`;
- `noisy-success`;
- `repair-needed`;
- `blocked`;
- `runaway`.

## Policy Feedback Boundary

P69 summaries may recommend tighter tickets, repair tickets, escalation, or more
archive collection, but they must not tune default delegation policy from one or
two anecdotes. The minimum archive count before changing defaults is ten runs.

Raw transcripts remain ignored. The analyzer consumes sanitized P65 archive
manifests and emits public-safe JSON/Markdown summaries.
