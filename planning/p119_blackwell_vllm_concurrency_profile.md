# P119 Blackwell vLLM Concurrency Profile

Parent issue: #719

Branch: `feature/p119-vllm-blackwell-concurrency-profile`

## Goal

Promote the reusable, public-safe parts of the local Blackwell vLLM deployment
into Agent Workbench as a packaged playbook for concurrency-capable VS Code
Copilot custom-agent workflows.

## Starting Evidence

A local RTX PRO 6000 Blackwell host successfully served NVIDIA's
`Qwen3.6-27B-NVFP4` checkpoint through vLLM as an OpenAI-compatible Chat
Completions endpoint. The most productive Agent Hub configuration used:

- vLLM native install with model and compile caches outside the repo;
- FlashInfer attention;
- FP8 KV cache;
- prefix caching and chunked prefill;
- MTP speculative decoding;
- Copilot-compatible response shaping by disabling Qwen reasoning-parser output
  and setting the chat template to return normal content fields.

The observed workflow improvement was practical rather than merely benchmark
cosmetic: VS Code Copilot custom-agent sessions could continue across the
swapped backend and run agent-workbench tasks with better responsiveness than
earlier open-model configurations.

## Scope

- Track sanitized launch profiles, helper scripts, and operator documentation
  under `playbooks/vllm_blackwell/`.
- Record the deployment's concurrency implications for Agent Workbench.
- Keep P119 as a packaging and operating-contract phase, not a fresh model
  leaderboard.
- Keep P118 profile-language edits separate if they are being completed in a
  parallel session.

## Out of Scope

- Live endpoint URLs, credentials, Cloudflare tunnel configuration, raw logs,
  transcripts, model blobs, or cache directories.
- Claims that this model is universally best for all tasks.
- A new automated daemon, hosted service, or productized installer.
- Closing or superseding P118 while it is actively being edited elsewhere.

## Concurrency Interpretation

P118 began with a serial-inference assumption because the earlier single-model
deployment saturated GPU memory and lacked demonstrated multi-agent headroom.
The rebuilt FlashInfer/FP8-KV profile changes that operating envelope.

The safe contract is not "fan out freely." It is bounded concurrency:

- permit parallel independent read/diagnostic tasks;
- keep edits and final synthesis centrally coordinated;
- avoid concurrent mutation of the same files;
- reduce fan-out when requests queue, validation output becomes noisy, or
  operator observability degrades.

## Acceptance

- `ROADMAP.md` maps P119 to issue #719 and the feature branch.
- `CHANGE_LOG.md` records the phase start and rationale.
- `playbooks/vllm_blackwell/` contains only sanitized templates and helpers.
- The imported profiles exclude live secrets and publish no provider URL.
- Any P118 agent-profile concurrency language lands through the active P118
  session or a later reconciliation, not by conflicting edits in this branch.

## Validation Record

The sanitized import was checked without modifying `.github/agents/`,
`AGENTS.md`, `planning/p118_fresh_vllm_agent_plan.md`, or other P118-owned
paths. Validation covers:

- `bash -n` across every imported shell helper;
- Python bytecode compilation and `--help` smoke checks for benchmark tools;
- mocked OpenAI-compatible streaming responses for the single and concurrent
  benchmark clients;
- profile loading and dry-run launch argument construction;
- scans for credentials, live provider URLs, private home paths, logs, model
  blobs, caches, and raw transcript artifacts;
- `git diff --check` and focused Ruff checks for the imported Python helpers.

The full repository suite was also attempted in a clean temporary environment
with both `dev` and `graph` extras. It reported 725 passed, 1 skipped, and 21
failures in unrelated existing bridge, supervision, evidence, and Windows-path
tests. Repository-wide pre-commit checks likewise expose pre-existing Ruff
format/lint and mypy debt outside the P119 paths. P119 does not modify those
areas.

Hardware-specific FlashInfer, CUDA, model-loading, and throughput claims remain
observed host evidence rather than repository-local validation.
