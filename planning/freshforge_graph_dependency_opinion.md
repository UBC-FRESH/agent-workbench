# FreshForge Graph Dependency Opinion

## Question

Should Agent Workbench literally import FreshForge as a dependency and use
FreshForge workflow graph-definition functions to define agentic role workflow
structure?

## Short Opinion

Yes, probably. But the dependency should be used for graph records,
validation, provider references, diagnostics, and planning semantics, not for
making Agent Workbench a competing workflow execution engine.

The best direction is:

```text
Agent Workbench agent semantics
  on top of
FreshForge graph records and validation
  around
project-native execution tools
```

The bad direction is:

```text
Agent Workbench grows a parallel workflow orchestration framework
```

The distinction matters.

## Why FreshForge Fits

FreshForge already has the core graph vocabulary Agent Workbench needs:

- `WorkflowSpec`;
- `WorkflowNode`;
- node ids;
- provider references;
- `needs` dependencies;
- `inputs`;
- `outputs`;
- `parameters`;
- `artifacts`;
- `provenance`;
- diagnostics;
- validation of duplicate nodes, missing dependencies, invalid structure, and
  dependency cycles;
- provider metadata;
- provider/node-type validation; and
- non-executing planning surfaces.

That is almost exactly the structural layer Agent Workbench needs for role
workflows. An agentic workflow graph can be represented as:

| FreshForge Field | Agent Workbench Meaning |
| --- | --- |
| `workflow.id` | supervised workbench task bundle |
| `nodes[].id` | bounded role/capability step |
| `nodes[].provider` | implementation namespace, such as `agent.qwen`, `supervisor.review`, `freshforge.run`, or `project.cli` |
| `nodes[].needs` | evidence or dependency order |
| `nodes[].inputs` | source artifacts, worker tickets, context packets |
| `nodes[].outputs` | generated proposal, evidence summary, decision packet |
| `nodes[].artifacts` | source/generated/promoted/rejected artifacts |
| `nodes[].provenance` | model, role, capability, authority, cost, verification metadata |
| diagnostics | claim-review, validation, boundary, and policy warnings |

Using FreshForge here avoids inventing a second graph grammar with slightly
different semantics.

## Why A Literal Dependency May Be Good

A literal dependency would give Agent Workbench several benefits:

- one graph vocabulary across UBC-FRESH workflow projects;
- less duplicate validation code;
- inherited cycle detection and dependency checking;
- alignment with existing FreshForge provider concepts;
- easier future interoperability with FreshForge run summaries and evidence;
- clearer story for CLEWS/FreshForge/FEMIC-style projects; and
- less risk that Agent Workbench invents its own incompatible graph dialect.

This is especially attractive because the P39 graph envelope is already
FreshForge-shaped. If Agent Workbench keeps hand-rolling that shape, drift is
likely.

## Why It Could Be A Bad Move

The main risk is coupling Agent Workbench too tightly to FreshForge while both
packages are still alpha-stage and evolving.

Specific risks:

- FreshForge currently targets workflow-as-code for scientific/project
  execution, while Agent Workbench targets delegation/evidence/accounting.
- FreshForge may change its graph schema before it stabilizes.
- Agent Workbench may need agent-specific metadata that does not belong in
  FreshForge core.
- A hard dependency may make Agent Workbench harder to install in environments
  where the user only wants lightweight prompt/evidence/accounting tools.
- If we import FreshForge too broadly, developers may assume Agent Workbench now
  executes workflow graphs.
- Provider naming could get confusing unless we clearly separate FreshForge
  execution providers from Agent Workbench role/capability providers.

These are real concerns, but none of them argues against reusing the graph
model. They argue for doing it deliberately.

## Recommended Architecture

Use FreshForge for the structural graph layer:

- load graph documents;
- validate graph structure;
- validate node dependencies;
- validate provider-reference syntax;
- produce diagnostics;
- maybe produce non-executing plans.

Keep Agent Workbench responsible for agent-specific semantics:

- roles;
- capabilities;
- authority levels;
- model/profile references;
- worker tickets;
- evidence summaries;
- claim review;
- token/cash accounting;
- policy tuning;
- supervisor promotion decisions.

Do not use Agent Workbench to execute FreshForge workflows unless a later phase
explicitly chooses to call FreshForge as a project-native implementation node.

## Practical Shape

Agent Workbench could define an agentic graph as an ordinary FreshForge workflow
document with Agent Workbench metadata in node `parameters`, `artifacts`, and
`provenance`.

Example shape:

```yaml
workflow:
  id: p13_proposal_assist
  name: P13 proposal assist

nodes:
  - id: select_task
    provider: agent_workbench.supervisor_task_selection
    outputs:
      task_bundle: p13-evidence-intake
    provenance:
      role: supervisor
      capability: task_selection
      authority_level: supervisor-owned

  - id: worker_proposal
    provider: agent_workbench.local_worker_proposal
    needs: [select_task]
    inputs:
      task_bundle: ${nodes.select_task.outputs.task_bundle}
    artifacts:
      - runtime/agent_workbench/p13/worker_proposal.md
    provenance:
      role: analyst
      capability: evidence_intake
      implementation: qwen3-coder-next:latest
      authority_level: L1

  - id: project_verification
    provider: freshforge_or_project_cli.verify
    needs: [worker_proposal]
    provenance:
      role: programmer
      capability: project_native_verification
      implementation: FreshForge or project CLI
      authority_level: supervisor-owned

  - id: supervisor_promotion
    provider: agent_workbench.supervisor_promotion
    needs: [worker_proposal, project_verification]
    provenance:
      role: supervisor
      capability: promotion_decision
      authority_level: supervisor-owned
```

FreshForge validates the graph. Agent Workbench interprets the agent metadata.
Project-native tools execute project work.

## Dependency Strategy

I would not immediately make FreshForge a required dependency for every
Agent Workbench install without a compatibility check.

Recommended sequence:

1. Add a planning phase for `FreshForge graph integration spike`.
2. Add FreshForge as an optional dependency first, for example:

   ```toml
   [project.optional-dependencies]
   graph = ["freshforge>=0.1.0a5"]
   ```

3. Add `agent-workbench graph validate` that uses FreshForge when installed.
4. Convert `templates/workbench_templates/agentic_graph_envelope.json` into a
   FreshForge-valid workflow document.
5. Keep existing Agent Workbench role/workflow/token commands working without
   FreshForge.
6. If the spike proves clean, promote FreshForge to a required dependency in a
   later phase.

This avoids premature hard coupling while testing the real integration.

## What Would Make It A Bad Move

I would argue against a literal required dependency if any of these turn out to
be true:

- FreshForge cannot represent Agent Workbench node metadata cleanly without
  abusing fields.
- Agent Workbench needs graph semantics that contradict FreshForge validation.
- FreshForge schema churn creates too much overhead.
- FreshForge pulls in dependencies or runtime assumptions that make
  Agent Workbench less useful as a lightweight local supervisor tool.
- The integration causes users to think Agent Workbench owns execution rather
  than evidence/accounting around execution.

If those happen, Agent Workbench should still reuse the vocabulary
conceptually, but keep a small compatibility adapter instead of a hard
dependency.

## Current Recommendation

My current recommendation is:

```text
Add FreshForge as an optional graph dependency in the next tranche, then spike
using FreshForge validation for Agent Workbench agentic graph envelopes.
```

If the spike is clean, make FreshForge the canonical graph layer for Agent
Workbench. That would reduce architectural duplication and make the overall
UBC-FRESH toolchain more coherent.

Do not build another graph validator inside Agent Workbench unless the
FreshForge integration fails for concrete technical reasons.

## Immediate Next Phase Candidate

Potential next phase:

```text
P41: FreshForge graph integration spike
```

Possible tasks:

- Add optional FreshForge dependency.
- Convert `agentic_graph_envelope.json` to a FreshForge-valid workflow document.
- Add `agent-workbench graph validate` backed by FreshForge.
- Add an Agent Workbench metadata convention for roles, capabilities,
  authority, token accounting, and supervisor decision fields.
- Verify that graph validation catches duplicate nodes, missing dependencies,
  cycles, and malformed provider references.
- Document the execution boundary: FreshForge validates/plans graph structure;
  project-native tools execute project work; Agent Workbench records evidence,
  claims, policy, and token/cash economics.
