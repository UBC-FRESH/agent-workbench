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

Ticket A was completed while P70 was parked by the P71 SDK remote-control bridge dogfood run. The SDK-owned session produced a FEMIC `CHANGE_LOG.md` ordering repair, the coordinator verified the diff directly, and the repair was committed to FEMIC PR #303 as `181cb16`.

## P70 Resume After P71

P70 resumes after P71 with SDK-owned sessions as the primary delegation path. New P70 tickets should use ignored `copilot-sdk` manifests, `agent-workbench copilot-sdk start`, `monitor`, `nudge-plan`, and `nudge`, then coordinator-owned verification of the FEMIC or TSA23 instance worktree before any commit or acceptance.

The next active target is Ticket B: reconcile the parent FEMIC P108 roadmap/issue state with the TSA23 instance roadmap completion state. The intended worker scope is to inspect the parent P108 surfaces, inspect `external/femic-tsa23-instance/ROADMAP.md`, propose or apply only the smallest roadmap/status correction, and stop before any parent PR merge or issue closure.

## P70.2 Ticket B Result

Ticket B ran through SDK session `cdba1e8b-5173-4676-bacc-081e18d9eec8` using ignored manifest `runtime/p70_ticket_b_tsa23_instance_roadmap/manifest.json`. The worker inspected FEMIC issue #300, issue #301, the parent P108 roadmap state, and the TSA23 instance roadmap, then updated only `external/femic-tsa23-instance/ROADMAP.md`.

Supervisor verification accepted the candidate after confirming the instance diff marked P108.4 and P108.5 complete, extended the Phase 0 range to P108.2-P108.5, and passed `git diff --check`. The coordinator added an instance changelog note, committed and pushed TSA23 instance commit `282da67`, then updated the parent FEMIC submodule pointer and changelog in PR #303 as commit `b60dbd5`.

The live run exposed one bridge improvement: SDK `working_directory` must be absolute at session creation, but manifests should remain public-safe. The bridge now resolves relative manifest working-directory values at launch time.

Ticket B also exposed an evaluation gap: `run.sdk_events.jsonl` contains the raw `user.message`, `assistant.message`, tool, and permission events, but the file is not readable as a conversation. P70.3 therefore adds `agent-workbench copilot-sdk transcript` to render an ignored Markdown transcript from any SDK session manifest, with raw `system.message` events omitted by default and available through an explicit flag for local review.

The transcript command also supports `--compact-output` for a second, super-compact Markdown view that approximates the default Copilot/Codex chat-window information load: each visible entry shows the user/assistant/tool signal first, while full message and tool payloads remain available in expandable details.
