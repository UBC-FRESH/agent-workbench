# Phase 50 FreshForge P16 A/B Benchmark Run

P50 is the first real phase-scale benchmark run. It stays open across multiple
iterations until the maintainer explicitly says it is done.

## Benchmark Target

- target repo: `UBC-FRESH/freshforge`
- target phase: FreshForge P16, provider result and validation evidence
  conventions
- direct lane worktree: `../freshforge-benchmark-p16-direct`
- delegated lane worktree: `../freshforge-benchmark-p16-delegated`
- benchmark record:
  `templates/benchmarks/freshforge_p16_phase_ab_benchmark.json`

## Iteration Policy

The direct-supervisor lane runs first. The supervisor performs the actual
FreshForge P16 implementation in the direct lane and records:

- files changed;
- commands run;
- verification results;
- GitHub issue or PR URLs touched;
- blockers or rework;
- paid supervisor token usage when available from Codex goal/report evidence.

The delegated lane runs later from the same recorded start commit using Agent
Workbench graph/delegation surfaces. It should not merely replay the direct lane
by hand.

## Current Iteration

Iteration 1 starts the direct-supervisor FreshForge P16 baseline. The goal is to
produce substantive FreshForge code, docs, tests, or a precise blocker before
returning to the maintainer for review.

P50 should not close after Iteration 1.
