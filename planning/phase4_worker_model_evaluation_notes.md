# Phase 4 Worker Model Evaluation Notes

## Purpose

Phase 4 defines how Agent Workbench scores local Ollama-backed worker models on
bounded coding-agent tasks. The phase is rubric-first, with one small A/B dry
run used to check whether the scoring surface captures useful behavior
differences.

## Current Installed Model Inventory

The current worker host inventory was user-provided from `ollama list` after
installing `qwen3-coder-next:latest`.

| Model tag | Model ID | Size | Inventory note |
| --- | --- | --- | --- |
| `qwen3-coder-next:latest` | `ca06e9e4087c` | 51 GB | Newly installed for P4 A/B testing. |
| `qwen3-coder:latest` | `06c1097efce0` | 18 GB | Existing Phase 3 worker baseline. |
| `llama3.1:latest` | `46e0c10c039e` | 4.9 GB | Installed general baseline; not primary P4 target. |
| `starcoder2:latest` | `9f4ae0aff61e` | 1.7 GB | Installed small code baseline; not primary P4 target. |
| `nomic-embed-text:latest` | `0a109f422b47` | 274 MB | Embedding model; not a worker-chat target. |

Before any worker ticket assigns a model, the active host inventory should be
rechecked with:

```bash
ollama list
```

## P4 Evaluation Pair

The first comparison pair is:

- `qwen3-coder:latest`
- `qwen3-coder-next:latest`

This pair is intentionally narrow. Both models are from the same family, so the
first question is not "which local model is best?" The first question is:

> Does the newer Qwen coding model follow the same strict worker ticket more
> reliably, and does the rubric make that visible?

## A/B Ticket Requirements

The P4 ticket should:

- use one unique marker per model run;
- require exactly one short terminal command;
- require exactly one ignored result file;
- forbid tracked-file edits;
- forbid GitHub operations;
- require the worker to report the observed model tag in the result file;
- require the bridge supervisor report to prove the resolved model; and
- stop at the first blocker.

The command should be harmless and deterministic enough for supervisor checks,
but still force one observable terminal action.

## Model Selection Constraint

The local `code chat` command currently exposes `--mode`, `--add-file`,
`--reuse-window`, `--new-window`, `--maximize`, `--profile`, and stdin support.
It does not expose a command-line model-selection flag.

Therefore P4 cannot treat "requested model" as proof. A run counts for model
comparison only when the persisted session evidence reports the expected
resolved model.

If model selection cannot be set reliably from the VS Code UI before a run, the
comparison must be recorded as blocked rather than inferred from the prompt.

## Scoring Plan

For each run:

1. Launch the same ticket through `scripts/copilot_chat_bridge.py`.
2. Inspect the generated supervisor report.
3. Confirm the observed model tag.
4. Fill `templates/model_eval_result.md`.
5. Apply `rubrics/worker_model_evaluation.md`.
6. Record whether the result is `accepted`, `retry`, `blocked`, or `reject`.

For the A/B comparison:

- compare category scores;
- list failure modes;
- note command/file deviations;
- note evidence gaps;
- avoid broad model-ranking claims from a single run; and
- decide whether the rubric was useful enough to support repeated P5 runs.

## Initial Findings

- Phase 3 already proved that duplicate command execution matters. A worker can
  complete the requested file output while still violating command discipline.
- Model-comparison claims require observed `resolvedModel` evidence from the
  session artifact.
- The P4 scoring dry run is recorded in
  `planning/phase4_ab_scoring_results.md`.
- The attempted `qwen3-coder-next:latest` run resolved to
  `qwen3-coder:latest`, so the qwen3-coder-next comparison is blocked until a
  reliable model-switching procedure is verified.
- The same observed `qwen3-coder:latest` model produced different command
  discipline outcomes across tiny runs, which supports repeated-run evaluation
  in a later phase.
