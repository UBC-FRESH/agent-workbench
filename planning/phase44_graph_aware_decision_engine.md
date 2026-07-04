# Phase 44 Graph-Aware Delegation Decision Engine

## Purpose

P44 upgrades delegation recommendations from isolated task descriptions to
graph-node recommendations. The command reads a FreshForge-compatible graph,
validates Agent Workbench metadata, derives conservative decision inputs per
node, and renders a supervisor-readable recommendation report.

## Command

```powershell
python -m agent_workbench graph decide --input templates/workbench_templates/freshforge_proposal_assist_graph.json --output runtime/graph_decisions/p44_freshforge_proposal_assist.md --agent-metadata
```

The command does not execute graph nodes or contact worker models.

## Decision Mapping

P44 maps graph metadata to the existing rules-based task decision engine:

- `provenance.capability` becomes the task type.
- `provenance.authority_level` becomes the authority boundary.
- `parameters.agent_workbench.node_kind` helps distinguish worker proposal
  nodes from supervisor-owned nodes.
- `needs` are rendered as graph context in the report.
- worker proposal nodes receive conservative positive token/cash assumptions so
  the report can identify plausible delegation candidates.
- supervisor-owned nodes are forced into the direct supervisor lane through
  nondelegable flags.

## Boundary

This is a decision aid, not an executor. The supervisor still chooses whether
to launch workers, apply patches, run project-native verification, create
issues, or close phases.

P45 can build on this by replacing placeholder node economics with real
per-node token/cost records.

## Dogfood Result

Running the command on `freshforge_proposal_assist_graph.json` produced the
expected split:

- `select_freshforge_task`: `do-directly`;
- `worker_evidence_intake`: `delegate`;
- `worker_cli_proposal`: `delegate`;
- `project_native_verification`: `do-directly`; and
- `supervisor_promotion`: `do-directly`.

The useful behavior is that graph-node metadata lets the decision report
identify the worker proposal nodes as plausible delegation candidates while
keeping selection, verification, and promotion in the supervisor lane.
