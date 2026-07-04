# ADR 0002: Interface Direction After P15-P20

Status: accepted

Date: 2026-07-04

## Context

ADR 0001 kept Agent Workbench as Markdown protocols plus local scripts for the
P15-P20 tranche. That tranche produced new evidence:

- P15 broadened SDK/Ollama model-family trials beyond the qwen pair.
- P16 added a smoke checker for direct script command surfaces.
- P17 defined a raw-evidence and sanitized-summary boundary.
- P18 showed a richer ignored-runtime VS Code Chat tool trial can be verified.
- P19 defined trust levels and nondelegable supervisor actions.

The direct-script surface now has enough repeated use to justify a narrow
interface wrapper, but not enough maturity to justify a VS Code extension, MCP
server, hosted agent, or broad public benchmark system.

## Decision

Start a narrow local Python package and CLI spike in the next tranche. The first
slice should wrap existing supervisor-side commands only:

- command-surface smoke checks;
- SDK same-ticket evaluation;
- evidence-summary validation or rendering; and
- supervisor-side sandbox patch application.

The package must not expand worker authority. It should preserve the P19 trust
levels and continue treating tracked-file mutation, GitHub mutation, issue
closure, PR merge, release, and phase closeout as supervisor-only.

Do not start a VS Code extension, MCP server, hosted agent, or dashboard until
the local CLI shape proves useful.

## Consequences

Positive:

- Local commands become easier to discover and compose.
- Future phases can test command contracts through one entrypoint.
- Packaging work has a narrow boundary and does not force UI/runtime decisions.

Costs:

- The repository will need package metadata and basic command tests.
- Some script paths may need migration or wrapper compatibility.
- Governance must keep the package from implying production readiness.

## Rejected Options

- Keep scripts only forever: too much repeated command friction after P16-P19.
- Build a VS Code extension next: premature while chat-session control and
  response capture remain unstable.
- Build MCP next: premature because tool authority policy is still conservative.
- Build a hosted agent next: not needed for local Ollama/GPU worker experiments.
- Build a dashboard next: premature before evidence summaries are validated.
