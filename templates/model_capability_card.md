# Model Capability Card Template

Use this template to create public-safe profiles for worker models that have
been exercised through Agent Workbench tickets. A capability card is not a
leaderboard entry. It records what this repository has actually observed about
a model under specific task shapes, harnesses, and authority limits.

## Model Identity

- Model tag:
- Model family:
- Provider or host class: configured Ollama worker host
- Profile status: `observed`, `partial`, or `planned`
- Last reviewed:

## Inventory Evidence

- Installed-model evidence:
- Inventory date or source:
- Important caveat:

Use only sanitized inventory evidence. Do not include private endpoint URLs,
headers, server names, personal paths, or raw provider configuration.

## Evidence Scope

- Observed ticket families:
- Harness or bridge path:
- Repeats observed:
- Evidence surfaces:

Describe the exact task classes and evidence surfaces behind the profile.
Examples include no-tool marker probes, structured Markdown output trials,
patch-proposal trials, supervisor decision packets, or comparison summaries.

## Observed Strengths

-

## Observed Failure Modes

-

## Loop And Stop-Condition Risk

- Loop risk:
- Stop-compliance notes:
- Recommended retry limit:

## Ticket-Shape Sensitivity

- Good fit:
- Weak fit:
- Avoid:

## Delegation Guidance

- Recommended default authority ceiling:
- Suitable task types:
- Requires repeat run: `yes` or `no`
- Requires independent claim review: `yes`
- Suggested supervisor verification:

## Decision-Engine Inputs

- Default recommendation bias: `delegate`, `split`, `do-directly`,
  `needs-human-decision`, or `defer`
- Confidence: `low`, `medium`, or `high`
- Primary economics benefit:
- Primary cleanup risk:

## Open Questions

-

## Public-Safety Review

- [ ] No private endpoint, header, token, or credential values.
- [ ] No personal absolute paths.
- [ ] No raw transcript excerpts.
- [ ] No broad claims beyond observed Agent Workbench evidence.
- [ ] Authority guidance stays inside the current delegation policy.
