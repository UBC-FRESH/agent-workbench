# Phase 5 Custom Agent Model Switching Notes

## Purpose

Phase 5 tested whether VS Code workspace custom agents can provide a reliable
model-selection path for Ollama-backed worker evaluations.

The target question was:

> Can `.github/agents/*.agent.md` files pin one worker to
> `qwen3-coder:latest` and another worker to `qwen3-coder-next:latest` so the
> bridge can run repeatable same-ticket model comparisons?

## Implemented Probe

Phase 5 added two workspace custom agents:

- `.github/agents/qwen3-coder-strict-worker.agent.md`
- `.github/agents/qwen3-coder-next-strict-worker.agent.md`

Both agents use narrow worker instructions and `tools: []` for no-tool probes.
The bridge script also gained a `--mode` option so it can call:

```powershell
python scripts\copilot_chat_bridge.py --mode <custom-agent-id> ...
```

## Probe Results

The custom agent mode was loaded successfully. Persisted session state for the
qwen3-coder-next probe showed a custom mode backed by the workspace
`qwen3-coder-next-strict-worker.agent.md` file.

The model pin was not honored for the Ollama provider in this setup. The
decisive post-restart probe used:

- requested custom agent: `qwen3-coder-next-strict-worker`;
- requested model frontmatter: `qwen3-coder-next:latest`;
- active VS Code panel model state set to `ollama-models/Ollama/qwen3-coder-next:latest`;
- no-tool ticket;
- no terminal commands;
- no file writes; and
- bridge parser updated to fall back from `resolvedModel` to `modelId`.

Persisted session evidence still reported:

```text
resolved_model: qwen3-coder:latest
```

Therefore workspace custom agents are useful for custom instructions and tool
restriction, but they do not currently provide a reliable Ollama model-switching
mechanism for Agent Workbench.

## Looping Behavior

No-tool custom-agent probes sometimes produced repeated completion summaries in
the visible Copilot Chat UI after the required marker line had already been
emitted.

The bridge evidence showed no external terminal or file tools in those no-tool
runs. The looping appears to be an interaction between Copilot Chat agent-mode
completion handling and the Ollama-backed worker model, not a normal command or
file mutation loop.

This reinforces the Phase 4 rubric rule that visible worker prose is not enough.
The supervisor must rely on persisted session evidence and explicit stop/loop
failure modes.

## Bridge Findings

- `code chat --mode <custom-agent-id>` can launch a workspace custom agent.
- Custom-agent no-tool sessions may initially produce only transcript evidence;
  the matching `chatSessions/*.jsonl` artifact can appear a few seconds later.
- Some sessions contain `modelId` but not `resolvedModel`. The bridge now falls
  back to `modelId` and normalizes Ollama provider prefixes.
- Plain `ask` mode did not produce a matching persisted session artifact for
  the bridge within the tested timeout.

## Decision

P5 rejects workspace custom-agent model frontmatter as the model-switching path
for local Ollama worker benchmarking in this setup.

Recommended next tranche:

1. Keep VS Code custom agents available for instruction profiles and tool
   restrictions.
2. Do not use them as the source of truth for model selection.
3. Move the repeatable model-comparison path toward a direct Ollama API worker
   harness where the supervisor controls the `model` field explicitly.
4. Keep VS Code Copilot Chat as an optional visible UI experiment, not the
   primary benchmark substrate.
