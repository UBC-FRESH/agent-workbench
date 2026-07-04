# Phase 34 Delegation Decision Engine V0

Phase 34 adds the first transparent rules-based delegation recommender. The
goal is to help the supervisor decide whether a candidate task bundle should be
delegated, split smaller, deferred, handled directly, or escalated to human
judgment.

## Boundary

P34 is a supervisor-side decision aid. It does not run workers, install models,
mutate target projects, instrument observability, or optimize policy with
machine learning.

The command evaluates one JSON input file and renders a Markdown report:

```powershell
agent-workbench decide task `
  --input runtime/decision_examples/delegate.json `
  --output runtime/decision_examples/delegate.md
```

Raw dogfood inputs and generated reports stay under ignored runtime paths unless
sanitized findings are promoted into tracked planning notes.

## Input Contract

The tracked template is `templates/delegation_decision_input.json`.

Required fields:

- `task_id`
- `title`
- `task_type`
- `roadmap_level`
- `suitability`
- `risk`
- `model`
- `authority_level`
- `expected_verification`
- `model_profile_status` or `model_profile_path`

Optional safety fields:

- `requires_tracked_mutation`
- `requires_github_mutation`
- `requires_release_or_closeout`
- `requires_private_context`

Optional economics fields live under `economics`:

- `direct_supervisor_input_tokens`
- `direct_supervisor_output_tokens`
- `delegated_supervisor_input_tokens`
- `delegated_supervisor_output_tokens`
- `worker_input_tokens`
- `worker_output_tokens`
- `cleanup_supervisor_input_tokens`
- `cleanup_supervisor_output_tokens`
- `supervisor_input_price_per_1m_usd`
- `supervisor_output_price_per_1m_usd`
- `worker_input_price_per_1m_usd`
- `worker_output_price_per_1m_usd`
- `failure_probability`
- `latency_friction_minutes`

The primary unit is token-priced USD, not wall-clock time. Minutes are retained
only as optional friction metadata because paid supervisor cost is driven by
token usage while the supervisor is thinking, prompting, verifying, and fixing.
Self-hosted worker models usually have zero marginal API-token price in this
model, but they still have verification and cleanup risk.

Token counts should come from real run usage when available. PostHog-style AI
observability can capture model, latency, input tokens, output tokens, total
cost, and multi-agent/tool trace structure for OpenAI Agents SDK workflows.
OpenAI model pricing is published as input, cached-input, and output prices per
1M tokens, so the price fields in a decision input should be supplied from the
current provider price matrix instead of hard-coded in Agent Workbench.

The command computes:

```text
direct supervisor cost =
  direct input tokens * supervisor input price
  + direct output tokens * supervisor output price

expected delegated cost =
  delegated supervisor token cost
  + worker token cost
  + failure_probability * cleanup supervisor token cost

expected net savings USD =
  direct supervisor cost
  - expected delegated cost
```

## Recommendation Set

The first engine can return:

- `delegate`
- `do-directly`
- `split-smaller`
- `needs-human-decision`
- `defer`

Every result includes reason strings, cautions when relevant, economics terms,
and a supervisor next action.

## Conservative Rules

The rules are intentionally conservative:

- tracked-file mutation, GitHub mutation, release work, closeout work, and L4-L6
  authority stay supervisor-owned;
- private or hidden context produces `defer`;
- planned or missing model profiles produce `defer`;
- project and phase-level bundles produce `split-smaller`;
- critical-risk tasks produce `do-directly`;
- negative expected net savings USD produces `do-directly`; and
- observed-profile, low/medium-risk, high/medium-suitability L0/L1 tasks with
  positive economics can produce `delegate`.

These rules are not meant to be optimal. They are meant to be auditable.

## Dogfood Findings

P34 dogfood used ignored runtime inputs for three representative cases:

| Case | Expected decision | Purpose |
| --- | --- | --- |
| Evidence intake task | `delegate` | Shows the useful L1 proposal-assist path. |
| Phase-level roadmap review | `split-smaller` | Shows broad work should be decomposed first. |
| GitHub closeout task | `do-directly` | Shows nondelegable workflow state stays supervisor-owned. |

The reports exposed the expected token-priced USD economics and rule reasons.
The output is good enough to paste into a planning discussion, but it is
deliberately not a worker launcher.

## P35 Implication

P35 should use `agent-workbench decide task` before launching real-project pilot
packs. For `gpt-oss:*` model variants, the decision engine should initially
return `defer` unless an exact installed tag and observed capability profile are
available. That makes the next real-world data step explicit rather than
letting an untested model family slip into project work.
