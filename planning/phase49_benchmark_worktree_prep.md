# Phase 49 Benchmark Worktree Preparation

P49 makes the P48 benchmark packet operational enough to start the first real
phase-scale A/B test. The purpose is not to implement FreshForge P16 yet; the
purpose is to create the isolated lane checkouts where the direct-supervisor
and delegated-graph implementations can be run from the same start commit.

## Benchmark Target

The current benchmark target remains FreshForge P16: provider result and
validation evidence conventions. The benchmark packet is:

`templates/benchmarks/freshforge_p16_phase_ab_benchmark.json`

That packet records the FreshForge start commit, lane branch names, lane
worktree paths, token accounting fields, validation commands, and decision
rules.

## Worktree Strategy

P49 uses Git worktrees instead of stash-based rollback.

The direct lane is prepared at:

`../freshforge-benchmark-p16-direct`

The delegated lane is prepared at:

`../freshforge-benchmark-p16-delegated`

Both lane branches are created from the benchmark record's `start_commit`.
This makes the later comparison easier to audit because both runs begin from
the same FreshForge tree state without requiring destructive local rollback.

## Command

Dry-run:

```powershell
python -m agent_workbench benchmark prepare-worktrees --input templates/benchmarks/freshforge_p16_phase_ab_benchmark.json --project-root ../freshforge --dry-run
```

Execute:

```powershell
python -m agent_workbench benchmark prepare-worktrees --input templates/benchmarks/freshforge_p16_phase_ab_benchmark.json --project-root ../freshforge --output runtime/benchmarks/freshforge_p16_worktree_prep.md
```

The command validates the benchmark record first, checks that the target
project is a Git checkout, verifies that the recorded start commit is present,
and then creates missing lane worktrees. Existing worktrees are reported and
left unchanged.

## Supervisor Boundary

P49 still does not spend the direct implementation baseline. The next phase can
start the direct-supervisor lane inside `../freshforge-benchmark-p16-direct`,
record the paid supervisor token usage for the full phase, and preserve the
result for comparison against the delegated lane.

FreshForge `main` must remain clean throughout P49.
