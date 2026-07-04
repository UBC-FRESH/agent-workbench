# Phase 15 Model-Family Expansion Notes

Phase 15 tested the existing no-tool SDK evaluation harness against three
configured non-qwen coding models. The goal was not to rank models broadly, but
to check whether the stable P8-P10 ticket families can expose useful behavioral
differences across model families.

## Selected Models

The P15 trial subset was:

- `codestral:latest`
- `devstral-small-2:latest`
- `deepseek-coder-v2:16b`

These models were selected from the configured Ollama-compatible provider
inventory because they are coding-oriented and smaller than the largest local
models. The qwen models were already covered in earlier phases, so they were
not repeated in this first expansion pass.

Deferred models:

- `gpt-oss:120b` and `gemma4:31b` were deferred because P15 was intended as a
  small-repeat expansion trial, not a large-model throughput test.
- `gpt-oss:20b` remains a reasonable near-term candidate, but P15 prioritized
  three non-qwen coding-oriented models first.
- `llama3.1:latest`, `starcoder2:latest`, and `nomic-embed-text:latest` were
  not selected for this tranche because they are either less relevant to the
  coding-worker ticket families or not a chat/code worker target.

## Ticket Families

P15 reused the existing ignored runtime tickets from earlier phases:

- marker-only no-tool ticket from P8;
- structured documentation-output ticket from P9; and
- proposal-only patch ticket from P10.

Each model was run once per ticket family through the SDK/Ollama harness. Raw
per-run outputs, manifests, endpoints, headers, and assistant messages remain
ignored under `runtime/`.

## Sanitized Results

| Model | Marker | Structured Output | Patch Proposal |
| --- | --- | --- | --- |
| `codestral:latest` | `exact-marker` | `structured-output` | `patch-proposal` |
| `devstral-small-2:latest` | `exact-marker` | `structured-output` | `patch-proposal` |
| `deepseek-coder-v2:16b` | `exact-marker` | `structured-output` | `missing-section` |

The patch-proposal family was the first P15 discriminator. Both
`codestral:latest` and `devstral-small-2:latest` produced valid bounded patch
proposals for the allowed file. `deepseek-coder-v2:16b` proposed the allowed
file but omitted the required `## Verification` section, so the harness
classified the run as `missing-section`.

## Findings

- The existing SDK same-ticket harness can run non-qwen configured models
  without changing the ticket format.
- Marker-only and basic structured-output tickets are too easy to separate the
  selected models in a single-repeat pass.
- Proposal-only patch tickets remain the better small discriminator because
  they require section discipline plus a constrained diff block.
- `codestral:latest` and `devstral-small-2:latest` are reasonable additions to
  the near-term worker shortlist for no-tool proposal work.
- `deepseek-coder-v2:16b` should stay in the trial pool, but results that depend
  on required Markdown sections need supervisor verification or a retry ticket.

## Decision

Keep `codestral:latest` and `devstral-small-2:latest` in the near-term worker
shortlist beside the qwen pair for no-tool marker, structured-output, and patch
proposal trials. Continue treating `deepseek-coder-v2:16b` as experimental for
structured proposal tasks until repeated runs show whether the missing
verification section was a one-off or a stable failure mode.

Do not expand to the largest configured models until the command surface and
evidence schema are more stable.
