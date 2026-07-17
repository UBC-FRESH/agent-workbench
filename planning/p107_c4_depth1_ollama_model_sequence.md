# P107 C4 depth-1 Ollama Worker sequence

## Decision

C4 is a C2 variant, not a C1 variant. The Coordinator directly owns one
Luna/Medium Supervisor, one Ollama Worker, and one Terra/Medium Advisor. The
Supervisor is a planning/review relay and must not spawn. This preserves the
flat depth-1 configuration that has been more stable than nested C3.

## Fixed invariants

- frozen provenance-audit workload, baseline, fixture, and Advisor contract;
- direct Coordinator ownership of Supervisor, Worker, and Advisor;
- literal detached-worktree validation before Advisor review;
- exact returned-agent-ID to session-JSONL resolution and qualified bounded
  paid-role USD accounting; and
- local Worker cost recorded separately from paid-host USD, never assumed zero.

## Model order

Each accepted lane changes only the Ollama Worker model after live inventory
verification.

1. `qwen3-coder:latest` — accepted P107.1 Worker profile and C4 baseline.
2. `qwen3-coder-next:latest` — only with persisted exact-model evidence; older
   custom-agent paths sometimes fell back to `qwen3-coder`.
3. `qwen3.6:35b-a3b-bf16` — prior same-family execution evidence.
4. `qwen3.6:35b-a3b-q8_0` — prior quantization comparison evidence.

Stop the sequence when a lane lacks deterministic acceptance, Advisor
acceptance, exact model evidence, or usable paid-role accounting. Do not turn a
missing model into installation work. `gpt-oss` remains outside this sequence
until fresh inventory and separate authorization exist.
