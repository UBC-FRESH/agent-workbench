# Phase 39 Reusable Scientific Workbench Templates

Phase 39 adds reusable template envelopes for common UBC-FRESH software and
research tasks. These templates are planning artifacts, not workflow runners.

## Template Families

Templates live under `templates/workbench_templates/`:

- `software_task_template.md`;
- `paper_task_template.md`;
- `proposal_task_template.md`; and
- `benchmark_task_template.md`.

Each template starts from the same pattern:

```text
workflow id
nodes
needs
providers and implementations
inputs and outputs
artifacts
diagnostics
project-native execution boundary
claim review
token/cash accounting
promotion gate
```

This deliberately reuses FreshForge's graph vocabulary without importing
FreshForge's execution semantics into Agent Workbench.

## Artifact Layout

The templates show how the main Agent Workbench record families fit together:

- worker tickets remain ignored local inputs;
- generated worker outputs remain ignored until reviewed;
- evidence summaries capture sanitized findings;
- workflow records describe artifact transformations;
- role records describe who or what can perform a capability;
- accounting records capture token/cash economics; and
- promoted outputs are supervisor-owned tracked files, issue comments, PRs, or
  reports.

## Integration Boundary

Agent Workbench does not replace FreshForge, Snakemake, notebooks, GitHub
Actions, Quarto, project CLIs, or release tooling.

The template should point to project-native commands when execution is needed.
For a FreshForge-style project, that means the target project still owns build,
test, docs, distribution, and report semantics. Agent Workbench records the
delegation context, evidence, verification, and economics around those commands.

## Closeout Evidence

P39 adds:

- `templates/workbench_templates/agentic_graph_envelope.json`;
- four reusable Markdown template envelopes;
- `templates/workbench_templates/README.md`;
- this planning note; and
- roadmap/changelog updates.

P40 can now add observability/token-cost ingestion without changing the
non-orchestration boundary.
