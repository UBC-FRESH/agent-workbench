# Agent Workbench Roadmap

This roadmap is the current project plan and issue tracker map. Keep it
synchronized with GitHub issues, planning notes, pull requests, and
`CHANGE_LOG.md`.

## Issue Tracker Map

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P0 Governance and workflow scaffold | #1 | `feature/p0-governance-scaffold` | Complete |
| P1 Worker protocol templates | #7 | `feature/p1-worker-protocol-templates` | Complete |
| P2 VS Code Chat bridge playbook | #13 | `feature/p2-vscode-chat-bridge-playbook` | Complete |
| P3 Copilot Chat Bridge V0 Prototype | #21 | `feature/p3-copilot-chat-bridge-v0` | Complete |
| P4 Worker model evaluation rubric | #28 | `feature/p4-worker-model-evaluation-rubric` | Complete |
| P5 Custom agent model switching spike | #35 | `feature/p5-custom-agent-model-switching` | Complete |

## Phase 0: Governance And Workflow Scaffold

Parent issue: #1

Branch: `feature/p0-governance-scaffold`

Status: complete

Goal: establish Agent Workbench as a public-safe sandbox for supervised
multi-agent development workflows with UBC-FRESH phase/task/subtask discipline.

- [x] P0.1 Agent contract and repo boundaries (#2)
  - [x] Add `AGENTS.md` project purpose and repo state.
  - [x] Add supervisor/worker operating principles.
  - [x] Add safe mutation and evidence-reporting rules.
  - [x] Add file-based job ticket and result-file protocol.
- [x] P0.2 Contributor workflow and roadmap scaffold (#3)
  - [x] Add concise contributor guide.
  - [x] Add roadmap issue tracker map.
  - [x] Add Phase 0 checklist with child issue references.
  - [x] Add initial changelog entries.
- [x] P0.3 Scratch-space, transcript, and public-safety rules (#4)
  - [x] Add ignored local working paths.
  - [x] Add transcript and worker-result handling rules.
  - [x] Add governance-rationale planning note.
  - [x] Confirm no private/raw project transcript content is tracked.
- [x] P0.4 Phase closeout, verification, and PR (#5)
  - [x] Run `git diff --check`.
  - [x] Inspect governance Markdown files.
  - [x] Search for private paths, credentials, raw transcript leakage, and
        project-specific contamination.
  - [x] Comment on and close child issues.
  - [x] Open, merge, and verify PR closeout.

Phase 0 acceptance criteria:

- Governance files are tracked and public-safe.
- `ROADMAP.md`, `CHANGE_LOG.md`, GitHub issues, and PR body agree.
- All Phase 0 child issues are closed or explicitly deferred before parent
  closure.
- Final local checkout is clean on `main`.

## Phase 1: Worker Protocol Templates

Parent issue: #7

Branch: `feature/p1-worker-protocol-templates`

Status: complete

Goal: create reusable Markdown templates for supervisor tickets, worker results,
acceptance checks, and failure reports so worker-agent tasks become bounded,
evidence-driven, and independently verifiable.

- [x] P1.1 Supervisor ticket template (#8)
  - [x] Add `templates/supervisor_ticket.md`.
  - [x] Include current-state and task-boundary sections.
  - [x] Include allowed/forbidden action sections.
  - [x] Include success, failure, and final-response requirements.
- [x] P1.2 Worker result template (#9)
  - [x] Add `templates/worker_result.md`.
  - [x] Include command/file/check/GitHub evidence sections.
  - [x] Include exact blocker/error text section.
  - [x] Include constrained final status values.
- [x] P1.3 Acceptance and verification checklist (#10)
  - [x] Add `templates/acceptance_checklist.md`.
  - [x] Add `templates/failure_report.md`.
  - [x] Include independent verification requirements.
  - [x] Include blocked/retry decision guidance.
- [x] P1.4 Dogfood trial and closeout (#11)
  - [x] Add `planning/phase1_worker_protocol_notes.md`.
  - [x] Perform a manual dry run with a documented equivalent.
  - [x] Record sanitized dogfood findings.
  - [x] Run governance checks and close P1 through PR.

Phase 1 acceptance criteria:

- Worker tickets define current state, task boundary, allowed files and
  commands, stop conditions, success criteria, and required evidence.
- Worker results define commands run, files changed, checks run, GitHub URLs
  touched, blockers/errors, and final status.
- Acceptance requires independent supervisor verification before success is
  claimed.
- Failure reports capture exact command/error text and reject "would have" or
  "ready" as substitutes for completed actions.

## Phase 2: VS Code Chat Bridge Playbook

Parent issue: #13

Branch: `feature/p2-vscode-chat-bridge-playbook`

Status: complete

Goal: document the file-based workflow for launching bounded worker jobs through
VS Code chat using `code chat --mode agent`, without automating response parsing.

- [x] P2.1 Record `code chat` invocation patterns (#14)
  - [x] Add command-surface section to the bridge playbook.
  - [x] Include stdin-based launch pattern.
  - [x] Include file-context launch pattern.
  - [x] Include caveats about UI dispatch and response capture.
- [x] P2.2 Define worker ticket and result-file directory conventions (#15)
  - [x] Document `runtime/agent_jobs/` ticket and result paths.
  - [x] Document `tmp/transcripts/` transcript paths.
  - [x] Document sanitized promotion path into `planning/`.
  - [x] Include filename examples that avoid private or machine-specific paths.
- [x] P2.3 Document supervisor verification after a chat-run candidate (#16)
  - [x] Add supervisor verification section to the bridge playbook.
  - [x] Reference `templates/acceptance_checklist.md`.
  - [x] Define retry/reject/blocked/accepted outcomes.
  - [x] State that worker prose is never sufficient evidence.
- [x] P2.4 Run public-safe bridge dry run and closeout (#17)
  - [x] Add `planning/phase2_vscode_chat_bridge_notes.md`.
  - [x] Record the dry-run command surface and outcome.
  - [x] Run governance checks.
  - [x] Close P2 through PR.

Phase 2 acceptance criteria:

- The playbook explains how to launch a bounded worker prompt through
  `code chat --mode agent --reuse-window` using stdin and optional `--add-file`
  context.
- The playbook explains where ignored worker tickets, worker results, and
  transcripts belong.
- Supervisor verification happens outside Copilot chat and does not trust worker
  prose by itself.
- The dry run proves the command surface and file protocol are usable without
  introducing raw private transcripts or project-specific content.

## Phase 3: Copilot Chat Bridge V0 Prototype

Parent issue: #21

Branch: `feature/p3-copilot-chat-bridge-v0`

Status: complete

Goal: implement a local-only bridge harness that launches bounded VS Code
Copilot Chat worker tickets via stdin, extracts persisted session evidence, and
writes supervisor verification reports.

- [x] P3.1 Bridge launch harness (#22)
  - [x] Add a script-level local helper for stdin ticket dispatch.
  - [x] Accept ticket path, marker, timeout, and workspace root inputs.
  - [x] Launch `code chat --reuse-window --maximize --mode agent` without
        embedding multiline ticket text in the command-line prompt.
  - [x] Keep raw tickets, reports, and transcripts in ignored runtime paths.
- [x] P3.2 Session artifact parser (#23)
  - [x] Locate matching `chatSessions/*.jsonl` artifacts by unique marker.
  - [x] Extract `resolvedModel`, `permissionLevel`, final response, terminal
        tool calls, file tool calls, and tool results.
  - [x] Report missing, incomplete, and timed-out sessions as blocked evidence.
- [x] P3.3 Supervisor verification report (#24)
  - [x] Extract expected commands and allowed output files from the ticket.
  - [x] Compare observed terminal commands and file mutations against the ticket.
  - [x] Flag extra commands, missing commands, missing files, and wrong
        model/permission state.
  - [x] Write an ignored Markdown supervisor report.
- [x] P3.4 Dogfood bridge on one bounded task (#25)
  - [x] Run one local `agent-workbench` worker ticket through the harness.
  - [x] Inspect the generated supervisor report.
  - [x] Record sanitized findings in `planning/phase3_copilot_chat_bridge_v0_notes.md`.
  - [x] Update `playbooks/vscode_chat_bridge.md` with v0 lessons.
- [x] P3.5 Phase closeout, verification, and PR (#26)
  - [x] Run `git diff --check`.
  - [x] Inspect changed Markdown files.
  - [x] Search for credentials, private paths, raw transcript leakage, and
        unrelated project contamination.
  - [x] Comment on and close child issues.
  - [x] Open, merge, and verify PR closeout.

Phase 3 acceptance criteria:

- The bridge can launch a visible Copilot Chat worker session from a stdin
  ticket.
- The bridge can find the matching persisted session artifact by marker.
- The bridge extracts model, permission level, final response, terminal
  commands, file tools, and tool results.
- The verifier distinguishes worker claims from observed tool evidence.
- The verifier flags policy deviations such as extra terminal commands or
  unexpected file mutations.
- Raw tickets, reports, and transcripts remain ignored unless sanitized and
  deliberately promoted into planning notes.

## Phase 4: Worker Model Evaluation Rubric

Parent issue: #28

Branch: `feature/p4-worker-model-evaluation-rubric`

Status: complete

Goal: create a lightweight Markdown rubric for comparing local Ollama-backed
worker models on bounded repo tasks, using P3 bridge evidence rather than
subjective impressions.

- [x] P4.1 Model inventory and run metadata (#29)
  - [x] Track the current installed Ollama model panel.
  - [x] Promote the install shortlist into tracked planning.
  - [x] Define per-run metadata fields.
  - [x] Require `ollama list` verification before assigning models.
- [x] P4.2 Evaluation rubric (#30)
  - [x] Add `rubrics/worker_model_evaluation.md`.
  - [x] Define scoring scale and categories.
  - [x] Define supervisor decision rules.
  - [x] Tie scoring to observed evidence, not worker prose.
- [x] P4.3 Failure-mode taxonomy (#31)
  - [x] Document looping, fake completion, duplicate commands, refusal, and
        over-broad workflow behavior.
  - [x] Include Phase 3 duplicate-command behavior.
  - [x] Map failure modes to scoring and decision consequences.
- [x] P4.4 Evaluation result template (#32)
  - [x] Add `templates/model_eval_result.md`.
  - [x] Include model, ticket, bridge-evidence, score, failure-mode, and
        decision fields.
- [x] P4.5 A/B dry scoring run and closeout (#33)
  - [x] Prepare one fixed evaluation ticket.
  - [x] Attempt or complete qwen3-coder baseline scoring.
  - [x] Attempt or complete qwen3-coder-next scoring.
  - [x] Record comparison findings and caveats.
  - [x] Close P4 through PR.

Phase 4 acceptance criteria:

- The installed-model shortlist and current `ollama list` inventory are
  captured in public-safe planning language.
- The rubric can score observed worker behavior from a P3 supervisor report
  without trusting worker prose alone.
- The failure taxonomy includes observed looping, fake-completion,
  duplicate-command, refusal, and over-broad workflow modes.
- The result template can hold one model run's metadata, evidence, scores,
  decision, and caveats.
- A bounded P4 dry run compares `qwen3-coder:latest` and
  `qwen3-coder-next:latest` on the same ticket, or explicitly records why that
  comparison could not be completed in this phase.

## Phase 5: Custom Agent Model Switching Spike

Parent issue: #35

Branch: `feature/p5-custom-agent-model-switching`

Status: complete

Goal: determine whether VS Code workspace custom agents can provide a reliable,
scriptable model-selection path for Ollama-backed worker evaluations.

- [x] P5.1 Workspace custom agent definitions (#36)
  - [x] Add qwen3-coder worker custom agent.
  - [x] Add qwen3-coder-next worker custom agent.
  - [x] Include model frontmatter fields.
  - [x] Include strict worker-ticket behavior instructions.
- [x] P5.2 Custom-agent launch probe (#37)
  - [x] Prepare ignored probe tickets.
  - [x] Attempt qwen3-coder custom-agent launch.
  - [x] Attempt qwen3-coder-next custom-agent launch.
  - [x] Inspect resolved model evidence.
  - [x] Record blockers or success criteria in planning notes.
- [x] P5.3 Bridge and playbook updates (#38)
  - [x] Add `planning/phase5_custom_agent_model_switching_notes.md`.
  - [x] Update the VS Code chat bridge playbook.
  - [x] Update the bridge parser for custom-mode and model evidence.
  - [x] Keep raw evidence ignored and promote only sanitized findings.
- [x] P5.4 Closeout, PR, and next-step decision (#39)
  - [x] Run `git diff --check`.
  - [x] Inspect changed Markdown files.
  - [x] Search for credentials, private paths, raw transcript leakage, and
        unrelated project contamination.
  - [x] Comment on and close child issues.
  - [x] Open, merge, and verify PR closeout.

Phase 5 acceptance criteria:

- Workspace custom agent files are public-safe and use documented `.agent.md`
  structure.
- A same-ticket probe is attempted for both `qwen3-coder:latest` and
  `qwen3-coder-next:latest` through custom-agent launch paths.
- Persisted session evidence either proves model switching works or records the
  exact blocker.
- `ROADMAP.md`, `CHANGE_LOG.md`, planning notes, issue comments, and PR body
  agree.
