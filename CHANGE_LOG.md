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

## 2026-07-31 - P125 Sockeye findings, contract fix, and 32B plan

- Ruled out both MoE candidates on Sockeye. The sm70/Volta vLLM 0.10.0 build
  has no MoE kernels: engine startup dies with `_moe_C` missing
  `topk_softmax`. `qwen3-coder-next` is absent from the registry entirely.
- Recorded the Sockeye billing model: `MAX_TRES` over
  `CPU=1.0,Mem=5.00G,gres/gpu=6.0`. The 120G memory request bills 600 while 4
  GPUs bill 24, so memory — not GPUs — is the cost lever. Measured vLLM host
  RSS was 0.9 GB against that 120G request.
- Recorded that tool calling fails on the 7B despite correct server flags and
  a correct checkpoint template; the model emits markdown-fenced JSON. Logged
  as a measured model property (`tool_calling_verified: false`), not a
  misconfiguration.
- Fixed a structural defect in the Coordinator contract: it declared a local
  default model, forbade the frontmatter mechanism, and never mentioned
  `runSubagent`'s `model` parameter, so every delegation silently inherited
  the paid frontier chat model.
- Corrected a fabricated issue reference (`#770`) in `ROADMAP.md`. No such
  issue existed at the time. **Note (2026-08-01):** issue `#770` has since been
  created for an unrelated purpose — a docs-sync ticket for the published
  roadmap overview. The correction above was right when made; the number was
  later assigned by GitHub to a genuine, different issue. Do not read the
  present existence of `#770` as evidence the original reference was valid.
- Planned the 32B dense upgrade in `planning/p125_sockeye_32b_upgrade.md`.
- Quality: all cluster interaction was read-only; the provider was verified
  serving and undisturbed throughout.
- Protocol: the P125.3 child issue is drafted but unfiled — GitHub write
  tools are disabled. Two delegations in this session ran on the frontier
  chat model because `model` was omitted.
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

## 2026-08-01 - Agent Hub Advisor lane: model binding, caps and floors removed

- Removed the hard "at most one Advisor invocation per roadmap phase" cap, then
  removed hard floors as well. Ceilings and floors are the same defect:
  agent-planted rules that convert judgment into ritual. Deleted the
  mandatory-invocation apparatus from
  `planning/native_codex_remote_ollama_findings.md` — seven mandatory Advisor
  triggers, a required consultation-packet schema, and a five-step enforcement
  ladder ending in "make deterministic closeout validation fail when a mandatory
  trigger is present but no Advisor evidence exists." Retained the underlying
  signal (where advice has paid off), explicitly labelled as not a checklist.
- Bound the Advisor to a paid frontier model, `claude-opus-5`
  (`Claude Opus 5 (copilot)`). Supervisor and Worker lanes remain on the local
  vLLM model. Chosen on catalog evidence: every Claude model bills long context
  at the flat short-context rate, while every GPT-5.x, Gemini Pro, and Grok
  model charges 2.0x input / 1.5x output past the threshold. The Advisor is a
  large-context role by construction.
- Made Advisor continuity file-based in `planning/advisor_dossier.md`. Copilot
  subagents are stateless across invocations — no resume handle, no follow-up
  channel — so standing positions must be auditable artifacts rather than an
  unlogged memory trace.
- Reconciled the superseded "all roles share one model" claim across `AGENTS.md`,
  `.github/copilot-instructions.md`, both affected agent profiles,
  `planning/delegation_policy.md`,
  `planning/authority_hierarchy_and_subagent_direction.md`,
  `playbooks/p118_single_model_operator_checklist.md`,
  `planning/p120_sdk_authoritative_agent_hub_qualification.md`, and
  `docs/roadmap_and_release/roadmap_overview.md`.
- Scoped `model_profiles/pricing_catalog.json` explicitly to OpenAI
  first-party API rates. It was correct for what it claimed but unlabelled, and
  was nearly used to validate Copilot billing. Copilot rates differ materially
  (`gpt-5.6-luna` by 5x). Entries and rates unchanged; tests pass.
- Added `notes/operations/copilot-model-catalog.md`: how to enumerate the live
  Copilot catalog from the chat extension's per-session `models.json`, the
  25 picker-enabled models with rates and reasoning-effort ladders, selection
  traps, and subagent routing behaviour.
- Filed #770 for the stale published roadmap overview (see the disambiguation
  note above — the number was previously used by a fabricated reference).
- Quality: measured rather than assumed. `Claude Opus 5 (copilot)` probed and
  self-identified. An explicit `model` argument on `runSubagent` was shown to
  **override** profile `model:` frontmatter, so frontmatter is a fallback and
  not a guardrail; the no-argument fallback path is recorded as **unverified**
  because the test chat ran the same model, making the two cases
  indistinguishable.
- Protocol: the change set was reviewed by the Advisor before commit; its
  findings and the Coordinator's dispositions, including deferrals, are in
  `planning/advisor_dossier.md`. Commit `36eda1b` bundled pre-existing
  uncommitted work from earlier sessions, disclosed in its message.
- Economics: not measured. Advisor invocations this session were not
  token-accounted.

## 2026-08-01 - P125 Nibi sanitization, readiness qualification, and planning

- Qualified the 2026-07-26 "verified bring-up" in `notes/clusters/nibi.md` so
  it no longer implies unqualified Qwen3.6 readiness. The earlier verification
  covered SSH login only; the 2026-08-01 P125 investigation did not prove
  readiness. Added a scope-of-verification note to the Verified outcome
  section and a precise current conclusion in the P125 findings section.
- Scrubbed real-world identifiers from allowed staged public artifacts:
  `notes/clusters/nibi.md`,
  `playbooks/popup_provider/targets/arbutus.example.yaml`,
  `planning/session_cbebdef3_summary.md`,
  `planning/p125_handoff_sockeye_blocked.md`, and
  `CHANGE_LOG.md`. Replaced `def-gep`/`st-gep` allocation names, tunnel UUID
  `51059526`, tunnel hostname `fresh02-vllm`, tunnel name `nginx`, jump-host
  IP `134.87.8.128`, and local secrets path `/srv/shared-data/vllm/secrets.env`
  with generic placeholders. Retained `nibi.alliancecan.ca` where useful.
- Added a new test class `TestPublicArtifactMarkerScan` in
  `tests/test_popup_provider_nibi.py` that scans the Nibi descriptor, Arbutus
  descriptor, and `notes/clusters/nibi.md` for the scrubbed markers. Tests
  enforce that no marker re-enters the public artifact surface.
- Added a "Remote-state changes performed on Nibi" subsection to
  `notes/clusters/nibi.md` documenting SSH alias repair, HF credential
  provisioning, venv repair, scratch model/config/shim, and cleanup, with a
  token scope/revocation caution.
- Replaced intent claims ("lied", "gaslit") in
  `planning/session_cbebdef3_summary.md` with auditable behavior descriptions
  (post-hoc rationalization, post-hoc justification) and qualified stale
  present-state claims with "as of 2026-08-01".
- Economics: three Nibi allocations were consumed during the P125 investigation
  with no readiness proven:
  - Allocation `18923603` on `g30` (two-hour probe) — timed out during
    environment installation.
  - Allocation `18927835` on `g31` — canceled by Slurm with `ReqNodeNotAvail`
    before vLLM started.
  - Allocation `18939706` on `g30` (8-hour allocation) — ran for 1:11:09
    before being canceled after the model-load investigation had no active
    server. Did not leave a provider or listener running.
  Total documented runtime: 1:11:09 of active compute (allocation `18939706`);
  the other two allocations contributed wall-clock time but no productive
  output. No readiness claim is made for Qwen3.6 on Nibi.
- Quality: all changes are documentation-only; no infrastructure, SSH, Slurm,
  Cloudflare, or GitHub state was touched. All 57 Nibi tests pass.
- Protocol: the scrubbed markers are now detectable by test; any reintroduction
  will fail the test suite. The qualification of the 2026-07-26 verification
  is explicit and auditable.
- Economics: no provider usage was incurred by this documentation pass.

## Older entries

See `planning/archives/changelog_archive.md` for entries older than the
last 10 entries.
