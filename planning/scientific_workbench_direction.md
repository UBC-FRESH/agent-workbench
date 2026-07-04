# Scientific Workbench Direction

This note promotes a strategic idea from local external-chat discussion into
public-safe Agent Workbench planning. The raw conversation remains local working
material. This note is the durable planning surface.

## Strategic Claim

Agent Workbench should avoid becoming another general-purpose agent framework.
The stronger direction is a reproducible workbench for supervised AI-assisted
scientific and software development.

The near-term product should still be practical and narrow:

```text
reduce paid supervisor token spend per useful merged unit of work
```

The longer-term product can be broader:

```text
make research and development workflows reproducible, attributable, auditable,
and executable across humans, local workers, paid agents, scripts, and existing
workflow tools
```

## What Not To Build

Do not optimize toward "LangChain but different."

Agent Workbench should not compete directly as a general agent runtime,
orchestration graph, model router, MCP server, VS Code extension, notebook
system, CI engine, or workflow engine before there is evidence that the core
delegation loop creates net value.

When mature external tools are good enough, Agent Workbench should wrap or
interoperate with them rather than replacing them.

## Workbench-First Framing

The important object is not the agent. The important object is the supervised
work unit and its evidence trail:

- task bundle;
- source artifacts;
- worker role;
- capability required;
- concrete implementation used;
- output artifact;
- claim review;
- verification evidence;
- token/cash accounting; and
- supervisor promotion decision.

Agents are one implementation class. Humans, scripts, package commands, CI jobs,
notebooks, and workflow engines are also possible implementations.

## Role, Capability, Implementation

A future workbench layer should separate three concepts:

| Layer | Meaning | Examples |
| --- | --- | --- |
| Role | Persistent project responsibility. | Reviewer, programmer, analyst, documentation editor. |
| Capability | Bounded action the role can perform. | Summarize evidence, propose tests, review claims, draft patch. |
| Implementation | Tool or actor used for the capability. | Local qwen worker, `gpt-oss:*`, paid supervisor model, Python script, human. |

This matters because workflows should not depend on a specific model. If a
workflow says "review evidence," the implementation can change as model
profiles and economics change.

## Artifact-First Direction

Conversations and prompts should not be the durable center of the system.
Artifacts should be:

- issue bodies;
- roadmap tasks;
- worker tickets;
- evidence summaries;
- decision packets;
- model profiles;
- token/cost records;
- generated reports;
- code/docs/tests; and
- release or publication outputs.

Every promoted artifact should have a source, a transformation, a verifier, and
a supervisor decision.

## Relationship To Current Roadmap

This direction supports, rather than replaces, the current roadmap.

P35 and P36 should remain focused on empirical delegation economics:

- choose real project task bundles;
- estimate direct paid-supervisor token/cash cost;
- run proposal-assist workers where appropriate;
- record delegated supervisor token/cash cost;
- record accepted/rejected claims and cleanup;
- compare against the direct-work counterfactual; and
- tune policy from observed outcomes.

Only after this loop produces useful evidence should Agent Workbench expand
toward broader workbench abstractions.

## Proposed P37+ Direction

After P35/P36, the next tranche should add planning and small implementation
surfaces for:

- artifact/workflow contracts;
- role/capability/implementation records;
- reusable workbench templates for software, papers, proposals, and benchmark
  tasks; and
- optional observability ingestion for token/cash accounting.

This keeps the long-term scientific-workbench vision visible without letting it
swallow the immediate empirical work.

## Messaging

Near-term description:

> Agent Workbench is a local supervisor tool for reproducible,
> token-accounted, AI-assisted development workflows.

Longer-term description:

> Agent Workbench is a reproducible workbench for supervised AI-assisted
> scientific and software development.

Avoid:

> Agent Workbench is a framework for building agents.
