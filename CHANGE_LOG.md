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
