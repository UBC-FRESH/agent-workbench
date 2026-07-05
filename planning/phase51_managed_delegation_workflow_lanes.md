# Phase 51 Managed Delegation Workflow Lanes

## Purpose

P51 turns the P50 evidence into reusable managed-loop structure. The point is
to stop spending paid supervisor tokens reinventing the same orchestration
shape for every delegated job.

The core lane is:

1. A supervisor or deterministic script prepares a bounded ticket.
2. A local worker extracts candidate records.
3. A local worker in self-audit mode labels likely defects.
4. A local worker in repair mode repairs only source-supported defects.
5. A deterministic convergence checker decides whether to continue, stop,
   escalate, or abandon.
6. The paid supervisor performs source-level delta review and owns final
   acceptance, promotion, scale, and closeout decisions.

This does not make the local model a trusted validator. It makes the local model
a cheap candidate generator, defect finder, and repair drafter inside a narrow
workflow lane.

## Role Vocabulary

The tracked role vocabulary lives in `templates/managed_role_vocabulary.json`.

The important boundary is ownership:

- `extractor`: local worker, proposal-only source-anchored candidate records.
- `self_auditor`: local worker, defect labels only.
- `repairer`: local worker, candidate repair only.
- `convergence_checker`: deterministic script or policy, routing only.
- `supervisor_auditor`: paid supervisor, final source-level audit and
  acceptance.

Local self-audit is not validation. Local repair is not approval. The
supervisor still owns tracked-file promotion, GitHub mutation, scientific
acceptance, economics interpretation, and phase closeout.

## Stop Conditions

The tracked stop-rule template lives in
`templates/managed_iteration_stop_rules.json`.

The default policy gives the local loop a bounded opportunity to improve
candidate quality without allowing infinite churn:

- stop at a configured maximum iteration count;
- escalate after repeated format failures;
- stop when two iterations show no meaningful improvement;
- abandon or rechunk when record retention is too low;
- require a supervisor checkpoint before scaling; and
- treat convergence as readiness for supervisor delta-review, not approval.

These rules are deliberately conservative. They are intended to generate
repeatable evidence for later P54 policy tuning, not to maximize autonomy.

## Graph Templates

P51 adds `templates/workbench_templates/managed_delegate_loop_graph.json` as
the generic loop pattern.

P51 also updates
`templates/workbench_templates/document_library_index_graph.json` so public
technical-document indexing can use the same managed local-worker loop:

- structure/content extraction;
- local self-audit;
- delegated repair iteration;
- deterministic convergence check;
- paid supervisor audit calibration; and
- supervisor-approved index assembly.

This is the intended near-term path for high-volume technical-document
metadata indexing, including the MP11-style benchmark and future public
document-library pilots.

## What This Buys

The managed lane should reduce paid-token cost in three ways:

- reusable graph structure reduces ad hoc supervisor planning;
- self-audit and repair drafts reduce first-pass supervisor review burden; and
- convergence checks stop weak runs before they create more supervisor cleanup.

The lane may still lose on economics if local outputs are too noisy, if the
ticket size is wrong, or if supervisor audit remains as expensive as direct
completion. P52 and P54 are responsible for measuring that.

## Verification Notes

P51 is governance/template work. It does not run a new worker experiment.

Required verification:

- validate JSON templates;
- validate graph metadata where FreshForge is available;
- inspect Markdown rendering;
- scan tracked files for raw transcripts, provider details, credentials,
  private paths, and raw source text.

## Verification Results

P51 verification passed in the local Agent Workbench environment:

- `python -m json.tool` accepted the role vocabulary, stop-rule template,
  generic managed-loop graph, and updated document-library graph.
- `.venv\Scripts\python.exe -m agent_workbench graph validate --input templates/workbench_templates/managed_delegate_loop_graph.json --agent-metadata`
  returned `ok: true` with six nodes and no diagnostics.
- `.venv\Scripts\python.exe -m agent_workbench graph validate --input templates/workbench_templates/document_library_index_graph.json --agent-metadata`
  returned `ok: true` with nine nodes and no diagnostics.
- `.venv\Scripts\python.exe -m pytest` passed all seven tests.
