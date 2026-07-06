# Task Delegation Ticket

## Task Identity

- Run id:
- Phase:
- Parent issue:
- Child task issue:
- Branch:
- Target repository:
- Workspace root:
- Coordinator:
- Delegated supervisor or worker:
- Expected model:
- Expected permission mode:

## Current State

Summarize only the state needed to execute this child task. Include the current
branch, relevant issue or PR state, and known artifacts. Do not include raw
private transcripts, provider endpoints, credentials, or machine-specific paths.

## Task Boundary

The delegated agent owns exactly this child task:

-

Out of scope:

-

The delegated agent must stop when this task is complete, blocked, or outside
scope. It must not continue to sibling tasks, parent-phase closeout, PR merge,
or issue closure unless those actions are explicitly listed below.

## Shell And Runtime Context

- Shell:
- Operating system:
- Python or package environment:
- Required environment variables:
- Commands must be run from:

If the delegated agent cannot confirm the shell or root, it must write a blocker
instead of improvising.

## Allowed Files And Paths

The delegated agent may read:

-

The delegated agent may edit or create:

-

The delegated agent must not touch:

-

## Allowed Commands

The delegated agent may run:

```text

```

The delegated agent must not run:

```text

```

## Required Evidence Paths

- Result file:
- Blocker file:
- Heartbeat file:
- Copilot archive output directory:
- Token ledger or cost record:

The delegated agent must write the result or blocker file before stopping.
For Copilot-backed runs, the coordinator must archive the chat session before
accepting the result.

## Heartbeat Requirements

Append one JSONL heartbeat record after each material action or every bounded
work interval. Each record must include:

- `timestamp`;
- `checklist_item`;
- `status`;
- `action`;
- `artifact_path`;
- `command_summary`; and
- `next_intended_action`.

## Success Criteria

The task is successful only when:

-

Prose summaries do not substitute for command execution, file evidence, issue
state, or artifact inspection.

## Stop Conditions

Stop and write the blocker file when:

-

## Final Response Contract

The final response must contain only:

- final status: `accepted-candidate`, `blocked`, or `needs-supervisor-review`;
- result file path or blocker file path;
- heartbeat file path;
- archive path if applicable; and
- exact blocker or error text if any.
