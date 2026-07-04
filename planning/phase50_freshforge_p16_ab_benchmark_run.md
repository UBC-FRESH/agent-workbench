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
