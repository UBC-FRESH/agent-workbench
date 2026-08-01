# P118 — Single-Model Operator Checklist

Use this checklist to launch a single-model session. Fan out 2-4 parallel children for independent work; keep coupled or mutating work serial.

1. **Confirm custom-agent selection:** verify the active session uses the
   `agent-workbench-coordinator` profile with the current local serving alias
   (`ornith-1.0-35b-fp8`, passed as
   `Ornith 1.0 35B FP8 (copilotcustommodelsendpoint)`). Check the Model Identity
   table in `.github/agents/agent-workbench-coordinator.agent.md` — that table,
   not this checklist, is the source of truth for aliases.
2. **Confirm concurrency mode:** 2-4 parallel agents for independent work, serial for coupled/mutating work. Burst to 6 for read-only/diagnostic.
3. **Prepare the ticket:** write a bounded ticket to
   `runtime/agent_jobs/<task>_ticket.md` with explicit allowed files, commands,
   and result paths.
4. **Delegate:** launch the appropriate worker subagent (e.g.,
   `agent-workbench-local-supervisor` or a strict worker) with the ticket. For independent work, fan out 2-4 parallel agents. For coupled work, keep serial.
5. **Inspect:** read the worker's compact evidence (result file, diff summary,
   validator output) — not raw transcripts or large files.
6. **Verify:** independently validate the artifact (run checks, inspect diff).
   Do not trust the worker's prose claim.
7. **Decide:** accept, issue one bounded repair follow-up, or escalate to the
   developer. Do not try a third attempt.

**Advisor use:** invoke the advisor when asking for advice adds value — hard
reasoning, not routine acceptance review or mechanical checks. There is **no
cap** on invocation count and **no mandatory trigger** that forces one; it is a
judgment call. The advisor runs on `Claude Opus 5 (copilot)` and reads
`planning/advisor_dossier.md` for continuity; append its returned entry
afterwards, including when you reject its advice.