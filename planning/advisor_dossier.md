# Advisor Dossier

This file is the Advisor's memory.

Copilot subagents are **stateless across invocations**. There is no persistent
Advisor session, no resume handle, and no channel to send a follow-up. Every
invocation constructs a fresh Advisor from its prompt. Anything the Advisor
"knows" about its own prior positions has to be read from this file.

That constraint is not purely a limitation. It matches the working contract's
**"structured handoff, not memory trace"** principle: a persistent, stateful
Advisor would accumulate unlogged context that silently shapes its judgments,
and you would lose the ability to audit which evidence produced which
recommendation. Here, every standing position is an artifact.

## When to invoke the Advisor

There is **no cap** on invocations and **no mandatory trigger** that forces one.
Invoke it when asking for advice adds value. That is a judgment call belonging
to the Coordinator.

Advice has tended to pay off around workflow-critical milestones — reviewing
planning before a phase launches, auditing a phase at closeout, a hard mid-phase
design choice, or finding the clue that gets past a stubborn blocker. Read that
as signal about where to think harder, not as a checklist to satisfy. Agents
must not add invocation rules in either direction.

## Protocol

This is bookkeeping, so advice stays auditable and a later Advisor is not flying
blind. It is not a ceremony, and none of it obliges anyone to consult.

**Coordinator, when you have consulted the Advisor:**

- Point it at this file in the ticket so it can read its own prior positions.
- The Advisor is read-only (`tools: ['read', 'search']`) and **cannot write
  here**. It returns a `Dossier entry:` block; you append it.
- Append the entry **whether or not you took the advice**. Record rejections and
  the reason — otherwise a future Advisor will confidently re-recommend things
  you already turned down.
- Keep entries sanitized and public-safe: no credentials, no private paths, no
  raw transcripts.

The one hard rule is about honesty, not process: if a report claims the Advisor
was consulted, there must be an entry here showing it.

**Advisor:** end each reply with the `Dossier entry:` block defined in
`.github/agents/agent-workbench-advisor.agent.md`. Always state what would change
your mind — a judgment with no stated falsifier is an opinion, not advice.

## Entry format

```
### <YYYY-MM-DD> — <short title>
- question: <one line>
- recommendation: <one line>
- key evidence: <paths, commands, or artifacts actually relied on>
- confidence: high | medium | low
- would change my mind: <what evidence would flip this>
- coordinator disposition: accepted | rejected | deferred — <why>
```

## Log

### 2026-08-01 — Advisor model binding probe

Not an advisory judgment. Recorded because it establishes the lane.

- question: does the model string `Claude Opus 5 (copilot)` route to the
  intended model, and does the Advisor profile's read-only boundary hold?
- recommendation: n/a (verification call)
- key evidence: `runSubagent` probe returned a self-identification as Claude
  Opus 5 (Anthropic); the Advisor confirmed read-only status and that it is
  barred from invoking subagents; it correctly flagged that the returned
  identity did **not** match the documented local vLLM default at the time,
  and recommended checking the routing.
- confidence: high (call succeeded, string is valid, boundary held)
- would change my mind: n/a
- coordinator disposition: accepted — the flagged mismatch was the intended
  change, not a defect. Model Identity table updated in the same session.

Note: the Advisor's self-reported context window ("on the order of 200K") is
**wrong** and it correctly hedged that it could not verify. The live catalog
reports a 936k prompt window / 1M context window for `claude-opus-5`. Do not
take model self-reports about their own limits as evidence.

### 2026-08-01 — Review of the Advisor-lane contract change set

- question: is the 2026-08-01 change set (cap removal, Opus 5 binding,
  file-based continuity) consistent, evidenced, and free of cap residue?
- recommendation: do not close out yet. Direction correct and the edited files
  cohere, but six unedited tracked files still asserted the Advisor shares the
  local vLLM model; the cap-removal rationale rested on a premise the same note
  later overturned; the pricing universals had no in-repo artifact; and the
  dossier obligation was missing from the coordinator profile — the only
  channel that reliably reaches a Coordinator running as a subagent.
- key evidence: `planning/delegation_policy.md` L4;
  `playbooks/p118_single_model_operator_checklist.md` L6, L20;
  `docs/roadmap_and_release/roadmap_overview.md` L33 vs L52;
  `planning/coordinator_advisor_paid_boost_strategy.md` L142, L163;
  `planning/p120_sdk_authoritative_agent_hub_qualification.md` L43;
  `planning/native_codex_remote_ollama_findings.md` L324-396;
  `planning/session_cbebdef3_summary.md` L41;
  `.github/agents/agent-workbench-coordinator.agent.md` (no dossier reference);
  `.github/copilot-instructions.md` L85 vs Topology section.
- confidence: high on file-level contradictions and the missing enforcement
  mechanism (directly read); medium on the risk ranking.
- would change my mind: a committed/dated catalog snapshot backing the pricing
  universals; a `model:` frontmatter field on the Advisor profile or a validator
  failing packets that claim "Advisor consulted" without a dossier entry;
  evidence that subagent-invoked Coordinators reliably receive
  `.github/copilot-instructions.md`.
- coordinator disposition: **accepted in substance, partially deferred.**

  Acted on the same session:
  - Added `model: Claude Opus 5 (copilot)` to the Advisor profile frontmatter.
    This was the Advisor's own stated mind-changer for the primary risk, and
    `.github/agents/ornith-read-tool-probe.agent.md` confirmed the field is
    supported. The lane is now pinned in config, not only in prose.
  - Added a dossier-obligation section to the coordinator profile, including
    "no entry, no claim."
  - Fixed `delegation_policy.md`, the P118 operator checklist (both the stale
    `Fresh vLLM Agent (Qwen 3.6 27B)` alias and the "invoke only for" rationing
    phrasing), `roadmap_overview.md`, the P120 shared-alias claim, and the
    residual same-model line in the strategy note.
  - Rewrote the cap-removal rationale. The Advisor was right that it rested on
    a dead premise ("it is free now") which the same note falsifies. It now
    rests on flat pricing and cost asymmetry, with an explicit warning not to
    reinstate the cap on the grounds that the Advisor became paid again.
  - Scoped the pricing universals to the dated snapshot, recorded how to
    reproduce it, and noted it is local/untracked.
  - Withdrew `pricing_catalog.json` as corroboration, per the circularity
    finding — it is wrong on two of three rows.
  - Fixed the "one child task at a time" cap that contradicted the 2-4 parallel
    guidance in the same file. Good catch; that was pre-existing residue.

  Deferred, with reasons:
  - **Format mismatch** between the Advisor's flat `- date:` block and this
    file's heading format: resolved by instructing the Coordinator to transform
    rather than append verbatim, rather than by loosening the format.
  - **Dated experimental protocols** (`phase95`, `phase107_2`,
    `p107_2_ab_research...`) left as history. They record what was done in a
    past run and are not live policy.
  - **`native_codex_remote_ollama_findings.md` mandatory-trigger policy**
    (7 mandatory Advisor triggers + proposed hard closeout failure): escalated
    to the Developer, not unilaterally rewritten. The Advisor correctly
    identified it as the same defect species inverted — a floor rather than a
    ceiling — but removing a mandatory-consultation policy is a judgment call
    about how much discretion the Coordinator should have, which is the
    Developer's to make.
    **RESOLVED same day:** the Developer directed that hard floors be removed
    too. The seven mandatory triggers, the required consultation-packet schema,
    and the five-step enforcement ladder (ending in "make deterministic closeout
    validation fail") are deleted. The section is now `Advisor Role and
    Invocation Judgment` and carries the useful signal — where advice has paid
    off — explicitly labelled as *not* a checklist. Developer's stated intent:
    invoke the Advisor when requesting advice adds value; no "agent cult"
    performing invented rituals.
  - **`roadmap_overview.md` wholesale staleness** (still says "Current Active
    Phase: P118"; `ROADMAP.md` says P125): flagged, not fixed. Syncing the
    published roadmap is real work and deserves a bounded ticket, not an inline
    edit buried in an unrelated change set.
  - **Unverified probe provenance** for the Ornith and Sockeye model strings:
    acknowledged as a fair hit. Not re-probed this session; both are pre-existing
    claims inherited from 2026-07-31.

### 2026-08-01 — Model pinning precedence (measurement, not advice)

Recorded because it qualifies the mitigation adopted above.

- question: does `model:` frontmatter on an agent profile actually enforce the
  Advisor's model, closing the "silently inherits the wrong model" risk?
- finding: **No — it is a fallback, not a guardrail.** An explicit `model`
  argument on `runSubagent` overrides the profile frontmatter. Verified by
  invoking `agent-workbench-advisor` with
  `Ornith 1.0 35B FP8 (copilotcustommodelsendpoint)`; it ran on Ornith despite
  the profile pinning Opus 5.
- second finding, **inconclusive**: invoking the Advisor with the `model`
  argument omitted returned Opus 5, consistent with frontmatter pinning — but
  the calling chat was itself Opus 5, so frontmatter-default and
  chat-inheritance cannot be distinguished from that observation. Recorded as
  unverified rather than counted as a pass.
- consequence: the Advisor's proposed mitigation ("a `model:` frontmatter field
  would retire the primary risk") is **only partly satisfied**. The residual
  risk inverts: because the standing rule is "always pass `model`," a
  Coordinator can paste the routine local string into an Advisor call and
  silently downgrade the Advisor while still reporting "Advisor consulted."
  Documented as an explicit foot-gun in the coordinator profile.
- confidence: high on the override behaviour (directly measured); the fallback
  behaviour is explicitly unverified.
- would change my mind: a control test from a chat session running a
  non-Opus model, invoking the Advisor with `model` omitted, would settle the
  fallback question.
- coordinator disposition: accepted. The frontmatter is retained as a
  defence-in-depth default, but the contract no longer claims it enforces
  anything. The real enforcement remains the "no entry, no claim" dossier rule.


