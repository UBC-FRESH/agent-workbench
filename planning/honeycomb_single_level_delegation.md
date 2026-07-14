# Honeycomb single-level delegation

The current tactical default is a one-level Coordinator hub:

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

The six outer seats are all first-level Coordinator subagents. Their labels
are assigned per task; the diagram shows one useful mix, not fixed reporting
lines between outer agents.

Operationally, the Coordinator is the authority and may keep up to six first-
level subagent threads open. Each Supervisor owns one bounded assignment and
may recommend one or more non-overlapping Worker tasks to the Coordinator. The
Coordinator then decides which Workers to spawn, relays their results, and
requests review or repair. This deliberately approximates deeper delegation
without requiring recursive tool access inside a Supervisor.

Default role configuration:

- Coordinator: `gpt-5.6-terra`, `medium` reasoning effort.
- Supervisor: `gpt-5.6-luna`, `medium` reasoning effort.
- Worker: task-selected; use `qwen3.6:35b-a3b-bf16` or another configured
  Ollama model for zero paid-token-cost grind work, or GPT-5.6 Luna when paid
  speed/reliability is preferable.
- Advisor: selective review and strategic planning, not a routine execution
  node.

## Native recursive profile

When a task specifically requires a visible depth-2 chain in the Codex UI,
use the P111-proven topology instead of the single-level approximation:

```text
Coordinator: generic gpt-5.6, high reasoning
  -> Supervisor: gpt_luna_supervisor, gpt-5.6-luna, medium reasoning
       -> Worker: ollama_worker, qwen3.6:35b-a3b-bf16, low reasoning
```

Both edges use the configured `agent_type`, `fork_context: false`, and no model
override. `ollama_supervisor` is not on the recursive Supervisor allowlist:
two fresh non-counting rehearsals reached the configured Qwen Supervisor at
depth 1 but produced malformed unsupported native calls and no Worker at depth
2. That profile remains available for serial/local analysis or proposal work
that does not require child spawning.

## Within-session persistence

Keep the named Supervisor and Advisor threads persistent for the duration of a
Coordinator session by default. Their accumulated context is useful: the
Supervisor can retain the task graph, prior Worker results, recurring defects,
and acceptance history; the Advisor can retain strategic intent, decisions,
and unresolved tradeoffs. The Coordinator should reuse those threads with
follow-up messages rather than spawn a fresh replacement for every turn.

Workers are different: use short-lived, ticket-bounded Worker threads unless a
particular batch benefits from a documented persistent Worker host. Closing a
completed Worker frees one of the six first-level seats and prevents irrelevant
task context from contaminating the next assignment.

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
