# Copilot Model Catalog — Enumeration, Pricing, and Subagent Routing

Operational reference for choosing and routing GitHub Copilot models in Agent
Workbench. Captured 2026-08-01.

Vendor pricing and model availability change without notice. Everything below is
a **dated observation from one snapshot**, not a standing law. Re-enumerate
before relying on it for a new decision.

## How to enumerate the live catalog

The Copilot chat extension writes the model list the backend advertised for the
session to disk. This is the authoritative source for what is actually available
under the current plan — better than recollection, and better than public docs.

```
<VS Code user dir>/workspaceStorage/<workspace-hash>/GitHub.copilot-chat/debug-logs/<session-id>/models.json
```

Sibling `main.jsonl` in the same directory is the session transcript. The
snapshot is local and untracked; do not commit it.

Useful fields per entry:

| Field | Meaning |
| --- | --- |
| `model_picker_enabled` | whether it appears in the picker at all |
| `billing.token_prices.default` | rates in **USD per 1M x 100** (`500` = $5.00) |
| `billing.token_prices.long_context` | rates past the long-context threshold |
| `billing.restricted_to` | plan gating (`pro`, `pro_plus`, `business`, ...) |
| `capabilities.limits.max_prompt_tokens` | usable prompt window |
| `capabilities.supports.reasoning_effort` | the effort ladder, if any |
| `capabilities.supports.adaptive_thinking` | thinking support |
| `policy.state` | `enabled`, or needs opt-in |

The 2026-08-01 snapshot held 49 entries, 25 picker-enabled.

## Picker-enabled models (2026-08-01 snapshot)

| Model | id | Vendor | In $/1M | Out $/1M | Long-ctx | Prompt win | Max out | Think | Reasoning effort |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Fable 5 | `claude-fable-5` | Anthropic | 10.00 | 50.00 | flat | 936,000 | 64,000 | yes | `low`, `medium`, `high`, `xhigh`, `max` |
| Claude Opus 4.8 (fast mode) (Preview) | `claude-opus-4.8-fast` | Anthropic | 10.00 | 50.00 | flat | 936,000 | 64,000 | yes | `low`, `medium`, `high`, `xhigh`, `max` |
| Claude Opus 4.5 | `claude-opus-4.5` | Anthropic | 5.00 | 25.00 | n/a | 127,997 | 32,000 | no | **none** |
| Claude Opus 4.6 | `claude-opus-4.6` | Anthropic | 5.00 | 25.00 | flat | 936,000 | 64,000 | yes | `low`, `medium`, `high`, `max` |
| Claude Opus 4.7 | `claude-opus-4.7` | Anthropic | 5.00 | 25.00 | flat | 936,000 | 64,000 | yes | `low`, `medium`, `high`, `xhigh`, `max` |
| Claude Opus 4.8 | `claude-opus-4.8` | Anthropic | 5.00 | 25.00 | flat | 936,000 | 64,000 | yes | `low`, `medium`, `high`, `xhigh`, `max` |
| Claude Opus 5 | `claude-opus-5` | Anthropic | 5.00 | 25.00 | flat | 936,000 | 64,000 | yes | `low`, `medium`, `high`, `xhigh`, `max` |
| GPT-5.5 | `gpt-5.5` | OpenAI | 5.00 | 30.00 | 2.0x/1.5x | 922,000 | 128,000 | no | `none`, `low`, `medium`, `high`, `xhigh` |
| GPT-5.6 Sol | `gpt-5.6-sol` | OpenAI | 5.00 | 30.00 | 2.0x/1.5x | 922,000 | 128,000 | no | `none`, `low`, `medium`, `high`, `xhigh`, `max` |
| Claude Sonnet 4.5 | `claude-sonnet-4.5` | Anthropic | 3.00 | 15.00 | n/a | 124,801 | 32,000 | no | **none** |
| Claude Sonnet 4.6 | `claude-sonnet-4.6` | Anthropic | 3.00 | 15.00 | flat | 936,000 | 64,000 | yes | `low`, `medium`, `high`, `max` |
| GPT-5.4 | `gpt-5.4` | OpenAI | 2.50 | 15.00 | 2.0x/1.5x | 922,000 | 128,000 | no | `none`, `low`, `medium`, `high`, `xhigh` |
| Claude Sonnet 5 | `claude-sonnet-5` | Anthropic | 2.00 | 10.00 | flat | 936,000 | 64,000 | yes | `low`, `medium`, `high`, `xhigh`, `max` |
| GPT-5.6 Terra | `gpt-5.6-terra` | OpenAI | 2.00 | 12.00 | 2.0x/1.5x | 922,000 | 128,000 | no | `none`, `low`, `medium`, `high`, `xhigh`, `max` |
| Gemini 3.1 Pro (Preview) | `gemini-3.1-pro-preview` | Google | 2.00 | 12.00 | 2.0x/1.5x | 936,000 | 64,000 | no | `low`, `medium`, `high` |
| Grok 4.5 | `grok-4.5` | xAI | 2.00 | 6.00 | 2.0x/2.0x | 425,001 | 128,000 | no | `low`, `medium`, `high` |
| GPT-5.3-Codex | `gpt-5.3-codex` | OpenAI | 1.75 | 14.00 | n/a | 271,997 | 128,000 | no | `low`, `medium`, `high`, `xhigh` |
| Gemini 3.5 Flash | `gemini-3.5-flash` | Google | 1.50 | 9.00 | flat | 936,000 | 64,000 | no | `minimal`, `low`, `medium`, `high` |
| Gemini 3.6 Flash | `gemini-3.6-flash` | Google | 1.50 | 7.50 | flat | 936,000 | 64,000 | no | `minimal`, `low`, `medium`, `high` |
| Claude Haiku 4.5 | `claude-haiku-4.5` | Anthropic | 1.00 | 5.00 | n/a | 124,801 | 32,000 | no | **none** |
| Kimi K2.7 Code | `kimi-k2.7-code` | Moonshot AI | 0.95 | 4.00 | n/a | 223,997 | 32,000 | no | **none** |
| GPT-5.4 mini | `gpt-5.4-mini` | OpenAI | 0.75 | 4.50 | n/a | 271,997 | 128,000 | no | `none`, `low`, `medium`, `high`, `xhigh` |
| MAI-Code-1-Flash | `mai-code-1-flash-picker` | Microsoft | 0.75 | 4.50 | n/a | 127,997 | 128,000 | no | `low`, `medium`, `high` |
| GPT-5 mini | `gpt-5-mini` | Azure OpenAI | 0.25 | 2.00 | n/a | 127,997 | 64,000 | no | `low`, `medium`, `high` |
| GPT-5.6 Luna | `gpt-5.6-luna` | OpenAI | 0.20 | 1.20 | 2.0x/1.5x | 922,000 | 128,000 | no | `none`, `low`, `medium`, `high`, `xhigh`, `max` |

## The long-context pricing asymmetry

The single most decision-relevant finding in the snapshot:

- **Every Claude model bills long context at the flat short-context rate.**
- **Every GPT-5.x, Gemini Pro, and Grok model charges 2.0x input / 1.5x output**
  past the threshold. Grok charges 2.0x/2.0x.

This matters for any role that is large-context *by construction* — a reviewer
or auditor whose protocol is "attach all the evidence and ask one question"
lives permanently in the penalised regime. Worked example: GPT-5.6 Sol and
Claude Opus 5 both list $5.00 input, but in long context Sol is $10.00/$45.00
against Opus 5's flat $5.00/$25.00.

Conversely, for short-context high-volume work the GPT lane is far cheaper —
GPT-5.6 Luna at $0.20/$1.20 is an order of magnitude below any Claude model.
The asymmetry is a reason to match model to *context profile*, not a reason to
prefer one vendor.

## Selection traps

- **Claude Opus 4.5** is the same $5.00/$25.00 as Opus 5 but has a **128k**
  window and **no reasoning-effort ladder**. Easy to misselect by name.
- Several models expose **no `reasoning_effort` ladder at all**: Opus 4.5,
  Sonnet 4.5, Haiku 4.5, Kimi K2.7 Code. Poor fits wherever a caller is expected
  to dial effort up for hard work.
- **Claude Fable 5** and **Opus 4.8 fast** cost 2x Opus 5 with metadata that is
  otherwise identical (same window, same 32k thinking budget, same ladder, same
  `powerful` category). No metadata-visible justification for the premium.
- Plan gating is real: `claude-opus-5`, `claude-fable-5`, `gpt-5.6-sol` and
  `gpt-5.5` are restricted to `pro_plus` / `business` / `enterprise` / `max`.

## Subagent model routing

### Model string format

`runSubagent` takes `model` as `<displayName> (<vendor>)`:

- **Built-in Copilot models** -> vendor is `copilot`, e.g.
  `Claude Opus 5 (copilot)`.
- **Custom endpoint models** -> vendor is `copilotcustommodelsendpoint`, and
  `displayName` must match the Keklick `customcopilot.models` entry exactly,
  e.g. `Ornith 1.0 35B FP8 (copilotcustommodelsendpoint)`. See
  `keklick-copilot-extension-config.md`.

### Precedence (measured 2026-08-01)

- An explicit `model` argument on `runSubagent` **overrides** an agent profile's
  `model:` frontmatter. Verified by invoking a profile pinned to Claude Opus 5
  with the Ornith string; it ran on Ornith.
- Omitting `model` appears to fall back to the profile frontmatter, else the
  current chat model. **Not cleanly verified** — the test chat was itself running
  the pinned model, so frontmatter-default and chat-inheritance were
  indistinguishable. A control from a chat on a different model would settle it.

**Consequence:** profile `model:` frontmatter is a *fallback, not a guardrail*.
It cannot protect against a caller passing the wrong model. Two failure modes,
both silent:

1. Omitting `model` inherits the current chat model — usually a paid frontier
   model — silently billing frontier tokens for work assumed to be free.
2. Mechanically pasting the routine local-lane string into a call meant for a
   paid reviewer silently downgrades it, while the report still claims the
   reviewer was consulted.

### Subagents are stateless across invocations

Copilot chat subagents cannot be resumed, messaged mid-flight, or run in the
background. Each invocation builds a fresh agent from its prompt; only the
final message comes back. State *is* preserved within a single invocation's
internal loop — it is discarded between invocations.

This differs from Codex, whose subagent implementation supports a persistent,
repeatedly-addressable agent.

Copilot *does* support persistent sessions, but on a different plane: the
SDK-owned session bridge built in P71/P72 has `resume_session()`, `session_id`
manifests, monitoring and nudging (`src/agent_workbench/copilot_sdk_bridge.py`).
That is script-driven and cannot be reached from inside a chat turn as a
subagent.

Practical pattern for cross-invocation continuity: keep a durable dossier file
and pass its path in each call, so continuity runs through the filesystem rather
than session state. See `planning/advisor_dossier.md`.

## Don't trust model self-reports

A probed model correctly self-identified its family but reported its context
window as "on the order of 200K" when the catalog listed a 936k prompt window /
1M context window. It hedged appropriately, but the number was wrong. Read
limits from `models.json`, never from the model.

## Copilot rates vs OpenAI first-party rates

`model_profiles/pricing_catalog.json` holds **OpenAI first-party API** list
rates and is explicitly scoped as such. Those are not Copilot billing rates.
Observed divergence on 2026-08-01:

| Model | OpenAI API catalog | Copilot billing |
| --- | --- | --- |
| `gpt-5.6-sol` | $5.00 / $30.00 | $5.00 / $30.00 (match) |
| `gpt-5.6-terra` | $2.50 / $15.00 | $2.00 / $12.00 |
| `gpt-5.6-luna` | $1.00 / $6.00 | $0.20 / $1.20 (5x) |

Agreement on one model is not validation of the catalog for Copilot purposes.
