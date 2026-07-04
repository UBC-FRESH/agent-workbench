# Phase 36 Policy Tuning Loop

Phase 36 turns P35 pilot accounting records into transparent delegation policy
guidance. The policy loop stays rules-based and supervisor-auditable.

## Outcome Schema

P36 uses sanitized P35 accounting records as the outcome schema. The fields
needed for policy tuning are:

- `task_type`;
- `roadmap_level`;
- `model`;
- `protocol`;
- `authority_level`;
- `task_selection`;
- `token_accounting`;
- `claim_review`;
- `verification`;
- `outcome.classification`; and
- `supervisor_assessment`.

This preserves enough detail to tune task suitability, model trust, ticket
shape, retry limits, and bailout thresholds without storing raw prompts,
transcripts, provider endpoints, headers, credentials, or personal paths.

## Tuning Rules

The first tuning loop is deliberately simple:

- promote cautiously when records are mostly promising, net savings are
  positive, and accepted claims exceed rejected claims;
- hold steady when evidence is sparse or mixed;
- lower trust when records are mostly poor, net savings are negative, or
  rejected claims exceed accepted claims;
- use one retry for sparse/mixed evidence;
- allow two retries only for positive groups with repeat evidence; and
- bail out after two poor outcomes for the same task/model/protocol group unless
  the supervisor rewrites the ticket or changes the model.

Policy changes are recommendations, not automatic repository mutations.

## CLI Surface

Render a tuning report from one or more accounting records:

```powershell
agent-workbench policy tune `
  --input-dir <pilot-runtime-dir> `
  --output <policy-tuning-report.md>
```

The report groups records by task type, model, and protocol. For each group it
reports:

- record count;
- promising, poor, mixed, and insufficient-evidence counts;
- claim-review totals;
- total and average net savings;
- retry limit guidance;
- bailout guidance; and
- supervisor-readable rationale.

## Future ML Boundary

Machine-learning policy optimization remains premature. A later ML optimizer is
not worth designing until the record set is large, varied, sanitized, and
independently verifiable.

The P36 report uses conservative thresholds:

- at least 100 sanitized records;
- at least 6 task types; and
- at least 3 model or project groups.

Until those thresholds are met, Agent Workbench should continue using
rules-based tuning.

## Closeout Evidence

P36 adds:

- `src/agent_workbench/policy.py`;
- `agent-workbench policy tune`;
- this planning note;
- README and deployment playbook updates; and
- roadmap/changelog updates.

P37 can now build artifact/workflow contracts with a concrete evidence loop
behind it.
