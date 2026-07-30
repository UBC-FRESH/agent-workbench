# Agent Workbench Roadmap

<!-- Migration: 2026-07-23. Full historical issue-tracker map is in
     planning/archives/issue_tracker_archive.md. Generated projections
     are in runtime/projections/ (ignored). -->

This roadmap is the current project plan and issue tracker map. Keep it
synchronized with GitHub issues, planning notes, pull requests, and
`CHANGE_LOG.md`.

## Active phase

- P124 Sockeye private vLLM provider bring-up (#766), child task #767.

## Parked phase

- P123 CPU scraper benchmark and route decision (#764), child task #765.
  Parked pending a private provider that satisfies P124 readiness checks.

## Recent completed phases

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P120 SDK-authoritative agent-hub qualification | #755 | `feature/p120-sdk-authoritative-agent-hub` | Complete |
| P121 CPU document scraper implementation | #758 | `feature/p121-cpu-document-scraper` | Complete — child #759 and PR #762 |
| P122 HPC GPU capacity and provider workflow | #760 | `feature/p122-hpc-gpu-capacity-provider` | Complete — child #761 and PR #763 |
| P119 Blackwell/vLLM phase | #739 | `feature/p119-blackwell-vllm` | Complete |
| P118 Concurrency stress testing | #743 | `feature/p118-concurrency-stress` | Complete |
| P115 Validation fixtures | #731 | `feature/p115-validation-fixtures` | Complete |

## Full issue-tracker map

See generated projection: `runtime/projections/issue_tracker_map.md`
(Regenerate with: `python scripts/generate_projections.py issue-tracker-map`)

## Completed phase archive

See `planning/archives/` for completed-phase summaries.
