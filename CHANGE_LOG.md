# Change Log

<!-- Migration: 2026-07-23. Older entries are in
     planning/archives/changelog_archive.md. -->

Newest entries are last. Keep this file synchronized with `ROADMAP.md`, GitHub
issues, pull requests, and closeout comments.

## 2026-07-23 - P120.5 Roadmap/changelog architecture repair

- Architecture proposal written: thin local index plus GitHub canonical
  hierarchy with generated projections.
- See `runtime/agent_jobs/p120_5_roadmap_changelog_rearchitecture_proposal.md`.
- Migration executed: ROADMAP.md reduced from ~6,400 lines to ~60 lines.
  CHANGE_LOG.md reduced from ~4,900 lines to ~30 lines. Older entries
  moved to `planning/archives/changelog_archive.md`.

## 2026-07-23 - P120.4 SDK architecture repair

- SDK session authority confirmed: SDK-owned sessions are the automation
  authority. Keklick Copilot UI is for manual smoke tests only.
- SDK manifests accept generic OpenAI-compatible base URL and model alias.
- Profile catalog includes Coordinator and Advisor profiles.

## 2026-07-22 - P119.5 Blackwell/vLLM phase closeout

- P119.5 completed. Parent issue #749 closed.
- Branch `feature/p119-blackwell-vllm` merged to main.

## 2026-07-22 - P119.4 Concurrency stress testing

- P119.4 completed concurrency stress testing. Parent issue #743 closed.

## 2026-07-22 - P115 Validation fixtures

- P115 validation fixtures completed. Parent issue #731 closed.

## 2026-07-22 - P109.3-4: Yield gate and promotion complete

- P109.3 ran `scripts/p109_3_yield_gate.py` — content-bearing yield only. 242/242
  content-bearing records accepted (100% yield).
- P109.4: gate passed, promotion proceeds. Issues #745, #746 closed.

## 2026-07-22 - P109.2: Audit and promote accepted records (250 accepted)

- P109.2 ran `scripts/p109_2_batch_audit.py` against 250 candidates from P109.1.
- 250 records accepted. Issue #744 closed.

## 2026-07-22 - P109.1: 2012 Cycle Extraction Complete

- P109.1 ran `scripts/p109_1_batch_extract.py` — 250 candidate records across 3
  documents. Issue #742 closed.

## 2026-07-22 - P109 Workflow Compliance

- Brought P109 into UBC-FRESH dev workflow compliance.
- Parent issue #741 created with child issues #742-#746.

## 2026-07-29 - P119 follow-up service-hardening closeout

- Added sanitized crash-forensics guidance, service/watchdog templates, and
  runtime hardening helpers for the completed P119 vLLM phase.
- Added a public-safe secrets-path resolver and the remote-access safety
  contract; neither change performs a live service, connector, DNS, or
  credential operation.
- Quality: focused shell/Python checks and secret-resolution tests pass.
- Protocol: this closes the documentation/template follow-up only; it does not
  claim the underlying GPU-kernel root cause is solved.
- Economics: not measured.

## 2026-07-31 - P125 Popup provider framework: schema and preflight

- Created `playbooks/popup_provider/` — portable framework for popup LLM
  providers on shared HPC clusters.
- Target descriptor schema (`targets/_schema.yaml`) and Sockeye example
  (`targets/sockeye.example.yaml`).
- Launch profile schema (`profiles/_schema.yaml`) with two example profiles:
  Qwen2.5 Coder 7B (GGUF) and Qwen3.6 27B NVFP4 (ModelOpt).
- VRAM catalog (`preflight/catalog.json`) with measured/estimated values for
  five models across GGUF and ModelOpt runtimes.
- Fit preflight checker (`preflight/check.py`) — refuses or downsizes requests
  that cannot fit the target's VRAM, with alternative suggestions.
- Unattended bring-up script (`bringup/autostart.sh`) — submit → wait → stage
  → serve → bridge → verify, reusing P119 launch-profile and readiness-probe
  assets.
- Loopback bridge (`bringup/bridge.py`) — auto-discovers job ID, captures
  srun stderr, refuses when no allocation exists, auto-reconnects on failure.
- Bounded verification script (`bringup/verify.sh`) — /v1/models + single
  chat completion, writes JSON evidence.
- Quality: preflight passes for both example profiles on the Sockeye target.
- Protocol: all new files are public-safe; no credentials, endpoints, or
  private paths are committed.
- Economics: not measured.

- Added a public-safe extraction contract, CPU and optional GPU-fallback
  profiles, resumable JSONL coordinator, controlled endpoint tests, and a
  decision-packet template for issue #758 / child #759.
- Quality: controlled OpenAI-compatible endpoint tests pass; no corpus run,
  benchmark, or production-readiness claim is made.
- Protocol: raw document text, endpoint URLs, credentials, and host paths stay
  local; live endpoint benchmarking is deferred to a later registered phase.
- Economics: not measured.

## 2026-07-29 - P122 HPC GPU capacity and provider workflow

- Added a dry-run-first multi-cluster Slurm GPU capacity coordinator and
  public-safe configuration template.
- Added client-owned SSH forwarding guidance and an optional existing-tunnel
  DNS helper that refuses connector creation or replacement.
- Quality: focused unit tests cover capacity reconciliation and provider
  safety guards; no live scheduler or Cloudflare mutation is claimed.
- Protocol: real targets, credentials, job records, and raw cluster material
  remain local.
- Economics: not measured.

## Older entries

See `planning/archives/changelog_archive.md` for entries older than the
last 10 entries.
