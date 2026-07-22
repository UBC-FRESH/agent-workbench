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
| P55 TSA23 first real indexing run | #367 | `feature/p55-tsa23-first-indexing-run` | Complete |
| P56 Authority hierarchy and supervisor contract scaffold | #372 | `feature/p56-authority-hierarchy-supervisor-contracts` | Complete |
| P57 VS Code subagent supervisor-worker spike | #378 | `feature/p57-vscode-subagent-supervisor-worker-spike` | Complete |
| P58 Evidence consolidation and active-phase reconciliation | #384 | `feature/p58-evidence-consolidation-active-phase-reconciliation` | Complete |
| P59 Paid-supervisor budget gates and stop rules | #390 | `feature/p59-supervisor-budget-gates` | Complete |
| P60 Outcome semantics and scoring split | #396 | `feature/p60-outcome-semantics-scoring-split` | Complete |
| P61 Packaged local-supervisor workflow v1 | #402 | `feature/p61-packaged-local-supervisor-workflow-v1` | Complete |
| P62 Document-indexing workflow recipe v1 | #408 | `feature/p62-document-indexing-recipe-v1` | Complete |
| P63 Bounded TSA23 recipe pilot | #414 / PR #419 | `feature/p63-bounded-tsa23-recipe-pilot` | Complete |
| P64 Deployment environment and operator playbook | #420 / PR #425 | `feature/p64-deployment-environment-operator-playbook` | Complete |
| P65 Copilot session archive | #426 | `feature/p65-copilot-session-archive` | Complete |
| P66 Task-level delegation protocol | #431 | `feature/p66-task-level-delegation-protocol` | Complete |
| P67 Heartbeat and nudge protocol | #437 | `feature/p67-heartbeat-nudge-protocol` | Complete |
| P68 Copilot task controller v0 | #448 | `feature/p68-copilot-task-controller-v0` | Complete |
| P69 Behavior analytics from archives | #454 | `feature/p69-behavior-analytics-from-archives` | Complete |
| P70 FEMIC P108 repair dogfood | #461 / PR #484 | `feature/p70-femic-p108-repair-dogfood` | Complete |
| P71 Copilot SDK remote-control bridge | #466 / PR #472 | `feature/p71-copilot-sdk-remote-control-bridge` | Complete |
| P72 Copilot SDK custom agent profiles | #473 / PR #479 | `feature/p72-sdk-custom-agent-profiles` | Complete |
| P73 Standard Agent Workbench profile catalog | #480 / PR #483 | `feature/p73-standard-agent-profile-catalog` | Complete |
| P74 FoundryTK profile optimization | #481 / PR #482 | `feature/p74-foundrytk-profile-optimization` | Complete |
| P75 Comparable live overlay-selected SDK run battery | #485 | `feature/p75-live-overlay-sdk-run-battery` | Complete |
| P76 Profile evaluation aggregate comparison reports | #491 | `feature/p76-profile-evaluation-aggregate-reports` | Complete |
| P77 Profile contract repair plan | #496 | `feature/p77-profile-contract-repair-plan` | Complete |
| P78 Profile evidence review contract repair | #501 | `feature/p78-profile-evidence-review-contract` | Complete |
| P79 Repaired profile-evidence-review battery design | #507 | `feature/p79-repaired-profile-review-battery` | Complete |
| P80 Repaired profile-evidence-review battery execution | #512 | `feature/p80-repaired-profile-review-execution` | Complete |
| P81 Controller/session health gate for live SDK batteries | #518 | `feature/p81-controller-session-health-gate` | Complete |
| P82 Health-gated repaired profile-evidence-review battery | #524 | `feature/p82-health-gated-repaired-battery` | Complete |
| P83 Review-subject access contract repair | #530 | `feature/p83-review-subject-access-contract` | Complete |
| P84 Review-subject live access probe | #536 | `feature/p84-review-subject-live-access-probe` | Complete |
| P85 Health-gated repaired profile-evidence-review battery rerun | #542 | `feature/p85-health-gated-repaired-battery-rerun` | Complete |
| P86 Dev validation toolchain repair | #549 | `feature/p86-dev-validation-toolchain-repair` | Complete |
| P87 Real-project ROI roadmap reset | #551 | `feature/p87-real-project-roi-roadmap-reset` | Complete |
| P88 Real-corpus benchmark registry | #552 | `feature/p88-real-corpus-benchmark-registry` | Closeout |
| P89 Document-indexing recipe v2 | #553 | `feature/p89-document-indexing-recipe-v2` | Closeout |
| P90 Full-document candidate extraction run | #554 | `feature/p90-full-document-candidate-extraction` | Complete |
| P91 Reporting-worker decision packets | #555 | `feature/p91-reporting-worker-decision-packets` | Complete |
| P92 Whole-document supervisor pilot | #556 | `feature/p92-whole-document-supervisor-pilot` | Closeout |
| P93 Second public corpus application | #576 | `feature/p93-second-public-corpus-application` | Complete |
| P94 Project-owned index promotion | #578 | `feature/p94-project-owned-index-promotion` | Complete |
| P95 Retrieval and modelling-agent usability | #580 | `feature/p95-index-retrieval-usability` | Complete |
| P96 Yield and audit-cost model comparison | #585 | `feature/p96-yield-audit-cost-model-comparison` | Complete (qualified) |
| P97 Reusable workflow graph packaging | #592 | `feature/p97-reusable-workflow-graphs` | Complete — merged via PR #596 at `b2b929f`; parent issue #592 closed |
| P98 Reporting-worker template packaging | #599 | `feature/p98-reporting-worker-templates` | Complete |
| P99 Economics dashboard and release criteria | #601 | `feature/p99-economics-dashboard-release-criteria` | Complete — merged via PR #602; parent issue #601 closed |
| P100 Public alpha readiness review | #603 | `feature/p100-public-alpha-readiness-review` | Complete — merged via PR #604 |
| P101 Sphinx technical documentation and GitHub Pages | #598 | `feature/p101-sphinx-docs-github-pages` | Complete: Live at https://ubc-fresh.github.io/agent-workbench/, CI passing (BUILD+DEPLOY), Advisor alpha-readiness verified |
| P102 Native Codex + remote Ollama orchestration | #605 | `feature/p102-native-codex-ollama-orchestration` | Complete (qualified) |
| P103 Paid Coordinator economics trial | #611 | `feature/p103-paid-coordinator-economics-trial` | Complete (qualified) |
| P104 Canonical model pricing and economics provenance | #614 / PR #619 | `feature/p104-model-pricing-provenance` | Complete |
| P105 Matched public-corpus benchmark contract | #621 / PR #626 / PR #628 | `feature/p105-matched-public-corpus-contract` | Complete |
| P106 Matched direct-vs-delegated execution | #629 | `feature/p106-matched-roi-benchmark` | Complete (qualified) — quality validated; protocol and economics not accepted |
| P107 Economics decision and delegation policy | #644 | `feature/p107-delegation-economics-policy` | Complete (bounded tranche) — accepted native slices and control-layer integration recorded; no final cross-epoch ROI claim |
| P108 Fresh TSA23 slice preparation | TBD | `feature/p108-fresh-tsa23-slice-prep` | Planned - P107 gated |
| P109 Productive delegated TSA23 pilot | TBD | `feature/p109-productive-tsa23-pilot` | Planned — live-run gated |
| P110 Alpha readiness refresh and GitHub pre-release | TBD | `feature/p110-public-alpha-prerelease` | Planned — release gated |
| P111 Native recursive Codex UI delegation | #634 / PR #639 | `feature/p111-native-recursive-ui-delegation` | Complete — merged via PR #639; parent issue #634 closed |
| P113 Codex-Ollama function-tool adapter sandbox | #648 / PR #652 / PR #653 | `feature/p113-codex-ollama-function-tool-adapter` | Complete - PRs #652 and #653 merged; parent issue #648 closed; P107 remains parked pending a separate resume decision |
| P114 Codex-Ollama C4 capability parity and viability | #661 / PR #667 | `feature/p114-c4-ollama-capability-parity` | Complete - PR #667 merged; baseline P107 route admitted |
| P115 | Scientific artifact-inspection bridge pilot | #666 | `feature/p115-scientifactifact-inspection` | Active — rescoped to P118 native Agent Hub (Qwen3-coder profile, `runSubagent`) |
| P116 Event-driven supervision control plane | #669 / #710 | `feature/p116-event-driven-supervision-control-plane` | Complete — bounded native in-session control layer; no daemon or P107 economics claim |
| P117 Run-scoped supervision daemon | #686 | `feature/p117-run-scoped-supervision-daemon` | Complete — bounded run-scoped proof only; no unattended runtime claim |
| P118 FRESH vLLM Agent | #716 | `feature/p118-fresh-vllm-agent` | Active — P118.1 merged via PR #714; P118.2-P118.5 planned |
| P119 Blackwell vLLM concurrency profile | #719 / #720 | `feature/p119-vllm-blackwell-concurrency-profile` | Complete — sanitized playbook and bounded-concurrency guidance delivered via PR #720 |

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

Status: complete

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

## Phase 56: Authority Hierarchy And Supervisor Contract Scaffold

Parent issue: #372

Branch: `feature/p56-authority-hierarchy-supervisor-contracts`

Status: complete

Goal: formalize the authority hierarchy and supervisor job contract layer
needed for local Copilot/Ollama supervisors, worker subagents, and paid Codex
coordinator review.

Planned tasks:

- [x] P56.1 Authority schema and validators (#373)
  - [x] Define required developer, coordinator, supervisor, and worker roles.
  - [x] Validate workspace-root policy and wrong-root stop rules.
  - [x] Validate allowed tools, forbidden actions, stop conditions, success
        criteria, final signals, verification requirements, and public-safety
        posture.
  - [x] Validate supervisor report final status, artifacts, observations,
        blockers, and errors.
- [x] P56.2 Supervisor job templates (#374)
  - [x] Add generic supervisor job contract template.
  - [x] Add generic supervisor job report template.
  - [x] Add document-artifact audit supervisor contract template.
  - [x] Add document-artifact audit supervisor ticket template.
- [x] P56.3 CLI validation and rendering surface (#375)
  - [x] Add `agent-workbench authority validate`.
  - [x] Add `agent-workbench authority render`.
  - [x] Support contract and report validation/rendering.
  - [x] Render compact Markdown summaries for coordinator review.
- [x] P56.4 Planning, tests, and PR closeout (#376)
  - [x] Link P56 roadmap and planning notes to GitHub issues.
  - [x] Update `CHANGE_LOG.md`.
  - [x] Run focused authority tests.
  - [x] Open a P56-only PR against `main`.

## Phase 57: VS Code Subagent Supervisor-Worker Spike

Parent issue: #378

Branch: `feature/p57-vscode-subagent-supervisor-worker-spike`

Status: complete

Goal: test whether a VS Code Copilot/Ollama local supervisor can reliably
execute bounded supervisor-worker graph tasks through custom agents, subagent
calls, deterministic validators, and packaged launcher evidence.

Planned tasks:

- [x] P57.1 Custom-agent bridge and subagent handshake (#379)
  - [x] Add local-supervisor and result-auditor custom agent definitions.
  - [x] Harden bridge launch so it does not maximize the Copilot pane.
  - [x] Capture bridge evidence for expected model, permission mode, final
        marker, expected commands, expected output files, and deviations.
  - [x] Require reports to preserve subagent payload evidence when subagent
        invocation is attempted.
- [x] P57.2 Document-artifact audit materialization and validators (#380)
  - [x] Add materializers for document-artifact audit jobs and graph jobs.
  - [x] Add validators for document-artifact audit reports and graph reports.
  - [x] Add repair helpers for malformed graph reports.
  - [x] Track sanitized summaries while keeping raw runtime artifacts ignored.
- [x] P57.3 Graph batch packaged launcher evidence (#381)
  - [x] Add graph batch materialization and runner surfaces.
  - [x] Track sanitized summaries for accepted, rejected, aborted, and
        internal P57 runs.
  - [x] Add packaged launcher economics comparison.
  - [x] Document the pre-materialized ticket boundary and quiet-runtime output
        result.
- [x] P57.4 Economics summary, planning, tests, and PR closeout (#382)
  - [x] Link P57 roadmap and planning notes to GitHub issues.
  - [x] Update `CHANGE_LOG.md`.
  - [x] Run focused P57 test suite.
  - [x] Open a P57-only PR against `main`.

## Phase 58: Evidence Consolidation And Active-Phase Reconciliation

Parent issue: #384

Branch: `feature/p58-evidence-consolidation-active-phase-reconciliation`

Status: complete

Goal: turn the P55-P57 experimental state into a trustworthy decision base
before any more large live Copilot/Ollama experiments.

No new live worker, Copilot Chat, or Ollama runs are allowed in P58.

Planned tasks:

- [x] P58.1 Evidence register normalization (#385)
  - [x] Define accepted, quality-valid, diagnostic, stale, historical, and
        deferred evidence categories.
  - [x] Classify P55 evidence.
  - [x] Classify P56 evidence.
  - [x] Classify P57 evidence.
  - [x] Mark P50-era and overrun artifacts as historical or diagnostic where
        appropriate.
- [x] P58.2 Active-phase reconciliation (#386)
  - [x] Update P55 status and defer further extraction work.
  - [x] Update P56 status and move remaining policy detail to later phases.
  - [x] Update P57 status and defer further live full-batch retries.
  - [x] Keep P58 itself non-live.
- [x] P58.3 Decision memo and no-live-run gate (#387)
  - [x] Add `planning/p58_active_phase_reconciliation.md`.
  - [x] Add `planning/p58_p64_roadmap_tranche.md`.
  - [x] Update cost-discipline guidance after the P57 overrun.
  - [x] Update `AGENTS.md` with the paid-supervisor cost-control lesson.
- [x] P58.4 Planning, tests, and PR closeout (#388)
  - [x] Rebase P58 onto merged P57 `main`.
  - [x] Resolve conflicts without rewriting landed P55-P57 history.
  - [x] Run focused validation.
  - [x] Open a P58-only PR.

## Phase 59: Paid-Supervisor Budget Gates And Stop Rules

Parent issue: #390

Branch: `feature/p59-supervisor-budget-gates`

Status: complete

Goal: make paid-supervisor budget declarations, checkpoint spans, stop
conditions, and maintainer checkpoints enforceable in tooling.

Planned tasks:

- [x] P59.1 Budget declaration schema and template (#391)
  - [x] Define required budget declaration fields.
  - [x] Include experiment question, max paid cost, max attempts, checkpoint
        spans, stop condition, and maintainer checkpoint.
  - [x] Add summary status fields for declared/exceeded/attempt/stop/checkpoint
        state.
  - [x] Add a public-safe template.
- [x] P59.2 Supervisor budget CLI validation (#392)
  - [x] Add `agent-workbench supervisor budget validate`.
  - [x] Fail closed for missing or malformed fields.
  - [x] Render concise validation diagnostics.
  - [x] Preserve existing supervisor token commands.
- [x] P59.3 Stop-rule and summary status fields (#393)
  - [x] Define `budget_declared`, `budget_exceeded`, `attempt_count`,
        `stop_rule_triggered`, and `maintainer_checkpoint_required`.
  - [x] Validate attempt counts and max-attempt limits.
  - [x] Validate stop condition and maintainer checkpoint settings.
  - [x] Document that aborted/stale runs are diagnostic evidence, not progress.
- [x] P59.4 Planning, tests, and PR closeout (#394)
  - [x] Link P59 roadmap and planning notes to GitHub issues.
  - [x] Update `CHANGE_LOG.md`.
  - [x] Run focused validation.
  - [x] Open a P59-only PR against `main`.

Closeout boundary: P59 adds the budget declaration validator and status
semantics needed before future live economics runs. The existing packaged
document-audit graph run and summary paths are wired to require valid budget
records for live/economics use, but P59 launches no live runs while testing
that enforcement.

## Phase 60: Outcome Semantics And Scoring Split

Parent issue: #396

Branch: `feature/p60-outcome-semantics-scoring-split`

Status: complete

Goal: separate artifact quality, protocol compliance, and economics usability
across benchmark summaries.

Planned tasks:

- [x] P60.1 Outcome field schema (#397)
  - [x] Define `quality_validated_candidate`.
  - [x] Define `protocol_accepted_candidate`.
  - [x] Define `economics_usable`.
  - [x] Define `final_decision`.
  - [x] Define `rejection_reasons`.
- [x] P60.2 Hard constraint semantics (#399)
  - [x] Preserve hard failure for invalid schema shape.
  - [x] Preserve hard failure for wrong source identity or invalid source IDs.
  - [x] Preserve hard failure for authority-boundary violations.
  - [x] Keep model-provenance mismatch as a protocol defect.
- [x] P60.3 Soft scoring semantics (#398)
  - [x] Keep quote length as a soft weighted penalty by default.
  - [x] Support configurable penalty weights for task-specific preferences.
  - [x] Keep downstream-consumer hard excerpt limits opt-in.
  - [x] Document how soft scores affect scale/repair/escalate decisions.
- [x] P60.4 Decision packet migration (#400)
  - [x] Update comparison scripts to emit split outcome fields.
  - [x] Update decision packets so quality-valid/protocol-noisy results are not
        collapsed into vague rejected states.
  - [x] Add tests for accepted, quality-valid, protocol-rejected, economics
        diagnostic, and stale cases.
  - [x] Backfill at least one P57-style summary fixture.

## Phase 61: Packaged Local-Supervisor Workflow V1

Parent issue: #402

Branch: `feature/p61-packaged-local-supervisor-workflow-v1`

Status: complete

Goal: promote the successful P57 pre-materialized graph-ticket pattern into a
reusable packaged workflow.

Planned tasks:

- [x] P61.1 Packaged workflow contract (#404)
  - [x] Define coordinator-owned setup and pre-materialization nodes.
  - [x] Define local-supervisor audit, repair, validation, and compact-report
        nodes.
  - [x] Define deterministic validator authority boundaries.
  - [x] Define paid-coordinator review and escalation nodes.
- [x] P61.2 Launcher hardening (#405)
  - [x] Make pre-materialized graph tickets the default launcher mode.
  - [x] Keep setup/materializer commands out of local-supervisor action lists by
        default.
  - [x] Require high-entropy run IDs for live bridge jobs.
  - [x] Keep quiet runtime output as the default for large packaged runs.
- [x] P61.3 Evidence replay (#406)
  - [x] Replay P57 v13/v11-style summaries without launching live Copilot jobs.
  - [x] Confirm accepted, rejected, aborted, and diagnostic evidence renders
        consistently.
  - [x] Confirm budget records from P59 can be attached to replayed summaries.
  - [x] Add focused tests for replay and launcher-plan rendering.
- [x] P61.4 Documentation and closeout (#403)
  - [x] Update workflow docs and planning note.
  - [x] State when subagent use is required versus advisory.
  - [x] Public-safety scan generated docs/templates.
  - [x] Open a P61-only PR after validation.

## Phase 62: Document-Indexing Workflow Recipe V1

Parent issue: #408

Branch: `feature/p62-document-indexing-recipe-v1`

Status: complete

Goal: convert TSA23/MP11 lessons into a reusable public technical PDF
document-indexing recipe.

Planned tasks:

- [x] P62.1 Recipe stage model (#411)
  - [x] Define corpus resolution and materialization stage.
  - [x] Define deterministic page/chunk manifest generation stage.
  - [x] Define section-map extraction stage.
  - [x] Define typed TSR fact extraction stage.
  - [x] Define repair, normalization, verification, and paid sample-audit
        stages.
- [x] P62.2 Task sizing and split strategy (#412)
  - [x] Define default page/chunk sizes for public technical PDFs.
  - [x] Define split strategy for long documents and mini-corpora.
  - [x] Explicitly forbid hidden record caps.
  - [x] Define stop/escalation behavior for scanned/OCR-poor inputs.
- [x] P62.3 Model role defaults (#409)
  - [x] Assign Qwen3.6-style general document models to extraction roles.
  - [x] Assign coding-oriented models to JSON repair roles.
  - [x] Assign verifier/critic roles only where P55-P57 evidence supports them.
  - [x] Keep model defaults configurable per deployment.
- [x] P62.4 Public-safe recipe artifacts (#410)
  - [x] Track recipe docs and templates only.
  - [x] Keep raw PDF text, prompts, worker outputs, and provider details
        ignored.
  - [x] Include P59 budget hooks and P60 outcome fields.
  - [x] Add public-safety scan and docs validation.

## Phase 63: Bounded TSA23 Recipe Pilot

Parent issue: #414

Branch: `feature/p63-bounded-tsa23-recipe-pilot`

Status: complete

Goal: run one controlled, budgeted pilot using the P62 recipe on a bounded
TSA23 slice.

Planned tasks:

- [x] P63.1 Pilot selection and budget (#415)
  - [x] Choose one most-recent TSA23 information-package or rationale slice.
  - [x] Declare a P59 budget record before any live execution.
  - [x] Define maximum attempts and maintainer checkpoint.
  - [x] Confirm raw materialized inputs stay ignored.
- [x] P63.2 Recipe execution (#418)
  - [x] Generate ignored runtime tickets and SDK eval manifests from the
        tracked P63 pilot plan.
  - [x] Verify generated manifests with a dry run before contacting the
        provider.
  - [x] Confirm the selected local model is available through the configured
        Ollama/OpenAI-compatible provider path.
  - [x] Run exactly one live local-worker extraction attempt within the
        declared P59 budget and attempt limit.
  - [x] Capture raw worker output, prompts, provider details, and token traces
        only under ignored runtime paths.
  - [x] Run deterministic validation for JSONL parseability, document ID,
        chunk ID, model provenance, schema shape, and public-safety boundaries.
  - [x] Run repair/normalization only if the budget gate and stop rules allow
        it; otherwise record the repair need as an unresolved outcome.
  - [x] Stop immediately when budget, attempt, model-availability,
        malformed-output, wrong-root, or public-safety stop rules trigger.
  - Result: the single live attempt produced 40 parseable candidate records but
    stopped as diagnostic evidence because the SDK observed a provider 524
    model-call failure, malformed/truncated JSONL, and one invalid chunk ID.
    No retry or repair expansion is allowed before maintainer checkpoint.
- [x] P63.3 Outcome and economics reporting (#416)
  - [x] Produce tracked sanitized summaries only; do not promote raw source
        text, raw quotes, raw prompts, transcripts, provider URLs, headers, or
        credentials.
  - [x] Use P60 outcome semantics for every candidate artifact:
        `quality_validated_candidate`, `protocol_accepted_candidate`,
        `economics_usable`, `final_decision`, and `rejection_reasons`.
  - [x] Track accepted, repaired, rejected, escalated, and unresolved fact
        counts by stage and by source chunk.
  - [x] Track hard-constraint failures separately from soft scoring penalties
        such as quote length.
  - [x] Produce line-item paid supervisor, local worker, audit, repair,
        validation, and reporting cost tables.
  - [x] Compare delegated cost against the direct-supervisor sample audit
        baseline for the same bounded slice.
        Result: comparison is `not_comparable` because the stop rule triggered
        before a quality-valid delegated candidate existed, so running a new
        paid direct-supervisor baseline would answer a different question.
  - [x] Mark aborted, stale, malformed, or budget-blocked runs as diagnostic
        evidence rather than successful economics evidence.
  - [x] Update the P63 planning note with what the pilot actually taught before
        proposing any scale-up.
  - Result: tracked sanitized reporting records 0 accepted, 0 repaired, 1
    rejected, 0 escalated, and 39 unresolved candidate records. P63 remains at
    maintainer checkpoint before P63.4 scale decision.
- [x] P63.4 Scale decision (#417)
  - [x] Draft the scale/adjust/repeat/pause decision memo from measured P63.2
        and P63.3 evidence.
  - [x] Recommend whether the next move is scale document indexing, adjust the
        recipe, repeat the bounded slice, change model roles, or pause the
        lane.
  - [x] Record maintainer-facing value: what usable document-indexing work was
        produced, what paid-supervisor cost was avoided or added, and what
        quality risk remains.
  - [x] Record the exact gate for any follow-on live run, including budget,
        attempt limit, model lane, document slice, and stop rule.
  - [x] Receive maintainer acceptance of the scale, adjust, repeat, pause, or
        abandon decision.
  - [x] Update roadmap, changelog, planning note, parent issue, and child issue
        to reflect the accepted decision.
  - [x] Confirm P63-only PR and merge remain parent-phase closeout steps rather
        than unresolved scale-decision subtasks.
  - Draft recommendation: pause live scaling and adjust the recipe/provider
    execution shape before any repeat. Do not rerun, repair-expand, broaden the
    slice, add a model family, or run a direct-supervisor baseline without a new
    maintainer-approved gate.
  - Maintainer decision options:
    - [ ] Pause and merge diagnostic evidence.
    - [x] Adjust recipe in a follow-on phase.
    - [ ] Approve bounded repeat under a new gate.
    - [ ] Approve a different model/provider lane.
    - [ ] Abandon or park the TSA23 indexing lane.
  - Accepted decision: close P63 as diagnostic evidence and move any repeat
    into a follow-on recipe-adjustment phase focused on smaller section-level
    tickets, deterministic JSONL repair, chunk-ID hardening, and provider 524
    isolation. P63 authorizes no further live model calls, direct-supervisor
    baseline, broader slice, or model-lane change.

Phase closeout:

- [x] Open a P63-only PR after P63.2-P63.4 evidence agrees (#419).
- [x] Merge the P63 PR (#419).
- [x] Verify parent issue #414 closure after merge.
- [x] Sync local `main` and delete `feature/p63-bounded-tsa23-recipe-pilot`.

## Phase 64: Deployment Environment And Operator Playbook

Parent issue: #420

Branch: `feature/p64-deployment-environment-operator-playbook`

Status: complete

Goal: make Agent Workbench usable in the intended remote GPU/code-server or
VS Code environment without relying on chat memory.

Planned tasks:

- [x] P64.1 Environment shape (#421)
  - [x] Create the P64 parent issue and child issue before branch work begins.
  - [x] Link P64 issue numbers in this roadmap section after issue creation.
  - [x] Document supported VS Code and code-server configurations.
  - [x] Document Copilot Chat permission-mode expectations.
  - [x] Document Ollama provider and model inventory requirements.
  - [x] Document ignored runtime paths for tickets, transcripts, reports, and
        provider details.
  - [x] Document what must remain environment-specific and ignored.
- [x] P64.2 Operator checklist (#422)
  - [x] Add model inventory checklist.
  - [x] Add permission-mode and workspace-root checklist.
  - [x] Add bridge launch and budget declaration checklist.
  - [x] Add evidence collection and public-safety checklist.
  - [x] Add pre-run and post-run checks for stale sessions, run IDs, and
        budget records.
  - [x] Add explicit "do not run" gates for missing budget, wrong model, wrong
        root, stale chat evidence, or repeated failed attempts.
- [x] P64.3 Troubleshooting (#423)
  - [x] Document stale chat session symptoms and reset procedure.
  - [x] Document wrong workspace root and model mismatch checks.
  - [x] Document runaway loop cancellation procedure.
  - [x] Document when not to run because budget or evidence gates are missing.
  - [x] Document how to distinguish provider/model failures from Copilot Chat
        session-loop failures.
  - [x] Document when to restart Ollama versus when to reset VS Code/Copilot
        state.
- [x] P64.4 Public-safe closeout (#424)
  - [x] Add a P64 planning note that records the supported deployment posture
        and excluded private details.
  - [x] Keep private endpoint, server, credential, and personal-path details out
        of tracked docs.
  - [x] Validate docs and examples.
  - [x] Public-safety scan tracked playbook.
  - [x] Update roadmap, changelog, parent issue, child issues, and PR body from
        the same subtask checklist.
  - [x] Open a P64-only PR after review (#425).

Phase closeout:

- [x] Open a P64-only PR after P64.1-P64.4 evidence agrees (#425).
- [x] Merge the P64 PR (#425).
- [x] Verify parent issue #420 closure after merge.
- [x] Sync local `main` and delete
      `feature/p64-deployment-environment-operator-playbook`.

## Phase 65: Copilot Session Archive

Parent issue: #426

Branch: `feature/p65-copilot-session-archive`

Status: complete

Goal: make ticket-plus-Copilot-chatlog archival a systematic Agent Workbench
function so delegated-run behavior evidence is captured by default.

Planned tasks:

- [x] P65.1 Archive command surface (#427)
  - [x] Add `agent-workbench copilot archive`.
  - [x] Resolve VS Code workspace storage from `workspace.json`.
  - [x] Match sessions by session id, run id, prompt marker, or latest session.
  - [x] Copy raw `chatSessions/*.jsonl` and Copilot transcript JSONL into
        ignored runtime storage.
  - [x] Fail closed when no matching session exists.
- [x] P65.2 Sanitized manifest (#428)
  - [x] Record event counts, model ids, permission levels, message counts, and
        tool-request counts.
  - [x] Record bounded snippets for user messages, assistant messages, tool
        requests, stall nudges, and `keep going` nudges.
  - [x] Keep source paths and raw transcript content out of the manifest.
  - [x] Mark raw files as runtime-only and not safe for tracked commit without
        sanitization.
- [x] P65.3 Tests and docs (#429)
  - [x] Add fake VS Code workspace-storage fixtures for archive tests.
  - [x] Test successful archive and no-match fail-closed behavior.
  - [x] Add a P65 planning note explaining the evidence unit and boundaries.
  - [x] Update `AGENTS.md` so future Copilot delegation tests archive chat
        behavior by default.

Closeout boundary:

- [x] Run focused tests for the archive helper and CLI.
- [x] Run `git diff --check`.
- [x] Update `CHANGE_LOG.md`.

## Phase 66: Task-Level Delegation Protocol

Parent issue: #431

Branch: `feature/p66-task-level-delegation-protocol`

Status: complete

Goal: make one roadmap child task the default delegation unit, with coordinator
ownership of phase sequencing and acceptance.

Planned tasks:

- [x] P66.1 Protocol contract (#432)
  - [x] Define coordinator-owned responsibilities for phase setup, task
        sequencing, acceptance, PR merge, parent issue closure, and final
        completion claims.
  - [x] Define delegated local-supervisor responsibilities for one child task
        at a time.
  - [x] Define when whole-phase delegation is allowed as an experiment.
  - [x] Define handoff boundaries between child-task runs.
- [x] P66.2 Child-task ticket template (#433)
  - [x] Add a template with current state, governing child issue, allowed files,
        allowed commands, stop conditions, and evidence requirements.
  - [x] Require explicit result, blocker, heartbeat, and archive paths.
  - [x] Require Windows/Linux shell context to be stated explicitly.
  - [x] Include a no-summary substitute rule: prose cannot replace command
        execution or artifact evidence.
- [x] P66.3 Task result and decision packets (#434)
  - [x] Add a result schema for commands run, files changed, tests/checks,
        GitHub URLs touched, artifacts produced, and blockers.
  - [x] Add coordinator decision packet states: accept, reject, repair,
        escalate, or abandon.
  - [x] Add repair-ticket input fields that cite exact defects in the previous
        task output.
- [x] P66.4 P108 retrospective (#435)
  - [x] Summarize the P108 whole-phase delegation success signals.
  - [x] Summarize P108 control-loop failures and housekeeping defects.
  - [x] Record why future default delegation should be task-level.

Closeout boundary:

- [x] Validate JSON templates.
- [x] Run `git diff --check`.
- [x] Update `CHANGE_LOG.md`.

## Phase 67: Heartbeat And Nudge Protocol

Parent issue: #437

Branch: `feature/p67-heartbeat-nudge-protocol`

Status: complete

Goal: make delegated-run stalls observable and make mid-run nudges structured,
cheap, and auditable.

Planned tasks:

- [x] P67.1 Heartbeat file contract (#438)
  - [x] Define `runtime/agent_jobs/<run_id>.heartbeat.jsonl`.
  - [x] Define required heartbeat fields: timestamp, checklist item, action,
        artifact path, command summary, and next intended action.
  - [x] Define result and blocker companion files.
  - [x] Define public-safety rules for heartbeat content.
- [x] P67.2 Stale-run detection (#439)
  - [x] Define stale heartbeat thresholds by run type.
  - [x] Distinguish thinking, command execution, tool blockage, and no-progress
        states where possible.
  - [x] Define when the coordinator should inspect filesystem/Git state before
        nudging.
- [x] P67.3 Nudge templates (#440)
  - [x] Add canned nudges for continue-next-subtask, stop-summarizing,
        write-blocker, fix-shell-context, and reconcile-checklist states.
  - [x] Require every nudge to be archived with timestamp and triggering
        evidence.
  - [x] Define a stop rule after repeated failed nudges.
- [x] P67.4 Nudge evidence summary (#442)
  - [x] Define nudge count and stall count as behavior metrics.
  - [x] Define accepted versus protocol-noisy behavior after nudges.
  - [x] Add examples derived from P108 without tracking raw transcripts.

Closeout boundary:

- [x] Run focused heartbeat tests.
- [x] Run `git diff --check`.
- [x] Update `CHANGE_LOG.md`.

## Phase 68: Copilot Task Controller V0

Parent issue: #448

Branch: `feature/p68-copilot-task-controller-v0`

Status: complete

Goal: package the launch, archive, heartbeat check, nudge, and review loop for
one child-task delegation run.

Planned tasks:

- [x] P68.1 Controller run manifest (#449)
  - [x] Define a manifest tying together run id, ticket path, child issue,
        expected model, permission mode, heartbeat path, result path, blocker
        path, archive path, and token ledger path.
  - [x] Require high-entropy run ids for live Copilot sessions.
  - [x] Validate wrong-root, wrong-model, missing-budget, and stale-session
        stop gates before launch.
- [x] P68.2 Launch wrapper (#450)
  - [x] Add a command to generate a child-task prompt through the Copilot
        controller without maximizing the UI.
  - [x] Preserve model and permission evidence expectations.
  - [x] Fail closed when the prompt cannot be delivered as an executable
        directive.
- [x] P68.3 Archive integration (#451)
  - [x] Require P65 archive after a task run by session id, run id, or prompt
        marker.
  - [x] Link archive manifest to the run manifest and result file.
  - [x] Refuse economics or behavior claims without archive evidence when the
        run used Copilot Chat.
- [x] P68.4 Review packet (#452)
  - [x] Generate a coordinator-facing review packet summarizing task output,
        heartbeat state, archive metrics, validation checks, and recommended
        decision.
  - [x] Keep raw logs ignored and promote only sanitized summaries.

Closeout boundary:

- [x] Run focused controller tests.
- [x] Run `git diff --check`.
- [x] Update `CHANGE_LOG.md`.

## Phase 69: Behavior Analytics From Archives

Parent issue: #454

Branch: `feature/p69-behavior-analytics-from-archives`

Status: complete

Goal: mine archived Copilot sessions for reusable delegation behavior metrics.

Planned tasks:

- [x] P69.1 Metrics schema (#455)
  - [x] Define stall count, nudge count, tool-call count, command-failure count,
        shell-mismatch count, repeated-summary count, and premature-completion
        claim count.
  - [x] Define user-intervention burden and coordinator-review burden fields.
  - [x] Define behavior outcome classes: smooth, nudged-success,
        noisy-success, repair-needed, blocked, or runaway.
- [x] P69.2 Archive analyzer (#456)
  - [x] Add a command to analyze P65 archive manifests.
  - [x] Detect common P108-style patterns from sanitized snippets and event
        structure.
  - [x] Emit a public-safe behavior summary JSON/Markdown pair.
- [x] P69.3 Cross-run synthesis (#457)
  - [x] Aggregate behavior summaries across delegation tests.
  - [x] Group by model, permission mode, ticket type, task size, and authority
        level.
  - [x] Report trends without exposing raw transcript text.
- [x] P69.4 Policy feedback (#458)
  - [x] Feed behavior metrics into task-suitability and delegation-policy
        recommendations.
  - [x] Identify ticket patterns that reduce stalls or repair burden.
  - [x] Define minimum archive count before tuning defaults.

Closeout boundary:

- [x] Run focused behavior analytics tests.
- [x] Run `git diff --check`.
- [x] Update `CHANGE_LOG.md`.

## Phase 70: FEMIC P108 Repair Dogfood

Parent issue: #461

Branch: `feature/p70-femic-p108-repair-dogfood`

Status: complete

Goal: test the task-level delegation controller on real P108 cleanup tasks in
FEMIC, while keeping coordinator authority over final PR merge and parent issue
closure.

Resume note: P71 delivered and merged the SDK-owned Copilot remote-control
bridge. P70 now resumes with SDK session manifests, `copilot-sdk start`,
`monitor`, `nudge-plan`, and `nudge` as the primary delegation path. VS Code
Chat archives remain evidence-only fallback material.

Planned tasks:

- [x] P70.1 Dogfood setup (#462)
  - [x] Select the P108 cleanup branch/PR state as the target.
  - [x] Declare a budget and stop rule before any paid-coordinator monitoring.
  - [x] Generate one child-task ticket at a time through the P66 protocol.
  - [x] Require P65 archive capture for every Copilot-backed task.
- [x] P70.2 Cleanup ticket set (#463)
  - [x] Ticket A: repair `CHANGE_LOG.md` ordering and encoding damage
        (completed during P71 SDK dogfood and verified as FEMIC commit
        `181cb16` on PR #303).
  - [x] Ticket B: reconcile parent roadmap versus instance roadmap completion
        state (completed with SDK session
        `cdba1e8b-5173-4676-bacc-081e18d9eec8`, instance commit `282da67`,
        and parent FEMIC commit `b60dbd5` on PR #303).
  - [x] Ticket C: repair stale P108 supervisor result-report claims
        (completed with selected profile `agent-workbench-local-supervisor`,
        SDK session `6ebd387b-b23a-4ff1-8e22-5abc46a2cba0`, and
        coordinator-verified repair of the ignored FEMIC P108 supervisor result
        report).
  - [x] Ticket D: verify PR #303 and child issue checklist consistency
        (completed with selected profile `agent-workbench-local-supervisor`,
        SDK session `b44c04bb-2414-4175-9208-e773747f48f7`, and coordinator
        verification that PR #303 is open/non-draft/mergeable, child issues
        #297-#301 are closed, and parent issue #302 remains open; counted as
        `needs-supervisor-review` for controller scoring because the SDK emitted
        a `model.call_failure` XML syntax error).
  - [x] Ticket E: produce final coordinator review packet (completed as
        `runtime/p70_ticket_e_final_review_packet/review_packet.md`, with
        coordinator verification that PR #303 remains open/non-draft/mergeable,
        child issues #297-#301 are closed, parent issue #302 remains open, and
        P70.3 should score Ticket D's SDK `model.call_failure` separately from
        result validity).
- [x] P70.3 Controller evaluation (#464)
  - [x] Add full and compact human-readable SDK transcript renderers so
        coordinator-supervisor and supervisor-worker conversation evidence can
        be audited before behavior scoring.
  - [x] Measure stall count, nudge count, tool-call count, result validity, and
        coordinator repair burden per ticket.
  - [x] Compare task-level behavior to the whole-phase P108 run.
  - [x] Record whether child-task tickets reduce drift and stale-report defects.

P70.3 evaluation result: the task-level SDK controller is a net improvement
over the whole-phase P108 run for bounded cleanup/review work. Ticket-level
runs reduced manual stall nudges and made stale-report defects independently
reviewable, but Ticket D proved controller scoring must separate result
validity from session health because a correct result can coexist with an SDK
`model.call_failure`. The full evaluation is recorded under ignored runtime
storage at `runtime/p70_controller_evaluation/controller_evaluation.md`.
- [x] P70.4 Scale decision (#465)
  - [x] Decide whether to use task-level Copilot supervision for the next real
        FEMIC or CLEWS development phase.
  - [x] Record remaining risks and required controller improvements.
  - [x] Keep final P108 merge/parent closure under coordinator/maintainer
        authority.

P70.4 scale decision: use task-level SDK Copilot supervision by default for
bounded cleanup/review lanes with explicit result or blocker artifacts,
coordinator verification, ignored raw runtime evidence, and compact transcript
review. Do not yet use it as the default for broad multi-day implementation
phases. The next implementation tranche should activate P73 before P74 so the
standard profile catalog and tool-aware evidence schema stabilize before
FoundryTK optimization work begins. FEMIC PR #303 merge and parent issue #302
closure remain outside P70 and require coordinator/maintainer authority.

## Phase 71: Copilot SDK Remote-Control Bridge

Parent issue: #466

Branch: `feature/p71-copilot-sdk-remote-control-bridge`

Status: complete

Goal: replace brittle VS Code Chat session driving with an SDK-owned bridge that
can create resumable Copilot sessions, monitor event streams in near real time,
detect stalls, and send explicit nudges or ad hoc directives to the same
session.

Scope:

- SDK-owned session manifests, event logs, status summaries, and nudge records.
- Runtime commands for session creation, resume/reconnect, prompt send, monitor,
  nudge, and review.
- FEMIC P108 dogfood runs as the first live evidence source.
- Public-safe tracked contracts, with raw transcripts and SDK event payloads
  stored only under ignored local runtime paths.

Out of scope:

- Closing FEMIC P108, merging FEMIC PR #303, or claiming P108 repair success.
- Reopening P70 until P71 produces enough bridge evidence for a scale decision.
- Treating arbitrary VS Code Chat transcript artifacts as controllable SDK
  sessions.
- Publishing private prompts, raw transcripts, credentials, endpoints, or
  machine-specific paths.

Planned tasks:

- [x] P71.1 SDK remote-control contract (#467)
  - [x] Add the phase planning note, SDK session manifest template, event/status
        vocabulary, and P70/P108 resume gates.
  - [x] Define the difference between SDK-owned sessions and archived VS Code
        Chat sessions.
  - [x] Define the evidence required before a run can count as monitored,
        nudged, blocked, or accepted for dogfood.
- [x] P71.2 SDK session runtime commands (#468)
  - [x] Add a reusable SDK bridge module with create, resume, send, and event
        capture primitives.
  - [x] Add CLI commands that operate from the manifest and fail closed when the
        session state is missing or ambiguous.
  - [x] Cover the runtime path with fake-SDK tests before live dogfood.
- [x] P71.3 Monitoring, stall detection, and nudge commands (#469)
  - [x] Summarize SDK events into coordinator-readable status records.
  - [x] Detect quiet stalls, repeated non-progress, blockers, and completion
        candidates.
  - [x] Send a same-session nudge/directive and record the exact nudge evidence.
- [x] P71.4 FEMIC P108 dogfood runs (#470)
  - [x] Use FEMIC P108 as the target task lane for controlled SDK-owned runs.
  - [x] Capture create/resume, monitor, and nudge evidence from live sessions.
  - [x] Verify any worker claim against the FEMIC worktree before accepting it.
- [x] P71.5 Evidence synthesis and P70 resume decision (#471)
  - [x] Summarize the bridge evidence and remaining SDK limitations.
  - [x] Record whether P70 can resume with SDK-owned remote control.
  - [x] Synchronize roadmap, changelog, issue comments, and PR closeout.

Closeout boundary:

- [x] Run focused SDK bridge tests.
- [x] Run `git diff --check`.
- [x] Dogfood at least one FEMIC P108 session or record the exact live blocker.
- [x] Update `CHANGE_LOG.md` and GitHub issues.

## Phase 72: Copilot SDK Custom Agent Profiles

Parent issue: #473

Branch: `feature/p72-sdk-custom-agent-profiles`

Status: complete

Goal: upgrade the SDK-owned Copilot bridge so sessions can be launched and
resumed with explicit custom agent profiles, selected agent names, default
agent controls, subagent streaming, and conservative Agent Workbench custom
tools.

Scope:

- Manifest-driven `sdk.agent_profiles` configuration.
- `.agent.md` profile parsing shared with VS Code custom-agent experiments.
- SDK create/resume kwargs for `custom_agents`, `agent`, `default_agent`,
  `custom_agents_local_only`, `include_sub_agent_streaming_events`, and
  custom tools.
- Profile validation/rendering CLI commands.
- Custom-agent and subagent event evidence in monitor and transcript views.

Out of scope:

- Standardizing every profile/model-role combination; that is P73.
- Pulling FoundryTK into the runtime bridge; that is P74 exploration.
- Claiming FEMIC P108 repair quality without P70 coordinator verification.

Planned tasks:

- [x] P72.1 Profile planning and manifest contract (#475)
  - [x] Add the P72 planning note and issue mapping.
  - [x] Extend the SDK manifest template with `sdk.agent_profiles`.
  - [x] Define public-safe profile, overlay, and custom-tool boundaries.
- [x] P72.2 Profile parser and resolver (#474)
  - [x] Parse `.agent.md` frontmatter and Markdown body with PyYAML.
  - [x] Map SDK-supported fields and preserve unsupported VS Code-only fields
        in validation output.
  - [x] Validate selected agents, required names, non-empty prompts, task
        overlays, and profile tool coverage.
- [x] P72.3 SDK bridge launch integration (#476)
  - [x] Pass resolved custom-agent kwargs through live session creation.
  - [x] Pass resolved custom-agent kwargs through live session resume.
  - [x] Register conservative Agent Workbench custom SDK tools from the
        manifest.
- [x] P72.4 Profile CLI and transcript evidence (#478)
  - [x] Add `agent-workbench copilot-sdk profile-validate`.
  - [x] Add `agent-workbench copilot-sdk profile-render`.
  - [x] Count and render `session.custom_agents_updated`, `subagent.*`, and
        assistant messages with agent metadata.
- [x] P72.5 Custom tool registry and verification (#477)
  - [x] Add read-only/validation tools for run context, result contract, and
        result validation.
  - [x] Cover parser, bridge kwargs, transcript, and tool behavior with focused
        tests.
  - [x] Run one P70 Ticket C or later FEMIC dogfood task with
        `agent-workbench-local-supervisor` selected.
  - [x] Compare behavior against P70 Ticket B baseline.

P72.5 live evidence: Ticket C ran as SDK session
`6ebd387b-b23a-4ff1-8e22-5abc46a2cba0` against the ignored FEMIC P108
supervisor result report. Compared with Ticket B, Ticket C produced visible
subagent events, invoked the custom `agent_workbench_validate_result` tool, and
recorded a manifest-derived custom-agent evidence event for
`agent-workbench-local-supervisor`. Coordinator verification confirmed the
target report no longer contains the placeholder PR URL, reports child issues
#297-#301 closed, reports parent issue #302 open, and reports PR #303 open and
mergeable.

Closeout boundary:

- [x] Run focused P72 tests.
- [x] Run full `pytest`.
- [x] Run `ruff format`, `ruff check`, and `git diff --check`.
- [x] Smoke-test `profile-validate` and `profile-render` on an ignored runtime
      manifest.
- [x] Dogfood a selected custom-agent profile on P70 Ticket C and compare it to
      the P70 Ticket B baseline.
- [x] Update `CHANGE_LOG.md`.
- [x] Update GitHub issues.
- [x] Merge PR #479 into the active P70 branch.

## Phase 73: Standard Agent Workbench Profile Catalog

Parent issue: #480

Branch: `feature/p73-standard-agent-profile-catalog`

Status: complete

Goal: turn the P72 bridge into a curated profile catalog with standard
model-role wrappers and task overlays that can be selected reliably by
manifest.

Planned scope:

- Keep `.github/agents/*.agent.md` as the canonical editable profile format.
- Standardize supervisor, auditor, strict-worker, and strict-worker-variant
  profiles.
- Add role/task overlays for repair-list execution, new Python module
  implementation, debugging, systematic refactors, documentation expansion,
  notebook/example authoring, and release-readiness review.
- Treat tools as a first-class profile dimension with explicit validation.

Planned tasks:

- [x] P73.1 Catalog activation and overlay registry
  - [x] Open parent issue #480 and activate the P73 branch.
  - [x] Add checked-in standard task overlays that can be referenced by manifest.
  - [x] Resolve named and path-based overlays without modifying source profiles.
  - [x] Validate standard profile and overlay references from the CLI.

P73.1 result: added the standard overlay registry under
`.github/agents/overlays/`, including repair-list execution, new Python module
implementation, existing-code debugging, systematic refactor/sweep,
documentation expansion, notebook/example authoring, and release-readiness
review. SDK manifests can now resolve `sdk.agent_profiles.task_overlay.name`,
`names`, `path`, `paths`, and `text` into the selected profile prompt without
editing the source `.agent.md` files. `profile-validate`, `profile-render`, and
the synthetic `session.custom_agents_updated` event now expose selected overlay
metadata for coordinator review.
- [x] P73.2 Profile/tool catalog validation
  - [x] Report standard profile coverage and explicit tool declarations.
  - [x] Validate profile-declared tools against built-in tools and registered
        Agent Workbench custom tools.
  - [x] Add public-safe catalog preview output for coordinator review.

P73.2 result: added a standard profile catalog validator and public-safe
Markdown preview for the four canonical `.github/agents/*.agent.md` profiles
and seven task overlays. The `copilot-sdk catalog-validate` command reports
profile count, overlay count, warnings, errors, declared models, explicit tool
sets, unsupported VS Code-only frontmatter fields, and prompt character counts
without exposing full prompt text. Profile-declared tools are validated against
known SDK built-ins and the Agent Workbench custom tool registry.
- [x] P73.3 Profile-run evidence summary
  - [x] Summarize selected profile, overlay, custom tools, transcript shape,
        result status, and controller health from SDK manifests/events.
  - [x] Reuse P70/P72 evidence as the first comparison baseline.

P73.3 result: added `copilot-sdk profile-run-summary`, which reads an SDK
manifest, event log, status summary, and result/blocker paths to produce a
public-safe profile-run evidence packet. The packet reports selected profile,
task overlays, custom tools, transcript-shape counts, latest controller status,
controller health, and result/blocker final status when the artifact follows
the current `Final status:` contract. P70 Ticket C and Ticket D were rendered
as ignored baseline evidence; Ticket D correctly classifies controller health
as `error`, preserving the P70 result-validity versus controller-health split.
Older P70 result artifacts without an exact `Final status:` line leave
`result_status` blank instead of inventing a status.
- [x] P73.4 Dogfood and scale recommendation
  - [x] Run or replay one bounded task with a selected standard profile and
        task overlay.
  - [x] Record whether the catalog improves profile selection reliability and
        coordinator review burden.
  - [x] Keep FoundryTK runtime integration deferred to P74.

P73.4 result: replayed a bounded SDK run artifact with selected profile
`agent-workbench-local-supervisor`, task overlay `release-readiness-review`,
and the conservative Agent Workbench custom tools. The profile-run summary
reported `controller_health=healthy`, `result_status=accepted-candidate`, one
custom-agent event, and one subagent event. The scale recommendation is stored
under ignored runtime evidence at
`runtime/p73_overlay_replay/p73_4_scale_recommendation.md`. Recommendation:
use the standard profile catalog for future bounded SDK delegation runs because
profile source paths, selected profile, task overlay, custom tools, and
profile/tool coverage are validated before the run and summarized afterward.
Coordinator authority remains required for result acceptance, issue closure,
PR merge, and release actions. FoundryTK remains deferred to P74.

## Phase 74: FoundryTK Profile Optimization Exploration

Parent issue: #481

Branch: `feature/p74-foundrytk-profile-optimization`

Status: complete
Status note: complete repo-side; GitHub parent issue #481 was created after
`gh` access returned.

Goal: evaluate whether FoundryTK and related evaluation tooling can improve
Agent Workbench model/profile selection, prompt optimization, trace review, and
delegated workflow efficiency.

Planned scope:

- Keep FoundryTK out of the P72/P73 runtime bridge.
- Investigate FoundryTK as external evaluation guidance, optional tool/MCP
  provider, model-selection evidence source, and trace/evaluation runner.
- Define reliability, work quality, efficiency, and conversation-shape metrics
  before any model customization work.

Planned tasks:

- [x] P74.1 Local evaluation scaffold
  - [x] Add a FoundryTK-style profile optimization plan renderer that consumes
        P73 profile-run evidence without adding a FoundryTK runtime dependency.
  - [x] Define reliability, work quality, efficiency, and conversation-shape
        dimensions in the rendered plan.
  - [x] Render an ignored P74 plan from P73 overlay replay evidence and P70
        Ticket D controller-health evidence.

P74.1 result: added `agent-workbench foundrytk profile-optimization-plan`,
which summarizes one or more SDK manifests through the P73 profile-run evidence
schema and renders a public-safe FoundryTK-facing optimization plan. The first
plan artifact is stored at
`runtime/p74_foundrytk_profile_optimization/profile_optimization_plan.md`; it
correctly recommends stabilizing controller/session health before prompt or
model optimization because the comparison includes P70 Ticket D's
`controller_health=error` evidence.
- [x] P74.2 Evaluation dataset contract
  - [x] Define the public-safe row schema for profile/overlay/model comparison
        runs.
  - [x] Map local evidence fields to potential Foundry evaluation inputs
        without requiring Azure resources.
  - [x] Keep raw transcript text and private paths out of evaluation datasets.

P74.2 result: added `agent-workbench foundrytk profile-evaluation-dataset`,
which writes public-safe JSONL rows and a Markdown preview from SDK manifests.
Rows include selected profile, task overlays, custom tools, controller health,
result status, and nested reliability, work-quality, efficiency, and
conversation-shape metrics. The first two-row dataset is stored under ignored
runtime evidence at
`runtime/p74_foundrytk_profile_optimization/profile_evaluation_dataset.jsonl`
with preview
`runtime/p74_foundrytk_profile_optimization/profile_evaluation_dataset.md`.
The dataset excludes raw transcript text and private paths.
- [x] P74.3 FoundryTK integration decision
  - [x] Decide whether FoundryTK should remain external guidance, become an
        optional tool provider, or provide trace/evaluation runner integration.
  - [x] Record prerequisites before any prompt optimization, agent optimizer,
        or model fine-tuning work.

P74.3 result: recorded the integration decision under ignored runtime evidence
at
`runtime/p74_foundrytk_profile_optimization/p74_3_integration_decision.md`.
Decision: keep FoundryTK outside the Agent Workbench runtime bridge for now and
use it as external evaluation guidance only. Optional tool-provider,
model-selection, trace/evaluation runner, prompt-optimization, agent-optimizer,
or fine-tuning work requires comparable live overlay-selected SDK runs,
controller-health versus result-validity scoring, public-safe evaluation rows,
compact transcript review, and an explicit treatment comparison plan.

## Phase 75: Comparable Live Overlay-Selected SDK Run Battery

Parent issue: #485

Branch: `feature/p75-live-overlay-sdk-run-battery`

Status: complete

Goal: collect comparable live SDK run evidence for Agent Workbench profiles
using named P73 task overlays, then render P74-compatible public-safe
evaluation rows before any deeper FoundryTK integration or optimization work.

Planned scope:

- Use the same bounded task, evidence contract, profile-run summary contract,
  and public-safe dataset shape across the live runs.
- Use P73-selected profiles and named task overlays so profile and overlay
  choices are visible before and after each run.
- Treat three comparable live SDK run attempts as the minimum smoke gate for
  the evidence pipeline, not as the intended empirical sample size.
- Design and run a factorial battery with declared factors, replication,
  blocking or randomization, and a sample-size rationale large enough to inform
  the next development decision unless the documented stop rule fires.
- Score result validity separately from controller/session health.
- Render public-safe profile-run summaries and P74 evaluation dataset rows from
  live evidence before making any FoundryTK follow-on decision.

Out of scope:

- Adding FoundryTK as a runtime bridge dependency.
- Provisioning Azure resources.
- Installing new worker models.
- Claiming broad model or profile superiority from too few matched runs.
- Delegating GitHub mutation, PR merge, issue closure, or final acceptance to
  worker agents.

Planned tasks:

- [x] P75.1 Run matrix, budget, and stop-rule activation (#489)
  - [x] Select bounded reusable task families suitable for matched
        profile/overlay comparison.
  - [x] Choose the P75 factors: P73 profiles, named overlays, model lanes,
        task families, and repetition or retry lanes.
  - [x] Declare fixed versus exploratory factors, blocking variables,
        randomization or rotation order, replication count, and planned minimum
        analyzable sample size.
  - [x] Preserve replication before breadth if budget or operational limits
        require narrowing the matrix.
  - [x] Define manifest, result, status, profile-run summary, dataset, compact
        transcript, and optional heartbeat evidence paths.
  - [x] Declare supervisor budget and repeated-blocker stop rules before any
        live run.
  - [x] Define how result validity and controller/session health will be
        scored independently.
- [x] P75.2 Live SDK run execution and evidence capture (#486)
  - [x] Launch each run from the selected manifests.
  - [x] Capture SDK event logs, status summaries, result or blocker files, and
        compact transcript review artifacts.
  - [x] Stop after the declared run count or repeated-blocker rule.
  - [x] Verify worker result claims against actual artifacts before classifying
        any run.
- [x] P75.3 Public-safe dataset rendering and profile comparison (#487)
  - [x] Render P74-compatible JSONL rows and Markdown preview from the P75 live
        run manifests.
  - [x] Compare reliability, work quality, efficiency, and conversation-shape
        metrics.
  - [x] Keep controller/session health separate from result validity.
  - [x] Record evidence limits without broad model/profile superiority claims.
- [x] P75.4 Scale decision and closeout (#488)
  - [x] Decide whether FoundryTK remains external guidance or a narrower
        follow-on integration lane is justified.
  - [x] Name prerequisites for any optional tool-provider, trace/evaluation
        runner, model-selection, prompt-optimization, agent-optimizer, or
        fine-tuning follow-on work.
  - [x] Synchronize roadmap, changelog, issue comments, and PR description.
  - [x] Verify and close through the normal PR workflow.

Activation note: P75 starts from P74's integration decision. FoundryTK remains
external guidance until P75 produces enough matched live SDK evidence to justify
a narrower next lane. Underpowered or stopped batteries must be reported as
design or infrastructure evidence, not as profile/model recommendations.

Completion note: P75 produced a 24-row analyzable dataset with healthy
controller status for every row. Result validity was mixed: 9 accepted-candidate
rows, 11 needs-supervisor-review rows, and 4 blocked rows. FoundryTK remains
external guidance; the next useful lane is automated comparison summaries and
clearer task/profile contracts over the public-safe local dataset, not runtime
FoundryTK integration or model selection.

## Phase 76: Profile Evaluation Aggregate Comparison Reports

Parent issue: #491

Branch: `feature/p76-profile-evaluation-aggregate-reports`

Status: complete

Goal: turn P75-style public-safe profile evaluation datasets into aggregate
comparison reports that make profile, overlay, task-family, controller-health,
result-validity, and conversation-shape patterns reproducible and actionable.

Planned scope:

- Add a CLI/report surface that consumes public-safe profile evaluation JSONL
  rows from `agent-workbench foundrytk profile-evaluation-dataset`.
- Aggregate by selected profile, task overlay, inferred task family,
  controller health, result status, and conversation-shape counters.
- Preserve the P75 scoring boundary: controller/session health is separate
  from result validity.
- Render Markdown and machine-readable summary outputs without raw transcript
  text, prompts, credentials, private paths, endpoints, or machine-specific
  values.
- Use the P75 24-row dataset shape as the primary fixture.
- Record whether the aggregate evidence points next to task/profile contract
  repair, another replicated battery, model-lane expansion, or FoundryTK
  integration.

Out of scope:

- Running another live SDK battery.
- Adding FoundryTK as a runtime dependency.
- Claiming model selection or profile superiority beyond the dataset evidence.
- Introducing Azure or external evaluation services.

Planned tasks:

- [x] P76.1 Aggregate report contract and roadmap activation (#492)
  - [x] Add the P76 planning note.
  - [x] Update the roadmap tracker and detailed phase section.
  - [x] Define input schema assumptions, grouping dimensions, summary outputs,
        privacy boundaries, and closeout decision criteria.
  - [x] Record P75 evidence limits so P76 does not overclaim model or profile
        superiority.
- [x] P76.2 Aggregate comparison CLI and tests (#493)
  - [x] Add a command that reads profile evaluation JSONL rows.
  - [x] Write Markdown and JSON summary outputs.
  - [x] Aggregate controller health, result status, profile, overlay,
        task-family, and conversation-shape metrics.
  - [x] Preserve public-safe output boundaries.
  - [x] Add focused tests.
- [x] P76.3 P75 dataset dogfood report and next-lane decision (#494)
  - [x] Render ignored runtime aggregate outputs from the P75 dataset when
        available.
  - [x] Inspect the aggregate report for public-safe content and decision
        usefulness.
  - [x] Update roadmap/changelog/planning with the resulting next-lane
        recommendation.
  - [x] Close out through normal issue/PR hygiene.

Activation note: P76 starts from P75's scale decision. The immediate value is a
reproducible summary layer over existing public-safe evidence, not another live
run. Model-lane expansion and FoundryTK runtime integration remain blocked on
stronger local aggregate evidence and verified multi-model inventory.

Completion note: P76 added
`agent-workbench foundrytk profile-evaluation-aggregate`, which reads
public-safe profile evaluation JSONL rows and writes both Markdown and JSON
aggregate summaries. Dogfooding on the P75 24-row dataset reproduced the core
counts and exposed the main weak cells: `profile-evidence-review` produced all
4 blocked rows and only 2 accepted-candidate rows, while
`manifest-contract-audit` produced 7 accepted-candidate rows and no blocked
rows. The next roadmap lane should prioritize task/profile contract repair,
especially profile-evidence-review fixtures and result-auditor-as-primary
behavior, before another live battery, model-lane expansion, or FoundryTK
runtime integration.

## Phase 77: Profile Contract Repair Plan

Parent issue: #496

Branch: `feature/p77-profile-contract-repair-plan`

Status: complete

Goal: convert the P75/P76 aggregate evidence into a deterministic
task/profile contract repair plan before spending on another live SDK battery.

Planned scope:

- Add a CLI/report surface that consumes P76 aggregate JSON summaries.
- Rank weak profile/overlay/task-family treatment cells by blocked and
  review-heavy outcomes.
- Preserve the P75 scoring boundary: controller/session health is separate
  from result validity.
- Render public-safe Markdown and JSON repair-plan outputs without raw
  transcript text, prompts, credentials, private paths, endpoints, or
  machine-specific values.
- Dogfood the command on the P75 aggregate summary under ignored runtime
  evidence.
- Use the resulting plan to name the next contract-repair implementation lane.

Out of scope:

- Running another live SDK battery.
- Adding FoundryTK as a runtime dependency.
- Provisioning Azure or external evaluation services.
- Claiming model or profile superiority from the P75 dataset.

Planned tasks:

- [x] P77.1 Roadmap and planning activation (#497)
  - [x] Add the P77 planning note.
  - [x] Update the roadmap tracker and detailed phase section.
  - [x] Define input contract, output contract, privacy boundary, and
        closeout criteria.
  - [x] Tie the next-lane rationale to the P75/P76 aggregate evidence.
- [x] P77.2 Repair-plan command and tests (#498)
  - [x] Add a command that reads aggregate JSON.
  - [x] Write Markdown and JSON repair-plan outputs.
  - [x] Rank weak treatment cells and summarize task/profile repair targets.
  - [x] Preserve public-safe output boundaries.
  - [x] Add focused tests.
- [x] P77.3 P75 aggregate dogfood and closeout (#499)
  - [x] Render ignored runtime repair-plan outputs from the P75 aggregate
        summary when available.
  - [x] Inspect the repair plan for public-safe content and decision
        usefulness.
  - [x] Update roadmap/changelog/planning with the resulting next-lane
        recommendation.
  - [x] Close out through normal issue/PR hygiene.

Activation note: P77 starts from P76's decision that task/profile contract
repair is the highest-value lane. The immediate value is a deterministic
repair-plan artifact over existing public-safe evidence, not another live run.
The expected implementation target after P77 is profile-evidence-review task
contract hardening and result-auditor-as-primary behavior repair.

Completion note: P77 added
`agent-workbench foundrytk profile-contract-repair-plan`, which reads
public-safe aggregate JSON and writes Markdown plus JSON repair plans.
Dogfooding on the P75 aggregate summary ranked `profile-evidence-review` as
the top task-family target and `agent-workbench-result-auditor` as the top
profile target. The top weak treatment cell was
`agent-workbench-result-auditor` / `release-readiness-review` /
`profile-evidence-review`, with 0 accepted-candidate, 1
needs-supervisor-review, and 2 blocked rows. The next roadmap lane should
repair profile-evidence-review fixtures and result-auditor-as-primary behavior
before another live battery, model-lane expansion, or FoundryTK runtime
integration.

## Phase 78: Profile Evidence Review Contract Repair

Parent issue: #501

Branch: `feature/p78-profile-evidence-review-contract`

Status: complete

Goal: repair the profile-evidence-review task contract and
result-auditor-as-primary behavior before another live SDK battery.

Planned scope:

- Add a manifest-backed profile-evidence-review contract and ticket renderer.
- Require profile-evidence-review tasks to declare a pre-existing public-safe
  review subject artifact.
- Keep current-run result and blocker paths separate from the review subject.
- Update the standard result-auditor profile so it behaves correctly when it
  is the selected primary profile, not only a subagent.
- Dogfood the repaired contract on a P75-style manifest using existing ignored
  public-safe runtime evidence.

Out of scope:

- Running another live SDK battery.
- Expanding model lanes.
- Adding FoundryTK as a runtime dependency.
- Claiming profile or model superiority.

Planned tasks:

- [x] P78.1 Roadmap and planning activation (#502)
  - [x] Add the P78 planning note.
  - [x] Update the roadmap tracker and detailed phase section.
  - [x] Define the review-subject input contract and output contract.
  - [x] Preserve the P77 evidence-backed rationale.
- [x] P78.2 Profile-evidence-review ticket contract (#503)
  - [x] Add code that identifies profile-evidence-review manifests.
  - [x] Require a pre-existing review subject path for that task family.
  - [x] Render a ticket that separates review subject evidence from current
        run outputs.
  - [x] Add focused tests for valid, missing-subject, unsafe-subject, and CLI
        output cases.
- [x] P78.3 Result-auditor primary-mode repair (#504)
  - [x] Update the standard result-auditor profile for selected-primary use.
  - [x] Require primary-mode runs to use Agent Workbench result contract and
        result writer tools when available.
  - [x] Preserve read-only, no-GitHub, no-commit, and no-whole-job-completion
        boundaries.
  - [x] Add or update catalog/profile tests as needed.
- [x] P78.4 Repaired contract dogfood and closeout (#505)
  - [x] Render ignored runtime ticket/contract artifacts from a repaired
        P75-style manifest with a pre-existing review subject.
  - [x] Inspect generated artifacts for public-safe content and decision
        usefulness.
  - [x] Update roadmap/changelog/planning with the resulting next-lane
        recommendation.
  - [x] Close out through normal issue/PR hygiene.

Activation note: P78 starts from P77's repair-plan recommendation. The target
is not more sample volume yet; it is removing a known self-referential fixture
defect so the next matched replicated live battery measures profile behavior
rather than an avoidable task-contract ambiguity.

Completion note: P78 added
`agent-workbench foundrytk profile-evidence-review-ticket`, a repaired
manifest-backed ticket renderer that requires a pre-existing review subject for
`profile-evidence-review` tasks and separates that subject from current-run
outputs. It also updated `agent-workbench-result-auditor` with explicit
selected-primary behavior. Dogfooding produced valid ignored runtime contract
and ticket artifacts from a repaired P75-style manifest using an existing P75
profile summary as the review subject. The next step should be a matched
replicated live battery over repaired profile-evidence-review cells, not model
lane expansion or FoundryTK runtime integration.

## Phase 79: Repaired Profile Evidence Review Battery

Parent issue: #507

Branch: `feature/p79-repaired-profile-review-battery`

Status: complete

Goal: design and scaffold a sufficiently replicated repaired
profile-evidence-review battery before live execution.

Planned scope:

- Define the repaired profile-evidence-review factorial design.
- Use selected profile, overlay, source-result stratum, and matched review
  subject as declared factors or blocking variables.
- Preserve replication before breadth if runtime limits force narrowing.
- Scaffold run matrix, repaired manifests, and repaired tickets under ignored
  runtime storage.
- Keep live execution as a separately gated follow-on until the full matrix
  and stop rules are ready.

Out of scope:

- Claiming repaired profile behavior before live execution.
- Model-lane expansion.
- FoundryTK runtime integration.
- Running an underpowered smoke and treating it as empirical evidence.

Planned tasks:

- [x] P79.1 Roadmap and planning activation (#508)
  - [x] Add the P79 planning note.
  - [x] Update the roadmap tracker and detailed phase section.
  - [x] Carry forward the P78 validation boundary.
- [x] P79.2 Repaired-cell factorial design (#509)
  - [x] Declare fixed factors, blocking variables, and stop rules.
  - [x] Use a 48-row target matrix:
        2 profiles * 2 overlays * 3 source-result strata * 4 matched subjects.
  - [x] Define a 36-row minimum analyzable threshold.
  - [x] Preserve replication before breadth.
- [x] P79.3 Repaired battery artifact scaffold (#510)
  - [x] Render ignored runtime matrix JSON and Markdown artifacts.
  - [x] Render repaired manifests with pre-existing review subject paths.
  - [x] Render repaired profile-evidence-review tickets with the P78 renderer.
  - [x] Verify generated artifacts are public-safe and structurally valid.

Activation note: P79 starts from P78's repaired contract. The target is a
48-row scaffolded matrix, not a minimal smoke. If execution resources later
force a narrower run, the minimum meaningful repaired-cell decision threshold
is 36 analyzable rows with at least three source subjects per stratum for every
profile/overlay pair.

Completion note: P79 scaffolded a balanced 48-row repaired
profile-evidence-review battery under ignored runtime storage. The matrix
crosses two profiles, two overlays, three source-result strata, and four
matched public-safe P75 profile-run summary subjects per stratum. Generated
artifacts include 48 manifests, 48 repaired tickets, 48 contract JSON files,
and matrix JSON/Markdown previews. Public-safety inspection found no personal
paths, provider URLs, or token-like values. The next phase should execute the
48-row repaired battery; any narrowed execution should preserve at least 36
analyzable rows with three matched source subjects per stratum for every
profile/overlay pair.

## Phase 80: Repaired Profile Evidence Review Execution

Parent issue: #512

Branch: `feature/p80-repaired-profile-review-execution`

Status: completed

Goal: execute and aggregate the repaired profile-evidence-review battery
scaffolded by P79.

Planned scope:

- Revalidate the P79 matrix, manifests, tickets, and contracts.
- Execute the declared 12-row smoke gate.
- Continue toward the full 48-row battery when the smoke gate passes.
- Capture manifests, SDK event logs, status summaries, results or blockers,
  compact transcripts, profile summaries, datasets, aggregate summaries, and
  repair-plan outputs.
- Decide whether repaired profile-evidence-review is stable enough for model
  lane expansion or still needs contract/profile repair.

Out of scope:

- Treating the smoke gate as repaired-profile evidence.
- Model-lane expansion before the repaired-cell battery is aggregated.
- FoundryTK runtime integration.
- Broad profile/model superiority claims.

Planned tasks:

- [x] P80.1 Execution readiness checks (#513)
  - [x] Validate the active shell has Copilot SDK and Pydantic dependencies.
  - [x] Validate representative P79 manifests.
  - [x] Record exact runner command shape and readiness caveats.
- [x] P80.2 Twelve-row smoke gate (#514)
  - [x] Run one matched source subject per stratum across all four
        profile/overlay pairs.
  - [x] Capture SDK events, status summaries, result/blocker files, compact
        transcripts, and profile summaries.
  - [x] Evaluate continuation against the full gate: 10 of 12 rows produced
        result or blocker artifacts, but repeated provider quota errors blocked
        continuation.
  - [x] Report smoke rows as a gate, not as repaired-profile evidence.
- [x] P80.3 Full repaired battery execution (#515)
  - [x] Stop before the full 48-row matrix because the smoke gate failed.
  - [x] Preserve the 36-row minimum analyzable threshold by making no
        repaired-profile behavior claim.
  - [x] Apply declared stop rules without silently narrowing the design.
- [x] P80.4 P80 aggregate and next-lane decision (#516)
  - [x] Render P74/P76-compatible dataset, aggregate summary, and repair-plan
        outputs from P80 manifests.
  - [x] Defer repaired profile-evidence-review validity comparison against the
        P75 baseline because the smoke gate did not reach the 36-row threshold.
  - [x] Keep controller health separate from worker result validity.
  - [x] Decide whether the next lane is model expansion, another repaired
        battery, profile/ticket repair, or FoundryTK runtime integration.

Activation note: P80 starts from the P79 48-row scaffold. The 12-row smoke gate
is an execution-readiness gate only. Repaired profile behavior claims require
at least 36 analyzable rows and preferably the full 48-row matrix.

Completion note: P80 attempted all 12 smoke-gate rows and rendered smoke
dataset, aggregate, and repair-plan outputs under ignored runtime evidence.
The gate produced 10 valid result-or-blocker artifacts and 3 controller/provider
error rows, including repeated provider quota-exceeded errors, so
`smoke_gate_passed=false`. The full 48-row battery was not executed, and no
repaired profile-evidence-review behavior conclusion was drawn. The next lane
is controller/session health repair or quota recovery before another repaired
battery.

## Phase 81: Controller/Session Health Gate

Parent issue: #518

Branch: `feature/p81-controller-session-health-gate`

Status: completed

Goal: add a deterministic public-safe controller/session health gate before
live SDK batteries.

Planned scope:

- Define the P81 health-gate contract and its public-safety boundary.
- Implement a `copilot-sdk health-gate` command over existing SDK manifests,
  status summaries, and event logs.
- Keep controller/session health separate from worker result quality.
- Dogfood the gate against P80 smoke evidence.
- Decide whether the next lane is a full repaired battery rerun after health
  recovery or further SDK summary/health-contract repair.

Out of scope:

- Contacting the live provider as part of the health gate.
- Retrying the P80 repaired battery.
- Reducing the repaired battery sample size below the P79/P80 design.
- Tracking raw transcripts, prompts, worker answers, provider URLs, headers,
  credentials, or personal paths.

Planned tasks:

- [x] P81.1 Health-gate contract (#519)
  - [x] Add a planning note tying P81 to P80's quota/controller-health evidence.
  - [x] Define required inputs, outputs, public-safety boundaries, and
        go/no-go semantics.
  - [x] Record that a failed health gate blocks full repaired-battery
        execution without weakening the factorial design.
- [x] P81.2 Deterministic health-gate command (#520)
  - [x] Add `copilot-sdk health-gate`.
  - [x] Read existing status summaries and SDK event logs without provider
        contact.
  - [x] Emit public-safe JSON and Markdown reports.
  - [x] Classify go/no-go from manifest validity, missing evidence,
        controller/provider errors, and repeated error signatures.
- [x] P81.3 P80 smoke-evidence dogfood (#521)
  - [x] Run the health gate over P80 smoke manifests under ignored runtime
        evidence.
  - [x] Confirm the gate blocks continuation because of repeated quota/provider
        errors.
  - [x] Promote only sanitized counts, classifications, recommendations, and
        artifact paths to tracked docs.
- [x] P81.4 Closeout and next-lane decision (#522)
  - [x] Run focused validation.
  - [x] Prepare child issue and PR closeout evidence.
  - [x] Record whether the next lane is a repaired 48-row battery rerun or
        continued controller/session repair.

Activation note: P81 is an execution-quality repair phase. It protects the
larger repaired profile-evidence-review factorial design by making provider and
controller health a deterministic go/no-go check before another live SDK
battery.

Completion note: P81 added `agent-workbench copilot-sdk health-gate` and
dogfooded it against the 12 P80 smoke manifests. The gate returned `no-go`
with 9 healthy rows, 3 controller-error rows, and repeated sanitized
`quota_exceeded` signatures across 3 rows. P81 confirms that the next empirical
lane remains the full P79/P80 repaired 48-row battery only after
controller/session quota health recovers and the health gate can pass.

## Phase 82: Health-Gated Repaired Battery Execution

Parent issue: #524

Branch: `feature/p82-health-gated-repaired-battery`

Status: completed

Goal: execute the full repaired profile-evidence-review battery only after a
live P81 health gate passes.

Planned scope:

- Scaffold a fresh ignored P82 runtime from the P79 repaired 48-row matrix.
- Run a dedicated live SDK health probe and classify it with
  `copilot-sdk health-gate`.
- Execute the full 48-row repaired battery only if the health probe passes.
- Stop on repeated controller/provider health failures without reducing the
  sample size.
- Render profile-evaluation dataset, aggregate, and repair-plan outputs when
  execution evidence supports them.
- Decide whether repaired profile-evidence-review is stable enough for
  model-lane expansion or still needs targeted repair.

Out of scope:

- Treating a health probe as profile behavior evidence.
- Replacing the full battery with another underpowered smoke.
- Drawing repaired-profile behavior conclusions from fewer than 36 analyzable
  rows.
- Tracking raw transcripts, prompts, worker answers, provider URLs, headers,
  credentials, or personal paths.

Planned tasks:

- [x] P82.1 Scaffold and validate execution runtime (#525)
  - [x] Create a fresh ignored P82 runtime from the P79 repaired 48-row matrix.
  - [x] Update phase, run IDs, governing issue, child issue, seed, paths, and
        SDK homes for P82.
  - [x] Preserve 48 rows across the declared profile, overlay, and stratum
        factors.
  - [x] Validate generated manifests before any live provider call.
  - [x] Inspect generated scaffold artifacts for public-safety issues.
- [x] P82.2 Live health preflight (#526)
  - [x] Run a dedicated live SDK health probe that is not profile behavior
        evidence.
  - [x] Render status, monitor, transcript, and profile summary artifacts.
  - [x] Run `copilot-sdk health-gate` over the probe evidence.
  - [x] Continue to the full battery only if the gate returns `go`.
  - [x] If the gate returns `no-go`, stop and record controller/session health
        evidence without weakening the battery design.
- [x] P82.3 Full repaired 48-row battery execution (#527)
  - [x] Execute all 48 repaired matrix rows only after health preflight passes.
  - [x] Capture SDK events, status summaries, monitor summaries, compact
        transcripts, profile summaries, and result/blocker artifacts.
  - [x] Apply repeated controller/provider stop rules without silently
        narrowing the design.
  - [x] Preserve the 36-row minimum analyzable threshold with balanced stratum
        coverage before any repaired-profile behavior claim.
- [x] P82.4 Aggregate evidence and next-lane decision (#528)
  - [x] Render the P74/P76-compatible profile-evaluation dataset, aggregate
        summary, and P77-style repair plan when enough execution evidence
        exists.
  - [x] Keep controller/session health separate from worker result validity.
  - [x] Compare repaired profile-evidence-review result validity against the
        P75 baseline only when the 36-row threshold is met.
  - [x] Decide whether the next lane is model expansion, targeted repair, or
        continued controller/session health repair.

Activation note: P82 is a health-gated full-battery execution phase. The live
health probe answers whether it is worth spending the full 48-row battery now;
it is not a substitute empirical sample.

Completion note: P82 passed the live health preflight and attempted all 48
repaired battery rows. The full battery produced 40 analyzable result/blocker
artifacts, 8 missing artifacts from quiet-stall/unknown controller rows, no
repeated controller/provider error signatures, and 40 blocked final statuses.
The balanced 3-per-cell threshold was not met because minimum cell coverage was
2. P82 therefore makes no repaired profile-evidence-review behavior claim. The
next lane should repair review-subject path/materialization or SDK run-context
access before another repaired battery.

## Phase 83: Review-Subject Access Contract Repair

Parent issue: #530

Branch: `feature/p83-review-subject-access-contract`

Status: complete

Goal: make declared review subjects readable through a stable public-safe
custom-tool interface before another repaired battery.

Planned scope:

- Add or extend custom SDK tooling so workers can resolve and read the declared
  review subject without filesystem search.
- Return public-safe metadata and bounded content from the declared subject.
- Reject missing, private-looking, current-run-output, or outside-allowed-root
  review subjects.
- Expose the repaired access interface in profile-evidence-review tickets and
  custom tool declarations.
- Dogfood the repair on both a deterministic fixture and a real P75
  profile-summary subject.

Out of scope:

- Rerunning the repaired 48-row battery.
- Model-lane expansion.
- Tracking raw transcripts, provider URLs, headers, credentials, personal
  paths, or raw worker blocker text.

Completed tasks:

- [x] P83.1 Review-subject access contract (#531)
  - [x] Add a planning note tying P83 to the P82 access failure.
  - [x] Define the required review-subject resolver/reader behavior.
  - [x] Define public-safe output fields and redaction boundaries.
  - [x] Record that P83 repairs access/materialization only.
- [x] P83.2 Resolver/reader tool support (#532)
  - [x] Add or extend custom SDK tooling for declared review-subject reads.
  - [x] Return public-safe metadata and bounded content/snippets.
  - [x] Reject missing, private-looking, current-run-output, or outside-root
        review subjects.
  - [x] Expose the tool in profile-evidence-review custom tool declarations.
  - [x] Add focused tests.
- [x] P83.3 Review-subject access dogfood (#533)
  - [x] Run deterministic fixture-level validation.
  - [x] Dogfood against one real P75 profile-summary subject used by the matrix.
  - [x] Render ignored JSON/Markdown evidence.
  - [x] Promote only sanitized counts, paths, and conclusions to tracked docs.
- [x] P83.4 Closeout and next-lane decision (#534)
  - [x] Run focused validation.
  - [x] Prepare child issue and PR closeout evidence.
  - [x] Record whether the next lane is a small live access probe or a repaired
        battery rerun.

Closeout note: P83 added the `agent_workbench_review_subject` SDK tool and
proved it can read both a deterministic fixture subject and a real P75
profile-summary subject declared from a P82 manifest. The next lane is a small
live SDK access probe before another health-gated repaired battery.

## Phase 84: Review-Subject Live Access Probe

Parent issue: #536

Branch: `feature/p84-review-subject-live-access-probe`

Status: complete

Goal: run one small live SDK probe that asks a profile-evidence-review worker to
use `agent_workbench_review_subject` before spending another health-gated
repaired battery.

Planned scope:

- Build one public-safe live probe manifest from existing P82/P75 evidence.
- Preserve the P83 review-subject access contract in the run context and result
  contract.
- Require the worker to use the declared review-subject tool when available.
- Collect result or blocker evidence from exactly one live SDK worker run.
- Render a concise public-safe probe summary under ignored runtime storage.
- Decide whether the next lane can return to a repaired battery or needs
  another targeted access-contract repair.

Out of scope:

- Rerunning the 48-row repaired battery.
- Model-lane expansion.
- Publishing raw transcripts, provider URLs, headers, credentials, personal
  paths, or raw worker blocker text.
- Treating a single probe as repaired profile-evidence-review behavior evidence.

Completed tasks:

- [x] P84.1 Live access probe contract (#539)
  - [x] Add a planning note tying P84 to the P83 closeout decision.
  - [x] Define live probe success and stop criteria.
  - [x] Record the public-safety boundary and evidence artifacts.
- [x] P84.2 Live probe manifest and ticket (#540)
  - [x] Select one real P82 manifest whose declared subject points to P75.
  - [x] Generate P84 manifest, contract, and ticket artifacts.
  - [x] Validate that the manifest exposes `agent_workbench_review_subject`.
- [x] P84.3 Live SDK access probe execution (#537)
  - [x] Run one live SDK profile-evidence-review probe.
  - [x] Monitor and collect result or blocker artifacts.
  - [x] Evaluate whether the worker consumed the declared access path.
- [x] P84.4 Closeout and next-lane decision (#538)
  - [x] Run focused validation.
  - [x] Prepare child issue and PR closeout evidence.
  - [x] Record whether the next lane is a repaired battery or another targeted
        access repair.

Closeout note: P84 ran one live profile-evidence-review SDK probe. The worker
requested and executed `agent_workbench_review_subject` once, wrote an
`accepted-candidate` result, and validated the result artifact. The next lane
can return to a health-gated repaired battery using the P83/P84 access repair;
P84 remains access evidence only, not repaired behavior evidence.

## Phase 85: Health-Gated Repaired Profile-Evidence-Review Battery Rerun

Parent issue: #542

Branch: `feature/p85-health-gated-repaired-battery-rerun`

Status: complete

Goal: run the full health-gated repaired profile-evidence-review battery with
the P83/P84 declared review-subject access repair included.

Planned scope:

- Preserve the P79/P80/P82 48-row repaired battery design.
- Regenerate P85 runtime manifests, tickets, and contracts with
  `agent_workbench_review_subject` declared in custom tools.
- Run a live P81 health preflight before spending the 48-row battery.
- Execute all 48 rows only if the health gate returns `go`.
- Render ignored public-safe monitor, summary, aggregate, and evaluation
  evidence.
- Require at least 36 analyzable rows and balanced minimum cell coverage before
  making repaired profile-evidence-review behavior claims.

Out of scope:

- Reducing the matrix because the run is expensive.
- Model-lane expansion.
- Publishing raw transcripts, provider URLs, headers, credentials, personal
  paths, provider-side identifier strings, or raw worker blocker text.
- Treating the health probe as empirical profile-evidence-review behavior
  evidence.

Planned tasks:

- [x] P85.1 Full repaired battery rerun activation (#544)
  - [x] Add a planning note tied to the P84 live access proof.
  - [x] Record the 48-row design, health-gate requirements, thresholds, and
        stop rules.
  - [x] Keep P85 distinct from P84 access evidence.
- [x] P85.2 Runtime matrix and manifest generation (#545)
  - [x] Reuse the P79/P80/P82 balanced 48-row repaired battery structure.
  - [x] Ensure every manifest declares `agent_workbench_review_subject`.
  - [x] Validate all manifests, custom profiles, and repaired tickets.
  - [x] Render public-safe matrix and validation summaries under ignored
        runtime storage.
- [x] P85.3 Live health preflight (#546)
  - [x] Generate a separate live health-probe manifest.
  - [x] Run the probe before the 48-row battery.
  - [x] Render the P81 health-gate report.
  - [x] Stop before the full battery if the decision is not `go`.
- [x] P85.4 Full repaired battery execution (#547)
  - [x] Execute all 48 repaired rows after a passing health gate.
  - [x] Monitor each row and collect result or blocker artifacts.
  - [x] Render compact transcripts, profile summaries, monitor summaries, and
        execution progress under ignored runtime storage.
  - [x] Do not silently narrow the sample after partial failures.
- [x] P85.5 Battery evaluation and closeout (#543)
  - [x] Render the profile-evaluation dataset and aggregate report.
  - [x] Evaluate analyzable row count, final-status distribution, and balanced
        cell coverage.
  - [x] Compare repaired validity against P75 only if thresholds are met.
  - [x] Update roadmap, changelog, planning note, issues, and PR with the
        outcome.

Activation note: P85 is the next empirical battery after P83/P84 repaired and
live-probed declared review-subject access. It should not reduce the sample size
or replace the full balanced design with another smoke.

Evaluation note: P85 met the repaired-battery evidence thresholds with 48
analyzable rows, 12 balanced source cells at 4 rows per cell, 48 healthy
controller rows, 47 accepted-candidate results, 1 needs-supervisor-review
result, and 0 blocked results. Compared with the P75 profile-evidence-review
baseline, accepted rows increased from 2 to 47, blocked rows decreased from 4
to 0, and needs-supervisor-review rows decreased from 6 to 1. GitHub issue/PR
closeout proceeds from the resumed session with authenticated `gh` access.

Closeout note: P85 merged through PR #548 at
`625c26dc72d4263c2d29716965d7387aac05462a`, and parent issue #542 closed on
merge.

## Phase 86: Dev Validation Toolchain Repair

Parent issue: #549

Branch: `feature/p86-dev-validation-toolchain-repair`

Status: complete

Goal: make the previously skipped `mypy src` and
`pre-commit run --all-files` validation gates reproducible and runnable.

Scope:

- Add a reproducible development dependency extra for validation tools.
- Add a minimal pre-commit configuration for the repository's validation gates.
- Repair type-checking issues so `mypy src` passes.
- Verify `pre-commit run --all-files` runs successfully.

Out of scope:

- New workflow features.
- Live SDK reruns.
- Model-lane evaluation.
- Broad refactors unrelated to validation tooling or type checking.

Planned tasks:

- [x] P86.1 Dev dependency contract
  - [x] Declare validation tools in `pyproject.toml`.
  - [x] Confirm the active venv has the declared tools.
- [x] P86.2 Pre-commit configuration
  - [x] Add a minimal `.pre-commit-config.yaml`.
  - [x] Confirm `pre-commit run --all-files` invokes the intended checks.
- [x] P86.3 Type-check repair
  - [x] Fix or narrowly configure current `mypy src` failures.
  - [x] Keep runtime behavior unchanged except where a type defect reveals an
        actual bug.
- [x] P86.4 Validation and closeout
  - [x] Run `ruff format src tests`.
  - [x] Run `ruff check src tests`.
  - [x] Run `mypy src`.
  - [x] Run `pytest tests -q`.
  - [x] Run `pre-commit run --all-files`.
  - [x] Update roadmap, changelog, issue, and PR state.

Closeout note: P86 added a reproducible `dev` extra, added a focused
pre-commit configuration, repaired current type-check failures, and verified
that `mypy src` and `pre-commit run --all-files` pass. P86 merged through PR
#550 at `2c323fa60591809bdd23a05c745f7442f4215b58`, and parent issue #549
closed on merge.

## Phase 87: Real-Project ROI Roadmap Reset

Parent issue: #551

Branch: `feature/p87-real-project-roi-roadmap-reset`

Status: complete

Goal: reset the Agent Workbench roadmap around real-project ROI and make
P87-P92 the next detailed tranche.

Scope:

- Mark P86 complete after PR #550.
- Add `planning/p87_p92_real_project_roi_roadmap.md`.
- Summarize the P55, P63, P85, and P86 evidence into one decision memo.
- Park profile-battery work unless it answers a direct real-project ROI
  question.
- Add the strategic P93-P100 arc and detailed P87-P92 tranche to this roadmap.
- Update `CHANGE_LOG.md` and GitHub issue/PR state.

Out of scope:

- Live SDK or local-worker runs.
- Additional profile/model batteries.
- Implementing document-indexing recipe v2.
- Creating a production document index.

Planned tasks:

- [x] P87.1 Roadmap status reset
  - [x] Mark P86 complete with merge and issue-close evidence.
  - [x] Add P87-P92 issue tracker rows with parent issue anchors.
  - [x] Add P93-P100 strategic planned rows without opening those issues yet.
- [x] P87.2 Evidence synthesis
  - [x] Summarize P55 document-indexing evidence.
  - [x] Summarize P63 recipe-pilot stop decision.
  - [x] Summarize P85 profile-battery repair result.
  - [x] Summarize P86 validation-gate repair.
- [x] P87.3 Real-project ROI roadmap note
  - [x] Add the P87-P92 tranche note.
  - [x] Define the default rule that profile/model batteries are parked unless
        tied to direct real-project ROI.
  - [x] Define the validation and live-run gate policy.
- [x] P87.4 Planning closeout
  - [x] Run planning-only validation.
  - [x] Prepare GitHub issue and PR closeout state.
  - [x] Prepare final `main` verification for after merge.

Closeout note: P87 reset the roadmap around real-project ROI, added the
P87-P92 planning note, opened P87-P92 parent issues, marked P86 complete, and
parked profile/model batteries unless they answer a direct real-project ROI
question. Validation passed with `ruff format src tests`, `ruff check src
tests`, `mypy src`, `pytest tests -q`, `pre-commit run --all-files`, and
`git diff --check`. P87 merged through PR #557 at
`47dd779cad8c6c2dd9e7b745baf47d6de2f18924`, and parent issue #551 closed on
merge.

## Phase 88: Real-Corpus Benchmark Registry

Parent issue: #552

Branch: `feature/p88-real-corpus-benchmark-registry`

Status: closeout

Goal: define the real-corpus benchmark registry for the real-project ROI
tranche.

Planned scope:

- Define candidate public technical corpora, starting with TSA23/MP11-style
  forestry planning documents.
- Record corpus value, source availability, expected downstream use, risk, and
  audit burden.
- Choose exactly one bounded first corpus slice for the next live run.
- Record source provenance, document IDs, chunk scope, budget boundary, and
  stop rules.

Out of scope:

- Running local workers.
- Expanding to multiple corpora before the first slice is selected.
- Creating a production index.

Completed tasks:

- [x] P88.1 Candidate corpus registry (#558)
  - [x] Compare candidate public technical corpus slices by readiness,
        downstream value, risk, and audit burden.
  - [x] Track a public-safe candidate registry.
  - [x] Keep raw documents, raw text, prompts, and worker outputs out of
        tracked files.
- [x] P88.2 First-slice selection (#559)
  - [x] Select exactly one bounded corpus slice.
  - [x] Record source provenance, document ID, source hash, page/chunk scope,
        and existing evidence.
  - [x] Explain why broader or alternate slices are deferred.
- [x] P88.3 Budget and stop-rule record (#560)
  - [x] Define what later phases must provide before any live run.
  - [x] Preserve the P63 single-attempt lesson.
  - [x] Require one model/provider lane, one bounded corpus slice, hard stop
        rules, and no direct-supervisor baseline until a quality-valid
        delegated candidate exists.
- [x] P88.4 Registry closeout and P89 handoff (#561)
  - [x] Update roadmap, changelog, planning note, parent/child issue state, and
        PR state.
  - [x] Run full validation gates.
  - [x] Record the P89 handoff constraints from P88.

P88 originally selected the P63 repeat slice, then P89.0 amended the source
scope to `p88_tsa23_2012_data_package_full_document_pages_001_041`: the full
2012 100 Mile House TSA data package `tsa23_2012_23tsdp12`, pages 1-41,
represented by all six tracked chunks in the document manifest. This keeps one
complete useful document-indexing unit in scope while still requiring P89 to
change execution shape before any live repeat.

Tracked P88 artifacts:

- `planning/phase88_real_corpus_benchmark_registry.md`;
- `benchmarks/document_library/p88_candidate_corpus_registry.json`; and
- `benchmarks/document_library/p88_selected_corpus_slice.json`.

P88 does not authorize live model execution. P89 must stay dry-run and
materialization-only: section-level tickets, explicit chunk-ID enum,
deterministic JSONL validation, deterministic repair where possible, and no
live worker call.

## Phase 89: Document-Indexing Recipe V2

Parent issue: #553

Branch: `feature/p89-document-indexing-recipe-v2`

Status: closeout

Goal: build document-indexing recipe v2 from the P63 lessons.

Planned scope:

- Repair the P63 recipe shape with smaller section-level tickets.
- Add explicit chunk-ID enum handling.
- Add deterministic JSONL validation and deterministic repair where possible.
- Keep raw PDF text and worker outputs in ignored runtime paths.
- Produce only sanitized manifests, summaries, and decision artifacts in
  tracked files.

Out of scope:

- Live worker execution.
- Supervisor audit loops.
- Production index promotion.

Completed tasks:

- [x] P89.0 Full-document TSA23 data package scope amendment (#567)
  - [x] Update the P88 selected-slice artifact to cover pages 1-41 across all
        six tracked chunks.
  - [x] Update roadmap, changelog, and planning surfaces so the full-document
        scope is explicit.
  - [x] Preserve no-live-execution gates until P89 dry-run materialization and
        validation pass.
- [x] P89.1 Recipe v2 ticket and manifest shape (#563)
  - [x] Add the P89 v2 materializer script.
  - [x] Split the full selected data package into smaller section-level
        runtime tickets.
  - [x] Keep rendered tickets and raw source text under ignored `runtime/`.
- [x] P89.2 Chunk-ID enum and validation contract (#564)
  - [x] Generate an explicit six-value chunk-ID enum from the selected full
        document.
  - [x] Require generated tickets and candidate validation to use only the
        selected chunk IDs.
- [x] P89.3 Deterministic JSONL repair path (#565)
  - [x] Add deterministic JSONL validation.
  - [x] Repair only safe mechanical defects.
  - [x] Reject unknown chunk IDs after repair.
- [x] P89.4 Dry-run materialization and closeout (#566)
  - [x] Materialize full-document dry-run artifacts without live model contact.
  - [x] Add focused tests for materialization and JSONL validation/repair.
  - [x] Update roadmap, changelog, planning note, issue state, and PR state.

P89 materialized the full `tsa23_2012_23tsdp12` data package, pages 1-41, into
60 unique page/section units and 120 ignored runtime ticket placeholders across
`structure` and `content_metadata` passes. The tracked artifacts are sanitized:

- `planning/phase89_document_indexing_recipe_v2.md`;
- `benchmarks/document_library/p89_chunk_id_enum.json`;
- `benchmarks/document_library/p89_jsonl_validation_contract.json`;
- `benchmarks/document_library/p89_validation_input_manifest.json`;
- `benchmarks/document_library/p89_recipe_v2_materialization_manifest.json`; and
- `benchmarks/document_library/p89_dry_run_materialization_summary.json`.

P89 still does not authorize live model execution. It leaves P90 with a
full-document source scope, explicit chunk-ID enum, runtime ticket placeholders,
candidate JSONL placeholders, and deterministic validation/repair contract.

## Phase 90: Full-Document Candidate Extraction Run

Parent issue: #554

Branch: `feature/p90-full-document-candidate-packet`

Status: complete

Goal: run actual worker extraction against the P89 full-document packet and
produce candidate records before doing more audit/reporting design.

Planned scope:

- Run P89 section-level tickets against one named local worker lane.
- Capture raw worker results and candidate JSONL under ignored `runtime/`.
- Run deterministic JSONL validation and deterministic repair where possible.
- Track only sanitized extraction summaries in `benchmarks/document_library/`.
- Stop on provider failure, repeated format failure, invalid chunk IDs, missing
  token evidence when needed, or budget/attempt boundary.

Out of scope:

- Production index assembly.
- Direct-supervisor baseline runs before a quality-valid delegated candidate
  exists.
- Broad model comparisons.
- Claiming accepted records before source audit.

Activation tasks:

- [x] P90.0 Live extraction smoke over one complete section.
  - [x] Run the P89 `structure` ticket for
        `tsa23_2012_23tsdp12__pages_001_008__p004__s02`.
  - [x] Run the matching `content_metadata` ticket.
  - [x] Validate or deterministically repair candidate JSONL.
  - [x] Track a sanitized smoke summary without raw source text or raw worker
        output.
- [x] P90.1 Side-by-side model-lane extraction batch.
  - [x] Run the first 10 P89 `structure` tickets against
        `qwen3.6:35b-a3b-q8_0`.
  - [x] Run the same 10 tickets against `qwen3.6:35b-a3b-bf16`.
  - [x] Validate or deterministically repair candidate JSONL for both lanes.
  - [x] Track a sanitized side-by-side summary without raw source text or raw
        worker output.
- [x] P90.2 Full-document extraction execution.
  - [x] Add a resumable full-document q8 extraction runner.
  - [x] Run all 60 `structure` tickets.
  - [x] Run all 60 `content_metadata` tickets.
  - [x] Keep raw worker outputs and candidate JSONL under ignored `runtime/`.
- [x] P90.3 Validation/repair summary and stop-rule decision.
  - [x] Validate every ticket output through the P89 deterministic validator.
  - [x] Summarize attempted, completed, blocked, valid, invalid, repaired, and
        zero-record counts by ticket type.
  - [x] Record fatal validation error classes and extraction modes.
  - [x] Decide `ready_for_source_audit`, `repair_protocol_first`,
        `provider_or_runtime_blocked`, or `manual_review_needed`.
- [x] P90.4 Candidate packet handoff for source audit.
  - [x] Produce a public-safe packet manifest with runtime path inventory.
  - [x] Recommend a bounded source-audit sample.
  - [x] State explicitly that all records remain candidates until source audit.

P90.0 actual extraction smoke produced
`benchmarks/document_library/p90_actual_extraction_smoke_summary.json`. Two live
`qwen3.6:35b-a3b-q8_0` worker calls completed over one full section pair:
`structure` and `content_metadata`. They produced 51 valid raw candidate records
after deterministic extraction/repair into JSONL. No record is accepted yet:
source audit has not run. Observed protocol defects are material and must shape
P90.1: the structure pass returned prose plus fenced JSONL, and the content pass
returned key/value blocks that required deterministic conversion before
validation.

P90.1 side-by-side model-lane batch produced
`benchmarks/document_library/p90_qwen36_side_by_side_batch_summary.json`.
Twenty live worker calls completed over the first 10 P89 `structure` tickets:
10 with `qwen3.6:35b-a3b-q8_0` and 10 with `qwen3.6:35b-a3b-bf16`. The q8 lane
produced 49 schema-valid candidate records over 9 valid runs; the bf16 lane
produced 64 schema-valid candidate records over 8 valid runs. Three completed
runs emitted malformed/key-value records that deterministic validation rejected.
These are still raw candidates only: P90 has not performed source audit or
accepted records into an index.

Detailed P90.2-P90.4 execution plan:
`planning/phase90_full_document_candidate_packet.md`. The primary lane is
`qwen3.6:35b-a3b-q8_0` because P90.1 showed better protocol validity than the
bf16 lane. The target work product is one complete full-document candidate
packet ready for source audit, not a production index.

P90.2-P90.4 produced
`benchmarks/document_library/p90_full_document_candidate_packet_summary.json`
and
`benchmarks/document_library/p90_full_document_candidate_packet_manifest.json`.
All 120 P89 tickets completed: 60 `structure` and 60 `content_metadata`.
Deterministic validation marked 94 runs valid and 26 invalid, with 800 repaired
candidate records emitted across the full document. The stop decision is
`ready_for_source_audit`; the packet is not an accepted index, and the accepted
record count remains zero until source audit.

## Phase 91: Source-Audit Decision Packets

Parent issue: #555

Branch: `feature/p91-source-audit-decision-packet`

Status: complete

Goal: source-audit a bounded sample from the P90 full-document candidate packet
and produce a decision packet that separates quality, protocol, and economics
implications.

Planned scope:

- Select a bounded mixed sample from the P90 packet.
- Audit sampled candidate records against ignored P89 source excerpts.
- Classify records as `accepted`, `repairable`, `rejected`, or
  `needs_review`.
- Classify zero-record and invalid-run defects separately from record quality.
- Generate a non-authoritative reporting-worker draft from sanitized audit rows.
- Keep the paid supervisor focused on source audit and final acceptance
  decisions.
- Split task economics from repository governance overhead.
- Define the decision-packet shape and supervisor approval boundary.

Out of scope:

- Delegating final acceptance authority.
- Raw transcript, raw PDF text, provider URL, header, or credential handling in
  tracked artifacts.
- New live benchmarking unless gated by prior phases.

Activation tasks:

- [x] P91.1 Audit-sample manifest.
  - [x] Select valid `structure` and `content_metadata` records.
  - [x] Include invalid-run records with emitted repaired candidates.
  - [x] Include all zero-record runs as run-level defect rows.
  - [x] Keep sample manifest public-safe.
- [x] P91.2 Supervisor source-audit packet.
  - [x] Define audit statuses and defect classes.
  - [x] Audit sampled records against ignored source excerpts.
  - [x] Report accepted, repairable, rejected, needs-review, and defect counts.
- [x] P91.3 Reporting-worker draft packet.
  - [x] Generate a sanitized non-authoritative summary draft from audit rows.
  - [x] Keep the supervisor audit rows as the authority.
- [x] P91.4 Decision and closeout.
  - [x] Decide scale audit, repair protocol, promote seed, switch model/prompt,
        or stop.
  - [x] Split quality, protocol, and economics/governance implications.

Detailed P91 plan: `planning/phase91_source_audit_decision_packet.md`.

P91 produced `benchmarks/document_library/p91_source_audit_sample_manifest.json`,
`benchmarks/document_library/p91_supervisor_source_audit_packet.json`,
`benchmarks/document_library/p91_reporting_worker_draft_packet.json`, and
`benchmarks/document_library/p91_source_audit_decision_packet.json`. The bounded
sample audited 16 candidate records plus six zero-record run defects. The
sample produced eight accepted records, two repairable records, six rejected
records, and no needs-review records. The decision is `promote_seed`, scoped to
the audited sample only; the full P90 packet still requires additional audit
before any broad index promotion.

P91 source-quote scoring recalibration (#573) replaced binary exact quote
containment with functional source-support levels. The recalibrated packet adds
`benchmarks/document_library/p91_source_quote_scoring_recalibration_delta.json`.
The accepted sample count remains eight, but repairable records rise from two
to seven, rejected records fall from six to one, and useful sample yield rises
from 0.625 to 0.938. The decision remains `promote_seed`; the change affects
how much good work is preserved for repair, not the immediate next action.

## Phase 92: Packaged Graph-Shaped Pilot

Parent issue: #556

Branch: `feature/p92-whole-document-supervisor-pilot`

Status: closeout

Goal: test whether one whole-document delegated supervisor job can produce a
useful document-metadata seed with much lower paid coordinator micromanagement
than the P89/P90 section-ticket battery.

Active scope:

- Represent the P92 pilot as a graph template:
  select, materialize whole-document ticket, run delegated document supervisor,
  validate report, bounce once or audit seed, decide.
- Materialize one ignored runtime ticket for the full
  `tsa23_2012_23tsdp12` data-package text, with a compact delegated supervisor
  report contract and bounce ticket.
- Use a dedicated `document-metadata-extraction-supervisor` custom-agent skin
  with full local tool access for source inspection, search, bounded validation,
  subagent audit, and writing the assigned runtime report.
- Keep the coordinator role thin: select the document, launch one job, run
  deterministic report validation, issue at most one compact bounce, then make
  the final decision.
- Compare the whole-document delegated-supervisor shape against the measured
  P90/P91 chunk-pipeline coordinator overhead.
- Preserve separated quality, protocol, and economics outcomes.

Out of scope:

- Ungated repeated live runs.
- Production release.
- Broad corpus scale-up before the pilot decision packet is reviewed.
- Treating exact quote matching as the only valid source-anchor success mode.

Activation tasks:
- [x] P92.1 Whole-document supervisor graph template and role skin.
  - [x] Create `document_library_whole_document_supervisor_graph.json` under
        templates/workbench_templates/ with a graph-shaped workflow:
        select document → materialize whole-doc ticket → run delegated doc
        supervisor → validate report → bounce once or audit seed → decide.
  - [x] Create the `document-metadata-extraction-supervisor.agent.md` custom-agent
        skin under `.github/agents/` with full local tool access for source
        inspection, search, bounded validation, subagent audit, and writing
        the assigned runtime report.
  - [x] Ensure graph template is generic enough to apply to other corpora beyond
        TSA23 once the P94 schema contract is stable.
- [x] P92.2 Bounded pilot gate definition and ROI hypothesis.
  - [x] Define the pilot gate: what conditions must hold before this run counts
        as a valid test of whole-document delegation.
  - [x] Formulate the ROI hypothesis: expected reduction in paid-coordinator
        micromanagement tokens compared to the P90/P91 chunk-pipeline baseline
        (recorded at 236,008 cached-input tokens minimum).
  - [x] Record the ROI estimate at
        `benchmarks/document_library/p92_whole_document_supervisor_roi_estimate.json`.
- [x] P92.3 Runtime ticket, compact bounce ticket, and report contract
  materialization.
  - [x] Materialize one ignored runtime ticket for the full
        `tsa23_2012_23tsdp12` data-package text under
        `runtime/document_library/tsa23_tsr/p92_whole_document_supervisor_pilot/`.
  - [x] Create a compact delegated-supervisor report contract at
        `benchmarks/document_library/p92_whole_document_supervisor_report_contract.json`
        specifying expected output schema, final marker string, and field
        requirements.
  - [x] Materialize a compact bounce ticket template for one audit/repair loop
        if the report fails validation.
  - [x] Write pilot manifest at
        `benchmarks/document_library/p92_whole_document_supervisor_pilot_manifest.json`
        and gate decision at
        `benchmarks/document_library/p92_whole_document_supervisor_gate.json`.
- [x] P92.4 One live delegated-supervisor run with token-span measurement.
  - [x] Accept the R3 run: launched `qwen3.6:35b-a3b-bf16` through the
        `document-metadata-extraction-supervisor` skin in autopilot mode.
  - [x] Produced a deterministic-valid 28-record report.
  - [x] Report reached the required final marker, used the expected model and
        full-tool supervisor surface, and had zero bridge deviations.
  - [x] Measured coordinator token span: 449,382 tokens (447,232 cached-input),
        against the P90/P91 minimum of 236,008 tokens.
- [x] P92.5 Report validation, compact audit, and scale/repair/switch/stop
  decision.
  - [x] Run deterministic validation on the 28-record report — all fields pass.
  - [x] Compile a compact audit summary verifying model lane, tool surface,
        zero bridge deviations, and correct report schema.
  - [x] Write the decision packet at
        `benchmarks/document_library/p92_whole_document_supervisor_decision_packet.json`
        separating quality-valid candidate (yes), protocol-accepted candidate
        (yes), economics (not_yet_proven).
  - [x] Final decision: `accept_seed_for_coordinator_audit` — authorize further
        coordinator-level audit of the seed but block broader corpus scale-up
        pending lower launch and cached-context overhead.

P92.1-P92.3 retargeted the pilot away from coordinator-built microtickets and
toward one whole-document delegated supervisor job. The tracked P92 artifacts
are:
`templates/workbench_templates/document_library_whole_document_supervisor_graph.json`,
`.github/agents/document-metadata-extraction-supervisor.agent.md`,
`benchmarks/document_library/p92_whole_document_supervisor_pilot_manifest.json`,
`benchmarks/document_library/p92_whole_document_supervisor_gate.json`,
`benchmarks/document_library/p92_whole_document_supervisor_report_contract.json`,
and `benchmarks/document_library/p92_whole_document_supervisor_roi_estimate.json`.
The raw full-document ticket and bounce ticket remain ignored under
`runtime/document_library/tsa23_tsr/p92_whole_document_supervisor_pilot/`.
The accepted R3 live run used `qwen3.6:35b-a3b-bf16` through the
`document-metadata-extraction-supervisor` skin in autopilot mode. It produced a
deterministic-valid 28-record report, reached the required final marker, used
the expected model and full-tool supervisor surface, and had zero bridge
deviations. The tracked
`benchmarks/document_library/p92_whole_document_supervisor_decision_packet.json`
separates the result into a quality-valid candidate, a protocol-accepted
candidate, and economics that are not yet proven. The measured coordinator span
was 449,382 tokens, including 447,232 cached-input tokens, against the recorded
236,008-token P90/P91 minimum. The decision is
`accept_seed_for_coordinator_audit`; broader scale-up remains blocked on lower
launch and cached-context overhead.

## Phase 93: Second Public Corpus Application

Parent issue: #576

Branch: `feature/p93-second-public-corpus-application`

Status: complete (merged via PR #577)

Goal: apply the repaired document-indexing workflow to a second public
technical corpus after P92 produces a reviewed decision packet.

Activation tasks:
- [x] P93.0 Activate feature branch and prepare corpus slice.
  - [x] Check out `feature/p93-second-public-corpus-application` from current main.
  - [x] Select a second public technical corpus (distinct from the TSA23 source used in P90-P92).
  - [x] Slice into extractable sections matching the P89 ticket shape.
- [x] P93.1 Run supervisor pilot over the new corpus slice.
  - [x] Execute `structure` and `content_metadata` tickets against
        `qwen3.6:35b-a3b-q8_0` with the same document-metadata-extraction-supervisor skin.
  - [x] Validate candidate JSONL through the deterministic validator used in P90-P92.
  - [x] Confirm zero bridge deviations against expected evidence format.
- [x] P93.2 Generalize verification: confirm protocol works beyond original TSA23 source.
  - [x] Compare record yield and validation outcomes against P90-P92 baselines.
  - [x] Document any corpus-specific defects or adaptations in a planning note.

P93 produced no new tracked artifacts beyond what PR #577 already merged.
The supervisor pilot validated that the P90-P92 document-indexing protocol
generalizes to a second public corpus: record yield was consistent, validation
passed with zero bridge deviations, and no corpus-specific defect class emerged
that would block index promotion. The next step is P94: promote these records
into a project-owned index format.

## Phase 94: Project-Owned Index Promotion

Parent issue: #578

Branch: `feature/p94-project-owned-index-promotion`

Status: complete (merged via PR #579)

Goal: promote accepted or repaired records into a project-owned index format
with source hashes, page/chunk anchors, model lane, audit status, and
provenance.

Activation tasks:
- [x] P94.0 Design the promoted index schema contract.
  - [x] Define fields: source hash, page/chunk anchor, model lane, audit status,
        provenance metadata, and record content.
  - [x] Ensure the schema is stable enough that subsequent phases (P95+)
        validate against it to avoid rework if format changes.
- [x] P94.1 Aggregate accepted/repaired records from P90-P93 into project-owned index.
  - [x] Promote 47 records with complete source anchors and audit metadata.
  - [x] Verify each record carries a valid provenance chain back to the
        original source document.
- [x] P94.2 Validate provenance chain integrity across all promoted records.
  - [x] Run deterministic provenance validation: every source hash resolves,
        page/chunk anchors are consistent, audit status is documented.
  - [x] Record any orphaned or incomplete provenance as defects (expected zero).

P94.0-P94.2 produced `benchmarks/document_library/` index records for the
project-owned index. All 47 promoted records have complete source anchors and
audit metadata. Provenance chain integrity was validated across all promoted
records: every source hash resolves, page/chunk anchors are consistent, and
audit status is documented. The project-owned index is now a stable schema
contract for P95+ phases to query against.

Key linkage to subsequent phases:
- P95 (Retrieval And Modelling-Agent Usability) queries this promoted index —
  the index format from P94 must remain stable or any changes must be tracked
  as a breaking schema change with a migration plan.
- P96 (Yield And Audit-Cost Model Comparison) uses this index as the baseline
  against which to compare worker/model lane yield differences.

## Phase 95: Retrieval And Modelling-Agent Usability — COMPLETE

Parent issue: #580

Branch: `feature/p95-index-retrieval-usability`

Status: **complete** — all 4 child tasks closed (#581-#584). Close parent issue #580 after merging the feature branch.

Goal: add retrieval and use-case surfaces that help modelling agents find and
cite source-backed facts from promoted public-document indexes.

Key Advisor insight (2026-07-11):
- The P94 promoted index (47 records) must become a stable schema contract that
  subsequent phases validate against to avoid rework if format changes.
- Consider adding a coordinator ticket-assembly cost reduction subtask given
  the P92 overhead measured at 449,382 tokens per document (~$0.087).

Tasks:
- [x] P95.1 Select 1-2 retrieval use cases scoped to the P94 index format (#581)
  - Use Case 1: Page/Chunk Anchor Lookup — "find all source-backed facts about page X-Y of document D"
  - Use Case 2: Full-Document Provenance Trace — "show every record from document D grouped by model lane and audit status"
  - Documented in `planning/phase95_retrieval_use_case_selection.md`
- [x] P95.2 Define query contract: input/output schema, provenance inclusion rules (#582)
  - 4 JSON schemas in `templates/query_schemas/`
  - Field mapping grounded in P94 metadata (source_hash, document_id, page_anchor, chunk_id, model_lane, audit_status, is_dedup)
  - Documented in `planning/phase95_query_contract.md`
- [x] P95.3 Implement retrieval against promoted index (#583)
  - `src/agent_workbench/retrieval.py` — IndexRecord, PromotedIndex, query_by_page_range(), trace_full_document()
  - `src/agent_workbench/cli.py` — `retrieve` subcommand with list-docs/page-range/trace operations
  - All three CLI operations verified against real data (3 docs, 16 records)
  - Bugfix commit: `9e136a7` (missing page-range handler in cli.py)
- [x] P95.4 Write a modelling-agent usage example (#584)
  - `templates/retrieval_usage_example.md` — end-to-end walkthrough for both use cases
  - Includes synthetic run script, schema reference, and agent guidance notes

## Phase 96: Yield And Audit-Cost Model Comparison

Parent issue: #585
Child issues: #586 closed, #587 closed, #588 closed, #589 closed

Branch: `feature/p96-yield-audit-cost-model-comparison`

Status: **complete (qualified)** — corrected run p96_4 produced token-level
comparison; full accepted-record classification yield not executed.

Corrected run metadata:
- `runtime/agent_jobs/p96_4_baseline_probe.md` — status: completed, 336 output tokens
- `runtime/agent_jobs/p96_4_candidate_probe.md` — status: completed, 311 output tokens
- Verdict superseded from `insufficient_evidence` to `attempted_with_partial_signal`

Goal: compare worker/model lanes only where they affect accepted-record yield,
repairable-record yield, or supervisor audit cost.

Key Advisor insight (2026-07-11):
- Frame this as a **recipe-stability confirmation**, not a deep model-lane ranking.
  After P87-P94 the only model family with two variants is `qwen3.6:35b-a3b-q8_0`
  vs `qwen3.6:35b-a3b-bf16`. A comparison between quantization variants alone
  risks becoming profile-evidence-review-in-disguise, which the strategic arc
  (p87_p92) has already decided to park.
- Only compare lanes where they directly affect accepted-record yield or supervisor
  audit cost per the ROI thesis; exclude pure latency/throughput claims.

Tasks:
- [x] P96.1 Define comparison boundary and protocol (#586)
  - `planning/phase96_comparison_protocol.md` created; includes recipe-stability framing,
    P87-P92 boundary rules, and remote Ollama model-verification assumptions.
- [x] P96.2 Select exactly one model lane to compare against baseline (#587)
  - `planning/phase96_model_lane_selection.md` created with baseline/candidate lanes
    and remote-ollama verification assumptions.
  - Reproducible run manifest variables declared in
    `benchmarks/document_library/tsa23_tsr/p96_model_lane_comparison_manifest.json`.
- [x] P96.3 Run bounded comparison on one document, one chunk set (#588)
  - Record accepted/repairable/rejected yields and auditor-token spans per lane
  - Sanitized summary split into `quality_validated_candidate` / `protocol_accepted_candidate`
    / `economics_usable` (per P60 outcome semantics)
  - Execution packet scaffolded in `planning/phase96_p963_execution_packet.md`
    with concrete manifest `benchmarks/document_library/tsa23_tsr/p96_model_lane_comparison_manifest.json`.
  - SDK model-list probe implemented via local `~/projects/copilot-sdk` clone;
    current blocker captured in `runtime/agent_jobs/p96_3_model_inventory_snapshot.md`
    (`Internal Windows PowerShell error ... 8009001d` during CLI start).
  - Direct VS Code wrapper probe also blocked in this shell context:
    `Cannot find GitHub Copilot CLI ... Install GitHub Copilot CLI? (y/N)`.
  - Use `templates/p96_model_inventory_capture.md` to capture provider-picker
    model evidence when proceeding via VS Code UI path.
  - Explicit model probes attempted for both lanes via
    `scripts/copilot_sdk_ollama_probe.py`; blocked before model-call events with
    `OSError: [WinError 193] %1 is not a valid Win32 application`.
    Sanitized execution summary: `benchmarks/document_library/tsa23_tsr/p96_model_lane_comparison_execution_summary.json`.
- [x] P96.4 Render verdict: same-lane recommendation, switch, or insufficient evidence (#589)
  - With explicit boundary warnings
  - Verdict rendered in `planning/phase96_verdict.md` as `insufficient_evidence`.
  - Diagnostic-only closeout: no broad scale-up authorization.

## Phase 97: Reusable Workflow Graph Packaging

Parent issue: #592
Child issues: #593 closed, #594 closed, #595 closed

Branch: `feature/p97-reusable-workflow-graphs`

Status: **complete** — merged via PR #596 at `b2b929f`; parent issue #592 closed.

Goal: package repeatable workflow graph templates for successful Agent
Workbench real-project workflows.

Key Advisor insight (2026-07-11):
- P39 already produced reusable workbench graph templates and P43 produced
  FreshForge-compatible proposal-assist graphs. Clarify whether P97 produces
  **new** artifact families or **promotes existing TSA23-derived templates**
  into the `workbench_templates/` namespace. If it's promotion, scope should
  reflect that — changing both task decomposition and verification.

Outcome: P97 chose the promotion path. Audited 10 existing graph templates,
retired 4 non-applicable ones, promoted 4 (renamed with `workbench_` prefix
and updated JSON), and kept 2 as FreshForge-specific examples. The canonical
`document_library_index_workflow.json` captures the P88-P94 document-indexing
recipe. Merged through PR #596.

Tasks:
- [x] P97.1 Audit existing graph templates for reuse (#593)
  - Templates audited: P39 `agentic_graph_envelope.json`, P43
    `freshforge_proposal_assist_graph.json`, P92 `whole_document_graph_template`,
    and 7 additional historical graphs from P61/P88/P90
  - Outcome: promote=4, retire=2, keep-as-example=2, not-in-scope=4
  - Promoted templates renamed with `workbench_` prefix in `templates/workbench_templates/`
- [x] P97.2 Create canonical `document_library_index_workflow.json` (#594)
  - Renamed from `document_library_index_graph.json` (internal
    `workflow.id` already had target name); git detected 100% rename
  - Under `templates/workbench_templates/`; captures the P88-P94 recipe as a
    FreshForge-compatible graph; JSON validated against existing graph validation;
    public-safety scan passed
- [x] P97.3 Write minimal instantiation guide (#595)
  - Updated `templates/workbench_templates/README.md` with full classification table,
    detailed descriptions of each promoted template's role, and a future requirements
    section documenting JSON Schema validation as a P98+ item
  - All references updated from old filename to new: README, test suite, manifest
    template, benchmark plan JSON
  - pytest suite passes (4/4)

Closeout note: P97 merged through PR #596 at `b2b929f`, and parent issue #592
closed on merge.

## Phase 98: Reporting-Worker Template Packaging

Parent issue: #599 (create on activation)

Branch: `feature/p98-reporting-worker-templates`

Status: complete — all tasks done; PR merged 2026-07-12.

Goal: package reporting-worker templates and supervisor decision packets that
proved useful in P91/P92.

Coordination directive (2026-07-12): the free gpt-oss:120b Coordinator session
may finish its current P98 pass. Do NOT run a second Coordinator on this branch
concurrently. Its output stays untrusted until verified. The upgraded paid
Coordinator (`gpt-5.4-mini`, thin-router contract) does mop-up as P98.4 below
after the gpt-oss pass checkpoints — verify-and-closeout, do not race it.

- [x] P98.4 Upgraded-Coordinator audit, review, and closeout (mop-up)
  - Verify P98.1-P98.3 artifacts exist and are public-safe with deterministic
    checks and validators (no re-reasoning, no raw-artifact reads).
  - Reconcile ROADMAP.md / CHANGE_LOG.md / issue #599 / PR state.
  - Run one Advisor pre-closeout review, then present a compact closeout packet
    to the developer for merge approval. Do not merge or close #599 without it.

Tasks:
 - [x] P98.1 Audit existing reporting artifacts for reuse (#599)
   - Artifacts to audit: P91 source-audit decision packet, P73 overlay catalog,
     P70-Ticket-C worker result templates
   - Document scope boundaries and reusable vs. TSA23-specific structures
 - [x] P98.2 Create `source_audit_decision_packet.md` template (#599)
   - Derived from the P91 structure — generic enough for non-document-indexing use
     but informed by TSA23 lessons; validated against P91's tracked artifacts;
     source-anchor rules generalized
 - [x] P98.3 Capture one supervisor decision packet pattern as reusable template (#599)
   - The compact ROI decision: accept seed / repair / switch lane / stop
   - Template with declared fields and validation semantics
 - [x] P98.4 Audit, review, and closeout — upgraded Coordinator (#599)
   - Runs AFTER the gpt-oss:120b Coordinator checkpoints its current pass; no
     two Coordinators on the `feature/p98-reporting-worker-templates` branch at
     once.
   - Verify P98.1-P98.3 against tracked artifacts and `git diff`; treat the
     local Coordinator's prose as untrusted until evidence-checked.
   - Reconcile the P98 checklist and finish/verify P98.1.
   - Run validation gates: `ruff format src tests`, `ruff check src tests`,
     `mypy src`, `pytest tests -q`, `pre-commit run --all-files`,
     `git diff --check`.
   - Coordinator-owned closeout (nondelegable): confirm/create parent issue
     #599, open PR, merge, close issue, sync `main`.

Coordinator upgrade note (2026-07-12): the paid Coordinator role moves off the
free gpt-oss:120b lane to `Claude Sonnet 4.8 (copilot)` (confirm exact label in
the model picker), with `gpt-5.4-mini` at low reasoning as the cheaper verified
fallback. The Coordinator delegates maximum work to the free gpt-oss:120b
Supervisor, which drives free Ollama Worker sessions through the SDK bridge
(option b). Coordinator contract: delegate-don't-do, compact-packets-only,
run-validators-don't-reason, fresh session per task.

## Phase 99: Economics Dashboard And Release Criteria

Parent issue: #601

Branch: `feature/p99-economics-dashboard-release-criteria`

Status: complete — merged via PR #602; parent issue #601 closed.

Goal: make task economics, governance overhead, and release-readiness criteria
visible enough for public-alpha decisions.

Key Advisor insight (2026-07-11):
- The ROI thesis target is "reduce paid supervisor cost per useful, source-backed
  unit of real project work." P99 should include this as an **indexed-cost metric**
  (not just task-level accounting): paid-supervisor tokens per promoted record,
  broken into extraction, repair-prepass, audit, and index-assembly stages.

Tasks:
- [x] P99.1 Define indexed-cost metric specification (#601)
  - Paid-supervisor tokens per promoted record by stage; wire to existing `accounting`
    and `tokens` commands (from P35/P40); calculation formula documented
- [x] P99.2 Implement dashboard surface: `agent-workbench economics render` (#601)
  - Reads pilot-accounting records, token-cost records, and index metadata; produces
    a Markdown table with per-corpus and aggregate indexed-cost values
  - Dogfood on P90-P94 accounting data for verification
- [x] P99.3 Define release-readiness criteria for public alpha (#601)
  - Minimum indexed cost target, provenance completeness threshold, governance-surface
    checklist (AGENTS.md compliance, public-safety scan)
  - Criteria document with pass/fail semantics; checked against current state

## Phase 100: Public Alpha Readiness Review

Parent issue: #603

Branch: `feature/p100-public-alpha-readiness-review`

Status: complete (qualified) — merged via PR #610; parent issue #605 closed.

Goal: prepare a public alpha only after one end-to-end real-project workflow
shows net value.

Tasks:
- [x] P100.1 Compile readiness checklist (#603)
  - All tracked artifacts public-safe, all templates validated, ROI thesis statement
    coherent, indexed-cost metric reported, AGENTS.md governance rules current
  - `planning/public_alpha_readiness_checklist.md` — PASS WITH NOTED LIMITATIONS
- [x] P100.2 Produce `public_alpha_readiness_review.md` note (#603)
  - Declares workbench current state: what is ready, what is experimental, what is not production-ready
  - `planning/public_alpha_readiness_review.md` — confidence MEDIUM-HIGH; open questions for reviewers documented

## Phase 102: Native Codex + Remote Ollama Orchestration

Parent issue: #605

Branch: `feature/p102-native-codex-ollama-orchestration`

Status: complete (qualified) — merged via PR #610; parent issue #605 closed.

Goal: make native Codex the primary Coordinator host while using an
operator-configured OpenAI-compatible Ollama provider for default Supervisor
and Worker roles.

Scope:

- Define generic native-Codex role profiles and a local-only provider bootstrap
  boundary without tracking endpoint or credential values.
- Add deterministic configuration and evidence-contract validation.
- Prove one bounded Coordinator -> Supervisor -> Worker vertical slice with
  persisted evidence of both delegation edges.
- Record separate quality, protocol, and economics verdicts before deciding on
  a substantive native-hierarchy TSA23 job.

Out of scope:

- Broad TSA23 extraction before the vertical slice is accepted.
- Deleting or replacing the Copilot SDK interoperability path.
- Publishing provider endpoints, credentials, raw sessions, or local model
  inventory.

Tasks:

- [x] P102.1 Native architecture and public-safe profiles (#606)
  - Define Coordinator, Supervisor, and Worker role boundaries.
  - Add generic project role profiles; keep provider configuration machine-local.
- [x] P102.2 Native configuration and evidence contracts (#607)
  - Implement fail-closed role/configuration and proof-artifact validation.
- [x] P102.3 Bounded native delegation proof (#608) — qualified no-modal Supervisor-authored ticket -> Worker -> Supervisor verification proof accepted
  - Run one trivial two-edge proof with one evidence-based repair at most.
  - Keep app-server completion stalls explicit; the Coordinator remains the
    transport/sequence owner for the Supervisor-authored ticket handoff.
- [x] P102.4 Native proof decision packet (#609) — decision recorded: do not authorize substantive TSA23 work
  - Inspect proof evidence, record distinct verdicts, and decide whether a
    substantive native-hierarchy job is authorized.
  - Do not authorize substantive TSA23 work until a Supervisor-owned dispatch
    path reaches the persistent Worker host with observed evidence.

## Phase 103: Paid Coordinator Economics Trial

Parent issue: #611

Branch: `feature/p103-paid-coordinator-economics-trial`

Status: complete (qualified) — bounded run accepted; economics backfilled from Codex session accounting.

Goal: measure one bounded non-trivial Supervisor-authored Worker handoff with
paid Coordinator token-span accounting before authorizing substantive TSA23
delegation.

Scope:

- Record the paid Coordinator token-span start and end metadata.
- Run one structured ignored-runtime ticket through the accepted P102 hybrid
  Supervisor-authored handoff and persistent Worker host.
- Independently verify the Worker result and return separate quality, protocol,
  and economics verdicts.

Out of scope:

- TSA23 source extraction or substantive project work.
- Provider, header, or model-inventory changes.
- Nested `codex exec` Worker launches.
- Tracked-file Worker mutation, release actions, or phase closeout.

Tasks:

- [x] P103.1 Bounded structured handoff run (#612)
  - [x] Capture Coordinator token-span start/end metadata and selected model.
  - [x] Have the Supervisor author one structured Worker ticket under
        `runtime/agent_jobs/`.
  - [x] Execute the persistent Worker and capture exact result evidence.
  - [x] Verify the result in a fresh Supervisor turn.
  - [x] Stop after one run and at most one evidence-based repair.
  - [x] Record separate quality, protocol, and economics verdicts.

Closeout decision: quality PASS; protocol PASS, qualified; economics PASS,
qualified for actual paid Coordinator cost. The backfilled span records 1,922
fresh input tokens, 110,218 cached input tokens, 629 output tokens, 186
  reasoning tokens, and approximately `$0.017834` Coordinator cost using GPT-5.6
  Luna pricing. No direct-supervisor
  counterfactual was captured, so this is not an ROI/savings claim and no
  substantive TSA23 authorization follows from this trial.

Next-step plan:

- [ ] Establish a dated model-price catalog for future economics records.
- [ ] Design one separately authorized counterfactual benchmark with matching
      task, model, and token-span checkpoints.
- [ ] Compare delegated actual cost with direct-supervisor cost before making
      any savings or ROI claim.

Acceptance criteria:

- The ticket, Worker result, Supervisor dispatch/verification evidence, and
  token ledger are persisted under ignored runtime paths.
- No substantive TSA23 work, provider change, release action, or nested
  `codex exec` launch occurs.
- The decision packet distinguishes quality validation, protocol acceptance, and
  economics usability.

## Phase 104: Canonical Model Pricing And Economics Provenance

Parent issue: #614

Branch: `feature/p104-model-pricing-provenance`

Status: complete — corrective validation gates merged via PR #628; P106 remains
unactivated.

Goal: replace conflicting hard-coded model prices with a dated, validated
catalog and make economics claims carry explicit model and pricing provenance.

Tasks:

- [x] P104.1 Canonical price catalog and resolver (#615)
  - [x] Add dated GPT-5.6 Sol, Terra, and Luna input, cached-read, cache-write,
        output, and long-context pricing.
  - [x] Add fail-closed catalog validation and effective-date resolution.
- [x] P104.2 Pricing CLI and supervisor-token integration (#616)
  - [x] Add `agent-workbench pricing validate` and `pricing resolve`.
  - [x] Add model/catalog/as-of options to `supervisor-tokens span`.
  - [x] Keep legacy token records readable while rejecting unproven economics
        claims from legacy defaults.
- [x] P104.3 Token provenance and bounded-cost semantics (#617)
  - [x] Record price source, effective date, model ID, cache-write observability,
        long-context status, and lower/upper cost bounds.
  - [x] Reprice P103 as a qualified bounded estimate.
- [x] P104.4 Validation and closeout (#618)
  - [x] Test catalog resolution, unknown models, effective dates, cache pricing,
        long-context multipliers, and legacy compatibility.
  - [x] Run scoped validation and synchronize governance surfaces.

P104 performs no live model call, provider change, TSA23 extraction, or release.

## Phase 105: Matched Public-Corpus Benchmark Contract

Parent issue: #621

Branch: `feature/p105-matched-public-corpus-contract`

Status: complete.

Goal: materialize a deterministic, dry-run-only matched benchmark contract over
`tsa23_2012_23tsdp12::pages_001_008` before spending paid or remote-worker
tokens.

Tasks:

- [x] P105.1 Immutable source/task fixture (#622)
  - [x] Pin the existing source chunk hash and P89 record schema.
  - [x] Require 8-12 records with at least three structure and three
        content-metadata records.
- [x] P105.2 Lane-symmetry contract (#623)
  - [x] Give direct and delegated lanes the same source bundle, schema, repair
        allowance, audit rules, and scoring.
  - [x] Declare GPT-5.6 Luna direct/Coordinator, `qwen3-coder:latest`
        Supervisor, and `qwen3.6:35b-a3b-bf16` Worker identities.
- [x] P105.3 Hybrid-runner model separation (#624)
  - [x] Add separate Supervisor and Worker model arguments.
  - [x] Persist exact-model evidence without changing provider configuration.
- [x] P105.4 Dry-run validation (#625)
  - [x] Validate fixture hashes, manifests, stop rules, and output contracts.
- [x] P105.5 Advisor corrective validation gates (#627)
  - [x] Validate every pinned source/P89 artifact hash and source semantics.
  - [x] Validate stop rules, output contract, role identities, and model-argument
        contract exactly.
  - [x] Add tampering and missing-artifact negative tests.
  - [x] Reopen/close the corrective issue after the repair PR was merged.

P105 permits no live inference.

## Phase 106: Matched Direct-Vs-Delegated Execution

Parent issue: #629

Branch: `feature/p106-matched-roi-benchmark`

Status: complete (qualified) — quality validated; protocol and economics not
accepted. P111 and its non-counting Agent Hub shadow do not alter the matched
benchmark contract.

Goal: measure quality and paid cost for the P105 task through delegated and
direct GPT-5.6 Luna lanes.

Tasks:

- [x] P106.1 Budget and checkpoint gate (#630)
  - [x] Set a `$0.25` total paid cap and `$0.125` delegated-lane stop threshold.
  - [x] Require catalog-backed pricing and exact-model evidence.
- [x] P106.2 Delegated lane (#631)
  - [x] Run one attempt and at most one evidence-based repair.
  - [x] Audit every emitted record; require at least 90% useful yield and no
        critical source-anchor defect before the direct lane.
  - [x] Stop after the native attempt and one repair failed protocol and token
        boundaries; do not spend a third attempt.
- [x] P106.3 Direct lane (#632)
  - [x] Run the identical source/schema task directly with GPT-5.6 Luna.
  - [x] Apply the same audit and quality rules; strict structured output passed.
  - [x] Record the ordering defect instead of rerunning after the attempt cap.
- [x] P106.4 Sanitized comparison packet (#633)
  - [x] Record quality, protocol, latency, token classes, and bounded known cost.
  - [x] Keep raw source text, prompts, transcripts, and outputs ignored.

Observed quality evidence (ignored runtime, 2026-07-13): the strict direct
Luna lane produced 11 valid records with 100% useful yield and zero critical
anchor defects. The delegated Worker produced 8 valid records after one
evidence-based quote repair; the Supervisor independently verified the
repaired output, which also reached 100% useful yield and zero anchor defects.
The sanitized packet preserves `quality_validated_candidate: true` while
recording `protocol_accepted_candidate: false` and `economics_usable: false`.
The known direct bounded cost is `$0.020963`; the delegated and total paid costs
remain unknown because the required Coordinator span boundary was not captured.
P106 stops rather than authorizing a third delegated attempt. See
`planning/phase106_matched_execution_result.md`.

## Phase 107: Economics Decision And Delegation Policy

Parent issue: #644

Branch: `feature/p107-delegation-economics-policy`

Status: complete as a bounded exploration tranche. P107 established the usable
native control-layer route and recorded accepted C0, C1, supervised C2, and C4+
observations, while retaining failed/invalid lanes as evidence. Its evolving
workloads, topologies, and provider configurations mean it does not yield a
single final cross-epoch ROI ranking. P108 remains inactive. The next
development direction is the separately planned P118 single-provider vLLM
deployment, not another P107 model sweep.

Goal: convert P106 evidence into a fail-closed economics decision.

Mission guardrail: P107 measures whether a native Agent Hub configuration can
do useful ordinary development work. Frozen deterministic checks judge the
artifact, not whether an LLM behaved deterministically. After a run, preserve
quality variance as evidence; do not change the workload or externally repair
the candidate to manufacture an accepted outcome. Repair only a demonstrated
control-layer observation/boundary/accounting defect, record it separately as
protocol evidence, and freeze a new block if it changes the comparison.

Parking decision: P113 closed the bounded one-tool adapter, containment, and
first-call reliability sandbox. The later C4 observations did not deploy that
route and therefore cannot support a model-quality or economics comparison.
P114 now owns the broader, preregistered C4 capability-parity and viability
decision. This is not a P107 pass, closure, or authorization for P108.

Tasks:

- [x] P107.1 Record protocol and quality re-entry evidence
  - [x] Encode `gpt_luna_supervisor` as the accepted recursive Supervisor and
        reject `ollama_supervisor` for child-spawning work pending new evidence.
  - [x] Preserve historical quality evidence without using it as a fresh C4
        baseline.
  - [x] Record the effective-configuration and tool-route gaps as blockers.
- [x] P107.2 Research contract and offline replay (#646)
  - [x] Freeze the provenance-audit bundle workload, rubric, configuration,
        packet, review, accounting, observation, and comparison contracts.
  - [x] Implement fail-closed materialized-run, topology, session, Advisor,
        accounting, replay, and comparison validation with synthetic replay.
  - [x] Implement and freeze the deterministic provenance-audit workload and
        its batch acceptance fixture.
  - [x] Verify the P107 selection offline: 150 passed, 2 privilege-dependent
        skips; no live C0-C4 run and no economics conclusion.
- [x] P107.3 C0 BAU baseline (#647)
  - [x] Capture non-comparative C0 instrumentation evidence for root binding,
        immutable review, and session-bound accounting on a microtask.
  - [x] Build the five-slice `p107-run-evidence-dossier-v3` local quality
        candidate: integrity-checked typed artifacts, schema validation,
        reconciliation, timeline/anomaly analysis, and deterministic CLI
        rendering/validation.
  - [x] Add the public-safe V3 dossier fixture and reach the planned `100`
        focused passing dossier cases (plus one platform-dependent skip).
  - [x] Freeze and validate the local pre-C0 V3 block: ticket, fixture,
        reset-consistent prompts, model/pricing catalogs, effective Terra
        configuration snapshot, and Advisor rubric are hash-bound to the clean
        pre-implementation baseline.
  - [x] Run one fresh native C0 observation against the frozen V3 block; keep
        its submitted task quality as an observation rather than externally
        repairing it into baseline acceptance.
  - [x] Align active run-evidence, accounting, and comparison validators to the
        reset-consistent C0-C4 ladder; remove mandatory Advisor/Supervisor
        roles and permit the normal submitted implementation diff.
  - [x] Record frozen-workload quality acceptance, native protocol acceptance,
        and complete paid-role accounting for eligible C0 r3; Sol remained
        selective rather than routine.
- [x] P107.4-P107.7 C1-C4 configuration observations (#655, #656, #657, #658)
  - [x] Record the unsupervised C1 Terra-to-Luna Worker baseline observation:
        accepted artifact/protocol/economics under its former topology,
        `$1.2145648` paid cost, and 42.0% lower paid cost than C0; it does not
        establish the canonical supervised route.
  - [x] Record the unsupervised C2 Terra-to-configured-Ollama Worker baseline:
        Worker incomplete with no final result; retain as failed quality
        evidence with no external repair or economics comparison.
  - [x] Run C2 r7 under the unchanged V3 workload with Coordinator-owned P116
        supervision active before Worker tools; quality and protocol accepted,
        with outer-controller paid-Coordinator estimate `$0.413974` and
        separate local-Qwen usage capture.
  - [x] Stop the unfinished C3/C1-rerun/C5 sequence rather than blend its
        changed workload, topology, and provider conditions into a false ROI
        conclusion; P118 owns the fresh single-provider deployment boundary.
- [x] P107.8 Tranche synthesis (#659)
  - [x] Record accepted and failed observations separately, close without a
        cross-epoch winner, and defer any new sequence to P118.

Entry evidence: P106 closed with quality validated but protocol and economics
unaccepted. P113 proved a constrained one-tool adapter sandbox but did not
prove the C4 Worker can exercise the complete tool/session contract used by the
paid C2 comparator. See `planning/phase107_c4_capability_parity_pause.md`.
P114 has resolved the baseline route validity prerequisite. See
`planning/p107_c4_package_route_reentry_packet.md`; P107 workload quality and
economics remain separate gates.

Closeout decision: P107's accepted C0/C1/C2/C4+ observations demonstrate that
the native Agent Hub and Coordinator-owned P116 control layer can support real
bounded work. They are not normalized into one winner because workload,
topology, and provider conditions changed across the exploration. The recorded
economic facts remain usable at their own boundaries: C0 `$2.0937575`, C1
`$1.2145648`, supervised C2 `$0.413974` paid Coordinator estimate, and the
accepted Qwen 3.6 C4+ lane `$0.231600` paid Coordinator estimate. Local-worker
usage remains separate. Further deployment work moves to P118 with one declared
provider/model and a fresh stable workload boundary.

## Phase 108: Fresh TSA23 Slice Preparation

Parent issue: TBD

Branch: `feature/p108-fresh-tsa23-slice-prep`

Status: planned - activate only after a passing P107 decision and an accepted
P113 Worker-editability decision.

Goal: prepare pages 1-8 of `tsa23_2006_23ts06ra` as a fresh, bounded,
public-corpus slice without live inference.

Tasks:

- [ ] P108.1 Record source URL, hash, and provenance.
- [ ] P108.2 Materialize an ignored raw-text slice and tracked chunk manifest.
- [ ] P108.3 Reuse P89 validation, P91 audit, and P107 economics contracts.
- [ ] P108.4 Validate a one-run/one-repair `$0.125` P109 budget gate.

## Phase 109: Productive Delegated TSA23 Pilot

Parent issue: TBD

Branch: `feature/p109-productive-tsa23-pilot`

Status: planned — requires explicit live-run activation after P108 closeout.

Goal: produce and audit one useful fresh-corpus result under the measured P107
policy.

Tasks:

- [ ] P109.1 Run one delegated extraction with at most one evidence-based repair.
- [ ] P109.2 Audit every candidate and promote accepted records only.
- [ ] P109.3 Require at least 90% useful yield, zero critical defects, protocol
      acceptance, catalog-backed economics, and cost within the P107 threshold.
- [ ] P109.4 Stop without promotion or scope expansion when any gate fails.

## Phase 110: Alpha Readiness Refresh And GitHub Pre-Release

Parent issue: TBD

Branch: `feature/p110-public-alpha-prerelease`

Status: planned — release action requires passing P107 and P109 decisions.

Goal: make one explicit release/no-go decision and, only on passing evidence,
publish the first GitHub public-alpha pre-release.

Tasks:

- [ ] P110.1 Refresh stale roadmap, docs, and economics claims.
- [ ] P110.2 Run public-safety, CLI, package, docs, and full validation gates.
- [ ] P110.3 Produce separate quality, protocol, and economics release verdicts.
- [ ] P110.4 If all gates pass, merge normally and publish GitHub pre-release
      `v0.1.0a1`; otherwise publish a no-go packet.

P110 does not publish to PyPI.

## Phase 111: Native Recursive Codex UI Delegation

Parent issue: #634

Branch: `feature/p111-native-recursive-ui-delegation`

Status: complete — PR #639 merged; parent issue #634 and child issues #635-#638 closed.

Goal: productize the accepted usable-adjacent proof that a native Codex UI
Coordinator can spawn a configured Luna Supervisor, which can spawn and expose
an interactive configured remote-Ollama Worker at depth 2.

Parallel-lane boundary: the maintainer explicitly authorized P111 alongside
the still-active P106 benchmark. P111 does not alter or satisfy P106/P107
quality, ordering, token-span, or economics gates.

Tasks:

- [x] P111.1 Role-aware v1 configuration contract (#635)
  - [x] Preserve the historical generic `gpt-5.6`/`high` proof and productize
        Terra/Medium through a machine-local version-pinned v1 catalog.
  - [x] Validate machine-local named roles and environment-backed headers.
  - [x] Reject UI-root configuration drift fail-closed.
- [x] P111.2 Recursive role-provenance evidence (#636)
  - [x] Freeze raw rollout copies and hashes in ignored runtime storage.
  - [x] Validate role, provider, model, reasoning, depth, and parentage.
  - [x] Reject v2 generic children, model overrides, and inherited-history spawns.
- [x] P111.3 Interactive UI operator workflow (#637)
  - [x] Document Coordinator -> Supervisor -> Worker UI navigation.
  - [x] Preserve multi-turn Worker and remote-GPU corroboration evidence.
  - [x] Document failure signatures, recovery, cleanup, and privacy boundaries.
- [x] P111.4 Validation, documentation, and closeout (#638)
  - [x] Synchronize roadmap, changelog, planning, issues, and PR state.
  - [x] Run focused tests, config validation, diff checks, and privacy scans.
  - [x] Open the phase PR without merging or closing the parent before approval.

Acceptance criteria:

- The phase branch starts from current `origin/main` and excludes P106-only
  history.
- Deterministic evidence accepts the exact recursive role-bound chain and
  interactive Worker persistence.
- Raw provider/session material remains ignored and tracked docs stay public-safe.
- Quality, protocol/usability, and economics conclusions remain separate.

## Phase 113: Codex-Ollama Function-Tool Adapter Sandbox

Parent issue: #648

Branch: `feature/p113-codex-ollama-function-tool-adapter`

Status: complete - PR #652 merged implementation and PR #653 merged closeout
reconciliation; parent issue #648 closed. Adapter quality, protocol, and
bounded Worker reliability are accepted; P107 remains parked pending a separate
resume decision.

Goal: design and implement a narrow local adapter that enables a configured
Ollama-backed native Codex Worker to use the native `apply_patch` handler via a
standard Responses function call, then determine whether it is reliable enough
to unblock P107.

Boundary: P113 is a local adapter sandbox. It does not generalize Code Mode,
MCP, or arbitrary Responses tools; it does not run P107 economics work or
authorize P108.

Tasks:

- [x] P113.1 Adapter contract and threat model (#649)
  - [x] Specify the one-tool request and stream-translation contract.
  - [x] Define allowed roots, one-call limits, failure behavior, and evidence
        boundaries.
  - [x] Define quality, protocol, and economics acceptance separately.
- [x] P113.2 Narrow adapter implementation and deterministic checks (#650)
  - [x] Implement only `apply_patch(patch: string)` translation.
  - [x] Fail closed on malformed calls, outside-root paths, and excess calls.
  - [x] Add focused deterministic translation and containment tests.
- [x] P113.3 Native-worker reliability evidence and decision (#651)
  - [x] Run fresh bounded native Worker trials on ignored targets.
  - [x] Require one valid call containing two required edits and normal follow-up
        completion.
  - [x] Record the resume/P107 decision without activating P108.

Acceptance criteria:

- A configured Ollama Worker completes a constrained native patch task without
  shell-writing fallback.
- The adapter rejects malformed, out-of-scope, and excess patch behavior before
  mutation.
- Raw runtime evidence proves model/provider, standard function call,
  translated custom call, native patch result, final diff, and terminal status.
- The final decision distinguishes quality, protocol, and economics outcomes.

P113.3 decision: five distinct fresh `qwen3-coder:latest` sessions each made
one native `apply_patch` call, changed both ignored targets, and returned the
terminal marker. Deterministic containment, call-limit, malformed-output, and
history fixtures pass; no counted adapter verdict was rejected. This accepts
`quality_validated_candidate`, `protocol_accepted_candidate`, and bounded
Worker reliability as P113 evidence. `economics_usable` remains out of scope;
P107 stays parked pending a separate resume decision and P108 is not activated.

## Phase 114: Codex-Ollama C4 Capability Parity And Viability

Parent issue: #661

Branch: `feature/p114-host-proof-repair` (merged through PR #667)

Status: complete. PR #667 merged and parent issue #661 closed on 2026-07-18.
The locked v1 direct data-plane adapter, role-bound C4 package route, fresh
capability battery, and baseline C4 protocol qualification are complete. This
is a new phase; it is not the earlier supplementary P114 reliability label that
was reconciled into P113.3.

Goal: establish, before further P107 comparison runs, whether the configured
Codex/Ollama route can satisfy the preregistered capability contract required
by the C4 workload and its C2 comparator. A capability failure is an invalid
treatment observation, not a model-quality loss.

Parallel-lane boundary: the maintainer authorized P114 while P107 remains
parked. P114 does not resume P107, authorize P108, or make an economics claim.

Tasks:

- [x] P114.1 Capability-parity preregistration
  - [x] Freeze the workload, C2/C4 tool contract, topology, role profiles,
        model catalogs, invalid-observation rules, costs, and stop rules before
        live Ollama outcomes are observed.
  - [x] Define the minimum required interface rather than claiming parity with
        every possible Codex feature.
- [x] P114.2 Offline bridge conformance
  - [x] Validate the declared read, patch, shell, history, repair, containment,
        and unsupported-tool behaviors from clean processes.
  - [x] Fail closed when a required capability lacks deterministic evidence.
- [x] P114.3 Codex host/runtime deployment proof
  - [x] Prove the direct-MWE route's run-scoped configuration, literal
        worktree binding, provider/catalog configuration, adapter teardown, and
        restored normal configuration (`p114_core_adapter_deployment_proof_r15`
        and the later fresh composites).
  - [x] Prove fresh-session binding to the frozen
        `ollama_qwen_coder_worker` C4 role and persist effective role/session
        identity. Fresh runs `p114_c4_role_binding_r3` and r5 proved identity
        and real-upstream role binding, but each child exposed only `exec` and
        the required `apply_patch` returned unsupported. In r5 the child then
        made a prohibited `Set-Content` shell write plus a fifth read; the
        target changed despite two adapter `undeclared_exec` rejections. Repair
        host-plane tool-schema registration and undeclared-write containment
        before any separately authorized fresh proof. The deterministic repair
        is implemented and tested, including a run-scoped temporary provider
        name, but r6 inherited r5's stopped adapter endpoint from the existing
        parent session before making any request. R7 then proved that a
        run-scoped bridge must be enabled before, rather than inside, a new
        parent session. R8 used that ordering and reached the repaired bridge,
        but the host still registered only `shell_command`: its exact native
        `apply_patch` returned unsupported and the target remained `before`.
        R9 then ruled out the profile-permission theory: its child still
        rejected the native patch after the temporary profile change. Compare
        direct-runner and multi-agent code-mode-host patch registration before
        another Worker proof. CLI-parent controls r10/r11 did create one native
        child each, but r11's literal ticket still failed before its first
        adapter event with an upstream stream disconnection; do not treat CLI
        parenting as a host-route repair. Superseded for the corrected
        Cloudflare-authenticated CLI parent: `p114_c4_cli_parent_r15` loaded
        the documented provider-header file before launch, then one frozen
        Worker with `fork_context:false` completed the exact
        `exec -> native apply_patch -> exec` sequence and
        `P114_C4_ROLE_DONE`. Its target is `after`; raw child
        `019f7252-32fc-70d2-b804-9d614386fe45` and the adapter record the
        accepted sequence. This is a CLI-parent route result only. Fresh Luna
        evidence showed the VS Code child mutates through `exec` calling
        `tools.apply_patch(...)`, not a top-level patch event. The Qwen
        adapter's patch-via-exec repair was attempted in fresh run
        `p114_c4_role_binding_r10_exec_wrapper`, but the VS Code host rejected
        the wrapper as `unsupported custom tool call: exec`; the target stayed
        `before`, later adapter activity included rejected `undeclared_exec`,
        and no `P114_C4_ROLE_DONE` marker occurred. The r10 bridge was
        disabled after inspection. P114.3 remains open for the intended VS
        Code-parent route; this is not a quality, protocol, or economics
        result. Before another patch Worker, run the new no-mutation
        `-HostToolInventory` preflight from a fresh parent. It must record
        executor-local `ALL_TOOLS` containing both `shell_command` and
        `apply_patch` plus `P114_C4_HOST_TOOL_INVENTORY_DONE`; otherwise stop
        and restore the bridge without a patch attempt. Fresh r11
        (`p114_c4_role_binding_r11_host_inventory`) is invalid: the Coordinator
        sent the ticket filename instead of its verbatim contents, so the child
        never received the inventory instruction. Its disconnected stream and
        repeated adapter `undeclared_exec` verdicts are not a VS Code host
        result. The bridge was torn down; r11 is excluded from all P114.3
        quality, protocol, and economics evidence. Repeat the preflight only
        from a fresh parent with the generated ticket text as the Worker
        message. R12 corrected that handoff and reached one inert custom
        `exec`; the VS Code host returned `unsupported custom tool call: exec`.
        No shell, file, or patch call occurred and the target remained
        `before`. This is valid negative host-dispatch evidence: do not launch
        another UI patch Worker until generic custom-executor registration is
        repaired. A fresh VS Code app-server observation then recorded
        `dynamicTools: null`. The documented app-server mechanism does support
        dynamic tool registration, so this identifies the installed extension's
        omission of that mechanism, not a Codex limitation. The deterministic
        installed-executable probe also reported `host_registration_gap`:
        direct `codex.exe` contains native patch/custom-dispatch markers while
        sibling `codex-code-mode-host.exe` contains none. This is a bounded VS
        Code integration diagnosis, not a complete tool inventory or a precise
        component attribution. Keep productive C4 work on the accepted
        CLI-parent route; do not repeat UI Workers until the extension supplies
        dynamic tools and handles client-executed calls.
  - [x] Prove the VS Code parent can register and handle a no-mutation
        `p114_exec` dynamic tool: fresh threads carried the tool, one
        `item/tool/call` reached the client handler, and it returned
        `P114_DYNAMIC_EXEC_HANDLER_REACHED`. This is parent-only evidence;
        Worker inheritance and command authority remain unproven.
  - [x] Run one fresh no-mutation Worker inheritance check
        (`p114_c4_role_binding_r13_dynamic_exec_inheritance`). The child emitted
        `p114_exec`, but its nested host returned `unsupported call: p114_exec`
        and no parent dynamic-tool handler ran. The target stayed `before` with
        no shell, patch, file, or extra host call. Dynamic registration reaches
        the parent and Worker model surface but is not routed through the
        current multi-agent host; do not repeat this Worker probe without a
        nested-host routing repair.
  - [x] Accept the fresh CLI-parent package-MCP route for the bounded
        `exec`, `apply_patch`, and read-to-patch-to-validate composite. The
        accepted package route supersedes the earlier r1 registration failure
        as the P107 entry candidate; the VS Code nested-host custom-tool route
        remains retained negative integration evidence and is not required for
        P107 entry.
- [x] P114.4 Fresh live capability battery
  - [x] Run the locked direct-MWE composite in three independent fresh Qwen
        sessions: `p114_core_adapter_envelope_r20`,
        `p114_core_adapter_battery_r21`, and
        `p114_core_adapter_battery_r22`.
  - [x] Require and independently verify native patching, declared shell/test
        behavior, preserved continuation history, artifact flow, and root
        containment in all three direct-MWE runs.
  - [x] Repeat the battery through the frozen role-bound C4 Worker route after
        P114.3's role-binding proof. Three fresh Cloudflare-authenticated
        CLI-parent rows (`p114_c4_capability_battery_r23` through r25) passed
        the declared five-call sequence, two native patches, exit codes
        `0, 17, 0`, final `after`, and `P114_C4_BATTERY_DONE`. This
        establishes historical CLI-parent evidence only. The P107 entry route
        now requires a new three-row package-MCP battery from the frozen
        admission manifest; VS Code nested-host parity is not a P107 gate.
  - [x] Freeze and execute the three-row package-MCP admission battery:
        `p114_package_mcp_battery_r3`, r4, and r5 each passed
        `verify_p114_package_mcp_battery.py` against its raw child session.
        Every row used exactly deferred discovery plus namespaced
        `exec -> apply_patch -> exec -> apply_patch -> exec`, recorded only
        allow decisions, returned exec codes `0, 17, 0`, finished with exact
        `after\n`, and restored live config plus Worker role byte-for-byte.
- [x] P114.5 C4 qualification and viability decision
  - [x] Implement and test the task-specific package grant profile required by
        the frozen `p107-provenance-audit-bundle-v1` workload. Do not reuse the
        exact-command/pre-hashed-patch P114.4 battery grant as a fake coding
        qualification.
  - [x] Run two fresh non-comparative C4 protocol qualification observations:
        r10 and r12 independently prove deferred discovery, namespaced package
        `read_file`, `apply_patch`, and `exec`, grant containment and denial,
        raw logging, and byte-for-byte restoration. Their frozen workload
        validation failures are P107 quality evidence, not P114 failures.
  - [x] Return the P107 package-route re-entry packet. It admits baseline C4
        execution after P114 closeout while preserving separate task-quality
        and economics gates.

Acceptance criteria:

- The capability contract is frozen and reviewed before new live C4 evidence.
- Every counted observation persists the effective role/model/provider/tool
  route, worktree identity, session parentage, and complete validation output.
- P114 distinguishes bridge/host failure, model-control failure, task-quality
  failure, and accounting failure.
- A failed capability gate invalidates the observation and cannot become a
  Qwen quality or economics result.

Current checkpoint: the locked v1 fail-closed data-plane adapter delivery gate
is complete. The direct-MWE battery report is retained at ignored
`runtime/agent_jobs/p114_direct_mwe_battery_report.json`; it does not qualify
C4, resume P107, or make an economics claim.

The current P114 closeout route is the fresh CLI-parent package-MCP route,
not the unrepaired VS Code nested-host custom-tool route. The frozen admission
manifest, deterministic validator, three fresh package composite battery rows,
and two baseline `qwen3-coder:latest` protocol qualification observations have
passed. The frozen workload checks from the qualification observations are P107
quality evidence, not P114 bridge gates. Other C4+ profiles require their own
successful non-comparative package admission observation before they can enter
a P107 comparison. See `planning/p114_c4_reentry_closeout_plan.md`.

P114.3 UI-route note: the supported local MCP parent probe passed one
no-mutation `p114_exec` inventory call and restored configuration. A Worker MCP
test is not yet valid because the C4 provider adapter replaces MCP-provided
        tools with its legacy two-function catalog; preserve that boundary until a
        separate fail-closed catalog-preservation repair is verified.

R14 showed no *direct* child MCP schema: its raw request contained the bridge's
provider-facing `apply_patch` and `exec` definitions, with no
`additional_tools` or `p114_exec` schema, and the local MCP server recorded
zero child calls. It did not rule out deferred discovery.

R15 enabled Code Mode with empty namespace filters and showed the missing route:
the raw child request exposed `p114_exec_probe` in deferred `tool_search`
guidance, which explicitly requires discovery before the MCP call. The frozen
ticket wrongly prohibited `tool_search` and demanded a direct call, so the one
Worker emitted markup, no MCP `tools/call` occurred, and the target remained
`before`.

R16 used that corrected two-call proof. The raw provider stream contained six
completed `tool_search` calls, but the nested Worker host executed none and
returned no discovery result; it retried until the provider stream disconnected.
No MCP `tools/call` occurred and the target remained `before`. The current
repair target is nested code-mode `tool_search` dispatch and turn continuation,
not MCP registration or provider catalog preservation. Configuration and
Worker-role restoration were verified.

R17 tested the direct-MCP workaround by disabling deferred MCP exposure while
leaving Code Mode enabled. It launched one fresh Worker
`019f72ca-6aa5-7d53-b9ce-5e6de2133692`, but the raw child request still exposed
`p114_exec_probe` only through `tool_search` guidance and the bridge still sent
the provider only `apply_patch` and `exec`. The provider repeatedly emitted
`exec`, the adapter rejected six undeclared calls, the MCP server recorded zero
`tools/call` requests, the target stayed `before`, and the child stream
disconnected before completion. The direct-MCP workaround is rejected; the next
repair remains nested `tool_search` dispatch/continuation. MCP and bridge
teardown restored configuration and Worker-role hashes.

R19 then repaired the adapter boundary and retried the deferred MCP path. The
provider-facing sequence was now correct: one `tool_search`, followed by one
`mcp__p114_exec_probe__p114_exec`; adapter verdicts were all accepted, with no
shell, patch, file, or undeclared call. The child
`019f72db-e8e5-7a73-9a45-06fa2ec81f36` nevertheless received
`unsupported call: mcp__p114_exec_probe__p114_exec`, the MCP server recorded
zero `tools/call` requests, and the target stayed `before`. The terminal
marker after that unsupported call is not accepted. The next repair target is
spawned-child code-mode/MCP function dispatch or VS Code extension integration,
not the P114 adapter. Final cleanup restored original configuration and Worker
role state.

R20 source audit corrected that R19 boundary. The matching Codex source tag
`rust-v0.144.5` shows that native `tool_search` is a dedicated
`tool_search_call`, not an ordinary `function_call`. R19 had translated
provider `tool_search` as a function call; the next request showed its output
as `aborted`, then the adapter exposed the MCP tool synthetically anyway. The
adapter now emits native `tool_search_call`, preserves `tool_search_output`,
and exposes `mcp__p114_exec_probe__p114_exec` only after the real search output
contains the probe tool. Focused adapter validation is back to green with 28
tests. The next live step is one fresh no-mutation R20 MCP inventory proof after
VS Code restart.

R20 launched exactly one fresh Worker
`019f72e8-d351-7143-ad4f-55e0f41c3296` and waited once. The run is rejected,
but it proved native deferred MCP discovery in the child: raw session contains
`tool_search_call` followed by `tool_search_output` for namespace
`mcp__p114_exec_probe` and function `p114_exec`. The next provider request
failed with `input[3]: unknown input item type: "tool_search_call"`, so no MCP
`tools/call` executed and the target stayed `before`. Post-run repair taught
the adapter to recognize Codex's top-level namespace-shaped search output. The
next repair is provider-compatible continuation-history translation for
`tool_search_call`/`tool_search_output`.

The R20 follow-up adapter repair is now staged for R21. Child-native
`tool_search_call` and `tool_search_output` history remains visible in the raw
Worker session, but the adapter replays those items upstream as
provider-compatible `function_call` and `function_call_output` records. The
MCP inventory tool is still exposed only after a real search output contains
the probe tool. Focused validation passes with 29 adapter/loopback tests,
Python compile, and `git diff --check` success with LF/CRLF warnings only. The
next live step is one fresh no-mutation R21 proof after bridge/MCP staging and
VS Code reload.

R21 launched exactly one fresh Worker
`019f72f0-d984-7d32-878a-910c3d654b88` and waited once. The run is rejected,
even though the Worker returned `P114_C4_MCP_ROUTING_DONE`. The provider replay
repair worked: the adapter no longer sent unsupported `tool_search_call`
history upstream, and all adapter verdicts were accepted. The raw child
session reached native discovery, then attempted
`mcp__p114_exec_probe__p114_exec({"operation":"inventory"})`; the nested Worker
host returned `unsupported call: mcp__p114_exec_probe__p114_exec`. The MCP
server recorded zero `tools/call` requests, the target remained `before`, and
operator state was restored. The next repair is nested Worker MCP function
dispatch after deferred discovery, not provider replay serialization.

R21 source audit narrowed the defect again. Upstream Codex dispatches
search-surfaced MCP tools when the child response item is namespaced
(`mcp__server / tool`). R21 had forwarded the provider-side flat compatibility
name `mcp__p114_exec_probe__p114_exec` into the child, which could not match
the registered namespaced MCP handler. The adapter now translates provider-flat
MCP calls to child-native namespace `mcp__p114_exec_probe`, name `p114_exec`,
and translates that native history back to the flat provider call on replay.
Focused validation passes with 30 adapter/loopback tests, Python compile, and
`git diff --check` success with LF/CRLF warnings only. R22 should repeat the
same no-mutation proof after bridge/MCP staging and VS Code reload.

R22 accepted the no-mutation MCP routing proof. Fresh Worker
`019f72f7-9bc7-76f1-94de-9c16013ccede` ran once with `fork_context:false` and
the generated ticket verbatim. The raw child session recorded native
`tool_search_call`, native `tool_search_output`, then a namespaced
`function_call` to `mcp__p114_exec_probe / p114_exec` with
`{"operation":"inventory"}`. The MCP probe recorded exactly one `tools/call`
and marker `P114_MCP_EXEC_HANDLER_REACHED`; the Worker returned
`P114_C4_MCP_ROUTING_DONE`. Adapter verdicts were all accepted, the target
remained `before`, no shell/patch/file mutation occurred, and operator state
was restored. This proves VS Code Worker MCP routing through deferred discovery
for no-mutation inventory; patch/mutation semantics remain a separate proof.
The standalone milestone note is
`planning/p114_vs_code_worker_mcp_breakthrough.md`; preserve its core lesson:
provider-facing flat MCP compatibility names must be translated to child-facing
native namespaced MCP calls before entering the nested VS Code Worker.

R23 accepted the bounded MCP patch proof. Fresh Worker
`019f730c-a338-7b52-904e-0fbdf9a8fb45` ran once with `fork_context:false` and
the generated ticket verbatim. The raw child session recorded
`tool_search_call`, `tool_search_output`, then a namespaced `function_call` to
`mcp__p114_exec_probe / p114_exec` with `{"operation":"patch"}`. The MCP probe
recorded exactly one `tools/call` and marker
`P114_MCP_PATCH_HANDLER_REACHED`; the Worker returned
`P114_C4_MCP_PATCH_DONE`. The target changed from exact `before\n` to exact
`after\n`, no shell/exec/apply_patch/custom-tool fallback occurred, all adapter
verdicts were accepted, and operator state was restored. This proves the R22
MCP route can perform a tightly bounded mutation through the native namespaced
child call path.

The clean follow-on implementation plan is captured in
`planning/p114_worker_bridge_package_plan.md`. The next package milestone is a
route-qualified `agent_workbench.agent_bridge` MVP: freeze sanitized R22/R23
fixtures, move pure protocol translation into package modules, implement a
transactional config/role guardrail, then expose separate grant-bound MCP
`exec` and `apply_patch` tools. The design is role-agnostic so future
Worker/Supervisor/Coordinator/Advisor roles can be swapped to Ollama/open-model
providers only through explicit role/profile/provider grants.
The observed-tool backlog and deferred control-plane boundaries are tracked in
`planning/p114_agent_bridge_tool_matrix.md`.
The first packageization tranche has started: sanitized R22/R23 fixtures now
live under `tests/fixtures/p114/`, `agent_workbench.agent_bridge` provides the
initial pure tool/protocol helpers, and the P114 adapter consumes the canonical
bridge tool schemas while preserving its compatibility wrappers.
The transaction tranche has also started in package code: `agent_bridge`
includes TOML guards, stable bridge errors, and a journaled
`BridgeConfigTransaction` with byte-for-byte backups, staged TOML validation,
idempotent restore, concurrent-lock rejection, and prepared-journal recovery.
The P114 MCP and role-bridge staging scripts now call the package transaction
CLI with staged complete TOML files for run-scoped commit/restore instead of
direct live config writes. A disposable temp-home script smoke passed without
touching live Codex config: MCP run
`p114_mcp_tx_smoke_0b40beb0454d4874ad350de6aac72eff` restored one temp config
target byte-for-byte, and role run
`p114_role_tx_smoke_bca6ad6823054fb89ca75154b4a74123` restored temp config and
temp Worker role targets byte-for-byte. This proves local staging transaction
behavior through the converted scripts; no fresh VS Code Worker bridge proof
has been run through them yet.
The package MCP server MVP has also started:
`agent_workbench.agent_bridge.mcp_server` now exposes separate grant-bound
`exec` and `apply_patch` schemas, deny-by-default `RunGrant` policy, root
containment, injectable handlers, JSONL policy/outcome logging, and a
`python -m agent_workbench.agent_bridge.mcp_server` stdio entrypoint. Local
stdio smoke `p114_pkg_mcp_stdio_smoke_e47272b6ab67483cb5504713539a3618`
listed tools, executed granted `python -V`, returned `isError:false`, and
logged an allow policy decision. The package now also includes a constrained
relative-root patch backend, and patch stdio smoke
`p114_pkg_mcp_patch_stdio_smoke_acf11e9da19a4eefb869ef3cd40bd7b7` changed a
temp target from exact `before\n` to exact `after\n`, returned `PATCH_OK`, and
logged an allow policy decision. The legacy R22/R23 proof server remains the
live fallback until the reversible config script is wired to the package
module. That wiring has started as a separate script:
`scripts/enable_agent_bridge_mcp.ps1` stages the package-backed MCP server
without replacing the legacy proof server. Temp-home staging smoke
`p114_agent_bridge_mcp_stage_smoke_dd7f7215acd748eca0603db73d069b1e`
committed the generated config block and restored the disposable config hash
byte-for-byte.

The first fresh package-MCP composite Worker proof,
`p114_agent_bridge_mcp_worker_r1`, is negative host-registration evidence. One
fresh `ollama_qwen_coder_worker` child
`019f7388-f175-75a3-8a72-aecf66c0b427` launched with `fork_context:false` in
the literal P114 worktree and received the ticket contents verbatim. The raw
child session contains no callable package
`mcp__agent_bridge_p114_agent_bridge_mcp_worker_r1__exec` or
`...__apply_patch` schema. It instead attempted unsupported server-level
`mcp__agent_bridge_p114_agent_bridge_mcp_worker_r1`, then used direct
`shell_command` reads. The package server logged initialization, `tools/list`,
and resource discovery, but zero `tools/call` requests, policy decisions, or
outcomes. The target remained exact `before\n`; no direct non-MCP patch ran.
The run therefore is neither a quality-validated nor protocol-accepted
candidate, and economics is unusable because no accepted checkpoint boundary
or token ledger was captured. The required disable restored the live Codex
configuration byte-for-byte against `config.before.toml`.

The standalone package `apply_patch` proof subsequently passed in
`p114_package_mcp_adapter_r5`. The missing bounded package `exec` proof is now
also accepted: `scripts/enable_p114_c4_role_bridge.ps1 -PackageMcpExec` grants
one cross-shell read command and renders an exec-only ticket. After correcting
the ticket's Windows workdir rendering and command shell mismatch, fresh run
`p114_package_mcp_exec_r3` launched one `ollama_qwen_coder_worker`
(`019f73b6-3db7-7a71-9a93-06472751e404`) with `fork_context:false`, completed
one `tool_search` and one namespaced package `exec`, received an allow decision
and exit code 0, and returned `P114_C4_PACKAGE_MCP_EXEC_DONE`. The target
remained exact `before\n`, no fallback tool appeared, and config plus Worker
role restored byte-for-byte. The next package milestone is the declared
read-to-patch-to-validate composite; economics remains unavailable until an
accepted checkpoint/token-ledger boundary is captured.

That composite is now accepted in `p114_package_mcp_composite_r1`: one fresh
`ollama_qwen_coder_worker` (`019f73b8-913a-7701-9dca-d2038466720b`) with
`fork_context:false` performed exactly deferred discovery, a granted package
`exec` read, a granted package `apply_patch`, and a granted package `exec`
validation. Both exec calls had allow decisions and exit code 0; the patch
changed the target to exact `after\n`; no fallback tool appeared; and config
plus Worker role restored byte-for-byte. This accepts the package milestone's
quality and protocol claims. Economics remains unavailable without an accepted
checkpoint/token-ledger boundary; the next package work is the separately
authorized Tranche 5 data-plane tool expansion.

## Phase 115: Scientific Artifact-Inspection Bridge Pilot

Parent issue: #666

Branch: `feature/p115-scientific-artifact-inspection`

Status: active. P118 completed, maintainer explicitly reprioritized P115.
Branch `feature/p115-scientific-artifact-inspection` activated.
Parent issue #666, child issues #722-#729 created.

Rescope note (2026-07-21): P115 was originally scoped for the Codex SDK / P114
adapter / CLI-parent route. That entire route is parked. P115 now uses the P118
native Agent Hub with a single vLLM remote provider (Qwen 3.6 27B). Delegation
via `runSubagent` with bounded profile instructions. No SDK, no adapter, no MCP.

Goal: prove that a bounded Qwen agent profile, delegated through native Agent
Hub, can successfully inspect a frozen public-safe FRESH artifact bundle and
produce a provenance-bearing evidence report — without custom SDK tools, adapter
scaffolding, or MCP.

Boundary: P115 derives its capability boundary from a real FRESH task family.
It uses Copilot Chat native tools only (read_file, grep_search, file_search).
No Copilot SDK, no Codex adapter, no CLI-parent route, no MCP, no arbitrary
shell, no model execution, no GitHub mutation, no P107 economics claims.

Tasks:

- [ ] P115.1 Select a FRESH artifact family, create public-safe fixture bundle,
      and define deterministic oracle. (#722)
- [ ] P115.2 Create a bounded inspection agent profile (`.agent.md`) with
      explicit instructions on what to read, report, and refuse. (#723)
- [ ] P115.3 Create 2-3 validation fixtures (clean, anomaly, provenance-gap)
      and deterministic validation checks. (#724)
- [ ] P115.4 Prove one delegated Qwen3-coder inspection agent (via `runSubagent`)
      can inspect the fixture bundle and produce a provenance-bearing result. (#725)
- [ ] P115.5 Record quality/protocol/economics verdicts and decide whether
      inspection works as a bounded profile or needs scaffolding. (#726)

Acceptance criteria:

- The pilot represents a real FRESH software/model-instance workflow and uses
  reproducible public-safe inputs.
- The agent profile uses bounded instruction authority (not custom tool grants).
- Deterministic fixture validation and delegated inspection evidence agree.
- The phase produces an evidence-based next capability decision, not a generic
  agent-runtime expansion.

See `planning/p115_scientific_artifact_inspection_plan.md`.

## Phase 116: Event-Driven Supervision Control Plane

Parent issue: #669

Branch: `feature/p116-event-driven-supervision-control-plane`

Status: complete. P116.8 supplied the final safe diagnostic-envelope refinement
and fresh native proof. The delivered control layer binds a live Worker,
reduces safe events, permits same-Supervisor review and a Coordinator-approved
same-Worker cue when warranted, and closes the run. It is not a daemon and does
not make a P107 economics claim.

Goal: make the Supervisor an evidence-driven active participant in a live
Worker run. A Coordinator-owned controller will reduce sanitized Worker events,
re-invoke the Supervisor on new evidence, and relay an approved constructive
nudge to the same Worker session when warranted.

Problem statement: native `wait_agent` exposes lifecycle state, not the
intermediate tool/error/file evidence needed for supervision. A chat Supervisor
also does not continue executing after it has returned. The observed P107/P114
Qwen run therefore had an active Worker but no durable supervision loop. P116
repairs the information and invocation path; it does not attempt to make a
message-model Worker deterministic.

Boundaries:

- Preserve the accepted P114 provider/bridge/tool route; P116 does not change
  endpoint, model route, or Worker tool schemas.
- The Coordinator binds run/session identifiers, owns controller lifecycle and
  Worker messaging, and makes acceptance decisions.
- The Supervisor reads only sanitized new-event deltas and returns a structured
  assessment/nudge recommendation. It does not edit the task, operate tools,
  or accept results.
- A Worker has no Supervisor callback credential or new authority. Hook output
  is local, bounded, redacted event evidence only.
- No nested spawning, generic autonomous daemon, fixed retry cap, or P107
  economics conclusion is in scope.

Tasks:

- [x] P116.1 Freeze the run manifest, sanitized event, cursor, Supervisor
      packet, and Coordinator action-log contracts.
- [x] P116.2 Probe the actual Codex command-hook payload/ordering and implement
      sanitized hook-to-event capture with containment and redaction tests.
  - [x] Validate the exact Windows command handler with a lifecycle payload.
  - [x] Observe native hook dispatch from a trusted `codex_vscode` session at
        the exact P116 worktree: `Get-Location` caused run
        `p116_hook_vscode_r8` to write sanitized `PreToolUse` evidence with
        `tool_name: Bash`, `root_match: true`, and an `event_written` receipt.
        The hook path is `Bash` (the inner shell command), not the outer custom
        `exec` envelope.
  - [x] Keep the verdicts separate: focused P116 tests pass and native hook
        dispatch evidence is observed; economics are unassessed and no P107
        economics claim is made. This does not prove end-to-end supervision,
        automatic wake-up, Worker messaging, or native P116.3/P116.4 behavior.
- [x] P116.3 Implement the coordinator-owned event reducer/controller with
      deterministic cursor, idempotency, and restart-recovery tests.
- [x] P116.4 Specify and implement the Supervisor delta-review contract:
      productive repair versus material repeat, deviation, or block; proposed
      constructive nudge; and evidence citation.
- [x] P116.5 Prove the supported route to re-invoke the same Supervisor and
      deliver one Coordinator-approved message to the same Worker session.
  - [x] Execute the tracked r8 native contract: exact Worker/Supervisor binding,
        meaningful delta, same-Supervisor `send_input`, Coordinator decision,
        same-Worker delivery receipt, post-action observation, and transaction
        restore. SDK and app-server evidence are non-qualifying.
- [x] P116.6 Run one bounded native coding task through the complete loop and
      inspect actual session, event, packet, action, artifact, and token data.
- [x] P116.7 Publish the P107 re-entry decision packet and closeout record.
  - [x] P107 may use the P116 control plane only from a fresh native controller
        launched after run-scoped staging; P116 economics remains unassessed.
  - [x] Repair the VS Code in-session delta predicate: a fresh native
        Coordinator returned a sanitized `tool_completed` Worker delta before
        terminal completion, then completed a bounded workflow-package test
        ticket without unnecessary intervention.
- [x] P116.8 Refine the native diagnostic envelope (#710) — implementation and
      native proof complete; phase integration remains open.
  - [x] Freeze a versioned v2 event and immutable pre-tool policy contract.
  - [x] Correlate native call/output records across incremental tails and emit
        only operation class, scope status, declared check ID, bounded failure
        class, and exit code.
  - [x] Preserve explicit v1 compatibility and fail closed on malformed,
        ambiguous, or undeclared v2 policy/correlation input.
  - [x] Prove one fresh native Coordinator -> same Supervisor -> same Worker
        review cycle with a declared check failure and no raw-data leakage.

Acceptance criteria:

- A Supervisor recommendation is traceable to a sanitized event delta and
  cursor, while Coordinator action is traceable to that recommendation.
- The demonstrated loop observes ordinary repair without treating it as a
  failure, and sends useful feedback only when new evidence supports it.
- Contract/controller tests, hook evidence, and the native run agree; no event
  or packet contains provider headers, credentials, raw unrestricted command
  arguments, or raw tool output.
- Quality, protocol, and economics verdicts remain separate. P107 economics is
  not usable without its distinct checkpoint/token-ledger evidence.
- P116.8 must not claim P107 task quality or economics merely because it
  classifies a Worker failure more usefully.

See `planning/p116_event_driven_supervision_control_plane_plan.md`.

## Phase 117: Run-Scoped Supervision Daemon

Parent issue: #686

Branch: `feature/p117-run-scoped-supervision-daemon`

Status: complete. P117 is motivated by P116's r11 stale-post-cursor finding:
supervision state can outlive the cursor boundary unless lease, closure,
journal, and flush behavior are bound to one run. The accepted result remains
bounded to one run and does not establish an unbounded autonomous runtime.

Goal: define a bounded, evidence-auditable supervision daemon boundary for one
run at a time, preserving deterministic recovery and native-session authority
without turning the control plane into an unbounded autonomous runtime.

Tasks:

- [x] P117.1 Define the run-scoped lease, closure, journal, ownership, and
      terminal-state contract.
- [x] P117.2 Specify and test the deterministic flusher, including restart,
      ordering, idempotency, and closure behavior.
- [x] P117.3 Specify the native session adapter and its bounded authority and
      session-lineage evidence requirements.
- [x] P117.4 Produce one bounded native daemon proof with exact run-scoped
      artifacts and stop conditions.
- [x] P117.5 Run the offline sanitized policy replay.
- [x] P117.6 Perform the evidence audit, reporting quality, protocol, and
      economics separately.
- [x] P117.7 Production native adapter and receipt-bound restart proof (#699).

Acceptance criteria:

- Every lease, journal entry, flush, closure, adapter action, and proof artifact
  is bound to one run and has deterministic ordering and terminal behavior.
- The native proof is bounded and shows the actual native session lineage;
  offline replay is clearly identified as offline evidence.
- The bounded r17 evidence records ordered sanitized events, run-scoped lease
  and journal state, native delivery and restart-reconciliation receipts,
  deterministic closure, and rejection after closure. Repeated audits reached
  the same verdict: quality is a validated candidate and protocol is accepted.
- Quality, protocol, and economics remain separate. Economics is unassessed
  for P117, and P117 makes no P107 economics claim.

See `planning/p117_run_scoped_supervision_daemon_plan.md`.

## Phase 118: FRESH vLLM Agent

Parent issue: #716

Branch: `feature/p118-fresh-vllm-agent`

Status: active

Goal: establish a usable native VS Code Copilot Agent Hub deployment in which
one configured remote vLLM coding model serves the Coordinator, Supervisor,
Worker, and selective Advisor roles through distinct custom-agent instructions.
The point is productive development work with one locally controlled model
service, not a model sweep or a ritualized benchmark.

Role separation comes from bounded authority, instructions, tool permissions,
and session topology—not from pretending the underlying model is deterministic
or that role labels create different models. Serial inference is a hardware
requirement: at most one implementation or review child may be actively
reasoning at a time.

Completed tasks:

- [x] P118.1 Provider and role-profile contract (#714)
  - [x] Verify the configured vLLM endpoint/model identity locally without
        tracking credentials.
  - [x] Update all 7 role profiles with distinct authority and concise role
        directives, retaining one model alias.
  - [x] De-bloat `AGENTS.md` with single-model contract.

Planned tasks:

- [ ] P118.2 Serial single-model operating contract
  - [ ] Encode one-active-intense-child limits in the Coordinator and Worker
        directives.
  - [ ] Define Worker delivery, Coordinator verification, and one bounded
        repair handoff.
  - [ ] Add a concise operator launch/checklist for the VS Code UI.
- [ ] P118.3 Productive bounded ticket
  - [ ] Select one ordinary repository task with objective acceptance.
  - [ ] Run Coordinator-to-Worker delivery under the serial contract.
  - [ ] Independently inspect the diff and validation result.
- [ ] P118.4 Selective Advisor and recovery behavior
  - [ ] Exercise a real ambiguity or failed recovery only if one naturally
        occurs.
  - [ ] Confirm Advisor remains advisory and Coordinator owns the follow-up.
  - [ ] Confirm P116 cue delivery only when live evidence makes it useful.
- [ ] P118.5 Deployment decision
  - [ ] Summarize usable/blocked behavior for direct work and delegated tasks.
  - [ ] Report quality, protocol, and economics separately.
  - [ ] Decide whether this becomes the default native Agent Hub profile.

Acceptance criteria:

- Native custom-agent selection binds all participating roles to the declared
  vLLM model alias and records enough identity evidence to audit that claim.
- No more than one intensive child runs at once.
- At least one bounded ticket is delivered, independently validated, and
  classified honestly.
- Any recovery is a bounded response to observed evidence, not a substitute
  implementation by the Coordinator.
- Quality, protocol, and economics are reported independently.

See `planning/p118_fresh_vllm_agent_plan.md`.

## Phase 119: Blackwell vLLM Concurrency Profile

Parent issue: #719

Branch: `feature/p119-vllm-blackwell-concurrency-profile`

Status: complete — delivered via PR #720

Goal: promote the reusable, public-safe parts of the local Blackwell vLLM lab
into Agent Workbench as a packaged deployment playbook for concurrency-capable
VS Code Copilot custom-agent workflows.

P119 is a packaging and operating-contract phase. It records the observed
FlashInfer/FP8-KV/MTP deployment shape, imports sanitized helper scripts and
profiles, and defines bounded concurrency guidance for independent agent work.
It does not publish live endpoint URLs, credentials, raw logs, Cloudflare
configuration, or model/cache artifacts.

Planned tasks:

- [x] P119.1 Sanitized vLLM playbook import
  - [x] Add public-safe launch profiles for stable rollback and FlashInfer
        Copilot-compatible multi-agent operation.
  - [x] Add launch, benchmark, readiness, token, and watcher helper scripts
        without local secrets or raw logs.
  - [x] Document cache/storage assumptions and public-safety boundaries.
- [x] P119.2 Bounded concurrency operating guidance
  - [x] Record normal and burst fan-out guidance for independent read,
        diagnostic, and planning tasks.
  - [x] Preserve central Coordinator ownership for edits, final synthesis,
        service restarts, destructive commands, and conflict resolution.
  - [x] Reconcile with any active P118 role-profile edits without overwriting
        parallel-session work.
- [x] P119.3 Endpoint compatibility and benchmark evidence
  - [x] Document OpenAI Chat Completions / VS Code custom endpoint response
        shape requirements.
  - [x] Preserve local benchmark methodology for single-stream and concurrent
        long-context smoke tests.
  - [x] Record observed capacity as host-specific evidence, not a universal
        model leaderboard claim.
- [x] P119.4 Closeout and handoff
  - [x] Run public-safety checks for secrets, endpoint URLs, logs, and raw
        transcripts.
  - [x] Run Markdown and script sanity checks.
  - [x] Prepare closeout notes for issue #719 and any follow-on P118/P119
        reconciliation.

Acceptance criteria:

- `playbooks/vllm_blackwell/` contains only sanitized templates, profiles, and
  helper scripts.
- `ROADMAP.md`, `CHANGE_LOG.md`, planning notes, and issue #719 agree on scope.
- Bounded concurrency guidance is recorded without claiming unlimited fan-out.
- Live provider details, credentials, raw logs, model blobs, and private paths
  are absent from tracked content.
- P118 agent-profile language changes are either reconciled intentionally or
  left to the active P118 session rather than overwritten here.

See `planning/p119_blackwell_vllm_concurrency_profile.md`.
