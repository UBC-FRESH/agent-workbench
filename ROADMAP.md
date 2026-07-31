# Agent Workbench Roadmap

<!-- Migration: 2026-07-23. Full historical issue-tracker map is in
     planning/archives/issue_tracker_archive.md. Generated projections
     are in runtime/projections/ (ignored). -->

This roadmap is the current project plan and issue tracker map. Keep it
synchronized with GitHub issues, planning notes, pull requests, and
`CHANGE_LOG.md`.

## Active phase

- P125 Popup remote LLM provider deployment framework (#769).
  Planning: `planning/p125_popup_provider_framework.md`.
  Framework: `playbooks/popup_provider/`.
  Target 1 (Sockeye) verified; target 2 outstanding.
  Pending child issue — P125.3 Sockeye 32B upgrade, planned in
  `planning/p125_sockeye_32b_upgrade.md`, not yet filed (GitHub write tools
  disabled).

- P121 CPU document scraper implementation (#758), child task #759.

- P122 HPC GPU capacity and provider workflow (#760), child task #761.

## Recent completed phases

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P120 SDK-authoritative agent-hub qualification | #755 | `feature/p120-sdk-authoritative-agent-hub` | Complete |
| P121 CPU document scraper implementation | #758 | `feature/p121-cpu-document-scraper` | Active — P121.1 #759 |
| P122 HPC GPU capacity and provider workflow | #760 | `feature/p122-hpc-gpu-capacity-provider` | Active — P122.1 #761 |
| P119 Blackwell/vLLM phase | #749 | `feature/p119-blackwell-vllm` | Complete |
| P118 Concurrency stress testing | #743 | `feature/p118-concurrency-stress` | Complete |
| P115 Validation fixtures | #731 | `feature/p115-validation-fixtures` | Complete |

## Full issue-tracker map

See generated projection: `runtime/projections/issue_tracker_map.md`
(Regenerate with: `python scripts/generate_projections.py issue-tracker-map`)

## Completed phase archive

See `planning/archives/` for completed-phase summaries.
