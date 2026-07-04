# Phase 37 Artifact And Workflow Contract Model

Phase 37 makes the durable unit of work an artifact-first workflow step rather
than a chat transcript or model response.

## Artifact Vocabulary

Agent Workbench now recognizes four artifact kinds:

- `source`: an input artifact supplied by the supervisor, project, issue
  tracker, script, or workflow tool;
- `generated`: an intermediate output from a worker, human, script, CI job, or
  workflow tool;
- `promoted`: a generated or source-derived artifact accepted by the supervisor
  into a durable planning, code, docs, test, or release surface; and
- `rejected`: a generated artifact or claim explicitly rejected by the
  supervisor.

Each artifact record includes:

- artifact id;
- kind;
- path or reference;
- provenance;
- public-safety note;
- verifier; and
- supervisor decision when the artifact is promoted or rejected.

## Workflow Step Contract

`templates/workflow_step_record.json` defines a workflow step as:

- input artifacts;
- transformation;
- implementation;
- output artifacts;
- verification;
- token accounting; and
- supervisor decision.

The implementation can be a human, local worker, paid agent, script, CI job, or
external workflow tool. Agent Workbench records the implementation; it does not
require replacing the implementation.

## Non-Orchestration Boundary

P37 records workflow evidence; it does not execute or orchestrate project
workflows.

Where a project already has native workflow capabilities, those stay in charge.
Examples include FreshForge package commands, project-specific CLIs, Snakemake
pipelines, notebooks, CI jobs, and release tooling. Agent Workbench should wrap
their outputs in artifact records only when that helps supervision,
verification, or token/cash accounting.

This boundary is intentional. Agent Workbench should not become a parallel
workflow engine unless a future phase proves that existing project-native tools
cannot provide the required execution surface.

## CLI Surface

Validate one workflow step:

```powershell
agent-workbench workflow validate --input <workflow-step.json>
```

Render one workflow step:

```powershell
agent-workbench workflow render `
  --input <workflow-step.json> `
  --output <workflow-step.md>
```

## Example Records

Public-safe examples live under `templates/workflow_examples/`:

- software task review;
- documentation proposal;
- paper outline; and
- benchmark proposal.

These examples show how Agent Workbench can represent software, research, and
benchmark work without becoming a replacement for Git, CI, notebooks,
Snakemake, FreshForge, project CLIs, or human review.

## Closeout Evidence

P37 adds:

- `src/agent_workbench/workflow.py`;
- `agent-workbench workflow validate|render`;
- `templates/workflow_step_record.json`;
- `templates/workflow_examples/*.json`; and
- this planning note.

This gives P38 a stable surface for separating roles, capabilities, and
implementations.
