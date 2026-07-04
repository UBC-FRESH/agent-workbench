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
| P10 Patch proposal protocol trial | #73 | `feature/p10-patch-proposal-protocol` | Complete |
| P11 Supervisor-applied patch harness | #81 | `feature/p11-supervisor-applied-patch-harness` | Complete |
| P12 Restricted tool-enabled worker trial | #89 | `feature/p12-restricted-tool-worker-trial` | Complete |
| P13 GitHub workflow microtrial | #97 | `feature/p13-github-workflow-microtrial` | Complete |
| P14 Model matrix and packaging decision | #105 | `feature/p14-model-matrix-packaging-decision` | Complete |
| P15 Model-family expansion trial | #115 | `feature/p15-model-family-expansion-trial` | Complete |
| P16 Command surface stabilization | #122 | `feature/p16-command-surface-stabilization` | Complete |
| P17 Evidence store and summary schema | #129 | `feature/p17-evidence-store-summary-schema` | Complete |
| P18 Richer restricted tool trial | #136 | `feature/p18-richer-restricted-tool-trial` | Complete |
| P19 Delegation policy and trust levels | TBD | TBD | Planned |
| P20 Packaging revisit and interface decision | TBD | TBD | Planned |

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

Status: complete

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
- [x] P10.5 Closeout and mutation-readiness decision (#78)
  - [x] Update `ROADMAP.md`.
  - [x] Update `CHANGE_LOG.md`.
  - [x] Finalize P10 planning notes.
  - [x] Run verification.
  - [x] Comment on and close child issues.
  - [x] Open, merge, and verify PR closeout.

Phase 10 acceptance criteria:

- Workers can be evaluated on whether they produce a valid, bounded patch
  proposal.
- No worker-applied file mutation is required.
- Failure classifications distinguish malformed patch, wrong file, extra prose,
  missing rationale, and unsafe scope expansion.

## Phase 11: Supervisor-Applied Patch Harness

Parent issue: #81

Branch: `feature/p11-supervisor-applied-patch-harness`

Status: complete

Goal: add a supervisor-side harness that can parse a worker patch proposal,
apply it to an explicitly allowed target, run checks, and classify the result.

- [x] P11.1 Allowed-target patch application protocol (#82)
  - [x] Define allowed sandbox target rules.
  - [x] Document forbidden tracked-target mutation.
  - [x] Record protocol in planning notes.
- [x] P11.2 Guarded apply harness (#83)
  - [x] Add supervisor-side apply script under `scripts/`.
  - [x] Parse worker result assistant messages.
  - [x] Extract fenced diff blocks.
  - [x] Apply only to explicitly allowed sandbox paths.
- [x] P11.3 Check runner and rollback behavior (#84)
  - [x] Write a local report with status and exact error text.
  - [x] Support a post-apply expected-text check.
  - [x] Keep rollback/retry guidance explicit.
- [x] P11.4 Supervisor-applied patch trial (#85)
  - [x] Create ignored sandbox target.
  - [x] Create or reuse ignored patch proposal result.
  - [x] Run the guarded apply harness.
  - [x] Inspect the ignored report.
  - [x] Promote sanitized findings.
- [x] P11.5 Closeout and tool-readiness decision (#86)
  - [x] Update `ROADMAP.md`.
  - [x] Update `CHANGE_LOG.md`.
  - [x] Finalize P11 planning notes.
  - [x] Run verification.
  - [x] Comment on and close child issues.
  - [x] Open, merge, and verify PR closeout.

Phase 11 acceptance criteria:

- Mutation is performed by supervisor-controlled code, not unrestricted worker
  autonomy.
- The harness records exact apply/check failures.
- Raw worker outputs remain ignored; tracked notes record only sanitized
  findings.

## Phase 12: Restricted Tool-Enabled Worker Trial

Parent issue: #89

Branch: `feature/p12-restricted-tool-worker-trial`

Status: complete

Goal: test the narrowest available tool-enabled worker path with explicit
allowed paths, commands, and stop conditions, then verify observed tool evidence
against the ticket.

- [x] P12.1 Tool-enabled ticket safety contract (#90)
  - [x] Add a restricted tool-enabled ticket template.
  - [x] State allowed target paths.
  - [x] State forbidden commands and files.
  - [x] Require supervisor evidence review.
- [x] P12.2 Bridge capability audit for restricted mutation (#91)
  - [x] Compare SDK and VS Code Chat bridge tool surfaces.
  - [x] Record which bridge can observe file/tool evidence.
  - [x] Record model-selection caveats.
- [x] P12.3 Tiny allowed-file mutation trial (#92)
  - [x] Prepare ignored worker ticket.
  - [x] Attempt one tiny ignored file mutation through the selected bridge.
  - [x] Inspect supervisor report and target file.
  - [x] Promote sanitized findings.
- [x] P12.4 Supervisor verification report update (#93)
  - [x] Confirm the existing verifier captures allowed files and observed tools.
  - [x] Record any gaps or required changes.
  - [x] Keep raw reports ignored.
- [x] P12.5 Closeout and delegation boundary decision (#94)
  - [x] Update roadmap, changelog, and planning notes.
  - [x] Run verification.
  - [x] Close child issues.
  - [x] Open and merge PR.
  - [x] Close parent issue after merge.

Phase 12 acceptance criteria:

- Tool-enabled worker behavior is observed from bridge evidence, not worker
  prose.
- The trial uses a deliberately tiny mutation target.
- The phase states whether controlled mutation should continue, narrow, or
  revert to proposal-only mode.

## Phase 13: GitHub Workflow Microtrial

Parent issue: #97

Branch: `feature/p13-github-workflow-microtrial`

Status: complete

Goal: test small, bounded GitHub workflow participation without delegating broad
phase closeout.

- [x] P13.1 GitHub-task ticket safety contract (#98)
  - [x] Add GitHub microtask ticket template.
  - [x] Separate worker preparation from supervisor mutation.
  - [x] Forbid issue closure and PR merge delegation.
- [x] P13.2 Read-only issue inspection trial (#99)
  - [x] Run read-only `gh issue view`.
  - [x] Record exact issue state.
  - [x] Avoid mutation during read-only audit.
- [x] P13.3 File-backed comment preparation trial (#100)
  - [x] Prepare ignored worker ticket.
  - [x] Generate a bounded comment body candidate.
  - [x] Keep raw worker output ignored.
- [x] P13.4 Supervisor-applied GitHub mutation protocol (#101)
  - [x] Supervisor reviews candidate body.
  - [x] Supervisor posts one file-backed comment.
  - [x] Verify the mutation with read-only `gh issue view`.
- [x] P13.5 Closeout and GitHub delegation boundary decision (#102)
  - [x] Update roadmap, changelog, and planning notes.
  - [x] Run verification.
  - [x] Close child issues.
  - [x] Open and merge PR.
  - [x] Close parent issue after merge.

Phase 13 acceptance criteria:

- Workers do not fake GitHub actions or substitute "would have" reports.
- Read-only and mutation-capable GitHub actions are separated.
- The supervisor retains final authority for issue closure, PR merge, and phase
  closeout.

## Phase 14: Model Matrix And Packaging Decision

Parent issue: #105

Branch: `feature/p14-model-matrix-packaging-decision`

Status: complete

Goal: compare configured Ollama worker models across the stable P9-P13 ticket
families, then decide whether Agent Workbench should remain scripts/Markdown or
become a package, CLI, VS Code extension, hosted agent, or other tool surface.

- [x] P14.1 Configured Ollama model inventory refresh (#106)
  - [x] Query configured provider inventory.
  - [x] Record sanitized model IDs.
  - [x] Keep endpoint and headers ignored.
- [x] P14.2 Ticket-family scoring matrix (#107)
  - [x] Summarize P8-P13 ticket-family outcomes.
  - [x] Separate SDK trials from VS Code Chat bridge trials.
  - [x] Record evidence limits.
- [x] P14.3 Cross-model consistency and failure-mode summary (#108)
  - [x] Summarize qwen3-coder and qwen3-coder-next contrasts.
  - [x] Record looping, missing-section, and successful bounded mutation
        evidence.
  - [x] Avoid broad model superiority claims.
- [x] P14.4 Packaging/interface options analysis (#109)
  - [x] Compare scripts/Markdown, package/CLI, VS Code extension, MCP, hosted
        agent.
  - [x] Cite observed workflow friction.
  - [x] Recommend next architecture step.
- [x] P14.5 Architecture decision record and closeout (#110)
  - [x] Add architecture decision note.
  - [x] Update roadmap and changelog.
  - [x] Run verification.
  - [x] Close child issues.
  - [x] Open and merge PR.

Phase 14 acceptance criteria:

- Model comparisons use repeated evidence across more than one ticket family.
- The packaging decision cites observed workflow friction and reliability, not
  interface preference alone.
- Any decision to add package, CLI, extension, MCP, or hosted-agent structure is
  deferred until this evidence exists.

## Forward Plan: P15-P20

Planning note: `planning/p15_p20_next_tranche_plan.md`

The next tranche broadens evidence before broadening authority. It expands
model coverage, stabilizes local commands, normalizes evidence, runs richer
sandbox-only tool trials, writes delegation policy, and only then revisits
packaging.

## Phase 15: Model-Family Expansion Trial

Parent issue: #115

Branch: `feature/p15-model-family-expansion-trial`

Status: complete

Goal: run the stable P8-P10 ticket families across selected configured Ollama
models beyond the initial qwen pair.

Completed tasks:

- [x] P15.1 Select model subset from configured inventory (#116)
  - [x] Select at least three non-qwen configured coding models.
  - [x] Record large-model deferral rationale.
  - [x] Keep model-host details out of tracked files.
- [x] P15.2 Prepare repeated manifests for marker, structured-output, and
  patch-proposal ticket families (#117)
  - [x] Prepare ignored marker-family manifest.
  - [x] Prepare ignored structured-output-family manifest.
  - [x] Prepare ignored patch-proposal-family manifest.
  - [x] Keep raw outputs under ignored runtime paths.
- [x] P15.3 Run small-repeat SDK trials (#118)
  - [x] Run marker-family trial.
  - [x] Run structured-output-family trial.
  - [x] Run patch-proposal-family trial.
  - [x] Inspect ignored summaries before promoting findings.
- [x] P15.4 Produce sanitized cross-model summary (#119)
  - [x] Add `planning/phase15_model_family_expansion_notes.md`.
  - [x] Summarize classifications by model and ticket family.
  - [x] Record caveats and evidence limits.
- [x] P15.5 Closeout and model-shortlist decision (#120)
  - [x] Update roadmap and changelog.
  - [x] Run verification.
  - [x] Close child issues.
  - [x] Open and merge PR.

Phase 15 acceptance criteria:

- At least three non-qwen configured coding models are evaluated on repeated
  no-tool ticket families.
- Results distinguish marker, structured-output, and patch-proposal behavior.
- Large-model inclusion or deferral is explicit.

## Phase 16: Command Surface Stabilization

Parent issue: #122

Branch: `feature/p16-command-surface-stabilization`

Status: complete

Goal: stabilize the local script command surfaces that are now reused across
multiple phases without converting the repo into a package.

Completed tasks:

- [x] P16.1 Inventory script options and manifest fields (#123)
  - [x] Inventory reusable local scripts.
  - [x] Document manifest field expectations.
  - [x] Preserve the direct-script boundary.
- [x] P16.2 Normalize redaction and report metadata (#124)
  - [x] Record redaction policy for provider and transcript evidence.
  - [x] Document report metadata expectations.
  - [x] Keep private runtime inputs ignored.
- [x] P16.3 Add lightweight smoke fixtures or dry-run checks (#125)
  - [x] Add `scripts/check_command_surfaces.py`.
  - [x] Check script help surfaces.
  - [x] Check SDK manifest template fields.
  - [x] Check SDK harness dry-run planning.
- [x] P16.4 Update playbooks and templates (#126)
  - [x] Add `planning/phase16_command_surface_stabilization_notes.md`.
  - [x] Keep command-surface guidance public-safe.
  - [x] Avoid package or CLI expansion.
- [x] P16.5 Closeout and package-readiness checkpoint (#127)
  - [x] Update roadmap and changelog.
  - [x] Run verification.
  - [x] Close child issues.
  - [x] Open and merge PR.

Phase 16 acceptance criteria:

- Script help, manifest fields, and report metadata are internally consistent.
- Dry-run/smoke checks cover the major local scripts.
- Packaging remains deferred unless command surfaces are stable enough to wrap.

## Phase 17: Evidence Store And Summary Schema

Parent issue: #129

Branch: `feature/p17-evidence-store-summary-schema`

Status: complete

Goal: define an ignored evidence layout and sanitized summary schema for model
runs, bridge runs, patch trials, and GitHub microtasks.

Completed tasks:

- [x] P17.1 Evidence directory convention (#130)
  - [x] Add `playbooks/evidence_store.md`.
  - [x] Separate raw ignored evidence from tracked summaries.
  - [x] Document promotion paths.
- [x] P17.2 Summary JSON/Markdown field schema (#131)
  - [x] Add `templates/evidence_summary.md`.
  - [x] Add `templates/evidence_summary.schema.json`.
  - [x] Define required summary fields.
- [x] P17.3 Sanitized promotion rules (#132)
  - [x] Document allowed tracked evidence.
  - [x] Document forbidden private values.
  - [x] Preserve supervisor verification requirement.
- [x] P17.4 Backfill one summary from P15/P16 style outputs (#133)
  - [x] Backfill a sanitized P15 model-run summary.
  - [x] Use classification counts instead of raw assistant messages.
  - [x] Keep source runtime paths repo-relative.
- [x] P17.5 Closeout and evidence-retention decision (#134)
  - [x] Update roadmap and changelog.
  - [x] Run verification.
  - [x] Close child issues.
  - [x] Open and merge PR.

Phase 17 acceptance criteria:

- Raw evidence and sanitized summaries have distinct locations and purposes.
- Summary fields are sufficient for model comparison and supervisor audit.
- No private endpoint, header, transcript, or workstation path is tracked.

## Phase 18: Richer Restricted Tool Trial

Parent issue: #136

Branch: `feature/p18-richer-restricted-tool-trial`

Status: complete

Goal: run a richer VS Code Chat bridge tool trial in an ignored sandbox with one
read, one allowed ignored-file mutation, and supervisor verification.

Completed tasks:

- [x] P18.1 Rich restricted-tool ticket contract (#137)
  - [x] Update restricted-tool template for explicit required reads.
  - [x] Preserve one allowed ignored output boundary.
  - [x] Keep terminal commands forbidden unless explicitly listed.
- [x] P18.2 Sandbox target setup (#138)
  - [x] Prepare ignored input file.
  - [x] Prepare ignored worker ticket.
  - [x] Remove stale output before run.
- [x] P18.3 VS Code Chat bridge run (#139)
  - [x] Launch one visible bridge run.
  - [x] Observe read-plus-create tool use.
  - [x] Keep raw report ignored.
- [x] P18.4 Supervisor evidence report and deviation analysis (#140)
  - [x] Inspect supervisor report.
  - [x] Inspect output file content.
  - [x] Record sanitized evidence.
- [x] P18.5 Closeout and mutation-boundary decision (#141)
  - [x] Update roadmap and changelog.
  - [x] Run verification.
  - [x] Close child issues.
  - [x] Open and merge PR.

Phase 18 acceptance criteria:

- Worker tool use remains limited to ignored sandbox paths.
- Observed tool evidence supports or rejects the worker result.
- The phase explicitly states whether tracked-file mutation remains forbidden.

## Phase 19: Delegation Policy And Trust Levels

Parent issue: TBD

Branch: TBD

Status: planned

Goal: convert P8-P18 evidence into a formal delegation policy and trust-level
model for worker agents.

Planned tasks:

- P19.1 Define trust levels.
- P19.2 Map ticket families to allowed authority.
- P19.3 Define nondelegable actions.
- P19.4 Update AGENTS and playbooks.
- P19.5 Closeout and governance decision.

Phase 19 acceptance criteria:

- The policy distinguishes no-tool output, proposal-only work,
  supervisor-applied mutation, sandbox mutation, tracked mutation, and GitHub
  workflow authority.
- Issue closure, PR merge, and release actions remain supervisor-only unless
  evidence supports a future exception.

## Phase 20: Packaging Revisit And Interface Decision

Parent issue: TBD

Branch: TBD

Status: planned

Goal: revisit package, CLI, VS Code extension, MCP, and hosted-agent options
using P15-P19 evidence.

Planned tasks:

- P20.1 Review command-surface stability.
- P20.2 Review evidence schema stability.
- P20.3 Compare interface options and costs.
- P20.4 Decide next architecture move.
- P20.5 Closeout and next-roadmap tranche.

Phase 20 acceptance criteria:

- The architecture decision cites concrete evidence from P15-P19.
- If packaging is still deferred, the reason is explicit.
- If packaging starts, the chosen surface has a narrow first slice.
