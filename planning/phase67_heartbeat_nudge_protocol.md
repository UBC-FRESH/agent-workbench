# Phase 67: Heartbeat And Nudge Protocol

Phase 67 makes delegated-run stalls observable without requiring the paid
coordinator to watch every local-supervisor chat turn.

## Issue And Branch

- Parent issue: #437
- Child issues: #438, #439, #440, #442
- Branch: `feature/p67-heartbeat-nudge-protocol`

Duplicate issue cleanup:

- #441 and #443 were duplicate P67 issues created during a session retry and
  closed as duplicates.
- #444, #445, and #446 were duplicate child issues created during the same
  retry and closed as duplicates.

## Heartbeat Contract

Delegated child-task runs should append JSONL records to:

`runtime/agent_jobs/<run_id>.heartbeat.jsonl`

Required fields:

- `timestamp`
- `checklist_item`
- `status`
- `action`
- `artifact_path`
- `command_summary`
- `next_intended_action`

Allowed status values:

- `thinking`
- `running_command`
- `tool_blocked`
- `no_progress`
- `completed`
- `blocked`

The heartbeat is public-safe metadata. It must not include raw prompts,
provider details, credentials, private endpoints, or personal paths.

## Stale-Run Detection

`agent-workbench heartbeat summarize` reads the JSONL file and emits:

- validation state;
- latest checklist item;
- latest status;
- stale state;
- status counts;
- nudge count;
- stall count;
- recommended nudge type; and
- repeated-nudge stop-rule state.

The coordinator should inspect filesystem and Git state before issuing broad
nudges, but the heartbeat summary narrows the decision.

## Nudge Policy

`agent-workbench nudge suggest` turns a heartbeat summary into one targeted
message. The nudge vocabulary is intentionally small:

- continue next subtask;
- stop summarizing;
- write blocker;
- fix shell context;
- reconcile checklist.

After two failed or stale nudges in the same lane, the default stop rule
requires coordinator review rather than more local-supervisor prompting.

## P108 Carry-Forward

P108 showed that nudges can recover a useful local-supervisor run, but ad hoc
nudges make behavior evidence harder to interpret. P67 keeps nudges cheap,
structured, and countable so later phases can compare task designs and model
roles.
