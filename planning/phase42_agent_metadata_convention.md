# Phase 42 Agent Metadata Convention

## Purpose

P42 defines how Agent Workbench stores delegation metadata inside
FreshForge-compatible graph documents without forking the graph shape.

FreshForge remains responsible for structural graph validation. Agent Workbench
adds a semantic metadata check for the fields needed by supervisor/delegation
workflows.

## Field Placement

Canonical Agent Workbench graph templates use FreshForge fields as follows:

| FreshForge field | Agent Workbench usage |
| --- | --- |
| `parameters.agent_workbench` | Agent Workbench node semantics, evidence references, claim-review policy, supervisor-decision policy, and token/cost record references. |
| `artifacts` | Source, generated, promoted, and rejected artifacts referenced by the node. |
| `provenance` | Role, capability, authority level, implementation, model/profile reference, and related execution provenance. |

Canonical templates should not add Agent Workbench-only top-level node fields
such as `role`, `capability`, `authority_level`, `implementation`,
`token_accounting`, `claim_review`, or `supervisor_decision`.

## Required Node Metadata

When `agent-workbench graph validate --agent-metadata` is used, each node must
provide:

- `provenance.role`;
- `provenance.capability`;
- `provenance.authority_level`;
- `provenance.implementation`;
- `parameters.agent_workbench.node_kind`; and
- `parameters.agent_workbench.execution_boundary`.

This is intentionally small. It makes each node inspectable without forcing all
future evidence, claim-review, decision, and accounting metadata into one rigid
schema too early.

## Optional Semantic Metadata

Graph nodes may also include:

- `parameters.agent_workbench.evidence_reference`;
- `parameters.agent_workbench.claim_review`;
- `parameters.agent_workbench.supervisor_decision`;
- `parameters.agent_workbench.token_accounting`;
- `parameters.agent_workbench.allowed_authority`; and
- `provenance.model_profile`.

Raw prompts, raw transcripts, provider URLs, headers, credentials, and personal
paths remain forbidden in tracked graph templates.

## Validation Boundary

The P42 metadata validator is a supervisor-side convention check. It does not
execute graph nodes, register FreshForge providers, contact model providers, or
decide whether a worker result is accepted.

The validator exists to catch metadata drift before graph-backed pilots start
in P43.

## Verification Notes

The canonical template validates with:

```powershell
python -m agent_workbench graph validate --input templates/workbench_templates/agentic_workflow_graph.json --agent-metadata
```

The command reports `ok: true`, workflow id
`example_agentic_workbench_graph`, four nodes, and no diagnostics.

An ignored negative fixture with top-level `role`, missing
`provenance.authority_level`, missing `provenance.implementation`, and missing
`parameters.agent_workbench` exits nonzero and reports the expected metadata
diagnostics.
