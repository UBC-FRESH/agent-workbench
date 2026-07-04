# Supervisor Ticket Template

Use this template when assigning a bounded task to a worker agent. The ticket
should leave no workflow decisions for the worker.

## Current Known State

- Repository:
- Branch:
- Relevant issue or PR:
- Relevant files:
- Verified facts:

## Task Boundary

Do exactly this:

1.
2.
3.

Do not do:

- unrelated refactors;
- extra issue or PR actions;
- file edits outside the listed paths;
- broad follow-up work; or
- substitute summaries for commands.

## Allowed Files And Commands

Allowed files:

- 

Allowed commands:

```text

```

Commands that require stopping first:

- 

## Success Criteria

The task is successful only when:

- 

## Stop Conditions

Stop immediately and report exact evidence if:

- any command fails;
- a required file or issue is missing;
- repo state differs from the current known state;
- the task would require editing files outside scope; or
- the worker cannot provide concrete command or artifact evidence.

## Required Final Response

Reply only with:

- commands run;
- files changed;
- checks run;
- GitHub URLs touched;
- final status: `accepted-candidate`, `blocked`, or `needs-supervisor-review`;
- exact error text if blocked.

Do not say "would have", "ready", "should be", or "complete" unless the
relevant command actually succeeded and evidence is listed.
