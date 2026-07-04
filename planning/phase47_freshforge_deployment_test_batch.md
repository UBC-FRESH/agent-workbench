# Phase 47 FreshForge Deployment Test Batch

## Purpose

P47 queues a non-trivial Agent Workbench deployment-test batch against the next
FreshForge roadmap tranche without mutating FreshForge yet.

The target FreshForge phases are:

- P16: provider result and validation evidence conventions;
- P17: matrix aggregation and comparison exports; and
- P18: v0.1.0a6 evidence-orchestration PyPI alpha release.

## Test Batch

P47 adds three graph-backed test packet templates:

| Packet | FreshForge target | Purpose |
| --- | --- | --- |
| `templates/deployment_tests/freshforge/p16_provider_evidence_conventions_graph.json` | P16 | Test whether proposal-only workers can review provider evidence conventions while supervisor owns API decisions. |
| `templates/deployment_tests/freshforge/p17_matrix_export_graph.json` | P17 | Test whether workers can compare export shapes and downstream consumption needs while supervisor owns implementation. |
| `templates/deployment_tests/freshforge/p18_release_readiness_graph.json` | P18 | Test whether workers can help review release readiness while all release, tag, publish, and closeout actions remain supervisor-owned. |

## Expected Delegation Pattern

The graph-aware decision report should recommend delegation for bounded
proposal-only worker nodes:

- evidence review;
- export-shape comparison;
- downstream consumption review;
- release-readiness checklist review; and
- gap scan.

The report should keep supervisor-owned nodes in the direct lane:

- task selection;
- project-native verification;
- implementation and acceptance decisions;
- release, tag, publish, and GitHub closeout decisions.

## Boundary

P47 does not execute worker models and does not edit the FreshForge repository.
It queues the deployment-test batch so a later phase can run workers from these
packets, collect evidence, and decide which FreshForge work should actually be
implemented.

## Verification Commands

Each packet should pass:

```powershell
python -m agent_workbench graph validate --input <packet> --agent-metadata
python -m agent_workbench graph render --input <packet> --output <ignored-report> --agent-metadata
python -m agent_workbench graph decide --input <packet> --output <ignored-report> --agent-metadata
```

The decision reports are local ignored evidence. Only sanitized conclusions are
tracked.

## Verification Result

All three packet graphs validated with `--agent-metadata` and rendered to local
ignored reports.

The graph-aware decision reports produced the expected delegation split:

- P16 provider evidence packet:
  - `select_p16_scope`: `do-directly`;
  - `worker_provider_evidence_review`: `delegate`;
  - `worker_fixture_proposal`: `delegate`;
  - `supervisor_p16_acceptance`: `do-directly`.
- P17 matrix export packet:
  - `select_p17_scope`: `do-directly`;
  - `worker_export_shape_comparison`: `delegate`;
  - `worker_downstream_packet_review`: `delegate`;
  - `project_native_p17_verification`: `do-directly`.
- P18 release-readiness packet:
  - `select_p18_release_scope`: `do-directly`;
  - `worker_release_readiness_review`: `delegate`;
  - `worker_release_gap_scan`: `delegate`;
  - `supervisor_release_verification`: `do-directly`;
  - `supervisor_release_decision`: `do-directly`.

The FreshForge repository remained clean during P47. No FreshForge files,
issues, releases, tags, or branches were mutated.
