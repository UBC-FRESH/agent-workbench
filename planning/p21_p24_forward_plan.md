# P21-P24 Forward Plan

The next tranche starts the local package/CLI path selected in ADR 0002. It
should keep implementation narrow and supervisor-owned.

## P21 Minimal Local Package And CLI Skeleton

Goal: add the smallest Python package and local CLI entrypoint needed to wrap
existing supervisor-side scripts.

Scope:

- package metadata;
- importable package namespace;
- CLI help surface;
- no model calls by default; and
- no change to worker trust levels.

Out of scope:

- VS Code extension;
- MCP server;
- hosted agent;
- dashboard;
- CI release pipeline; and
- delegated tracked-file or GitHub mutation.

## P22 CLI Wrappers For Existing Commands

Goal: wrap command-surface smoke checks and SDK same-ticket evaluation through
the new CLI while preserving existing scripts for compatibility.

Scope:

- smoke-check command;
- same-ticket evaluation command;
- redacted dry-run output; and
- compatibility notes for direct script usage.

## P23 Evidence Summary Validation And Rendering

Goal: make the P17 evidence summary contract executable enough for local
supervisor review.

Scope:

- validate required evidence-summary fields;
- render a Markdown summary from JSON-like input; and
- reject private-looking absolute paths or provider values when detectable.

## P24 CLI Dogfood Workflow

Goal: dogfood the new CLI on one no-tool evaluation workflow from ticket through
sanitized summary.

Scope:

- use an ignored runtime manifest;
- run a small local dry run or provider-backed trial if configured inputs exist;
- render a sanitized summary; and
- record whether direct scripts can remain as implementation details.
