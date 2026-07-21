# P107.3 repaired C0 evaluation block

## Decision

The prior C0 attempt, `p107_3_c0_20260719_160000`, is retained as an invalid
observation. Its frozen `p107-provenance-audit-bundle-v1` workload was already
implemented at the starting commit and therefore produced no implementation
change. It supplies no C0 baseline and no economics result.

The repaired block starts at root commit
`3b0d44db316dea73468c30cc399e6e87f6581930` with one new, observable workload:
`p107-source-audit-output-projection-v1`.

## Frozen workload to materialize

Add a deterministic output projection to `agent-workbench source-audit`:

```text
agent-workbench source-audit ... --output-mode full|summary
```

- `full` is the default and preserves the current complete result shape.
- `summary` preserves the schema version, aggregate counts, per-input identity,
  per-input counts, provenance status, and findings, but omits raw per-record
  payloads from the rendered result.
- The selected projection applies identically to stdout and `--output`.
- An unknown output mode is a configuration error with exit code `2`.
- Projection ordering and JSON serialization remain deterministic.

This is useful generic workflow work: a Coordinator can retain actionable
provenance failures and aggregate audit evidence without emitting the complete
source-anchored record payload to every downstream review surface.

Allowed implementation paths are limited to:

- `src/agent_workbench/source_audit.py`
- `src/agent_workbench/cli.py`
- `tests/test_source_audit.py`
- `README.md`

## Pre-implementation proof and freeze procedure

Before a C0 run worktree is created, the root coordinator must materialize the
ticket, independent acceptance fixture, workload contract, evaluation block,
and all copied inputs under one ignored run directory. The block records the
start commit above and SHA-256 values for every frozen input.

The materialization preflight must prove all of the following against that
commit:

- `source-audit` has no `--output-mode` CLI argument;
- `source_audit.py` has no output-projection implementation; and
- the focused test suite contains no output-projection test.

If any condition is false, discard the block before a session or worktree is
created and select another new workload. No historical detached worktree or
archived branch is a substitute starting state.

The independent fixture must exercise full-mode compatibility, summary-mode
record omission, preserved counts and findings, deterministic output, output
file parity, and invalid-mode exit semantics. It is frozen before the C0
Coordinator starts and is outside the allowed implementation paths.

## C0 execution contract

C0 uses one fresh Terra/Medium Coordinator to implement the workload in one
announced, literal test-run worktree. It spawns no Worker or Supervisor. One
fresh read-only Advisor is `gpt-5.6-sol` at `medium` reasoning and receives
only the immutable inline review packet. The Coordinator hard-waits for a
schema-valid verdict and reuses that Advisor only through `send_input` for
review deltas.

The run record must report separate `quality_validated_candidate`,
`protocol_accepted_candidate`, and `economics_usable` verdicts. A result is an
eligible C0 only when deterministic acceptance, an accepted Advisor verdict,
uncontaminated provenance, and complete session-bound accounting all hold.

No C1-C4 worktree is named or created by this block.
