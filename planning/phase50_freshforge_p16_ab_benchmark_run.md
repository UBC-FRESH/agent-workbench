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

Iteration 1 has produced one direct-supervisor FreshForge P16 branch and one
delegated Agent Workbench FreshForge P16 branch from the same start commit. The
phase remains open so the maintainer can inspect the outputs, compare the design
choices, and decide the next iteration.

P50 should not close after Iteration 1.

## Iteration 1 Direct-Lane Evidence

FreshForge direct lane:

- worktree: `../freshforge-benchmark-p16-direct`
- branch: `benchmark/p16-direct-supervisor`
- commit: `0ebf8a2` (`P16 add provider evidence records`)
- FreshForge parent issue: #113
- FreshForge child issues touched: #114, #115, #116, #117

Implemented:

- added `ProviderEvidence` as a generic optional provider-reported evidence
  record;
- added optional evidence tuples to `ProviderRunResult` and `NodeRunResult`;
- threaded provider evidence through `run_workflow(...)`;
- added evidence counts and compact evidence entries to `NodeRunSummary`;
- verified workflow evidence manifests include provider evidence through full
  run records and summaries;
- exported `ProviderEvidence` from the public package surface;
- updated provider and workflow-runner docs;
- updated FreshForge roadmap and changelog for P16 activation.

Verification:

- `python -m pip install -e .[dev]` refreshed the shared editable environment
  for the direct benchmark worktree;
- `python -m pytest tests/test_records.py tests/test_execution.py tests/test_evidence.py`
  passed with 13 tests;
- `python -m pytest` passed with 97 tests;
- `python -m ruff check .` passed;
- `sphinx-build -b html docs _build/html -W` passed;
- `python -m build` passed;
- `python -m twine check dist/*` passed;
- `git diff --check` passed;
- public-safety scan found only existing policy text;
- FreshForge `main` remained clean.

Token accounting note:

- The active Codex goal token counter reported 129,063 tokens after opening P50
  and completing this first direct-lane iteration.
- This is an interim P50 supervisor-token observation, not a final isolated
  direct-lane benchmark score. It includes P50 setup and the first implementation
  pass.

## Iteration 1 Delegated-Lane Evidence

FreshForge delegated lane:

- worktree: `../freshforge-benchmark-p16-delegated`
- branch: `benchmark/p16-agent-workbench-delegated`
- start commit: `5bce95b` (`P15 add durable evidence manifests (#112)`)
- commit: `c781775` (`P16 add delegated provider evidence mapping`)
- FreshForge parent issue: #113
- FreshForge child issues touched: #114, #115, #116, #117

Worker tickets:

- `p16-provider-evidence-review`
  - model: `qwen3-coder-next:latest`
  - classification: `structured-output`
  - input tokens: 2265
  - output tokens: 300
  - useful signal: prefer an optional opaque provider-owned evidence mapping,
    keyed by evidence type or URI, with FreshForge preserving the JSON shape but
    not interpreting domain semantics.
- `p16-fixture-evidence-proposal`
  - model: `qwen3-coder-next:latest`
  - classification: `missing-section`
  - input tokens: 2200
  - output tokens: 332
  - useful signal: proposed fixture-oriented checks for round-trip preservation,
    backward compatibility, and downstream documentation, but missed the
    required `## Verification` section.

Delegated worker-token subtotal:

- worker input tokens: 4465
- worker output tokens: 632
- worker cash cost: zero under the local Ollama lane

Implemented:

- added optional `evidence` mappings to `ProviderRunResult` and
  `NodeRunResult`;
- threaded provider evidence through `run_workflow(...)`;
- added evidence counts and compact evidence mappings to `NodeRunSummary`;
- verified workflow evidence manifests preserve the provider-owned evidence
  mapping;
- updated provider and workflow-runner docs around generic provider-owned
  evidence;
- updated FreshForge roadmap and changelog for the delegated benchmark branch.

Verification:

- `python -m pip install -e .[dev]` refreshed the shared editable environment
  for the delegated benchmark worktree;
- `python -m pytest tests/test_records.py tests/test_execution.py tests/test_evidence.py`
  passed with 12 tests;
- `python -m pytest` passed with 96 tests;
- `python -m ruff check .` passed;
- `sphinx-build -b html docs _build/html -W` passed;
- `python -m build` passed;
- `python -m twine check dist/*` passed;
- `git diff --check` passed;
- public-safety scan found only existing policy text.

Design contrast against the direct lane:

- The direct lane introduced a typed `ProviderEvidence` dataclass and exported
  it from the public package surface.
- The delegated lane followed the strongest worker recommendation more closely:
  keep provider evidence as an opaque JSON-compatible mapping and avoid adding a
  new public record class until downstream usage proves the shape is stable.
- Both lanes reached full FreshForge verification, so the next comparison should
  focus on API quality, downstream ergonomics, migration risk, and paid
  supervisor-token burden rather than pass/fail validation alone.

Token accounting note:

- The active Codex goal token counter reported 278,526 total tokens after the
  delegated implementation was verified and pushed.
- This total is not yet a clean delegated-lane-only score because it includes
  P50 setup, direct-lane implementation, delegated worker orchestration,
  delegated implementation, and this evidence update.
- The immediate instrumentation gap is supervisor-lane token segmentation: P50
  can currently observe the goal-level total, but it cannot yet attribute paid
  supervisor tokens cleanly to direct implementation versus delegated
  orchestration and cleanup.
