# Phase 10 Patch Proposal Protocol Notes

## Purpose

Phase 10 tests whether configured Ollama worker models can produce a bounded,
parseable patch proposal without applying it. The mutation boundary remains on
the supervisor side.

This phase is the intermediate lane between P9 structured assistant output and
P11 supervisor-applied patches.

## Patch Proposal Contract

The worker must return:

- `## Rationale`
- `## Patch`
- `## Verification`

The patch must be a fenced `diff` or `patch` block. The local manifest can set:

- `require_patch`
- `allowed_patch_files`
- `required_sections`
- `forbidden_phrases`

The summary classifier can report:

- `patch-proposal`
- `missing-patch`
- `malformed-patch`
- `wrong-file`
- `extra-prose`
- `refusal-or-forbidden-phrase`
- `loop-like-repetition`
- existing runtime blockers

## First Trial

The first P10 trial will ask each worker model to propose a tiny Markdown patch
for an allowed example file path. The file will not be edited by the worker or
by the P10 harness.

Sanitized findings will be recorded here after the trial.

### Result

The first P10 patch-proposal trial completed through the Copilot SDK/Ollama
harness.

Run shape:

- ticket: ignored no-mutation patch-proposal ticket under `runtime/agent_jobs/`
- allowed proposal path: `planning/example_worker_note.md`
- models:
  - `qwen3-coder:latest`
  - `qwen3-coder-next:latest`
- repeats: two per model
- provider inputs: ignored local endpoint/header files
- raw evidence: ignored per-run result files and summary files under
  `runtime/agent_jobs/`

Sanitized outcome:

| Model | Repeats | Classification |
| --- | ---: | --- |
| `qwen3-coder:latest` | 2 | `missing-section` for both runs |
| `qwen3-coder-next:latest` | 2 | `patch-proposal` for both runs |

All four runs proposed the allowed file path. The two `qwen3-coder:latest` runs
included patch blocks but omitted the required `## Verification` section. The
two `qwen3-coder-next:latest` runs included the required sections and patch
block.

Interpretation:

- The patch-proposal classifier is useful: it separated a partial proposal from
  a complete proposal without applying any patch.
- `qwen3-coder-next:latest` was more reliable than `qwen3-coder:latest` on this
  bounded patch-proposal task in this small sample.
- P11 can proceed to supervisor-applied patch handling, but the harness should
  continue treating missing required sections as retry-worthy rather than
  accepted.
