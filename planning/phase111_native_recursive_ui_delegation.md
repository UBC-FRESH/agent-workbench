# Phase 111: Native Recursive Codex UI Delegation

Parent issue: #634

Branch: `feature/p111-native-recursive-ui-delegation`

Status: complete — PR #639 merged; parent issue #634 and child issues #635-#638 closed

## Purpose

P111 productizes the first usable-adjacent proof of the original Agent
Workbench concept: a native Codex UI Coordinator delegates to a configured paid
Supervisor, which delegates to a configured remote-Ollama Worker. All three
threads remain visible in the IDE, and the maintainer can navigate into and
interact directly with the nested Worker.

The maintainer explicitly authorized P111 alongside the still-active P106
benchmark lane. P111 proves orchestration capability and operator usability. It
does not satisfy P106 quality, ordering, token-span, or economics gates and does
not authorize P107-P110.

## Accepted topology

| Depth | Thread | Role | Provider | Model | Reasoning |
| --- | --- | --- | --- | --- | --- |
| 0 | `019f5e29-9020-74a3-afed-b248718dac3d` | Coordinator | `openai` | `gpt-5.6` | `high` |
| 1 | `019f5e29-bd4d-75b0-aa5c-5dc0936c5dfd` | `gpt_luna_supervisor` | `openai` | `gpt-5.6-luna` | `medium` |
| 2 | `019f5e29-f28e-7223-aac0-35e81ceffa0e` | `ollama_worker` | `agent_workbench_ollama` | `qwen3.6:35b-a3b-bf16` | `low` |

The Worker session names the Luna Supervisor as its parent. Both role-bound
edges used multi-agent v1, the exact configured `agent_type`,
`fork_context: false`, and no model override. Each child has a terminal
`task_complete` event.

## Interactive usability evidence

The maintainer opened the Supervisor thread from the Coordinator UI, opened the
nested Worker from the Supervisor UI, and continued chatting directly with the
same Worker. Across the inspected archive, the Worker retained its configured
provider and model for five turn contexts, completed three turns, issued ten
shell tool calls during an extended exercise, survived an intentional turn
interruption, and completed cleanup. The maintainer independently observed the
corresponding sustained GPU activity on the configured remote host.

Remote GPU observation is corroboration, not the sole acceptance authority.
Persisted session metadata establishes role, provider, model, depth, parentage,
and terminal state.

## Frozen evidence

Raw rollout copies are ignored under
`runtime/agent_jobs/honeycomb-native-depth2-ui-proof/raw_sessions/`.
They are not suitable for GitHub or tracked documentation.

| Session | Bytes | SHA-256 |
| --- | ---: | --- |
| Coordinator | 120359 | `1364a597b2fd130dae95c140451b39ed60c8fddb338fbba6db6d64813fcdaec7` |
| Supervisor | 135337 | `58d810b0c9c6990aa659e85783b13d974fd78759679b48987671c27dd4da4439` |
| Worker | 260481 | `fe63300dae460561d4623cfbb47852db80e2eac9184310e388800c7aafe9780b` |

`scripts/inspect_native_honeycomb_depth2_proof.py` regenerates the ignored
public-safe verdict. Acceptance requires exact v1 identities, configured roles
and providers, correct depth-1/depth-2 parentage, `fork_context: false`, no model
override, terminal completion, and at least two completed interactive Worker
turns.

The accepted verdict reports recursive protocol and interactive UI usability
as true, economics usability as false, and no deterministic validation errors.
Economics remains false because this proof did not capture a bounded
paid-Coordinator token span with catalog-backed pricing.

## Critical runtime distinction

The accepted Codex build exposed two materially different multi-agent surfaces:

- generic `gpt-5.6` at `high` reasoning exposed role-aware v1, whose spawn
  contract contains `agent_type` and `fork_context`;
- GPT-5.6 Terra and Sol sessions exposed v2, whose `task_name` contract created
  generic OpenAI descendants with `agent_role: null`, even when task labels
  matched configured role names.

The project configuration therefore pins generic `gpt-5.6`, `high`, depth `2`,
and six threads for this reproduction. This is an observed compatibility
contract for Codex CLI `0.144.0-alpha.4`, not a claim that future versions will
retain the v1/v2 distinction.

Full-history forks are incompatible with changing configured roles. The
runtime rejects a spawn that combines a different `agent_type` with inherited
full history. Both accepted edges use `fork_context: false`.

## Privacy and authority boundary

- Provider credentials, header values, endpoint details, and raw transcripts
  remain machine-local and ignored.
- The Worker has no commit, push, GitHub, provider-change, installation,
  release, or phase-completion authority.
- P111 proves a usable orchestration surface, not production reliability,
  benchmark quality, productive mutation policy, or cost advantage.
