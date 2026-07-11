# Phase 92 Whole-Document Supervisor Pilot

P92 retargets the packaged pilot around the highest-ROI delegation shape:
one delegated local supervisor receives the complete public technical document,
runs the document metadata extraction role, and returns one compact report for
coordinator validation.

## Why This Replaces The Chunk Battery Default

The P89/P90 section-ticket run proved that local workers can produce useful
source-backed candidates, but it also exposed a coordinator failure mode:
paid coordination can spend too much effort pre-decomposing, policing, and
re-auditing tiny chunks. That is not the product thesis.

The P92 hypothesis is that the coordinator should behave more like a traffic
controller:

- select one real document;
- define one delegated supervisor role and report contract;
- materialize one runtime ticket;
- validate one returned report;
- issue one compact bounce only if the minimum bar fails;
- decide whether to accept seed, repair, switch lane, or stop.

## Materialized Artifacts

Tracked public-safe artifacts:

- `templates/workbench_templates/document_library_whole_document_supervisor_graph.json`
- `.github/agents/document-metadata-extraction-supervisor.agent.md`
- `.github/agents/overlays/document-metadata-extraction-supervisor.md`
- `benchmarks/document_library/p92_whole_document_supervisor_pilot_manifest.json`
- `benchmarks/document_library/p92_whole_document_supervisor_gate.json`
- `benchmarks/document_library/p92_whole_document_supervisor_report_contract.json`
- `benchmarks/document_library/p92_whole_document_supervisor_roi_estimate.json`

Ignored runtime artifacts:

- `runtime/document_library/tsa23_tsr/p92_whole_document_supervisor_pilot/tickets/p92_tsa23_2012_23tsdp12_whole_document_supervisor.ticket.md`
- `runtime/document_library/tsa23_tsr/p92_whole_document_supervisor_pilot/tickets/p92_tsa23_2012_23tsdp12_bounce_redo.ticket.md`
- `runtime/document_library/tsa23_tsr/p92_whole_document_supervisor_pilot/p92_runtime_index.json`

## Gate

The current P92 gate passes for materialization:

- the selected document is nontrivial;
- P90 produced nontrivial candidate volume;
- P91 produced a promotable audited seed after source-quote scoring
  recalibration.

The gate does not authorize repeated live runs. The first live run still needs:

- explicit maintainer approval for one delegated supervisor attempt;
- supervisor-token start/end checkpoints around coordinator launch, validation,
  and decision work;
- one named custom agent/model lane;
- full local supervisor tool access inside a report-only authority boundary;
- hard stop after one initial run plus one compact bounce if needed.

## Decision Standard

The pilot succeeds only if the result separates:

- quality outcome: whether the returned seed contains useful source-anchored
  candidate records;
- protocol outcome: whether the delegated supervisor stayed within authority
  and report-shape boundaries;
- economics outcome: whether coordinator overhead plausibly improves on the
  P90/P91 chunk-pipeline minimum.

The pilot can still be useful if it returns `repair` rather than `accept_seed`.
It fails the ROI test if the coordinator has to rebuild a chunk-level ritual to
understand the result.
