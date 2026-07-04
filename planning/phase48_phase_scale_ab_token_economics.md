# Phase 48 Phase-Scale A/B Token Economics

## Purpose

P48 starts the actual measurement game: compare a full paid-supervisor phase
implementation against a graph-backed delegated implementation of the same
FreshForge phase target.

The benchmark target is FreshForge P16: provider result and validation evidence
conventions.

## Experimental Design

Use two isolated worktrees from the same FreshForge start commit:

- direct lane: `benchmark/p16-direct-supervisor`;
- delegated lane: `benchmark/p16-agent-workbench-delegated`.

Do not use a simple stash/rollback as the primary design. Stash-based rollback
does not isolate GitHub issue state, generated caches, branch history, or
review artifacts. Disposable worktrees are cleaner and make the start commit
auditable.

## Measurement Boundary

The main cost signal is paid supervisor token cost.

Measure:

- supervisor input tokens;
- supervisor output tokens;
- worker input tokens;
- worker output tokens;
- token price assumptions;
- validation outcome;
- cleanup/rework burden; and
- whether the delegated lane changed the final implementation decision.

Worker tokens may be priced at zero cash when using local Ollama, but they are
still recorded as tokens so the workflow can later compare capacity, latency,
and reliability.

## Benchmark Record

The first benchmark packet is:

`templates/benchmarks/freshforge_p16_phase_ab_benchmark.json`

It records:

- target repo and FreshForge phase;
- exact FreshForge start commit;
- direct supervisor lane;
- delegated graph lane;
- validation commands;
- token price assumptions; and
- win/loss decision rules.

## Execution Boundary

P48 creates the benchmark protocol and packet. It does not run the FreshForge
P16 benchmark itself.

The next phase should run the direct supervisor baseline first, record actual
token usage from the Codex goal completion report, then reset to the same
FreshForge commit in a second worktree and run the delegated lane using Agent
Workbench graph packets.
