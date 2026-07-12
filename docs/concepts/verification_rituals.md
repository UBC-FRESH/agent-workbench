Verification Rituals
==================

Agent Workbench requires evidence-based verification before any completion claim:

- Command output must show exact commands run and their exit codes
- File changes must be verifiable via `git status --short` or file inspection
- Test results must show pass/fail counts
- GitHub operations must cite issue/PR numbers and URLs

A worker agent's prose report is treated as untrusted until the supervisor verifies the underlying repo, GitHub, or filesystem state. If a worker cannot prove a command ran or a file changed, that is recorded as a blocker rather than smoothed into success.

For full verification requirements see `AGENTS.md` in the repository root.
