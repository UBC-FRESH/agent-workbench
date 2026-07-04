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
| P6 Copilot SDK Ollama feasibility spike | #41 | `feature/p6-copilot-sdk-ollama-spike` | Complete |
| P7 Copilot SDK local probe environment | #48 | `feature/p7-copilot-sdk-local-probe-env` | Complete |
| P8 SDK same-ticket evaluation harness | #55 | `feature/p8-sdk-same-ticket-evaluation-harness` | Complete |
| P9 SDK structured documentation-output trial | #65 | `feature/p9-structured-doc-output-trial` | Complete |
| P10 Patch proposal protocol trial | #73 | `feature/p10-patch-proposal-protocol` | Active |
| P11 Supervisor-applied patch harness | TBD | TBD | Planned |
| P12 Restricted tool-enabled worker trial | TBD | TBD | Planned |
| P13 GitHub workflow microtrial | TBD | TBD | Planned |
| P14 Model matrix and packaging decision | TBD | TBD | Planned |

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

## Phase 6: Copilot SDK Ollama Feasibility Spike

Parent issue: #41

Branch: `feature/p6-copilot-sdk-ollama-spike`

Status: complete

Goal: determine whether the GitHub Copilot SDK can provide a more reliable
programmatic worker bridge for configured Ollama models than the VS Code Chat
launch path tested in Phases 3 through 5.

- [x] P6.1 Copilot SDK support audit (#42)
  - [x] Inspect SDK documentation and examples.
  - [x] Record public-safe support summary in tracked planning notes.
  - [x] Avoid copying private endpoint details or raw local transcripts.
- [x] P6.2 Local SDK probe scaffold (#43)
  - [x] Add a local-only SDK probe scaffold.
  - [x] Document required inputs and safe defaults.
  - [x] Ensure outputs go under ignored runtime paths.
  - [x] Avoid adding package or CI scaffolding.
- [x] P6.3 Same-ticket Ollama model trial protocol (#44)
  - [x] Add trial protocol guidance.
  - [x] Define same-ticket run commands using explicit model arguments.
  - [x] Attempt local dry-run checks if dependencies and endpoint are available.
  - [x] Record blockers exactly if the SDK or endpoint is unavailable.
- [x] P6.4 Feasibility notes, closeout, and PR (#45)
  - [x] Synchronize roadmap and changelog.
  - [x] Run `git diff --check`.
  - [x] Inspect changed Markdown and script files.
  - [x] Search for credentials, private paths, raw transcript leakage, endpoint
        details, and unrelated project contamination.
  - [x] Comment on and close implementation child issues.
  - [x] Open PR and complete parent closeout after merge.

Phase 6 acceptance criteria:

- Tracked notes identify the SDK features relevant to Ollama BYOK, explicit
  model selection, provider configuration, tool restriction, and event capture.
- The repo contains a public-safe local-only probe scaffold or runbook for
  testing SDK sessions against configured Ollama models.
- The trial protocol can run the same bounded ticket against
  `qwen3-coder:latest` and `qwen3-coder-next:latest` without depending on VS
  Code model-picker state.
- Findings state whether the SDK path should replace, complement, or be
  deferred behind the VS Code Chat bridge.

## Phase 7: Copilot SDK Local Probe Environment

Parent issue: #48

Branch: `feature/p7-copilot-sdk-local-probe-env`

Status: complete

Goal: turn the P6 Copilot SDK/Ollama feasibility scaffold into a locally
runnable probe path by documenting and supporting a local SDK runtime
environment, then attempt the same no-tool probe boundary with explicit model
and provider configuration.

- [x] P7.1 Local SDK source-path support (#49)
  - [x] Add a CLI argument or environment-variable path for SDK source loading.
  - [x] Insert the path before importing `copilot`.
  - [x] Report exact import/dependency blockers in the probe result.
  - [x] Keep generated evidence under ignored runtime paths.
- [x] P7.2 Ignored probe environment setup notes (#50)
  - [x] Add public-safe setup notes for an ignored `.venv`.
  - [x] Document installing or exposing the SDK Python checkout.
  - [x] Document required local environment variables using placeholders.
  - [x] Preserve the boundary that raw outputs and endpoint details remain
        ignored.
- [x] P7.3 No-tool SDK/Ollama probe attempt (#51)
  - [x] Prepare an ignored no-tool ticket under `runtime/agent_jobs/`.
  - [x] Attempt the probe with explicit model and provider inputs if
        prerequisites are available.
  - [x] Record exact blocker text if prerequisites are missing.
  - [x] Promote only sanitized findings into tracked planning notes.
- [x] P7.4 Feasibility decision, closeout, and PR (#52)
  - [x] Update `ROADMAP.md`.
  - [x] Update `CHANGE_LOG.md`.
  - [x] Finalize P7 planning notes.
  - [x] Run verification.
  - [x] Comment on and close child issues.
  - [x] Open, merge, and verify PR closeout.

Phase 7 acceptance criteria:

- The probe can load a local Copilot SDK Python checkout through a CLI argument
  or environment variable without hard-coding a workstation path.
- Tracked docs explain how to create an ignored local probe environment and
  install/use the SDK source checkout or published SDK wheel.
- The no-tool probe is attempted with explicit model and provider inputs, or a
  concrete blocker is recorded with exact error text.
- `ROADMAP.md`, `CHANGE_LOG.md`, planning notes, issues, and PR body agree.

## Phase 8: SDK Same-Ticket Evaluation Harness

Parent issue: #55

Branch: `feature/p8-sdk-same-ticket-evaluation-harness`

Status: complete

Goal: turn the successful P7 one-off Copilot SDK/Ollama probe into a
repeatable, public-safe local evaluation harness that can run the same bounded
ticket multiple times against configured Ollama worker models and summarize
stability signals without trusting worker prose.

- [x] P8.1 Probe run manifest (#56)
  - [x] Document manifest fields for ticket, models, repeats, timeout, expected
        marker, output directory, and provider input references.
  - [x] Add a public-safe example manifest template under `templates/`.
  - [x] Keep real provider endpoint/header references in ignored runtime files.
  - [x] Document how the manifest relates to the existing SDK probe helper.
- [x] P8.2 Repeated same-ticket runner (#57)
  - [x] Add a local runner script under `scripts/`.
  - [x] Reuse `scripts/copilot_sdk_ollama_probe.py` rather than duplicating SDK
        session logic.
  - [x] Write raw per-run outputs under ignored runtime paths.
  - [x] Support a dry-run mode that prints planned runs without contacting the
        model provider.
- [x] P8.3 Result summarizer (#58)
  - [x] Add parser logic for the P7 probe Markdown result format.
  - [x] Classify exact marker match, duplicate output, missing marker, timeout,
        SDK/runtime failure, model-call failure, and simple loop-like
        repetition.
  - [x] Emit a sanitized Markdown summary under ignored runtime paths.
  - [x] Avoid copying raw event records into tracked files.
- [x] P8.4 First A/B consistency trial (#59)
  - [x] Create an ignored local manifest for the no-tool marker ticket.
  - [x] Run at least two repeats per model when local provider inputs are
        available.
  - [x] Inspect ignored per-run results and generated summary.
  - [x] Promote only sanitized findings into tracked P8 planning notes.
- [x] P8.5 Closeout, verification, and PR (#60)
  - [x] Update `ROADMAP.md`.
  - [x] Update `CHANGE_LOG.md`.
  - [x] Finalize P8 planning notes.
  - [x] Run verification.
  - [x] Comment on and close child issues.
  - [x] Open, merge, and verify PR closeout.

Phase 8 acceptance criteria:

- A maintainer can define a repeated model trial in an ignored manifest without
  embedding private endpoint/header details in tracked files.
- The harness can run the same ticket N times per configured model through the
  Copilot SDK probe path.
- The summarizer can classify exact marker matches, duplicate output, missing
  marker, timeouts, SDK/runtime failures, model-call failures, and simple
  loop-like repetition signals from ignored result files.
- The first A/B trial either records sanitized model-comparison findings for
  `qwen3-coder:latest` and `qwen3-coder-next:latest`, or records an exact
  blocker.
- `ROADMAP.md`, `CHANGE_LOG.md`, planning notes, issues, and PR body agree.

## Forward Plan: P9-P14

Planning note: `planning/p9_p14_forward_plan.md`

The next several phases move one risk boundary at a time: structured assistant
output, patch proposal, supervisor-applied mutation, restricted worker mutation,
GitHub workflow participation, and then broader model/packaging decisions.

## Phase 9: SDK Structured Documentation-Output Trial

Parent issue: #65

Branch: `feature/p9-structured-doc-output-trial`

Status: complete

Goal: use the P8 harness on a tiny documentation-style ticket where the worker
returns a structured Markdown result in the assistant response, with no tools
and no file mutation.

- [x] P9.1 Structured documentation-ticket template (#66)
  - [x] Add a tracked template under `templates/`.
  - [x] Require exact section headings.
  - [x] State that tools, commands, and file edits are forbidden.
  - [x] Include failure and stop-condition requirements.
- [x] P9.2 Assistant-result section parser (#67)
  - [x] Add manifest fields for required sections and forbidden phrases.
  - [x] Classify missing sections.
  - [x] Classify extra prose or unexpected sections.
  - [x] Classify refusal and loop-like repetition.
- [x] P9.3 Repeated same-ticket qwen A/B trial (#68)
  - [x] Create an ignored local structured-output ticket.
  - [x] Create an ignored P9 manifest with required sections.
  - [x] Run repeated trials for `qwen3-coder:latest`.
  - [x] Run repeated trials for `qwen3-coder-next:latest`.
  - [x] Inspect ignored result summary.
- [x] P9.4 Rubric mapping for structured-output behavior (#69)
  - [x] Document how structured-output classifications map to rubric
        categories.
  - [x] Identify which classifications force retry, blocked, or reject
        decisions.
  - [x] Keep the mapping generic across future ticket families.
- [x] P9.5 Closeout and next decision (#70)
  - [x] Update `ROADMAP.md`.
  - [x] Update `CHANGE_LOG.md`.
  - [x] Finalize P9 planning notes.
  - [x] Run verification.
  - [x] Comment on and close child issues.
  - [x] Open, merge, and verify PR closeout.

Phase 9 acceptance criteria:

- The harness can classify required sections present, missing section, malformed
  result, extra prose, refusal, and loop-like repetition.
- The same structured ticket is repeated against the configured qwen worker
  models.
- Tracked notes promote only sanitized counts and findings.

## Phase 10: Patch Proposal Protocol Trial

Parent issue: #73

Branch: `feature/p10-patch-proposal-protocol`

Status: active

Goal: ask workers to produce a small, parseable patch proposal without applying
it, so the supervisor can validate candidate edits before any file mutation.

- [x] P10.1 Patch-proposal ticket template (#74)
  - [x] Add a tracked template under `templates/`.
  - [x] Require rationale and fenced diff sections.
  - [x] Forbid tools, commands, and file edits.
  - [x] State that the patch is a proposal only.
- [x] P10.2 Patch block parser and classifier (#75)
  - [x] Add manifest fields for requiring a patch proposal.
  - [x] Parse fenced diff or patch blocks.
  - [x] Classify missing patch, malformed patch, wrong file, and valid
        proposal.
  - [x] Preserve existing marker and structured-output behavior.
- [x] P10.3 Repeated patch-proposal model trial (#76)
  - [x] Create an ignored local patch-proposal ticket.
  - [x] Create an ignored P10 manifest with allowed patch files.
  - [x] Run repeated trials for `qwen3-coder:latest`.
  - [x] Run repeated trials for `qwen3-coder-next:latest`.
  - [x] Inspect ignored result summary.
- [x] P10.4 Supervisor acceptance checklist for proposed patches (#77)
  - [x] Add patch proposal acceptance criteria.
  - [x] Map patch classifications to supervisor decisions.
  - [x] Preserve proposal-only boundary until P11.
- [ ] P10.5 Closeout and mutation-readiness decision (#78)
  - [x] Update `ROADMAP.md`.
  - [x] Update `CHANGE_LOG.md`.
  - [x] Finalize P10 planning notes.
  - [ ] Run verification.
  - [ ] Comment on and close child issues.
  - [ ] Open, merge, and verify PR closeout.

Phase 10 acceptance criteria:

- Workers can be evaluated on whether they produce a valid, bounded patch
  proposal.
- No worker-applied file mutation is required.
- Failure classifications distinguish malformed patch, wrong file, extra prose,
  missing rationale, and unsafe scope expansion.

## Phase 11: Supervisor-Applied Patch Harness

Parent issue: TBD

Branch: TBD

Status: planned

Goal: add a supervisor-side harness that can parse a worker patch proposal,
apply it to an explicitly allowed target, run checks, and classify the result.

Planned tasks:

- P11.1 Allowed-target patch application protocol.
- P11.2 Temporary-worktree or guarded-apply harness.
- P11.3 Check runner and rollback behavior.
- P11.4 Repeated supervisor-applied patch trial.
- P11.5 Closeout and tool-readiness decision.

Phase 11 acceptance criteria:

- Mutation is performed by supervisor-controlled code, not unrestricted worker
  autonomy.
- The harness records exact apply/check failures.
- Raw worker outputs remain ignored; tracked notes record only sanitized
  findings.

## Phase 12: Restricted Tool-Enabled Worker Trial

Parent issue: TBD

Branch: TBD

Status: planned

Goal: test the narrowest available tool-enabled worker path with explicit
allowed paths, commands, and stop conditions, then verify observed tool evidence
against the ticket.

Planned tasks:

- P12.1 Tool-enabled ticket safety contract.
- P12.2 Bridge capability audit for restricted mutation.
- P12.3 Tiny allowed-file mutation trial.
- P12.4 Supervisor verification report update.
- P12.5 Closeout and delegation boundary decision.

Phase 12 acceptance criteria:

- Tool-enabled worker behavior is observed from bridge evidence, not worker
  prose.
- The trial uses a deliberately tiny mutation target.
- The phase states whether controlled mutation should continue, narrow, or
  revert to proposal-only mode.

## Phase 13: GitHub Workflow Microtrial

Parent issue: TBD

Branch: TBD

Status: planned

Goal: test small, bounded GitHub workflow participation without delegating broad
phase closeout.

Planned tasks:

- P13.1 GitHub-task ticket safety contract.
- P13.2 Read-only issue inspection trial.
- P13.3 File-backed comment or PR-body preparation trial.
- P13.4 Supervisor-applied GitHub mutation protocol.
- P13.5 Closeout and GitHub delegation boundary decision.

Phase 13 acceptance criteria:

- Workers do not fake GitHub actions or substitute "would have" reports.
- Read-only and mutation-capable GitHub actions are separated.
- The supervisor retains final authority for issue closure, PR merge, and phase
  closeout.

## Phase 14: Model Matrix And Packaging Decision

Parent issue: TBD

Branch: TBD

Status: planned

Goal: compare configured Ollama worker models across the stable P9-P13 ticket
families, then decide whether Agent Workbench should remain scripts/Markdown or
become a package, CLI, VS Code extension, hosted agent, or other tool surface.

Planned tasks:

- P14.1 Configured Ollama model inventory refresh.
- P14.2 Ticket-family scoring matrix.
- P14.3 Cross-model consistency and failure-mode summary.
- P14.4 Packaging/interface options analysis.
- P14.5 Architecture decision record and closeout.

Phase 14 acceptance criteria:

- Model comparisons use repeated evidence across more than one ticket family.
- The packaging decision cites observed workflow friction and reliability, not
  interface preference alone.
- Any decision to add package, CLI, extension, MCP, or hosted-agent structure is
  deferred until this evidence exists.
