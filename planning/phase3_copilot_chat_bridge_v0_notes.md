# Phase 3 Copilot Chat Bridge V0 Notes

## Purpose

Phase 3 turns the Phase 2 playbook into a local-only prototype harness. The
goal is not full orchestration. The goal is enough evidence capture for a
supervisor to launch a bounded VS Code Copilot Chat worker job, find the
persisted session artifact, and compare observed tool use against the ticket.

## Implemented Contract

The prototype helper lives at:

```text
scripts/copilot_chat_bridge.py
```

It accepts:

- an ignored ticket path;
- a unique marker string;
- a workspace root;
- an optional report path;
- timeout and polling controls; and
- an optional `code` command override.

The helper launches:

```powershell
code chat --reuse-window --maximize --mode agent <prompt> -
```

The ticket body is sent through stdin so multiline worker instructions are not
embedded in the shell command line.

## Evidence Capture

The harness searches the local VS Code workspace storage for persisted Copilot
Chat session artifacts containing the unique ticket marker. It inspects both
chat session and transcript-style JSONL locations when present.

The supervisor report extracts and records:

- matching session artifact paths;
- observed resolved model values;
- observed permission-level values;
- terminal command tool calls;
- file-edit tool calls;
- tool names; and
- policy deviations detected by comparing observed evidence against the ticket.

Raw session artifacts and generated reports remain local runtime evidence and
are not tracked.

## Dogfood Trial

The Phase 3 dogfood used a bounded Agent Workbench ticket that required a
worker session to:

1. write one ignored result file under `runtime/agent_jobs/`;
2. run exactly one GUID-producing PowerShell command; and
3. avoid editing tracked files or touching GitHub.

The worker session was visible in VS Code Chat and used the configured Ollama
worker model selection. The harness found the matching persisted session by
marker, observed the terminal command, and confirmed the result file existed.

The supervisor report returned `needs-supervisor-review` because the worker ran
the required terminal command twice. This is a useful v0 result: the bridge did
not trust the worker's prose claim of completion and instead flagged the extra
observed command as a deviation.

## Findings

- `code chat` stdin launch is viable for visible worker sessions.
- On Windows, a Python subprocess may not resolve `code` even when PowerShell
  can. The harness now resolves `code` through `PATH` first and then falls back
  to VS Code's standard per-user `code.cmd` location.
- Persisted VS Code Chat artifacts currently contain enough information for a
  local verifier to inspect model values, permission-level values, terminal
  commands, file-tool calls, and completion state.
- Permission-level evidence should be treated as observed session evidence, not
  a formal VS Code API contract. A session may expose more than one
  permission-level value in its stored state.
- Counting command occurrences matters. A worker that runs the right command
  twice has still deviated from a ticket that allowed it once.
- V0 should stay supervisor-in-the-loop. The bridge can collect evidence and
  flag deviations, but the supervisor still decides whether to accept, retry,
  reject, or block.

## Deferred Work

- Do not automate approval or permission-level changes from the bridge.
- Do not parse natural-language worker responses as authoritative evidence.
- Do not rely on the current JSONL storage shape as a stable public API.
- Defer model comparison and scoring to the next rubric phase.
