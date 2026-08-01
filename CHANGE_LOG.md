# Change Log

<!-- Migration: 2026-07-23. Older entries are in
     planning/archives/changelog_archive.md. -->

Newest entries are last. Keep this file synchronized with `ROADMAP.md`, GitHub
issues, pull requests, and closeout comments.

## 2026-08-01 - P126 Agent Hub core roles and overlays

- Reduced the default Agent Hub catalog to four model-neutral profiles:
  Coordinator, Supervisor, Worker, and Advisor.
- Removed the duplicate model-era Worker variant and migrated the default
  Supervisor and Worker names to generic role identities.
- Restricted cross-project installation to the four core profiles plus the
  standard overlay catalog, so provider probes and specialized experiments are
  not silently installed.
- Added user-scope overlay transport and resolver fallback, with disposable
  target-workspace coverage proving core-role and overlay composition outside
  the Agent Workbench checkout.
- Added explicit `target_roles` metadata to the standard overlays and validated
  that overlays target only the four core roles.
- Kept deployment model/provider selection outside core profile identity.

Quality: focused installer, profile-catalog, setup, and cross-environment
validation passes (`53 passed`); the optional Copilot SDK bridge remains
separately dependent on the local SDK package.
Protocol: P126 remains scoped to core roles, overlays, installer behavior, and
documentation; no provider deployment or cluster work is included.
Economics: no provider inference or remote deployment work was required.

## 2026-08-01 - Interim Agent Hub setup playbook (docs PR)

- Created `playbooks/agent_hub_setup.md`: tiered canonical setup guide
  covering Tier 0 (stock Copilot + repo profiles), Tier 1 (GitHub MCP
  reference playbook), Tier 2 (custom provider reference playbook), and Tier 3
  (bridge/scripts). Includes credential boundary rules, pass/fail smoke
  checklist, and verification table with Linux code-server measured facts
  and Windows Desktop explicitly unverified.
- Included the full reference playbooks:
  `playbooks/github_mcp_setup.md` and
  `notes/operations/keklick-copilot-extension-config.md`.
- Linked playbook from `README.md`, `AGENTS.md`, and
  `.github/copilot-instructions.md`.
- Added `tests/test_agent_hub_setup_playbook.py`: referential-integrity and
  sanitization test scanning for private paths, tokens, endpoint markers,
  link resolution, and agent profile resolution.
- Clean-environment manual testing remains pending.

## 2026-08-01 - Agent Hub clean-session seed prompt

- Added `playbooks/agent_hub_seed_prompt.md` as the tracked copy-paste prompt
  for Tier 0 instruction-loading and Coordinator-routing smoke tests.
- Linked the seed prompt from the setup playbook, README, and always-on Copilot
  instructions so new clean sessions can discover it locally.
- Extended `tests/test_agent_hub_setup_playbook.py` to verify the seed prompt's
  existence, expected sections, link, and public-safe content.

Quality: seed prompt and setup links are covered by focused integrity tests.
Protocol: prompt is documentation-only and does not grant credentials,
delegation, remote access, or GitHub mutation authority.
Economics: not applicable (tracked prompt and test update only).

## 2026-08-01 - Agent Hub cross-project profile installation

- Added `scripts/install_agent_hub_profiles.py` to copy the tracked custom-agent
  profiles into the Copilot user scope at `~/.copilot/agents`.
- Documented the distinction between workspace-scoped `.github/agents` and
  user-scoped profiles available across other projects.
- Added conflict-safe installer tests covering first install, idempotency,
  explicit replacement, and dry-run behavior.

Quality: installer behavior is covered by focused tests; live Copilot picker
discovery still requires an editor reload and clean target-workspace check.
Protocol: installer writes only the user-specified profile destination and
never edits target repositories or credential files.
Economics: not applicable (local file copy and tests only).

## 2026-08-01 - Agent Hub full-contract deployment

- Extended `scripts/install_agent_hub_profiles.py` to install the complete
  Agent Hub contract as `~/.copilot/instructions/agent-workbench.instructions.md`
  in addition to the user-level custom-agent profiles.
- Updated the canonical contract and seed prompt for target workspaces where
  Agent Workbench is not the opened repository.
- Added tests for global instruction frontmatter, idempotency, and conflict
  protection.

Quality: full-contract deployment is covered by focused installer tests and
the generated user instruction contains the Coordinator hierarchy and evidence
rules.
Protocol: deployment writes only user-level Copilot customization paths; it
does not modify target repositories or credentials.
Economics: not applicable (local instruction/profile installation only).


Quality: playbook structure, tiering, and link integrity verified by test.
Protocol: one bounded docs task on `docs/agent-hub-setup` branch; no commits,
pushes, PRs, SSH, or unrelated file mutations.
Economics: not applicable (documentation-only task, no model inference).

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

## Older entries

See `planning/archives/changelog_archive.md` for entries older than the
last 10 entries.
