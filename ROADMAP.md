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
| P19 Delegation policy and trust levels | #143 | `feature/p19-delegation-policy-trust-levels` | Complete |
| P20 Packaging revisit and interface decision | #150 | `feature/p20-packaging-interface-decision` | Complete |
| P21 Minimal local package and CLI skeleton | #157 | `feature/p21-minimal-local-package-cli` | Complete |
| P22 CLI wrappers for existing commands | #164 | `feature/p22-cli-wrappers-existing-commands` | Complete |
| P23 Evidence summary validation and rendering | #171 | `feature/p23-evidence-summary-validation-rendering` | Complete |
| P24 CLI dogfood workflow | #178 | `feature/p24-cli-dogfood-workflow` | Complete |
| P25 Real-project pilot scaffold | #185 | `feature/p25-real-project-pilot-scaffold` | Complete |
| P26 Cross-project eval support | #192 | `feature/p26-cross-project-eval` | Complete |
| P27 Supervisor decision packets | #198 | `feature/p27-supervisor-decision-packets` | Complete |
| P28 Claim review aids | #204 | `feature/p28-claim-review-aids` | Complete |
| P29 Repeat-run and model comparison | #210 | `feature/p29-repeat-run-model-comparison` | Complete |
| P30 Real-project deployment playbook | #216 | `feature/p30-real-project-deployment-playbook` | Complete |
| P31 Delegation economics model | #222 | `feature/p31-delegation-economics-model` | Complete |
| P32 Task taxonomy and delegation suitability | #228 | `feature/p32-task-taxonomy-delegation-suitability` | Complete |
| P33 Worker model capability profiles | #234 | `feature/p33-worker-model-capability-profiles` | Complete |
| P34 Delegation decision engine v0 | #240 | `feature/p34-delegation-decision-engine-v0` | Complete |
| P35 Real-project pilot accounting | #250 | `feature/p35-real-project-pilot-accounting` | Complete |
| P36 Policy tuning loop | #256 | `feature/p36-policy-tuning-loop` | Complete |
| P37 Artifact and workflow contract model | #262 | `feature/p37-artifact-workflow-contracts` | Complete |
| P38 Role, capability, and implementation model | #268 | `feature/p38-role-capability-implementation` | Complete |
| P39 Reusable scientific workbench templates | #274 | `feature/p39-reusable-workbench-templates` | Complete |
| P40 Observability and token-cost ingestion | #280 | `feature/p40-token-cost-ingestion` | Complete |
| P41 FreshForge graph integration spike | #286 | `feature/p41-freshforge-graph-integration` | Complete |
| P42 Agent metadata convention | #292 | `feature/p42-agent-metadata-convention` | Complete |
| P43 Graph-backed pilot workflow | #298 | `feature/p43-graph-backed-pilot-workflow` | Complete |
| P44 Graph-aware delegation decision engine | #304 | `feature/p44-graph-aware-decision-engine` | Complete |
| P45 Per-node token economics | #310 | `feature/p45-per-node-token-economics` | Complete |
| P46 FreshForge dependency decision | #316 | `feature/p46-freshforge-dependency-decision` | Complete |
| P47 FreshForge deployment test batch | #322 | `feature/p47-freshforge-deployment-test-batch` | Complete |
| P48 Phase-scale A/B token economics benchmark | #328 | `feature/p48-phase-scale-ab-token-economics` | Complete |
| P49 Benchmark worktree preparation | #334 | `feature/p49-benchmark-worktree-prep` | Complete |
| P50 FreshForge P16 A/B benchmark run | #340 | `feature/p50-freshforge-p16-ab-benchmark-run` | Complete |
| P51 Managed delegation workflow lanes | #347 | `feature/p51-managed-delegation-workflows` | Complete |
| P52 Local self-audit and repair loop | #348 | `feature/p52-local-self-audit-repair-loop` | Complete |
| P53 Document library index pilot | #349 | `feature/p53-document-library-index-pilot` | Complete |
| P54 Delegation loop policy tuning | #350 | `feature/p54-delegation-loop-policy-tuning` | Complete |
| P55 TSA23 first real indexing run | #367 | `feature/p55-tsa23-first-indexing-run` | Active |

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

Parent issue: #143

Branch: `feature/p19-delegation-policy-trust-levels`

Status: complete

Goal: convert P8-P18 evidence into a formal delegation policy and trust-level
model for worker agents.

Completed tasks:

- [x] P19.1 Define trust levels (#144)
  - [x] Add L0-L6 trust levels.
  - [x] Distinguish response, proposal, sandbox, tracked, GitHub, and release
        authority.
- [x] P19.2 Map ticket families to allowed authority (#145)
  - [x] Map P8-P18 ticket families to maximum levels.
  - [x] Keep GitHub closeout supervisor-only.
  - [x] Keep tracked-file mutation forbidden.
- [x] P19.3 Define nondelegable actions (#146)
  - [x] List supervisor-only workflow actions.
  - [x] Define escalation triggers.
  - [x] Preserve model/provider configuration authority.
- [x] P19.4 Update AGENTS and playbooks (#147)
  - [x] Add trust-level summary to `AGENTS.md`.
  - [x] Add `planning/delegation_policy.md`.
  - [x] Add `planning/phase19_delegation_policy_notes.md`.
- [x] P19.5 Closeout and governance decision (#148)
  - [x] Update roadmap and changelog.
  - [x] Run verification.
  - [x] Close child issues.
  - [x] Open and merge PR.

Phase 19 acceptance criteria:

- The policy distinguishes no-tool output, proposal-only work,
  supervisor-applied mutation, sandbox mutation, tracked mutation, and GitHub
  workflow authority.
- Issue closure, PR merge, and release actions remain supervisor-only unless
  evidence supports a future exception.

## Phase 20: Packaging Revisit And Interface Decision

Parent issue: #150

Branch: `feature/p20-packaging-interface-decision`

Status: complete

Goal: revisit package, CLI, VS Code extension, MCP, and hosted-agent options
using P15-P19 evidence.

Completed tasks:

- [x] P20.1 Review command-surface stability (#151)
  - [x] Review P16 smoke-check evidence.
  - [x] Compare direct scripts against a wrapper interface.
  - [x] Preserve compatibility with existing scripts.
- [x] P20.2 Review evidence schema stability (#152)
  - [x] Review P17 evidence summary fields.
  - [x] Confirm raw evidence remains ignored.
  - [x] Identify validation as future work.
- [x] P20.3 Compare interface options and costs (#153)
  - [x] Compare scripts, local CLI, VS Code extension, MCP, hosted agent, and
        dashboard options.
  - [x] Record rejected options.
  - [x] Keep worker authority unchanged.
- [x] P20.4 Decide next architecture move (#154)
  - [x] Add `planning/adr_0002_interface_direction.md`.
  - [x] Add `planning/phase20_packaging_revisit_notes.md`.
  - [x] Select a narrow local package/CLI spike for P21.
- [x] P20.5 Closeout and next-roadmap tranche (#155)
  - [x] Add `planning/p21_p24_forward_plan.md`.
  - [x] Update roadmap and changelog.
  - [x] Run verification.
  - [x] Open and merge PR.

Phase 20 acceptance criteria:

- The architecture decision cites concrete evidence from P15-P19.
- The chosen packaging start has a narrow first slice.
- VS Code extension, MCP, hosted-agent, and dashboard work remain explicitly
  deferred.

## Forward Plan: P21-P24

Planning note: `planning/p21_p24_forward_plan.md`

The next tranche starts the narrow local package/CLI path selected in ADR 0002.
The first slice should wrap existing supervisor-owned local commands without
changing worker trust levels.

## Phase 21: Minimal Local Package And CLI Skeleton

Parent issue: #157

Branch: `feature/p21-minimal-local-package-cli`

Status: complete

Goal: add the smallest Python package and local CLI entrypoint needed to wrap
existing supervisor-side scripts.

Completed tasks:

- [x] P21.1 Package metadata and layout (#158)
  - [x] Add `pyproject.toml`.
  - [x] Use a `src/` package layout.
  - [x] Add `agent-workbench` console script metadata.
- [x] P21.2 Importable package namespace (#159)
  - [x] Add `src/agent_workbench/__init__.py`.
  - [x] Add package version.
  - [x] Add `python -m agent_workbench` entrypoint.
- [x] P21.3 Minimal CLI entrypoint (#160)
  - [x] Add `src/agent_workbench/cli.py`.
  - [x] Provide help output.
  - [x] Provide version output.
- [x] P21.4 Local install and help verification (#161)
  - [x] Run editable install.
  - [x] Verify console help and version.
  - [x] Verify module help.
- [x] P21.5 Closeout and package skeleton decision (#162)
  - [x] Update roadmap and changelog.
  - [x] Run verification.
  - [x] Close child issues.
  - [x] Open and merge PR.

Phase 21 acceptance criteria:

- `agent_workbench` imports from the local checkout.
- `agent-workbench --help` and `agent-workbench --version` work after editable
  install.
- Existing direct scripts remain present and usable.

## Phase 22: CLI Wrappers For Existing Commands

Parent issue: #164

Branch: `feature/p22-cli-wrappers-existing-commands`

Status: complete

Goal: wrap command-surface smoke checks and SDK same-ticket evaluation through
the new CLI while preserving direct script compatibility.

Completed tasks:

- [x] P22.1 CLI smoke-check wrapper (#165)
  - [x] Add `agent-workbench smoke`.
  - [x] Delegate to `scripts/check_command_surfaces.py`.
  - [x] Support optional report path.
- [x] P22.2 CLI same-ticket eval wrapper (#166)
  - [x] Add `agent-workbench eval`.
  - [x] Require manifest path.
  - [x] Delegate to `scripts/sdk_same_ticket_eval.py`.
- [x] P22.3 Redacted dry-run compatibility (#167)
  - [x] Support `--dry-run`.
  - [x] Support `--summary-only`.
  - [x] Preserve script-level redaction behavior.
- [x] P22.4 Direct script compatibility verification (#168)
  - [x] Keep direct scripts in place.
  - [x] Run direct command-surface smoke check.
  - [x] Verify package wrapper smoke check.
- [x] P22.5 Closeout and wrapper decision (#169)
  - [x] Update roadmap and changelog.
  - [x] Run verification.
  - [x] Close child issues.
  - [x] Open and merge PR.

Phase 22 acceptance criteria:

- `agent-workbench smoke` runs the P16 command-surface smoke check.
- `agent-workbench eval --manifest <path> --dry-run` plans SDK evaluation
  without provider contact.
- Existing direct scripts remain usable.

## Phase 23: Evidence Summary Validation And Rendering

Parent issue: #171

Branch: `feature/p23-evidence-summary-validation-rendering`

Status: complete

Goal: make the P17 evidence summary contract executable enough for local
supervisor review.

Completed tasks:

- [x] P23.1 Evidence validation module (#172)
  - [x] Add `src/agent_workbench/evidence.py`.
  - [x] Check required top-level fields.
  - [x] Detect obvious private-looking values.
- [x] P23.2 Evidence rendering module (#173)
  - [x] Render validated JSON summaries to Markdown.
  - [x] Include metadata, scope, outcomes, verification, boundary, and decision.
- [x] P23.3 CLI evidence commands (#174)
  - [x] Add `agent-workbench evidence validate`.
  - [x] Add `agent-workbench evidence render`.
  - [x] Fail invalid inputs with actionable errors.
- [x] P23.4 Validation fixtures and checks (#175)
  - [x] Prepare ignored valid evidence fixture.
  - [x] Prepare ignored invalid evidence fixture.
  - [x] Verify success and failure paths.
- [x] P23.5 Closeout and rendering decision (#176)
  - [x] Update roadmap and changelog.
  - [x] Run verification.
  - [x] Close child issues.
  - [x] Open and merge PR.

Phase 23 acceptance criteria:

- `agent-workbench evidence validate --input <summary.json>` validates required
  fields and privacy rules.
- `agent-workbench evidence render --input <summary.json> --output <summary.md>`
  writes a sanitized Markdown summary.
- Invalid summaries fail with actionable error text.

## Phase 24: CLI Dogfood Workflow

Parent issue: #178

Branch: `feature/p24-cli-dogfood-workflow`

Status: complete

Goal: dogfood the new CLI on one no-tool evaluation workflow from ticket through
sanitized summary.

Completed tasks:

- [x] P24.1 Dogfood runtime ticket and manifest (#179)
  - [x] Prepare ignored ticket.
  - [x] Prepare ignored manifest.
  - [x] Keep provider inputs ignored.
- [x] P24.2 CLI smoke and dry-run dogfood (#180)
  - [x] Run editable install.
  - [x] Run `agent-workbench smoke`.
  - [x] Run `agent-workbench eval --dry-run`.
- [x] P24.3 Provider-backed no-tool CLI trial (#181)
  - [x] Run provider-backed `agent-workbench eval`.
  - [x] Inspect ignored evaluation summary.
  - [x] Confirm `exact-marker` classification.
- [x] P24.4 Evidence summary validation and rendering (#182)
  - [x] Create ignored sanitized evidence summary JSON.
  - [x] Run `agent-workbench evidence validate`.
  - [x] Run `agent-workbench evidence render`.
- [x] P24.5 Closeout and deployment-readiness decision (#183)
  - [x] Add `playbooks/cli_workflow.md`.
  - [x] Add `planning/phase24_cli_dogfood_workflow_notes.md`.
  - [x] Update README, roadmap, and changelog.
  - [x] Open and merge PR.

Phase 24 acceptance criteria:

- `agent-workbench smoke` succeeds.
- `agent-workbench eval --manifest <manifest> --dry-run` succeeds without
  provider contact.
- Provider-backed `agent-workbench eval --manifest <manifest>` succeeds with
  configured inputs.
- `agent-workbench evidence validate` and `agent-workbench evidence render`
  succeed on the dogfood summary.
- README and playbook explain the minimal package workflow for real dev-project
  trials.

## Phase 25: Real-Project Pilot Scaffold

Parent issue: #185

Branch: `feature/p25-real-project-pilot-scaffold`

Status: complete

Goal: add a real-project pilot scaffold command so supervisors can create
bounded worker tickets, evaluation manifests, and sanitized evidence-summary
stubs for adjacent development projects.

Completed tasks:

- [x] P25.1 Pilot scaffold command design (#186)
  - [x] Add `agent-workbench pilot scaffold`.
  - [x] Support marker and proposal modes.
  - [x] Keep worker authority no-tool by default.
- [x] P25.2 Ticket and manifest generation (#187)
  - [x] Generate ignored ticket files.
  - [x] Generate SDK evaluation manifests.
  - [x] Preserve configurable model/provider file references.
- [x] P25.3 Evidence summary stub generation (#188)
  - [x] Generate evidence-summary JSON stubs.
  - [x] Use repo-relative runtime paths.
  - [x] Validate stubs with package evidence command.
- [x] P25.4 Local dogfood scaffold and dry-run (#189)
  - [x] Scaffold a local dogfood pilot.
  - [x] Run generated eval manifest with `--dry-run`.
  - [x] Run command-surface smoke check.
- [x] P25.5 Closeout and real-project trial decision (#190)
  - [x] Update playbook, roadmap, changelog, and planning notes.
  - [x] Run verification.
  - [x] Open and merge PR.

Phase 25 acceptance criteria:

- `agent-workbench pilot scaffold` creates ticket, manifest, and evidence JSON
  paths under an ignored runtime directory.
- Generated manifests can be used with `agent-workbench eval --dry-run`.
- Generated evidence stubs validate with `agent-workbench evidence validate`.
- The CLI workflow playbook explains how to use the scaffold for real project
  trials.

## Phase 26: Cross-Project Eval Support

Parent issue: #192

Branch: `feature/p26-cross-project-eval`

Status: complete

Goal: allow `agent-workbench eval` to execute manifests whose ticket/output
paths are relative to a target project root while keeping Agent Workbench script
lookup anchored to the Agent Workbench checkout.

Completed tasks:

- [x] P26.1 Eval project-root CLI contract (#193)
  - [x] Add `agent-workbench eval --project-root <target-project>`.
  - [x] Preserve existing eval behavior when omitted.
- [x] P26.2 Cross-project manifest execution path (#194)
  - [x] Resolve target-project paths from `--project-root`.
  - [x] Materialize private manifest copies beside the target manifest.
  - [x] Anchor probe script lookup to Agent Workbench.
- [x] P26.3 Dogfood cross-project dry run (#195)
  - [x] Scaffold ignored target-project files.
  - [x] Run cross-project eval dry run.
  - [x] Validate generated evidence stub.
- [x] P26.4 Documentation and closeout (#196)
  - [x] Update CLI playbook and planning notes.
  - [x] Run verification.
  - [x] Open and merge PR.

Phase 26 acceptance criteria:

- `agent-workbench eval --project-root <target-project> --manifest <manifest>
  --dry-run` resolves target-project ticket/output paths correctly.
- Private manifest copies stay in the same ignored target-project artifact
  tree as the input manifest.
- Existing `agent-workbench eval --manifest <manifest> --dry-run` behavior still
  works.
- `agent-workbench smoke` still passes.

## Phase 27: Supervisor Decision Packets

Parent issue: #198

Branch: `feature/p27-supervisor-decision-packets`

Status: complete

Goal: make Agent Workbench usable for repeatable supervisor review after
multiple worker proposal runs by adding isolated pilot-pack scaffolding and a
sanitized supervisor decision-packet command.

Completed tasks:

- [x] P27.1 Forward roadmap tranche (#199)
  - [x] Add `planning/p27_p30_forward_plan.md`.
  - [x] Add P27-P30 to the issue tracker map.
  - [x] Keep P28-P30 planned rather than active.
- [x] P27.2 Isolated pilot pack scaffold (#200)
  - [x] Add `agent-workbench pilot pack-scaffold`.
  - [x] Support repeated `--task task-id=Title` inputs.
  - [x] Isolate eval output and SDK scratch directories by task ID.
- [x] P27.3 Supervisor decision packet synthesis (#201)
  - [x] Add `agent-workbench evidence synthesize`.
  - [x] Validate each evidence summary before packet rendering.
  - [x] Render decision counts, classification counts, evidence table, notes,
    and promotion boundaries.
- [x] P27.4 Dogfood and closeout (#202)
  - [x] Dogfood pack scaffolding under ignored runtime paths.
  - [x] Validate, render, and synthesize dogfood evidence.
  - [x] Update playbook, planning notes, roadmap, and changelog.

Phase 27 acceptance criteria:

- `agent-workbench pilot pack-scaffold` creates multiple isolated ticket,
  manifest, and evidence files under a chosen ignored target-project directory.
- Generated manifests do not overwrite each other's eval outputs.
- `agent-workbench evidence synthesize` validates evidence JSON files and
  renders one sanitized Markdown decision packet.
- CLI workflow docs explain how to use the packet workflow for real projects.

## Phase 28: Claim Review Aids

Parent issue: #204

Branch: `feature/p28-claim-review-aids`

Status: complete

Goal: make unsupported worker claims easier to identify before supervisor
promotion.

Completed tasks:

- [x] P28.1 Claim review evidence contract (#205)
  - [x] Add optional `accepted_claims`, `rejected_claims`, and
    `needs_evidence_claims` fields.
  - [x] Validate claim-review fields when present.
  - [x] Preserve compatibility with evidence summaries that omit claim fields.
- [x] P28.2 Claim-aware rendering and packets (#206)
  - [x] Render claim review sections in evidence summaries.
  - [x] Render claim disposition counts and per-evidence claim review in
    supervisor decision packets.
- [x] P28.3 Claim review template and docs (#207)
  - [x] Add `templates/claim_review_checklist.md`.
  - [x] Update the CLI workflow playbook.
  - [x] Add P28 planning notes.
- [x] P28.4 Dogfood and closeout (#208)
  - [x] Dogfood valid and invalid claim-review evidence.
  - [x] Run verification.
  - [x] Open and merge PR.

Phase 28 acceptance criteria:

- Evidence summaries may include accepted, rejected, and needs-evidence claim
  fields.
- Invalid claim-review fields fail validation.
- Evidence rendering and synthesis show claim review sections when fields are
  present.
- The claim review checklist documents the promotion boundary.

## Phase 29: Repeat-Run And Model Comparison

Parent issue: #210

Branch: `feature/p29-repeat-run-model-comparison`

Status: complete

Goal: compare consistency across repeated runs and installed Ollama worker
models for identical ticket families.

Completed tasks:

- [x] P29.1 Comparison contract and command (#211)
  - [x] Add `agent-workbench compare eval`.
  - [x] Accept one or more existing eval `summary.json` inputs.
  - [x] Write a Markdown comparison report.
- [x] P29.2 Model/repeat summary rendering (#212)
  - [x] Render classification counts by evaluation and model.
  - [x] Render per-model consistency across repeats.
  - [x] Render per-run status, blocker, classification, and result file.
- [x] P29.3 Documentation and planning sync (#213)
  - [x] Add P29 planning notes.
  - [x] Update CLI workflow playbook.
  - [x] Update roadmap and changelog.
- [x] P29.4 Dogfood and closeout (#214)
  - [x] Dogfood against existing ignored eval summaries.
  - [x] Run verification.
  - [x] Open and merge PR.

Phase 29 acceptance criteria:

- `agent-workbench compare eval` renders a model/repeat comparison report for
  existing same-ticket eval summaries.
- The report includes classification counts, consistency, per-run outcomes, and
  a scope boundary.
- Dogfood succeeds against existing ignored summary artifacts.

## Phase 30: Real-Project Deployment Playbook

Parent issue: #216

Branch: `feature/p30-real-project-deployment-playbook`

Status: complete

Goal: turn the P26-P29 workflow into a reusable deployment playbook for
UBC-FRESH projects.

Completed tasks:

- [x] P30.1 Deployment playbook structure (#217)
  - [x] Add `playbooks/real_project_deployment.md`.
  - [x] Add P30 planning notes.
  - [x] Link the playbook from README.
- [x] P30.2 Supervisor gates and stop conditions (#218)
  - [x] Document target selection gates.
  - [x] Document supervisor promotion gates.
  - [x] Document stop conditions for worker use.
- [x] P30.3 Cleanup and promotion rules (#219)
  - [x] Document ignored target-project artifact rules.
  - [x] Document sanitized promotion rules.
  - [x] Document final closeout hygiene checks.
- [x] P30.4 Verification and closeout (#220)
  - [x] Inspect playbook Markdown.
  - [x] Run verification.
  - [x] Open and merge PR.

Phase 30 acceptance criteria:

- The playbook explains how to deploy Agent Workbench on a real project from
  target selection through supervisor promotion.
- The playbook references P27 packets, P28 claim review, and P29 comparison
  reports.
- The playbook includes cleanup rules and stop conditions.

## Phase 31: Delegation Economics Model

Parent issue: #222

Branch: `feature/p31-delegation-economics-model`

Status: complete

Goal: define the cost/benefit model that determines whether self-hosted worker
delegation produces positive net value compared with direct paid-supervisor
token spend.

Planned tasks:

- [x] P31.1 Cost vocabulary and accounting boundary (#223)
  - [x] Define avoided paid-supervisor effort.
  - [x] Define delegation setup effort.
  - [x] Define supervisor verification effort.
  - [x] Define retry, delay, and context-switching effort.
- [x] P31.2 Failure-risk and cleanup model (#224)
  - [x] Define worker failure probability.
  - [x] Define expected cleanup cost.
  - [x] Define rollback, patch-forward, and direct-redo cases.
- [x] P31.3 Net-benefit formula and examples (#225)
  - [x] Document a simple expected-value equation.
  - [x] Include qualitative examples for small, useful middle-zone, and
    oversized tasks.
  - [x] Explain why worker success alone is not the success metric.
- [x] P31.4 Planning note, roadmap tranche, and closeout (#226)
  - [x] Preserve the raw developer framing as a dated note.
  - [x] Promote the delegation economics strategy into public-safe notes.
  - [x] Update roadmap and changelog.
  - [x] Run governance verification.

Phase 31 acceptance criteria:

- Agent Workbench has a public-safe token/cash economics model for delegation
  decisions.
- The model accounts for paid supervisor tokens, worker tokens, overhead,
  verification, retry, cleanup, and direct-work counterfactuals.
- The model identifies why too-small and too-large task bundles can both be
  net-negative.

## Phase 32: Task Taxonomy And Delegation Suitability

Parent issue: #228

Branch: `feature/p32-task-taxonomy-delegation-suitability`

Status: complete

Goal: classify UBC-FRESH development work types by delegation suitability,
expected worker value, and risk.

Planned tasks:

- [x] P32.1 Task-type taxonomy (#229)
  - [x] Classify evidence intake, roadmap review, docs proposal, issue triage,
    test design, patch proposal, mechanical edits, GitHub hygiene, and release
    closeout.
  - [x] Map each task type to the phase/task/subtask planning hierarchy.
- [x] P32.2 Suitability criteria (#230)
  - [x] Define good delegation candidates.
  - [x] Define poor delegation candidates.
  - [x] Define split-or-supervise-more cases.
- [x] P32.3 Authority-level mapping (#231)
  - [x] Map task types to default worker authority levels.
  - [x] Identify nondelegable supervisor actions.
  - [x] Identify candidate restricted-tool experiments.
- [x] P32.4 Documentation and closeout (#232)
  - [x] Add task taxonomy planning notes.
  - [x] Link taxonomy from relevant playbooks.
  - [x] Run governance verification.

Phase 32 acceptance criteria:

- Agent Workbench has a reusable taxonomy of task types relevant to UBC-FRESH
  project development.
- Each task type has a default delegation suitability assessment.
- The taxonomy explains which task classes should usually be done directly.

## Phase 33: Worker Model Capability Profiles

Parent issue: #234

Branch: `feature/p33-worker-model-capability-profiles`

Status: complete

Goal: record per-model capability profiles for installed Ollama workers so
delegation choices reflect observed model behavior rather than generic model
rankings.

Planned tasks:

- [x] P33.1 Capability-card template (#235)
  - [x] Define fields for model name, host inventory evidence, task strengths,
    failure modes, loop risk, ticket-shape sensitivity, and recommended
    authority limits.
- [x] P33.2 Initial qwen-family profiles (#236)
  - [x] Summarize observed `qwen3-coder:latest` behavior.
  - [x] Summarize observed `qwen3-coder-next:latest` behavior.
  - [x] Keep claims scoped to observed Agent Workbench tickets.
- [x] P33.3 Model comparison evidence links (#237)
  - [x] Link capability cards to comparison summaries and worker evidence.
  - [x] Distinguish task-local observations from broad model rankings.
  - [x] Add a planned `gpt-oss:*` family lane for future comparison.
- [x] P33.4 Documentation and closeout (#238)
  - [x] Add model capability notes.
  - [x] Update roadmap and changelog.
  - [x] Run governance verification.

Phase 33 acceptance criteria:

- Agent Workbench has a model capability-card format.
- Initial installed-worker profiles are evidence-scoped and public-safe.
- Capability cards are usable inputs for later delegation decisions.
- `gpt-oss:*` is represented as a planned comparison family without unsupported
  installed-run claims.

## Phase 34: Delegation Decision Engine V0

Parent issue: #240

Branch: `feature/p34-delegation-decision-engine-v0`

Status: complete

Goal: implement a transparent rules-based recommender that helps the supervisor
decide whether to delegate, split, retry, or do a task directly.

Planned tasks:

- [x] P34.1 Decision input contract (#241)
  - [x] Define task bundle, task type, roadmap level, risk, model, authority,
    and expected verification fields.
  - [x] Keep the first input format simple and inspectable.
- [x] P34.2 Rules-based recommendation logic (#242)
  - [x] Recommend `delegate`, `do-directly`, `split-smaller`,
    `needs-human-decision`, or `defer`.
  - [x] Include reason strings for every recommendation.
  - [x] Avoid hidden scoring that the supervisor cannot audit.
- [x] P34.3 CLI/report surface (#243)
  - [x] Add a command or report helper for evaluating candidate task bundles.
  - [x] Render the economics terms that drove the recommendation.
  - [x] Keep outputs public-safe and easy to paste into planning notes.
- [x] P34.4 Dogfood and closeout (#244)
  - [x] Evaluate candidate tasks from a real project roadmap.
  - [x] Compare recommendations with supervisor judgment.
  - [x] Run package verification.

Phase 34 acceptance criteria:

- Agent Workbench can produce a transparent delegation recommendation for a
  candidate task bundle.
- Recommendations expose token-priced economics and risk assumptions behind
  them.
- The first decision engine is rules-based rather than ML-based.
- Planned or missing model profiles are handled conservatively.

## Phase 35: Real-Project Pilot Accounting

Parent issue: #250

Branch: `feature/p35-real-project-pilot-accounting`

Status: complete

Goal: run multiple real-project delegation pilots with explicit accounting so
Agent Workbench can estimate whether delegation is producing net benefit.

Planned tasks:

- [x] P35.1 Pilot selection protocol (#251)
  - [x] Choose candidate tasks from a live project roadmap.
  - [x] Include varied task sizes and task types.
  - [x] Avoid project-critical-path tasks for early experiments.
- [x] P35.2 Delegation accounting record (#252)
  - [x] Record paid supervisor input/output tokens, worker input/output tokens,
    token price assumptions, verification, retry, cleanup, and direct-work
    counterfactual estimates.
  - [x] Record accepted, rejected, and needs-evidence claims.
  - [x] Record whether the worker changed the supervisor decision.
- [x] P35.3 Pilot execution and synthesis (#253)
  - [x] Provide a CLI synthesis surface for several proposal-assist pilots.
  - [x] Synthesize net-benefit estimates.
  - [x] Identify task/model/protocol pairs that appear promising or poor.
- [x] P35.4 Documentation and closeout (#254)
  - [x] Add sanitized pilot accounting notes.
  - [x] Update roadmap and changelog.
  - [x] Run verification.

Phase 35 acceptance criteria:

- Agent Workbench has real-project delegation records with token/cash
  cost-benefit fields.
- The pilot accounting distinguishes useful imperfect proposals from costly
  failures.
- The synthesis identifies at least one promising and one poor delegation class,
  or explains why evidence is still insufficient.

## Phase 36: Policy Tuning Loop

Parent issue: #256

Branch: `feature/p36-policy-tuning-loop`

Status: complete

Goal: turn pilot accounting into a repeatable policy-tuning loop for task
sizing, model selection, ticket shape, and retry limits.

Planned tasks:

- [x] P36.1 Outcome schema (#257)
  - [x] Define outcome fields needed to tune delegation policy over time.
  - [x] Preserve enough detail for later empirical analysis without tracking
    raw private transcripts.
- [x] P36.2 Tuning rules (#258)
  - [x] Define how positive and negative outcomes update task suitability.
  - [x] Define how repeated failures lower model/task trust.
  - [x] Define retry and bailout threshold updates.
- [x] P36.3 Reporting surface (#259)
  - [x] Summarize policy changes after pilot batches.
  - [x] Show before/after recommendations for representative task bundles.
  - [x] Keep all policy changes auditable by the supervisor.
- [x] P36.4 Future ML boundary (#260)
  - [x] Define what data volume and quality would be required before an ML
    policy optimizer is worth attempting.
  - [x] Keep ML optimization explicitly out of the first tuning loop unless a
    later phase activates it.

Phase 36 acceptance criteria:

- Agent Workbench can update delegation policy from observed pilot outcomes.
- The tuning loop remains transparent and supervisor-auditable.
- The roadmap has a clear boundary between rules-based tuning and any future ML
  inference engine.

## Phase 37: Artifact And Workflow Contract Model

Parent issue: #262

Branch: `feature/p37-artifact-workflow-contracts`

Status: complete

Goal: define the durable artifact and workflow contract layer needed to move
from ad hoc worker tickets toward reproducible AI-assisted scientific and
software workbenches.

Planned tasks:

- [x] P37.1 Artifact vocabulary (#263)
  - [x] Define source artifact, generated artifact, promoted artifact, and
    rejected artifact.
  - [x] Record provenance, verifier, and supervisor decision fields.
- [x] P37.2 Workflow step contract (#264)
  - [x] Define input artifacts, transformation, implementation, output
    artifacts, verification, and token/cash accounting.
  - [x] Keep the contract compatible with existing evidence summaries and
    decision packets.
- [x] P37.3 Example workflow records (#265)
  - [x] Create examples for software task review, documentation proposal, paper
    outline, and benchmark proposal.
  - [x] Keep examples public-safe and generic across UBC-FRESH projects.
- [x] P37.4 Documentation and closeout (#266)
  - [x] Add planning notes.
  - [x] Update roadmap and changelog.
  - [x] Run verification.

Phase 37 acceptance criteria:

- Agent Workbench has an artifact-first workflow vocabulary.
- Workflow records can explain what was transformed, by whom or what, with what
  evidence, and at what token/cash cost.
- The contract does not require replacing existing tools such as Git, CI,
  notebooks, Snakemake, FreshForge, or project-specific CLIs.

## Phase 38: Role, Capability, And Implementation Model

Parent issue: #268

Branch: `feature/p38-role-capability-implementation`

Status: complete

Goal: separate persistent project roles from capabilities and implementation
choices so workflows can swap local models, paid models, humans, scripts, or
external tools without rewriting the workflow.

Planned tasks:

- [x] P38.1 Role model (#269)
  - [x] Define role identity, scope, allowed artifacts, and responsibility.
  - [x] Include examples such as reviewer, programmer, analyst, and editor.
- [x] P38.2 Capability model (#270)
  - [x] Define bounded capabilities such as evidence intake, claim review,
    patch proposal, test-design proposal, and token accounting.
  - [x] Link capabilities to task taxonomy and delegation policy.
- [x] P38.3 Implementation mapping (#271)
  - [x] Map capabilities to implementations such as local qwen, `gpt-oss:*`,
    paid supervisor model, human, script, or external workflow tool.
  - [x] Use model profiles and decision-engine outputs as inputs.
- [x] P38.4 Documentation and closeout (#272)
  - [x] Add planning notes.
  - [x] Update roadmap and changelog.
  - [x] Run verification.

Phase 38 acceptance criteria:

- Agent Workbench can describe a role, capability, and implementation without
  conflating them.
- Model swaps do not change the abstract workflow contract.
- The model remains compatible with conservative worker authority levels.
- FreshForge and project-native tools are treated as implementation candidates,
  not systems to replace.

## Phase 39: Reusable Scientific Workbench Templates

Parent issue: #274

Branch: `feature/p39-reusable-workbench-templates`

Status: complete

Goal: sketch reusable project workbench templates for common UBC-FRESH work
without creating a heavyweight workflow engine or replacing FreshForge-style
project-native tools.

Planned tasks:

- [x] P39.1 Template scope (#275)
  - [x] Define first template families for software, paper, proposal, and
    benchmark tasks.
  - [x] Keep templates as Markdown/JSON planning artifacts first.
- [x] P39.2 Artifact layout examples (#276)
  - [x] Show how tickets, evidence, decision packets, reports, and promoted
    outputs relate.
  - [x] Avoid project-specific private assumptions.
- [x] P39.3 Integration boundaries (#277)
  - [x] Identify where existing tools such as GitHub Actions, Quarto,
    notebooks, Snakemake, FreshForge, or project CLIs should be reused rather
    than replaced.
- [x] P39.4 Documentation and closeout (#278)
  - [x] Add planning notes.
  - [x] Update roadmap and changelog.
  - [x] Run verification.

Phase 39 acceptance criteria:

- Agent Workbench has public-safe starter templates for reproducible
  AI-assisted scientific/software workbench tasks.
- Templates make agents boring: roles and artifacts are primary; model/runtime
  implementation is secondary.
- Templates are integration envelopes around existing project tools, not a new
  orchestration framework.
- Templates reuse FreshForge's graph vocabulary for workflow, nodes, providers,
  dependencies, artifacts, and diagnostics.

## Phase 40: Observability And Token-Cost Ingestion

Parent issue: #280

Branch: `feature/p40-token-cost-ingestion`

Status: complete

Goal: evaluate how to ingest token/cost observability records into Agent
Workbench pilot accounting without committing raw traces or provider secrets.

Planned tasks:

- [x] P40.1 Observability source audit (#281)
  - [x] Compare SDK result files, provider usage metadata, and PostHog-style AI
    observability exports.
  - [x] Identify fields needed for P35/P36 token/cash accounting.
- [x] P40.2 Sanitized import contract (#282)
  - [x] Define a public-safe token/cost record shape.
  - [x] Exclude prompts, raw transcripts, provider URLs, headers, and personal
    paths.
- [x] P40.3 Prototype import or render helper (#283)
  - [x] Add a small local helper only if it reduces manual accounting friction.
  - [x] Keep raw exports under ignored runtime paths.
- [x] P40.4 Documentation and closeout (#284)
  - [x] Add planning notes.
  - [x] Update roadmap and changelog.
  - [x] Run verification.

Phase 40 acceptance criteria:

- Agent Workbench has a clear path for importing or summarizing token/cost
  usage without exposing raw traces.
- Observability remains a measurement aid, not a dependency for basic pilot
  workflows.

## Phase 41: FreshForge Graph Integration Spike

Parent issue: #286

Branch: `feature/p41-freshforge-graph-integration`

Status: complete

Goal: test FreshForge as the optional structural graph-validation layer for
Agent Workbench agentic role workflows.

Planned tasks:

- [x] P41.1 Optional FreshForge dependency and graph command surface (#287)
  - [x] Add a `graph` optional dependency extra for FreshForge.
  - [x] Add `agent-workbench graph validate --input <path>`.
  - [x] Keep base package behavior working without FreshForge installed.
- [x] P41.2 FreshForge-valid agentic graph template (#288)
  - [x] Add `templates/workbench_templates/agentic_workflow_graph.json`.
  - [x] Move Agent Workbench-specific metadata into FreshForge-compatible
    `parameters`, `artifacts`, and `provenance` fields.
  - [x] Validate the template with FreshForge structural validation.
- [x] P41.3 Validation behavior and diagnostics (#289)
  - [x] Report workflow id, node count, and diagnostics.
  - [x] Exit nonzero on structural errors.
  - [x] Record that provider-registry validation is deferred.
- [x] P41.4 Documentation, roadmap tranche, and closeout (#290)
  - [x] Add P41 planning notes.
  - [x] Add P42-P46 roadmap tranche.
  - [x] Update README and changelog.
  - [x] Run verification.

Phase 41 acceptance criteria:

- Agent Workbench exposes a documented `graph validate` command.
- The command uses FreshForge structural workflow validation when the optional
  dependency is installed.
- The command fails clearly when FreshForge is missing and tells the user how
  to install the optional graph extra.
- The existing graph envelope has a FreshForge-valid tracked companion
  template.
- P42-P46 are planned as the next graph-backed delegation tranche.

## Phase 42: Agent Metadata Convention

Parent issue: #292

Branch: `feature/p42-agent-metadata-convention`

Status: complete

Goal: define the stable Agent Workbench metadata convention inside
FreshForge-compatible graph documents.

Planned tasks:

- [x] P42.1 Metadata field placement (#293)
  - [x] Define which fields belong in `parameters`, `artifacts`, and
    `provenance`.
  - [x] Avoid adding Agent Workbench-only top-level graph fields.
- [x] P42.2 Role and capability metadata (#294)
  - [x] Define role, capability, authority level, implementation, and model
    profile references.
- [x] P42.3 Evidence and decision metadata (#295)
  - [x] Define evidence packet, claim review, supervisor decision, and
    promotion metadata.
- [x] P42.4 Documentation and closeout (#296)
  - [x] Add examples and update templates.
  - [x] Run validation and governance checks.

Phase 42 acceptance criteria:

- Agent Workbench can represent its delegation metadata without forking the
  FreshForge graph shape.
- The convention is documented enough for graph-backed pilot workflows.

## Phase 43: Graph-Backed Pilot Workflow

Parent issue: #298

Branch: `feature/p43-graph-backed-pilot-workflow`

Status: complete

Goal: represent one real Agent Workbench deployment pilot as a
FreshForge-compatible graph and use Agent Workbench evidence/accounting around
that graph.

Planned tasks:

- [x] P43.1 Pilot selection (#299)
  - [x] Choose one bounded real-project pilot that is not on a project critical
    path.
- [x] P43.2 Graph representation (#300)
  - [x] Encode supervisor selection, worker proposal, project-native
    verification, and supervisor promotion as graph nodes.
- [x] P43.3 Evidence and accounting linkage (#301)
  - [x] Link evidence summaries and token/cost records to graph nodes.
- [x] P43.4 Pilot synthesis and closeout (#302)
  - [x] Record what graph structure helped or hindered.

Phase 43 acceptance criteria:

- A real pilot can be described as a FreshForge-compatible graph without making
  Agent Workbench the executor.
- Evidence and accounting can be associated with specific graph nodes.

## Phase 44: Graph-Aware Delegation Decision Engine

Parent issue: #304

Branch: `feature/p44-graph-aware-decision-engine`

Status: complete

Goal: upgrade delegation decisions from isolated task descriptions to graph-node
recommendations.

Planned tasks:

- [x] P44.1 Graph-node decision input (#305)
  - [x] Resolve task type, authority, dependencies, and verification context
    from graph nodes.
- [x] P44.2 Recommendation logic (#306)
  - [x] Recommend delegate, split, direct, defer, or human decision per node.
- [x] P44.3 Report surface (#307)
  - [x] Render graph-level and node-level delegation guidance.
- [x] P44.4 Dogfood and closeout (#308)
  - [x] Compare graph-aware recommendations against existing P34-style
    task-only recommendations.

Phase 44 acceptance criteria:

- Delegation recommendations can account for upstream/downstream graph context.
- Supervisor-only nodes remain nondelegable regardless of local model
  capability.

## Phase 45: Per-Node Token Economics

Parent issue: #310

Branch: `feature/p45-per-node-token-economics`

Status: complete

Goal: attribute paid supervisor tokens, local worker tokens, verification cost,
cleanup, and net benefit to graph nodes.

Planned tasks:

- [x] P45.1 Node-level token/cost record (#311)
  - [x] Extend token/cost records with graph and node identifiers.
- [x] P45.2 Graph economics synthesis (#312)
  - [x] Summarize which node types save paid supervisor tokens.
- [x] P45.3 Policy feedback (#313)
  - [x] Feed node-level economics into policy tuning.
- [x] P45.4 Documentation and closeout (#314)
  - [x] Update accounting docs and examples.

Phase 45 acceptance criteria:

- Agent Workbench can answer which graph-node classes produce useful token/cash
  savings.
- Token economics remain priced by token counts, not wall-clock minutes.

## Phase 46: FreshForge Dependency Decision

Parent issue: #316

Branch: `feature/p46-freshforge-dependency-decision`

Status: complete

Goal: decide whether FreshForge becomes a required Agent Workbench dependency,
stays optional, or remains behind a compatibility adapter.

Planned tasks:

- [x] P46.1 Evidence review (#317)
  - [x] Review P41-P45 implementation friction, validation coverage, and
    pilot usefulness.
- [x] P46.2 Dependency options (#318)
  - [x] Compare required dependency, optional dependency, and adapter-only
    strategies.
- [x] P46.3 Recommendation (#319)
  - [x] Record a decision with concrete package and maintenance implications.
- [x] P46.4 Closeout (#320)
  - [x] Update roadmap, README, package metadata, and planning notes according
    to the decision.

Phase 46 acceptance criteria:

- The FreshForge relationship is no longer ambiguous.
- Agent Workbench avoids a parallel graph engine unless the FreshForge
  integration failed for concrete technical reasons.

## Phase 47: FreshForge Deployment Test Batch

Parent issue: #322

Branch: `feature/p47-freshforge-deployment-test-batch`

Status: complete

Goal: queue a non-trivial FreshForge deployment-test batch that uses Agent
Workbench graph, decision, and token-economics surfaces against FreshForge
P16-P18 roadmap work.

Planned tasks:

- [x] P47.1 Roadmap cleanup and batch scope (#323)
  - [x] Mark P46 complete after merged closeout.
  - [x] Add a public-safe FreshForge deployment-test batch note.
- [x] P47.2 FreshForge P16 provider evidence test packet (#324)
  - [x] Add a graph-backed packet for provider evidence conventions.
  - [x] Validate and render the packet.
- [x] P47.3 FreshForge P17 matrix export test packet (#325)
  - [x] Add a graph-backed packet for matrix aggregation and exports.
  - [x] Validate and render the packet.
- [x] P47.4 FreshForge P18 release-readiness test packet and closeout (#326)
  - [x] Add a graph-backed packet for release-readiness review.
  - [x] Run graph decision reports and governance checks.

Phase 47 acceptance criteria:

- Agent Workbench roadmap status matches GitHub closeout state for P46.
- Three FreshForge deployment-test packet graphs validate with
  `--agent-metadata`.
- Graph decision reports identify worker-proposal nodes as delegation
  candidates and release/closeout nodes as supervisor-owned.
- No FreshForge repo files are mutated by this phase.

## Phase 48: Phase-Scale A/B Token Economics Benchmark

Parent issue: #328

Branch: `feature/p48-phase-scale-ab-token-economics`

Status: complete

Goal: create the first phase-scale A/B token-economics benchmark protocol so
Agent Workbench can compare direct paid-supervisor implementation against
graph-backed delegated implementation on the same FreshForge phase target.

Planned tasks:

- [x] P48.1 Benchmark protocol and lane design (#329)
  - [x] Define direct supervisor and delegated graph lanes.
  - [x] Use isolated worktrees from the same FreshForge start commit.
- [x] P48.2 Benchmark record validation and rendering (#330)
  - [x] Add benchmark validation and rendering command surface.
  - [x] Include token fields, price assumptions, validation commands, and
    win/loss rules.
- [x] P48.3 FreshForge P16 benchmark packet (#331)
  - [x] Add the FreshForge P16 phase-scale benchmark record.
  - [x] Link the delegated lane to the P47 P16 graph packet.
- [x] P48.4 Verification and closeout (#332)
  - [x] Validate and render the benchmark packet.
  - [x] Update roadmap and changelog.

Phase 48 acceptance criteria:

- A tracked benchmark record template exists for phase-scale direct-vs-delegated
  comparisons.
- Agent Workbench can validate and render the benchmark record.
- The FreshForge P16 benchmark packet identifies target repo, start commit,
  direct lane, delegated lane, rollback/worktree isolation, token fields,
  validation commands, and win/loss decision rules.
- P48 queues execution without mutating FreshForge.

## Phase 49: Benchmark Worktree Preparation

Parent issue: #334

Branch: `feature/p49-benchmark-worktree-prep`

Status: complete

Goal: turn the P48 phase-scale benchmark packet into an executable setup step
by preparing isolated FreshForge benchmark worktrees for the direct-supervisor
and delegated-graph lanes from the same recorded start commit.

Planned tasks:

- [x] P49.1 Worktree preparation contract (#335)
  - [x] Define the worktree setup boundary and safety rules.
  - [x] Document the FreshForge P16 setup protocol.
- [x] P49.2 Benchmark prepare command (#336)
  - [x] Add `agent-workbench benchmark prepare-worktrees`.
  - [x] Support dry-run and optional Markdown report output.
- [x] P49.3 FreshForge P16 setup dry run (#337)
  - [x] Dry-run the FreshForge lane setup.
  - [x] Create or verify lane worktrees from the same start commit.
- [x] P49.4 Verification and closeout (#338)
  - [x] Run command-surface smoke, benchmark validation, lint, and diff checks.
  - [x] Confirm FreshForge `main` remains clean.

Phase 49 acceptance criteria:

- Agent Workbench has a command that can prepare lane worktrees from the tracked
  P48 benchmark record.
- The command keeps script/package lookup anchored in Agent Workbench while
  operating on the target FreshForge repo.
- The FreshForge P16 direct and delegated lane branches/worktrees can be created
  from the same recorded start commit or a precise blocker is reported.
- Roadmap, changelog, planning note, issues, and PR agree.

## Phase 50: FreshForge P16 A/B Benchmark Run

Parent issue: #340

Branch: `feature/p50-freshforge-p16-ab-benchmark-run`

Status: complete

Goal: run the first real phase-scale A/B token economics benchmark using
FreshForge P16 as the target, starting with the direct-supervisor baseline lane
and iterating until the maintainer explicitly says the phase is done.

Active tasks:

- [ ] P50.1 Direct-supervisor FreshForge P16 baseline iteration (#341)
  - [x] Perform substantive FreshForge P16 work in
    `../freshforge-benchmark-p16-direct`.
  - [x] Report first-iteration output to the maintainer.
- [ ] P50.2 Direct-lane evidence and token accounting capture (#342)
  - [x] Record direct-lane command, file, and status evidence.
  - [x] Record paid supervisor token usage when available.
  - [x] Add mandatory Codex supervisor-token checkpoint commands with
    fresh-input, cached-input, output, and reasoning-output separation.
- [ ] P50.3 Delegated-graph FreshForge P16 iteration (#343)
  - [x] Run delegated-lane work from the same start commit.
  - [x] Preserve worker and supervisor token evidence.
- [x] P50.4 A/B comparison and benchmark record update (#344)
  - [x] Compare direct and delegated lanes after both have evidence.
  - [x] Record the target reassessment: broad FreshForge API-design work is a
    low-yield benchmark class for current local workers; high-volume
    document-metadata indexing is the stronger next delegation target.
  - [x] Establish that future benchmark economics claims require named
    supervisor-token start/end checkpoints for each supervisor-owned subtask.
  - [x] Add persistent delegation experiment observation records for scale
    tests and future policy tuning.
  - [x] Plan supervisor-overhead delegation so reporting and orchestration burn
    can be separated from source-level supervision.
  - [x] Add quiet batch orchestration and reporting-worker templates.
  - [x] Dogfood a local `gpt-oss:20b` reporting-worker draft over sanitized
    MP11 fixed-x8 benchmark summaries.
  - [x] Record the follow-up direction for excluding GitHub hygiene from task
    economics and representing recurring orchestration as workflow graphs.
  - [x] Run a first reporting A/B iteration and record the token-ledger overlap
    lesson for non-overlapping span discipline.
  - [x] Run a corrected non-overlapping reporting A/B and record the small
    isolated reporting savings signal.
  - [x] Promote the document-library indexing direction into generic workflow
    templates after MP11 showed the task class is high-potential.
  - [x] Update benchmark records with actual token economics where evidence is
        strong enough, and record explicit limits where attribution remains
        incomplete.
  - [x] Reframe the next benchmark direction around high-volume document
        metadata indexing rather than broad FreshForge API-design work.
  - [x] Add managed document-library workflow templates as the next reusable
        high-potential delegation lane.
- [x] P50.5 Maintainer-reviewed phase closeout (#345)
  - [x] Close only after the maintainer explicitly says P50 is done.
  - [x] Plan P51-P54 as the next managed-delegation roadmap tranche.

Phase 50 acceptance criteria:

- FreshForge P16 direct-lane work produces substantive code/docs/tests or a
  precise blocker.
- Direct-lane supervisor token usage is recorded from actual Codex
  `token_count` checkpoints with input, cached input, output, and reasoning
  output deltas.
- Delegated-lane work uses Agent Workbench worker/delegation surfaces rather
  than replaying the direct lane by hand.
- The final comparison distinguishes paid supervisor token cost, zero-cash
  local worker token usage, rework burden, verification outcome, and decision
  quality.
- Future benchmark economics claims are blocked unless setup, ticket build,
  worker orchestration, worker-output summarization, supervisor audit, tracked
  updates, GitHub hygiene, and any direct-supervisor baseline spans have
  start/end supervisor-token checkpoints.
- Scale-series benchmark output is recorded as sanitized experiment
  observations so later policy tuning can mine task size, model, protocol,
  outcome, and economics tuples.
- The phase records whether the benchmark task class itself appears profitable
  before further paid supervisor tokens are spent on that class.
- P50 remained open until the maintainer explicitly said the phase is done.

## Phase 51: Managed Delegation Workflow Lanes

Parent issue: #347

Branch: `feature/p51-managed-delegation-workflows`

Status: complete

Goal: turn P50's managed-delegation lessons into reusable graph templates,
ticket patterns, stop rules, and role boundaries for tightly guardrailed local
worker lanes.

Planned tasks:

- [x] P51.1 Managed role graph vocabulary (#351)
  - [x] Define extractor, self-auditor, repairer, convergence-checker, and
        supervisor-auditor node roles.
  - [x] Mark script-owned, local-worker-owned, and supervisor-owned boundaries.
- [x] P51.2 Iteration and stop-condition templates (#352)
  - [x] Define max-iteration, no-improvement, format-failure, and budget
        stop rules.
  - [x] Define escalation paths to supervisor repair, abandon, or scale.
- [x] P51.3 Document-library graph update (#353)
  - [x] Add local self-audit and delegated repair nodes to the document-library
        workflow graph.
  - [x] Keep local self-audit framed as defect reduction, not validation.

## Phase 52: Local Self-Audit And Repair Loop

Parent issue: #348

Branch: `feature/p52-local-self-audit-repair-loop`

Status: complete

Goal: dogfood a bounded local self-audit plus repair loop on the MP11 audit
sample and measure whether zero-cash worker iterations reduce paid supervisor
audit/repair cost.

Planned tasks:

- [x] P52.1 Self-audit and repair ticket templates (#355)
  - [x] Add local self-audit ticket template.
  - [x] Add delegated repair iteration ticket template.
- [x] P52.2 MP11 repair-loop experiment (#356)
  - [x] Run a local Ollama self-audit/repair loop on the qwen x16 audit sample.
  - [x] Record worker tokens, format errors, repair yield, and convergence
        behavior.
- [x] P52.3 Supervisor delta-review economics (#357)
  - [x] Measure paid supervisor delta-review tokens.
  - [x] Compare direct audit cost against repair-assisted audit cost.

## Phase 53: Document Library Index Pilot

Parent issue: #349

Branch: `feature/p53-document-library-index-pilot`

Status: complete

Goal: apply the document-library indexing workflow to all public TSA 23 TSR PDF
documents from 1995 onward so MP11-derived settings can later be tested for
cross-document generalization.

Planned tasks:

- [x] P53.1 TSA23 corpus selection and FEMIC materialization script (#359)
  - [x] Select all public TSA 23 TSR PDFs from 1995 onward.
  - [x] Add a tracked script that resolves the corpus from FEMIC metadata.
  - [x] Exercise FEMIC-backed materialization into ignored runtime storage.
  - [x] Record sanitized corpus registry entries.
- [x] P53.2 Multi-document extraction pilot scaffold (#360)
  - [x] Select at least two pilot documents across the TSA 23 corpus.
  - [x] Add comparable chunk, extraction, worker, and audit metadata scaffolds.
  - [x] Preserve source, model, chunk, and token metadata fields without raw
        PDFs, raw text, or worker outputs.
- [x] P53.3 Cross-document audit calibration plan (#361)
  - [x] Define cross-document audit strata and tracked metrics.
  - [x] Record whether task settings generalize or need retuning as the next
        worker-run question rather than claiming an unrun audit.

## Phase 54: Delegation Loop Policy Tuning

Parent issue: #350

Branch: `feature/p54-delegation-loop-policy-tuning`

Status: complete

Goal: convert managed-loop observations into conservative, explainable policy
guidance for splitting, iterating, self-auditing, repairing, escalating, or
stopping delegated work.

Planned tasks:

- [x] P54.1 Managed-loop decision rules (#363)
  - [x] Define task-shape thresholds and bailout rules.
  - [x] Define when to run self-audit, repair, supervisor audit, or direct
        supervisor completion.
- [x] P54.2 Evidence mining and policy update (#364)
  - [x] Mine experiment registry fields for cost/quality signals.
  - [x] Update delegation decision guidance with managed-loop recommendations.
- [x] P54.3 Missing-evidence reporting (#365)
  - [x] Make missing evidence explicit rather than inferred.
  - [x] Keep model-specific guidance scoped to observed task classes.

## Phase 55: TSA23 First Real Indexing Run

Parent issue: #367

Branch: `feature/p55-tsa23-first-indexing-run`

Status: ready for PR review; parent issue remains open until merge

Goal: run the first real multi-run document-indexing experiment over the P53
TSA23 corpus, with enough model/chunk/document variation to produce useful
delegation evidence rather than a one-off anecdote.

Planned tasks:

- [x] P55.1 PDF chunk extraction and worker-ticket generation (#368)
  - [x] Build reproducible chunk/ticket generation from the P53 corpus
        registry.
  - [x] Extract ignored page-window chunks for the three selected TSA23 pilot
        PDFs.
  - [x] Track sanitized chunk manifests and runtime/eval manifests.
  - [x] Dry-run all generated eval manifests without provider contact.
  - [x] Decide whether to revise chunk size/OCR before worker contact.
- [x] P55.2 No-tool local-worker extraction run (#369)
  - [x] Run Wave 1 single-model smoke across three documents.
  - [x] Run Wave 1.1 full-document smoke across the three 2012 documents.
  - [x] Run Wave 2 model A/B on identical document/chunk tickets.
  - [x] Run Wave 3 ticket-size scale tests if Wave 1/2 gates pass.
  - [x] Remove the hidden max-record ticket guardrail before further
        extraction tests.
  - [x] Run Wave 3.1 chunk-orchestrated coverage after regenerating uncapped
        tickets.
  - [x] Run Wave 3.2 Qwen3.6 BF16 chunk A/B against the Wave 3.1
        `qwen3-coder:latest` baseline.
  - [x] Run Wave 7 dual-model typed fact ensemble candidate extraction.
  - [x] Run Wave 8 disagreement-only verification if Wave 7 candidate JSON
        parses.
  - [x] Test DeepSeek-R1 as validation critic and Qwen3-Coder-Next as strict
        JSON repair executor.
  - [x] Defer Wave 4 repeatability and Wave 5 content probes; P55 produced
        enough signal to move into consolidation and recipe design before more
        live runs.
- [x] P55.3 Supervisor spot-check and scale/stop decision (#370)
  - [x] Run measured supervisor audit calibration slices.
  - [x] Record accepted, repairable, rejected, missing-evidence, and
        model-provenance counts in tracked summaries.
  - [x] Report wave results and stop further P55 live runs pending PR review
        and follow-on consolidation phases.

Closeout decision: P55 should merge as an evidence packet, not as a finished
production document-indexing workflow. The useful next step is consolidation,
budget enforcement, outcome semantics, and reusable recipe packaging before any
larger TSA23 or MP11 indexing run.
