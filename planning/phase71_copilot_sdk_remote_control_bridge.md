# Phase 71: Copilot SDK Remote-Control Bridge

Phase 71 parks Agent Workbench P70 and builds the missing control layer for SDK-owned Copilot sessions. FEMIC P108 remains the dogfood target, but P70 does not resume until the bridge can prove same-session create, resume, monitor, and nudge behavior from durable evidence.

## Governing Issues

- Parent phase issue: #466
- P71.1 SDK remote-control contract: #467
- P71.2 SDK session runtime commands: #468
- P71.3 Monitoring, stall detection, and nudge commands: #469
- P71.4 FEMIC P108 dogfood runs: #470
- P71.5 Evidence synthesis and P70 resume decision: #471

## Current Problem

The P70 attempt exposed a control gap. Existing Agent Workbench tooling can generate bounded tickets, archive VS Code Copilot Chat logs, validate heartbeats, suggest nudges, and review result files. It cannot reliably inject a nudge into a specific already-running VS Code Chat session, and transcript archives are evidence artifacts rather than a remote-control API.

The SDK path must therefore own the session lifecycle. A P71 run counts only when the session was created or resumed through the bridge, the bridge captured its own event stream or polling evidence, and any nudge was sent through the same SDK-owned session identity.

## Session Ownership Contract

An SDK-owned session is a session whose stable identifier is recorded in a P71 manifest and whose lifecycle is controlled by the bridge. The bridge may create a new session, resume an existing SDK-owned session, send prompts or directives, capture events, and produce status summaries. A VS Code Chat session discovered from workspace storage is archive evidence only unless it was also created and controlled through the SDK bridge.

Every live run must record:

- a public-safe run id;
- the workspace root as a repo-relative or operator-supplied path;
- the target task and governing issue;
- the SDK session id or resumable session key;
- the prompt, nudge, result, blocker, heartbeat, event-log, and status-summary paths;
- the expected stop condition;
- the supervisor budget or retry limit;
- whether raw events may be kept locally;
- the latest observed state and timestamp.

## Status Vocabulary

- `created`: the bridge created a new SDK-owned session and recorded the session id.
- `resumed`: the bridge reattached to a previously recorded SDK-owned session.
- `prompt_sent`: the initial task directive was sent to the session.
- `monitoring`: the bridge is actively polling or streaming events.
- `active`: recent events show useful work or a requested tool/action sequence.
- `quiet_stall`: no new event or heartbeat arrived within the configured threshold.
- `nonprogress_stall`: events continue, but the summarized state repeats without advancing the checklist or producing new evidence.
- `nudge_sent`: a same-session directive was sent after a stall or supervisor decision.
- `blocked`: the session reported or demonstrated a concrete blocker that needs supervisor action.
- `completion_candidate`: the session claims completion or writes a result file.
- `accepted_candidate`: supervisor verification found the expected artifact or change.
- `rejected_candidate`: supervisor verification found missing, wrong, or unverifiable work.

## P70 And FEMIC P108 Gates

P70 remains parked until P71 produces one of these outcomes:

- bridge-proven path: create or resume an SDK-owned session, monitor it, send at least one same-session directive when needed, and verify the resulting FEMIC P108 artifact or blocker;
- documented blocker: record the exact SDK limitation, exception, or missing API that prevents same-session control, with local evidence paths and a decision about whether to return to VS Code Chat archive-only workflows.

FEMIC P108 dogfood work must not be treated as complete by P71 alone. The bridge can produce candidate repairs or blockers, but coordinator-owned FEMIC verification, commit decisions, PR #303 status, and issue #302 closeout stay outside P71.

## Evidence Rules

- Raw SDK events, chat text, and transcripts stay in ignored local runtime paths.
- Tracked notes may contain sanitized status summaries, command names, path shapes, issue numbers, and verification outcomes.
- A worker prose response is not accepted until the supervisor checks the FEMIC worktree, relevant files, GitHub issue/PR state, or command output.
- Any live retry must cite the previous run id and the precise defect or missing evidence it is trying to repair.

## Implementation Sequence

1. Land this contract and `templates/copilot_sdk_session_manifest.json`.
2. Add manifest validation and fake-SDK unit tests.
3. Add create, resume, send, monitor, and nudge command surfaces.
4. Run one bounded FEMIC P108 dogfood session through the SDK bridge.
5. Summarize whether P70 can resume, needs a narrower bridge repair, or should fall back to archive-only Copilot Chat supervision.
