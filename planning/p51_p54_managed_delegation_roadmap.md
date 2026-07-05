# P51-P54 Managed Delegation Roadmap

## Context

P50 started as a FreshForge P16 A/B benchmark, but the most useful finding was
broader than that single package task. Broad API-design delegation is a poor
near-term target for current local Ollama workers. High-volume, chunkable,
source-anchored work is a much better place to look for positive delegation
economics.

The MP11 document-indexing experiments in `agent-delegation-lab` then showed a
more promising pattern:

- local workers can cheaply process large public technical documents;
- 24-page ticket windows avoided large-context collapse;
- quiet orchestration and scripted summaries compressed supervisor mechanics
  cost;
- source-level audit cost is real but measurable; and
- accepted/repairable candidate rates were high enough to justify deeper
  repair-loop experiments.

The next roadmap tranche should therefore move from one-off delegation tickets
to managed workflow lanes. The goal is to give free local workers enough
structure that they can iterate inside bounded lanes while the paid supervisor
acts as boundary controller, sampler, and final decision maker.

## P51: Managed Delegation Workflow Lanes

Issue: #347

Goal: define the reusable graph and template vocabulary for managed delegate
workflows.

Key outputs:

- workflow graph patterns for extractor, self-auditor, repairer, convergence
  checker, and supervisor-auditor roles;
- stop conditions and iteration-budget rules;
- authority boundaries for local self-audit and repair loops;
- generic templates that are not tied to MP11, FEMIC, or FreshForge; and
- document-library workflow graph updates that include local self-audit and
  delegated repair nodes.

Success condition: Agent Workbench can describe a managed local-worker loop
without making the paid supervisor reinvent the orchestration shape for every
job.

## P52: Local Self-Audit And Repair Loop

Issue: #348

Goal: dogfood a bounded self-audit/repair loop on the MP11 qwen x16 audit
sample and measure whether it reduces paid supervisor review cost.

Key outputs:

- local self-audit ticket;
- delegated repair-iteration ticket;
- deterministic convergence summary;
- one measured `gpt-oss` or comparable local-worker loop over the MP11 sample;
- paid supervisor delta-review token accounting; and
- updated audit calibration record comparing direct audit versus
  self-audit/repair-assisted review.

Success condition: the experiment can say whether local self-audit plus repair
improves economics, output quality, or neither.

## P53: Document Library Index Pilot

Issue: #349

Goal: apply the document-library workflow template to a small multi-document
public corpus so the evidence moves beyond one MP11 PDF.

Key outputs:

- corpus registry for at least two public technical documents;
- chunk manifests and extraction records;
- structure/content metadata runs;
- audit calibration observations; and
- cross-document tuning metadata.

Success condition: the workflow reveals whether the MP11-derived ticket size,
model choice, and audit strategy generalize across documents or need retuning.

## P54: Delegation Loop Policy Tuning

Issue: #350

Goal: convert the managed-loop evidence into conservative, explainable policy
guidance.

Key outputs:

- rules for when to split, retry, repair, self-audit, escalate, or stop;
- task-shape thresholds for document indexing workloads;
- model/protocol suitability updates;
- audit-cost and repair-yield decision guidance; and
- explicit missing-evidence reporting.

Success condition: Agent Workbench can recommend a managed workflow shape from
task metadata and prior evidence without pretending narrow benchmark results
are universal.

## Boundary

These phases do not replace supervisor responsibility. Local self-audit is not
validation; it is cheap defect reduction. Local repair is not approval; it is a
candidate-improvement step. The supervisor still owns final acceptance,
promotion, GitHub actions, and scientific/model-development decisions.
