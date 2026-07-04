# Phase 2 VS Code Chat Bridge Notes

## Purpose

Phase 2 documents the first practical bridge between Agent Workbench's
file-based worker protocol and VS Code Chat. The objective is a human-operated
launch pattern, not automated orchestration.

## Local Command Surface

The local command inspection used:

```powershell
code chat --help
```

Observed surface:

- `code chat [options] [prompt]`
- stdin is supported by appending `-`
- `--mode <mode>` supports `ask`, `edit`, `agent`, or a custom mode identifier
- `--add-file <path>` adds context files
- `--reuse-window` uses the last active VS Code window
- `--new-window` opens an empty window
- `--maximize` maximizes the chat session view

## Accepted Bridge Contract

- Use ignored ticket files under `runtime/agent_jobs/`.
- Launch the ticket through `code chat --mode agent`.
- Attach only the files the worker needs with `--add-file`.
- Require the worker to write or report a result using the P1 result template.
- Keep raw transcripts under `tmp/transcripts/` if captured manually.
- Verify all worker claims outside the chat session.

## Dry Run

The Phase 2 dry run was command-surface and file-protocol based. It did not
dispatch a live Copilot or Ollama worker to completion.

Dry-run checks:

1. Confirmed `code chat --help` exposes `--mode agent`, `--add-file`,
   `--reuse-window`, `--new-window`, and stdin via `-`.
2. Confirmed the P1 ticket/result/failure/acceptance templates provide enough
   structure for a chat-launched worker task.
3. Drafted the standard launch pattern in `playbooks/vscode_chat_bridge.md`.
4. Kept response parsing explicitly out of scope.

## Findings

- `code chat` is sufficient for launching a bounded worker prompt into VS Code
  Chat from a saved ticket.
- Response capture is still a manual/UI-side step; the supervisor must verify
  filesystem and GitHub state independently.
- The bridge should start with self-contained documentation tasks before
  attempting repo mutations in external projects.
- P3 can now define a worker model evaluation rubric using this launch pattern
  and the P1 acceptance checklist.
