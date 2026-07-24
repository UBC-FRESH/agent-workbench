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

## Older entries

See `planning/archives/changelog_archive.md` for entries older than the
last 10 entries.