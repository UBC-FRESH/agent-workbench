# ADR 0001: Keep Agent Workbench As Markdown Plus Local Scripts

## Status

Accepted

## Context

Agent Workbench now has evidence from exact marker probes, structured output,
patch proposals, supervisor-applied sandbox patches, restricted tool-enabled
VS Code Chat mutation, and supervisor-owned GitHub workflow microtasks.

The scripts and templates are useful, but their command surfaces are still
changing as the workflow matures.

## Decision

Keep Agent Workbench as tracked Markdown protocols plus local scripts for the
next tranche. Do not yet convert the repository into a Python package, VS Code
extension, MCP server, or hosted service.

## Consequences

- The project remains easy to inspect and change.
- Raw evidence can continue to live under ignored runtime paths.
- Packaging work is deferred until the stable command surface is clearer.
- Future phases can focus on broader model comparisons before interface
  investment.

