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

This is accepted evidence for direct single-level role provenance only. It does
not establish recursive Supervisor-to-Worker spawning or change the historical
P106 gate and economics contract.
