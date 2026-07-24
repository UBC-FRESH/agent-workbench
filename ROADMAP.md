# Agent Workbench Roadmap

<!-- Migration: 2026-07-23. Full historical issue-tracker map is in
     planning/archives/issue_tracker_archive.md. Generated projections
     are in runtime/projections/ (ignored). -->

This roadmap is the current project plan and issue tracker map. Keep it
synchronized with GitHub issues, planning notes, pull requests, and
`CHANGE_LOG.md`.

## Active phase

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P120 SDK-authoritative agent-hub qualification | #755 | `feature/p120-sdk-authoritative-agent-hub` | Active |

## Active tasks

- [x] P120.1 Coordinator-to-Worker implementation through SDK lane (#755 child)
- [x] P120.2 Tighten Coordinator/Advisor tool boundaries (#755 child)
- [x] P120.3 SDK result renderer (#755 child)
- [x] P120.4 Resolve ROADMAP.md worktree change (#755 child)
- [ ] P120.5 Roadmap/changelog architecture repair (#756 child)

## Recent completed phases

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P119 Blackwell/vLLM phase | #749 | `feature/p119-blackwell-vllm` | Complete |
| P118 Concurrency stress testing | #743 | `feature/p118-concurrency-stress` | Complete |
| P115 Validation fixtures | #731 | `feature/p115-validation-fixtures` | Complete |

## Full issue-tracker map

See generated projection: `runtime/projections/issue_tracker_map.md`
(Regenerate with: `python scripts/generate_projections.py issue-tracker-map`)

## Completed phase archive

See `planning/archives/` for completed-phase summaries.