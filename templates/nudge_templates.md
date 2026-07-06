# Delegated-Run Nudge Templates

Use these messages only after inspecting the heartbeat summary and relevant
filesystem or Git state. Every nudge should be archived with timestamp and
triggering evidence.

## Continue Next Subtask

Continue with the next unchecked checklist item in the current child task.
Append a heartbeat record before and after the next material action. Do not
summarize completion unless the result file is written.

## Stop Summarizing

Stop repeating completion summaries. Inspect the ticket checklist, run the next
required command, or write the blocker file with exact evidence.

## Write Blocker

Write the blocker file now with the exact failed command, error text, and
missing evidence. Do not replace the blocker with a prose summary.

## Fix Shell Context

Confirm the workspace root and shell context before running more commands. If
the context cannot be verified, write the blocker file.

## Reconcile Checklist

Reconcile the child-task checklist against files, commands, and checks. Then
write the result file with concrete evidence for each completed item.

## Stop Rule

After two failed or stale nudges in the same delegated lane, stop the lane and
require coordinator review of the ticket, heartbeat, result, blocker, archive,
and token/cash ledger.
