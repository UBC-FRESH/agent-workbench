# Delegated Repair Ticket

## Repair Identity

- Repair run id:
- Previous run id:
- Phase:
- Child issue:
- Coordinator decision packet:
- Previous result file:
- Previous archive manifest:

## Defects To Repair

List exact defects from the coordinator decision packet. Do not add new scope.

| Defect id | Severity | Evidence path | Required repair |
| --- | --- | --- | --- |
|  |  |  |  |

## Allowed Repair Surface

The delegated agent may change only:

-

The delegated agent may run only:

```text

```

## Forbidden Actions

- Do not redo the whole task unless explicitly instructed.
- Do not expand to sibling child tasks.
- Do not close GitHub issues, merge PRs, or claim parent-phase completion.
- Do not replace missing command evidence with prose.

## Required Output

- Updated artifact path:
- Repair result file:
- Heartbeat file:
- Blocker file:

## Acceptance Criteria

The repair is acceptable only if every listed defect is resolved or explicitly
reported as blocked with exact error text and evidence.
