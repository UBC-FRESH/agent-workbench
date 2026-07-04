# Phase 11 Supervisor-Applied Patch Harness Notes

## Purpose

Phase 11 tests the next mutation boundary: the worker still does not edit files,
but the supervisor can apply a proposed patch to an explicitly allowed ignored
sandbox target.

The purpose is to prove the control surface, not to generalize patch
application. The first harness supports a narrow add-only patch proposal so
failure behavior remains easy to inspect.

## Protocol

- Worker outputs remain ignored result files.
- The supervisor names one allowed file path.
- The harness extracts one fenced `diff` or `patch` block.
- The harness rejects missing patches, multiple patch blocks, wrong target
  files, and malformed patches.
- The harness writes only under the supplied ignored sandbox root.
- The harness writes a local Markdown report with status, classification, and
  exact error text.

## First Trial

The first trial will reuse a successful P10 `qwen3-coder-next:latest` patch
proposal result and apply it to an ignored sandbox target. No tracked file will
be edited.

Sanitized findings will be recorded here after the trial.

### Result

The first P11 supervisor-applied patch trial completed successfully.

Run shape:

- source proposal: ignored P10 patch proposal result
- allowed file: `planning/example_worker_note.md`
- sandbox root: ignored runtime sandbox
- report: ignored local Markdown report
- check: expected text must be present after apply

Sanitized outcome:

| Check | Result |
| --- | --- |
| Patch target matched allowed file | pass |
| Patch applied under ignored sandbox root | pass |
| Expected text present after apply | pass |
| Tracked files mutated by apply harness | no |

Interpretation:

- Supervisor-controlled patch application is viable for narrow add-only patch
  proposals.
- The harness should remain conservative until it supports broader unified diff
  semantics and rollback reporting.
- P12 can proceed to a deliberately tiny restricted tool-enabled worker trial,
  but direct worker mutation should remain limited to ignored sandbox targets.
