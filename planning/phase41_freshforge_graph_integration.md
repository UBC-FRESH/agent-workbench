# Phase 41 FreshForge Graph Integration

## Purpose

P41 tests whether Agent Workbench can reuse FreshForge as the structural graph
layer for agentic role workflows instead of growing a parallel workflow graph
validator.

The target architecture is:

```text
Agent Workbench delegation and evidence semantics
  on top of
FreshForge-compatible graph records and validation
  around
project-native execution tools
```

## Scope

This phase is a non-executing graph-validation spike. FreshForge is added as an
optional dependency so Agent Workbench can validate graph shape when the graph
extra is installed.

P41 does not execute FreshForge workflows. It also does not register Agent
Workbench provider metadata yet. Provider-aware validation is deferred until the
next tranche after the structural compatibility question is answered.

## Implementation

P41 adds:

- `agent-workbench[graph]` optional dependency metadata for FreshForge;
- `src/agent_workbench/graph.py` as the optional FreshForge validation adapter;
- `agent-workbench graph validate --input <path>`;
- `templates/workbench_templates/agentic_workflow_graph.json`, a
  FreshForge-valid graph template with Agent Workbench role/capability,
  authority, implementation, artifact, and token-accounting metadata stored in
  FreshForge-compatible fields; and
- P42-P46 roadmap entries for the graph-backed delegation direction.

## Local Development Dependency Mode

For active graph-integration development, install the adjacent FreshForge clone
into the Agent Workbench virtual environment in editable mode:

```powershell
python -m pip install -e ../freshforge
python -m pip install -e ".[graph]"
```

This keeps the public package metadata compatible with released FreshForge
versions while allowing local FreshForge graph API changes to be tested
immediately during Agent Workbench development.

## Verification Notes

The positive validation check was:

```powershell
python -m agent_workbench graph validate --input templates/workbench_templates/agentic_workflow_graph.json
```

The command reported `ok: true`, workflow id
`example_agentic_workbench_graph`, four nodes, and no diagnostics when the
FreshForge graph extra was installed.

The missing-dependency check reported an actionable error telling the user to
install `agent-workbench[graph]` instead of producing a Python traceback.

Ignored runtime negative fixtures showed that the command exits nonzero and
reports FreshForge structural diagnostics for duplicate node ids, missing
dependencies, and dependency cycles.

## Boundary

FreshForge structural validation checks workflow id, node ids, node
dependencies, cycles, mapping fields, and artifacts. Provider-reference syntax
and provider metadata validation are intentionally deferred until Agent
Workbench registers provider metadata in a later phase.

Agent Workbench interprets delegation semantics: roles, capabilities, authority
levels, model profiles, evidence summaries, claim review, supervisor decisions,
and token/cash accounting.

Project-native tools execute project work. Those tools may include FreshForge,
project CLIs, notebooks, scripts, CI, or human review, but Agent Workbench does
not become the executor merely because it validates a graph document.

## Next Tranche Implication

If P41 remains clean, the next phases should deepen the integration rather than
inventing a separate Agent Workbench graph framework:

- P42 defines the Agent Workbench metadata convention inside FreshForge-compatible
  graph fields.
- P43 runs a real graph-backed pilot workflow.
- P44 makes the delegation decision engine graph-node aware.
- P45 records token/cash economics per graph node.
- P46 decides whether FreshForge remains optional, becomes required, or is kept
  behind a compatibility adapter.
