# Restricted Tool-Enabled Worker Ticket Template

Use this template only for tightly bounded tool-enabled worker trials.

## Marker

`P12_EXAMPLE_MARKER`

## Task

Optionally read the explicitly listed ignored runtime input files. Create or
update exactly one ignored runtime output file with exactly the requested
content, then stop.

## Required Reads

- `runtime/agent_jobs/<task>_input.md`

## Allowed Files

- `runtime/agent_jobs/<task>_result.md`

## Forbidden Actions

- Do not edit tracked files.
- Do not edit files outside the allowed list.
- Do not read files outside the required-read list unless the ticket explicitly
  permits them.
- Do not run terminal commands unless the ticket explicitly lists them under
  `Required Commands`.
- Do not perform GitHub actions.
- Do not continue after writing the requested result.

## Required Commands

No terminal commands are required.

## Required Result

The allowed result file must contain only the exact requested text.

## Final Response

Reply with:

```text
P12_EXAMPLE_MARKER done
```

