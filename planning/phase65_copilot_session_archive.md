# Phase 65 Copilot Session Archive

## Purpose

P65 promotes a lesson from the FEMIC P108 delegation pilot into Agent
Workbench: every Copilot-backed delegation run should preserve the behavior
trace that connects a ticket to the agent behavior it produced.

The useful research datapoint is not only the final repo diff or result report.
For tuning delegation workflows, the durable evidence unit is:

1. the coordinator ticket;
2. model id and permission mode;
3. raw Copilot chat/session behavior stream;
4. tool requests and execution outcomes;
5. user or coordinator nudges;
6. final artifacts;
7. result report; and
8. paid-coordinator token/cash ledger.

## Initial Scope

P65 adds a local archive command:

```text
agent-workbench copilot archive --workspace-root <repo> --output-dir <runtime-dir>
```

The command:

- resolves the VS Code workspace storage directory from `workspace.json`;
- finds matching `chatSessions/*.jsonl` and
  `GitHub.copilot-chat/transcripts/*.jsonl`;
- matches sessions by exact session id, run id, prompt marker, or latest
  matching workspace session;
- copies raw logs into ignored runtime storage;
- writes a sanitized manifest with event counts, model ids, permission levels,
  user/assistant/tool counts, nudge snippets, and tool-request snippets; and
- fails closed when no matching session is found.

## Boundaries

This phase does not implement live monitoring, automatic mid-job nudges, or a
Copilot Chat UI controller. Those require a later controller phase. P65 only
makes post-run archival systematic and repeatable.

Raw chat logs must remain ignored runtime evidence. The tracked project should
promote only sanitized manifests or public-safe analysis notes.

## Follow-On Direction

A later task-level delegation controller should use the same archive evidence
to learn:

- where local supervisors stall;
- which prompts trigger summary loops;
- how often Windows shell mistakes occur;
- how many nudges are required per task type;
- whether one-child-task tickets reduce stall and repair burden; and
- which model/permission combinations produce acceptable behavior.
