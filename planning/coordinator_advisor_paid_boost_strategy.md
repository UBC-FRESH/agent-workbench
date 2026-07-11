# Coordinator Advisor Paid-Boost Strategy

This note records the Agent Workbench strategy pivot in which the coordinator
lane moves from a paid GPT-5.x agent (run in a separate Codex chat surface) to a
free local Ollama model running inside the VS Code GitHub Copilot chat UI, with
a new paid **Advisor** role available on demand.

## Strategy Pivot

Previous arrangement:

- Coordinator: paid GPT-5.x agent in a Codex chat interface.
- Supervisor and workers: free local Ollama models.

New arrangement (committed for the foreseeable future):

- All agentic UI workflow for Agent Workbench development runs in the built-in
  VS Code GitHub Copilot chat UI.
- Coordinator, supervisor, and worker roles all run as free-token open models
  on the configured GPU/Ollama worker host.
- Paid high-capability intelligence is no longer a persistent lane. It is an
  on-demand, budgeted **Advisor** the coordinator can invoke for hard subsets.

Tradeoff being accepted:

- Pro: large paid-token cash savings, since the always-on coordinator lane
  becomes free.
- Con: the local coordinator model (default `qwen3.6:35b-a3b-bf16`) is a capable
  process worker but weaker than GPT-5.x at open-ended big-picture reasoning.

Mitigation: the Advisor lets the coordinator "buy" bursts of strong reasoning
only where they add value, instead of paying for strong reasoning continuously.

## Custom Agent Profiles

Three profiles implement the hierarchy in `.github/agents/`:

- `agent-workbench-coordinator.agent.md` — free local coordinator; owns process
  discipline, ticketing, verification, and the paid budget.
- `agent-workbench-supervisor.agent.md` — free local supervisor; runs bounded
  job tickets and returns compact evidence with an explicit job-end signal.
- `agent-workbench-advisor.agent.md` — paid, read-only, advisory-only node
  (default Claude Opus 4.8) invoked by the coordinator for hard reasoning.

The Advisor reuses the existing subagent delegation plumbing (the coordinator
invokes it as a named subagent, the same way it would delegate to a supervisor).
The difference is only the skin: the Advisor's frontmatter pins a paid Copilot
model, which — unlike Ollama model frontmatter — is honored reliably by the
native Copilot path.

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
