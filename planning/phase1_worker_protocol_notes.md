# Phase 1 Worker Protocol Notes

## Purpose

Phase 1 turns the Phase 0 governance contract into reusable Markdown templates
for supervised worker-agent execution. The goal is to make worker tasks narrow,
evidence-driven, and easy for a supervisor to verify without trusting prose
summaries.

## Accepted Direction

- Keep templates in Markdown for now.
- Do not introduce YAML schemas, a CLI, CI, or validation tooling in this phase.
- Use Agent Workbench itself as the dogfood target.
- Defer `code chat --mode agent` launch mechanics to Phase 2.
- Defer model comparison and scoring to Phase 3.

## Template Set

- `templates/supervisor_ticket.md`: supervisor-authored worker task contract.
- `templates/worker_result.md`: worker-authored evidence report.
- `templates/acceptance_checklist.md`: supervisor verification checklist.
- `templates/failure_report.md`: exact-error blocker report.

## Manual Dogfood Dry Run

The Phase 1 dry run used the templates as a documentation-only self-workflow:

1. The supervisor-ticket shape was checked against the P1 task itself: it can
   describe current repo state, allowed files, forbidden scope expansion,
   success criteria, stop conditions, and final response requirements.
2. The worker-result shape was checked against the expected P1 closeout record:
   it has fields for commands run, files changed, checks run, GitHub URLs,
   blockers, and final status.
3. The acceptance checklist was checked against the P1 verification plan:
   independent `git`, file, GitHub, Markdown, and public-safety checks are all
   represented.
4. The failure report was checked against known worker failure patterns:
   tool-access confusion and "would have" summaries have explicit exact-error
   and stop-state slots.

## Findings

- The templates are intentionally repetitive; that is useful for weaker worker
  agents that need hard boundaries and explicit evidence slots.
- Markdown is sufficient for the next phase because humans and VS Code chat
  agents can read and copy it directly.
- A structured schema may become useful later, but adding one before real bridge
  trials would freeze the format too early.
- The next phase should document a file-based `code chat --mode agent` bridge
  without trying to parse Copilot responses automatically.
