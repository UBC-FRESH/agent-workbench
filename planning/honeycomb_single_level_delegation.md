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
