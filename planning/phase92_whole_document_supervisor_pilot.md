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
- `benchmarks/document_library/p92_whole_document_supervisor_decision_packet.json`

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

## Live Result And Decision

The accepted R3 run used `qwen3.6:35b-a3b-bf16` through the
`document-metadata-extraction-supervisor` custom-agent skin with autopilot
permission. The bridge observed `agent`, `create_file`, `runSubagent`,
`replace_string_in_file`, and `run_in_terminal`; the expected model resolved,
the final marker was present, and the bridge recorded no deviations.

Deterministic report validation returned `valid` with 28 candidate records and
zero fatal errors. The report read the source document, returned
`job_complete_with_caveats`, and recommended `accept_seed`. This is enough to
promote the report as a coordinator-audit seed without pretending all 28
records are already accepted index entries.

The economics outcome remains `not_yet_proven`. The measured coordinator span
was 449,382 tokens: 1,679 fresh input, 447,232 cached input, and 471 output. The
estimated cash cost was $0.087798, but the span exceeded the recorded 236,008
token P90/P91 minimum because launch, retry, and cached-context overhead were
still large.

The P92 decision is `accept_seed_for_coordinator_audit`. The whole-document
delegation shape produced useful auditable work and respected the intended
protocol boundary. Do not scale the lane broadly until launch and context
overhead are reduced; preserve the one-document report-and-decision-packet
shape rather than returning to coordinator-built section microtickets.
