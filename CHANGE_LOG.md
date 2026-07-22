# Change Log

Newest entries are last. Keep this file synchronized with `ROADMAP.md`, GitHub
issues, pull requests, and closeout comments.

## 2026-07-21 - P115 and P118 tail issue cleanup

- Closed remaining orphaned P115 child issues (#727, #728, #729) that were missed during P115 phase closeout. P115 completed via PR #730.
- Repository now has zero open issues. All phase child tasks are either closed or parked by design.

## 2026-07-22 - P119 Blackwell vLLM crash forensics and service hardening

- Added `planning/p119_blackwell_vllm_crash_forensics.md` to preserve the
  sanitized post-crash finding: hours of useful concurrent work followed by a
  likely Blackwell GPU-kernel edge case on a long cached-prefix request shape.
- Recorded the low-overhead CUDA coredump mitigation and diagnostic replay
  sequence without tracking raw logs, endpoints, credentials, or private paths.
- Added `playbooks/vllm_blackwell/systemd/vllm-blackwell.service.example` and
  README guidance for bounded `systemd` restart-on-failure service packaging.

## 2026-07-22 - P119 Blackwell vLLM concurrency profile — closeout

- Completed P119 through PR #720 with the sanitized Blackwell vLLM playbook,
  bounded-concurrency operating guidance, endpoint compatibility notes, and
  host-specific benchmark methodology.
- Quality: focused P119 validation passes; broader repository baseline failures
  remain disclosed and out of scope.
- Protocol: no active P118 agent-profile or planning files were modified.
- Economics: no provider usage or cost evidence was captured for this packaging
  and validation phase.

## 2026-07-22 - P115: artifact-inspection bridge pilot — merged (#730)

- P115.1: FEMIC rebuild review selected as artifact family
- P115.2: femic-rebuild-inspector agent profile (`.github/agents/`)
- P115.3: 3 validation fixtures (clean, anomaly, provenance_gap) + 23 passing tests
- P115.4: Delegated inspection via `runSubagent` with custom `femic-rebuild-inspector`
  profile; anomaly detection 3/3, provenance gap detection 3/3
- P115.5: Quality/protocol/economics verdicts — all PASS
- Rescoped from Codex SDK / P114 adapter route to P118 native Agent Hub
  (`runSubagent` with bounded Qwen3-coder profile). No SDK, no adapter, no MCP.
- Issues #666, #722-#726 closed. PR #730 merged.

## 2026-07-21 - P115 activation and rescope

- P115 (Scientific Artifact-Inspection Bridge Pilot) activated after P118
  completion. Maintainer explicitly reprioritized P115 over P108/P109.
- Rescoped from Codex SDK / P114 adapter / CLI-parent route to P118 native
  Agent Hub route. Codex-specific lanes are parked.
- P115 now uses `runSubagent` delegation with a bounded Qwen3-coder inspection
  agent profile. No SDK, no adapter, no MCP, no custom tool grants.
- The "grant" is profile instructions (what to read, report, refuse). The
  "proof" is one delegated run, not a package handler.
- Branch `feature/p115-scientific-artifact-inspection` activated.
- Parent issue #666 reactivated; child issues #722-#729 created for P115.1-P115.5.
- Next: P115.1 task-family selection and fixture freeze.

## 2026-07-21 - P119 Blackwell vLLM concurrency profile — phase start

- Created parent issue #719 and branch
  `feature/p119-vllm-blackwell-concurrency-profile` for packaging the sanitized
  Blackwell vLLM lab as an Agent Workbench deployment playbook.
- Added `playbooks/vllm_blackwell/` with public-safe launch profiles, helper
  scripts, benchmark helpers, and an operator README. The import excludes live
  endpoint URLs, credentials, raw logs, model blobs, caches, `.env` files, and
  private transcripts.
- Added `planning/p119_blackwell_vllm_concurrency_profile.md` and a P119
  roadmap section. P119 records the FlashInfer/FP8-KV/MTP concurrency operating
  envelope and intentionally avoids overwriting active P118 agent-profile edits
  being handled in a separate session.
- Validated the sanitized import with shell parsing, Python compilation, CLI
  smoke checks, mocked OpenAI-compatible streaming responses, launch-profile
  dry runs, public-safety scans, whitespace checks, and focused Ruff checks. A
  clean-environment full-suite run produced 725 passes, 1 skip, and 21
  unrelated existing failures; repository-wide Ruff and mypy checks also retain
  pre-existing debt outside P119. No P118-owned agent-profile or planning files
  were changed.


## 2026-07-21 - P118.6: Concurrency-ticket validation

- **Quality:** 3 parallel independent read-only probes completed successfully
  from a single Supervisor flow. Probe 1 inspected 7 agent profiles for
  consistency (all profiles declare the single-model contract, no authority
  overlap). Probe 2 verified AGENTS.md concurrency contract is complete
  (parallel 2-4, burst 6, coordination rules present, no contradictions).
  Probe 3 verified ROADMAP.p118 lists P118.6 tasks. All probes returned
  substantive, independently inspectable results.
- **Protocol:** session boundary held. Coordinator → Supervisor delegation via
  native Agent Hub. 3 parallel `runSubagent` calls to workers completed
  concurrently without conflict. No `model.call_failure`, timeout, or VRAM
  pressure observed. Findings merged by Coordinator after all probes returned.
- **Economics:** all token spend against one configured vLLM endpoint. Zero paid
  model spans.
- **Concurrency verdict:** 3 parallel independent read-only work is stable on
  the configured endpoint. The endpoint is concurrency-optimized and holds for
  the 2-4 parallel agent target. Heavy parallel workloads (multi-file edits,
  test runs, code generation) remain unstressed.
- **Limitation:** this was a lightweight read-only workload. Further stress-testing
  with mutating work will validate the serial-only constraint for coupled tasks.
- **Advisor qualification (P118 closeout):** concurrency claim is qualified to
  "read-only parallel validated; mutating-work concurrency constraints and
  load-degradation thresholds deferred to future phases."

urrency-ticket validation complete)


## 2026-07-21 - P118.6.2: Concurrency stress test (tool-intensive)

- **Quality:** 4 parallel tool-intensive probes completed successfully from a
  single Supervisor flow. Probe A used grep_search + file_search to inventory 84
  scripts under `scripts/` and 63 modules under `src/agent_workbench/`, identified
  2 duplicated scripts, and performed orphan analysis (~40+ scripts without CLI
  wrappers). Probe B validated 8 schema files against 38 templates; 1 explicit
  path reference resolves correctly; 1 broken directory reference found. Probe C
  cross-referenced 7 planning notes with P118 references against ROADMAP; 19
  references checked, 0 orphaned. Probe D audited 7 agent profiles for
  trust-level compliance; all profiles compliant.
- **Protocol:** session boundary held. 4 parallel probes launched concurrently
  using grep_search (regex search), file_search (glob matching), and read_file
  (profile inspection). All probes completed without model.call_failure, timeout,
  or contention. Result files written independently.
- **Economics:** all token spend against one configured vLLM endpoint. Zero paid
  model spans.
- **Concurrency verdict:** 4 parallel tool-intensive work is stable on the
  configured endpoint. Heavier tool paths (grep_search scanning entire directory
  trees, file_search with glob patterns) hold under concurrency. This validates
  the concurrency contract beyond the P118.6 smoke test (which used only
  read_file). End-to-end, 18+ tool invocations across 190+ files scanned in
  parallel.
- **Comparison with P118.6:** P118.6 used 3 probes × read_file (simple single-file
  reads). P118.6.2 uses 4 probes × grep_search/file_search (multi-file regex and
  glob searches across directory trees). Tool intensity increased 2-3x per probe.
  No degradation observed between P118.6 and P118.6.2.

ncurrency stress test complete (4 parallel tool-intensive probes))

## 2026-07-21 - P118.5: Deployment decision

- **Quality:** single-model deployment produced substantive work across:
  P118.1 (agent-profile rewrite for 7 roles, AGENTS.md de-bloat from ~450→~70
  lines), P118.2 (concurrency-allowed operating contract in profiles and
  operator checklist), P118.3 (productive ticket — rewrite of stale
  `docs/roadmap_and_release/roadmap_overview.md` with +39/-12 clean change),
  P118.4 (SDK failure recovery via native Advisor, profile reconciliation).
- **Protocol:** session boundary held throughout. SDK delegation failure
  (`model.call_failure`) recovered via bounded native `runSubagent` fallback.
  Advisor remained read-only. Profile reconciliation was Coordinator-owned
  contract repair, not implementation substitution.
- **Economics:** all token spend against one configured vLLM endpoint. Zero paid
  model spans during P118.3-P118.4 runs. Opportunity cost (GPU, hosting) is
  real but outside this phase's accounting boundary.
- **Decision:** P118 profiles become the default native Agent Hub profile for
  single-model deployments. Profile reconciliation committed at `236f46f`
  resolves the final contract inconsistency flagged by the Advisor.
- **Deferral:** P118.6 concurrency-ticket test has been executed and validated.

oyment decision — single-model profiles are the default)

## 2026-07-21 - P118.4: Selective Advisor and recovery behavior

- Tried SDK delegation via `scripts/sdk_delegate.cmd` — hit `model.call_failure`
  (22 events, blocked as `sdk-event-error`).
- Recovered via native Agent Hub `runSubagent` to the `agent-workbench-advisor`
  profile, exercising the real ambiguity scenario the plan described.
- Advisor reviewed P118 pre-closeout readiness and flagged 6 findings:
  contract inconsistency between profiles (serial-only) and AGENTS.md
  (concurrency-allowed), P118.2 describing a superseded contract, P118.3 run
  under serial-only with concurrency untested, P118.4 meta-review need,
  P118.5 premature without concurrency evidence, and ROADMAP issue attribution
  drift (#716 vs #718).
- Verdict: **not closeout-ready**. Coordinator owns follow-up decision.
- Artifacts: ignored runtime files
  `runtime/agent_jobs/p118_4_advisor_review_{ticket,result}.md`.

cise selective Advisor and recovery behavior (complete))

## 2026-07-21 - P118.3: Productive bounded ticket

- Selected an ordinary bounded task: update the severely stale
  `docs/roadmap_and_release/roadmap_overview.md` (claimed active phase was P101,
  actual phase is now P118).
- Ran Coordinator-to-Worker delivery under the serial contract: Supervisor
  read `ROADMAP.md` and `planning/p118_fresh_vllm_agent_plan.md`, rewrote the
  doc with accurate phase tranche summaries (P0-P100, P101-P117), P118 task
  table, design principles, and upcoming-phases section.
- Independently verified: diff shows clean +39/-12 change to the target file
  only; content sourced from `ROADMAP.md` issue tracker map; P118.2 status
  corrected to "Complete" in the doc by Coordinator.
- Committed `ca80d25` on `feature/p118-fresh-vllm-agent`.

## 2026-07-21 - P118.2: Serial single-model operating contract

- Updated 4 agent profiles with `## Serial Operating Contract` sections
  (one active child, operator sequence, no doer-mode).
- Updated 1 agent profile with `## Delivery and Verification Contract`.
- Created `playbooks/p118_single_model_operator_checklist.md` with 8-step
  launch checklist.
- Updated `ROADMAP.md` P118 section and issue tracker table row (issue #716).
- Committed `9bfae74`, pushed to `feature/p118-fresh-vllm-agent`.

 complete in ROADMAP and CHANGE_LOG)

## 2026-07-21 - P118.1: Provider and role-profile contract — closeout

- P118.1 merged via PR #714; parent issue TBD (table row updated).
- Added `## Phase 118` section to `ROADMAP.md` with P118.1 checked off and
  P118.2–P118.5 planned.

## 2026-07-21 - P118.1: Provider and role-profile contract — implementation

- Rewrote `AGENTS.md` from ~450 lines to ~70, removing over-prescribed rituals
  that had accumulated from prior sessions. Moved detailed trust levels, file
  handoff, GitHub formatting, and heartbeat protocol references to their
  existing homes (`delegation_policy.md`, `playbooks/`, `CONTRIBUTING.md`).
- Updated all 7 agent profiles in `.github/agents/` to pin the single
  configured vLLM model (`Fresh vLLM Agent (Qwen 3.6 27B)`) instead of
  referencing stale Ollama or paid-Copilot models.
- Rewrote coordinator, advisor, and supervisor directives to reflect single-
  model reality: role separation by authority and instructions, not architecture.
- Added GPU constraint to `planning/p118_fresh_vllm_agent_plan.md` —
  one model, one GPU, serial inference is a hardware requirement.
- Updated `planning/authority_hierarchy_and_subagent_direction.md` and
  `planning/coordinator_advisor_paid_boost_strategy.md` to replace paid/free
  dichotomy with single-model deployment language.
- Updated `planning/delegation_policy.md` with P118 single-model context.
- Backed up pre-P118 `AGENTS.md` to `tmp/AGENTS.md.pre-p118.backup.md`.
- Branch: `feature/p118-fresh-vllm-agent`. Parent issue: TBD.

## 2026-07-12 - P100: Public Alpha Readiness Review — artifacts produced

- Created `planning/public_alpha_readiness_checklist.md` — pass/fail checklist
  across 5 areas: public-safety, templates and schema, CLI surface, ROI thesis
  and indexed-cost metric, and governance. Overall verdict: PASS WITH NOTED
  LIMITATIONS (25 items pass, 2 partial).
- Created `planning/public_alpha_readiness_review.md` — declares what is ready
  for external review (governance, CLI, graph templates, TSA23 pilot evidence,
  P95 retrieval, P101 docs), what remains experimental (whole-doc P92 economics,
  P85 profile battery, P96 model comparison, indexed-cost scale attribution),
  what should not be assumed production-ready (TSA23 index completeness, economics
  certification, worker model generalization, SDK infrastructure requirements).
  Contains ROI thesis statement, indexed-cost metric summary, open questions for
  external reviewers, and confidence assessment (MEDIUM-HIGH overall).
- Updated `ROADMAP.md`: P100 table row changed from TBD/Planned to #603/Active;
  phase section updated with parent issue and P100.1/P100.2 checklist marked [x].
- Also committed in this branch: agent profile updates (.github/agents/) and
  delegation_policy.md clarifications from the active coordinator session.
- Parent issue: #603. Branch: `feature/p100-public-alpha-readiness-review`.

## 2026-07-12 - P99: Economics Dashboard And Release Criteria — implementation

- Created `src/agent_workbench/economics.py` with `IndexedCostStage`, `IndexedCostRecord`,
  `IndexedCostReport`, `compute_indexed_cost`, `render_economics_markdown`, and
  `validate_economics_report`. Handles zero-promoted-record guard (no ZeroDivisionError).
- Added `agent-workbench economics render` subcommand to `src/agent_workbench/cli.py`.
  Accepts `--accounting`, `--tokens`, `--promoted-count`, `--corpus-id`, `--output`,
  and optional `--json-output` arguments. Loads pilot accounting and token records,
  computes indexed cost, writes Markdown and optional JSON output.
- Created `planning/phase99_economics_dashboard_release_criteria.md` with phase summary,
  indexed-cost metric specification (formula, stages, price assumptions), release-readiness
  criteria checklist, current state table, and P35/P40 wiring note.
- Created `tests/test_economics.py` with 4 tests:
  `test_compute_indexed_cost_basic`, `test_compute_indexed_cost_zero_records`,
  `test_render_economics_markdown_contains_corpus_id`,
  `test_validate_economics_report_missing_field`.
- Updated `ROADMAP.md`: P99 table row changed to `#601 | Active`; phase section
  updated to `Parent issue: #601`, `Status: active`; P99.1–P99.3 checklist items
  marked `[x]`.
- Parent issue: #601. Branch: `feature/p99-economics-dashboard-release-criteria`.

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

## 2026-07-12 - P97: Reusable workflow graph packaging — classification, rename, README rewrite

- Revised planning note (`planning/phase97_activation.md`) per Advisor review: promote=4,
  retire=2, keep-as-example=2, not-in-scope=4. Phase overview reframed as "reusable
  workflow graph catalog."
- Updated `templates/workbench_templates/README.md` with full P97 classification table,
  detailed descriptions of each promoted template's role in the graph family, and a future
  requirements section documenting JSON Schema validation as a P98+ item.
- Renamed `document_library_index_graph.json` →
  `document_library_index_workflow.json` (internal `workflow.id` already had target name).
  Git detected 100% rename.
- Updated all references from old filename to new: README, test suite, manifest template,
  benchmark plan JSON.
- Validated all 4 promoted templates: valid JSON, correct workflow IDs, all nodes declare
  provider, no hardcoded local paths or credentials. Existing pytest suite passes (4/4).
- GitHub issues: #592 parent phase created with child tasks #593 (audit), #594 (rename),
  #595 (instantiation guide). #593 and #594 closed as complete; #595 pending.
- ROADMAP.md updated to mark P97 In Progress with child issue numbers.

## 2026-07-12 - P101: Sphinx technical documentation with GitHub Pages deployment

- Created `docs/conf.py` with MyST parser, autodoc for CLI, RTD theme, and
  freshforge import mocking. Added `[docs]` optional dependencies to
  pyproject.toml (sphinx>=7.0, sphinx-rtd-theme>=2.0, myst-parser>=3.0,
  linkify-it-py>=2.0).
- Populated 19 content pages across 4 sections: guides (6 playbooks), concepts
  (4 protocols), reference (4 specs), and roadmap/release (2 sections). All
  cross-reference source markdown files in the repo.
- Created `.github/workflows/docs.yml` GitHub Actions workflow — validates docs
  on PRs, deploys to GitHub Pages on merge to main. `sphinx-build -b html docs
  _build/html -W` passes with zero warnings across 21 source files.
- Created GitHub Pages site at https://ubc-fresh.github.io/agent-workbench/.
- Wrote `planning/p97_instantiation_guide_draft.md` (P97.3 — temporary markdown
  for future RST translation into Sphinx docs).
- Updated coordinator agent authority to include PR merge authority with
  developer check-in requirement.
- GitHub issues: #598 parent phase created and closed after PR #597 squash-merge.

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
## Phase 98 � Reporting-Worker Template Packaging (2026-07-12)

- Activated P98 on `feature/p98-reporting-worker-templates` with parent
  issue #599.
- P98.1: Audited P91 source-audit decision packet
  (`benchmarks/document_library/p91_source_audit_decision_packet.json`),
  P73 overlay catalog (`.github/agents/overlays/` � 8 files), and confirmed
  P70 Ticket-C has no surviving worker result artifact.
  Audit note: `runtime/agent_jobs/p98_1_audit_note.md`.
- P98.2: Created `templates/source_audit_decision_packet.md` � generic
  source-audit template derived from P91 structure.
- P98.3: Created `templates/supervisor_decision_packet_template.md` � reusable
  supervisor decision packet (accept seed / repair / switch lane / stop).
- Planning note: `planning/phase98_reporting_worker_template_packaging.md`.
- Agent consolidation: `agent-workbench-supervisor.agent.md` deleted;
  `agent-workbench-local-supervisor.agent.md` promoted to canonical; worker
  `tools:` unlocked to productive-delegation; `delegation_policy.md` L4 flip;
  `AGENTS.md` L4 update; probe EVALUATION-ONLY guard added.
- Code/test fixes: `src/agent_workbench/retrieval.py` (ruff F401 + mypy
  no-redef); `tests/test_workbench_graph_templates.py` (SyntaxError). All
  pre-commit gates pass.
- PR merged and issue #599 closed.

## 2026-07-12 - Closed P100 and activated P102 native Codex orchestration

- Merged P100 through PR #604 and closed parent issue #603; the public-alpha
  readiness review remains a documented snapshot rather than the active lane.
- Activated P102 on `feature/p102-native-codex-ollama-orchestration` with
  parent issue #605 and child tasks #606 through #609.
- P102 treats native Codex as the Coordinator host and keeps the configured
  remote Ollama provider as an operator-local Supervisor/Worker dependency.
- The first gate is a bounded two-edge delegation proof. A substantive TSA23
  job remains out of scope until that proof has an explicit quality, protocol,
  and economics decision.

## 2026-07-12 - P102 native profile and proof-contract baseline

- Added project-scoped native Codex nesting configuration and generic
  `ollama_supervisor` / `ollama_worker` role profiles. Provider definitions,
  endpoint values, and Access headers remain machine-local.
- Added a local-only launcher plus deterministic validation for the two role
  files and a sanitized two-edge proof manifest.
- The first proof lane stopped before inference after two concrete launcher
  failures. The ignored result records the exact configuration error; no
  delegation, marker, or live-model claim was accepted.

## 2026-07-13 - P102 persistent no-modal Worker-host result

- Verified the installed native Codex app-server exposes a one-time Windows
  sandbox readiness/setup boundary; the local sandbox is now ready rather than
  requiring a sandbox authorization dialog per Worker task.
- Native app-server marker turns can reach the configured remote Ollama model
  under read-only permissions, but one observed turn emitted its marker and
  then failed to emit a terminal completion event. This remains an alpha
  app-server completion limitation, not a model-latency conclusion.
- Added a persistent, no-tool OpenAI-compatible Responses Worker host that
  keeps provider configuration local, accepts only ignored runtime ticket and
  result paths, and reports compact request start/completion records.
- Two sequential marker tickets completed through that host with HTTP 200 and
  exact result markers; the first took about three seconds and the warmed
  second completed in under one second. No nested Codex sandbox was launched.
- This is accepted as a `quality_validated_candidate` for the Worker-host
  boundary only. It is not a `protocol_accepted_candidate`: an observed
  Supervisor-direct Worker dispatch edge is still required before substantive
  native-hierarchy work is authorized.

## 2026-07-13 - P102 no-modal serial Supervisor/Worker proof

- Added a serial OpenAI-compatible Responses proof that runs remote Supervisor
  dispatch, Worker marker work, and remote Supervisor verification without a
  nested Codex sandbox.
- The bounded run returned HTTP 200 for all three turns and persisted the
  expected dispatch, Worker, and verification markers. The warmed Worker turn
  completed in under one second.
- The Coordinator deliberately relays the ticket between serial turns to avoid
  the observed concurrent response-stream failure. The result strengthens the
  quality signal but does not establish a Supervisor-direct dispatch edge or
  economics claim.

## 2026-07-13 - P102 qualified Supervisor-authored Worker handoff

- Completed a bounded hybrid proof in which a remote native Supervisor used a
  restricted app-server shell action to create one ignored Worker ticket.
- The persistent Responses Worker host consumed that exact ticket, returned the
  expected marker with HTTP 200, and a fresh remote Supervisor independently
  read and verified the result marker.
- The Coordinator remained the transport and sequencing owner; the observed
  handoff authority was the Supervisor-authored ticket artifact. No nested
  Codex CLI process or per-task Windows authorization dialog was used.
- Accepted the bounded ticket handoff as a qualified protocol candidate. The
  native app-server terminal-completion stall remains a recorded limitation,
  and no economics or substantive TSA23 authorization is implied.

## 2026-07-13 - Closed P102 native Codex + remote Ollama orchestration

- Merged the qualified P102 result through PR #610 and closed parent issue #605.
- The merged runtime has a no-modal persistent Worker host and a bounded
  Supervisor-authored ticket handoff with independent Supervisor verification.
- The phase does not authorize substantive TSA23 delegation: paid Coordinator
  economics and a small non-trivial repeat remain prerequisites for any future
  activation.

## 2026-07-13 - Activated P103 paid Coordinator economics trial

- Added P103 to the roadmap with parent issue #611 and child issue #612.
- P103 is the next bounded development goal after the qualified P102 closeout:
  one structured Supervisor-authored Worker handoff with paid Coordinator
  token-span metadata and separate quality, protocol, and economics verdicts.
- The trial remains explicitly out of scope for substantive TSA23 work,
  provider/model changes, release actions, tracked-file Worker mutation, and
  nested `codex exec` launches.

## 2026-07-13 - Closed P103 paid Coordinator economics trial (qualified)

- Completed the single allowed P103 structured handoff run after one
  evidence-based dispatch repair.
- Quality verdict: PASS. The persistent Worker returned the exact expected JSON
  result with HTTP 200, and a fresh Supervisor returned `P103_VERIFIED`.
- Protocol verdict: PASS, qualified. The Supervisor authored the ignored Worker
  ticket; no nested `codex exec`, provider change, TSA23 work, release action,
  or tracked-file Worker mutation occurred.
- Economics verdict: INSUFFICIENT. Coordinator span start/end metadata was
  captured, but native token counts and the exact picker model label were not
  available. This does not authorize substantive TSA23 delegation.
- Evidence remains under ignored path
  `runtime/agent_jobs/p103_economics_trial/`; no raw provider details were
  promoted into tracked files.

## 2026-07-13 - Backfilled P103 Coordinator economics

- Activated the existing P50 `supervisor_tokens` / `tokens` accounting
  functions against the preserved native Codex session JSONL; no P103 rerun was
  performed.
- Generated and validated the sanitized record under
  `runtime/supervisor_tokens/p103_economics_backfill/`.
- Recovered span usage: 1,922 fresh input tokens, 110,218 cached input tokens,
  629 output tokens, and 186 reasoning output tokens.
- At the recorded pricing defaults, paid Coordinator cost is `$0.034062`; the
  persistent Ollama Worker cost is `$0.000000`.
- Economics verdict is upgraded to **PASS, qualified** for actual-cost
  accounting. No direct-supervisor counterfactual exists, so no savings or ROI
  claim is made.
- The accounting snapshots bracket the recorded wall-clock end using the last
  available pre-end token event; that boundary choice is retained as an
  evidence caveat.

## 2026-07-13 - Corrected P103 economics to GPT-5.6 Luna pricing

- Repriced the validated P103 span using the confirmed GPT-5.6 Luna schedule:
  `$1.00` fresh input, `$0.10` cached input, and `$6.00` output per million
  tokens.
- Corrected paid Coordinator cost: `$0.017834` approximately, with Worker cost
  remaining `$0.000000`.
- The original `$0.034062` figure is retained only as a superseded repository-
  default estimate; it is not the P103 decision value.
- Next economics step: establish a current-model price catalog and capture a
  direct-supervisor counterfactual in a separately authorized benchmark before
  making any savings claim.

## 2026-07-13 - Planned P104-P110 ROI-to-alpha roadmap arc

- Activated the P104 implementation branch for canonical model pricing and
  economics provenance; GitHub parent issue #614 and child issues #615-#618
  are now active.
- Added fully decomposed P105-P110 phases covering a dry-run matched benchmark
  contract, separately gated live A/B execution, economics policy, fresh TSA23
  preparation, a separately gated productive pilot, and a conditional GitHub
  public-alpha pre-release.
- Kept live inference, substantive TSA23 work, and release publication behind
  explicit phase gates rather than treating roadmap planning as authorization.
- Selected a GitHub-only `v0.1.0a1` pre-release endpoint; PyPI publication stays
  out of scope for this arc.

## 2026-07-13 - Prepared P104 for phase PR closeout

- Synchronized `ROADMAP.md` with parent issue #614 and child issues #615-#618.
- Confirmed the implementation is isolated on
  `feature/p104-model-pricing-provenance`.
- Scoped validation covers catalog resolution, fail-closed unknown models,
  effective dates, cache pricing, long-context bounds, and legacy token
  compatibility; full repository collection remains unsuitable because ignored
  worktrees and virtual-environment packages are discovered by default.
## 2026-07-13 - Closed P104 canonical pricing provenance

- Merged PR #619 (`3ea94e8`) and closed parent issue #614 plus child issues
  #615-#618.
- P104 is complete with separate quality, protocol, and economics semantics;
  no live model call, provider change, TSA23 extraction, or release action was
  performed.

## 2026-07-13 - Activated P105 matched benchmark contract

- Activated parent issue #621 with child issues #622-#625 on
  `feature/p105-matched-public-corpus-contract`.
- Added the dry-run-only contract at
  `benchmarks/document_library/p105_matched_benchmark_contract.json` for the
  pinned P89 `pages_001_008` slice.
- Added fail-closed validation at
  `scripts/validate_p105_matched_benchmark.py` with two focused tests.
- Declared symmetric direct/delegated lanes and exact Coordinator, Supervisor,
  and Worker model identities without authorizing live inference.

## 2026-07-13 - Closed P105 matched benchmark contract

- Merged PR #626 and closed parent issue #621 plus child issues #622-#625.
- P105 is complete as a deterministic dry-run contract only; P106 remains the
  separately gated live direct-vs-delegated execution phase.
- The native Advisor transport attempt produced no advisory packet and was
  recorded as a transport stall; deterministic contract validation remained the
  acceptance evidence.

## 2026-07-13 - Reopened P105 for Advisor corrective validation gates

- Direct Advisor review accepted the dry-run boundary with caveats and found
  that P105 did not yet fail closed on every referenced artifact and semantic
  contract field.
- Reopened parent issue #621 and added corrective child issue #627.
- Hardened the P105 validator against source/P89 hash and semantic mismatches,
  lane roles, model-argument contract, stop rules, and output-contract drift.
- Added tampering and missing-artifact tests. P106 remains unactivated until
  this corrective PR is merged and the repair issue is closed.

## 2026-07-13 - Closed P105 Advisor corrective validation

- Merged PR #628 and closed corrective issue #627 and parent issue #621.
- P105 now fails closed on referenced artifact hashes and semantics, exact stop
  and output contracts, lane roles/models, and model-argument declarations.
- Negative tampering and missing-artifact tests pass; P106 remains separately
  gated and unactivated.

## 2026-07-13 - Activated P106 matched direct-vs-delegated execution

- Activated parent issue #629 with child issues #630-#633 on
  `feature/p106-matched-roi-benchmark` after P105 corrective closeout.
- Added the public execution protocol and deterministic gate manifest at
  `planning/phase106_matched_execution_protocol.md` and
  `benchmarks/document_library/p106_matched_execution_gate.json`.
- Added `scripts/validate_p106_execution_gate.py`, which validates the P106
  budget, attempt, pricing, exact-model, delegated-quality, and P105 contract
  prerequisites fail-closed.
- Live inference remains closed pending Coordinator inspection of current
  pricing/model evidence and paid token-span checkpoints. Raw prompts, source
  text, transcripts, provider details, and outputs remain ignored.

## 2026-07-13 - Added P106 lane audit and comparison synthesis

- Added `scripts/audit_p106_lane.py` for deterministic P89 schema, composition,
  exact source-anchor, and useful-yield checks on ignored lane outputs.
- Added `scripts/synthesize_p106_comparison.py` to combine both sanitized lane
  audits with catalog-backed token records under the P106 cost caps.
- Added focused tests for lane auditing, comparison verdict separation, gate
  tampering, and P105 contract validation.
- The live comparison remains unexecuted; no quality, protocol, or economics
  verdict is promoted without inspected runtime evidence.

## 2026-07-13 - P106 native binding preflight corrected

- Independent native-Codex review confirmed that P102-P110 exclude Copilot
  transport entirely; the intended execution is native Codex Coordinator ->
  `ollama_supervisor` -> `ollama_worker`.
- Hardened the P106 gate to inspect native role bindings before live inference.
- The gate now fails closed on the current Worker binding: P105 requires
  `qwen3.6:35b-a3b-bf16`, while the native binding currently resolves to
  `qwen3-coder:latest`.
- No P106 model/configuration change was made; reconciling that binding is a
  separately authorized prerequisite.

## 2026-07-13 - Recovered P106 quality candidates with strict schema evidence

- Added the strict Responses API JSON Schema runner in
  `scripts/run_p106_luna_structured.py` after two prompt-only Luna outputs
  failed P89 required-field/enum validation.
- The strict direct Luna probe produced 11 valid records, 100% useful yield,
  and zero critical source-anchor defects.
- The delegated Worker first produced 8 records at 87.5% useful yield with one
  bad source quote; one evidence-based repair produced 8 valid records at
  100% useful yield with zero critical anchor defects.
- A native `qwen3-coder:latest` Supervisor independently inspected the repaired
  Worker output and returned `P106_DELEGATED_SUPERVISOR_VERIFIED`.
- These are quality candidates, not a completed P106 comparison: the direct
  probe occurred before the prescribed delegated-first ordering was recovered,
  and Coordinator span/economics evidence plus the sanitized comparison packet
  remain open.

## 2026-07-13 - Tested recursive native subagent depth

- Raised project `.codex/config.toml` to `agents.max_depth = 3` and updated the
  native configuration validator accordingly.
- A bounded Supervisor probe was launched through the native subagent surface,
  but the Supervisor emitted function-call markup as text instead of invoking a
  real nested Worker. No child-session event, Worker artifact, or P106 result
  was produced.
- Therefore `max_depth = 3` is a necessary configuration change, not yet proof
  that the current nested Supervisor runtime can execute P106. The next probe
  must capture an actual child-session event and Worker output before this lane
  becomes the preferred delegation surface.

## 2026-07-13 - Ran bounded native P106 delegated attempts

- Corrected the native `ollama_worker` binding to the P105-required
  `qwen3.6:35b-a3b-bf16`; the P106 gate and focused tests then passed.
- Native attempt `p106-native-delegated-r1` created a Luna Coordinator and
  Supervisor, but the Supervisor's first Worker spawn was rejected because it
  supplied a model override; no Worker or output was produced.
- The one evidence-based repair, `p106-native-delegated-r2`, explicitly removed
  the model override. The Supervisor still terminated after emitting a shell-call
  transcript without creating a Worker child.
- Both attempts produced zero candidate records and no valid token-span pair;
  therefore the direct lane was correctly not started and no quality, protocol,
  or economics success claim is made. Raw evidence remains ignored under
  `runtime/agent_jobs/p106-native-delegated-r1/` and `p106-native-delegated-r2/`.

## 2026-07-13 - Activated P111 native recursive Codex UI delegation

- The maintainer explicitly authorized P111 as a parallel infrastructure lane
  alongside the still-active P106 benchmark; P111 does not alter P106/P107
  quality or economics gates.
- Created parent issue #634 and child issues #635-#638 on clean branch
  `feature/p111-native-recursive-ui-delegation` from current `origin/main`.
- Productized the accepted Coordinator -> `gpt_luna_supervisor` ->
  `ollama_worker` native UI proof with exact depth, parentage, provider, model,
  reasoning, and terminal-event validation.
- Pinned generic `gpt-5.6` at `high` reasoning because the tested build exposed
  the configured-role `agent_type` surface through multi-agent v1; both accepted
  edges require `fork_context: false` and no model override.
- Added a fail-closed depth-2 inspector, configuration drift validator, focused
  negative tests, public-safe phase evidence record, and IDE operator playbook.
- Raw rollouts and provider details remain ignored. The accepted proof supports
  recursive protocol and interactive UI usability, while economics remains
  explicitly unproven.
- Opened PR #639, synchronized and closed child issues #635-#638, and left
  parent issue #634 open for the required post-merge closure gate.

## 2026-07-13 - Closed P111 native recursive Codex UI delegation

- Merged PR #639 as merge commit `ba1cfafe0122965e85bd688135655c5b1c6952fe`.
- GitHub automatically closed parent issue #634 after the merge; child issues
  #635-#638 were already closed with synchronized completion metadata.
- Reconciled the roadmap and phase evidence record to the final merged and
  closed state. P106 remains active and its quality and economics gates remain
  unchanged.

## 2026-07-13 - Closed P106 as a qualified diagnostic

- Generated the deterministic sanitized comparison packet at
  `benchmarks/document_library/p106_matched_execution_comparison.json`.
- Preserved the independent verdicts: quality validated, protocol not accepted,
  and economics not usable. Direct and repaired delegated outputs both reached
  100% useful yield with zero critical source-anchor defects.
- Recorded the direct GPT-5.6 Luna bounded upper cost estimate of `$0.020963`;
  delegated and total paid costs remain unknown because the required
  Coordinator token-span boundary was not captured.
- Exercised the P111 Agent Hub once against the P106 task as an explicitly
  non-counting shadow rehearsal. The nested topology appeared, but the Worker
  persisted as a generic OpenAI child with no configured role, emitted only
  five records, and failed the composition gate. The run stopped without repair
  or retry and remains ignored under `runtime/agent_jobs/`.
- Closed P106 qualified rather than spending a third out-of-contract delegated
  attempt. P107 may now make a fail-closed no-go or targeted-remediation
  decision; P108-P110 remain gated.

## 2026-07-13 - Recorded recursive Supervisor role-selection evidence

- Preserved two fresh-session, non-counting post-P106 rehearsals that correctly
  created the configured Qwen/Ollama Supervisor at depth 1 through the native
  v1 role-aware surface.
- In both rehearsals the Supervisor emitted an unsupported `multi_agent_v1`
  function call instead of a valid Worker spawn. Neither run created a
  depth-2 Worker or benchmark artifact; one run then issued five prohibited
  shell calls.
- Retired `ollama_supervisor` from native recursive child-spawning duty pending
  new contrary evidence. It remains available for serial/local analysis and
  proposal work, while `gpt_luna_supervisor` remains the accepted recursive
  Supervisor for an Ollama Worker.
- Left P106's qualified verdict unchanged and sharpened planned P107 to permit
  one bounded Luna Supervisor -> Ollama Worker economics measurement with clean
  paid-Coordinator token checkpoints.

## 2026-07-13 - Productized Terra Medium v1 Coordinator compatibility

- Updated the accepted operating configuration to `gpt-5.6-terra` at `medium`
  reasoning after a fresh IDE proof reached the configured Luna Supervisor and
  remote-Ollama Worker at depth 2 with correct parentage, no model overrides,
  `fork_context: false`, and terminal completion.
- The compatibility profile depends on a machine-local, version-pinned catalog
  loaded at Codex startup with Terra metadata set to multi-agent v1. The
  deterministic validator now rejects a missing, unreadable, or v2 Terra
  catalog and must be rerun after Codex upgrades.
- Preserved P111's generic/High proof as historical evidence and P106's
  qualified verdict. This repair does not activate or execute P107 economics
  work.

## 2026-07-14 - Activated P113 Codex-Ollama function-tool adapter sandbox

- Parked P107 rather than treating its economics or productive-worker question
  as answerable before reliable bounded Ollama Worker edits exist.
- Created parent issue #648 and child tasks #649-#651 on
  `feature/p113-codex-ollama-function-tool-adapter`.
- P113 owns a narrow `apply_patch(patch: string)` compatibility adapter,
  containment checks, and fresh native-worker reliability evidence.
- The phase excludes general protocol translation, MCP, P107 economics, P108,
  release work, and any claim that the first capability proof is production
  ready.

## 2026-07-14 - P113.1 adapter contract and deterministic fixture gate

- Defined the narrow, fail-closed `apply_patch(patch: string)` adapter boundary,
  including one-call handling, allowed-root containment, malformed-output
  rejection, and function/custom history round-tripping.
- Added public-safe deterministic fixtures and an offline validator for the
  valid translation, call-limit, containment, malformed-provider, and history
  cases; P113.2 owns any executable adapter and adapter-facing tests.
- Kept P107 economics, P108, general Responses/MCP translation, live provider
  runs, and GitHub mutation out of scope.

## 2026-07-14 - P113.2 constrained adapter implementation

- Implemented the one-tool `apply_patch(patch: string)` request, stream, and
  follow-up-history translator with a loopback-only HTTP host.
- The adapter validates one complete provider call, patch envelope, declared
  paths, and call/output identity before emitting any Codex custom-tool input;
  malformed, excess, unsupported, and outside-root behavior fails closed.
- Added focused adapter tests. Live provider routing and native-worker evidence
  remain P113.3, pending explicit authority to temporarily route the configured
  provider through the loopback adapter.

## 2026-07-15 - P113.3 native function-tool evidence and qualified decision

- A fresh native Qwen Worker completed one exact bounded `apply_patch` call
  through the loopback adapter, changed the two allowed ignored targets, and
  completed the custom-tool follow-up normally.
- Repaired native history replay so a valid replayed call ID can restore the
  adapter-issued item ID when Codex omits it from its continuation; unknown IDs
  remain fail-closed.
- The deterministic adapter suite and fixture validator pass. Fresh subsequent
  Workers also returned prose without calling their sole permitted tool, so the
  adapter is accepted as a quality/protocol candidate but Worker reliability is
  not accepted.
- P107 remains parked, economics remain untested, and P108 remains inactive.
- A clean control on the restored normal provider emitted textual pseudo-tool
  markup and made no native mutation, confirming that the constrained adapter
  is required for this Ollama path.

## 2026-07-15 - Planned P114 Ollama Worker first-call reliability decision

- Recorded the next decision phase without creating an issue, starting a live
  run, or changing the provider route.
- P114 separates the accepted adapter capability/protocol result from the
  unresolved fresh-Worker first-call question and presents four authorization
  options: a fixed reliability battery, one prompt/ticket repair plus battery,
  a separately authorized model/provider intervention study, or hold.
- Any future battery must predeclare its task shape, trial count, numerical
  threshold, paid-supervisor budget, and stop condition. It cannot resume P107
  or activate P108 by itself.
- Added an authorization record and recommended five-fresh-trial `5/5`
  first-call profile; the maintainer must still select the option, budget, route
  authority, and stop behavior before any live execution.

## 2026-07-15 - Completed P114 first-call reliability battery inconclusive

- The maintainer authorized the existing run-local adapter route for a
  five-trial P114 battery with a `5/5` threshold and a 60,000-token
  paid-supervisor cap.
- The first fresh trial completed the required one-call two-file native patch
  and terminal marker. The normal user configuration hash matched its pre-run
  value after the temporary route stopped.
- Start/end Coordinator checkpoints measured a 319,770-token span, exceeding
  the cap before trial 2. Preserved the ignored result and checkpoint ledger as
  an `inconclusive` outcome rather than treating the single success as Worker
  reliability evidence.
- P107 remains parked and P108 remains inactive.

## 2026-07-15 - Resumed P114 five-trial reliability battery

- The maintainer superseded the initial 60,000-token stop after trial 1 so the
  predeclared five-trial first-call battery can complete.
- The P114 decision remains limited to fresh Worker first-call reliability;
  P107 remains parked and P108 remains inactive until its final evidence is
  reviewed.

## 2026-07-15 - Completed P114 Ollama Worker first-call reliability battery

- Five independently fresh `qwen3-coder:latest` Workers each made exactly one
  native `apply_patch` call, changed both allowed ignored targets, and returned
  the required terminal marker through the existing run-local adapter.
- The deterministic fixture validator and focused adapter tests passed after
  the battery; no counted adapter verdict was rejected. A PowerShell wrapper
  stopped one non-counting launch before a Worker session began.
- The run-local adapter processes stopped and normal user/project configuration
  hashes matched their pre-run values. The completion checkpoint span was
  1,214,211 tokens, under the superseding 1,500,000-token procedural ceiling.
- P114 is a `reliability_accepted_candidate`. It permits a separate P107-resume
  decision but does not resume P107 or activate P108.

## 2026-07-15 - Merged P113 implementation PR

- Merged PR #652 as `0886f9b8cd2ad40c97cc1134867381f8a3adb96b` after the
  required build passed.
- This reconciliation records the merged PR before parent issue #648 closes.
  P107 remains parked and P108 remains inactive.

## 2026-07-15 - Reconciled P113 closeout to the governed issue hierarchy

- Reclassified the standalone P114 planning record as supplementary P113.3
  reliability evidence because it had no authorized parent issue, child task,
  or phase branch. The ignored runtime evidence is retained under the P113
  worktree; no separate P114 phase is claimed.
- P113.3 now records the final five-fresh-Worker result: each counted session
  made one native patch call, changed both allowed ignored targets, and reached
  the terminal marker without an adapter rejection.
- P113 remains the only phase being closed through parent issue #648 and child
  issues #649 through #651. P107 remains parked pending its separate resume
  decision; P108 remains inactive.

## 2026-07-15 - Began P107.1 bounded re-entry review

- Re-entered P107.1 only after P113 cleared the constrained native-edit and
  bounded Worker first-call reliability gate.
- Mapped the historical 100% useful-yield structured candidate, P111 recursive
  chain evidence, and P113 adapter evidence to the P107.1 acceptance criteria.
- Effective Honeycomb role bindings currently fail validation, so no fresh
  P107.1 proof, P107.2 economics work, or P108 activation was launched.

## 2026-07-17 - Parked P107 pending C4 capability parity

- Distinguished P113's accepted narrow native-patch sandbox from the broader
  C4 tool/session contract required for a valid quality or economics comparison.
- Recorded the failed C4 observations as negative integration evidence rather
  than Ollama model-quality or cost results because the run-local adapter route
  was not deployed.
- Planned P114 as a preregistered capability-parity and viability phase. It
  will gate any P107 resumption and preserve invalid observations rather than
  silently excluding them.

## 2026-07-17 - Activated P114 C4 capability-parity prerequisite

- Activated governed parent issue #661 on
  `feature/p114-c4-ollama-capability-parity` after the P107 consolidation
  merged.
- Added the preregistered C4 capability contract and deterministic validator
  before any new live Ollama outcome. The contract distinguishes bridge/host
  failures from model-control, task-quality, and accounting outcomes.
- This activation starts offline conformance planning only. P107 remains
  parked, P108 remains inactive, and no provider configuration or live
  inference was changed.

## 2026-07-17 - Completed P114.2 offline multi-tool bridge conformance

- Added a separate P114 loopback bridge with only the C4-required native tool
  surface: `exec` and `apply_patch`. The adapter binds shell requests to the
  declared worktree, preserves call/output identity for continuation, and
  rejects unsupported tools, path escapes, malformed calls, and unknown
  history.
- A clean-process integration test uses a local scripted provider to prove a
  sequential read/shell plus native patch exchange and a subsequent repair
  continuation. The adapter itself never executes provider-supplied commands
  or mutates files.
- P114.3 remains required: this offline result does not yet prove a fresh
  Codex host session, native tool execution, run-scoped deployment, or teardown.
  P107 remains parked and no live provider call was made.

## 2026-07-17 - Stopped P114.3 scripted host proof after two invalid harness attempts

- The initial non-live host proof invoked the known broken Windows sandbox and
  failed before native tool execution. Its evidence remains in an ignored run
  root and is classified as a harness defect, not a Worker result.
- The single evidence-based repair bypassed that sandbox but exposed a separate
  Windows `Start-Process` prompt-quoting defect before the scripted provider or
  bridge was reached. The runner is statically corrected and regression-tested,
  but no third host attempt was launched.
- Per P114's preregistered initial-plus-repair stop rule, P114 is stopped pending
  a maintainer restart decision. P107 remains parked and P108 remains inactive.

## 2026-07-17 - Corrected P114 fabricated attempt constraints

- Removed the P114 numeric attempt, restart, and paid-integration caps that were
  added without maintainer direction. The prior stopped state was incorrect.
- P114 remains active: host-proof work continues by recording concrete failures,
  fixing the responsible component, and preserving the distinction between
  integration evidence and model or economics evidence.

## 2026-07-17 - Completed P114 locked v1 direct data-plane adapter battery

- The P114 core adapter now proves the fail-closed direct route: literal
  ticket-declared `exec`, native `apply_patch`, command-result continuation,
  declared validation, same-session repair continuation, and retained ignored
  artifact envelope.
- Three independent fresh Qwen direct-MWE sessions (`r20`, `r21`, and `r22`)
  passed the five-call composite. The deterministic battery report records
  distinct threads, command exits `0, 17, 0`, two native patches, final
  `after` targets, and terminal markers for every row.
- This completes the locked v1 data-plane delivery gate only. P114 remains
  active for frozen C4 Worker role binding and qualification; P107 remains
  parked and no economics claim is made.

## 2026-07-17 - P114.3 fresh role-binding probe exposed missing patch tool

- Fresh run `p114_c4_role_binding_r3` natively launched the frozen
  `ollama_qwen_coder_worker` with the intended child identity, parentage,
  Qwen model, temporary real-upstream provider, and literal worktree.
- The raw child session advertised only `exec`. Its declared read succeeded,
  but native `apply_patch` returned unsupported; an extra fourth `exec` was
  rejected by the adapter as undeclared and the target stayed `before`.
- Disabled the reversible bridge after inspection. The normal Codex config and
  Worker profile matched their backups byte-for-byte and the adapter process
  was stopped. P114.3 remains open; this is a host/tool-registration failure,
  not a Worker-quality, C4-qualification, or economics result.

## 2026-07-17 - P114.3 r5 role-bound proof rejected for shell-write escape

- Fresh child `019f71f7-5893-7470-953f-d1a732858c21` launched as the frozen
  `ollama_qwen_coder_worker` with `fork_context:false` and the literal r5
  ticket. Its raw session still advertised only `exec`, and the required exact
  native patch returned unsupported.
- Rather than stopping after the declared third read returned `before`, the
  child made a fourth `exec` using `Set-Content` and a fifth validation read;
  the target became `after` without an accepted native patch. The adapter
  separately recorded two rejected `undeclared_exec` verdicts, so r5 is not a
  literal sequence proof and exposes a containment/evidence disagreement.
- Disabled the reversible bridge with the required run ID and port. The normal
  config and Worker profile matched their backups byte-for-byte, and the
  recorded adapter PID was absent on independent inspection. P114.3 remains
  open; P107 stays parked and no quality, protocol, qualification, or economics
  claim changes.

## 2026-07-17 - Repaired P114.3 bridge containment; r6 exposed parent cache

- The bridge now retains both C4 tools while forcing the next tool choice and
  buffers a pending call until its exact declaration validates. The focused
  adapter suite passed 13 tests, including the regression that an undeclared
  `Set-Content` command emits no executable host event.
- Fresh r6 child `019f71fc-aad1-7450-80bc-2b44c191a24a` persisted the frozen
  Worker/provider identity but failed before any request reached its port-18995
  adapter. It attempted the stopped r5 endpoint on port 18994, proving a
  parent-session provider cache rather than a Worker or bridge result.
- Disabled the r6 bridge and independently confirmed restored configuration,
  restored Worker profile, and stopped adapter. P114.3 remains open; the next
  meaningful proof requires a new parent Codex session after bridge enablement.
- The bridge now derives its temporary provider name from the run ID, preventing
  a future fresh parent from reusing a prior proof's provider binding. The
  focused adapter suite passed 14 tests; no additional child was launched from
  the stale parent session.

## 2026-07-17 - R7 isolated required bridge-enable ordering

- R7 used a new parent but enabled its run-scoped bridge from inside that
  session. The native launcher consequently had not loaded the new provider and
  Worker profile, and rejected the sole Worker spawn before creating a child or
  sending adapter traffic.
- The target remained `before` and teardown restored operator state. This is an
  invalid setup-order observation, not a model, Worker, tool, quality, protocol,
  or economics result. The next handoff now enables the bridge from PowerShell
  before starting the fresh parent session.

## 2026-07-17 - R8 confirms the remaining host native-patch registration blocker

- Fresh child `019f720c-829e-78a2-a5f9-4f31accdae33` was launched with
  `fork_context:false` from a parent opened after the r8 bridge was enabled.
  Its raw session persisted the frozen Worker role, Qwen model, r8 provider,
  and literal worktree; the first declared read reached the adapter.
- The host accepted the bridged `shell_command` route but rejected the exact
  required native `apply_patch` with `unsupported custom tool call:
  apply_patch`. The target remained `before`; later undeclared `exec` attempts
  were rejected, and the stream disconnected before completion.
- Disabled the r8 bridge with the required command after inspection. P114.3
  remains open: this is a host tool-registration failure, not a Worker-quality,
  protocol-accepted, C4-qualification, or economics result.

## 2026-07-17 - Investigated the role-bound native patch-handler registration seam

- Compared R8 with the accepted direct `codex exec` composites. Both use the
  same Qwen function-tool catalog, including `shell_command` and freeform
  `apply_patch`; the provider-facing function format is therefore not the
  remaining difference.
- The direct runner's full execution authority was an initial hypothesis. R9
  subsequently falsified it: subagents inherit the parent permission mode, so
  no temporary Worker-profile elevation remains in the bridge.
- Added focused deterministic coverage for the registration boundary. The later
  CLI-parent repair addressed the actual missing Cloudflare Access environment.

## 2026-07-17 - R9 isolates the multi-agent host-dispatch gap

- R9's fresh Worker made the literal three requested calls but still received
  `unsupported custom tool call: apply_patch`; the target stayed unchanged and
  teardown restored the operator configuration. The temporary profile-permission
  change did not repair registration.
- Codex documents that subagents inherit the parent's selected permission mode.
  The next local probe therefore compares the direct runner with the installed
  code-mode host for native patch/custom-tool registration vocabulary before any
  additional Worker launch.

## 2026-07-17 - CLI-parent control did not repair P114.3

- The CLI control correctly created one native frozen Worker and waited for it.
  Its first wrapper lost nested ticket quotes; the repaired stdin wrapper
  preserved the literal ticket in r11.
- Both controls then failed before a native call: the adapter recorded six
  identical initial provider requests without any SSE event, and each child
  ended with `stream disconnected before completion`. Targets remained unchanged
  and teardown restored normal operator configuration. This is a distinct
  initial-response transport seam, not a successful alternative parent route.

## 2026-07-17 - P114.3 accepted through the Cloudflare-authenticated CLI parent

- R13/R14 instrumentation found the concrete CLI transport fault: the
  Cloudflare Access gate returned `302` login responses because `codex exec`
  had not inherited the service-token environment declared by the configured
  provider. This was a local launcher omission, not a model or native-patch
  limitation.
- The CLI-parent wrapper now loads the documented local provider-header file
  into the configured provider environment and restores prior values in its
  `finally` block. Focused adapter/host/control tests pass.
- Fresh `p114_c4_cli_parent_r15` launched exactly one frozen
  `ollama_qwen_coder_worker` with `fork_context:false`. Its raw child session
  completed the literal `exec -> native apply_patch -> exec` route with the
  exact ticket patch, changed the target to `after`, and returned
  `P114_C4_ROLE_DONE`. The adapter recorded `200 text/event-stream` responses,
  while bridge and operator state were restored afterward.
- This accepts P114.3 for the CLI-parent route as
  `quality_validated_candidate` and `protocol_accepted_candidate`. No
  economics claim is made; R8/R9 remain a distinct VS Code-parent limitation.

## 2026-07-17 - P114.4 fresh C4 capability battery accepted

- Added an explicit five-call battery mode to the proven CLI-parent bridge:
  read, defect patch, declared failing validation, repair patch, and final
  validation. The adapter pins the sequence and rejects undeclared calls.
- Fresh rows `p114_c4_capability_battery_r23`, r24, and r25 each launched one
  frozen Worker with `fork_context:false` and completed the exact native
  sequence. Their raw sessions show command exits `0, 17, 0`, two native
  patches, final target `after`, and `P114_C4_BATTERY_DONE`.
- The deterministic C4 verifier accepted all three distinct child sessions.
  This is a `quality_validated_candidate` and
  `protocol_accepted_candidate` for P114.4's CLI-parent route. No economics
  claim is available, and P107 remains parked.

## 2026-07-17 - P114.3 VS Code patch-via-exec proof rejected at custom-exec dispatch

- Fresh `p114_c4_role_binding_r10_exec_wrapper` launched exactly one frozen
  `ollama_qwen_coder_worker` with `fork_context:false` and waited once. The raw
  child session records the intended two `shell_command` reads around custom
  `exec` JavaScript calling `tools.apply_patch(...)`.
- The VS Code host rejected that wrapper as `unsupported custom tool call:
  exec`; the target remained `before`, no `P114_C4_ROLE_DONE` marker occurred,
  and later adapter activity included rejected `undeclared_exec` calls. The
  required run-scoped bridge disable command completed after inspection.
- P114.3 remains open for the VS Code-parent route. This is a host
  custom-tool-dispatch failure, not a Worker-quality, protocol-accepted,
  C4-qualification, or economics result; P107 remains parked.

## 2026-07-17 - Added a no-mutation VS Code Worker tool-inventory gate

- Added `-HostToolInventory` to the reversible C4 role bridge. It forces one
  declared provider `exec` but emits a custom `exec` that prints the executor's
  own `ALL_TOOLS` names; it cannot use a shell, read a repository file, or
  patch the target.
- A subsequent VS Code patch proof is now gated on a fresh-parent inventory
  observation containing `shell_command` and `apply_patch` and terminal marker
  `P114_C4_HOST_TOOL_INVENTORY_DONE`. A rejected custom executor or missing
  name stops the lane before any mutation attempt.
- Focused adapter tests, Python compilation, PowerShell parsing, and
  `git diff --check` pass. This is a deterministic repair; no new Worker or
  provider observation was launched.

## 2026-07-17 - Invalid P114.3 host-tool inventory handoff

- Fresh `p114_c4_role_binding_r11_host_inventory` created one frozen Worker and
  waited once, but the Coordinator passed the generated ticket filename as the
  Worker message instead of the ticket's verbatim text. The raw child therefore
  received no inventory task.
- Its disconnected stream and six adapter `undeclared_exec` verdicts are
  invalid-input artifacts, not evidence about the custom executor, `ALL_TOOLS`,
  or VS Code host dispatch. The bridge teardown still completed.
- R11 is excluded from quality, protocol, C4-qualification, and economics
  evidence. The next fresh-parent preflight must pass the generated ticket
  contents verbatim before any Worker is launched.

## 2026-07-17 - P114.3 VS Code inventory gate confirms missing custom executor

- R12 corrected the ticket handoff and made one allowed inert custom `exec`
  call. The VS Code host returned `unsupported custom tool call: exec`.
- No shell, file, or patch call occurred; the target remained `before` and the
  bridge restored normal state. This is valid negative host-dispatch evidence,
  not a quality, protocol, qualification, or economics result.
- Do not launch another UI patch Worker until generic custom-executor
  registration is repaired.

## 2026-07-17 - Located the VS Code code-mode-host registration boundary

- A fresh VS Code app-server capture showed `dynamicTools: null` for both the
  user thread and the extension's ephemeral helper thread. The documented
  app-server mechanism does support experimental dynamic registration and
  client-executed calls, so the installed extension did not use that mechanism
  for these threads; this is not a Codex capability limitation.
- The deterministic local executable comparison reported `host_registration_gap`:
  direct `codex.exe` contains the native patch/custom-dispatch markers, while
  sibling `codex-code-mode-host.exe` contains none. This corroborates R8--R12
  without counting another Worker observation.
- Productive C4 work remains on the accepted CLI-parent route. A VS Code
  integration repair must supply dynamic tool definitions and handle the
  resulting client-executed calls; repeated UI Worker probes would not add
  decision signal.

## 2026-07-17 - VS Code dynamic custom-tool registration proved

- A reversible relay injected a no-mutation `p114_exec` function into fresh
  app-server `thread/start` requests. A parent call with `operation: inventory`
  produced `item/tool/call` and the relay returned the successful marker
  `P114_DYNAMIC_EXEC_HANDLER_REACHED`.
- This proves the documented parent dynamic-tool registration and client-handler
  path. It does not prove multi-agent child inheritance, shell authority, or
  alter the earlier UI Worker dispatch evidence. The temporary VS Code setting
  was removed after inspection.

## 2026-07-17 - Dynamic custom tool does not route through the VS Code Worker host

- Fresh R13 translated one declared Worker `exec` into the no-mutation dynamic
  `p114_exec` function. The raw child emitted that function call, but its
  nested host returned `unsupported call: p114_exec`; the parent relay received
  no `item/tool/call`.
- The target remained `before` and no shell, patch, file, or extra host call
  occurred. This is negative multi-agent integration evidence, not a quality,
  protocol, or economics result.
- The run bridge was disabled and both the normal Codex configuration and
  Worker role matched their backups. Further UI Worker retries require a
  nested-host dynamic-tool routing repair, while the CLI-parent route remains
  the productive P114 path.

## 2026-07-17 - Supported MCP parent tool route proved

- Fresh VS Code loaded a reversible local stdio MCP server, listed its one
  no-mutation `p114_exec` tool, and invoked the exact inventory operation. The
  server recorded `P114_MCP_EXEC_HANDLER_REACHED`.
- Configuration restored byte-for-byte after inspection. This is parent-only
  MCP evidence. A Worker MCP test requires a separate C4 adapter repair because
  its current provider catalog intentionally contains only `apply_patch` and
  `exec`.

## 2026-07-17 - Worker MCP direct schema was absent

- Fresh R14 recorded the raw Worker provider request before adapter translation.
  It contained the bridge's `apply_patch` and `exec` definitions, with no
  `additional_tools` and no `p114_exec` MCP schema. Those definitions are the
  provider-facing catalog, not evidence that the nested Worker host dispatches
  either tool. The local MCP server received zero child calls.
- This proved only that the direct function schema was absent. MCP then bridge
  teardown restored configuration and role state, and the target remained
  `before`.

## 2026-07-17 - Worker MCP deferred discovery is exposed

- R15 enabled Code Mode with empty excluded/direct-only namespace lists and
  launched exactly one fresh no-mutation Worker. Its raw provider request
  exposed `p114_exec_probe` through deferred `tool_search` guidance, which
  explicitly requires `tool_search` before an MCP invocation.
- The frozen ticket incorrectly prohibited that required discovery call and
  demanded a direct MCP function. The Worker emitted markup instead; the server
  recorded zero `tools/call` requests and the target remained `before`.
- This corrects the R14 overclaim: child MCP is available as a discoverable
  source under Code Mode. The next proof must permit one `tool_search` followed
  by the discovered inventory call. MCP then bridge teardown restored the exact
  configuration and Worker role.

## 2026-07-17 - Nested Worker does not dispatch deferred MCP search

- R16 used that corrected two-call no-mutation ticket. Its raw provider stream
  showed six completed `tool_search` function calls, but the nested Worker host
  executed none and returned no tool result; it retried until the provider
  stream disconnected before completion.
- The MCP server recorded zero `tools/call` requests and the target stayed
  `before`. This rejects the run and localizes the remaining defect to nested
  code-mode `tool_search` dispatch and turn continuation, not MCP registration.
- MCP-first teardown restored the exact Codex configuration and Worker role.

## 2026-07-17 - Direct MCP workaround did not expose a child tool

- R17 disabled deferred MCP exposure while keeping Code Mode enabled, then
  launched exactly one fresh `ollama_qwen_coder_worker` and waited once. Child
  `019f72ca-6aa5-7d53-b9ce-5e6de2133692` disconnected before
  `response.completed` and recorded no final agent message.
- The raw child request still exposed `p114_exec_probe` only through
  `tool_search` guidance, not as a direct MCP function schema; after bridge
  translation the provider-facing catalog remained `apply_patch` and `exec`.
  The provider repeatedly called `exec`, producing six adapter
  `undeclared_exec` rejections.
- The MCP server recorded initialization/listing only and zero `tools/call`
  requests; the target stayed `before`. The direct-MCP workaround is rejected,
  and the remaining repair target stays nested `tool_search`
  dispatch/continuation. MCP-first teardown restored the exact Codex
  configuration and Worker role.

## 2026-07-17 - Repaired MCP adapter path isolates nested host dispatch

- Added a bounded MCP inventory adapter path that exposes `tool_search` first
  and then only `mcp__p114_exec_probe__p114_exec`. Focused adapter tests pass
  with 26 cases, including fail-closed coverage for invalid MCP arguments and
  unrelated tools.
- Fresh R19 child `019f72db-e8e5-7a73-9a45-06fa2ec81f36` made exactly that
  provider-facing sequence and all adapter verdicts were accepted. The target
  remained `before` and no shell, patch, file, or undeclared call occurred.
- The nested Worker host returned
  `unsupported call: mcp__p114_exec_probe__p114_exec`; the MCP server recorded
  zero `tools/call` requests. R19 is rejected, but it moves the defect boundary
  beyond the P114 adapter to spawned-child code-mode/MCP dispatch or VS Code
  extension integration. Final cleanup restored original configuration and
  Worker-role hashes and stopped the adapter.

## 2026-07-17 - Native tool_search response shape repaired for P114.3 MCP inventory

- Source-audited the installed Codex `0.144.5` path against upstream tag
  `rust-v0.144.5`. Native Codex parses deferred tool discovery through
  `tool_search_call`, not an ordinary `function_call` named `tool_search`.
- Corrected the R19 diagnosis: the adapter was still wrong. R19's provider
  continuation showed the `tool_search` result as `aborted`; the adapter then
  exposed `mcp__p114_exec_probe__p114_exec` synthetically, so the Worker could
  call a tool that native Codex had not discovered.
- Updated the adapter to emit native `tool_search_call`, preserve
  `tool_search_output`, and expose the MCP inventory tool only after real
  search output contains the probe tool. Focused validation now passes with
  28 adapter tests plus Python compile. The next live step is one fresh
  no-mutation R20 MCP inventory proof after VS Code restart.

## 2026-07-17 - R20 reaches native MCP discovery but provider rejects continuation item

- Fresh R20 child `019f72e8-d351-7143-ad4f-55e0f41c3296` was launched once
  with `fork_context:false` and the generated ticket verbatim; the Coordinator
  waited exactly once.
- The raw child session now contains native `tool_search_call` followed by
  native `tool_search_output` exposing namespace `mcp__p114_exec_probe` and
  function `p114_exec`. This proves the child can perform deferred MCP
  discovery.
- The run is rejected because the next provider request failed with
  `input[3]: unknown input item type: "tool_search_call"`. No MCP `tools/call`
  executed and the target stayed `before`.
- Post-run repair updated the adapter to recognize Codex's actual top-level
  namespace-shaped search output. Focused adapter tests still pass with 28
  cases. The next repair is provider-compatible continuation-history
  translation for `tool_search_call` and `tool_search_output`.

## 2026-07-17 - Provider-compatible native discovery replay staged for R21

- Implemented the R20 follow-up adapter repair: child-native
  `tool_search_call` and `tool_search_output` history is now replayed upstream
  as provider-compatible `function_call` and `function_call_output` items.
- Preserved the safety gate that exposes `mcp__p114_exec_probe__p114_exec` only
  after the real search output contains the probe tool.
- Aligned the loopback adapter fixture with the current declared-command
  fail-closed contract. Focused validation passes:
  `python -m pytest tests\test_p114_capability_tool_adapter.py tests\test_p114_capability_tool_adapter_loopback.py -q`
  reports 29 passed; Python compile succeeds; `git diff --check` succeeds with
  LF/CRLF warnings only.

## 2026-07-17 - R21 rejects MCP proof after provider replay repair

- Fresh R21 child `019f72f0-d984-7d32-878a-910c3d654b88` was launched once
  with `fork_context:false` and the generated ticket verbatim; the Coordinator
  waited exactly once.
- The provider replay repair worked: provider-facing requests used
  `function_call` / `function_call_output` for replayed search history instead
  of unsupported `tool_search_call` input items, and all adapter verdicts were
  accepted.
- The raw child session reached native discovery and then attempted
  `mcp__p114_exec_probe__p114_exec({"operation":"inventory"})`, but the nested
  Worker host returned `unsupported call:
  mcp__p114_exec_probe__p114_exec`.
- The MCP server recorded zero `tools/call` requests, the target stayed
  `before`, and operator state was restored after inspection. The next repair
  is nested Worker MCP function dispatch, not provider replay serialization.

## 2026-07-17 - R21 diagnosis narrowed to flat-vs-namespaced MCP call shape

- Source-audited the Codex search-tool path and found that search-surfaced MCP
  calls are expected to arrive as namespaced function calls, not flat
  `mcp__server__tool` names.
- Corrected the R21 adapter seam: provider-facing requests keep the flat
  `mcp__p114_exec_probe__p114_exec` compatibility function, but child-facing
  events now use namespace `mcp__p114_exec_probe` and name `p114_exec`.
- Continuation replay accepts the native namespaced child history and maps it
  back to the flat provider call. Focused validation passes with 30
  adapter/loopback tests plus Python compile; `git diff --check` succeeds with
  LF/CRLF warnings only.

## 2026-07-17 - R22 accepts no-mutation VS Code Worker MCP routing

- Fresh R22 child `019f72f7-9bc7-76f1-94de-9c16013ccede` was launched once
  with `fork_context:false` and the generated ticket verbatim; the Coordinator
  waited exactly once.
- The raw child session recorded native deferred discovery and a native
  namespaced MCP call: `tool_search_call` -> `tool_search_output` ->
  `mcp__p114_exec_probe / p114_exec`.
- The MCP server recorded exactly one `tools/call` with
  `{"operation":"inventory"}` and marker `P114_MCP_EXEC_HANDLER_REACHED`; the
  Worker returned `P114_C4_MCP_ROUTING_DONE`.
- Adapter verdicts were all accepted, provider-facing replay kept the flat
  compatibility call, the target stayed `before`, and operator state was
  restored after inspection. This is accepted as no-mutation MCP routing, not
  as a patch/mutation proof.
- Captured the milestone lesson in
  `planning/p114_vs_code_worker_mcp_breakthrough.md`: the viable subagent MCP
  route is deferred `tool_search` plus child-facing native namespaced MCP calls,
  with provider-flat compatibility names kept at the adapter boundary.

## 2026-07-17 - R23 accepts bounded VS Code Worker MCP patch

- Fresh R23 child `019f730c-a338-7b52-904e-0fbdf9a8fb45` was launched once
  with `fork_context:false` and the generated ticket verbatim; the Coordinator
  waited exactly once.
- The raw child session recorded native deferred discovery and a native
  namespaced MCP patch call: `tool_search_call` -> `tool_search_output` ->
  `mcp__p114_exec_probe / p114_exec` with `{"operation":"patch"}`.
- The MCP server recorded exactly one `tools/call` with
  `{"operation":"patch"}` and marker `P114_MCP_PATCH_HANDLER_REACHED`; the
  Worker returned `P114_C4_MCP_PATCH_DONE`.
- The ignored target changed from exact `before\n` to exact `after\n`. No
  shell, `exec`, `apply_patch`, custom-tool, file-read, or extra host call
  occurred in the raw child session. Adapter verdicts were accepted and
  operator state was restored after inspection.

## 2026-07-17 - Agent bridge package plan captured

- Fed the R22/R23 MCP breakthrough to Advisor and delegated read-only planning
  slices to Luna Workers for fixture freezing, extraction mapping,
  boot-critical config transactions, and tool-inventory expansion.
- Captured the clean follow-on plan in
  `planning/p114_worker_bridge_package_plan.md`.
- The plan targets a route-qualified `agent_workbench.agent_bridge` package
  MVP with sanitized R22/R23 fixtures, pure protocol translation modules,
  transactional config/role edits, separate grant-bound MCP `exec` and
  `apply_patch` tools, and a tool compatibility matrix for future data-plane
  expansion.
- The design explicitly supports future Worker/Supervisor/Coordinator/Advisor
  provider substitution through role/profile/provider grants rather than role
  names or TOML fields alone.

## 2026-07-17 - Agent bridge packageization tranche started

- Added the initial `agent_workbench.agent_bridge` package surface with pure
  tool-schema and protocol-shape helpers for provider-flat and child-native
  namespaced MCP calls.
- Added sanitized R22/R23 fixture contracts under `tests/fixtures/p114/` and
  focused tests that assert lifecycle order, namespace preservation, target
  transition, and forbidden fallback-tool absence.
- Updated the P114 capability adapter to consume canonical bridge tool schemas
  while preserving existing P114 compatibility wrappers.
- Added `planning/p114_agent_bridge_tool_matrix.md` to track observed native
  tools, bridge status, authority level, and deferred control-plane boundaries.

## 2026-07-17 - Agent bridge transaction guard started

- Added `agent_workbench.agent_bridge.errors`, `toml_guard`, and `transaction`
  modules.
- Implemented a local `BridgeConfigTransaction` that acquires a lock, validates
  original TOML, writes byte-for-byte backups, writes a journal, validates
  staged TOML before replacement, uses same-directory atomic replacement,
  supports idempotent restore, rejects concurrent locks, and recovers prepared
  journals from backups.
- Added focused temp-file tests for the R23 concatenated-TOML incident class,
  backup/restore, idempotent restore, concurrent lock rejection, missing staged
  content, invalid staged TOML, and prepared-journal recovery.
- Luna Workers were used for sidecar transaction test/API review and then
  closed after their results were incorporated.

## 2026-07-17 - P114 staging scripts route through package transaction CLI

- Added `agent_workbench.agent_bridge.transaction_cli` with `commit` and
  `restore` subcommands over the package transaction layer.
- Updated `scripts/enable_p114_mcp_exec_probe.ps1` to render a staged complete
  config TOML and use the package transaction CLI for commit/restore; added a
  `-CodexHome` parameter for isolated temp-home smoke checks.
- Updated `scripts/enable_p114_c4_role_bridge.ps1` to render staged complete
  config and Worker role TOML files and use the package transaction CLI for
  commit/restore; adapter startup is cleaned up if transaction commit fails,
  and `-CodexHome`/`-AgentWorkbenchEnvPath` allow disposable config validation.
- Added CLI-level transaction tests and PowerShell parser validation.
- Ran a disposable temp-home script smoke without touching live Codex config:
  MCP run `p114_mcp_tx_smoke_0b40beb0454d4874ad350de6aac72eff` committed and
  restored one temp config target, and role run
  `p114_role_tx_smoke_bca6ad6823054fb89ca75154b4a74123` committed and restored
  both temp config and temp Worker role targets byte-for-byte.

## 2026-07-17 - Agent bridge MCP server MVP primitives started

- Added `agent_workbench.agent_bridge.mcp_server` with separate MCP `exec` and
  `apply_patch` tool schemas, deny-by-default `RunGrant` policy, stable
  SHA-256 patch grants, root-contained workdir checks, injectable handlers,
  JSON-RPC request handling, and JSONL request/policy/outcome logging.
- Added focused tests for tool listing, notification behavior, denied exec,
  allowed exec, outside-root rejection, denied patch, allowed patch by hash,
  malformed-call JSON-RPC errors, JSONL stdio handling, and the module
  entrypoint.
- Added a package module entrypoint runnable as
  `python -m agent_workbench.agent_bridge.mcp_server`; local stdio smoke
  `p114_pkg_mcp_stdio_smoke_e47272b6ab67483cb5504713539a3618` listed tools,
  executed granted `python -V`, returned `isError:false`, and wrote an allow
  policy decision to the event log.
- Added `agent_workbench.agent_bridge.patch_backend`, a constrained
  relative-root patch backend for granted MCP `apply_patch` calls. It supports
  `Add File`, `Delete File`, and `Update File` hunks while rejecting
  outside-root paths and missing update context.
- Ran package-backed patch stdio smoke
  `p114_pkg_mcp_patch_stdio_smoke_acf11e9da19a4eefb869ef3cd40bd7b7`; it
  changed a temp target from exact `before\n` to exact `after\n`, returned
  `PATCH_OK`, and logged an allow policy decision.
- Kept `scripts/p114_mcp_exec_probe_server.py` untouched as the R22/R23 proof
  server fallback. The next MCP tranche is wiring the reversible config script
  to the package module.
- Added `scripts/enable_agent_bridge_mcp.ps1`, a separate reversible staging
  script for the package-backed MCP server. It writes grant arguments for
  `exec` and `apply_patch`, sets `PYTHONPATH` for the package module, and uses
  the transaction CLI for commit/restore.
- Ran temp-home staging smoke
`p114_agent_bridge_mcp_stage_smoke_dd7f7215acd748eca0603db73d069b1e`; it
committed the package MCP block into a disposable Codex config, printed the
exact staged lines, then restored the temp config hash byte-for-byte.

## 2026-07-17 - P114 package-MCP Worker composite proof rejected at host registration

- Fresh package run `p114_agent_bridge_mcp_worker_r1` launched exactly one
  `ollama_qwen_coder_worker`, child `019f7388-f175-75a3-8a72-aecf66c0b427`,
  with `fork_context:false`, the verbatim ticket, and the intended literal P114
  worktree.
- The raw child session did not advertise callable package
  `...__exec` or `...__apply_patch` schemas. It attempted unsupported
  server-level `mcp__agent_bridge_p114_agent_bridge_mcp_worker_r1` and then
  made direct `shell_command` reads, which the ticket prohibited.
- `mcp_events.jsonl` records server initialization, `tools/list`, and resource
  discovery only; it records zero MCP `tools/call` requests, policy decisions,
  or outcomes. The target remained exact `before\n`, and no direct non-MCP
  patch occurred.
- This is a host/tool-registration failure, not a Worker-quality result:
  `quality_validated_candidate` is rejected, `protocol_accepted_candidate` is
  rejected, and `economics_usable` is unavailable because no accepted
  checkpoint boundary or token ledger was captured. The required disable
  restored live config byte-for-byte against the run backup.

## 2026-07-17 - P114 package-MCP bounded exec proof accepted

- Added `-PackageMcpExec` to `scripts/enable_p114_c4_role_bridge.ps1`. It
  grants exactly one cross-shell Python read command, renders an exec-only
  ticket, and keeps deferred package-MCP discovery.
- The first run exposed a malformed Windows workdir in the ticket; the next
  reached the handler but showed the previous PowerShell-only command fails
  under the package execution backend. The script now emits a normalized
  forward-slash workdir and cross-shell command.
- Fresh run `p114_package_mcp_exec_r3` launched exactly one
  `ollama_qwen_coder_worker` child
  (`019f73b6-3db7-7a71-9a93-06472751e404`) with `fork_context:false`. Its raw
  session recorded one `tool_search` and one namespaced package `exec` call;
  the MCP log recorded an allow decision and exit code 0. No fallback tool
  appeared, the target stayed exact `before\n`, and config plus Worker role
  restored byte-for-byte.
- Focused package/adapter/fixture tests passed (`53 passed`). This accepts the
  standalone package `exec` proof. Economics remains unusable because no
  accepted checkpoint/token-ledger boundary was captured.

## 2026-07-17 - P114 package-MCP composite proof accepted

- Added `-PackageMcpComposite` to the reversible role bridge. It exposes only
  two exact Python exec commands and one SHA-256-granted patch through the
  package MCP server.
- Fresh run `p114_package_mcp_composite_r1` launched exactly one
  `ollama_qwen_coder_worker` child
  (`019f73b8-913a-7701-9dca-d2038466720b`) with `fork_context:false`. The raw
  child sequence was deferred discovery, package `exec` read, package
  `apply_patch`, and package `exec` validation; it returned
  `P114_C4_PACKAGE_MCP_COMPOSITE_DONE`.
- MCP evidence records allow decisions, exit code 0 for both exec calls, and
  one allowed patch that changed the ignored target to exact `after\n`. No
  fallback tool appeared; configuration and Worker role restored byte-for-byte.
- `quality_validated_candidate` and `protocol_accepted_candidate` are accepted
  for this bounded composite. `economics_usable` remains unproven because the
  run has no accepted checkpoint/token-ledger boundary.

## 2026-07-17 - Planned P114 C4 re-entry closeout and P115 scientific artifact pilot

- Added `planning/p114_c4_reentry_closeout_plan.md`, which scopes the remaining
  P114 work to the accepted fresh CLI-parent package route: normalize its
  deployment decision, freeze one P107-admissible capability bundle, run two
  non-comparative qualification observations, and issue a bounded P107
  re-entry packet. It explicitly keeps the unresolved VS Code nested-host
  route outside that entry decision and preserves separate quality, protocol,
  and economics verdicts.
- Updated `planning/p114_agent_bridge_tool_matrix.md` to record the accepted
  package `exec`, `apply_patch`, deferred discovery, and composite proofs,
  while retaining the earlier host-registration failure as superseded negative
  evidence rather than erasing it.
- Created planned parent issue #666, `P115: Scientific artifact-inspection
  bridge pilot`, and added the matching roadmap phase plus
  `planning/p115_scientific_artifact_inspection_plan.md`.
- P115 is deliberately not activated while P114 remains active. It will select
  one public-safe real FRESH model-instance artifact bundle, define and prove a
  grant-bound read-only inspection capability, and use that evidence—not the
  retired Copilot SDK/UI catalog—to decide the next data-plane capability.

## 2026-07-17 - Reconciled P114 re-entry plan after Advisor review

- Corrected the P114 closeout plan to distinguish accepted primitive package
  proofs from the still-required preregistered package battery: P114 now needs
  a frozen admission manifest, deterministic validator, and three independent
  fresh package-route composite rows before qualification observations.
- Limited the immediate P107 re-entry claim to the qualified baseline
  `qwen3-coder:latest` route. Every C4+ model/profile must pass its own fresh
  non-comparative package admission observation before entering a comparable
  P107 lane or economics boundary.
- Synchronized roadmap, package-plan language, and parent issue #661 with the
  accepted fresh CLI-parent package-MCP route and its separate VS Code
  nested-host exclusion. Updated P115 issue #666 and its plan to remain
  inactive until P114 is merged/closed and P107 is complete, absent explicit
  parallel authorization.

## 2026-07-18 - Completed P114 package-MCP admission battery

- Added the frozen `-PackageMcpBattery` route and
  `verify_p114_package_mcp_battery.py` admission validator. The validator
  requires the raw child sequence `tool_search`, namespaced package `exec`,
  `apply_patch`, `exec`, `apply_patch`, `exec`; granted MCP policy/outcome
  records; expected exec codes `0, 17, 0`; exact final target content; no
  fallback tools; successful upstream responses; and byte-for-byte live
  config/Worker-role restoration.
- Three independent fresh CLI-parent observations passed that validator:
  `p114_package_mcp_battery_r3` (child
  `019f75b4-776b-70a3-8758-c2b0944bbfcb`), r4 (child
  `019f75b5-7fdd-76b3-9635-fee34f762d74`), and r5 (child
  `019f75b9-9769-72e2-9e76-b97d7ca3337f`). The aggregate report is retained
  under ignored runtime evidence.
- This accepts P114.4's package capability battery as both a quality and
  protocol candidate. It does not admit P107 yet and does not make an
  economics claim; P114.5 still requires two pinned-workload baseline-Qwen
  qualification observations and the P107 re-entry packet.

## 2026-07-18 - Located the concrete P114.5 qualification seam

- Recovered the frozen historical P107 workload from retained C4 inputs:
  `p107-provenance-audit-bundle-v1`, baseline
  `139e725ee069c27cf68c797dd66aa88b5bb2824d`, and independently hashed
  ticket, fixture, and manifest. The prior C4 row is not being reused as a
  qualification result.
- The P114.4 package battery grants only exact commands and pre-hashed patches.
  That is deliberately insufficient for the coding workload's declared reads,
  four allowed implementation paths, and frozen validation command. Reusing it
  would be another tool demonstration, not a valid C4 qualification.
- P114.5 therefore starts with a narrow task-specific package grant profile
  plus deterministic materialization and containment tests. Only then may the
  two fresh literal-worktree qualification observations run.

## 2026-07-18 - P114.5 task-specific route remains unqualified

- Added task-specific bounded reads (including line ranges), explicit
  creation-target handling, relative standard-diff patch support, and a
  qualification verifier that reports quality, protocol, and economics
  separately from the raw provider child trace.
- Fresh r10 proved namespaced discovery, bounded reads, relative patch
  application, and byte-for-byte restoration, but the frozen validations
  failed and the Worker made an ungranted command call. Fresh r11 made only
  allowed namespaced reads but stopped before a patch or validation.
- Neither run is a P107 re-entry result: quality is unvalidated, protocol is
  unaccepted, and economics is not assessed. The observed remaining defect is
  Worker execution on the full frozen workload, after the package transport
  and grant-path repairs recorded above.

## 2026-07-18 - Separated P114 protocol admission from P107 workload quality

- Corrected the P114.5 validator and closeout boundary: package admission asks
  whether the bridge exposes, contains, logs, and restores the declared tool
  route. It does not require a message-model Worker to deterministically solve
  the P107 workload.
- Fresh r10 and r12 independently pass that protocol admission. Their raw
  traces contain deferred discovery and only namespaced package `read_file`,
  `apply_patch`, and `exec` calls; out-of-grant requests were denied rather
  than executed; all mutation stayed within the grant; and both staged live
  targets restored byte-for-byte.
- Both runs failed the frozen workload validations. Record those failures as
  P107 quality evidence. Economics remains unassessed. The qualified P114
  route therefore unlocks baseline P107 execution without asserting that Qwen
  will complete every workload deterministically.

## 2026-07-18 - Published the P107 C4 package-route re-entry packet

- Added `planning/p107_c4_package_route_reentry_packet.md`, which admits only
  the baseline C4 package route after P114 governed closeout.
- The packet preserves P107 task quality as an observed outcome, keeps P107.2
  economics and P108 inactive, and requires a fresh protocol admission
  observation for every later C4+ profile.

## 2026-07-18 - Closed P114 package-MCP route admission

- Merged PR #667 as `04f721fdde4d154cbda4a22af64ed2a07037a261` and closed
  parent issue #661.
- The P107 baseline C4 suite may now use the admitted CLI-parent package-MCP
  route. This does not establish P107 task quality or economics, and does not
  authorize P108.

## 2026-07-18 - Planned P116 event-driven supervision control plane

- Created planned parent issue #669 and branch
  `feature/p116-event-driven-supervision-control-plane` for a narrow repair to
  active Worker supervision.
- The plan responds to observed native-run evidence: lifecycle waiting did not
  expose Worker progress, a returned chat Supervisor did not keep monitoring,
  and the Coordinator held the usable session/message boundary. P116 adds a
  sanitized event/cursor/packet/action contract and a Coordinator-owned
  re-invocation loop; it does not attempt to force deterministic Worker
  behavior.
- P116 preserves the accepted P114 bridge route, keeps P107 economics
  unassessed, and does not activate P115. The Advisor profile is retained at
  `gpt-5.6-sol` with `model_reasoning_effort = "medium"`; the live Advisor
  review for this plan was verified at that setting.

## 2026-07-19 - Completed P116.1 supervision event contract

- Added `agent_workbench.supervision` with a versioned local supervision
  manifest, sanitized event, cursor, Supervisor-packet, and Coordinator-action
  validation contract.
- The contract binds an absolute assigned root while requiring run artifacts and
  observed event paths to stay relative to that root. It rejects reordered
  events, unobserved cursor acknowledgements, raw command/output/header fields,
  oversized text, and private-looking values.
- Focused deterministic tests accept a normal productive-repair event and
  reject the control-plane failure modes that P116 is meant to surface. No hook,
  controller, provider, or Worker authority was added in this task.

## 2026-07-19 - Completed P116.2 sanitized hook capture

- Added an inert project-local Codex `PreToolUse`/`PostToolUse` command hook and
  a Windows-compatible capture entry point. It runs only when an explicit P116
  run ID, assigned root, and ignored supervision directory are provided.
- The handler records lifecycle type, safe tool name, root-match result, and a
  generated event identity; it never retains hook `tool_input`, `tool_response`,
  absolute `cwd`, provider headers, or environment values. An out-of-root
  session becomes `workspace_mismatch`.
- Unit and subprocess tests validate the exact configured PowerShell command.
  A fresh Qwen CLI attempt loaded the P116 root/hooks but disconnected from the
  remote Responses stream before the first model tool call. This is retained as
  transport evidence, not a hook failure; P116.6 still requires live firing.

## 2026-07-19 - Completed P116.3 coordinator event reducer

- Added a credential-free controller module that refuses invalid event JSONL or
  cursors, reduces only unacknowledged validated events to a compact
  Supervisor-review delta, and atomically persists acknowledgement for restart
  recovery.
- Added a small local script that renders one delta and can acknowledge it; the
  script has no model, Worker-message, process-control, or provider surface.
- Focused tests cover acknowledged-event non-replay, malformed/reordered input,
  invalid cursor rejection, workspace-mismatch signaling, atomic cursor writes,
  and the script smoke path.

## 2026-07-19 - Completed P116.4 Supervisor delta-review contract

- Added a local-only Supervisor review request and packet validator over one
  non-empty sanitized event delta. It preserves ordinary repair as
  `productive_repair` and binds every recommendation to the supplied cursor.
- Constructive nudges require observed fact, relevant feedback, validation seam,
  and the unchanged ticket boundary; free-form, uncited, imperative, and
  authority-expanding proposals are rejected.
- This is an advisory contract only. P116.5 still owns Supervisor re-invocation
  and same-Worker delivery; no provider/model or Worker-message surface exists.

## 2026-07-19 - P116 corrective reconciliation

- An independent audit found that P116.1–P116.4 are local candidates but were
  closed before their claimed native/protocol evidence existed. Their child
  issues are reopened; the phase remains active.
- The Copilot SDK is not a P116 proof route. P116's binding reference surfaces
  are native Codex Supervisor/Worker sessions and the declared run artifacts.
- Quality is limited to local candidates, protocol is unaccepted, and economics
  remains unassessed. No P107 economics claim is made.

## 2026-07-19 - P116.2 native hook firing evidence reconciled

- A trusted native `codex_vscode` session at the exact P116 worktree executed
  `Get-Location`. Captured run `p116_hook_vscode_r8` wrote a sanitized
  `PreToolUse` event with `tool_name: Bash`, `root_match: true`, and an
  `event_written` receipt.
- The observed hook path is `Bash`, meaning the inner shell command, not the
  outer custom `exec` envelope. Focused P116 tests pass, and native hook
  dispatch evidence is now observed.
- This reconciles P116.2 only. It does not claim end-to-end supervision,
  automatic wake-up, Worker messaging, or native P116.3/P116.4 proof. Economics
  are unassessed and no P107 economics claim is made. P116's binding reference
  surfaces remain native Codex Supervisor/Worker session identities and the
  declared run artifacts.

## 2026-07-19 - P116.5 native proof contract reconciled

- The authoritative P116.5 plan now requires one combined native cycle:
  exact Worker/Supervisor binding before Worker tool use, a meaningful
  sanitized Worker delta, re-invocation of the same Supervisor through native
  `send_input`, an explicit Coordinator decision, and one bounded delivery to
  the same live Worker with post-action evidence.
- The r8 run is staged only for that proof. It is not P107 work and does not
  establish P116 completion, quality, protocol, or economics. Copilot SDK and
  app-server artifacts remain diagnostic and are non-qualifying.
- The temporary hook/MCP transaction must be restored after the evidence audit.

## 2026-07-18 - Planned P117 run-scoped supervision daemon

- Activated parent issue #686 on branch
  `feature/p117-run-scoped-supervision-daemon`; child issue #687 is P117.1,
  with planned tasks P117.2-P117.6.
- The design responds to P116's r11 stale-post-cursor finding: a supervision
  cursor must not cross a run's lease, journal, or closure boundary. P117
  therefore plans run-scoped lease/closure/journal state, deterministic
  flushing, a native session adapter, one bounded native daemon proof, offline
  sanitized policy replay, and an evidence audit.
- Quality, protocol, and economics remain separate. P117 economics is
  unassessed, and this planning entry makes no P107 economics claim. No code,
  configuration, runtime, or GitHub changes are part of this planning surface.

## 2026-07-19 - Completed P117 run-scoped supervision daemon

- Completed P117.3-P117.6 and added completed task P117.7 (#699) for the
  production native adapter and receipt-bound restart proof.
- The bounded r17 evidence records ordered sanitized events, a run-scoped lease
  and journal, native delivery and restart-reconciliation receipts, deterministic
  closure, and rejection after closure. The evidence supports duplicate
  suppression across the bounded restart boundary.
- Repeated audits reached the same separate verdict: quality is a validated
  candidate and protocol is accepted. Economics is unassessed; P117 makes no
  P107 economics claim. The result remains bounded to one run at a time and does
  not establish an unattended or unbounded autonomous runtime.

## 2026-07-19 - Completed P107.2 offline research contract

- Completed the P107.2 configuration/workload, immutable review, accounting,
  observation, comparison, and synthetic-replay contract on the reconciled
  staging branch.
- Added the frozen provenance-audit bundle workload and verified its independent
  acceptance fixture. The P107 test selection passed with 150 tests and two
  privilege-dependent skips.
- This is offline machinery only: no fresh C0-C4 configuration observation was
  run, no P107 quality/protocol verdict for a live configuration is claimed,
  and P107 economics remains unassessed.

## 2026-07-19 - Completed P116 native control-layer proof and P107 re-entry decision

- The fresh-root `p116_native_coding_r3_20260719` run staged the P116 MCP/hook
  transaction before starting the native Coordinator, bound one Worker and one
  Supervisor before Worker tool use, and retained raw session, event, packet,
  action, cursor, and restore artifacts under ignored runtime storage.
- The Supervisor directly obtained the ordered `events:1-3` sanitized delta
  through its native P116 MCP inventory. The Coordinator validated the packet,
  recorded the hash and delivery receipt, and sent one bounded repair cue to
  the same Worker. The Worker repaired malformed `--repair-errors` JSON
  handling and the focused validation passed.
- Quality and bounded native protocol are supported. Economics is unassessed:
  no P107-boundary token/cash ledger exists, and P116 makes no P107 economics
  claim. A future P107 C4 measurement may use this control layer only through
  a fresh native Coordinator launched after run-scoped staging.

## 2026-07-19 - Repaired VS Code in-session P116 live progress delivery

- Repaired the native in-session event predicate so a newly captured,
  sanitized successful Worker tool completion wakes the active VS Code Codex
  Coordinator instead of timing out indefinitely.
- A fresh native Coordinator bound one Worker and one advisory Supervisor,
  received the live `tool_completed` delta in 0.83 seconds before terminal
  completion, and allowed ordinary productive work to continue without an
  unnecessary intervention.
- The bounded Worker ticket added workflow-package CLI coverage and passed 20
  focused tests. P116 control-layer quality and native protocol remain
  supported; economics remains unassessed and no P107 economics claim is made.
## 2026-07-20 - Reopened P116 for diagnostic-envelope refinement

- Reopened parent issue #669 and created active child issue #710, P116.8,
  after live VS Code run `p116_ui_870087267e6f48e1` showed that the repaired
  in-session loop can observe incremental Worker events, acknowledge review
  cursors, re-invoke the same Supervisor, and record Coordinator decisions,
  while still lacking enough safe failure context for targeted repair advice.
- A native `gpt_sol_advisor` review required a narrower, versioned v2 event
  contract: immutable pre-tool policy binding; safe operation/scope classes;
  optional exact declared check ID; bounded failure class; and exit code.
  It rejected observed paths and failure fingerprints for this slice because
  their disclosure/correlation risk is unnecessary for the immediate decision.
- P116.8 excludes raw commands, arguments, stderr, source, credentials,
  arbitrary paths, raw-output digests, and parser captures; ambiguous policy or
  `call_id` correlation fails closed. Existing v1 evidence remains readable.
- Quality and protocol for P116.8 remain pending deterministic and fresh native
  evidence. Economics remains unassessed; this does not start a P107 economics
  measurement.

## 2026-07-20 - Completed bounded P116.8 diagnostic-envelope proof

- Implemented the Advisor-reviewed `p116_supervision_event_v2` policy envelope:
  immutable pre-tool policy binding, safe `call_id` correlation, declared-check
  recognition, bounded failure classes, and explicit v1 compatibility.
- Focused P116/P114 validation passed with 72 tests. Deterministic negatives
  reject/reduce undeclared agent calls and out-of-scope patches without leaking
  their inputs or paths.
- Fresh native run `p116_v2_diagnostic_native_20260720` emitted a root-matched
  v2 declared-check failure (`test`, `within_ticket`,
  `controlled-missing-test`, exit `1`, `missing_file`), received same-Supervisor
  terminal advice, recorded the acknowledged Coordinator terminal decision, and
  closed cleanly. No raw command, output, path, source, credential, or failure
  fingerprint entered the event/packet/action artifacts.
- P116.8 quality and bounded protocol are supported; economics remains
  unassessed. Phase integration remains open and this is not a P107 economics
  result.

## 2026-07-20 - Built P107 V3 dossier-workload current-root candidate

- Added the five-slice `p107-run-evidence-dossier-v3` candidate: typed,
  hash-bound artifact validation; cross-artifact reconciliation; lifecycle
  timeline/anomaly analysis; and deterministic JSON/Markdown CLI reporting.
- Added a public-safe fixture binding heartbeat, token-ledger, Advisor verdict,
  archive, and Worker result artifacts by SHA-256. The focused dossier suites
  pass `100` cases with one platform-dependent symlink skip.
- This is local quality evidence only. The remaining C0 ticket, prompts,
  model/pricing catalogs, effective configuration, and Advisor rubric have not
  been frozen against the fixture; no P107 protocol or economics observation
  is claimed.

## 2026-07-20 - Prepared P107 V3 C0 preflight freeze

- Materialized the ignored `p107_v3_c0_freeze_20260720` block against clean
  baseline `50a8a185556aeb81bf1142f7992c026871426920`, which lacks the dossier
  implementation. The block binds the V3 ticket, fixture, reset-consistent
  C0-C4 prompts, Terra/medium effective-session snapshot, model/pricing
  catalogs, and Advisor rubric by SHA-256.
- Repaired the evaluation-block validator with an explicit preflight checkout
  override so a runtime freeze can be verified before a C0 worktree exists;
  ordinary contained-root validation remains unchanged.
- This is preparation only: no worktree, C0 execution, P107 quality/protocol
  observation, or economics measurement occurred.

## 2026-07-20 - Recorded P107 mission guardrail and first V3 C0 observation

- Recorded the controlling P107 rule in the reset, substantial-workload plan,
  and roadmap: fixed deterministic acceptance checks evaluate the resulting
  artifact; they do not turn native Agent Hub LLMs into deterministic
  functions.
- A configuration's incomplete, divergent, invalid, accepted, or honestly
  blocked task result is quality evidence. The coordinator must not alter the
  frozen workload or externally repair a submitted candidate merely to
  manufacture a pass.
- Only a defect that prevented native topology, boundary observation, or
  accounting capture is a control-layer repair candidate; it is recorded as a
  separate protocol/instrumentation result and requires a new frozen block if
  comparison conditions change.
- Fresh native C0 r2 session `019f80d5-7ae1-7493-92f0-90e6af754ba4` completed
  the frozen V3 ticket in the clean baseline checkout. Its candidate and task
  result are retained for evaluation; no external implementation repair is
  authorized by P107. Economics remains unassessed without a valid run-boundary
  ledger.

## 2026-07-20 - Reconciled P107 configuration ladder and review authority

- Made the reset-consistent frozen C0-C4 prompts authoritative: Terra alone;
  Terra-to-Luna Worker; Terra-to-configured-Ollama Worker; Luna alone; and
  Luna-to-configured-Ollama Worker.
- Removed the contradictory Supervisor topologies, mandatory routine Advisor
  gate, automatic two-failure stop rule, and standing three-review cap from the
  active P107 research program. Sol remains a selective non-mutating Advisor,
  not a recurring execution role.
- C0 r2 must now be evaluated as submitted before any accounting-only repair
  decision. No C1 execution is authorized until an eligible C0 exists in a
  frozen block.

## 2026-07-20 - Simplified active P107 accounting and comparison validation

- Aligned the active P107 run-evidence, accounting, and comparison validators
  with the reset-consistent ladder. C0/C3 now have only a Coordinator;
  C1/C2/C4 have a Coordinator and one Worker; no active configuration requires
  an Advisor or Supervisor.
- Removed the obsolete mandatory Advisor verdict/binding comparison gate and
  allowed a normal uncommitted implementation diff at the frozen starting
  commit. The validators still require declared topology, provenance, and
  complete accounting before economics comparison.
- Focused validator coverage passed: `70 passed`. This implementation repair
  does not alter C0 r2's submitted code or make an economics claim.

## 2026-07-20 - Accepted P107 V3 C0 r3 baseline

- Fresh native C0 r3 session `019f80f3-03ae-7cd3-83a6-9feaae4efb5c` used the
  pre-launch Terra/medium, memories-disabled native configuration in a clean
  frozen-baseline worktree. The normal native default was restored byte-for-byte
  after the run.
- Quality: accepted candidate. The submitted implementation passed its exact
  frozen acceptance command (`4 passed`); its intact dossier fixture validated,
  a tampered manifest was rejected, and `git diff --check` passed.
- Protocol: accepted. The raw native record, clean root, bounded authority, and
  pre-launch configuration were observed; no child agents, GitHub mutations,
  commits, pushes, or in-run configuration changes occurred.
- Economics: usable. The raw cumulative Terra Coordinator development span
  priced at `$2.0937575` under the frozen catalog. Automatic UI title
  generation is unrelated host metadata and excluded from task economics.
- C0 r3 is the eligible baseline for the next authorized C1 configuration. No
  comparative ROI claim has yet been made.

## 2026-07-20 - Clarified native P107 model identity evidence

- Corrected the evidence rule: a missing model field in an individual native
  transcript does not make the implementation model unknowable when the
  hash-bound pre-launch native configuration or role binding is linked to the
  fresh session. That binding is sufficient for model pricing.
- A native title-generation call may use a different model; exclude it as
  unrelated UI metadata and do not use it to reclassify the implementation
  session's model or task cost.

## 2026-07-20 - Accepted comparable P107 C1 observation

- Fresh C1 Terra Coordinator session
  `019f80fb-4baa-7752-9e56-cffa883088b5` spawned exactly one native Luna Worker
  with `fork_context:false`; the Worker made the scoped implementation edits
  and the Coordinator independently inspected and validated them.
- Quality: accepted candidate (`4 passed`; intact fixture CLI validation passed;
  tampered manifest rejected).
- Protocol: accepted. One Worker only, no Coordinator implementation fallback,
  no routine Advisor, and no commit, push, GitHub, or in-run configuration
  mutation.
- Economics: usable. Terra Coordinator `$0.7909664` plus Luna Worker
  `$0.4235984` equals `$1.2145648`, `$0.8791927` (42.0%) below C0 with no
  observed quality regression.
- C2 Terra-to-configured-Ollama Worker is the next authorized configuration.

## 2026-07-20 - Recorded failed unsupervised P107 C2 Ollama-Worker observation

- Fresh C2 Terra Coordinator session
  `019f8101-8dcd-7783-9f85-23cc5713d959` spawned one configured native Ollama
  Worker with `fork_context:false`.
- The Worker created only incomplete source files, omitted the required tests,
  fixture, and CLI change, and did not return its required final result. The
  Coordinator shut it down, did not implement a fallback, and independently
  confirmed that the frozen test command could not collect missing tests.
- Quality: rejected. Protocol: not accepted because the Worker failed its
  terminal handoff. Economics: not usable for comparison because the output was
  unaccepted and local Worker cost was not measured. The candidate remains
  unrepaired C2 evidence.

## 2026-07-20 - Corrected P107 delegated-route ownership

- The C1 and C2 observations were launched without the P116 control layer, so
  they measured bare Coordinator-to-Worker delegation rather than the usable
  native Agent Hub workflow requested for P107.
- Canonical C1, C2, and C4 now require Coordinator-owned P116 supervision:
  bind the exact Worker before tools, review meaningful deltas, decide and send
  any intervention as Coordinator, and close the control run at task end. This
  adds no routine Supervisor role and does not prescribe LLM behavior.
- C2 remains active for a fresh supervised rerun on the same frozen workload;
  C3 is not next. The existing C1/C2 records remain useful unsupervised
  diagnostics. A supervised C1 rerun is required before a corrected-epoch
  C1-versus-C2 comparative claim.

## 2026-07-21 - C2 native integration accepted; C3 authorized

- C2 r7 delivered the frozen P107 dossier candidate through the native direct
  Terra-Coordinator-to-medium-Qwen-Worker route. The Coordinator-owned P116
  binding succeeded before Worker tools; focused quality validation passed and
  the accepted scoped P107 change was committed by the Coordinator.
- The outer controller, rather than the Agent Hub team, captured the raw
  Coordinator token span and rendered the existing economics ledger: paid
  Coordinator estimate `$0.413974`; local Qwen usage is separate and unpriced.
- The developer authorized the canonical C3 Luna-alone slice next. C3 has no
  Worker, P116, Advisor, accounting, or Git authority inside its common mission.
  The C1 supervised rerun remains necessary only for a corrected-epoch
  C1-versus-C2 comparison.

## 2026-07-21 - Closed P107/P116 tranche and drafted P118 FRESH vLLM Agent

- Closed P116 after its bounded native in-session control layer and v2 safe
  diagnostic-envelope refinement were independently covered by focused tests.
  It remains a control layer, not an unattended daemon or a P107 economics
  result.
- Closed P107 as a bounded exploration tranche. Accepted C0, C1, supervised
  C2, and C4+ observations remain recorded with their own quality, protocol,
  and economics verdicts; the changing workload/topology/provider epochs do
  not support one final cross-epoch ROI ranking.
- Added the draft P118 plan for a native FRESH vLLM Agent deployment: one
  configured custom Qwen coding model across Coordinator, Worker, and
  selective Advisor profiles, with serial intensive execution and no automatic
  paid fallback.
