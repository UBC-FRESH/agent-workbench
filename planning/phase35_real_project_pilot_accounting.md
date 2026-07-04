# Phase 35 Real-Project Pilot Accounting

Phase 35 adds the first durable accounting surface for real-project
Agent Workbench pilots. The purpose is to measure whether supervised delegation
reduces paid supervisor token/cash cost per useful merged unit of work.

## Scope

P35 is about accounting, not broader automation.

Included:

- candidate pilot selection protocol;
- sanitized pilot accounting record template;
- CLI validation, rendering, and synthesis;
- net-savings calculations from token counts and price assumptions;
- claim-review counts; and
- supervisor-visible promising/poor delegation class summaries.

Excluded:

- raw prompt or transcript ingestion;
- provider secret or endpoint tracking;
- worker mutation authority;
- GitHub closeout by workers; and
- automatic policy tuning.

## Pilot Selection Protocol

Early real-project pilots should be selected from a live project roadmap or
issue tracker, but they should not be on a project critical path. The useful
first set should include variation across:

- task type;
- task size;
- worker model;
- ticket protocol; and
- expected verification cost.

Good early candidates:

- evidence intake;
- documentation proposal;
- test-design proposal;
- issue triage;
- bounded API ergonomics proposal; and
- benchmark interpretation.

Poor early candidates:

- broad phase closeout;
- release management;
- GitHub issue/PR mutation;
- private-context work;
- high-risk architecture decisions; and
- tasks where worker output cannot be independently verified.

## Accounting Record

`templates/pilot_accounting_record.json` defines the P35 record shape. Each
record captures:

- project and task metadata;
- why the pilot was selected;
- paid supervisor token counts and price assumptions;
- local worker token counts and price assumptions;
- verification, cleanup, and retry token counts;
- accepted, rejected, and needs-evidence claim counts;
- whether the worker changed the supervisor decision; and
- the supervisor's final assessment.

Records should live under ignored target-project runtime paths while raw pilot
work is active. Sanitized records can be promoted only when they contain no raw
transcripts, provider endpoints, secrets, or personal paths.

## CLI Surface

Validate one record:

```powershell
agent-workbench accounting validate --input <pilot.accounting.json>
```

Render one record:

```powershell
agent-workbench accounting render `
  --input <pilot.accounting.json> `
  --output <pilot.accounting.md>
```

Synthesize a pilot batch:

```powershell
agent-workbench accounting synthesize `
  --input-dir <pilot-runtime-dir> `
  --output <pilot-accounting-synthesis.md>
```

The synthesis reports direct paid-supervisor cost, delegated cost, worker cost,
verification/cleanup/retry cost, net savings, and promising/poor delegation
classes.

## Interpretation

A worker result is not successful merely because it looks plausible. The
supervisor should classify a pilot as promising only when the accepted value and
token/cash savings exceed setup, verification, retry, cleanup, and
context-switching costs.

Imperfect proposals can still be promising when accepted claims are useful,
rejected claims are easy to discard, and verification is cheaper than direct
supervisor synthesis.

Failures are useful evidence when they expose task/model/protocol combinations
that should be avoided or split smaller.

## Closeout Evidence

P35 adds:

- `src/agent_workbench/accounting.py`;
- `agent-workbench accounting` CLI commands;
- `templates/pilot_accounting_record.json`;
- real-project deployment playbook guidance; and
- roadmap/changelog updates.

This gives P36 a concrete input surface for policy tuning.
