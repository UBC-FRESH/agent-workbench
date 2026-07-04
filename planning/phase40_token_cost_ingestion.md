# Phase 40 Observability And Token-Cost Ingestion

Phase 40 adds a public-safe token/cost record surface for Agent Workbench pilot
accounting. Observability remains optional measurement input, not a dependency
for basic workflows.

## Source Audit

Useful token/cost sources include:

- SDK summary files produced by local model evaluation runs;
- provider usage metadata when available;
- PostHog-style AI observability exports after sanitization; and
- manual estimates when direct usage data is unavailable.

Agent Workbench should not commit raw observability exports. Raw prompts,
messages, traces, provider URLs, headers, cookies, credentials, and personal
paths must stay out of tracked records.

## Sanitized Import Contract

`templates/token_cost_record.json` defines the sanitized record shape:

- record id;
- source type;
- generated timestamp;
- project/task/model/protocol scope;
- supervisor and worker input/output token counts;
- per-1M-token price assumptions; and
- public-safety assertions that raw prompts, traces, URLs, headers, and personal
  paths are excluded.

The record is intentionally close to the P35 accounting fields so supervisors
can copy or summarize token data into pilot accounting records.

## CLI Surface

Validate one record:

```powershell
agent-workbench tokens validate --input <usage.tokens.json>
```

Render one record:

```powershell
agent-workbench tokens render `
  --input <usage.tokens.json> `
  --output <usage.tokens.md>
```

Synthesize a batch:

```powershell
agent-workbench tokens synthesize `
  --input-dir <runtime-dir> `
  --output <token-cost-synthesis.md>
```

## Boundary

The token-cost helper is a measurement aid. It does not:

- collect telemetry automatically;
- send data to an observability service;
- parse raw prompts or messages;
- store provider endpoints or headers; or
- replace P35 pilot accounting records.

## Closeout Evidence

P40 adds:

- `src/agent_workbench/tokens.py`;
- `agent-workbench tokens validate|render|synthesize`;
- `templates/token_cost_record.json`;
- this planning note; and
- README, roadmap, changelog, and smoke-check updates.
