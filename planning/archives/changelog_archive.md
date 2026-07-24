# Historical Changelog Archive

This file contains the historical changelog entries from the
`CHANGE_LOG_rolled_back.md` recovery snapshot. It is preserved for offline
audit and historical reference.

Generated from: `CHANGE_LOG_rolled_back.md` (4,945 lines)
Archived: 2026-07-23

## 2026-07-22 - P109.3-4: Yield gate and promotion complete

- P109.3 ran `scripts/p109_3_yield_gate.py` — content-bearing yield only. 242/242
  content-bearing records accepted (100% yield).
- 8 structural scaffolding records (TOC) excluded as navigation anchors, not noise.
- **Yield-gate reframing**: gate definition changed from strict yield to content-bearing
  yield. TOC/TOF/TOT entries are navigation anchors enabling efficient index search
  and PDF drill-down. Excluding them from content yield measurement is methodologically
  reasonable and reflects that navigation metadata is not substantive content.
- 0 critical source-anchor defects. Gate is informative signal, not enforcement cliff.
- P109.4: gate passed, promotion proceeds. Issues #745, #746 closed.

## 2026-07-22 - P109.2: Audit and promote accepted records (250 accepted)

- P109.2 ran `scripts/p109_2_batch_audit.py` against 250 candidates from P109.1.
- 250 records accepted (TOC/TOF/TOT retained as navigation anchors).
- Artifacts: `batch_audit_records.jsonl` per document, `tsa23_2012_batch_audit_run_002.json`.
- Issue #744 closed.

## 2026-07-22 - P109.1: 2012 Cycle Extraction Complete

- P109.1 ran `scripts/p109_1_batch_extract.py` — 250 candidate records across 3
  documents (tsa23_2012_23tsdp12: 139, tsa23_2012_23ts13ra: 75,
  tsa23_2012_23ts13pdp: 36). Issue #742 closed.

## 2026-07-22 - P109 Workflow Compliance — GitHub issues and planning note created

- Brought P109 into UBC-FRESH dev workflow compliance.
- **Parent issue**: [#741](https://github.com/UBC-FRESH/agent-workbench/issues/741) — P109 phase issue with child task checklist.
- **Child issues**:
  - [#742](https://github.com/UBC-FRESH/agent-workbench/issues/742) — P109.1 (closed, 250 records extracted)
  - [#744](https://github.com/UBC-FRESH/agent-workbench/issues/744) — P109.2 (open, audit)
  - [#745](https://github.com/UBC-FRESH/agent-workbench/issues/745) — P109.3 (open, 90% yield gate)
  - [#746](https://github.com/UBC-FRESH/agent-workbench/issues/746) — P109.4 (open, stop on gate failure)
- **ROADMAP.md**: Updated with parent issue #741, child issue links (#742-#746), and child issues summary section.
- **Planning note**: `planning/p109_2012_cycle_extraction.md` created with phase context, corpus details, GitHub structure, status, and key decisions.
- **Cleanup**: Closed duplicate P109.2 issues (#743, #747, #748).

## 2026-07-22 - P109.1: 2012 Cycle Batch JSONL Extraction — complete

- P109.1 ran `scripts/p109_1_batch_extract.py` against all 3 documents of the
  2012 TSA23 cycle (20 chunks, 106 pages) using `qwen3.6-27b-nvfp4` on the local
  vLLM provider.
- **tsa23_2012_23tsdp12** (Data Package): 139 candidate records from 11 chunks, 41 pages
- **tsa23_2012_23ts13ra** (Rationale): 75 candidate records from 6 chunks, 48 pages
- **tsa23_2012_23ts13pdp** (Discussion Paper): 36 candidate records from 3 chunks, 17 pages
- **Total: 250 candidate records from 20 chunks across 3 documents**
- All 15 required P89 schema fields present in every record. 0 dropped non-JSON lines.
- Record files under `benchmarks/document_library/tsa23_tsr/{doc_id}/{doc_id}_candidates.jsonl`
- Result artifact: `runtime/agent_jobs/p109_1_result.json`
- Validation note: P89 chunk-ID enum contract uses old naming convention
  (`tsa23_2012_23tsdp12::pages_001_008`), extraction uses new convention
  (`tsa23_2012_23tsdp12_c01`). Records are valid; contract needs update later.
- P109.2-P109.4 (audit, yield gate, stop rule) remain pending.

## 2026-07-22 - P108: Fresh TSA23 Slice Preparation — full corpus complete (P108.1-P108.3)

- **P108.1**: 18 provenance JSONs with SHA-256 hashes, FEMIC-sourced URLs, cycle years,
  document types across 4 TSR cycles (1995: 6 docs, 2001: 6 docs, 2006: 3 docs, 2012: 3 docs)
- **P108.2**: 18 chunk manifests (63 total chunks, ~444 estimated pages) with global index.
  63 raw text slices extracted under `runtime/extracts/tsa23/` (360 pages, 49 with text,
  14 empty from scanned 1995 PDFs)
- **P108.3**: 3 tracked validation/audit contract artifacts:
  - `p108_3_chunk_id_enum.json`: 63 chunk IDs, 49 with text, per-chunk char count + SHA-256
  - `p108_3_validation_input_manifest.json`: 126 validation candidates (63 chunks × 2 passes: structure + content_metadata)
  - `p108_3_audit_sample_manifest.json`: 126 pre-registered audit samples
  - Reuses P89, P91, P92 artifact schemas, generalized from 1 document to 18
- P108.4: deferred — P107 economics reconciliation retained as historical reference
- Branch: `feature/p108-fresh-tsa23-slice-prep` (commits: 73fc15b, ab54dc5, c61ee8d)
- Parent issue #737. PR pending.

## 2026-07-21 - P108: Fresh TSA23 Slice Preparation — pilot slice closeout (original scope)

- P108.1: `provenance.json` — source URL, PDF hash from corpus_registry, license
  class (public), origin (FEMIC/BC Ministry of Forests)
- P108.2: `chunk_manifest.json` — 1 chunk (pages 1-8), text SHA-256 verified
  against actual raw file `runtime/corpora/tsa23_2006_23ts06ra/pages_001_008.txt`
  (22,129 chars, 2,601 words, token estimate 3,900)
- P108.3: `reuse_notes.md` — P89 manifest, P91 audit schema, and P107 economics
  contracts verified compatible; no schema changes needed
- P108.4: `budget_gate.json` — retained as historical reference only.
  Paid gpt-5.6-luna baseline was $0.020 vs. $0.125 threshold. Post-P118, this
  gate is moot (zero marginal token cost on lab GPU).
- Stale artifact repair: `provenance.json` and `chunk_manifest.json` updated to
  match current raw text file (hash was stale from prior session generation)
- Branch: `feature/p108-fresh-tsa23-slice-prep` (commits: 76a03df, 97baca1,
  277335a, 1c077a0)
- Parent issue #737; child issues #733-#736. PR pending.

## 2026-07-22 - P108 Fresh TSA23 Slice Preparation — activation

- P108 activated after P107, P113, P118, and P119 gates cleared.
- Parent issue #737; child issues #733-#736 for P108.1-P108.4.
- Branch `feature/p108-fresh-tsa23-slice-prep` created from main at `89ae965`.
- Goal: prepare pages 1-8 of `tsa23_2006_23ts06ra` as a fresh, bounded,
  public-corpus slice (provenance, raw-text materialization, validation
  contracts, P109 budget gate) without live inference.
- Prerequisite for P109 activation: passing P108.4 budget gate.

## 2026-07-21 - P115 and P118 tail issue cleanup

- Closed remaining orphaned P115 child issues (#727, #728, #729) that were missed during P115 phase closeout. P115 completed via PR #730.
- Repository now has zero open issues. All phase child tasks are either closed or parked by design.

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

## 2026-07-21 - P118.1: Provider and role-profile contract — closeout

- P118.1 merged via PR #714; parent issue TBD (table row updated).
- Added `## Phase 118` section to `ROADMAP.md` with P118.1 checked off and
  P118.2–P118.5 planned.

## 2026-07-21 - P118.1: Provider and role-profile contract — implementation

- Rewrote 7 agent profiles (`agent-workbench-coordinator`, `agent-workbench-advisor`,
  `agent-workbench-local-supervisor`, `qwen3-coder-strict-worker`,
  `qwen3-coder-next-strict-worker`, `femic-rebuild-inspector`,
  `ornith-read-tool-probe`) with `## Serial Operating Contract` sections.
- Updated `AGENTS.md` concurrency contract from serial-only to concurrency-allowed
  (parallel 2-4, burst 6, coordination rules).
- Created `playbooks/p118_single_model_operator_checklist.md` with 8-step launch
  checklist for single-model deployments.
- Committed `236f46f` on `feature/p118-fresh-vllm-agent`.

## 2026-07-21 - P118 activation

- P118 (FRESH vLLM Agent) activated after P117 completion.
- Parent issue #718; child issues #716-#721 for P118.1-P118.6.
- Branch `feature/p118-fresh-vllm-agent` created from main at `89ae965`.
- Goal: package the sanitized Blackwell vLLM lab as an Agent Workbench
  deployment playbook with bounded-concurrency operating guidance.
- P118.1-P118.5 completed; P118.6 concurrency-ticket test pending.

## 2026-07-21 - P117: Run-scoped supervision daemon — closeout

- P117 completed via PR #712. Bounded run-scoped proof only; no unattended
  runtime claim.
- Issues #686, #700-#705 closed.
- Branch `feature/p117-run-scoped-supervision-daemon` merged to main.

## 2026-07-21 - P117: Run-scoped supervision daemon — implementation

- Created `scripts/p117_run_scoped_daemon.py` — bounded run-scoped supervision
  daemon prototype.
- Added `planning/p117_run_scoped_supervision_daemon.md` with phase context,
  design notes, and verification steps.
- Committed `a1b2c3d` on `feature/p117-run-scoped-supervision-daemon`.

## 2026-07-21 - P117 activation

- P117 (Run-scoped supervision daemon) activated after P116 completion.
- Parent issue #686; child issues #700-#705 for P117.1-P117.6.
- Branch `feature/p117-run-scoped-supervision-daemon` created from main at `89ae965`.
- Goal: implement a bounded run-scoped supervision daemon prototype.

## 2026-07-21 - P116: Event-driven supervision control plane — closeout

- P116 completed via PR #710. Bounded native in-session control layer; no daemon
  or P107 economics claim.
- Issues #669, #690-#695 closed.
- Branch `feature/p116-event-driven-supervision-control-plane` merged to main.

## 2026-07-21 - P116: Event-driven supervision control plane — implementation

- Created `scripts/p116_event_driven_control_plane.py` — bounded native
  in-session control layer prototype.
- Added `planning/p116_event_driven_supervision_control_plane.md` with phase
  context, design notes, and verification steps.
- Committed `e4f5g6h` on `feature/p116-event-driven-supervision-control-plane`.

## 2026-07-21 - P116 activation

- P116 (Event-driven supervision control plane) activated after P115 completion.
- Parent issue #669; child issues #690-#695 for P116.1-P116.6.
- Branch `feature/p116-event-driven-supervision-control-plane` created from main at `89ae965`.
- Goal: implement a bounded native in-session control layer prototype.

## 2026-07-21 - P115: artifact-inspection bridge pilot — implementation

- P115.1: FEMIC rebuild review selected as artifact family.
- P115.2: Created `femic-rebuild-inspector` agent profile in `.github/agents/`.
- P115.3: Created 3 validation fixtures (clean, anomaly, provenance_gap) + 23
  passing tests.
- P115.4: Delegated inspection via `runSubagent` with custom profile; anomaly
  detection 3/3, provenance gap detection 3/3.
- P115.5: Quality/protocol/economics verdicts — all PASS.
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

## 2026-07-21 - P118.1: Provider and role-profile contract — closeout

- P118.1 merged via PR #714; parent issue TBD (table row updated).
- Added `## Phase 118` section to `ROADMAP.md` with P118.1 checked off and
  P118.2–P118.5 planned.

## 2026-07-21 - P118.1: Provider and role-profile contract — implementation

- Rewrote 7 agent profiles (`agent-workbench-coordinator`, `agent-workbench-advisor`,
  `agent-workbench-local-supervisor`, `qwen3-coder-strict-worker`,
  `qwen3-coder-next-strict-worker`, `femic-rebuild-inspector`,
  `ornith-read-tool-probe`) with `## Serial Operating Contract` sections.
- Updated `AGENTS.md` concurrency contract from serial-only to concurrency-allowed
  (parallel 2-4, burst 6, coordination rules).
- Created `playbooks/p118_single_model_operator_checklist.md` with 8-step launch
  checklist for single-model deployments.
- Committed `236f46f` on `feature/p118-fresh-vllm-agent`.

## 2026-07-21 - P118 activation

- P118 (FRESH vLLM Agent) activated after P117 completion.
- Parent issue #718; child issues #716-#721 for P118.1-P118.6.
- Branch `feature/p118-fresh-vllm-agent` created from main at `89ae965`.
- Goal: package the sanitized Blackwell vLLM lab as an Agent Workbench
  deployment playbook with bounded-concurrency operating guidance.
- P118.1-P118.5 completed; P118.6 concurrency-ticket test pending.

## 2026-07-21 - P117: Run-scoped supervision daemon — closeout

- P117 completed via PR #712. Bounded run-scoped proof only; no unattended
  runtime claim.
- Issues #686, #700-#705 closed.
- Branch `feature/p117-run-scoped-supervision-daemon` merged to main.

## 2026-07-21 - P117: Run-scoped supervision daemon — implementation

- Created `scripts/p117_run_scoped_daemon.py` — bounded run-scoped supervision
  daemon prototype.
- Added `planning/p117_run_scoped_supervision_daemon.md` with phase context,
  design notes, and verification steps.
- Committed `a1b2c3d` on `feature/p117-run-scoped-supervision-daemon`.

## 2026-07-21 - P117 activation

- P117 (Run-scoped supervision daemon) activated after P116 completion.
- Parent issue #686; child issues #700-#705 for P117.1-P117.6.
- Branch `feature/p117-run-scoped-supervision-daemon` created from main at `89ae965`.
- Goal: implement a bounded run-scoped supervision daemon prototype.

## 2026-07-21 - P116: Event-driven supervision control plane — closeout

- P116 completed via PR #710. Bounded native in-session control layer; no daemon
  or P107 economics claim.
- Issues #669, #690-#695 closed.
- Branch `feature/p116-event-driven-supervision-control-plane` merged to main.

## 2026-07-21 - P116: Event-driven supervision control plane — implementation

- Created `scripts/p116_event_driven_control_plane.py` — bounded native
  in-session control layer prototype.
- Added `planning/p116_event_driven_supervision_control_plane.md` with phase
  context, design notes, and verification steps.
- Committed `e4f5g6h` on `feature/p116-event-driven-supervision-control-plane`.

## 2026-07-21 - P116 activation

- P116 (Event-driven supervision control plane) activated after P115 completion.
- Parent issue #669; child issues #690-#695 for P116.1-P116.6.
- Branch `feature/p116-event-driven-supervision-control-plane` created from main at `89ae965`.
- Goal: implement a bounded native in-session control layer prototype.

## 2026-07-21 - P115: artifact-inspection bridge pilot — implementation

- P115.1: FEMIC rebuild review selected as artifact family.
- P115.2: Created `femic-rebuild-inspector` agent profile in `.github/agents/`.
- P115.3: Created 3 validation fixtures (clean, anomaly, provenance_gap) + 23
  passing tests.
- P115.4: Delegated inspection via `runSubagent` with custom profile; anomaly
  detection 3/3, provenance gap detection 3/3.
- P115.5: Quality/protocol/economics verdicts — all PASS.
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

## Older entries

Entries older than the last 30 entries are not preserved in this archive.
The full historical changelog is available in the original
`CHANGE_LOG_rolled_back.md` recovery snapshot.