# Patch Proposal Ticket Template

Use this template when a worker should propose a bounded patch but must not
apply it.

## Worker Instructions

You are executing an Agent Workbench patch-proposal probe.

Do not use tools.
Do not run commands.
Do not edit files.
Do not claim that the patch has been applied.

Return only the required Markdown sections below, in the exact order shown.
Do not add a preamble, signoff, or extra section.

## Required Output Shape

~~~markdown
## Rationale

One short paragraph explaining the proposed change.

## Patch

```diff
--- a/path/to/file.md
+++ b/path/to/file.md
@@
-old text
+new text
```

## Verification

- Supervisor must review and apply this patch separately.
~~~

## Acceptance Rules

- The patch must touch only the allowed file or files named in the ticket.
- The patch must be syntactically recognizable as a unified diff proposal.
- The worker must not state that files were edited.
- The worker must not include unrelated changes.
