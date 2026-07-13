# Honeycomb single-level delegation

The current tactical default is a one-level Coordinator hub:

```text
                         [Supervisor]

                [Worker]             [Worker]

                      [Coordinator]

                [Worker]             [Worker]

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
- Supervisor: `gpt-5.6-luna`, `low` reasoning effort.
- Worker: task-selected; use `qwen3.6:35b-a3b-bf16` or another configured
  Ollama model for zero paid-token-cost grind work, or GPT-5.6 Luna when paid
  speed/reliability is preferable.
- Advisor: selective review and strategic planning, not a routine execution
  node.

The existing `responses_nested_tree`, `codex_native_handoff`, and `copilot_sdk`
transport names remain unchanged. This is a role/topology policy layered over
those transports, not a claim that every transport provides recursive nesting.
