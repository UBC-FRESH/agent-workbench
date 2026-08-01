# Coordinator Advisor Paid-Boost Strategy

This note records the Agent Workbench strategy for the coordinator and advisor
lanes. P118 moved every role onto one shared vLLM model and made the advisor
same-model advisory-only. **The 2026-08-01 decision below partially reverses
that** for the advisor lane specifically: the advisor is paid again, on
evidence. Read the sections in reverse-chronological order; earlier ones are
retained for history.

## Advisor Model Decision (2026-08-01)

**Decision:** the Advisor runs on `claude-opus-5`, invoked as
`Claude Opus 5 (copilot)`. Supervisor and Worker lanes stay on the local vLLM
model. This is a standing exception, not a general return to paid roles.

**Evidence and its limits.** The live Copilot model catalog was enumerated on
2026-08-01 from the chat extension's per-session `models.json` debug-log
snapshot: 49 entries, 25 picker-enabled. **That snapshot is local and untracked**
(it lives under the VS Code `workspaceStorage` Copilot chat debug-log directory
for the session), so a later reader cannot re-verify it from the repo alone. To
reproduce, read `models.json` in the current session's Copilot chat debug-log
folder. Price units are USD-per-1M x 100.

The decisive finding — stated as scoped to that snapshot, not as a standing law
of the vendors:

- **Every Claude model in the snapshot bills long context at the flat
  short-context rate.**
- **Every GPT-5.x, Gemini Pro, and Grok model in the snapshot charges 2.0x input
  / 1.5x output** past the long-context threshold (Grok: 2.0x/2.0x).

Pricing is vendor-controlled and can change without notice, so treat this as a
dated observation. Re-check the snapshot before relying on it for a future model
decision.

The Advisor is a large-context role by construction — its whole protocol is
"attach all the evidence and ask one well-scoped question." It therefore lives
permanently in the regime where the GPT lane doubles. Concretely, Claude Opus 5
is $5.00/$25.00 per 1M flat, versus GPT-5.6 Sol at $5.00/$30.00 rising to
$10.00/$45.00 in long context.

Opus 5 also carries a 936k prompt window, adaptive thinking with a 32k thinking
budget, and a `low`->`max` reasoning-effort ladder — the last matters because
the advisor profile's own hint tells the caller to raise reasoning effort for
hard calls. Several otherwise-plausible models (Claude Opus 4.5, Sonnet 4.5,
Haiku 4.5, Kimi K2.7) expose **no** reasoning-effort ladder at all and are poor
fits for this reason.

**Rejected alternatives:**

- *GPT-5.6 Sol / GPT-5.5* — costlier on both axes than Opus 5, no adaptive
  thinking, and penalized precisely in the long-context regime this role
  occupies. Strictly dominated.
- *Claude Fable 5 / Opus 4.8 fast* — $10.00/$50.00, i.e. 2x Opus 5, with
  metadata identical to Opus 5 (same 936k window, same 32k thinking budget,
  same effort ladder, same category). No observable capability delta to justify
  the premium. Held as an escalation target only if Opus 5 demonstrably
  underperforms on a real advisory call.
- *Claude Opus 4.5* — same price as Opus 5 but a 128k window and no effort
  ladder. A picker trap; do not substitute.

**Supersedes** the earlier provisional conjecture in this note that Claude Opus
4.8 was the large-context candidate. Opus 5 is the same price, window, and
thinking budget, one generation newer — strictly dominant at equal cost. The
conjecture is now settled by catalog evidence rather than adopted on faith.

**Also settled:** the hard "one Advisor invocation per phase" cap was removed
the same day (see Invocation Discipline below). The two changes are coupled —
the cap's original justification was rationing paid tokens, and the flat-priced
lane makes repeated well-framed calls cheap. A heavy Advisor call (~200k
evidence in, ~30k out including thinking) costs roughly $1.75.

**Open follow-up (not actioned):** `model_profiles/pricing_catalog.json`
disagrees with Copilot billing for two of its three entries — Terra listed
$2.50/$15.00 vs actual $2.00/$12.00, Luna listed $1.00/$6.00 vs actual
$0.20/$1.20. It appears to hold OpenAI direct-API rates while being consulted in
a Copilot context. Only its `gpt-5.6-sol` row matches. Note the corollary: that
file is **not** usable as independent corroboration of the snapshot's price
units, since a source wrong on two of three rows agreeing on the third is weak
evidence. Out of scope for this decision; recorded so it is not lost.

## Advisor Continuity (2026-08-01)

Copilot subagents are stateless across invocations — no resume handle, no
follow-up channel. Advisor continuity is therefore **file-based**, in
`planning/advisor_dossier.md`. The Advisor reads it at the start of each call;
the Coordinator appends the returned `Dossier entry:` block, including for
advice it rejected.

This is treated as contract-aligned rather than a workaround. A persistent,
stateful Advisor would be exactly the "memory trace" that `AGENTS.md` rejects in
favour of structured handoff, and would make advisory judgments unauditable.

## P118 Deployment (2026-07-21)


**Arrangement as of P118 (superseded for the advisor lane on 2026-08-01):**

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

Multiple profiles implement the hierarchy in `.github/agents/`. Under P118 all
roles shared one configured remote vLLM model (`Fresh vLLM Agent (Qwen 3.6
27B)`); since 2026-08-01 the advisor runs on `claude-opus-5` instead. Role
separation otherwise comes from bounded instructions and authority, not from
deploying different models:

- `agent-workbench-coordinator.agent.md` — thin coordinator; owns process
  discipline, ticketing, verification, and serial inference enforcement.
- `agent-workbench-local-supervisor.agent.md` — supervisor; runs bounded job
  tickets and returns compact evidence with an explicit job-end signal.
- `agent-workbench-advisor.agent.md` — read-only, advisory-only node invoked by
  the coordinator for hard reasoning (on `claude-opus-5` since 2026-08-01).
- `strict-worker.agent.md` — strict bounded worker.
- `strict-worker-next.agent.md` — strict bounded worker.
- `agent-workbench-result-auditor.agent.md` — internal read-only auditor.
- `document-metadata-extraction-supervisor.agent.md` — domain-specific supervisor
  for document metadata extraction pilots.

The Advisor reuses the existing subagent delegation plumbing (the coordinator
invokes it as a named subagent). The differences are the skin and the model: the
Advisor's tools are restricted to read-only, its instructions enforce
advisory-only output, and its profile pins `model: Claude Opus 5 (copilot)`.
The other profiles use the shared local vLLM alias.

## Advisor Delegation Candidates

High-value, hard-for-local, expensive-if-wrong question types:

- pre-closeout review of a coordinator report and its evidence before a roadmap
  phase is closed;
- roadmap critique recommending strategic, tactical, or operational shifts; and
- several-phases-ahead look-ahead roadmap extension, expansion, or pivot design.

**Settled 2026-08-01.** This note previously conjectured, unverified, that Claude
Opus 4.8 was strong at large-context big-picture work, and adopted that
provisionally. The Advisor Model Decision section above replaces the conjecture
with `claude-opus-5`, chosen on catalog evidence (flat long-context pricing,
936k window, adaptive thinking, full reasoning-effort ladder) rather than on an
assumed capability ranking. Opus 5 matches Opus 4.8 on price, window, and
thinking budget while being one generation newer, so nothing is given up.

Whether the Advisor lane actually earns its cost remains an open empirical
question, now tracked per-invocation in `planning/advisor_dossier.md`.

Poor candidates (coordinator does these itself): mechanical checks, ticket
templating, status polling, evidence existence checks, checklist reconciliation,
routine supervisor ticket preparation.

## Invocation Discipline

**Superseded (P118, then revised 2026-08-01):** the original "scarce paid-token
budget" model rationed a genuinely paid Advisor. P118 briefly made the Advisor
free by putting it on the shared local model, and the 2026-08-01 decision made
it paid again on `claude-opus-5`. The hard "one invocation per phase" default is
removed regardless — **but note the reason is not "it is free now," because it
is not.** The reason is that the Advisor lane is flat-priced, a well-framed call
costs on the order of a dollar or two, and rationing that against the cost of a
bad phase closeout is a false economy. Do not reinstate the cap on the grounds
that the Advisor became paid again.

There is no fixed cap on Advisor invocations, and no mandatory trigger that
forces one. The Coordinator invokes the Advisor when doing so adds value:

- The coordinator should not spend Advisor time on work it can verify
  mechanically — not because calls are rationed, but because a mechanical
  question wastes the lane's only real advantage.
- Prefer one well-scoped Advisor question with all evidence attached over
  several vague ones.
- Define the question, the stop condition, and the evidence artifact before
  invoking.
- If repeated Advisor passes stop changing the decision, treat that as a signal
  the question is misframed. Reframe it or escalate to the developer.

Advice has tended to pay off around workflow-critical milestones: reviewing
planning before a phase launches, auditing a phase at closeout, a hard mid-phase
design choice, or breaking a stubborn blocker. That is a description of where
value has shown up, **not** a set of gates to satisfy.

**Ceilings and floors are the same defect.** Per the project's "signal over
enforcement" principle, guidance here is a tripwire the coordinator reads, not a
rail the workflow must bend to. Agents must not reintroduce an invocation budget
*or* a mandatory-consultation trigger as a default. If either is ever wanted,
the developer sets it explicitly for that stretch of work.

The reason is not squeamishness about rules. A workflow in which agents perform
invented ceremonies is worse than one in which they think: the ceremony becomes
the goal, evidence of compliance substitutes for judgment, and the ritual
survives long after the condition that motivated it has gone. The 2026-08-01
removal of the seven "mandatory Advisor triggers" from
`native_codex_remote_ollama_findings.md` is the worked example.

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
