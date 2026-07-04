# Phase 0 Governance Notes

## Purpose

Agent Workbench is starting as a governance-only sandbox. The immediate need is
not a package, extension, benchmark harness, or model registry. The immediate
need is a clean public repository where UBC-FRESH can develop and test reliable
supervisor/worker agent workflows without contaminating modelling project repos
with raw prompt experiments and local agent transcripts.

## Accepted Phase 0 Direction

- Use the UBC-FRESH phase/task/subtask workflow from the beginning.
- Treat one phase as one parent issue and one feature branch.
- Treat each roadmap task as one child issue.
- Keep implementation subtasks as checklist items in child issue bodies unless a
  later phase needs deeper issue hierarchy.
- Require command and artifact evidence before accepting worker-agent claims.
- Use ignored local files for raw tickets, worker results, runtime notes, and
  transcripts.
- Promote only sanitized, durable findings into tracked planning notes.

## Deferred Work

Phase 0 deliberately does not add:

- Python package code;
- command-line interfaces;
- Sphinx documentation;
- CI workflows;
- model benchmark infrastructure;
- VS Code extensions;
- MCP servers; or
- persistent worker-agent orchestration services.

Those surfaces should be introduced only after the repository has enough
governance structure to evaluate them safely.

## Public-Safety Boundary

Raw conversations with agent tools often include project-specific paths,
unreviewed claims, private planning context, and noisy model output. Those files
belong under ignored paths such as `tmp/` and `runtime/`.

Tracked files should describe reusable workflow patterns, not private project
content or unfiltered transcripts.
