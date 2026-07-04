# Phase 23 Evidence Validation And Rendering Notes

Phase 23 makes the P17 evidence summary contract executable through the package
CLI.

## Commands Added

```text
agent-workbench evidence validate --input <summary.json>
agent-workbench evidence render --input <summary.json> --output <summary.md>
```

The commands are package-native and do not call the older direct scripts.

## Validation Behavior

Validation checks:

- required top-level evidence summary fields;
- `source_runtime_paths` as repo-relative strings;
- `outcomes` as a list; and
- obvious private-looking values such as personal home paths, GitHub-style
  tokens, credential key/value strings, and access-header names.

The validator is deliberately lightweight. It is not a full JSON Schema engine
and does not guarantee that every possible private value will be detected.

## Rendering Behavior

Rendering validates the input first, then writes a Markdown evidence summary
with metadata, scope, source runtime paths, outcomes, verification, promotion
boundary, and supervisor decision sections.

## Decision

The package now has useful functionality beyond script wrapping. P24 should
dogfood `agent-workbench smoke`, `agent-workbench eval --dry-run`,
`agent-workbench evidence validate`, and `agent-workbench evidence render` in one
local no-tool workflow.
