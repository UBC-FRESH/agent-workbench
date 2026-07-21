# Coordinator Advisor Paid-Boost Strategy

This note records the Agent Workbench strategy for the coordinator and advisor
lanes. P118 supersedes the earlier "paid boost" framing: all roles now share one
configured vLLM model, and the advisor is same-model advisory-only, not a paid
model invocation. The title is retained for historical reference.

## P118 Deployment (2026-07-21)

**Current arrangement (supersedes previous):**

- All agentic UI workflow for Agent Workbench runs in the built-in VS Code
  GitHub Copilot chat UI.
- Coordinator, supervisor, worker, and advisor roles all run the same configured
  remote vLLM model (`Fresh vLLM Agent (Qwen 3.6 27B)`).
- Role separation comes from bounded instructions, tool permissions, and session
  topology — not from different models.
- Paid high-capability intelligence has been replaced by the same-model advisory
  lane. The advisor is not paid; it is the same model with read-only constraints.
- GPU constraint: the model consumes near-maximum VRAM; no additional models
  should be loaded. Serial inference (one child at a time) is a hardware
  requirement.

**Previous arrangement (archived for reference):**

- Coordinator: paid GPT-5.x agent in a Codex chat interface.
- Supervisor and workers: free local Ollama models.
- Advisor: paid Claude Opus on demand.

Tradeoff being accepted:

- Pro: large paid-token cash savings, since the always-on coordinator lane
  becomes the same provider-side model. No paid API calls required.
- Con: all roles share the same model, so the coordinator is not inherently
  stronger or weaker than the supervisor — it is the same model. The advisor
  lane provides additional reasoning effort through isolation and read-only
  constraints, not through a different model.

Mitigation: the advisor lets the coordinator "buy" advisory reasoning where it
adds value, using the same model with bounded authority. The ROI ledger tracks
whether the advisor lane produces better judgments than the coordinator working
independently.

## Custom Agent Profiles

Multiple profiles implement the hierarchy in `.github/agents/`. All roles now
share one configured remote vLLM model (`Fresh vLLM Agent (Qwen 3.6 27B)`).
Role separation comes from bounded instructions and authority, not from
deploying different models (P118 update, 2026-07-21):

- `agent-workbench-coordinator.agent.md` — thin coordinator; owns process
  discipline, ticketing, verification, and serial inference enforcement.
- `agent-workbench-local-supervisor.agent.md` — supervisor; runs bounded job
  tickets and returns compact evidence with an explicit job-end signal.
- `agent-workbench-advisor.agent.md` — same-model, read-only, advisory-only
  node invoked by the coordinator for hard reasoning.
- `qwen3-coder-strict-worker.agent.md` — strict bounded worker.
- `qwen3-coder-next-strict-worker.agent.md` — strict bounded worker.
- `agent-workbench-result-auditor.agent.md` — internal read-only auditor.
- `document-metadata-extraction-supervisor.agent.md` — domain-specific supervisor
  for document metadata extraction pilots.

The Advisor reuses the existing subagent delegation plumbing (the coordinator
invokes it as a named subagent). The only difference is the skin: the Advisor's
tools are restricted to read-only and the instructions enforce advisory-only
output. All profiles use the same vLLM model alias.

## Advisor Delegation Candidates

High-value, hard-for-local, expensive-if-wrong question types:

- pre-closeout review of a coordinator report and its evidence before a roadmap
  phase is closed;
- roadmap critique recommending strategic, tactical, or operational shifts; and
- several-phases-ahead look-ahead roadmap extension, expansion, or pivot design.

Claude Opus 4.8 is conjectured (not yet verified) to be strong at large-context
big-picture work. This conjecture is adopted provisionally and should be
confirmed or refuted with empirical ROI records.

Poor candidates (coordinator does these itself): mechanical checks, ticket
templating, status polling, evidence existence checks, checklist reconciliation,
routine supervisor ticket preparation.

## Paid-Token Budget Model

The Advisor is a scarce "intelligence boost" budget, not a default reflex.

- The developer sets a paid budget per session, per phase, or per day.
- Default when unstated: at most one Advisor invocation per roadmap phase; ask
  the developer before exceeding it.
- The coordinator must never spend paid Advisor time on work it can verify
  mechanically.
- Prefer one well-scoped Advisor question with all evidence attached over
  several vague ones.
- When the budget is exhausted, the coordinator escalates the open question to
  the developer instead of the Advisor.

This aligns with the project's existing paid-supervisor cost discipline: define
the question, the budget, the stop condition, and the evidence artifact before
spending paid tokens.

## ROI-Gradient Learning Loop

Goal: over hours and days of work, the coordinator learns to follow the
paid-token benefit/cost ratio gradient — spending where paid help has repeatedly
paid off and avoiding where it has not.

Mechanism (transparent and rules-based, not ML):

1. Raw ledger (ignored, local):
   `runtime/advisor_jobs/advisor_roi_ledger.jsonl`. The coordinator reads it at
   session start and appends one public-safe JSON line per Advisor invocation.
2. Per-record fields: `date`, `phase_or_task`, `question_type`,
   `predicted_value`, `advisor_model`, `outcome` (did it change the decision or
   catch a real defect?), `net_judgment` (`worth_it` | `marginal` |
   `not_worth_it`), and a one-sentence `lesson`.
3. Durable lessons (tracked): at phase closeout the coordinator promotes
   sanitized, public-safe lessons into `planning/advisor_roi_lessons.md`.
4. Gradient following: raise the confidence bar for question types that
   repeatedly score `not_worth_it`; spend more freely on types that repeatedly
   score `worth_it`.

The raw ledger is never committed. Only sanitized lessons are promoted. This
keeps the learning loop auditable and consistent with the file-based handoff and
evidence conventions in `AGENTS.md`.

The `planning/advisor_roi_lessons.md` file is created lazily on the first phase
closeout that produces a durable lesson; it does not need to exist up front.

## Open Questions For Evidence

- Does Claude Opus 4.8 actually outperform the local coordinator enough on
  pre-closeout review and roadmap planning to justify its cost?
- Which question types most reliably score `worth_it`?
- What is a sensible default per-phase paid budget once real records exist?
- Does raising Advisor thinking effort to very-high change the ROI enough to
  justify the extra cost on hard questions?

These should be answered from accumulated `advisor_roi_ledger.jsonl` records and
promoted `advisor_roi_lessons.md` entries, not from a single run.
