File-Based Handoff Protocol
===========================

Agent Workbench uses ignored local files for raw coordination between agents:

- Worker ticket path: `runtime/agent_jobs/<phase_or_task>_ticket.md`
- Worker result path: `runtime/agent_jobs/<phase_or_task>_result.md`
- Raw transcript path: `tmp/transcripts/<date>_<short-topic>.md`

Worker tickets include current state, governing issues, exact task boundary, files in scope, allowed commands, success criteria, failure stop conditions, and required evidence format.

Worker result files must include commands run, files changed, tests/checks run, GitHub URLs touched, blockers/errors, and final status: `accepted-candidate`, `blocked`, or `needs-supervisor-review`.

For complete protocol details see `AGENTS.md` in the repository root.
