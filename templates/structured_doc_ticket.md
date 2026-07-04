# Structured Documentation Output Ticket Template

Use this template for no-tool worker trials where the worker must return a
small, parseable Markdown work product in the assistant response.

## Worker Instructions

You are executing an Agent Workbench structured-output probe.

Do not use tools.
Do not run commands.
Do not edit files.
Do not describe what you would do.

Return only the required Markdown sections below, in the exact order shown.
Do not add a preamble, apology, signoff, or extra section.

## Required Output Shape

```markdown
## Summary

One sentence that restates the bounded task.

## Observations

- First concise observation.
- Second concise observation.

## Decision

accepted-candidate
```

## Stop Conditions

If you cannot comply, return:

```markdown
## Summary

blocked

## Observations

- Exact blocker text.

## Decision

blocked
```
