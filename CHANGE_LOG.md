# Change Log

<!-- Migration: 2026-07-23. Repaired 2026-07-30: the original migration
     dropped most historical entries; the full history is restored in
     planning/archives/changelog_archive.md. -->

Newest entries are last. Keep this file synchronized with `ROADMAP.md`, GitHub
issues, pull requests, and closeout comments.

## 2026-07-22 - P119.4 Concurrency stress testing

- P119.4 completed concurrency stress testing. Parent issue #743 closed.

## 2026-07-22 - P115 Validation fixtures

- P115 validation fixtures completed. Parent issue #731 closed.

## 2026-07-22 - P109 Workflow Compliance

- Brought P109 into UBC-FRESH dev workflow compliance.
- Parent issue #741 created with child issues #742-#746.

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

## 2026-07-27 - AGENTS contract hardening for remote-access safety

- Added a non-negotiable remote-access safety policy to `AGENTS.md` after the
  Cloudflare tunnel outage. Agents must inspect the live topology, back up
  configs, verify tunnel information before and after changes, preserve the
  active ingress path, and never reuse production tunnel credentials on another
  host without explicit authorization.

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

## 2026-07-29 - P121 CPU document scraper implementation

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

## 2026-07-30 - P124 Sockeye private vLLM provider bring-up opened

- Opened P124 parent issue #766 and child task #767 on branch
  `feature/p124-sockeye-vllm-provider-bringup`.
- Parked P123 (#764/#765) pending P124 readiness; no CPU scraper benchmark
  work is performed in this phase.
- Scope is limited to a loopback-only vLLM provider in an existing approved
  Sockeye allocation and client-owned SSH forwarding.
- Preflight identified implementation prerequisites: the staged launchers bind
  publicly and the selected allocation lacks the intended vLLM environment.
  P124 remains active and will create an allocation-local, loopback-only
  wrapper plus an isolated, version-pinned runtime or reuse a validated staged
  runtime.
- Quality: no provider readiness or model-capability claim is made until local
  discovery and a bounded request succeed.
- Protocol: Cloudflare tunnels, DNS, connectors, public listeners, credentials,
  raw logs, endpoint values, and allocation changes remain out of scope.
- Economics: not measured.

## 2026-07-30 - P124 parked; P125 popup provider framework opened

- Rebuilt the Sockeye provider bring-up so it completes unattended: the model
  stages and the server launches automatically once an allocation lands, and
  the loopback bridge discovers the Slurm job id at runtime instead of pinning
  a dead one.
- Corrected PoC defects: hardcoded job id, discarded bridge errors, tensor
  parallelism of four for a model that fits one GPU, manual staging and launch,
  missing tool-call parser, and a client context window larger than the server
  served.
- Established that MFA-gated clusters cannot be authenticated by an agent.
  Forwards must be injected into the human-authenticated multiplexed master
  with `ssh -O forward`; `-o`/`-F` overrides and `ssh -N -L` force a denied
  login. Recorded in `AGENTS.md`.
- Repaired the changelog architecture. The 2026-07-23 migration preserved only
  30 of 380 entries; the full history is reconstructed in
  `planning/archives/changelog_archive.md` with no entries lost.
- Opened P125 (#769) to generalize popup remote LLM provider deployment across
  shared HPC and cloud clusters, reusing the existing capacity coordinator,
  vLLM launch profiles, readiness probe, and watchdog.
- Quality: the access path and unattended bring-up are implemented and the
  bridge degrades cleanly with no allocation; no model response has been served
  since the replacement allocation is still queued.
- Protocol: P124 is parked rather than closed because its acceptance boundary
  requires a served bounded client request. Issues #766 and #767 remain open.
- Economics: not measured. Research delegation for this work ran on the local
  vLLM endpoint at zero marginal token cost.

## Older entries

See `planning/archives/changelog_archive.md` for the 370 entries older
than the last 10.
