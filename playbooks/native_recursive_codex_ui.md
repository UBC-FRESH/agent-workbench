# Native Recursive Codex UI Operator Playbook

Use this playbook to reproduce a visible Coordinator -> Supervisor -> remote
Ollama Worker chain inside the Codex IDE UI.

## Prerequisites

1. Use a fresh Codex chat in the `agent-workbench` workspace.
2. Keep project `.codex/config.toml` at generic `gpt-5.6`, `high` reasoning,
   `agents.max_depth = 2`, and `agents.max_threads = 6`.
3. Keep the tracked project roles under `.codex/agents/`; Codex loads those
   role files for the trusted workspace. Keep provider definitions and
   credentials machine-local.
4. Configure the Ollama provider with environment-backed headers and the
   Responses wire API. Do not put private values in tracked files.
5. Run the Honeycomb configuration validator before the proof.

```powershell
.venv\Scripts\python.exe scripts\validate_honeycomb_native_config.py `
  --codex-home $env:USERPROFILE\.codex `
  --project-config .codex\config.toml
```

## Coordinator prompt

```text
Spawn exactly one gpt_luna_supervisor with fork_context false and no model
override. Instruct that Supervisor to spawn exactly one ollama_worker with
fork_context false and no model override, wait for it, and relay its result.
Do not perform the Worker task in the Coordinator or Supervisor.
```

The important contract is the native `agent_type`, not the thread display name.

## Inspect and steer

1. Expand the Codex subagent activity UI.
2. Open the Luna Supervisor from the Coordinator session.
3. Confirm the Supervisor spawned one nested Worker.
4. Open the Worker from the Supervisor session.
5. Send a bounded follow-up directly to the Worker when interactive behavior is
   under test.
6. Return to parent threads and confirm relayed results when requested.

## Fail-closed acceptance

Do not accept labels, prose, or GPU activity alone. Require persisted evidence
for generic `gpt-5.6`/`high` multi-agent v1 at the root,
`gpt_luna_supervisor`/`gpt-5.6-luna`/`medium` at depth 1, and
`ollama_worker`/`agent_workbench_ollama`/`qwen3.6:35b-a3b-bf16`/`low` at
depth 2. The Worker parent must equal the Supervisor thread ID, both spawns must
use `fork_context: false` without model overrides, and all sessions must reach
terminal completion.

Regenerate the sanitized verdict from the ignored archive with
`scripts/inspect_native_honeycomb_depth2_proof.py`.

## Known failure signatures

`agent_role: null` with `provider: openai` means a generic child was created.
In the accepted build, Terra and Sol roots exposed a v2 `task_name` surface that
could not select configured roles. Start a fresh generic `gpt-5.6`/`high`
session instead.

An error stating that full-history forked agents inherit the parent agent type,
model, and reasoning means a role-bound spawn used inherited history. Set
`fork_context: false` and retry in a fresh bounded proof.

## Cleanup and privacy

- Interrupt intentionally long Worker turns through the UI.
- Verify Worker-started background processes have terminated.
- Store raw rollout copies only under ignored runtime paths.
- Publish only sanitized metadata and deterministic verdicts.
