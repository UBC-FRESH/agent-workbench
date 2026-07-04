# Phase 43 Graph-Backed Pilot Workflow

## Purpose

P43 proves that a real Agent Workbench deployment pilot can be represented as a
FreshForge-compatible graph without turning Agent Workbench into the executor.

The pilot pattern is based on the earlier FreshForge proposal-assist deployment
work: supervisor task selection, worker evidence intake, worker proposal,
project-native verification, and supervisor promotion.

## Implemented Surface

P43 adds:

- `templates/workbench_templates/freshforge_proposal_assist_graph.json`;
- `agent-workbench graph render --input <graph> --output <markdown>`;
- graph render coverage in the command-surface smoke check; and
- roadmap/changelog synchronization for P43.

## Graph Nodes

The pilot graph contains five nodes:

1. `select_freshforge_task`: supervisor-owned pilot task selection.
2. `worker_evidence_intake`: L1 proposal-only worker evidence summary.
3. `worker_cli_proposal`: L1 proposal-only worker CLI/API improvement proposal.
4. `project_native_verification`: supervisor-owned FreshForge/project-native
   verification.
5. `supervisor_promotion`: supervisor-owned promotion, revision, rejection, or
   deferral decision.

Each node includes Agent Workbench metadata in `parameters.agent_workbench` and
role/capability/authority metadata in `provenance`.

## Evidence And Accounting Links

P43 deliberately uses placeholder ignored-runtime paths such as
`runtime/agent_workbench/<pilot>/...` instead of real private project outputs.
Those references show how graph nodes connect to evidence summaries, token/cost
records, verification reports, and decision packets without tracking raw
worker output.

## Boundary

The graph is descriptive and auditable. It does not execute workers, run
FreshForge, mutate target projects, create issues, or make promotion decisions.

P44 can use this graph as the input shape for node-aware delegation decisions.
