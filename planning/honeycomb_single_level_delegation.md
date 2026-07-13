# Honeycomb delegation

The Coordinator may use the runtime topology that best serves the active
objective. This diagram is a useful pattern, not a cap or required reporting
line:

```text
                         [Supervisor]
                              |

                [Worker] \    |    / [Worker]
                          \   |   /
                           \  |  /

                      [Coordinator]

                           /  |  \
                          /   |   \
                [Worker] /    |    \ [Worker]
                              |

                          [Advisor]
```

The outer seats are Coordinator subagents. Their labels, count, and depth are
assigned per objective; the diagram shows one useful mix, not a fixed topology.

Operationally, the Coordinator is the authority. It chooses task decomposition,
concurrency, delegation shape, review cadence, and repairs from the runtime
capabilities that are actually observed. A Supervisor may recommend Worker
work; the Coordinator decides whether and how to execute it. The evidence must
describe the topology that actually occurred rather than treating this diagram
as proof.

Default role configuration:

- Coordinator: `gpt-5.6-terra`, `medium` reasoning effort.
- Supervisor: `gpt-5.6-luna`, `medium` reasoning effort.
- Worker: task-selected; use `qwen3.6:35b-a3b-bf16` or another configured
  Ollama model for zero paid-token-cost grind work, or GPT-5.6 Luna when paid
  speed/reliability is preferable.
- Advisor: selective review and strategic planning, not a routine execution
  node.

## Within-session persistence

Keep the named Supervisor and Advisor threads persistent for the duration of a
Coordinator session by default. Their accumulated context is useful: the
Supervisor can retain the task graph, prior Worker results, recurring defects,
and acceptance history; the Advisor can retain strategic intent, decisions,
and unresolved tradeoffs. The Coordinator should reuse those threads with
follow-up messages rather than spawn a fresh replacement for every turn.

Workers are different: use short-lived, ticket-bounded Worker threads unless a
particular batch benefits from a documented persistent Worker host. Closing a
completed Worker prevents irrelevant task context from contaminating later
work.

Restart a persistent Supervisor or Advisor only when inspected evidence shows
context rot or a broken session, for example repeated confusion about the
current task boundary, stale assumptions that survive correction, irrelevant
tool activity, degraded adherence to the result contract, or an unrecoverable
transport/session error. Before replacement, write a compact ignored handoff
that states the current objective, accepted evidence, open decisions, active
Workers, and exact next action. The Coordinator then closes the stale thread,
spawns one replacement in the same role, and supplies that handoff; it does
not silently treat the replacement as if it retained the old context.

The existing `responses_nested_tree`, `codex_native_handoff`, and `copilot_sdk`
transport names remain unchanged. This is a role/topology policy layered over
those transports, not a claim that every transport provides recursive nesting.

## Fresh-session native role-provenance acceptance

On 2026-07-13, a fresh VS Code Codex session proved direct, single-level native
fan-out to the configured named roles. This supersedes the earlier launcher
probe as the current role-provenance result. The earlier
`run_native_honeycomb_proof.ps1` attempt remains useful negative evidence: its
fresh Terra execution emitted no native spawn event. It is not equivalent to
the successful interactive native subagent invocation described here.

The accepted run used these observed host and configuration conditions:

- workspace: `agent-workbench` on `sandbox/open-coordinator-lab`;
- originator: VS Code Codex;
- Codex CLI version: `0.144.0-alpha.4`;
- a newly started Codex chat after the user-local configuration loaded;
- `default_permissions = ":workspace"` in `~/.codex/config.toml` because the
  configuration defines a custom permission profile;
- named user-local roles registered for `gpt_luna_supervisor`,
  `gpt_sol_advisor`, and `ollama_worker`;
- an OpenAI-compatible Ollama provider using the Responses wire API and a base
  URL ending in `/v1`;
- provider credential values supplied only through the private local launch
  environment/header file, with the credential variables excluded from child
  shell environments; and
- the Ollama Worker permission profile denying access to the private provider
  header file.

The effective role bindings observed in native child rollout evidence were:

| Role | Provider | Model | Reasoning | Permissions |
| --- | --- | --- | --- | --- |
| `gpt_luna_supervisor` | `openai` | `gpt-5.6-luna` | `medium` | read-only role configuration |
| `gpt_sol_advisor` | `openai` | `gpt-5.6-sol` | `high` | read-only role configuration |
| `ollama_worker` | `agent_workbench_ollama` | `qwen3.6:35b-a3b-bf16` | `low` | `agent_workbench_ollama_readonly` |

The Coordinator used the native subagent interface directly. It did not use a
generic background-chat agent, shell-launched Codex process, proof wrapper, or
model override. It launched one `gpt_luna_supervisor`, one `gpt_sol_advisor`,
and two distinct `ollama_worker` children. Each received a unique, one-line,
no-tool marker task.

The accepted native evidence unit for every child required all of the
following:

1. a nonempty native child thread ID and the expected parent thread ID;
2. `session_meta` identifying the requested and effective named role plus the
   model provider;
3. `turn_context` identifying the effective model and reasoning effort;
4. an exact marker response; and
5. a terminal native `task_complete` event.

The accepted parent thread was
`019f5d14-1d4b-7f02-916d-994d9584a1f5`. Its direct children were:

- `019f5d14-6fd1-7061-a97b-01e05d8244a3`:
  `gpt_luna_supervisor`, `openai`, `gpt-5.6-luna`, `medium`;
- `019f5d14-8a8e-7c73-bcd3-61d31959dd42`:
  `gpt_sol_advisor`, `openai`, `gpt-5.6-sol`, `high`;
- `019f5d14-b51d-7fd0-901a-639aa8e13d09`:
  `ollama_worker`, `agent_workbench_ollama`,
  `qwen3.6:35b-a3b-bf16`, `low`; and
- `019f5d14-cf33-79b0-aa3e-c32f56e9d103`:
  `ollama_worker`, `agent_workbench_ollama`,
  `qwen3.6:35b-a3b-bf16`, `low`.

Reproduction checklist:

1. Load the private provider environment before starting the Codex host. Keep
   the endpoint, credential values, and raw provider evidence out of tracked
   files and GitHub.
2. Confirm the provider URL supplied to the SDK ends in `/v1` and the provider
   uses `wire_api = "responses"`.
3. Validate configuration loading with
   `codex debug prompt-input "configuration load diagnostic"` and
   `codex doctor --json`.
4. Start a fresh Codex chat in the `agent-workbench` workspace after any role or
   provider configuration change.
5. Invoke the exact named roles through the native subagent interface without a
   model override, assigning distinct no-tool marker tasks.
6. Inspect each child rollout JSONL under the user-local Codex session store for
   the required `session_meta`, `turn_context`, marker, and `task_complete`
   evidence. Configuration files or spawn prose alone are not acceptance.
7. Store raw session/provider material only under ignored local paths. Preserve
   a sanitized result and verdict under
   `runtime/agent_jobs/honeycomb-native-fresh-session/`.

This acceptance proves direct single-level named-role selection and remote
Ollama execution from a fresh native Codex session. It does not prove recursive
Supervisor-to-Worker spawning, tracked-file mutation authority, benchmark
quality, or usable Coordinator economics.
