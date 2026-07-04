# Phase 8 SDK Same-Ticket Evaluation Notes

## Purpose

Phase 8 promotes the successful Phase 7 one-off Copilot SDK/Ollama probe into a
repeatable local evaluation harness. The goal is not to create a benchmark
product. The goal is to make the next worker-model comparison boring enough to
repeat: same ticket, same configured provider, explicit model names, repeated
runs, and a compact supervisor summary.

## Local Manifest Protocol

The tracked template is `templates/sdk_eval_manifest.json`. Real manifests stay
under ignored runtime paths because they may reference local provider endpoint
files, provider header files, SDK source checkouts, and raw output directories.

Minimum fields:

- `evaluation_id`: short local identifier for the trial.
- `ticket`: ignored ticket file sent unchanged to every model/repeat.
- `expected_marker`: exact marker used for no-tool stop-condition checks.
- `models`: configured Ollama model names to compare.
- `repeats`: number of repeats per model.
- `output_dir`: ignored result directory.
- `base_url_file` or `base_url`: provider endpoint input.
- `provider_headers_file`: optional ignored provider headers input.

The default P8 trial uses the same no-tool marker boundary as Phase 7 because it
is the smallest useful stability check. Richer docs-editing tickets should wait
until the repeated no-tool harness is stable.

## Harness Behavior

`scripts/sdk_same_ticket_eval.py` reads the manifest and shells out to
`scripts/copilot_sdk_ollama_probe.py` for each model/repeat pair. Reusing the
existing probe keeps SDK session creation, provider configuration, event
capture, and result writing in one place.

The runner supports:

- `--dry-run`: print redacted planned probe commands without contacting the
  provider.
- `--summary-only`: summarize existing result files without rerunning probes.

Raw per-run probe results and summaries are written under the manifest's ignored
`output_dir`.

## Summary Classifications

The P8 summarizer reads ignored probe result files and assigns one primary
classification per run:

- `exact-marker`: assistant output exactly equals the expected marker.
- `duplicate-marker`: expected marker appears more than once.
- `extra-output`: expected marker appears once with surrounding text.
- `missing-marker`: completed run did not include the expected marker.
- `timeout`: probe timed out waiting for `session.idle`.
- `model-call-failure`: provider/model call failure event was observed.
- `sdk-runtime-error`: SDK runtime raised an exception.
- `loop-like-repetition`: simple repeated-line or low-diversity text signal.
- `missing-result-file`: expected ignored result file was not present.

These classifications are not a full model-quality score. They are a
supervisor-friendly prefilter for deciding which runs deserve rubric scoring.

## First P8 Trial

The first P8 trial uses:

- `qwen3-coder:latest`
- `qwen3-coder-next:latest`
- two repeats per model
- an ignored no-tool ticket requiring exactly one marker line

Sanitized findings will be recorded here after the local trial runs.

### Result

The first P8 trial completed successfully through the Copilot SDK/Ollama probe
path.

Run shape:

- ticket: ignored no-tool marker ticket under `runtime/agent_jobs/`
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
| `qwen3-coder:latest` | 2 | `exact-marker` for both runs |
| `qwen3-coder-next:latest` | 2 | `exact-marker` for both runs |

Interpretation:

- The P8 harness can execute repeated same-ticket SDK/Ollama probes.
- The no-tool marker boundary was stable for both tested models in this small
  sample.
- This does not prove either model is better for repo-editing tasks. It proves
  the harness can now generate repeatable evidence for the next, richer ticket.

Recommended next tranche:

- Use the P8 harness on a tiny documentation-only ticket with allowed file
  boundaries and exact expected result evidence.
- Keep repeats small until failure classification and summary review remain
  reliable on nontrivial tickets.
