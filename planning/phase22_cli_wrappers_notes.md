# Phase 22 CLI Wrapper Notes

Phase 22 makes the package useful by wrapping the first existing
supervisor-owned commands behind the `agent-workbench` entrypoint.

## Commands Added

```text
agent-workbench smoke
agent-workbench eval --manifest <path> [--dry-run] [--summary-only]
```

`agent-workbench smoke` delegates to `scripts/check_command_surfaces.py`.

`agent-workbench eval` delegates to `scripts/sdk_same_ticket_eval.py`.

Both wrappers accept the top-level `--repo-root` option so a supervisor can point
the CLI at an Agent Workbench checkout explicitly when needed. Direct script
usage remains supported.

## Redaction And Provider Boundary

The CLI wrappers do not add provider configuration handling. They reuse the
existing manifest and script behavior. Dry-run redaction still belongs to
`scripts/sdk_same_ticket_eval.py`, and real provider inputs remain in ignored
runtime files.

## Verification

P22 verification includes:

- `agent-workbench smoke`;
- `agent-workbench eval --manifest <ignored-smoke-manifest> --dry-run`;
- direct `python scripts/check_command_surfaces.py`;
- compile checks; and
- public-safety search over tracked files.

## Decision

The CLI wrapper layer is useful enough to keep extending. P23 should add
evidence summary validation and rendering as package-native behavior rather than
another direct script.
