# Phase 38 Role, Capability, And Implementation Model

Phase 38 separates persistent project responsibilities from bounded actions and
the tools or actors that perform those actions.

## Core Separation

The contract has three layers:

- Role: a persistent responsibility in the project workflow.
- Capability: a bounded action the role may perform.
- Implementation: the human, local worker, paid agent, script, or workflow tool
  used for that capability.

This separation prevents model names from becoming workflow design. A workflow
can ask for `claim-review`; the implementation can be a local qwen worker, a
paid supervisor model, a deterministic script, or a human reviewer depending on
policy and evidence.

## Record Shape

`templates/role_capability_implementation.json` records:

- role id, type, scope, responsibility, and allowed artifacts;
- capability id, description, task types, inputs, outputs, and maximum authority
  level;
- implementation candidates with type, name, authority level, optional model
  profile path, and fit notes; and
- selection policy explaining when implementations may be swapped.

## CLI Surface

Validate a record:

```powershell
agent-workbench roles validate --input <role-record.json>
```

Render a record:

```powershell
agent-workbench roles render `
  --input <role-record.json> `
  --output <role-record.md>
```

## Examples

Public-safe examples live under `templates/role_examples/`:

- programmer patch proposal;
- analyst token accounting; and
- editor documentation proposal.

Together with the canonical reviewer template, these cover reviewer,
programmer, analyst, and editor roles.

## Authority Boundary

Capabilities carry a maximum authority level. Implementations must not exceed
that level unless they are explicitly supervisor-owned.

Model swaps are allowed only when:

- the role stays the same;
- the capability stays the same;
- the implementation authority ceiling is compatible; and
- model profile, decision report, accounting record, or policy tuning evidence
  supports the substitution.

## Closeout Evidence

P38 adds:

- `src/agent_workbench/roles.py`;
- `agent-workbench roles validate|render`;
- `templates/role_capability_implementation.json`;
- `templates/role_examples/*.json`; and
- this planning note.

This prepares P39 to build reusable workbench templates around roles and
artifacts instead of hard-coded model assumptions.
