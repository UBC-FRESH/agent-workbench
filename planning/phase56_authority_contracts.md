# Phase 56 Authority Contract Scaffold

This note records the first concrete implementation slice for the authority
hierarchy direction.

P56 is not yet opened as a GitHub phase issue, but the core contract surface is
useful immediately for P55/P57 experiments: supervisor tickets need a
machine-checkable way to declare role boundaries, workspace roots, allowed
tools, output artifacts, final signals, and public-safety posture.

## Implemented Contract Surface

New command group:

```powershell
python -m agent_workbench authority validate --kind contract --input templates\supervisor_job_contract.json
python -m agent_workbench authority validate --kind report --input templates\supervisor_job_report.json
python -m agent_workbench authority render --kind contract --input templates\supervisor_job_contract.json --output runtime\authority_contract.md
python -m agent_workbench authority render --kind report --input templates\supervisor_job_report.json --output runtime\authority_report.md
```

Tracked templates:

- `templates/supervisor_job_contract.json`
- `templates/supervisor_job_report.json`
- `templates/document_artifact_audit_supervisor_contract.json`
- `templates/document_artifact_audit_supervisor_ticket.md`

Validation module:

- `src/agent_workbench/authority.py`

Tests:

- `tests/test_authority.py`

## Contract Rules

The supervisor job contract requires:

- all four authority roles: `developer`, `coordinator`, `supervisor`, and
  `worker`;
- workspace root and root policy;
- explicit wrong-root stop rule;
- input and output artifacts;
- allowed tools;
- forbidden actions;
- stop conditions;
- success criteria;
- allowed final signals;
- verification requirements;
- public-safety posture.

The final signal vocabulary is:

- `job_complete`
- `job_complete_with_caveats`
- `needs_coordinator_review`
- `needs_developer_decision`
- `job_failed`
- `job_aborted`
- `job_partially_complete`

Tracked templates must remain public-safe. Runtime-only contracts may use
absolute workspace roots when `public_safety.tracked_artifact` is `false`.
This preserves the P55 lesson that Copilot tickets often need explicit
absolute roots in multi-root VS Code sessions, without leaking those paths into
tracked docs.

## Immediate Use

Use this contract layer before the next Copilot supervisor delegation test:

1. Materialize a runtime-only supervisor job contract with the real workspace
   root and output path.
2. Validate it with `agent-workbench authority validate --kind contract`.
3. Embed or attach the validated contract in the Copilot supervisor ticket.
4. Require the supervisor to write a report matching
   `templates/supervisor_job_report.json`.
5. Validate the report before scoring the run.

This creates the bridge between the high-level hierarchy design and concrete
P57 subagent experiments.

## Document-Artifact Audit Template

The P57 strict repeat showed that the local Copilot supervisor can preserve a
document-indexing gate result when the decision vocabulary and invariants are
explicit. That pattern is now captured as a tracked template pair:

- `templates/document_artifact_audit_supervisor_contract.json`
- `templates/document_artifact_audit_supervisor_ticket.md`

The template exists to prevent the paid coordinator from re-deriving the same
audit ritual for each document-indexing run. It requires:

- explicit source summary and report paths;
- a named auditor subagent;
- an allowed decision vocabulary:
  `paid_supervisor_audit_required`, `quote_repair_required`,
  `ready_to_scale`, and `needs_coordinator_review`;
- a gate-to-decision invariant, including the rule that
  `quote-repair-needed` maps to `quote_repair_required`; and
- required report JSON fields that the Copilot bridge can verify after the
  run.

This is still a template, not a full graph compiler. The next step is to
materialize runtime contracts and tickets from it for larger P57 supervisor
scope tests, then move the same role boundaries into FreshForge-compatible
workflow graph metadata.

## FreshForge-Compatible Graph Mapping

The P57 document-artifact audit workflow is now represented as a
FreshForge-compatible graph:

- `templates/workbench_templates/document_artifact_audit_supervisor_graph.json`

The graph maps the authority hierarchy into node metadata:

- coordinator-owned ticket preparation;
- supervisor-owned materializer execution;
- worker-owned subagent artifact audit;
- supervisor-owned report writing;
- coordinator-owned authority validation and repair routing; and
- coordinator-owned developer review packet assembly.

Validation command:

```powershell
python -m agent_workbench graph validate `
  --input templates\workbench_templates\document_artifact_audit_supervisor_graph.json `
  --agent-metadata
```

Decision-rendering command:

```powershell
python -m agent_workbench graph decide `
  --input templates\workbench_templates\document_artifact_audit_supervisor_graph.json `
  --output runtime\graphs\document_artifact_audit_supervisor_graph_decisions.md `
  --agent-metadata
```

The graph validates with six nodes and no diagnostics. The delegation decision
adapter now maps graph authority strings into decision-engine authority levels,
so `worker-owned` subagent audit nodes become `L1`, while supervisor,
coordinator, and developer nodes remain outside the worker delegation boundary.
