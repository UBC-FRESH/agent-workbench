# P118 — Single-Model Operator Checklist

Use this checklist to launch a single-model session. Fan out 2-4 parallel children for independent work; keep coupled or mutating work serial.

1. **Confirm custom-agent selection:** verify the active session uses the
   `agent-workbench-coordinator` profile with `Fresh vLLM Agent (Qwen 3.6 27B)`.
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

**Advisor use:** invoke the advisor only for a concrete ambiguity, not for
routine acceptance review or mechanical checks.