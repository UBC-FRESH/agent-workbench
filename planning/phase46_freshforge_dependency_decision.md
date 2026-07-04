# Phase 46 FreshForge Dependency Decision

## Decision

FreshForge remains an optional Agent Workbench dependency through the `graph`
extra, but it is now the canonical graph-validation layer for Agent Workbench
graph documents.

In practical terms:

```powershell
python -m pip install -e ".[graph]"
```

enables FreshForge-backed graph validation, graph rendering, graph-aware
decision reports, and graph-node token/cost synthesis workflows.

For active local co-development, install the adjacent FreshForge checkout in
editable mode:

```powershell
python -m pip install -e ../freshforge
```

## Rationale

P41-P45 showed that FreshForge can support Agent Workbench graph needs without
requiring Agent Workbench to become a workflow engine:

- P41: FreshForge structural validation worked for Agent Workbench graph
  templates.
- P42: Agent Workbench metadata fit cleanly inside `parameters`,
  `artifacts`, and `provenance` without custom top-level graph fields.
- P43: a real FreshForge proposal-assist pilot could be represented as a
  FreshForge-compatible graph and rendered for supervisors.
- P44: graph-node metadata could drive delegation recommendations by reusing
  the existing rules-based decision engine.
- P45: graph-node token/cash economics could be synthesized from sanitized
  records.

No P41-P45 evidence justified building a parallel graph validator inside Agent
Workbench.

## Options Considered

### Required FreshForge Dependency

Pros:

- simplest mental model for graph-backed workflows;
- no optional install branch for graph commands; and
- stronger coupling to the UBC-FRESH graph vocabulary.

Cons:

- makes lightweight prompt/evidence/accounting installs heavier;
- couples Agent Workbench to FreshForge release cadence too early; and
- may imply that Agent Workbench executes workflows, which remains false.

### Optional FreshForge Dependency

Pros:

- keeps base Agent Workbench lightweight;
- enables graph-backed workflows when explicitly installed;
- allows local editable FreshForge co-development;
- avoids a duplicate graph engine; and
- preserves a clear non-execution boundary.

Cons:

- graph commands need clear missing-dependency errors;
- users must understand when to install the graph extra; and
- FreshForge API drift still needs active coordination.

### Adapter-Only Strategy

Pros:

- maximum insulation from FreshForge schema changes.

Cons:

- recreates a graph dialect by stealth;
- increases maintenance;
- weakens interoperability with FreshForge projects; and
- contradicts the P41-P45 evidence that direct FreshForge validation works.

## Final Position

Use FreshForge directly for graph structure and validation when graph support is
installed. Keep Agent Workbench responsible for delegation semantics, evidence,
claim review, supervisor decisions, and token/cash economics.

Do not build a parallel graph engine in Agent Workbench unless a future
FreshForge change creates a concrete, documented incompatibility.

## Follow-On Guidance

Future graph-backed phases should:

- keep the base install useful without graph extras;
- test graph commands with editable local FreshForge during co-development;
- keep provider registration and graph execution separate from Agent Workbench
  unless explicitly planned;
- continue pricing delegation economics by tokens rather than wall-clock time;
  and
- prefer adapting FreshForge graph records over inventing Agent Workbench-only
  graph structures.
