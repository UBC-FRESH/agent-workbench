# Failure Report Template

Use this template when a worker-agent task cannot be completed as assigned.

## Failed Task

- Ticket:
- Repository:
- Branch:
- Intended final state:

## Stop Condition Triggered

- [ ] Command failed.
- [ ] Required file or issue missing.
- [ ] Repo state differed from ticket.
- [ ] Scope required out-of-bound file edits or commands.
- [ ] Tool access could not be proven.
- [ ] Other:

## Exact Failed Command

```text

```

## Exact Error Text

```text

```

## State At Stop

```text

```

## Safe Next Step

- 

Do not convert this failure into a success summary. If the assigned command did
not run successfully, the work is blocked or needs a new bounded ticket.
