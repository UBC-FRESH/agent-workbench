# Phase 9 Structured Documentation-Output Trial Notes

## Purpose

Phase 9 tests whether configured Ollama worker models can produce a bounded,
parseable Markdown work product through the Copilot SDK harness without tools,
commands, or file mutation.

This is deliberately one step harder than the P8 exact-marker probe but still
well short of file editing. The supervisor should learn whether workers can
follow an output contract before testing patch proposals or restricted tool use.

## Output Contract

The P9 ticket requires exactly these sections:

- `## Summary`
- `## Observations`
- `## Decision`

The local manifest can set:

- `required_sections`
- `forbidden_phrases`
- `allow_unexpected_sections`
- `allow_preamble`

The summary classifier can report:

- `structured-output`
- `missing-section`
- `extra-prose`
- `refusal-or-forbidden-phrase`
- `loop-like-repetition`
- existing P8 blocker classifications such as `timeout`,
  `model-call-failure`, and `sdk-runtime-error`

## Rubric Mapping

Structured-output classifications map into the worker model rubric as follows:

| Classification | Usual decision | Rubric impact |
| --- | --- | --- |
| `structured-output` | `accepted` | High task-boundary and stop-condition scores if content is coherent. |
| `missing-section` | `retry` | Lower task-boundary and evidence-quality scores. |
| `extra-prose` | `retry` | Lower stop-condition score; reject if extra content changes scope. |
| `refusal-or-forbidden-phrase` | `retry` or `blocked` | Lower task-boundary score; blocked if caused by external policy/runtime limits. |
| `loop-like-repetition` | `reject` | Low recovery and stop-condition scores. |
| `timeout` | `blocked` | External or model-runtime blocker. |
| `model-call-failure` | `blocked` | Provider/model call blocker. |
| `sdk-runtime-error` | `blocked` | Local SDK/runtime blocker. |

## First Trial

The first P9 trial will use:

- `qwen3-coder:latest`
- `qwen3-coder-next:latest`
- two repeats per model
- an ignored structured-output ticket under `runtime/agent_jobs/`
- ignored provider inputs and ignored raw result files

Sanitized findings will be recorded here after the trial.

### Result

The first P9 structured-output trial completed successfully through the
Copilot SDK/Ollama harness.

Run shape:

- ticket: ignored structured documentation-output ticket under
  `runtime/agent_jobs/`
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
| `qwen3-coder:latest` | 2 | `structured-output` for both runs |
| `qwen3-coder-next:latest` | 2 | `structured-output` for both runs |

All four runs included the required `## Summary`, `## Observations`, and
`## Decision` sections. The summary recorded no missing sections, no unexpected
sections, and no preamble for the four inspected runs.

Interpretation:

- Both tested models can satisfy a small structured Markdown response contract
  through the SDK harness.
- This supports proceeding to P10 patch-proposal trials, where the worker will
  still avoid file mutation but will produce a more constrained proposed edit.
- The P9 sample is intentionally small and should not be treated as a broad
  model-quality benchmark.
