Governance Overview
==================

Agent Workbench is a public-safe sandbox for supervised multi-agent development workflows. It follows strict phase/task/subtask discipline with evidence-driven verification.

Key principles:

- **File-based handoffs**: All agent coordination uses ignored local files for raw data, promoted only to tracked files after supervisor verification.
- **Evidence requirements**: Every completion claim must be backed by verifiable evidence (command output, file diffs, issue URLs, or inspected artifacts).
- **Public-safe by default**: Raw transcripts, credentials, and private project notes stay in ignored paths unless sanitized into planning notes.
- **Verification over trust**: Prose reports from workers are untrusted until independently verified against repo state, GitHub state, or filesystem state.

Full governance rules are in `AGENTS.md` at the repository root. This documentation surface curates public-safe excerpts for external consumption.
