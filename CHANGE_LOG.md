# Change Log

Newest entries are last. Keep this file synchronized with `ROADMAP.md`, GitHub
issues, pull requests, and closeout comments.

## 2026-07-04 - Launched Phase 0 governance scaffold

- Created the Phase 0 governance lane for Agent Workbench on
  `feature/p0-governance-scaffold`, with parent issue #1 and child task issues
  #2 through #5.
- Scoped Phase 0 as a governance-only bootstrap: agent contract, contributor
  guide, roadmap, changelog, scratch-space policy, and planning note.
- Excluded package code, CI, docs build, benchmark harnesses, and runtime
  integrations from this first slice.

## 2026-07-04 - Added Agent Workbench governance scaffold

- Added `AGENTS.md` with supervisor/worker agent roles, evidence-based
  reporting rules, file-based handoff/result protocols, and UBC-FRESH issue
  workflow discipline.
- Added `CONTRIBUTING.md`, `ROADMAP.md`, `.gitignore`, and
  `planning/phase0_governance_notes.md` so the repository can host public-safe
  multi-agent workflow experiments without contaminating project-specific repos.
- Recorded Phase 0 acceptance criteria and closeout checks before opening the
  first PR.

## 2026-07-04 - Closed Phase 0 governance scaffold

- Verified the governance-only scaffold with `git diff --check`, Markdown
  inspection, and a public-safety search for private paths, credentials, raw
  transcript leakage, and project-specific contamination.
- Closed child issues #2 through #5 with matching completion comments and opened
  the Phase 0 PR back to `main`.
- Merged the Phase 0 PR and verified parent issue #1 closed after the PR landed.

## 2026-07-04 - Launched Phase 1 worker protocol templates

- Created the Phase 1 protocol-template lane on
  `feature/p1-worker-protocol-templates`, with parent issue #7 and child task
  issues #8 through #11.
- Added planned roadmap placeholders for Phase 2 VS Code Chat bridge playbook
  work and Phase 3 worker model evaluation rubric work.
- Kept Phase 1 scoped to Markdown templates and planning notes, with no package,
  CLI, schema, CI, benchmark harness, or VS Code extension.

## 2026-07-04 - Added worker protocol templates

- Added supervisor ticket, worker result, acceptance checklist, and failure
  report templates under `templates/`.
- Added `planning/phase1_worker_protocol_notes.md` with the manual dogfood dry
  run and sanitized findings.
- Updated `ROADMAP.md` and `CHANGE_LOG.md` so Phase 1 can close through the
  normal issue, PR, and verification ritual.

## 2026-07-04 - Launched Phase 2 VS Code Chat bridge playbook

- Created the Phase 2 bridge-playbook lane on
  `feature/p2-vscode-chat-bridge-playbook`, with parent issue #13 and child task
  issues #14 through #17.
- Scoped Phase 2 to documenting `code chat --mode agent` launch patterns,
  file-based ticket/result conventions, and supervisor verification boundaries.
- Kept response parsing, VS Code extension work, CLI helpers, schemas, CI, and
  live model evaluation deferred.

## 2026-07-04 - Added VS Code Chat bridge playbook

- Added `playbooks/vscode_chat_bridge.md` with stdin launch patterns,
  `--add-file` context examples, ignored job-file conventions, and supervisor
  verification rules.
- Added `planning/phase2_vscode_chat_bridge_notes.md` with the local
  `code chat --help` command-surface dry run and sanitized findings.
- Updated `ROADMAP.md` and `CHANGE_LOG.md` so Phase 2 can close through the
  normal issue, PR, and verification ritual.

## 2026-07-04 - Documented current Ollama worker-model boundary

- Updated `AGENTS.md` and `playbooks/vscode_chat_bridge.md` to require worker
  model choices to come from the configured Ollama host's live `ollama list`
  inventory by default.
- Clarified that installing larger or additional models is a separate setup task
  requiring explicit post-install verification.
- Kept public wording generic around the configured Ollama/GPU worker host rather
  than publishing personal server details.

## 2026-07-04 - Launched Phase 3 Copilot Chat bridge v0 prototype

- Created the Phase 3 bridge-prototype lane on
  `feature/p3-copilot-chat-bridge-v0`, with parent issue #21 and child task
  issues #22 through #26.
- Promoted the Copilot Chat bridge from playbook-only guidance to a local-only
  script-level harness that can launch stdin worker tickets, parse persisted VS
  Code chat session evidence, and write supervisor verification reports.
- Moved the worker model evaluation rubric to Phase 4 so scoring work can build
  on automated bridge evidence rather than manual transcript inspection.

## 2026-07-04 - Added Copilot Chat bridge v0 harness

- Added `scripts/copilot_chat_bridge.py`, a local-only helper that launches
  bounded VS Code Chat worker tickets through stdin and writes ignored
  supervisor reports.
- Implemented session artifact discovery by unique marker plus extraction of
  observed model values, permission-level values, terminal commands, file-tool
  calls, tool names, and blocked or timed-out session state.
- Added `planning/phase3_copilot_chat_bridge_v0_notes.md` and updated the
  bridge playbook with dogfood findings from a visible Ollama-backed worker
  session.
- Confirmed the verifier flags policy deviations from observed evidence, such
  as a worker running an allowed terminal command more times than the ticket
  permitted.

## 2026-07-04 - Closed Phase 3 Copilot Chat bridge v0 prototype

- Verified the Phase 3 script and documentation with Python compilation,
  `git diff --check`, Markdown inspection, and public-safety searches for
  private paths, credentials, raw transcript leakage, and unrelated project
  assumptions.
- Updated and closed child issues #22 through #25 after implementation,
  parser, verifier, and dogfood evidence were synchronized with `ROADMAP.md`,
  `CHANGE_LOG.md`, `planning/`, and `playbooks/`.
- Used child issue #26 for final PR closeout so Phase 3 lands through the same
  GitHub issue, PR, merge, parent-closure, and local branch-cleanup discipline
  that Agent Workbench is designed to study.

## 2026-07-04 - Launched Phase 4 worker model evaluation rubric

- Created the Phase 4 evaluation-rubric lane on
  `feature/p4-worker-model-evaluation-rubric`, with parent issue #28 and child
  task issues #29 through #33.
- Scoped Phase 4 to Markdown-first evaluation artifacts: model inventory notes,
  a worker-model rubric, a failure-mode taxonomy, a result template, and one
  bounded qwen3-coder versus qwen3-coder-next A/B scoring dry run.
- Kept benchmark harnesses, schemas, CI, VS Code extensions, Foundry
  integration, and broad multi-model leaderboards deferred.

## 2026-07-04 - Scored Phase 4 bridge dry run

- Ran a bounded bridge ticket with observed model `qwen3-coder:latest`; the
  worker created the expected ignored result file but ran the required terminal
  command twice, so the rubric classified the result as `retry` with the
  `duplicate-command` failure mode.
- Attempted the matching `qwen3-coder-next:latest` ticket after changing the
  local VS Code panel model state, but persisted session evidence still
  resolved to `qwen3-coder:latest`, so the candidate comparison is recorded as
  blocked by `missing-model-evidence`.
- Added `planning/phase4_ab_scoring_results.md` with sanitized scoring results
  and left raw tickets, reports, and transcripts ignored under runtime paths.

## 2026-07-04 - Synchronized Phase 4 evaluation artifacts

- Updated `AGENTS.md` so the current repository state reflects the bridge
  helper, templates, playbooks, and Markdown rubrics now present in Agent
  Workbench.
- Checked off completed Phase 4 roadmap tasks for model inventory, run
  metadata, rubric, failure taxonomy, evaluation template, and dry-run scoring
  evidence.

## 2026-07-04 - Closed Phase 4 worker model evaluation rubric

- Verified the Phase 4 artifacts with Python compilation of the bridge helper,
  `git diff --check`, Markdown inspection, and public-safety searches for
  private paths, credentials, raw transcript leakage, and unrelated project
  assumptions.
- Closed child issues #29 through #32 after rubric, taxonomy, inventory, and
  template work landed; used issue #33 for final A/B dry-run and PR closeout.
- Recorded the qwen3-coder-next comparison as blocked by observed model
  mismatch, which confirms the rubric's rule that model-comparison claims need
  persisted `resolvedModel` evidence.

## 2026-07-04 - Closed Phase 5 custom agent model switching spike

- Added experimental VS Code workspace custom agents under `.github/agents/`
  for qwen3-coder and qwen3-coder-next strict-worker probes.
- Updated the bridge helper with a `--mode` option and model evidence fallback
  from `resolvedModel` to `modelId`.
- Probed custom-agent no-tool runs and found that the custom agent file loads,
  but the `model` frontmatter does not reliably switch Ollama models in this
  VS Code setup.
- Recorded the next tranche decision: use custom agents for instructions/tool
  restriction only, and move repeatable model comparisons toward a direct
  Ollama API worker harness.

## 2026-07-04 - Launched Phase 6 Copilot SDK Ollama feasibility spike

- Created the Phase 6 SDK/Ollama feasibility lane on
  `feature/p6-copilot-sdk-ollama-spike`, with parent issue #41 and child task
  issues #42 through #45.
- Scoped Phase 6 to a local-only Copilot SDK probe scaffold, public-safe support
  audit notes, and a same-ticket qwen3-coder versus qwen3-coder-next trial
  protocol.
- Kept package scaffolding, CI, VS Code extension work, MCP servers, benchmark
  harnesses, and production bridge claims deferred.

## 2026-07-04 - Added Copilot SDK Ollama probe scaffold

- Added `scripts/copilot_sdk_ollama_probe.py`, a local-only helper that creates
  Copilot SDK sessions with explicit Ollama model and OpenAI-compatible provider
  configuration, then writes observable event evidence to ignored runtime paths.
- Added `planning/phase6_copilot_sdk_ollama_spike_notes.md` with the SDK support
  audit, safe run protocol, same-ticket model comparison commands, and next-step
  decision criteria.
- Recorded the feasibility boundary: the SDK path is promising because it avoids
  VS Code model-picker state, but it must still prove local connection, idle,
  event-capture, and no-loop behavior before becoming the preferred bridge.

## 2026-07-04 - Closed Phase 6 Copilot SDK Ollama feasibility spike

- Verified the P6 probe scaffold with Python compilation, the script help
  surface, `git diff --check`, and a public-safety search over tracked planning,
  script, template, playbook, and rubric surfaces.
- Ran a blocked local dry-run through the probe scaffold; the result correctly
  recorded the local dependency blocker as `No module named 'copilot'` rather
  than claiming a live SDK/Ollama trial had succeeded.
- Merged PR #46 and recorded the next decision point: install or expose the
  Copilot SDK in the probe environment for a real same-ticket Ollama run, or
  move to a raw Ollama API harness if the SDK path remains blocked.

## 2026-07-04 - Launched Phase 7 Copilot SDK local probe environment

- Created the Phase 7 SDK local-probe lane on
  `feature/p7-copilot-sdk-local-probe-env`, with parent issue #48 and child
  task issues #49 through #52.
- Scoped Phase 7 to local SDK source-path support, ignored virtual-environment
  setup notes, provider-header handling, and one no-tool SDK/Ollama probe
  attempt.
- Kept package scaffolding, CI, VS Code extension work, MCP servers, benchmark
  harnesses, production bridge claims, and raw endpoint details deferred.

## 2026-07-04 - Reached SDK provider-call boundary

- Updated `scripts/copilot_sdk_ollama_probe.py` to support optional local SDK
  source loading, ignored SDK base storage, explicit empty tool allowlists,
  optional provider headers, and blocked classification for model-call failures.
- Added `planning/phase7_copilot_sdk_local_probe_env_notes.md` with the local
  setup path and sanitized no-tool probe findings.
- Parsed the local VS Code Ollama provider configuration into ignored runtime
  inputs, added a non-default user-agent for the access layer, and verified that
  both `qwen3-coder:latest` and `qwen3-coder-next:latest` returned the no-tool
  marker exactly once through the SDK bridge.

## 2026-07-04 - Closed Phase 7 Copilot SDK local probe environment

- Merged PR #53 for the Phase 7 SDK/Ollama probe path and verified merge commit
  `a9090fb8875eecc50b3b7ff3e5dafe3abe4ee183`.
- Closed the P7 implementation child issues after updating issue bodies and
  posting closeout comments.
- Recorded the next direction as continuing with the Copilot SDK bridge path in
  a repeated same-ticket model evaluation harness.

## 2026-07-04 - Launched Phase 8 SDK same-ticket evaluation harness

- Created the Phase 8 repeated SDK/Ollama evaluation lane on
  `feature/p8-sdk-same-ticket-evaluation-harness`, with parent issue #55 and
  child task issues #56 through #60.
- Added a public-safe SDK evaluation manifest template and a local-only runner
  that reuses the Phase 7 Copilot SDK probe helper for repeated model/repeat
  trials.
- Scoped Phase 8 to no-tool or tiny bounded same-ticket stability checks, with
  package scaffolding, CI, VS Code extension work, MCP servers, hosted services,
  tool-enabled trials, and production benchmark claims deferred.

## 2026-07-04 - Ran first P8 same-ticket SDK model trial

- Added `scripts/sdk_same_ticket_eval.py`, a local-only manifest runner and
  summarizer that reuses the Phase 7 SDK probe helper for repeated model/repeat
  trials.
- Ran two no-tool marker repeats each for `qwen3-coder:latest` and
  `qwen3-coder-next:latest` through the configured remote Ollama provider path.
- Verified that all four runs classified as `exact-marker` in the ignored P8
  summary, showing the harness is ready for a slightly richer bounded
  documentation-ticket trial.

## 2026-07-04 - Closed Phase 8 SDK same-ticket evaluation harness

- Merged PR #61 for the Phase 8 repeated SDK/Ollama evaluation harness and
  verified merge commit `24c06edb9fd73f7c87e93bb935420bf00084e4ba`.
- Closed P8 implementation child issues after updating issue bodies and posting
  closeout comments.
- Recorded the next direction as using the harness on a tiny documentation-only
  worker ticket before attempting tool-enabled repo-editing trials.

## 2026-07-04 - Planned P9-P14 forward roadmap

- Added a forward roadmap from structured assistant output through patch
  proposal, supervisor-applied mutation, restricted worker mutation, GitHub
  workflow microtrials, and model/packaging decisions.
- Added `planning/p9_p14_forward_plan.md` to explain the sequencing principle:
  move one risk boundary at a time instead of mixing model behavior, tool
  safety, GitHub permissions, and interface decisions in one experiment.
- Left future P9-P14 issue numbers and branches as `TBD` so issue trees are
  created only when each phase actually starts.

## 2026-07-04 - Launched Phase 9 structured documentation-output trial

- Created the Phase 9 structured-output lane on
  `feature/p9-structured-doc-output-trial`, with parent issue #65 and child
  task issues #66 through #70.
- Added `templates/structured_doc_ticket.md` and extended the SDK same-ticket
  summarizer with required-section, extra-prose, forbidden-phrase, and
  loop-like repetition classifications.
- Scoped Phase 9 to no-tool structured assistant output only; patch proposals,
  file mutation, tool-enabled work, and GitHub workflow delegation remain
  deferred to later phases.

## 2026-07-04 - Ran Phase 9 structured-output trial

- Ran two structured-output repeats each for `qwen3-coder:latest` and
  `qwen3-coder-next:latest` through the SDK/Ollama harness.
- Verified that all four runs classified as `structured-output`, with required
  `## Summary`, `## Observations`, and `## Decision` sections present.
- Recorded the next decision: proceed to P10 patch-proposal trials while still
  keeping worker file mutation disabled.

## 2026-07-04 - Closed Phase 9 structured documentation-output trial

- Merged PR #71 for the Phase 9 structured-output harness update and verified
  merge commit `9a70fda17f097e08d299d4e7b8b839b8b274b2dd`.
- Closed P9 implementation child issues after updating issue bodies and posting
  closeout comments.
- Confirmed the next phase should proceed to patch-proposal trials without
  worker-applied file mutation.

## 2026-07-04 - Launched Phase 10 patch proposal protocol trial

- Created the Phase 10 patch-proposal lane on
  `feature/p10-patch-proposal-protocol`, with parent issue #73 and child task
  issues #74 through #78.
- Added patch-proposal templates and extended the SDK same-ticket summarizer
  with fenced patch parsing and proposal classifications.
- Preserved the no-mutation boundary: workers may propose patches, but P10 does
  not apply them.

## 2026-07-04 - Ran Phase 10 patch-proposal trial

- Ran two no-mutation patch-proposal repeats each for `qwen3-coder:latest` and
  `qwen3-coder-next:latest` through the SDK/Ollama harness.
- Verified that all four runs proposed the allowed file path, but
  `qwen3-coder:latest` omitted the required `## Verification` section in both
  repeats.
- Verified that `qwen3-coder-next:latest` produced two complete
  `patch-proposal` classifications, supporting P11 supervisor-applied patch
  harness work.

## 2026-07-04 - Closed Phase 10 patch proposal protocol trial

- Merged PR #79 for the Phase 10 no-mutation patch-proposal protocol and
  verified merge commit `725240c35e7e8ab5898c54504855bab7d50d89fc`.
- Closed P10 implementation child issues after updating issue bodies and
  posting closeout comments.
- Confirmed the next phase should proceed to supervisor-applied patch harness
  work while keeping mutation under supervisor control.

## 2026-07-04 - Launched Phase 11 supervisor-applied patch harness

- Created the Phase 11 supervisor-applied patch lane on
  `feature/p11-supervisor-applied-patch-harness`, with parent issue #81 and
  child task issues #82 through #86.
- Added `scripts/supervisor_patch_apply.py`, a guarded supervisor-side helper
  that extracts one proposed diff block and writes only under an ignored
  sandbox root.
- Preserved the safety boundary that workers do not mutate files directly.

## 2026-07-04 - Ran Phase 11 supervisor-applied patch trial

- Reused a successful ignored P10 patch proposal result and applied it under an
  ignored supervisor sandbox with `scripts/supervisor_patch_apply.py`.
- Verified that the proposed target matched the allowed file and the expected
  text was present after sandbox application.
- Confirmed no tracked file was mutated by the apply harness, supporting a
  narrow P12 restricted tool-enabled worker trial in an ignored sandbox.

## 2026-07-04 - Closed Phase 11 supervisor-applied patch harness

- Merged PR #87 for the Phase 11 supervisor-applied patch harness and verified
  merge commit `f4757187db3b2927f70a739594763d4b391e9400`.
- Closed P11 implementation child issues after posting closeout comments.
- Confirmed the next phase can test a restricted tool-enabled worker path only
  against ignored sandbox targets.

## 2026-07-04 - Launched Phase 12 restricted tool-enabled worker trial

- Created the Phase 12 restricted tool-enabled lane on
  `feature/p12-restricted-tool-worker-trial`, with parent issue #89 and child
  task issues #90 through #94.
- Added `templates/restricted_tool_ticket.md` and
  `planning/phase12_restricted_tool_trial_notes.md`.
- Recorded the bridge decision: the SDK path remains no-tool, while the VS Code
  Chat bridge is the available tool-observable path for one ignored-file trial.

## 2026-07-04 - Ran Phase 12 restricted tool-enabled worker trial

- Launched one VS Code Chat bridge worker ticket that allowed exactly one
  ignored runtime file mutation and forbade terminal commands.
- Verified from the supervisor report that the worker used the `create_file`
  tool, wrote only the allowed runtime file, ran no terminal commands, and
  produced the final marker.
- Confirmed the target file contained exactly the requested marker line, while
  raw session and transcript paths remained ignored local evidence.

## 2026-07-04 - Closed Phase 12 restricted tool-enabled worker trial

- Merged PR #95 for the Phase 12 restricted tool-enabled worker trial and verified merge commit `9968858eb84994d89245ac427eb93a51885e891c`.
- Closed P12 implementation child issues after posting closeout comments.
- Confirmed the next phase can test GitHub workflow microtasks, but issue closure and PR merge remain supervisor-only.

## 2026-07-04 - Ran Phase 13 GitHub workflow microtrial

- Created the Phase 13 GitHub workflow lane on
  `feature/p13-github-workflow-microtrial`, with parent issue #97 and child
  task issues #98 through #102.
- Added `templates/github_microtask_ticket.md` and
  `planning/phase13_github_workflow_microtrial_notes.md`.
- Ran a worker-prepared comment-body trial that classified as
  `missing-section`, then posted a supervisor-reviewed file-backed comment to
  issue #100 and verified it with read-only `gh issue view`.

## 2026-07-04 - Closed Phase 13 GitHub workflow microtrial

- Merged PR #103 for the Phase 13 GitHub workflow microtrial and verified merge commit `0b70ce738df381a5b56aa610b8c11696c33d4841`.
- Closed P13 implementation child issues after posting closeout comments.
- Confirmed that workers may prepare GitHub text, but supervisor retains mutation, issue closure, and PR merge authority.

## 2026-07-04 - Launched Phase 14 model matrix and packaging decision

- Created the Phase 14 model matrix and packaging lane on
  `feature/p14-model-matrix-packaging-decision`, with parent issue #105 and
  child task issues #106 through #110.
- Refreshed the configured Ollama-compatible model inventory through ignored
  local provider inputs and recorded only sanitized model IDs.
- Added `planning/phase14_model_matrix_packaging_decision.md` and
  `planning/adr_0001_workbench_surface.md`, deciding to keep Agent Workbench as
  Markdown protocols plus local scripts for the next tranche.

## 2026-07-04 - Closed Phase 14 model matrix and packaging decision

- Merged PR #111 for the Phase 14 model matrix and architecture decision and verified merge commit `36f3fb9095f27cc19770121e00d55dd8eadeb2ed`.
- Closed P14 implementation child issues after posting closeout comments.
- Accepted ADR 0001: keep Agent Workbench as Markdown protocols plus local scripts for the next tranche.

## 2026-07-04 - Planned P15-P20 next tranche

- Added a forward roadmap from model-family expansion through command-surface
  stabilization, evidence schema, richer sandbox tool trials, delegation
  policy, and packaging revisit.
- Added `planning/p15_p20_next_tranche_plan.md` to ground the next tranche in
  P9-P14 evidence.
- Kept future P15-P20 issue numbers and branches as `TBD` so issue trees are
  created only when each phase starts.

## 2026-07-04 - Ran Phase 15 model-family expansion trial

- Created the Phase 15 model-family expansion lane on
  `feature/p15-model-family-expansion-trial`, with parent issue #115 and child
  task issues #116 through #120.
- Ran the stable marker, structured-output, and patch-proposal no-tool ticket
  families against `codestral:latest`, `devstral-small-2:latest`, and
  `deepseek-coder-v2:16b` through the SDK/Ollama harness.
- Verified that all three models passed marker and structured-output
  classifications, while `deepseek-coder-v2:16b` missed the required
  `## Verification` section in the patch-proposal family.
- Added `planning/phase15_model_family_expansion_notes.md` with sanitized
  findings and deferred the largest configured models until command surfaces and
  evidence schema are more stable.

## 2026-07-04 - Stabilized Phase 16 command surfaces

- Created the Phase 16 command-surface lane on
  `feature/p16-command-surface-stabilization`, with parent issue #122 and child
  task issues #123 through #127.
- Added `scripts/check_command_surfaces.py`, a local smoke checker for reusable
  script help surfaces, SDK manifest template fields, and SDK harness dry-run
  planning.
- Added `planning/phase16_command_surface_stabilization_notes.md` to record the
  direct-script command contract, redaction boundary, report metadata
  expectations, and package-readiness checkpoint.
- Kept packaging deferred until the evidence layout and delegation policy are
  more stable.

## 2026-07-04 - Defined Phase 17 evidence summary schema

- Created the Phase 17 evidence-schema lane on
  `feature/p17-evidence-store-summary-schema`, with parent issue #129 and child
  task issues #130 through #134.
- Added `templates/evidence_summary.md` and
  `templates/evidence_summary.schema.json` as the lightweight summary contract
  for local evidence promotion.
- Added `playbooks/evidence_store.md` to separate ignored raw evidence from
  tracked public summaries and define promotion rules.
- Added `planning/phase17_evidence_schema_notes.md` with a sanitized backfilled
  P15 model-run summary and the decision to defer databases, CI schema
  validation, and packaged evidence collectors.

## 2026-07-04 - Ran Phase 18 richer restricted tool trial

- Created the Phase 18 richer restricted-tool lane on
  `feature/p18-richer-restricted-tool-trial`, with parent issue #136 and child
  task issues #137 through #141.
- Updated `templates/restricted_tool_ticket.md` so restricted tool tickets can
  explicitly list required ignored-runtime reads as well as one allowed output.
- Ran one VS Code Chat bridge worker trial that read an ignored input file and
  created the allowed ignored output file without terminal commands.
- Added `planning/phase18_richer_restricted_tool_trial_notes.md` with
  sanitized supervisor evidence and kept tracked-file mutation forbidden.

## 2026-07-04 - Added Phase 19 delegation policy

- Created the Phase 19 delegation-policy lane on
  `feature/p19-delegation-policy-trust-levels`, with parent issue #143 and child
  task issues #144 through #148.
- Added `planning/delegation_policy.md` with trust levels L0 through L6 and
  ticket-family authority mapping.
- Added `planning/phase19_delegation_policy_notes.md` and updated `AGENTS.md`
  so worker authority boundaries are part of the live agent contract.
- Kept tracked-file mutation, GitHub mutation, issue closure, PR merge, release,
  and final phase closeout supervisor-only.

## 2026-07-04 - Accepted Phase 20 interface direction

- Created the Phase 20 packaging/interface lane on
  `feature/p20-packaging-interface-decision`, with parent issue #150 and child
  task issues #151 through #155.
- Added `planning/adr_0002_interface_direction.md`, accepting a narrow local
  Python package and CLI spike as the next architecture move.
- Added `planning/phase20_packaging_revisit_notes.md` and
  `planning/p21_p24_forward_plan.md` to cite P15-P19 evidence and plan the next
  tranche.
- Deferred VS Code extension, MCP server, hosted agent, dashboard, and broad
  benchmark-harness work until the local CLI path proves useful.

## 2026-07-04 - Added Phase 21 package and CLI skeleton

- Created the Phase 21 package-skeleton lane on
  `feature/p21-minimal-local-package-cli`, with parent issue #157 and child
  task issues #158 through #162.
- Added `pyproject.toml`, `src/agent_workbench/__init__.py`,
  `src/agent_workbench/__main__.py`, and `src/agent_workbench/cli.py`.
- Added the `agent-workbench` console script with minimal help and version
  surfaces while preserving direct script usage.
- Added `planning/phase21_minimal_package_cli_notes.md` and kept worker trust
  levels unchanged.

## 2026-07-04 - Added Phase 22 CLI wrappers

- Created the Phase 22 CLI-wrapper lane on
  `feature/p22-cli-wrappers-existing-commands`, with parent issue #164 and
  child task issues #165 through #169.
- Added `agent-workbench smoke` as a package entrypoint for command-surface
  smoke checks.
- Added `agent-workbench eval --manifest <path>` with `--dry-run` and
  `--summary-only` support for the SDK same-ticket evaluation harness.
- Added `planning/phase22_cli_wrappers_notes.md` and preserved direct script
  compatibility.

## 2026-07-04 - Added Phase 23 evidence commands

- Created the Phase 23 evidence-validation lane on
  `feature/p23-evidence-summary-validation-rendering`, with parent issue #171
  and child task issues #172 through #176.
- Added `src/agent_workbench/evidence.py` with lightweight evidence summary
  validation and Markdown rendering.
- Added `agent-workbench evidence validate` and
  `agent-workbench evidence render`.
- Added `planning/phase23_evidence_validation_rendering_notes.md` and kept the
  validator local, conservative, and dependency-free.

## 2026-07-04 - Dogfooded Phase 24 CLI workflow

- Created the Phase 24 CLI-dogfood lane on
  `feature/p24-cli-dogfood-workflow`, with parent issue #178 and child task
  issues #179 through #183.
- Ran `agent-workbench smoke`, `agent-workbench eval --dry-run`, and a
  provider-backed no-tool `agent-workbench eval` against `qwen3-coder:latest`.
- Verified the provider-backed run classified as `exact-marker` and rendered a
  sanitized evidence summary through `agent-workbench evidence validate` and
  `agent-workbench evidence render`.
- Added `playbooks/cli_workflow.md`,
  `planning/phase24_cli_dogfood_workflow_notes.md`, and README quickstart
  guidance for small real-project trials.

## 2026-07-04 - Added Phase 25 real-project pilot scaffold

- Created the Phase 25 real-project pilot lane on
  `feature/p25-real-project-pilot-scaffold`, with parent issue #185 and child
  task issues #186 through #190.
- Added `agent-workbench pilot scaffold` to create bounded worker tickets, SDK
  evaluation manifests, and evidence-summary stubs for target project roots.
- Added marker and proposal modes while keeping worker authority no-tool and
  supervisor-owned.
- Updated `playbooks/cli_workflow.md` and added
  `planning/phase25_real_project_pilot_scaffold_notes.md` so the package can be
  used for small real-project trials without hand-writing every runtime file.

## 2026-07-04 - Added Phase 26 cross-project eval support

- Created the Phase 26 cross-project eval lane on
  `feature/p26-cross-project-eval`, with parent issue #192 and child task issues
  #193 through #196.
- Added `agent-workbench eval --project-root <target-project>` so manifests,
  tickets, outputs, and evidence can live under a target project root while
  harness scripts stay anchored to the Agent Workbench checkout.
- Materialized private manifest copies are written beside the target manifest,
  so ignored target-project artifact trees remain self-contained.
- Updated the CLI workflow playbook and added
  `planning/phase26_cross_project_eval_notes.md`.

## 2026-07-04 - Added Phase 27 supervisor decision packets

- Created the Phase 27 supervisor-decision-packet lane on
  `feature/p27-supervisor-decision-packets`, with parent issue #198 and child
  task issues #199 through #202.
- Added `agent-workbench pilot pack-scaffold` for multi-ticket proposal packs
  with isolated eval output and Copilot SDK scratch directories per task.
- Updated single-ticket pilot scaffolds so generated manifests no longer share
  one eval output directory by default.
- Added `agent-workbench evidence synthesize` to validate multiple evidence
  summaries and render one sanitized supervisor decision packet.
- Added `planning/p27_p30_forward_plan.md`,
  `planning/phase27_supervisor_decision_packets.md`, and updated the CLI
  workflow playbook.

## 2026-07-04 - Added Phase 28 claim review aids

- Created the Phase 28 claim-review lane on `feature/p28-claim-review-aids`,
  with parent issue #204 and child task issues #205 through #208.
- Added optional `accepted_claims`, `rejected_claims`, and
  `needs_evidence_claims` fields to sanitized evidence summaries.
- Extended evidence validation, rendering, and supervisor decision packets to
  surface claim dispositions when present.
- Added `templates/claim_review_checklist.md` and
  `planning/phase28_claim_review_aids.md` to make unsupported worker-claim
  review explicit before supervisor promotion.

## 2026-07-04 - Added Phase 29 repeat-run and model comparison

- Created the Phase 29 comparison lane on
  `feature/p29-repeat-run-model-comparison`, with parent issue #210 and child
  task issues #211 through #214.
- Added `agent-workbench compare eval` to render Markdown comparison reports
  from existing SDK same-ticket evaluation `summary.json` artifacts.
- The comparison report includes classification counts, per-model consistency,
  per-run outcomes, and a boundary warning against broad model rankings.
- Added `planning/phase29_repeat_run_model_comparison.md` and updated the CLI
  workflow playbook.

## 2026-07-04 - Added Phase 30 real-project deployment playbook

- Created the Phase 30 deployment-playbook lane on
  `feature/p30-real-project-deployment-playbook`, with parent issue #216 and
  child task issues #217 through #220.
- Added `playbooks/real_project_deployment.md` to document target selection,
  proposal-pack scaffolding, evidence summaries, decision packets, claim review,
  optional model/repeat comparison, supervisor promotion, cleanup, and stop
  conditions.
- Added `planning/phase30_real_project_deployment_playbook.md` and linked the
  deployment playbook from the README.
- Closed the P27-P30 tranche with Agent Workbench ready for cautious
  real-project proposal-assist use, not autonomous implementation or delegated
  GitHub closeout.

## 2026-07-04 - Launched Phase 31 delegation economics model

- Reframed the post-P30 roadmap around whether supervised self-hosted worker
  delegation can reduce paid supervisor-token effort on real UBC-FRESH project
  work after setup, verification, retry, and cleanup costs are counted.
- Created the Phase 31 delegation-economics lane on
  `feature/p31-delegation-economics-model`, with parent issue #222 and child
  task issues #223 through #226.
- Preserved the raw developer framing in
  `planning/notes-gp-20260704-raw.md`, promoted the concise strategy into
  `planning/notes.md`, and added `planning/delegation_economics_vision.md` as
  a structured vision note.
- Added planned roadmap phases P31 through P36 covering the delegation economics
  model, task taxonomy, worker model capability profiles, a rules-based
  delegation decision engine, real-project pilot accounting, and policy tuning.
- Kept P32-P36 planned only so the next development environment can activate
  the FreshForge or CLEWS pilot lane deliberately.

## 2026-07-04 - Added Phase 32 task delegation taxonomy

- Created the Phase 32 task-taxonomy lane on
  `feature/p32-task-taxonomy-delegation-suitability`, with parent issue #228
  and child task issues #229 through #232.
- Added `planning/task_delegation_taxonomy.md` to classify common UBC-FRESH
  development task types by planning level, delegation suitability, default
  worker authority, expected value, and main risk.
- Defined high, medium, low, and avoid suitability levels plus good-delegation,
  poor-delegation, and split-or-supervise-more criteria.
- Mapped task types to the existing delegation trust levels and kept tracked
  mutation, GitHub mutation, release work, and parent phase closeout
  supervisor-owned by default.
- Linked the taxonomy from the real-project deployment and CLI workflow
  playbooks so supervisors classify candidate tasks before scaffolding worker
  tickets.

## 2026-07-04 - Added Phase 33 worker model capability profiles

- Created the Phase 33 worker-model profile lane on
  `feature/p33-worker-model-capability-profiles`, with parent issue #234 and
  child task issues #235 through #238.
- Added `templates/model_capability_card.md` and `model_profiles/` to record
  evidence-scoped worker model strengths, failure modes, loop risk,
  ticket-shape sensitivity, and recommended authority ceilings.
- Added initial public-safe profiles for `qwen3-coder:latest` and
  `qwen3-coder-next:latest` from existing Agent Workbench evidence.
- Added a planned `gpt-oss:*` profile lane so future non-qwen model-family
  comparisons can be tracked without unsupported installed-run claims.
- Linked model profiles from the CLI and real-project deployment playbooks so
  supervisors consult model-specific evidence before assigning worker tickets.

## 2026-07-04 - Added Phase 34 delegation decision engine v0

- Created the Phase 34 decision-engine lane on
  `feature/p34-delegation-decision-engine-v0`, with parent issue #240 and child
  task issues #241 through #244.
- Added `templates/delegation_decision_input.json` and a rules-based
  `agent-workbench decide task` command for transparent delegation
  recommendations.
- Implemented deterministic rules for `delegate`, `do-directly`,
  `split-smaller`, `needs-human-decision`, and `defer` recommendations using
  task type, roadmap level, risk, suitability, model profile status, authority
  level, and expected delegation economics.
- Added `planning/phase34_delegation_decision_engine_v0.md` and linked the
  decision command from the CLI and real-project deployment playbooks.
- Dogfooded the command on delegate, split-smaller, and do-directly candidate
  cases before closeout.

## 2026-07-04 - Corrected delegation economics to token-priced cost

- Updated the P34 decision engine and `templates/delegation_decision_input.json`
  so expected net benefit is driven by input/output token counts and
  per-1M-token USD prices instead of wall-clock minutes.
- Kept latency/friction minutes as optional metadata only.
- Updated the delegation economics vision, P34 planning note, roadmap, and
  changelog to make paid supervisor token spend the primary optimization target.
- Recorded PostHog-style AI observability and current provider price matrices as
  useful sources for future token/cost accounting without wiring external
  observability into Agent Workbench yet.
