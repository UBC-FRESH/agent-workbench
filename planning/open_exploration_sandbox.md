# Open exploration sandbox

Branch: `sandbox/open-coordinator-lab`

This branch is an intentionally unphased engineering laboratory. It does not
have a roadmap phase, GitHub parent issue, child issue set, or predetermined
attempt, repair, token, cash, topology, or concurrency limit.

The maintainer directs the Coordinator by objective. The Coordinator exercises
judgment about decomposition, delegation, retries, and evidence collection.
Agent conclusions remain evidence-scoped: prose is not proof, raw provider
details stay ignored, and quality, protocol, and economics claims remain
separate when those claims are made.

Historical phase manifests, budget declarations, loop policies, and stop-rule
templates are opt-in references here; none supplies a default cap unless the
maintainer explicitly adopts it for a particular experiment.

This sandbox does not alter the historical P106 contract on
`feature/p106-matched-roi-benchmark`. Productization, phase activation, GitHub
mutation, provider changes, releases, and phase-closeout claims require a
separate maintainer instruction.

## Native Honeycomb result

The machine-local configuration now registers canonical Terra, Luna, Sol, and
Ollama roles with private provider headers excluded from child shells. The
shell-launched Terra proof remained negative: it completed after an empty
native `wait` call and emitted no child thread. A subsequent fresh VS Code Codex
session then directly invoked the native subagent interface and successfully
launched one configured Luna Supervisor, one Sol Advisor, and two configured
Ollama Workers.

The accepted run captured nonempty child thread IDs, matching requested and
effective roles, expected provider/model/reasoning metadata, exact no-tool
markers, and terminal `task_complete` events. Both Ollama children resolved to
`agent_workbench_ollama` with `qwen3.6:35b-a3b-bf16`. The complete public-safe
reproduction contract is in `planning/honeycomb_single_level_delegation.md`;
the sanitized local evidence is under
`runtime/agent_jobs/honeycomb-native-fresh-session/`.

This is accepted evidence for direct single-level role provenance. The first
follow-on Supervisor-to-Ollama-Worker probe was invalid because
`agents.max_depth` was unset and Codex applied the default of `1`. The Luna
Supervisor was already at depth `1`, so the missing native spawn tool and absent
Worker descendant were expected consequences of configuration, not evidence
that recursive spawning is unsupported.

The corrected fresh-session run used generic `gpt-5.6` at `high` reasoning,
multi-agent v1, `agents.max_depth = 2`, and `fork_context: false` on both
role-bound edges. It created a real Luna Supervisor at depth `1` and a real
`agent_workbench_ollama` Worker at depth `2`. The maintainer navigated into both
child threads in the Codex UI and continued interacting directly with the
nested Worker while observing the corresponding remote GPU activity. The
accepted evidence and deterministic verdict are under
`runtime/agent_jobs/honeycomb-native-depth2-ui-proof/`. This establishes a
usable-adjacent recursive UI proof but does not change the historical P106 gate
or supply usable economics evidence.
