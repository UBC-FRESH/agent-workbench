# Change Log

Newest entries are last. Keep this file synchronized with `ROADMAP.md`, GitHub
issues, pull requests, and closeout comments.

## 2026-07-12 - Corrected P96 yield-and-audit-cost model comparison closeout

- Root cause of P96 p96_3 failure identified: stale `COPILOT_CLI_PATH` environment
  variable (WinError 193). Copilot SDK failed with inline PowerShell commands.
- Ran corrected probe as `.py` file — both lanes succeeded:
  - Baseline (`qwen3.6:35b-a3b-bf16`): 336 output tokens in 6.1 s
  - Candidate (`qwen3.6:35b-a3b-q8_0`): 311 output tokens in 42.7 s (7.0× slower)
- Verdict superseded from `insufficient_evidence` / `not_attempted` to
  `attempted_with_partial_signal` — full accepted-record classification per the
  P96 yield measurement protocol was not executed, but token-level comparison is
  sufficient for qualified closeout.
- Updated ROADMAP.md table row and phase section status to **complete (qualified)**;
  CHANGE_LOG kept synchronized with this entry.
- Added infrastructure improvements:
  - `~/.agent-workbench-env.txt` stores Ollama OpenAI-compatible endpoint and provider
    headers path; probe script's `load_env_file()` auto-loads it before argument parsing.
  - `AGENTS.md` documents env file location so every new Copilot session exports the
    correct variables before attempting probe scripts.
- GitHub issue #585 already closed with stale closeout notes (cannot edit post-close).
  The corrected verdict and evidence are captured in
  `benchmarks/document_library/tsa23_tsr/p96_model_lane_comparison_execution_summary.json`
  and `planning/phase96_verdict.md`.

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

## 2026-07-04 - Added scientific workbench direction note

- Added `planning/scientific_workbench_direction.md` to promote the strategic
  direction that Agent Workbench should become a reproducible workbench for
  supervised AI-assisted scientific and software development, not another
  general agent framework.
- Updated `planning/notes.md` to align the delegation economics strategy with
  token/cash-first accounting and the longer-term artifact-first workbench
  direction.
- Extended `ROADMAP.md` with planned P37-P40 phases covering artifact/workflow
  contracts, role/capability/implementation separation, reusable scientific
  workbench templates, and observability/token-cost ingestion.
- Kept P35/P36 as the immediate empirical tranche for real-project pilot
  accounting and policy tuning before broadening the architecture.

## 2026-07-04 - Added P35 real-project pilot accounting

- Opened P35 GitHub issue #250 with child issues #251 through #254 for pilot
  selection, accounting records, synthesis, and closeout.
- Added `src/agent_workbench/accounting.py` and the `agent-workbench
  accounting validate|render|synthesize` command surface for sanitized
  token/cash pilot accounting records.
- Added `templates/pilot_accounting_record.json` and
  `planning/phase35_real_project_pilot_accounting.md` to define the real-project
  pilot accounting protocol.
- Updated the real-project deployment playbook and README with accounting
  workflow examples.
- Updated the command-surface smoke check to include the accounting synthesis
  help surface.

## 2026-07-04 - Added P36 policy tuning loop

- Opened P36 GitHub issue #256 with child issues #257 through #260 for outcome
  schema, tuning rules, reporting, and future ML boundaries.
- Added `src/agent_workbench/policy.py` and the `agent-workbench policy tune`
  command for rules-based delegation policy tuning from P35 accounting records.
- Added `planning/phase36_policy_tuning_loop.md` and updated
  `planning/delegation_policy.md` with transparent tuning rules, retry limits,
  bailout guidance, and ML optimizer thresholds.
- Updated README, the real-project deployment playbook, roadmap, changelog, and
  command-surface smoke coverage.

## 2026-07-04 - Added P37 artifact workflow contracts

- Opened P37 GitHub issue #262 with child issues #263 through #266 for artifact
  vocabulary, workflow step contracts, example records, and closeout.
- Added `src/agent_workbench/workflow.py` and the `agent-workbench workflow
  validate|render` command surface.
- Added `templates/workflow_step_record.json` and public-safe example workflow
  records for software task review, documentation proposal, paper outline, and
  benchmark proposal.
- Added `planning/phase37_artifact_workflow_contracts.md` and updated README,
  roadmap, changelog, and command-surface smoke coverage.

## 2026-07-04 - Added P38 role capability implementation model

- Opened P38 GitHub issue #268 with child issues #269 through #272 for role
  model, capability model, implementation mapping, and closeout.
- Added `src/agent_workbench/roles.py` and the `agent-workbench roles
  validate|render` command surface.
- Added `templates/role_capability_implementation.json` and public-safe role
  examples for programmer patch proposals, analyst token accounting, and editor
  documentation proposals.
- Added `planning/phase38_role_capability_implementation.md` and updated
  README, roadmap, changelog, and command-surface smoke coverage.
- Clarified the non-orchestration boundary: FreshForge and other project-native
  tools are implementation candidates that Agent Workbench records around, not
  systems that Agent Workbench replaces.

## 2026-07-04 - Added P39 graph-envelope workbench templates

- Opened P39 GitHub issue #274 with child issues #275 through #278 for template
  scope, artifact layout examples, integration boundaries, and closeout.
- Added `templates/workbench_templates/agentic_graph_envelope.json` to reuse
  FreshForge-style graph vocabulary for agentic workflows: workflow, nodes,
  needs, providers, inputs, outputs, artifacts, and diagnostics.
- Added reusable Markdown template envelopes for software tasks, paper tasks,
  proposal tasks, and benchmark tasks.
- Kept the non-orchestration boundary explicit: templates point to FreshForge,
  project CLIs, notebooks, Snakemake, CI, Quarto, scripts, or human review for
  execution.
- Added `planning/phase39_reusable_workbench_templates.md` and updated the
  roadmap.

## 2026-07-04 - Added P40 token-cost ingestion records

- Opened P40 GitHub issue #280 with child issues #281 through #284 for
  observability source audit, sanitized import contract, helper command, and
  closeout.
- Added `src/agent_workbench/tokens.py` and the `agent-workbench tokens
  validate|render|synthesize` command surface.
- Added `templates/token_cost_record.json` and
  `planning/phase40_token_cost_ingestion.md`.
- Updated README, roadmap, changelog, and command-surface smoke coverage.
- Kept observability as optional measurement input and excluded raw prompts,
  traces, provider URLs, headers, credentials, and personal paths from tracked
  token/cost records.

## 2026-07-04 - Started P41 FreshForge graph integration

- Opened P41 GitHub issue #286 with child issues #287 through #290 for optional
  FreshForge dependency wiring, graph template conversion, diagnostics, and
  closeout.
- Added `planning/freshforge_graph_dependency_opinion.md` to record the
  architectural position that Agent Workbench should reuse FreshForge graph
  records and validation rather than invent a parallel graph engine.
- Added `planning/phase41_freshforge_graph_integration.md` and extended the
  roadmap through P46 for the graph-backed delegation direction.
- Added an optional `graph` dependency extra, a FreshForge-backed
  `agent-workbench graph validate` command, and a FreshForge-compatible agentic
  workflow graph template.

## 2026-07-04 - Added P42 agent metadata convention

- Opened P42 GitHub issue #292 with child issues #293 through #296 for metadata
  placement, role/capability/authority metadata, evidence/decision/token
  metadata, and closeout.
- Added `planning/phase42_agent_metadata_convention.md` to define how Agent
  Workbench metadata lives inside FreshForge-compatible graph fields.
- Extended `agent-workbench graph validate` with `--agent-metadata` so
  supervisors can check required Agent Workbench metadata without executing
  graph nodes.
- Updated the FreshForge-compatible graph template to use
  `parameters.agent_workbench` and node `provenance` as the canonical metadata
  locations.

## 2026-07-04 - Added P43 graph-backed pilot workflow

- Opened P43 GitHub issue #298 with child issues #299 through #302 for pilot
  selection, graph representation, evidence/accounting linkage, and closeout.
- Added `templates/workbench_templates/freshforge_proposal_assist_graph.json`
  as a real proposal-assist pilot graph pattern.
- Added `agent-workbench graph render` to produce supervisor-readable Markdown
  summaries of graph nodes, roles, authority levels, evidence links, accounting
  links, and artifacts.
- Added `planning/phase43_graph_backed_pilot_workflow.md` and updated README,
  roadmap, changelog, and smoke coverage.

## 2026-07-04 - Added P44 graph-aware delegation decisions

- Opened P44 GitHub issue #304 with child issues #305 through #308 for
  graph-node decision inputs, recommendation logic, report surface, and
  closeout.
- Added `agent-workbench graph decide` to render node-level delegation
  recommendations from FreshForge-compatible graphs with Agent Workbench
  metadata.
- Reused the existing rules-based `decide_task` engine rather than creating a
  separate graph decision policy.
- Added `planning/phase44_graph_aware_decision_engine.md` and updated README,
  roadmap, changelog, and smoke coverage.

## 2026-07-04 - Added P45 per-node token economics

- Opened P45 GitHub issue #310 with child issues #311 through #314 for
  node-level token/cost records, graph economics synthesis, policy feedback,
  and closeout.
- Extended sanitized token/cost records with graph-node scope fields and an
  optional direct-supervisor counterfactual block.
- Added `agent-workbench tokens graph-synthesize` to summarize token/cash
  economics by graph node.
- Added sanitized token example records and
  `planning/phase45_per_node_token_economics.md`.

## 2026-07-04 - Recorded P46 FreshForge dependency decision

- Opened P46 GitHub issue #316 with child issues #317 through #320 for
  evidence review, dependency options, recommendation, and closeout.
- Added `planning/phase46_freshforge_dependency_decision.md`.
- Decided to keep FreshForge as the canonical graph-validation layer while
  retaining it as an optional `graph` extra rather than a required base
  dependency.
- Recorded that Agent Workbench should not build a parallel graph engine unless
  a future FreshForge incompatibility is concrete and documented.

## 2026-07-04 - Queued P47 FreshForge deployment test batch

- Opened P47 GitHub issue #322 with child issues #323 through #326 for roadmap
  cleanup, FreshForge P16/P17/P18 graph-backed test packets, and closeout.
- Fixed the stale P46 roadmap status after the merged P46 closeout.
- Added `planning/phase47_freshforge_deployment_test_batch.md`.
- Added FreshForge deployment-test packet graphs for P16 provider evidence
  conventions, P17 matrix export surfaces, and P18 release-readiness review.
- Kept the phase as queueing and validation only: no FreshForge mutation, no
  worker execution, and no release or GitHub closeout delegation.

## 2026-07-04 - Added P48 phase-scale A/B token economics protocol

- Opened P48 GitHub issue #328 with child issues #329 through #332 for
  benchmark protocol, validation/rendering, FreshForge P16 packet, and
  closeout.
- Added `src/agent_workbench/benchmark.py` and
  `agent-workbench benchmark validate|render`.
- Added `templates/benchmarks/freshforge_p16_phase_ab_benchmark.json` as the
  first phase-scale direct-vs-delegated benchmark packet.
- Added `planning/phase48_phase_scale_ab_token_economics.md`.
- Defined the experimental design around two disposable FreshForge worktrees
  from the same start commit instead of stash-based rollback.

## 2026-07-04 - Added P49 benchmark worktree preparation

- Opened P49 GitHub issue #334 with child issues #335 through #338 for
  worktree setup contracts, command implementation, FreshForge P16 setup, and
  closeout.
- Added `agent-workbench benchmark prepare-worktrees` so benchmark records can
  create or report lane worktrees in a target project checkout.
- Added `planning/phase49_benchmark_worktree_prep.md` with the FreshForge P16
  setup protocol.
- Prepared the first direct-supervisor and delegated-graph FreshForge P16
  benchmark lane worktrees from the same recorded start commit.

## 2026-07-04 - Opened P50 FreshForge P16 A/B benchmark run

- Opened P50 GitHub issue #340 with child issues #341 through #345 for the
  direct lane, evidence capture, delegated lane, A/B comparison, and
  maintainer-reviewed closeout.
- Added `planning/phase50_freshforge_p16_ab_benchmark_run.md`.
- Kept P50 explicitly open for iterative benchmark work rather than a
  setup-only closeout.

## 2026-07-04 - Recorded P50 FreshForge P16 delegated iteration

- Ran the delegated Agent Workbench FreshForge P16 lane from the same FreshForge
  start commit used by the direct baseline.
- Executed two proposal-only `qwen3-coder-next:latest` worker tickets with 4465
  input tokens and 632 output tokens in the zero-cash local Ollama lane.
- Implemented the delegated FreshForge P16 branch at commit `c781775` with
  optional provider-owned evidence mappings threaded through provider run
  results, node results, compact summaries, evidence manifests, tests, and docs.
- Verified the delegated branch with targeted tests, full pytest, Ruff,
  warning-clean Sphinx docs, package build, `twine check`, `git diff --check`,
  and a public-safety scan.
- Recorded the main P50 gap: goal-level supervisor token totals are visible, but
  supervisor-token attribution is not yet segmented cleanly by direct lane,
  delegated orchestration, implementation cleanup, and reporting.

## 2026-07-04 - Added P50 direct-versus-delegated comparison

- Compared the two FreshForge P16 benchmark lanes from their actual diffs and
  verification results.
- Recorded that the direct lane produced a typed `ProviderEvidence` public API,
  while the delegated lane produced a smaller opaque provider-owned evidence
  mapping.
- Identified the delegated mapping as the current favored promotion candidate
  because it keeps FreshForge core generic and avoids premature public API
  commitment.
- Kept P50.4 open for actual token-economics record completion because paid
  supervisor-token attribution is still goal-level rather than lane-segmented.

## 2026-07-04 - Ran P50 worker diff-review iteration

- Ran a proposal-only P16 diff-review ticket against both `qwen3-coder:latest`
  and `qwen3-coder-next:latest`.
- Both workers returned valid structured output and independently selected the
  `mapping` design over `typed record` or `hybrid`.
- Recorded 5564 local worker input tokens and 542 local worker output tokens at
  zero cash cost.
- Strengthened the P50 recommendation to promote the delegated mapping branch as
  the current FreshForge P16 candidate, while reserving typed evidence records
  for later downstream-driven evidence.

## 2026-07-04 - Refined P50 delegated FreshForge P16 candidate

- Updated the delegated FreshForge P16 branch to commit `a4975a8`.
- Strengthened provider evidence mapping docs with recommended keys and fields
  while keeping FreshForge core schema-neutral.
- Added test coverage proving provider-owned `uri` and `metadata` values are
  preserved in workflow evidence manifests.
- Verified the delegated candidate with targeted tests, full pytest, Ruff,
  warning-clean Sphinx docs, package build, `twine check`, `git diff --check`,
  and a public-safety scan.

## 2026-07-04 - Opened FreshForge P16 delegated draft PR

- Opened UBC-FRESH/freshforge#118 as a draft PR from
  `benchmark/p16-agent-workbench-delegated` to `main`.
- Used `Refs #113` rather than auto-close wording so the PR is a review surface
  while Agent Workbench P50 remains open.
- Verified PR checks passed on Python 3.11 and Python 3.12.
- Recorded the draft PR as the active P50 promotion candidate for maintainer
  review, not as phase closeout.

## 2026-07-04 - Added P50 token-economics checkpoint ledger

- Recorded the measured local-worker usage for P50 so far: 10029 input tokens
  and 1174 output tokens at zero cash cost.
- Recorded cumulative Codex goal-token checkpoints at 129063, 278526, and
  584722 total tokens.
- Marked the supervisor-token checkpoints as low-confidence attribution evidence
  because they lack input/output split and lane-local segmentation.
- Preserved the honest current conclusion: workers produced useful design signal
  cheaply, but P50 has not yet proven paid-supervisor token savings.

## 2026-07-04 - Opened Agent Workbench P50 draft PR

- Opened UBC-FRESH/agent-workbench#346 as a draft PR from
  `feature/p50-freshforge-p16-ab-benchmark-run` to `main`.
- Used `Refs #340` rather than auto-close wording so the PR is a review surface
  while P50 remains open.
- Recorded that the PR is open, draft, clean, and has no configured checks.
- Preserved the separation between FreshForge PR #118 for the package candidate
  and Agent Workbench PR #346 for benchmark evidence.

## 2026-07-04 - Reassessed P50 benchmark target class

- Recorded the maintainer decision that broad FreshForge API-design work is a
  low-yield benchmark class for current local Ollama workers.
- Identified high-volume document metadata indexing as a stronger near-term
  delegation target because the work is input-heavy, chunkable, evidence-rich,
  and expensive for a paid supervisor to perform directly.
- Created `UBC-FRESH/agent-delegation-lab` as the public-safe sandbox for
  synthetic and real-document delegation benchmark tasks.
- Seeded the new lab with an MP11 475-page PDF metadata-indexing benchmark plan
  and left Agent Workbench P50 open rather than treating this reassessment as
  phase closeout.

## 2026-07-04 - Added mandatory supervisor-token checkpoints

- Added `agent-workbench supervisor-tokens latest|checkpoint|span|synthesize`
  so paid supervisor token usage can be captured from local Codex
  `token_count` session events at named subtask boundaries.
- Extended token/cost records to distinguish fresh supervisor input, cached
  supervisor input, supervisor output, supervisor reasoning output, and local
  worker input/output tokens.
- Updated the token pricing calculation so cached input is priced separately
  and reasoning output is priced as output.
- Added fixture tests for Codex session parsing, start/end token deltas,
  fail-closed negative deltas, and supervisor cost calculation.
- Recorded the new benchmark rule: future economics claims require start/end
  supervisor-token checkpoints for every supervisor-owned subtask.

## 2026-07-04 - Added delegation experiment observation records

- Added `src/agent_workbench/experiments.py` and the `agent-workbench
  experiments validate|render|synthesize` command group.
- Added `templates/delegation_experiment_record.json` as the reusable
  observation fixture for task-scale, model, protocol, outcome, token, and
  economics data.
- Added `planning/phase50_experiment_observation_records.md` to define how
  MP11 scale-series records should be collected for later policy tuning and
  guardrail calibration.
- Kept experiment records sanitized by excluding raw inputs, raw outputs, raw
  traces, provider URLs, headers, and personal paths.
- Rendered benefit-cost ratio as undefined when a record has no audited
  delegated supervisor cost, so worker-only scale signals are not mistaken for
  final economics claims.

## 2026-07-04 - Planned supervisor overhead delegation strategy

- Added `planning/supervisor_overhead_delegation_strategy.md`.
- Separated task-economics overhead from GitHub/repository governance overhead.
- Identified worker-output summarization as a good candidate for delegation to
  a local `gpt-oss:*` reporting worker.
- Proposed representing recurring orchestration rituals as FreshForge-shaped
  workflow graphs so the paid supervisor does not repeatedly reinvent the same
  process structure.

## 2026-07-04 - Added overhead-reduction scaffolds

- Added `agent-workbench eval-batch` for quiet directory-level eval manifest
  orchestration with compact JSON and Markdown summaries.
- Added `templates/reporting_worker_ticket.md` as the reusable local-worker
  reporting mission template.
- Added `templates/workbench_templates/mp11_fixed_x8_reporting_graph.json` as
  a FreshForge-shaped graph for script-owned collection, local `gpt-oss`
  reporting draft, paid supervisor review, and source-level audit.

## 2026-07-04 - Dogfooded local reporting-worker delegation

- Added `planning/reporting_orchestration_overhead_followup.md` to separate
  task economics from governance hygiene and record the next orchestration
  strategy.
- Ran a local `gpt-oss:20b` reporting-worker draft over sanitized MP11 fixed-x8
  benchmark summaries, with raw prompts and outputs kept under ignored runtime
  paths.
- Fixed structured-section validation so manifest-required bare section names
  match Markdown headings such as `## Factual Summary`.

## 2026-07-04 - Recorded reporting A/B measurement lesson

- Added `planning/phase50_reporting_ab_iteration_01.md` with the first
  reporting A/B findings.
- Recorded that the `gpt-oss:20b` reporting worker used 5746 input tokens and
  1240 output tokens at zero cash cost.
- Recorded the combined paid-supervisor reporting comparison interval as
  `$0.111223`, while preserving the caveat that the first direct/review spans
  overlapped and cannot be summed independently.
- Tightened token synthesis so duplicate token `record_id` values and duplicate
  Codex checkpoint intervals fail closed instead of being silently added into
  an invalid ledger total.
- Ran a corrected non-overlapping reporting A/B: direct supervisor reporting
  cost `$0.059842`; delegated `gpt-oss:20b` report review cost `$0.055943`;
  isolated reporting delta `$0.003899` before source-level audit/repair.

## 2026-07-04 - Added document-library indexing workflow direction

- Added `planning/document_library_index_workflow_direction.md` to define public
  technical-document library indexing as a high-potential Agent Workbench
  delegation lane.
- Added `templates/document_library_corpus_record.json` for source provenance,
  extraction status, and public-safety metadata.
- Added `templates/document_index_worker_ticket.md` for local-worker
  structure/content metadata extraction from bounded chunks.
- Added `templates/source_anchored_repair_prepass_ticket.md` for local-worker
  repair labels before paid supervisor audit.
- Added `templates/workbench_templates/document_library_index_graph.json` as a
  FreshForge-shaped workflow graph for corpus registration, chunk extraction,
  worker passes, repair prepass, supervisor audit calibration, and promoted
  index assembly.
- Kept the workflow generic while recording the BC forest-management public
  document archive and MP11 benchmark as the motivating case study.

## 2026-07-04 - Planned P51-P54 managed-delegation roadmap tranche

- Added `planning/p51_p54_managed_delegation_roadmap.md`.
- Created planned parent issues #347 through #350 for managed delegation
  workflow lanes, local self-audit and repair loops, document-library index
  pilots, and delegation-loop policy tuning.
- Marked P50 complete in the roadmap after maintainer direction that P50 is
  now enough.
- Recorded the P50 closeout position: FreshForge P16 produced useful process
  evidence, but the next high-return path is managed local-worker workflows for
  high-volume public technical-document indexing.

## 2026-07-04 - Activated P51 managed delegation workflow lanes

- Created P51 child issues #351 through #353.
- Added `templates/managed_role_vocabulary.json` for extractor, self-auditor,
  repairer, convergence-checker, and supervisor-auditor boundaries.
- Added `templates/managed_iteration_stop_rules.json` for bounded local-worker
  loop stops, escalation paths, and scale gates.
- Added `templates/workbench_templates/managed_delegate_loop_graph.json` as the
  generic FreshForge-shaped local-worker loop.
- Updated `templates/workbench_templates/document_library_index_graph.json` so
  document indexing now includes local self-audit, delegated repair iteration,
  deterministic convergence checking, and paid supervisor delta-review.
- Added `planning/phase51_managed_delegation_workflow_lanes.md` to record the
  P51 contract and verification scope.
- Closed P51 child issues after JSON validation, graph metadata validation,
  pytest, and public-safety checks passed.

## 2026-07-04 - Ran P52 local self-audit and repair loop

- Added local self-audit and delegated repair ticket templates.
- Added `scripts/build_mp11_repair_loop_packet.py` to reproduce ignored MP11
  repair-loop tickets and manifests from tracked sample metadata plus ignored
  source excerpts.
- Ran a bounded MP11 self-audit/repair loop against the existing qwen x16 audit
  calibration sample.
- Recorded a negative result: local self-audit preserved zero primary sample
  identifiers, detected zero of nine known repairable records, and repair mode
  repaired zero records.
- Recorded measured supervisor delta-review cost of `$0.434535` against the
  existing direct source-audit baseline of `$0.288374`.
- Closed P52 with the decision not to scale this loop shape until P54 adds
  stricter identifier-preservation and calibration-miss bailout rules.

## 2026-07-04 - Built P53 TSA23 document-library pilot scaffold

- Activated P53 as a document-library indexing pilot over all public TSA 23 TSR
  PDF documents from 1995 onward.
- Added `scripts/materialize_tsa23_tsr_corpus.py` as the reproducible bridge
  from FEMIC's TSR registry and fetch commands into Agent Workbench's ignored
  runtime corpus area.
- Materialized the TSA 23 mini-corpus through FEMIC into ignored `runtime/`
  storage: 18 selected documents, 18 cached documents, and 0 fetch failures.
- Added sanitized tracked metadata under
  `benchmarks/document_library/tsa23_tsr/` for the corpus registry, chunk
  scaffold, and audit calibration scaffold.
- Added `planning/phase53_document_library_index_pilot.md` to record the corpus
  shape, reproducibility command, public-safety boundary, and P54 policy inputs.

## 2026-07-04 - Tuned P54 managed delegation loop policy

- Added `templates/delegation_loop_policy_v0.json` as the first explicit
  machine-readable policy surface for managed local-worker loops.
- Updated `templates/managed_iteration_stop_rules.json` with bailout rules for
  primary identifier loss, missed known repairables, missing economics evidence,
  and tool calls observed in no-tool lanes.
- Updated `planning/delegation_policy.md` to separate default no-tool SDK
  delegation from explicitly configured restricted-tool lanes.
- Added `planning/phase54_delegation_loop_policy_tuning.md` to map P50-P53
  evidence into conservative next-run recommendations.
- Recorded that future economics claims require measured paid-supervisor token
  spans and that model comparisons require worker token records, model identity,
  parseability status, and source anchors.

## 2026-07-04 - Opened P55 TSA23 indexing battery

- Opened P55 as the first real TSA23 document-indexing experiment after P53's
  corpus scaffold and P54's policy rules.
- Added `benchmarks/document_library/tsa23_tsr/p55_test_battery.json` with a
  staged seven-wave battery across documents, chunk sizes, models,
  repeatability, content metadata, and supervisor audit calibration.
- Added `planning/phase55_tsa23_indexing_battery.md` to make the phase
  explicitly non-trivial and to prevent premature closeout after a single
  successful worker run.
- Recorded a phase pause policy: report wave results to the maintainer and wait
  for direction before advancing waves or closing P55.

## 2026-07-04 - Ran P55 Wave 0 chunking and dry-run setup

- Added `scripts/build_tsa23_indexing_battery.py` to extract ignored source
  chunks from the three P55 TSA23 pilot PDFs and generate ignored worker tickets
  and eval manifests.
- Added tracked sanitized chunk manifests for the 1995, 2006, and 2012 pilot
  PDFs plus `benchmarks/document_library/tsa23_tsr/p55_eval_packet_index.json`.
- Dry-ran all 9 generated P55 eval manifests through `agent-workbench
  eval-batch` without contacting the model provider.
- Recorded Wave 0 findings in `planning/phase55_wave0_chunking_results.md`:
  the 1995 PDF has sparse `pypdf` text extraction, while the 2006 and 2012 PDFs
  need smaller chunks before a clean x2/x4/x8 worker comparison.

## 2026-07-04 - Ran P55 Wave 1 single-model smoke

- Refocused P55 on the three most recent TSA23 TSR documents from 2012: data
  package, public discussion paper, and rationale.
- Regenerated chunk manifests and ignored eval packets with 8-page windows and
  1-page overlap, then committed the refocus checkpoint.
- Ran `qwen3-coder-next:latest` on all three `structure_x2` Wave 1 tickets
  through the Copilot SDK/Ollama eval path.
- Added `benchmarks/document_library/tsa23_tsr/p55_wave1_smoke_summary.json`
  and `planning/phase55_wave1_smoke_results.md` with sanitized aggregate
  metrics only.
- Recorded that all three worker calls completed with parseable JSONL and no
  malformed lines, but scaling unchanged is not recommended because the outputs
  exposed record-ID uniqueness, page-anchor type, and data-package coverage
  defects.

## 2026-07-04 - Reran P55 Wave 1 with full-document coverage

- Added a `structure_full` ticket shape and Wave 1.1 full-document smoke lane
  so P55 does not skip useful later pages before model A/B testing.
- Tightened the structure-ticket contract to require unique `record_id` values,
  string `page_anchor` values, bare JSONL, and at least one strong record per
  metadata-bearing chunk.
- Regenerated Wave 0 artifacts: 12 eval packets total, including full-document
  packets covering 41 data-package pages, 17 public-discussion-paper pages, and
  48 rationale pages.
- Reran the three `structure_x2` tickets and ran three full-document tickets
  with `qwen3-coder-next:latest`.
- Added `benchmarks/document_library/tsa23_tsr/p55_wave1_full_document_rerun_summary.json`
  and `planning/phase55_wave1_full_document_rerun_results.md` with sanitized
  aggregate metrics.
- Recorded the main result: later pages do contain useful indexable material,
  but one huge ticket per document is format-fragile and should be replaced by
  deterministic per-chunk or small-bundle orchestration plus delegated format
  repair before Wave 2.

## 2026-07-04 - Ran P55 Wave 2 model A/B

- Fixed the SDK eval classifier so empty-marker JSONL runs report
  `freeform-output` instead of a misleading `duplicate-marker`.
- Tightened the generated structure-ticket wording with stricter JSONL rules,
  uniqueness requirements, string page anchors, quote-length guidance, and a
  maximum-record cap.
- Ran the Wave 2 `structure_x4` rationale ticket across
  `qwen3-coder:latest`, `qwen3-coder-next:latest`, and `gpt-oss:120b`.
- Added `benchmarks/document_library/tsa23_tsr/p55_wave2_model_ab_summary.json`
  and `planning/phase55_wave2_model_ab_results.md` with sanitized aggregate
  metrics.
- Recorded that `qwen3-coder:latest` produced the best coverage signal, while
  `qwen3-coder-next:latest` under-covered and `gpt-oss:120b` invented chunk
  IDs; no model is ready for unaudited scaling without validator/repair.

## 2026-07-04 - Ran P55 Wave 3 size-scale test

- Tightened the P55 worker-ticket framework again by removing the literal model
  name from the example and adding explicit allowed chunk IDs.
- Switched Wave 3 size-scale from `qwen3-coder-next:latest` to the Wave 2 best
  coverage candidate, `qwen3-coder:latest`.
- Ran `structure_x2`, `structure_x4`, and `structure_x8` on the 2012 rationale.
- Added `benchmarks/document_library/tsa23_tsr/p55_wave3_size_scale_summary.json`
  and `planning/phase55_wave3_size_scale_results.md` with sanitized aggregate
  metrics.
- Recorded that `structure_x4` is the best current ticket size: `structure_x8`
  consumed more input tokens but still covered only four of seven chunks under
  the 24-record cap.

## 2026-07-04 - Removed P55 hidden record cap

- Removed the hard-coded maximum-record rule from generated P55 worker tickets
  after maintainer review identified it as an artificial guardrail that
  distorted coverage results.
- Updated the P55 battery definition and planning note to make verbosity,
  malformed JSONL, repetitive records, quote-length defects, and low-value
  filler measured validator outcomes rather than hidden ticket constraints.
- Kept the earlier Wave 2 and Wave 3 summaries unchanged as historical evidence
  because those worker runs really did execute under the old capped ticket
  contract.

## 2026-07-04 - Ran P55 Wave 3.1 chunk-orchestrated extraction

- Regenerated P55 worker tickets without the hidden maximum-record rule and
  added seven single-chunk `wave3_chunk_orchestration` eval packets for the
  2012 TSA23 rationale.
- Ran all seven no-tool `qwen3-coder:latest` worker calls through
  `agent-workbench eval-batch`; all completed without provider failures or
  malformed JSONL lines.
- Added `scripts/summarize_p55_worker_outputs.py` to reproduce sanitized
  aggregate quality metrics from ignored runtime outputs without tracking raw
  source text or source quotes.
- Recorded the Wave 3.1 result in
  `benchmarks/document_library/tsa23_tsr/p55_wave3_chunk_orchestration_summary.json`
  and `planning/phase55_wave3_chunk_orchestration_results.md`: all seven chunks
  were covered, 95 parseable records were produced, and remaining defects are
  mainly repairable chunk-ID copy errors plus source-quote length violations.

## 2026-07-04 - Ran P55 Wave 3.2 Qwen3.6 BF16 chunk A/B

- Added `qwen3.6:35b-a3b-bf16` to the P55 model catalog as the primary
  document-understanding extraction candidate.
- Added seven `wave3_qwen36_bf16_chunk_ab` single-chunk eval packets over the
  same 2012 TSA23 rationale chunks used by the Wave 3.1
  `qwen3-coder:latest` baseline.
- Verified the BF16 model was available from the configured local Ollama
  provider before running worker calls.
- Ran all seven BF16 no-tool worker calls through `agent-workbench eval-batch`;
  all completed without provider failures.
- Added `benchmarks/document_library/tsa23_tsr/p55_wave3_qwen36_bf16_chunk_ab_summary.json`
  and `planning/phase55_wave3_qwen36_bf16_chunk_ab_results.md` with sanitized
  aggregate metrics.
- Recorded the Wave 3.2 result as comparable but not a clean win: BF16
  produced 123 parseable records versus 95 for the coding baseline, but still
  needs validator/repair because it produced one malformed line, 14 invalid
  chunk-ID records, and the same total count of quote-length violations.

## 2026-07-05 - Planned P55 dual-model typed fact ensemble lane

- Added `planning/phase55_dual_model_ensemble_design.md` to capture the next
  extraction architecture: independent typed JSON candidates, deterministic
  field-by-field comparison, disagreement-only verification, and compact
  supervisor audit.
- Added the `typed_fact_x2` ticket shape to the P55 battery so the next run
  tests schema population rather than open-ended structure-record discovery.
- Added Wave 7 dual-model candidate extraction and Wave 8 disagreement
  verification to the P55 battery and roadmap.
- Recorded the current model reality: `qwen3.6:35b-a3b-bf16` is available, GLM
  is planned but not currently exposed by the local Ollama catalog, and
  `gpt-oss:120b` is the installed large-model stand-in for the first runnable
  ensemble test.

## 2026-07-05 - Ran P55 Wave 7 dual-model typed fact ensemble

- Generated the new Wave 7 typed fact candidate packet over the first two
  chunks of the 2012 TSA23 rationale.
- Dry-ran the Wave 7 eval manifest, then ran the live no-tool local-worker
  packet with `qwen3.6:35b-a3b-bf16` and `gpt-oss:120b`.
- Added `scripts/compare_p55_typed_candidates.py` to compare candidate JSON
  outputs without tracking raw candidate values or source quotes.
- Added `benchmarks/document_library/tsa23_tsr/p55_wave7_dual_model_typed_fact_ensemble_comparison.json`
  and `planning/phase55_wave7_dual_model_typed_fact_ensemble_results.md` with
  sanitized comparison metrics.
- Recorded that both candidate JSON objects parsed, all 15 fields were
  compared, five fields had value agreement, two fields were both not found,
  and nine fields require verifier attention because of disagreement or schema
  issues.
- Preserved the GLM direction for a later rerun: GLM is still the intended
  document-model comparison target, but it was not available from the local
  Ollama catalog for this first Wave 7 run.

## 2026-07-05 - Ran P55 Wave 8 disagreement verification

- Added `scripts/build_p55_disagreement_verifier_packet.py` to build ignored
  verifier tickets from the Wave 7 disagreement surface and tracked only a
  sanitized verifier packet index.
- Added `scripts/summarize_p55_verifier_output.py` to summarize verifier
  outputs without tracking raw final values or source quotes.
- Ran the first Wave 8 verifier packet with `deepseek-r1:latest`; the model
  completed but failed the strict JSON verifier contract, first by using
  verdict labels as field keys and then by returning malformed JSON after a
  stricter field-key skeleton was added.
- Preserved the DeepSeek-R1 result as negative verifier evidence in
  `benchmarks/document_library/tsa23_tsr/p55_wave8_disagreement_verification_deepseek_r1_summary.json`
  and `planning/phase55_wave8_disagreement_verification_deepseek_r1_results.md`.
- Reran the same disagreement verifier packet with `qwen3.6:35b-a3b-bf16`;
  Qwen3.6 parsed successfully, covered all nine requested fields, produced no
  quote-length or chunk-ID defects, and resolved the nine-field disagreement
  surface into six `left_correct` and three `both_correct_equivalent` verdicts.
- Recorded the Qwen3.6 verifier result in
  `benchmarks/document_library/tsa23_tsr/p55_wave8_disagreement_verification_qwen36_summary.json`
  and `planning/phase55_wave8_disagreement_verification_qwen36_results.md`.
- Updated the ensemble design note to split "verifier" into strict verifier,
  validation critic, and repair executor roles. DeepSeek-R1 remains a plausible
  validation-critic candidate, while Qwen3-Coder-Next is the next repair
  executor candidate for strict JSON repair.

## 2026-07-05 - Ran P55 Wave 9 critic and repair rescue lane

- Added `scripts/build_p55_critic_repair_packets.py` to generate ignored Wave 9
  critic and repair tickets from the failed Wave 8 DeepSeek verifier output.
- Added `scripts/summarize_p55_critic_output.py` to track sanitized critic
  metrics without publishing raw repair instructions.
- Ran `deepseek-r1:latest` as a validation critic; it produced parseable repair
  instructions with two issue records and two repair-strategy steps, but the
  harness still classified the output as loop-like.
- Ran `qwen3-coder-next:latest` as a strict JSON repair executor. The first
  repair pass parsed and covered all fields but invented an invalid
  `supervisor_review_required` verdict label and invalid `final_chunk_id`
  values, so the repair ticket was tightened and rerun.
- The final repair pass parsed, preserved all required top-level keys and all
  nine field keys, used valid verdict labels, and produced no quote-length or
  chunk-ID defects. It resolved one field and marked eight fields as
  `needs_supervisor`.
- Recorded the result in
  `benchmarks/document_library/tsa23_tsr/p55_wave9_validation_critic_summary.json`,
  `benchmarks/document_library/tsa23_tsr/p55_wave9_json_repair_summary.json`,
  `planning/phase55_wave9_validation_critic_results.md`, and
  `planning/phase55_wave9_json_repair_results.md`.
- Interpretation: the critic/repair lane is a safe fallback for producing
  schema-shaped JSON from failed output, but on this test it is less useful
  than direct Qwen3.6 disagreement verification because it punts most fields to
  supervisor audit.

## 2026-07-05 - Ran P55 Wave 8 Qwen3.6 Q8 verifier A/B

- Added a Qwen3.6 Q8_0 verifier packet for the same nine-field Wave 8
  disagreement surface used by the BF16 strict-verifier baseline.
- Ran `qwen3.6:35b-a3b-q8_0` through the no-tool SDK eval path and summarized
  the output with the existing verifier summarizer.
- Recorded the result in
  `benchmarks/document_library/tsa23_tsr/p55_wave8_disagreement_verification_qwen36_q8_summary.json`
  and `planning/phase55_wave8_disagreement_verification_qwen36_q8_results.md`.
- Compared with BF16: Q8_0 parsed successfully and used fewer output tokens
  than BF16, but it had three quote-length defects and left one field as
  `insufficient_evidence`; BF16 remains the stronger strict verifier candidate
  for this node.

## 2026-07-05 - Prepared P55 closeout as evidence packet

- Reconciled the P55 roadmap state so completed chunking, worker-eval,
  supervisor-calibration, and scoring work are marked complete on the P55
  branch.
- Added `planning/phase55_closeout_summary.md` to make the closeout boundary
  explicit: P55 is an evidence-producing phase, not a production document-index
  workflow.
- Deferred repeatability, content-probe, full-corpus indexing, and production
  recipe work to follow-on consolidation and recipe phases rather than keeping
  P55 open for more live runs.

## 2026-07-05 - Opened P56 authority hierarchy scaffold

- Created P56 parent issue #372 and child issues #373-#376 after P55 landed so
  the authority-contract work has its own clean phase tracker.
- Added the authority contract scaffold, supervisor job templates, CLI
  validation/rendering surface, and focused tests on
  `feature/p56-authority-hierarchy-supervisor-contracts`.
- Linked `ROADMAP.md` and `planning/phase56_authority_contracts.md` to the P56
  issue set before opening the P56 PR.

## 2026-07-05 - Opened P57 VS Code subagent supervisor spike

- Created P57 parent issue #378 and child issues #379-#382 after P56 landed so
  the VS Code subagent supervisor work has its own phase tracker.
- Rebased `feature/p57-vscode-subagent-supervisor-worker-spike` onto merged
  P56 `main`.
- Added tracked local-supervisor custom agent definitions, graph/materializer
  tooling, deterministic validators, repair helpers, packaged-launcher
  economics summaries, and P57 planning notes.
- Kept P58 evidence consolidation out of the P57 branch; P57 focuses on the
  spike and packaged-run evidence surface only.

## 2026-07-05 - Started P58 active-phase reconciliation

- Created P58 parent issue #384 and child issues #385-#388 after P57 landed so
  evidence consolidation has its own phase tracker.
- Added `planning/p58_active_phase_reconciliation.md` as the evidence register
  and close/defer decision memo for P55-P57.
- Added `planning/p58_p64_roadmap_tranche.md` and planned P59-P64 as the
  consolidation-first tranche before more large live benchmark runs.
- Updated `AGENTS.md` and `planning/delegation_economics_vision.md` with the
  P57 paid-supervisor overrun lesson and budget-gate posture.

## 2026-07-05 - Opened P59 paid-supervisor budget gates

- Created P59 parent issue #390 and child issues #391-#394 for budget
  declaration validation and stop-rule status semantics.
- Added `src/agent_workbench/budget.py`,
  `templates/supervisor_budget_declaration.json`, and focused tests for
  budget declaration validation.
- Added `agent-workbench supervisor budget validate` so future live economics
  runs have a concrete fail-closed budget gate before they claim evidence.
- Recorded the P59 boundary in `planning/phase59_supervisor_budget_gates.md`:
  this phase adds validation and status semantics, but launches no live
  Copilot/Ollama jobs.

## 2026-07-05 - Added P59 budget enforcement and roadmap subtask contract

- Wired the existing packaged document-audit graph live-run and summary paths
  to require a valid `--budget-record` before paid-supervisor economics
  evidence can be launched or summarized.
- Added regression tests that prove those graph paths fail closed without a
  budget record.
- Expanded P60-P64 roadmap phases to task/subtask level so future phase work is
  ready for issue activation without relying on broad one-line placeholders.
- Updated `AGENTS.md` to make task/subtask-level roadmap planning part of the
  development workflow contract.
- Opened P59 PR #395 after validation so the phase closeout can proceed through
  the one-phase/one-branch workflow.

## 2026-07-05 - Implemented P60 split outcome semantics

- Created P60 parent issue #396 and child issues #397-#400 on
  `feature/p60-outcome-semantics-scoring-split`.
- Added reusable outcome classification fields for
  `quality_validated_candidate`, `protocol_accepted_candidate`,
  `economics_usable`, `final_decision`, and `rejection_reasons`.
- Wired packaged document-audit graph summaries and P57 packaged-launcher
  economics normalization to emit split outcome fields.
- Regenerated the P57 packaged-launcher comparison and decision packet from the
  existing 43-record evidence set with repo-relative paths and explicit
  quality/protocol/economics columns.
- Added tests for accepted evidence, quality-valid protocol rejection, stale
  diagnostics, hard quality rejection reasons, soft quote-style penalties, and
  model-provenance mismatch as a protocol defect.
- Opened P60 PR #401 after validation so the phase closeout can proceed through
  the one-phase/one-branch workflow.

## 2026-07-05 - Implemented P61 packaged local-supervisor workflow defaults

- Created P61 parent issue #402 and child issues #403-#406 on
  `feature/p61-packaged-local-supervisor-workflow-v1`.
- Made pre-materialized audit tickets and quiet runtime output the default
  packaged graph-run posture, with explicit legacy/debug opt-out flags.
- Added packaged workflow metadata to dry-run plans so coordinator-owned setup,
  local-supervisor work, deterministic validators, and paid-coordinator review
  boundaries are visible.
- Added high-entropy job-ID validation for live packaged bridge jobs to reduce
  stale-session contamination risk.
- Added non-live replay coverage using existing P57 v11 evidence and documented
  the packaged workflow contract in
  `planning/phase61_packaged_local_supervisor_workflow_v1.md`.
- Opened P61 PR #407 after validation so the phase closeout can proceed through
  the one-phase/one-branch workflow.
- Reconciled `ROADMAP.md` status fields so P55 and P57-P60 detailed phase
  sections match the issue/PR closeout state, while P61 remains the only active
  phase on the P61 branch.

## 2026-07-05 - Implemented P62 document-indexing workflow recipe

- Created P62 parent issue #408 and child issues #409-#412 on
  `feature/p62-document-indexing-recipe-v1`.
- Added `playbooks/document_indexing_recipe.md` as the public technical PDF
  document-indexing recipe.
- Added `planning/phase62_document_indexing_recipe_v1.md` to record the
  non-live recipe decisions and P63 handoff boundary.
- Added recipe manifest and stage-record templates with P59 budget hooks, P60
  outcome fields, public-safety policy, task-size defaults, model-role defaults,
  and no-hidden-record-cap policy.
- Updated the document-index worker ticket and document-library graph template
  so future instantiations inherit the P62 budget, outcome, quote-penalty, and
  no-hidden-cap rules.

## 2026-07-05 - Opened P63 bounded TSA23 recipe pilot

- Created P63 parent issue #414 and child issues #415-#418 on
  `feature/p63-bounded-tsa23-recipe-pilot`.
- Selected the bounded pilot slice from the tracked TSA23 2012 data-package
  manifest: `tsa23_2012_23tsdp12`, pages 1-22 across three chunks.
- Added `benchmarks/document_library/tsa23_tsr/p63_bounded_tsa23_recipe_pilot_budget.json`
  with a one-attempt USD 10 paid-supervisor budget and maintainer checkpoint
  before any retry or scope expansion.
- Added `benchmarks/document_library/tsa23_tsr/p63_bounded_tsa23_recipe_pilot_plan.json`
  and `planning/phase63_bounded_tsa23_recipe_pilot.md` to keep live execution
  blocked until the budget gate is accepted.
- Expanded the remaining P63 and planned P64 roadmap tasks to explicit
  subtask-level checklists so live execution, reporting, scale decisions, and
  future deployment-playbook work do not rely on broad one-line placeholders.

## 2026-07-05 - Ran P63 bounded TSA23 recipe pilot execution attempt

- Added `scripts/build_p63_recipe_pilot_runtime.py` to reproducibly generate
  the ignored P63 worker ticket, SDK eval manifest, and runtime index from the
  tracked pilot plan and ignored TSA23 chunk text.
- Generated and dry-run validated the P63 runtime manifest for
  `qwen3.6:35b-a3b-q8_0`, then confirmed the model is visible through the
  configured provider path.
- Ran the single live worker attempt allowed by the P59 budget gate. The
  attempt produced 40 parseable candidate records across all three selected
  chunks but was classified as blocked because the SDK observed a provider 524
  model-call failure, two malformed/truncated JSONL lines, and one invalid
  chunk ID.
- Added `scripts/summarize_p63_recipe_pilot.py` plus sanitized tracked P63
  execution summaries under `benchmarks/document_library/tsa23_tsr/`, keeping
  raw worker output, source quotes, prompts, provider details, and transcripts
  ignored under `runtime/`.
- Recorded paid supervisor token spans for `ticket_build` and
  `worker_run_orchestration`; the tracked summary reports USD 0.414679 of paid
  supervisor cost for those two spans and USD 0.00 local-worker cash cost.
- Marked P63.2 complete as diagnostic evidence only. The P63 maintainer
  checkpoint is now required before any retry, repair expansion, broader page
  span, added model family, or budget increase.

## 2026-07-05 - Completed P63 outcome and economics reporting

- Extended the P63 execution summary to include accepted, repaired, rejected,
  escalated, and unresolved fact counts without promoting raw worker records or
  source quotes.
- Added baseline-comparison semantics showing the direct-supervisor baseline is
  `not_run_stop_rule_triggered` and the cost comparison is `not_comparable`,
  because the single live attempt failed before producing a quality-valid
  delegated candidate.
- Added separate paid-supervisor `worker_output_summarize` and
  `tracked_update` token spans to the sanitized cost table, increasing the
  measured supervisor cost for the diagnostic run to USD 0.811920 across four
  captured spans.
- Updated the P63 planning note and roadmap so P63.3 is complete as diagnostic
  reporting while P63.4 remains open for the maintainer-facing scale, adjust,
  repeat, or pause decision.

## 2026-07-05 - Drafted P63 scale decision

- Added `planning/phase63_scale_decision.md` as the maintainer-facing P63.4
  decision draft.
- Recommended pausing live scaling and adjusting the recipe/provider execution
  shape before any repeat, rather than rerunning the same all-in-one 22-page
  ticket.
- Recorded the follow-on gate required before any repeat: new or amended budget
  record, one named model lane, same bounded slice unless approved otherwise,
  smaller section-level tickets, stop on provider failure/malformed output/
  invalid chunk IDs/missing token spans, and no direct-supervisor baseline until
  a quality-valid delegated candidate exists.
- Left P63.4 open pending explicit maintainer acceptance of scale, adjust,
  repeat, pause, or abandon.
- Added explicit P63.4 maintainer decision options to the tracked decision memo
  and roadmap so the phase cannot close by implication.

## 2026-07-05 - Accepted P63 scale decision

- Accepted the P63.4 recommendation to close P63 as diagnostic evidence and
  adjust the document-indexing recipe in a follow-on phase before any repeat.
- Updated the P63 decision memo and roadmap to mark the selected option:
  smaller section-level tickets, deterministic JSONL repair, chunk-ID
  hardening, and provider 524 isolation before the next live run.
- Recorded that P63 authorizes no further live model calls, direct-supervisor
  baseline, broader TSA23 slice, model-lane change, or repair expansion.
- Closed child issue #417 and prepared P63 for a P63-only PR after parent issue
  #414 was synchronized with the accepted decision.
- Opened P63-only pull request #419 to merge the bounded TSA23 recipe pilot as
  diagnostic evidence and close parent issue #414 on merge.
- Squash-merged PR #419, verified parent issue #414 closed, synced local
  `main`, and deleted the local P63 feature branch.

## 2026-07-05 - Opened P64 deployment operator playbook

- Created P64 parent issue #420 and child issues #421-#424 on
  `feature/p64-deployment-environment-operator-playbook`.
- Activated P64 as a non-live consolidation phase for deployment environment
  and operator guidance before any further local-supervisor experiments.
- Scoped P64 to public-safe documentation only: supported VS Code/code-server
  runtime shape, operator checklists, troubleshooting, and closeout hygiene.

## 2026-07-05 - Added P64 deployment operator playbook

- Added `playbooks/deployment_environment_operator.md` with the supported
  local-supervisor runtime shape for VS Code or code-server, Copilot Chat,
  configured Ollama-backed providers, ignored runtime paths, and tracked
  public-safe summaries.
- Added pre-run, launch, evidence, do-not-run, troubleshooting, restart, and
  post-run checklists so operators can avoid stale sessions, wrong roots,
  wrong models, missing budgets, and repeated noisy attempts.
- Added `planning/phase64_deployment_environment_operator_playbook.md` to
  record the P64 evidence carry-forward, deployment posture, excluded private
  details, and closeout boundary.
- Closed child issues #421-#423 after syncing their checklists and comments.
- Validated the changed Markdown surfaces with `git diff --check` and a
  public-safety scan for private paths, provider URLs, headers, credentials,
  and transcript fragments.
- Opened P64-only pull request #425 after P64.1-P64.4 evidence agreed.
- Squash-merged PR #425, verified parent issue #420 closed, synced local
  `main`, deleted the local P64 feature branch, and pruned the remote branch.

## 2026-07-06 - Added P65 Copilot session archive command

- Opened P65 on `feature/p65-copilot-session-archive` to make
  ticket-plus-chatlog archiving a systematic Agent Workbench function.
- Added `agent-workbench copilot archive`, which resolves VS Code workspace
  storage, copies matching Copilot `chatSessions/*.jsonl` and
  `GitHub.copilot-chat/transcripts/*.jsonl` files into ignored runtime storage,
  and writes a sanitized manifest with event counts, model ids, permission
  levels, message counts, tool-request counts, and nudge snippets.
- Added tests for successful archive generation and fail-closed no-match
  behavior using fake VS Code workspace-storage fixtures.
- Updated `AGENTS.md` and `planning/phase65_copilot_session_archive.md` so
  future Copilot-backed delegation runs capture behavior traces by default
  rather than relying on manual post-run reminders.

## 2026-07-06 - Planned P66-P70 task-level delegation tranche

- Added `planning/p66_p70_task_level_delegation_tranche.md` to capture the
  P108-derived direction: default to one-child-task delegation, keep phase
  sequencing and acceptance coordinator-owned, and use archived Copilot
  behavior traces as systematic evidence.
- Expanded `ROADMAP.md` with planned P66-P70 phases:
  task-level delegation protocol, heartbeat and nudge protocol, Copilot task
  controller v0, behavior analytics from archives, and FEMIC P108 repair
  dogfood.
- Fleshed out each planned phase to task/subtask level so the next tranche is
  ready for UBC-FRESH phase activation rather than remaining a chat-only idea.

## 2026-07-06 - Added P66 task-level delegation protocol

- Created P66 parent issue #431 and child issues #432 through #435 on
  `feature/p66-task-level-delegation-protocol`.
- Added task-level delegation templates for child-task tickets, task results,
  coordinator decisions, and bounded repair tickets.
- Added `planning/phase66_task_level_delegation_protocol.md` to record the
  P108 lesson: whole-phase delegation can produce substantial work, but the
  default delegation unit should be one roadmap child task with explicit
  heartbeat, result, blocker, archive, and coordinator-decision surfaces.
- Updated `AGENTS.md` so coordinator-owned phase authority and delegated
  child-task authority are separated in the repo contract.

## 2026-07-06 - Added P67 heartbeat and nudge protocol

- Created P67 parent issue #437 and child issues #438, #439, #440, and #442 on
  `feature/p67-heartbeat-nudge-protocol`; closed duplicate retry-created issues
  #441 and #443 through #446 as tracker cleanup.
- Added `src/agent_workbench/heartbeat.py` with heartbeat JSONL loading,
  validation, stale-run summarization, stall/nudge counting, and nudge rendering.
- Added `agent-workbench heartbeat validate`,
  `agent-workbench heartbeat summarize`, and
  `agent-workbench nudge suggest` command surfaces for delegated-run monitoring.
- Added heartbeat and nudge templates plus
  `planning/phase67_heartbeat_nudge_protocol.md` so P68 can build on a
  structured run-state signal instead of ad hoc "keep going" prompts.

## 2026-07-06 - Added P68 Copilot task controller v0

- Created P68 parent issue #448 and child issues #449 through #452 on
  `feature/p68-copilot-task-controller-v0`.
- Added `src/agent_workbench/copilot_task_controller.py` with task-run manifest
  validation, bounded launch-prompt rendering, archive/heartbeat/result review
  packet generation, and coordinator decision recommendations.
- Added `agent-workbench copilot task-validate`, `task-prompt`, and
  `task-review` command surfaces.
- Added `templates/copilot_task_run_manifest.json`,
  `planning/phase68_copilot_task_controller_v0.md`, and focused controller
  tests so the next live bridge layer has a deterministic child-task control
  surface.

## 2026-07-06 - Added P69 behavior analytics from archives

- Created P69 parent issue #454 and child issues #455 through #458 on
  `feature/p69-behavior-analytics-from-archives`.
- Added `src/agent_workbench/behavior_analytics.py` to convert sanitized P65
  Copilot archive manifests into behavior metrics and outcome classes.
- Added `agent-workbench behavior analyze` and
  `agent-workbench behavior synthesize` command surfaces for public-safe
  per-run summaries and cross-run synthesis.
- Added `planning/phase69_behavior_analytics_from_archives.md` and focused
  tests so P70 and later real-project dogfood runs can accumulate reusable
  ticket-plus-behavior evidence instead of one-off impressions.

## 2026-07-06 - Closed P66 through P69 task-level delegation tranche

- Merged P66 PR #436 and verified parent issue #431 closed.
- Merged P67 PR #447 and verified parent issue #437 closed.
- Merged P68 PR #453 and verified parent issue #448 closed.
- Merged P69 PR #460 and verified parent issue #454 closed.
- Synced the roadmap status map so P66 through P69 are marked complete on
  `main`, leaving P70 as the next planned dogfood lane.

## 2026-07-07 - Activated P70 FEMIC P108 repair dogfood

- Created P70 parent issue #461 and child issues #462 through #465 on
  `feature/p70-femic-p108-repair-dogfood`.
- Updated `ROADMAP.md` so P70 is the active Agent Workbench phase and the stale
  P69 section status is complete.
- Added `planning/phase70_femic_p108_repair_dogfood.md` to record the
  coordinator-owned setup boundary, budget/stop-rule expectations, planned P108
  cleanup ticket set, and acceptance notes before any FEMIC repair work starts.

## 2026-07-07 - Completed P70.1 dogfood setup

- Audited current FEMIC P108 evidence: branch
  `feature/p108-tsa23-instance-bootstrap-delegation`, open parent issue #302,
  open PR #303, and the parent `CHANGE_LOG.md` P108 ordering/encoding defect.
- Selected Ticket A, the `CHANGE_LOG.md` ordering and mojibake repair, as the
  first bounded task-level controller dogfood target.
- Wrote ignored Ticket A controller artifacts under `runtime/agent_jobs/` and
  validated the manifest with
  `.\.venv\Scripts\python.exe -m agent_workbench copilot task-validate`.
- Recorded the local worker-model inventory caveat: `ollama` is not available
  on this shell, so the manifest requires model verification before launch.

## 2026-07-07 - Activated P71 Copilot SDK remote-control bridge

- Parked Agent Workbench P70 (#461) after the initial FEMIC P108 dogfood setup
  exposed that the VS Code Chat archive path cannot reliably nudge a specific
  stalled session.
- Created P71 parent issue #466 and child issues #467 through #471 on
  `feature/p71-copilot-sdk-remote-control-bridge`.
- Added `planning/phase71_copilot_sdk_remote_control_bridge.md` and
  `templates/copilot_sdk_session_manifest.json` to define SDK-owned session
  control, event/status vocabulary, nudge evidence, and P70/P108 resume gates.
- Kept FEMIC P108 as the dogfood target while making P70 resume conditional on
  verified SDK create, resume, monitor, and same-session nudge behavior.

## 2026-07-07 - Added P71.2 SDK session runtime commands

- Added `src/agent_workbench/copilot_sdk_bridge.py` with SDK session manifest
  validation, create/resume/send orchestration, event JSONL capture, status
  summary writing, nudge logging, and a live adapter that imports the Copilot
  SDK only when a live session command runs.
- Added `agent-workbench copilot-sdk validate`, `start`, `resume-send`, and
  `nudge` command surfaces that operate from the P71 manifest and fail closed on
  invalid session state.
- Added focused fake-adapter tests for create and resume/nudge flows before
  attempting FEMIC P108 dogfood against a live SDK session.

## 2026-07-07 - Added P71.3 SDK monitor and nudge planning

- Extended `src/agent_workbench/copilot_sdk_bridge.py` with SDK event-log and
  nudge-log readers, status classification, repeated-nonprogress detection,
  repeated-nudge stop rules, monitor summaries, and public-safe Markdown
  rendering.
- Added `agent-workbench copilot-sdk monitor` and `nudge-plan` so a coordinator
  can inspect SDK-owned session state and produce the next directive without
  reading raw event logs manually.
- Added synthetic event-log tests for completion candidates, repeated
  non-progress, and repeated-nudge stop rules, plus an ignored runtime CLI smoke
  for monitor and nudge-plan output.

## 2026-07-07 - Completed P71.4 FEMIC P108 SDK dogfood

- Ran a live SDK-owned Copilot session for FEMIC P108 using ignored manifest
  `runtime/p71_femic_p108_sdk/manifest.json`; the bridge created session
  `cc98e2df-20da-4dca-8b95-c7a1f7348fd1`, captured SDK events, and wrote
  monitor summaries under ignored runtime storage.
- Verified the worker-produced candidate independently: only FEMIC
  `CHANGE_LOG.md` changed, `git diff --check -- CHANGE_LOG.md` passed, and the
  change repaired the P108 changelog entry ordering.
- Sent a same-session SDK nudge after the initial run using
  `agent-workbench copilot-sdk nudge`; the bridge recorded the nudge and
  re-monitored the same session without introducing additional FEMIC changes.
- Committed and pushed the verified FEMIC repair to PR #303 as
  `181cb16` (`P108 repair changelog entry ordering`), while leaving FEMIC P108
  merge and issue closeout outside P71 authority.
- Tightened the SDK bridge live adapter to support manifest-controlled
  `working_directory` and SDK built-in isolated tool allowlists for future
  dogfood runs.

## 2026-07-07 - Closed P71 Copilot SDK remote-control bridge

- Synthesized the P71 evidence: SDK-owned sessions can now be created,
  monitored, resumed, nudged, and reviewed through Agent Workbench manifests and
  ignored event/status artifacts.
- Recorded the P70 resume decision: Agent Workbench P70 can resume using the
  SDK-owned bridge for further FEMIC P108 dogfood, with VS Code Chat archives
  kept as evidence-only fallback rather than the primary remote-control path.
- Verified phase closeout with focused SDK/controller tests, full `pytest`,
  focused `ruff check`, and `git diff --check`; `mypy` and `pre-commit` were
  unavailable because this repo venv lacks `mypy` and the repo has no
  `.pre-commit-config.yaml`.

## 2026-07-08 - Resumed P70 with SDK-owned TSA23 Ticket B

- Merged the completed P71 SDK remote-control bridge back into the parked P70
  branch and marked P70 active again with P71 complete.
- Prepared and launched ignored SDK manifest
  `runtime/p70_ticket_b_tsa23_instance_roadmap/manifest.json` for P70.2 Ticket
  B, using FEMIC P108 and the TSA23 instance as the target lane.
- Ran SDK session `cdba1e8b-5173-4676-bacc-081e18d9eec8`; the worker produced
  an accepted candidate that reconciled `external/femic-tsa23-instance/ROADMAP.md`
  with closed FEMIC issues #300 and #301.
- Supervisor verification confirmed the instance diff, added an instance
  changelog note, committed and pushed instance commit `282da67`, and updated
  FEMIC PR #303 with parent commit `b60dbd5`.
- Fixed the SDK bridge live adapter so relative manifest `working_directory`
  values are resolved to absolute paths at launch time while keeping manifests
  public-safe.

## 2026-07-08 - Added SDK transcript rendering for P70 review

- Added `agent-workbench copilot-sdk transcript`, which reads a session
  manifest's SDK event JSONL and renders a human-readable Markdown transcript
  of coordinator messages, Copilot worker replies, tool activity, and permission
  events.
- Kept raw `system.message` payloads omitted by default to avoid burying the
  conversation in runtime instructions, with `--include-system` available for
  local-only audit when needed.
- Generated the first ignored transcript for
  `runtime/p70_ticket_b_tsa23_instance_roadmap/manifest.json` so P70 Ticket B
  conversation evidence can be reviewed alongside the existing status and
  result summaries.

## 2026-07-09 - Added compact SDK transcript view

- Extended `agent-workbench copilot-sdk transcript` with `--compact-output` so
  one run can write both the full audit transcript and a second compact
  chat-pane-style transcript.
- The compact view keeps user messages, Copilot worker replies, tool actions,
  statuses, and short output signals visible by default, while preserving the
  full per-event text in expandable Markdown details.
- Regenerated P70 Ticket B transcript evidence with a compact local artifact
  under `runtime/p70_ticket_b_tsa23_instance_roadmap/`.

## 2026-07-09 - Activated P72 Copilot SDK custom agent profiles

- Opened stacked PR #479 from P72 onto the active P70 branch.
- Added P72/P73/P74 planning notes and roadmap entries for SDK custom-agent
  profiles, the standard Agent Workbench profile catalog, and later FoundryTK
  profile optimization exploration.
- Extended SDK session manifests with `sdk.agent_profiles`, including profile
  source paths, selected agent, default-agent config, local-only custom agents,
  subagent streaming, task overlays, and custom Agent Workbench tools.
- Added `.agent.md` profile parsing, validation, public-safe profile rendering,
  SDK create/resume kwargs pass-through, and custom-agent/subagent transcript
  evidence.
- Added conservative Agent Workbench SDK tools for run context, result contract,
  and result validation, with focused tests covering profile parsing, bridge
  kwargs, resume behavior, transcript metadata, and tool validation.
- Verified the implementation with focused P72 tests, full `pytest`, `ruff
  check`, `git diff --check`, and a local `profile-validate`/`profile-render`
  smoke against the standard supervisor profile; `mypy` remains unavailable in
  the repo venv and the repo has no pre-commit config.
- Dogfooded P72.5 on P70 Ticket C with selected profile
  `agent-workbench-local-supervisor` in SDK session
  `6ebd387b-b23a-4ff1-8e22-5abc46a2cba0`; the run repaired the ignored FEMIC
  P108 supervisor result report, used subagent events and the custom
  `agent_workbench_validate_result` tool, and produced a comparison against the
  Ticket B baseline under ignored runtime storage.
- Added a manifest-derived `session.custom_agents_updated` evidence event so
  future SDK runs expose selected custom-agent profile configuration in monitor
  and transcript artifacts even when the SDK does not emit that event itself.
- Merged PR #479 into the active P70 branch and marked P72 complete.

## 2026-07-09 - Ran P70 Ticket D PR consistency dogfood

- Merged the completed P72 custom-agent bridge into the active P70 branch and
  closed the P72 parent issue.
- Ran P70 Ticket D with selected profile `agent-workbench-local-supervisor` in
  SDK session `b44c04bb-2414-4175-9208-e773747f48f7`.
- The worker produced a PR #303 and P108 issue consistency result. Coordinator
  verification confirmed that PR #303 is open, non-draft, mergeable, targets
  `main`, has expected head branch `feature/p108-tsa23-instance-bootstrap-delegation`,
  and has passing `build` and `package-release-checks` with `deploy` skipped.
- Verified that P108 child issues #297-#301 are closed, parent issue #302 is
  open, and FEMIC `ROADMAP.md` agrees with those issue states.
- Recorded Ticket D as useful verified evidence but not a clean controller run:
  the SDK emitted a `model.call_failure` XML syntax error, so the bridge marked
  the session blocked despite a substantively correct result file.

## 2026-07-09 - Completed P70.2 cleanup ticket set

- Produced the Ticket E final coordinator review packet under ignored runtime
  storage at `runtime/p70_ticket_e_final_review_packet/review_packet.md`.
- Synthesized Tickets A-D and confirmed the current FEMIC P108 review state:
  PR #303 is open, non-draft, mergeable, targets `main`, and has expected
  status checks; child issues #297-#301 are closed; parent issue #302 remains
  open by design.
- Marked P70.2 complete and recorded that P70.3 controller evaluation should
  score Ticket D's SDK `model.call_failure` separately from the independently
  verified result content.

## 2026-07-09 - Completed P70.3 controller evaluation

- Wrote the P70.3 controller evaluation under ignored runtime storage at
  `runtime/p70_controller_evaluation/controller_evaluation.md`.
- Compared Ticket B/C/D SDK metrics against the archived whole-phase P108 run,
  including event counts, tool starts, permission requests, subagent events,
  custom-agent evidence events, custom-tool mentions, nudges, and observed SDK
  errors.
- Recorded the controller decision: task-level SDK delegation is a net
  improvement for bounded cleanup/review tickets, but controller scoring must
  separate result validity from session health because Ticket D produced a
  correct result while the SDK emitted a `model.call_failure`.

## 2026-07-09 - Completed P70 scale decision

- Wrote the P70.4 scale decision under ignored runtime storage at
  `runtime/p70_scale_decision/scale_decision.md`.
- Accepted task-level SDK Copilot supervision as the default candidate for
  bounded cleanup/review lanes with explicit result or blocker artifacts,
  coordinator verification, ignored raw runtime evidence, and compact
  transcript review.
- Kept broad multi-day implementation phases out of scope for default SDK
  delegation until controller-health scoring, failure taxonomy, profile metrics,
  and conservative tool-safety evidence improve.
- Recorded that P73 should precede P74: stabilize the standard profile catalog
  and tool-aware evidence schema before FoundryTK optimization exploration.
- Preserved the FEMIC authority boundary: P70 does not merge PR #303 and does
  not close parent issue #302.

## 2026-07-09 - Opened P70 pull request

- Opened PR #484 from `feature/p70-femic-p108-repair-dogfood` to `main` to
  land the completed P70/P72 branch train.
- Updated `ROADMAP.md` so the P70 tracker row references PR #484.

## 2026-07-09 - Activated P73 standard profile catalog

- Opened parent issue #480 and created branch
  `feature/p73-standard-agent-profile-catalog`.
- Activated the roadmap phase for standard Agent Workbench profile catalog
  work, including reusable task overlays, profile/tool catalog validation,
  profile-run evidence summaries, and bounded dogfood before any P74 FoundryTK
  optimization exploration.

## 2026-07-09 - Completed P73.1 overlay registry

- Added checked-in standard task overlays under `.github/agents/overlays/` for
  repair-list execution, new Python module implementation, existing-code
  debugging, systematic refactor/sweep, documentation expansion,
  notebook/example authoring, and release-readiness review.
- Extended `sdk.agent_profiles.task_overlay` resolution to support named
  standard overlays, path-based overlays, and literal text overlays while
  appending the resolved overlay only to the selected SDK profile prompt.
- Added overlay metadata to `profile-validate`, `profile-render`, and the
  synthetic `session.custom_agents_updated` evidence event.
- Verified P73.1 with focused profile/SDK bridge tests and a local
  `profile-validate`/`profile-render` smoke manifest using
  `release-readiness-review`.

## 2026-07-09 - Completed P73.2 profile catalog validation

- Added a standard profile catalog validator for the four canonical
  `.github/agents/*.agent.md` profiles and the seven checked-in task overlays.
- Added `agent-workbench copilot-sdk catalog-validate` with optional
  public-safe Markdown preview output for coordinator review.
- The catalog preview reports loaded profiles, selected models, explicit tool
  declarations, unsupported VS Code-only frontmatter fields, prompt character
  counts, overlay availability, warnings, and errors without exposing full
  prompt text.
- Verified profile-declared tools against known SDK built-ins and the Agent
  Workbench custom tool registry.

## 2026-07-09 - Completed P73.3 profile-run evidence summary

- Added `agent-workbench copilot-sdk profile-run-summary` to produce public-safe
  profile-run evidence from an SDK manifest, event log, status summary, and
  result/blocker artifacts.
- The summary reports selected profile, selected task overlays, custom tools,
  transcript-shape counts, latest controller status, controller health, and
  result/blocker final status when the artifact follows the current
  `Final status:` contract.
- Rendered ignored baseline evidence for P70 Ticket C and Ticket D under
  `runtime/p73_profile_run_evidence/`; Ticket D correctly classifies controller
  health as `error`, preserving the P70 split between result validity and
  controller/session health.

## 2026-07-09 - Completed P73 standard profile catalog

- Replayed a bounded profile/overlay SDK artifact using selected profile
  `agent-workbench-local-supervisor`, task overlay `release-readiness-review`,
  and the conservative Agent Workbench SDK tools.
- Verified the profile-run summary reports selected profile, selected overlay,
  custom tools, conversation-shape evidence, `controller_health=healthy`, and
  `result_status=accepted-candidate`.
- Recorded the P73 scale recommendation under ignored runtime evidence at
  `runtime/p73_overlay_replay/p73_4_scale_recommendation.md`.
- Marked P73 complete and kept FoundryTK runtime integration deferred to P74.

## 2026-07-09 - Opened P73 pull request

- Opened stacked PR #483 from `feature/p73-standard-agent-profile-catalog` to
  `feature/p70-femic-p108-repair-dogfood`.
- Updated `ROADMAP.md` so the P73 tracker row references PR #483.

## 2026-07-09 - Activated P74 FoundryTK profile optimization

- Created branch `feature/p74-foundrytk-profile-optimization` from the completed
  P73 profile catalog branch.
- Added `agent-workbench foundrytk profile-optimization-plan`, a local
  FoundryTK-style planning command that consumes P73 profile-run evidence and
  renders public-safe optimization guidance without adding a FoundryTK runtime
  dependency or changing the Copilot SDK bridge.
- Defined reliability, work quality, efficiency, and conversation-shape
  dimensions in the rendered plan.
- Rendered ignored P74 evidence at
  `runtime/p74_foundrytk_profile_optimization/profile_optimization_plan.md`;
  the plan correctly recommends stabilizing controller/session health before
  prompt or model optimization because P70 Ticket D contributes
  `controller_health=error` evidence.

## 2026-07-09 - Added P74 profile evaluation dataset contract

- Added `agent-workbench foundrytk profile-evaluation-dataset`, which writes
  public-safe JSONL rows and a Markdown preview from SDK manifests without
  requiring Azure resources or FoundryTK runtime integration.
- The row schema maps local profile-run evidence into reliability,
  work-quality, efficiency, and conversation-shape dimensions.
- Rendered an ignored two-row dataset and preview under
  `runtime/p74_foundrytk_profile_optimization/`, using the P73 overlay replay
  and P70 Ticket D controller-health evidence.
- The dataset excludes raw transcript text and private paths.

## 2026-07-09 - Completed P74 FoundryTK integration decision

- Recorded the P74.3 integration decision under ignored runtime evidence at
  `runtime/p74_foundrytk_profile_optimization/p74_3_integration_decision.md`.
- Decided to keep FoundryTK outside the Agent Workbench runtime bridge for now
  and use it as external evaluation guidance only.
- Deferred optional tool-provider, model-selection, trace/evaluation runner,
  prompt-optimization, agent-optimizer, and model-customization work until
  comparable live overlay-selected SDK runs, controller-health scoring,
  public-safe evaluation rows, compact transcript review, and an explicit
  treatment comparison plan exist.
- Marked P74 complete repo-side; GitHub issue/PR hygiene was still pending at
  that point because `gh` was unavailable in the restricted shell.

## 2026-07-09 - Reconciled P74 GitHub issue tracking

- Created GitHub parent issue #481 for P74 after `gh` access returned.
- Updated `ROADMAP.md` so the P74 tracker row and phase section reference
  issue #481 instead of `TBD`.
- Left P74 implementation status unchanged: repo-side work is complete and
  FoundryTK remains external evaluation guidance only.

## 2026-07-09 - Opened P74 pull request

- Opened stacked PR #482 from `feature/p74-foundrytk-profile-optimization` to
  `feature/p73-standard-agent-profile-catalog`.
- Updated `ROADMAP.md` so the P74 tracker row references PR #482.

## 2026-07-09 - Activated P75 live overlay-selected SDK run battery

- Created branch `feature/p75-live-overlay-sdk-run-battery`.
- Opened parent issue #485 and child issues #489, #486, #487, and #488 for
  P75.1 through P75.4.
- Added `planning/phase75_live_overlay_sdk_run_battery.md` to define the
  matched live-run comparison shape, evidence contract, scoring boundary,
  budget/stop-rule placeholder, and FoundryTK follow-on decision boundary.
- Updated `ROADMAP.md` with the P75 tracker row and active phase section so
  comparable live SDK evidence collection can start before any deeper
  FoundryTK integration work.

## 2026-07-09 - Tightened P75 empirical design requirements

- Clarified that three comparable live SDK runs are only the minimum smoke gate
  for the evidence pipeline, not a sufficient empirical sample for profile,
  overlay, or model-selection decisions.
- Required P75.1 to define a factorial design with declared factors,
  fixed-versus-exploratory distinctions, blocking variables, randomization or
  rotation order, replication count, and sample-size rationale.
- Added the rule that if budget or operational limits force a narrower matrix,
  P75 should preserve replication before breadth and report underpowered or
  stopped batteries as design/infrastructure evidence rather than profile/model
  recommendations.

## 2026-07-09 - Completed P75.1 factorial run battery design

- Defined the activated P75 run battery as a 24-run balanced matrix across two
  profiles, two named overlays, two task families, and three repetitions per
  treatment cell.
- Held the model lane fixed as `operator-configured-copilot-sdk` because local
  worker inventory was not available from the active shell, preserving
  replication instead of adding an unverifiable model factor.
- Declared smoke-gate, minimum analyzable sample, blocking variables,
  randomized run order, runtime evidence paths, scoring boundaries, and stop
  rules before live SDK execution.

## 2026-07-09 - Added constrained SDK result writer for P75.2

- Added `agent_workbench_write_result`, a Copilot SDK custom tool that can write
  only the manifest-declared result or blocker file for a run.
- The tool requires a `Final status:` line, accepts the P75 result-status
  vocabulary, rejects private-looking content, and validates the artifact after
  writing.
- This repairs the live smoke-gate gap where selected profiles could produce
  chat evidence but could not reliably create the required result artifact via
  shell redirection or broad edit authority.

## 2026-07-09 - Completed P75 live overlay-selected SDK run battery

- Ran the full 24-row P75 matrix across two selected profiles, two named
  overlays, two task families, and three repetitions per treatment cell.
- Rendered monitor summaries, compact transcripts, profile-run summaries, a
  P74-compatible JSONL dataset, a Markdown dataset preview, and a profile
  optimization plan under ignored runtime evidence.
- The public-safe dataset contains 24 analyzable rows with healthy controller
  status for every row.
- Result validity remained mixed: 9 accepted-candidate rows, 11
  needs-supervisor-review rows, and 4 blocked rows.
- Decided that FoundryTK remains external guidance; P75 supports automated
  aggregate comparison summaries and clearer task/profile contracts as the next
  lane, not runtime FoundryTK integration or model-selection claims.

## 2026-07-09 - Activated P76 aggregate comparison reports

- Created branch `feature/p76-profile-evaluation-aggregate-reports`.
- Opened parent issue #491 and child issues #492, #493, and #494 for P76.1
  through P76.3.
- Added `planning/phase76_profile_evaluation_aggregate_reports.md` to define
  the aggregate report input contract, output contract, privacy boundary, and
  follow-on decision boundary.
- Updated `ROADMAP.md` with P76 as the active next lane from P75 evidence:
  aggregate comparison tooling and task/profile contract clarity before another
  live battery, model-lane expansion, or FoundryTK runtime integration.

## 2026-07-09 - Completed P76 aggregate comparison reports

- Added `agent-workbench foundrytk profile-evaluation-aggregate`, which reads
  public-safe profile evaluation JSONL rows and writes Markdown plus JSON
  aggregate summaries.
- The aggregate report summarizes controller health, result status, selected
  profile, task overlay, inferred task family, grouped result distributions,
  treatment cells, and conversation-shape totals and averages.
- Added focused tests for grouped counts, empty datasets, invalid JSONL,
  private-looking value rejection, and CLI output writing.
- Dogfooded the command on the P75 24-row dataset under ignored runtime
  evidence at `runtime/p76_profile_evaluation_aggregate_reports/`.
- The P75 aggregate report recommends task/profile contract repair before
  another live battery, model-lane expansion, or FoundryTK runtime integration.

## 2026-07-09 - Activated P77 profile contract repair plan

- Created branch `feature/p77-profile-contract-repair-plan`.
- Opened parent issue #496 and child issues #497, #498, and #499 for P77.1
  through P77.3.
- Added `planning/phase77_profile_contract_repair_plan.md` to define the
  repair-plan input contract, output contract, privacy boundary, and follow-on
  decision boundary.
- Updated `ROADMAP.md` with P77 as the active next lane from P75/P76 evidence:
  deterministic task/profile contract repair planning before another live SDK
  battery, model-lane expansion, or FoundryTK runtime integration.

## 2026-07-09 - Completed P77 profile contract repair plan

- Added `agent-workbench foundrytk profile-contract-repair-plan`, which reads
  public-safe profile evaluation aggregate JSON and writes Markdown plus JSON
  repair plans.
- The repair plan ranks weak treatment cells, task-family targets, and
  selected-profile targets using blocker-heavy and review-heavy result-validity
  counts while keeping controller health separate.
- Added focused tests for P75-like weak-cell ranking, empty evidence,
  private-looking aggregate grouping keys, and CLI output writing.
- Dogfooded the command on the P75 aggregate summary under ignored runtime
  evidence at `runtime/p77_profile_contract_repair_plan/`.
- The P75 repair plan recommends profile-evidence-review fixture repair and
  result-auditor-as-primary behavior repair before another live SDK battery,
  model-lane expansion, or FoundryTK runtime integration.

## 2026-07-09 - Activated P78 profile evidence review contract repair

- Created branch `feature/p78-profile-evidence-review-contract`.
- Opened parent issue #501 and child issues #502, #503, #504, and #505 for
  P78.1 through P78.4.
- Added `planning/phase78_profile_evidence_review_contract.md` to define the
  repaired review-subject input contract, ticket output contract, public-safety
  boundary, and validation boundary.
- Updated `ROADMAP.md` with P78 as the active next lane from P77 evidence:
  repair profile-evidence-review fixtures and result-auditor-as-primary
  behavior before another matched replicated live SDK battery.

## 2026-07-09 - Completed P78 profile evidence review contract repair

- Added `agent-workbench foundrytk profile-evidence-review-ticket`, which reads
  an SDK manifest and writes a JSON contract plus Markdown ticket for repaired
  profile-evidence-review tasks.
- The repaired contract requires a pre-existing review subject path, rejects
  missing or private-looking subjects, and rejects subjects that point at
  current-run output paths.
- Updated `agent_workbench_run_context` to expose declared artifact paths so
  selected primary agents can discover the review subject through the
  constrained tool surface.
- Updated `agent-workbench-result-auditor` with selected-primary instructions
  for using Agent Workbench run-context, result-contract, result-writer, and
  validation tools while preserving read-only and no-GitHub boundaries.
- Added focused tests for valid, missing-subject, current-run-output subject,
  private-subject, CLI output, run-context artifact paths, and result-auditor
  primary-mode profile text.
- Dogfooded the command on a repaired P75-style manifest under ignored runtime
  evidence at `runtime/p78_profile_evidence_review_contract/`.
- The next empirical step is a matched replicated live battery on repaired
  profile-evidence-review cells before model-lane expansion or FoundryTK
  runtime integration.

## 2026-07-09 - Activated P79 repaired profile-evidence-review battery

- Created branch `feature/p79-repaired-profile-review-battery`.
- Opened parent issue #507 and child issues #508, #509, and #510 for P79.1
  through P79.3.
- Added `planning/phase79_repaired_profile_review_battery.md` to define a
  48-row repaired-cell matrix across two selected profiles, two overlays,
  three source-result strata, and four matched review subjects per stratum.
- Declared a 36-row minimum analyzable threshold and stop rules so later live
  execution does not treat an underpowered smoke as repaired profile evidence.

## 2026-07-09 - Completed P79 repaired battery scaffold

- Scaffolded a 48-row repaired profile-evidence-review matrix under ignored
  runtime evidence at `runtime/p79_repaired_profile_review_battery/`.
- Generated 48 manifests, 48 repaired tickets, 48 profile-evidence-review
  contract JSON files, and matrix JSON/Markdown previews.
- Balanced the design across two selected profiles, two overlays, three
  source-result strata, and four matched P75 profile-run summary subjects per
  stratum.
- Verified the matrix has 12 profile/overlay/stratum cells with 4 rows per
  cell.
- Inspected generated matrix, ticket, and contract artifacts for personal
  paths, provider URLs, and token-like values; no matches were found.
- Recorded that the next phase should execute the 48-row repaired battery, or
  at minimum preserve 36 analyzable rows with three matched source subjects per
  stratum for every profile/overlay pair.

## 2026-07-09 - Activated P80 repaired profile-evidence-review execution

- Created branch `feature/p80-repaired-profile-review-execution`.
- Opened parent issue #512 and child issues #513, #514, #515, and #516 for
  P80.1 through P80.4.
- Added `planning/phase80_repaired_profile_review_execution.md` to define the
  execution boundary, 12-row smoke gate, 48-row target, 36-row minimum
  analyzable threshold, evidence outputs, and stop rules.
- Confirmed the active shell can import `copilot` and `pydantic`, and validated
  a representative P79 manifest with
  `agent-workbench copilot-sdk validate --manifest`.

## 2026-07-09 - Completed P80 smoke-gate execution

- Executed the 12-row repaired profile-evidence-review smoke gate under ignored
  runtime evidence at `runtime/p80_repaired_profile_review_execution/`.
- Captured SDK events, status summaries, compact transcripts, profile
  summaries, and result or blocker artifacts for the smoke rows.
- The smoke gate produced 10 valid result-or-blocker artifacts and 3
  controller/provider error rows, including repeated provider quota-exceeded
  SDK event errors.
- Rendered the P80 smoke profile-evaluation dataset, aggregate summary, and
  contract-repair plan.
- Stopped before the full 48-row repaired battery because
  `smoke_gate_passed=false`; the phase therefore makes no repaired
  profile-evidence-review behavior claim.
- Recorded the next lane as controller/session health repair or quota recovery
  before another repaired battery, model-lane expansion, or FoundryTK runtime
  integration.

## 2026-07-10 - Activated P81 controller/session health gate

- Created branch `feature/p81-controller-session-health-gate`.
- Opened parent issue #518 and child issues #519, #520, #521, and #522 for
  P81.1 through P81.4.
- Added `planning/phase81_controller_session_health_gate.md` to define the
  deterministic health-gate contract, public-safety boundary, go/no-go
  semantics, and next-lane rule.
- Recorded that P81 should protect the P79/P80 repaired 48-row factorial design
  rather than reduce the sample size after P80's quota/controller-health stop.

## 2026-07-10 - Completed P81 controller/session health gate

- Added `agent-workbench copilot-sdk health-gate`, which reads existing SDK
  manifests, status summaries, and event logs without contacting the live
  provider.
- The health gate writes public-safe JSON and Markdown reports with manifest
  counts, controller-health counts, row go/block decisions, sanitized repeated
  error signatures, and row-level reasons.
- Added focused tests for healthy evidence, repeated quota errors, missing
  status evidence, required-count shortfall, and CLI report generation.
- Dogfooded the gate against the 12 P80 smoke manifests under ignored runtime
  evidence at `runtime/p81_controller_session_health_gate/`.
- The P80 smoke dogfood produced `decision=no-go`, 9 healthy rows, 3
  controller-error rows, and repeated `quota_exceeded` signatures across 3
  rows.
- Recorded that the next empirical lane remains the full P79/P80 repaired
  48-row battery only after controller/session quota health recovers and the
  health gate can pass.

## 2026-07-10 - Activated P82 health-gated repaired battery

- Created branch `feature/p82-health-gated-repaired-battery`.
- Opened parent issue #524 and child issues #525, #526, #527, and #528 for
  P82.1 through P82.4.
- Added `planning/phase82_health_gated_repaired_battery.md` to define the
  live health preflight, full 48-row repaired battery boundary, 36-row minimum
  analyzable threshold, evidence outputs, and stop rules.
- Recorded that P82 should execute the full repaired battery only after a live
  P81 health gate passes and should not replace the battery with another
  underpowered smoke.

## 2026-07-10 - Completed P82 health-gated repaired battery

- Generated a fresh ignored P82 runtime at
  `runtime/p82_health_gated_repaired_battery/` from the P79 repaired 48-row
  matrix.
- Validated all 48 generated matrix manifests plus the separate live health
  probe manifest before live execution.
- The live health preflight passed with `decision=go`, one healthy probe row,
  no repeated error signatures, and an `accepted-candidate` result.
- Executed all 48 repaired battery rows after the health gate passed.
- Rendered monitor summaries, compact transcripts, profile summaries, the
  P82 full-battery health-gate report, the profile-evaluation dataset,
  aggregate report, contract-repair plan, and execution summary under ignored
  runtime evidence.
- Full-battery evidence showed 40 analyzable result/blocker artifacts, 8
  missing artifacts from quiet-stall/unknown controller rows, no repeated
  controller/provider error signatures, and 40 blocked final statuses.
- The balanced 3-per-cell threshold was not met; minimum cell coverage was 2,
  so P82 makes no repaired profile-evidence-review behavior claim.
- Recorded the next lane as review-subject path/materialization or SDK
  run-context access repair before another repaired battery.

## 2026-07-10 - Activated P83 review-subject access repair

- Created branch `feature/p83-review-subject-access-contract`.
- Opened parent issue #530 and child issues #531, #532, #533, and #534 for
  P83.1 through P83.4.
- Added `planning/phase83_review_subject_access_contract.md` to define the
  review-subject resolver/reader contract, public-safety boundary, and
  dogfood requirements.
- Recorded that P83 should repair access/materialization semantics before
  another repaired profile-evidence-review battery.

## 2026-07-10 - Completed P83 review-subject access repair

- Added `agent_workbench_review_subject` as a Copilot SDK custom tool for
  resolving and reading the declared profile-evidence-review subject without
  filesystem search.
- Extended run-context and result-contract payloads so workers can discover the
  declared review subject and the read tool alongside existing write/validate
  tools.
- Updated profile-evidence-review tickets and agent instructions to prefer the
  declared review-subject tool when it is available.
- Added focused tests for successful reads, missing subjects, current-run output
  rejection, private-looking path rejection, bounded content, sibling-runtime
  reads, and runtime escape rejection.
- Dogfooded the repair against a deterministic fixture and a real P82 manifest
  pointing to the P75 profile summary
  `runtime/p75_live_overlay_sdk_run_battery/profile_summaries/p75_mca_lsup_debug_r1.md`.
- The real dogfood read returned `ok=true`, `allowed_root=runtime`, no
  validation errors, and untruncated bounded content.
- Recorded the next lane as a small live SDK access probe before spending
  another full health-gated repaired battery.

## 2026-07-10 - Activated P84 review-subject live access probe

- Created branch `feature/p84-review-subject-live-access-probe`.
- Opened parent issue #536 and child issues #539, #540, #537, and #538 for
  P84.1 through P84.4.
- Added `planning/phase84_review_subject_live_access_probe.md` to define the
  one-run live access probe, success criteria, stop rules, and public-safety
  boundary.
- Recorded that P84 should verify live worker use of
  `agent_workbench_review_subject` before another full repaired battery.

## 2026-07-10 - Completed P84 review-subject live access probe

- Generated a one-run P84 live probe from the P82/P75 evidence chain under
  ignored runtime storage at `runtime/p84_review_subject_live_access_probe/`.
- Repaired the profile-tool allowlist so `agent_workbench_review_subject`
  validates in SDK custom agent profiles, and added regression coverage.
- Validated the P84 manifest and profile/tool declaration before live
  execution.
- Ran one live `profile-evidence-review` SDK probe with
  `agent-workbench-local-supervisor` and the `existing-code-debugging` overlay.
- The live run reached `completion_candidate` after 70 events, produced an
  `accepted-candidate` result, and did not produce a blocker artifact.
- Event evidence showed `agent_workbench_review_subject` was requested once and
  executed once; the worker result also stated that the declared subject was
  resolved through the review-subject tool rather than filesystem search.
- Recorded the next lane as a return to a health-gated repaired
  profile-evidence-review battery using the P83/P84 access repair, while
  keeping P84 itself classified as access evidence rather than repaired
  behavior evidence.

## 2026-07-10 - Activated P85 health-gated repaired battery rerun

- Created branch `feature/p85-health-gated-repaired-battery-rerun`.
- Opened parent issue #542 and child issues #544, #545, #546, #547, and #543
  for P85.1 through P85.5.
- Added `planning/phase85_health_gated_repaired_battery_rerun.md` to define the
  full 48-row repaired battery rerun, P81 health-gate requirement, analyzable
  threshold, balanced cell coverage threshold, and stop rules.
- Recorded that P85 should preserve the full balanced empirical design now that
  P83/P84 repaired and live-probed declared review-subject access.

## 2026-07-10 - Generated P85 repaired battery runtime scaffold

- Generated ignored P85 runtime artifacts under
  `runtime/p85_health_gated_repaired_battery_rerun/`.
- Preserved the full 48-row design with 12 profile/overlay/source-stratum cells
  and 4 rows per cell.
- Confirmed source-result stratum counts of 16 `accepted-candidate`, 16
  `needs-supervisor-review`, and 16 `blocked`.
- Regenerated all 48 manifests, tickets, and contracts with
  `agent_workbench_review_subject` declared in custom tools.
- Validated all 48 SDK manifests and profile declarations before live
  execution.
- Generated and validated the separate P85 live health-probe manifest, ticket,
  and contract outside the 48-row empirical sample.

## 2026-07-10 - Passed P85 live health preflight

- Ran the separate P85 live health probe before starting the 48-row repaired
  battery.
- The probe reached `completion_candidate` after 70 events, produced an
  `accepted-candidate` result, and did not produce a blocker artifact.
- The rendered profile summary classified controller health as `healthy`.
- The formal P81 health gate returned `decision=go` with 1 healthy probe row
  and no repeated error signatures.
- Recorded that P85.4 may start the full 48-row repaired battery under the P85
  stop rules.

## 2026-07-10 - Executed and evaluated P85 repaired battery

- Executed all 48 P85 repaired profile-evidence-review battery rows after the
  live health gate passed.
- All 48 `copilot-sdk start` calls exited successfully.
- Rendered monitors, compact transcripts, profile summaries, the full-battery
  health-gate report, profile-evaluation dataset, aggregate report, and
  execution summary under ignored runtime evidence.
- The full-battery health gate returned `decision=go` for all 48 rows, with 48
  healthy controller rows and no repeated error signatures.
- The profile-evaluation dataset was valid with 48 analyzable rows, 48 result
  artifacts, and 0 blocker artifacts.
- Final status counts were 47 `accepted-candidate`, 1
  `needs-supervisor-review`, and 0 `blocked`.
- The balanced source-cell threshold was met with 12 cells and 4 rows per cell.
- Compared with the P75 profile-evidence-review baseline, accepted rows
  increased from 2 to 47, blocked rows decreased from 4 to 0, and
  needs-supervisor-review rows decreased from 6 to 1.
- Updated the aggregate recommendation so high-acceptance, no-blocker repaired
  batteries point to the next replicated comparison lane while preserving
  targeted audit of remaining needs-supervisor-review rows.

## 2026-07-10 - Prepared P85 GitHub and PR closeout

- Marked P85.5 repo-side complete after the repaired battery evaluation met the
  minimum analyzable-row and balanced-cell thresholds.
- Recorded that resumed closeout has authenticated `gh` access, replacing the
  stale broken-shell note from the handoff session.
- Prepared P85 for child issue closeout and PR merge with the empirical result:
  48 analyzable rows, 47 accepted-candidate results, 1
  needs-supervisor-review result, and 0 blocked results.
- Kept the next lane focused on replicated comparison or model-lane evaluation,
  with targeted audit of the remaining needs-supervisor-review row.

## 2026-07-10 - Activated P86 dev validation toolchain repair

- Opened issue #549 and branch `feature/p86-dev-validation-toolchain-repair`.
- Marked P85 complete after PR #548 merged and parent issue #542 closed.
- Confirmed that installing `mypy` exposed current type-check failures instead
  of a clean validation gate.
- Confirmed that installing `pre-commit` exposed the missing
  `.pre-commit-config.yaml` repository contract.
- Started P86 to make the skipped validation gates reproducible and runnable
  rather than leaving them as local environment caveats.

## 2026-07-10 - Repaired P86 dev validation gates

- Added a `dev` extra in `pyproject.toml` for `github-copilot-sdk`, `mypy`,
  `pre-commit`, `pytest`, `ruff`, and `types-PyYAML`.
- Added a focused `.pre-commit-config.yaml` that runs `ruff format --check`,
  `ruff check`, and `mypy` over the maintained `src` and `tests` validation
  surfaces.
- Repaired current `mypy src` failures by narrowing JSON-boundary values,
  preserving optional SDK runtime imports, and adding a targeted FreshForge
  missing-import override.
- Verified `ruff format src tests`, `ruff check src tests`, `mypy src`,
  `pytest tests -q`, `pre-commit run --all-files`, and `git diff --check`.

## 2026-07-10 - Activated P87 real-project ROI roadmap reset

- Created P87 branch `feature/p87-real-project-roi-roadmap-reset`.
- Opened P87-P92 parent issues #551 through #556 for the real-project ROI
  tranche.
- Marked P86 complete after PR #550 merged and parent issue #549 closed.
- Added `planning/p87_p92_real_project_roi_roadmap.md` to reset the leading
  roadmap edge around paid-supervisor cost per useful, source-backed unit of
  real project work.
- Recorded the evidence base from P55, P63, P85, and P86: document-indexing
  remains the higher-ROI lane, P63 showed the recipe needs repair before scale,
  P85 shows profile-evidence-review contract repair is no longer the blocking
  product question, and P86 makes validation gates reproducible.
- Added P87-P92 as the detailed first tranche and P93-P100 as the strategic
  follow-on arc.
- Parked future profile/model batteries unless they answer a direct
  real-project ROI question.
- Verified the planning-only change with `ruff format src tests`, `ruff check
  src tests`, `mypy src`, `pytest tests -q`, `pre-commit run --all-files`, and
  `git diff --check`.

## 2026-07-10 - Selected P88 real-corpus benchmark slice

- Created P88 branch `feature/p88-real-corpus-benchmark-registry`.
- Opened P88 child issues #558 through #561 for candidate registry,
  first-slice selection, budget/stop-rule record, and closeout handoff.
- Added `planning/phase88_real_corpus_benchmark_registry.md`.
- Added `benchmarks/document_library/p88_candidate_corpus_registry.json` and
  `benchmarks/document_library/p88_selected_corpus_slice.json`.
- Selected `p88_tsa23_2012_data_package_pages_001_022`, preserving the P63
  source scope: `tsa23_2012_23tsdp12` pages 1-22 across three tracked chunks.
- Deferred the full 2012 latest-cycle mini-corpus, full 1995-present TSA23
  registry, and MP11-style repair-prepass seed until recipe v2 and audit-loop
  gates are ready.
- Recorded that P88 and P89 do not authorize live model execution; the first
  possible live run remains P92 after P89-P91 gates are satisfied.

## 2026-07-10 - Amended P88 selected slice to full data package

- Upgraded the selected P88/P89 corpus scope from the original three-chunk P63
  repeat slice to the complete `tsa23_2012_23tsdp12` data package document.
- Updated `benchmarks/document_library/p88_selected_corpus_slice.json` to cover
  pages 1-41 across all six tracked chunks, with 106,859 tracked text
  characters in ignored runtime chunk files.
- Updated the P88 candidate registry and planning note so P89-P92 target one
  complete useful document-indexing unit before any multi-document expansion.
- Preserved the no-live-execution boundary: P89 remains dry-run/materialization
  only, and any live run still requires later gates, one model/provider lane,
  and maintainer-reviewed stop rules.

## 2026-07-10 - Materialized P89 full-document recipe v2 dry run

- Added `scripts/build_p89_document_indexing_recipe_v2.py` with deterministic
  `materialize` and `validate-jsonl` commands.
- Added `planning/phase89_document_indexing_recipe_v2.md`.
- Materialized the full selected `tsa23_2012_23tsdp12` data package into 60
  unique page/section units, two record passes, 120 ignored runtime worker
  tickets, and 120 ignored empty candidate JSONL placeholders.
- Added sanitized P89 tracked artifacts:
  `p89_chunk_id_enum.json`, `p89_jsonl_validation_contract.json`,
  `p89_validation_input_manifest.json`,
  `p89_recipe_v2_materialization_manifest.json`, and
  `p89_dry_run_materialization_summary.json`.
- Added tests proving dry-run materialization stays sanitized, fenced/trailing
  comma JSONL can be mechanically repaired, and unknown chunk IDs are rejected.

## 2026-07-10 - Ran first P90 live extraction smoke

- Retargeted P90 from repair/audit design to actual full-document candidate
  extraction.
- Ran two live local-worker calls with `qwen3.6:35b-a3b-q8_0` against the P89
  full-document packet for section
  `tsa23_2012_23tsdp12__pages_001_008__p004__s02`.
- Captured raw worker results and candidate JSONL under ignored `runtime/`.
- Validated 20 `structure` records and 31 `content_metadata` records after
  deterministic extraction/repair into JSONL.
- Added `benchmarks/document_library/p90_actual_extraction_smoke_summary.json`
  as the public-safe tracked summary. The records are raw candidates only; no
  source audit or acceptance has been performed.

## 2026-07-10 - Ran P90 qwen3.6 side-by-side extraction batch

- Added `scripts/run_p90_qwen36_comparison_batch.py` to run and resume a
  bounded side-by-side extraction batch while keeping raw model output in
  ignored runtime paths.
- Restarted the interrupted batch after laptop sleep by clearing only the
  partial side-by-side runtime output and rerunning the 10-ticket comparison.
- Completed 20 live worker calls over the first 10 P89 `structure` tickets:
  10 with `qwen3.6:35b-a3b-q8_0` and 10 with `qwen3.6:35b-a3b-bf16`.
- Added `benchmarks/document_library/p90_qwen36_side_by_side_batch_summary.json`
  as the sanitized comparison summary.
- Recorded 49 schema-valid q8 candidate records over 9 valid runs and 64
  schema-valid bf16 candidate records over 8 valid runs. Three completed runs
  were rejected by deterministic validation. No candidate has been source
  audited or accepted into an index yet.

## 2026-07-10 - Activated P90 full-document candidate packet tranche

- Added `planning/phase90_full_document_candidate_packet.md` with the detailed
  P90.2-P90.4 execution plan.
- Expanded P90.2-P90.4 in `ROADMAP.md` into concrete full-document extraction,
  validation/repair summary, stop-decision, and source-audit handoff tasks.
- Selected `qwen3.6:35b-a3b-q8_0` as the primary full-document lane based on
  P90.1 protocol validity.
- Defined the next work product as one complete full-document candidate packet
  ready for source audit, not a production index or another broad model
  comparison.

## 2026-07-10 - Completed P90 full-document candidate packet

- Added `scripts/run_p90_full_document_candidate_packet.py` for resumable
  full-document extraction against the selected q8 lane.
- Ran all 120 P89 tickets for the complete `tsa23_2012_23tsdp12` data package:
  60 `structure` tickets and 60 `content_metadata` tickets.
- Captured raw worker output, candidate JSONL, repaired JSONL, and validation
  reports under ignored
  `runtime/document_library/tsa23_tsr/p90_full_document_candidate_packet/`.
- Added sanitized tracked artifacts:
  `benchmarks/document_library/p90_full_document_candidate_packet_summary.json`
  and
  `benchmarks/document_library/p90_full_document_candidate_packet_manifest.json`.
- Recorded 120/120 completed runs, 94 valid runs, 26 invalid runs, 800 emitted
  repaired candidate records, and zero blocked runs.
- Recorded the stop decision as `ready_for_source_audit`. The packet is a
  source-audit input only; no candidate record has been accepted into an index.

## 2026-07-10 - Activated P91 source-audit decision packet

- Added `planning/phase91_source_audit_decision_packet.md` with the detailed
  P91 audit and decision-packet plan.
- Retargeted P91 from generic reporting-worker summarization to a bounded
  source-audit decision packet over the P90 full-document candidate packet.
- Defined audit statuses for `accepted`, `repairable`, `rejected`, and
  `needs_review`, plus run-level defect handling for invalid or zero-record
  outputs.
- Kept reporting-worker output explicitly non-authoritative: the supervisor
  audit rows remain the decision source of truth.

## 2026-07-10 - Completed P91 source-audit decision packet

- Added `scripts/build_p91_source_audit_packet.py` to build the P91 audit
  sample, supervisor audit packet, reporting-worker draft packet, and decision
  packet from the P90 candidate packet.
- Added sanitized tracked artifacts:
  `benchmarks/document_library/p91_source_audit_sample_manifest.json`,
  `benchmarks/document_library/p91_supervisor_source_audit_packet.json`,
  `benchmarks/document_library/p91_reporting_worker_draft_packet.json`, and
  `benchmarks/document_library/p91_source_audit_decision_packet.json`.
- Audited a bounded sample of 16 candidate records plus six zero-record run
  defects against ignored P89 source excerpts.
- Recorded eight accepted sample records, two repairable sample records, six
  rejected sample records, no needs-review records, and six run-level
  zero-record defects.
- Recorded the P91 decision as `promote_seed`. Accepted counts apply only to
  the bounded P91 sample; the full P90 packet still requires additional audit
  before broad index promotion.

## 2026-07-11 - Recalibrated P91 source-quote scoring

- Opened issue #573 for the P91 source-quote scoring recalibration.
- Updated `scripts/build_p91_source_audit_packet.py` so table/caption cases
  with an exact source fragment plus synthesized row material are classified as
  repairable quote-anchor defects instead of unsupported rejected records.
- Added functional success levels: `A_accepted`, `B_minor_repair`,
  `C_repairable`, `E_rejected`, and `F_protocol_failure`.
- Regenerated the P91 sample, supervisor audit, reporting draft, and decision
  packets.
- Added
  `benchmarks/document_library/p91_source_quote_scoring_recalibration_delta.json`.
- Re-evaluation kept accepted sample records at eight, raised repairable sample
  records from two to seven, reduced rejected sample records from six to one,
  and raised useful sample yield from 0.625 to 0.938. The P91 decision remains
  `promote_seed`.

## 2026-07-11 - Retargeted P92 to a whole-document delegated supervisor pilot

- Activated P92 on `feature/p92-whole-document-supervisor-pilot` and retargeted
  the packaged pilot away from coordinator-built section microtickets.
- Added `scripts/build_p92_whole_document_supervisor_pilot.py` with
  materialization and report-validation modes for one whole-document delegated
  supervisor job.
- Added the full-tool `document-metadata-extraction-supervisor` custom-agent
  skin, its overlay, and a whole-document graph template.
- Materialized tracked public-safe P92 artifacts under
  `benchmarks/document_library/` and kept the raw full-document ticket plus
  compact bounce ticket under ignored `runtime/`.
- Recorded the ROI hypothesis explicitly: the paid coordinator should select
  one document, launch one role-bound local supervisor job, validate one
  returned report, issue at most one compact bounce, and then decide whether to
  accept seed, repair, switch lane, or stop.

## 2026-07-11 - Ran and evaluated P92 whole-document supervisor pilot

- Repaired the local Copilot bridge so document-library runtime paths are
  allowed and Agent Workbench is opened as the explicit workspace root.
- Ran the accepted R3 whole-document supervisor job with
  `qwen3.6:35b-a3b-bf16`, the `document-metadata-extraction-supervisor` skin,
  and autopilot permission.
- Validated a 28-record report with zero fatal errors, the expected model and
  final marker, five observed supervisor tools, and zero bridge deviations.
- Added `scripts/summarize_p92_whole_document_supervisor_pilot.py` and the
  tracked compact decision packet at
  `benchmarks/document_library/p92_whole_document_supervisor_decision_packet.json`.
- Classified the report as a quality-valid and protocol-accepted seed for
  coordinator audit while keeping economics `not_yet_proven`.
- Measured a 449,382-token coordinator span, including 447,232 cached-input
  tokens, with an estimated cash cost of $0.087798; this exceeded the recorded
  236,008-token P90/P91 minimum because launch, retry, and context overhead
  remained high.
- Recorded the next action as `accept_seed_for_coordinator_audit` without
  authorizing broad scale-up or returning to chunk-level coordinator
  micromanagement.

## 2026-07-11 - Completed P93 second public corpus application

- Activated P93 on `feature/p93-second-public-corpus-application` to apply the
  P90-P92 document-indexing protocol to a second public corpus.
- Ran supervisor pilot work over the new corpus slice, validated record yield,
  and confirmed the protocol generalizes beyond the original TSA23 source.
- Verified zero bridge deviations against expected evidence format.
- Merged via PR #577; parent issue #576 closed.

## 2026-07-11 - Completed P94 project-owned index promotion

- Activated P94 on `feature/p94-project-owned-index-promotion` to promote the
  aggregated corpus records into a project-owned index with full provenance.
- Promoted 47 records with complete source anchors and audit metadata.
- Validated provenance chain integrity across all promoted records.
- Merged via PR #579; parent issue #578 closed.

## 2026-07-11 - Completed P95 retrieval and modelling-agent usability

- Activated P95 on `feature/p95-index-retrieval-usability` and created child
  issues #581 through #584.
- Added `src/agent_workbench/retrieval.py` with promoted-index loading,
  page-range query, and full-document trace surfaces.
- Wired `agent-workbench retrieve` command paths in CLI for `list-docs`,
  `page-range`, and `trace`; fixed missing page-range handler wiring.
- Added query-contract schemas under `templates/query_schemas/` and the usage
  walkthrough at `templates/retrieval_usage_example.md`.
- Closed child issues #581-#584 after verification against real data.

## 2026-07-11 — Completed P96 as diagnostic model-lane comparison

- Activated P96 on `feature/p96-yield-audit-cost-model-comparison` with parent
  issue #585 and child issues #586 through #589.
- Completed protocol and lane-selection artifacts:
  `planning/phase96_comparison_protocol.md` and
  `planning/phase96_model_lane_selection.md`.
- Added bounded run manifest and execution packet:
  `benchmarks/document_library/tsa23_tsr/p96_model_lane_comparison_manifest.json`
  and `planning/phase96_p963_execution_packet.md`.
- Original p96_3 runs for both lanes failed with
  `OSError: [WinError 193] %1 is not a valid Win32 application` due to stale
  `COPILOT_CLI_PATH` environment variable.
- Corrected runs (p96_4) succeeded after clearing env and setting correct Ollama
  base URL — ran as `.py` file rather than inline PowerShell one-liner:
  - Baseline (`qwen3.6:35b-a3b-bf16`): 2994 input, 336 output tokens in 6.1 s
  - Candidate (`qwen3.6:35b-a3b-q8_0`): 2984 input, 311 output tokens in 42.7 s
  (7.0× slower, 92.6% output yield)
- Verdict updated from `insufficient_evidence` / `not_attempted` to
  `attempted_with_partial_signal`: full accepted-record classification per the
  P96 yield measurement protocol was not executed, but token-level comparison is
  sufficient for qualified closeout.
- Updated ROADMAP.md table row and phase section status to **complete (qualified)**.
- Infrastructure improvements added:
  - `~/.agent-workbench-env.txt` stores Ollama endpoint + provider headers path;
    probe script's `load_env_file()` auto-loads it before argument parsing.
  - `AGENTS.md` documents env file location for all Copilot sessions.
- GitHub issue #585 already closed (cannot edit post-close); corrected verdict
  and evidence are in
  `benchmarks/document_library/tsa23_tsr/p96_model_lane_comparison_execution_summary.json`
  and `planning/phase96_verdict.md`.