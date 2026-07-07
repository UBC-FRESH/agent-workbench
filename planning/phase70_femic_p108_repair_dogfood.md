# Phase 70 FEMIC P108 Repair Dogfood

## Activation

Phase 70 is the first real-project dogfood pass for the task-level delegation controller built across P66-P69. The target is FEMIC P108 cleanup, but Agent Workbench remains the coordinator-owned control surface: phase setup, issue creation, branch management, ticket sequencing, acceptance decisions, commits, PR merge, and parent issue closure are not delegated.

GitHub tracker:

- Parent issue: #461
- P70.1 dogfood setup: #462
- P70.2 cleanup ticket set: #463
- P70.3 controller evaluation: #464
- P70.4 scale decision: #465

Branch: `feature/p70-femic-p108-repair-dogfood`

## Operating Boundary

P70 must proceed one bounded P108 cleanup ticket at a time. A delegated run may propose or perform only the child-task scope named in its ticket. The coordinator must verify the FEMIC checkout, GitHub state, and produced artifacts before accepting any result.

Raw tickets, heartbeats, run manifests, archives, and worker outputs stay under ignored runtime paths. Only sanitized evidence summaries and decisions may be promoted into tracked planning notes.

## Budget And Stop Rule

The initial P70.1 setup pass is coordinator-owned and does not launch a local Copilot-backed worker run. Before any Copilot-backed task is launched, the run manifest must state:

- one child-task objective;
- expected model and permission mode;
- heartbeat, result, blocker, archive, and token-ledger paths;
- one allowed repair/retry only when the first run exposes a concrete ticket or environment defect; and
- a hard stop after two unsuccessful attempts in the same ticket lane.

## First Target Selection

P70.1 must audit current FEMIC P108 evidence before choosing the first cleanup ticket. The planned cleanup set remains:

- Ticket A: repair `CHANGE_LOG.md` ordering and encoding damage.
- Ticket B: reconcile parent roadmap versus instance roadmap completion state.
- Ticket C: repair stale P108 supervisor result-report claims.
- Ticket D: verify PR #303 and child issue checklist consistency.
- Ticket E: produce final coordinator review packet.

The first active ticket should be the smallest cleanup action whose success can be verified directly from the current FEMIC checkout and GitHub issue or PR state.

## Acceptance Notes

P70 success is not just whether FEMIC cleanup artifacts improve. The phase must also record whether task-level controller use reduces drift, stale-result claims, repeated nudging, and coordinator repair burden compared with the earlier whole-phase P108 run.

## P70.1 Setup Result

P70.1 selected FEMIC Ticket A as the first bounded dogfood target. Current evidence from the FEMIC checkout and GitHub shows:

- FEMIC is on `feature/p108-tsa23-instance-bootstrap-delegation`.
- FEMIC parent issue #302 and PR #303 are open.
- PR #303 is mergeable with successful checks, but must remain unmerged until coordinator review.
- `CHANGE_LOG.md` has a P108 entry inserted at the top instead of appended last, and the entry contains mojibake in the child issue range.

The first controller-ready artifacts are ignored local files:

- `runtime/agent_jobs/p70_ticket_a_changelog_ordering_ticket.md`
- `runtime/agent_jobs/p70_ticket_a_changelog_ordering_manifest.json`
- `runtime/agent_jobs/p70_ticket_a_changelog_ordering_prompt.md`

The manifest validated with:

```powershell
.\.venv\Scripts\python.exe -m agent_workbench copilot task-validate --manifest runtime\agent_jobs\p70_ticket_a_changelog_ordering_manifest.json
```

The local shell does not currently expose `ollama`, so the Ticket A manifest intentionally uses `ollama/VERIFY_BEFORE_LAUNCH` and the ticket requires live worker-model inventory verification before any Copilot-backed launch.
