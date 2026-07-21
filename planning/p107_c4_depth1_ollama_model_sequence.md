# P107 C4 direct Ollama Worker sequence

## Current route

C4 is the canonical direct native route: one Luna/Medium Coordinator delegates
one bounded task to one configured Ollama Worker with `fork_context:false`.
The Coordinator, not a separate Supervisor or Advisor, starts and closes the
P116 run, reviews any meaningful control cue, verifies the delivered diff, and
makes the acceptance decision. The fixed workload is the frozen P107
evidence-dossier implementation task.

## Model order

Each C4+ lane changes only the Worker model after live-inventory confirmation.

1. `qwen3-coder:latest`;
2. `qwen3-coder-next:latest`;
3. `qwen3.6:35b-a3b-bf16`;
4. `qwen3.6:35b-a3b-q8_0`.

Do not add `gpt-oss` to this sequence without a separate declared lane and
fresh inventory evidence.

## Live findings, 2026-07-20

`qwen3-coder:latest` was reached through the native Agent Hub role with the
expected provider and `none` reasoning, but it did not create any P107
implementation. A minimal fresh-worker control reproduced the cause: instead
of emitting a structured native `shell_command`, the model returned the
Qwen3-Coder custom XML tool-call text as ordinary assistant output and then
completed. No tool was invoked.

This is not evidence that the frozen task or P116 control layer is broken.
Qwen3-Coder's XML tool-call format requires provider-side parsing and
normalization into Responses function-call events. Existing P114 adapter work
proves host-side handling of structured synthetic events, but does not yet
normalize live Qwen XML. Treat that adapter repair as a separate technical
lane; do not retry the unchanged Qwen Coder role for C4 implementation.

The next C4+ candidate is `qwen3-coder-next:latest`, subject to the same
fresh-session, exact-model, one-Worker, Coordinator-owned-P116 boundary.

## Accepted C4+ lane: Qwen 3.6 27B

The fresh `qwen3.6:27b` Worker at medium reasoning completed the frozen
evidence-dossier implementation through the direct Luna Coordinator route.
Independent verification confirmed the exact Worker model, `37` focused tests,
immutable-fixture CLI acceptance, and a clean diff check. The Coordinator-owned
P116 run bound and closed around the one Worker with no Advisor or Supervisor.

The outer `supervisor-tokens` module recorded a qualified bounded Luna
Coordinator estimate of `$0.231600`; the local Worker token volume remains
separate and locally unpriced. This is an accepted C4+ candidate, not evidence
that local workers behave deterministically on unrelated tasks.

## Authorized custom coding variant

`qwen3-blackwell:latest` is a locally prepared, GPU-tuned coding variant of
the accepted Qwen 3.6 27B family. It is a separately declared C4+ model lane:
use the same frozen workload, direct Coordinator-to-one-Worker topology,
medium reasoning setting, and outer economics procedure. Its live inventory
identity must be persisted before any comparison claim.

The first Blackwell attempt is not a model result: after a child transport
failure, the Coordinator incorrectly spawned additional Workers despite the
one-Worker C4 boundary. Direct non-streaming and streaming provider checks
returned HTTP 200 during the incident, so the generic "high demand" child
message is not evidence of external demand or a Blackwell model verdict. A
fresh later lane may retry only after the Coordinator's no-respawn rule is
loaded in a new session.
