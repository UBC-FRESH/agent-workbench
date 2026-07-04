# P50 Mandatory Supervisor Token Accounting

P50 exposed the central economics gap in Agent Workbench: local worker token
usage can be measured from Ollama/Copilot SDK metadata, but paid supervisor
usage must be segmented at the same operational granularity or the benchmark
cannot say whether delegation is winning.

## Contract

No future benchmark iteration may claim token-economics evidence unless every
supervisor-owned subtask has explicit start and end checkpoints.

The required runtime ledger root is:

```text
runtime/supervisor_tokens/<benchmark_id>/
```

Each benchmark should checkpoint these spans when present:

- `setup`;
- `ticket_build`;
- `worker_run_orchestration`;
- `worker_output_summarize`;
- `supervisor_audit`;
- `tracked_update`;
- `github_hygiene`; and
- `direct_supervisor_baseline`.

## Command Surface

Capture the current Codex token counter:

```powershell
agent-workbench supervisor-tokens latest
```

Write span checkpoints:

```powershell
agent-workbench supervisor-tokens checkpoint `
  --span supervisor_audit `
  --event start `
  --output runtime/supervisor_tokens/<benchmark_id>/supervisor_audit.start.json

agent-workbench supervisor-tokens checkpoint `
  --span supervisor_audit `
  --event end `
  --output runtime/supervisor_tokens/<benchmark_id>/supervisor_audit.end.json
```

Convert a checkpoint pair to a sanitized token/cost record:

```powershell
agent-workbench supervisor-tokens span `
  --start runtime/supervisor_tokens/<benchmark_id>/supervisor_audit.start.json `
  --end runtime/supervisor_tokens/<benchmark_id>/supervisor_audit.end.json `
  --output runtime/supervisor_tokens/<benchmark_id>/supervisor_audit.tokens.json `
  --project agent-delegation-lab `
  --phase p1 `
  --task-id appendix-a-opening-structure `
  --span-kind supervisor_audit
```

Validate and render the record:

```powershell
agent-workbench tokens validate `
  --input runtime/supervisor_tokens/<benchmark_id>/supervisor_audit.tokens.json

agent-workbench tokens render `
  --input runtime/supervisor_tokens/<benchmark_id>/supervisor_audit.tokens.json `
  --output runtime/supervisor_tokens/<benchmark_id>/supervisor_audit.tokens.md
```

Synthesize all span records in the ledger:

```powershell
agent-workbench supervisor-tokens synthesize `
  --input-dir runtime/supervisor_tokens/<benchmark_id> `
  --output runtime/supervisor_tokens/<benchmark_id>/summary.md
```

## Pricing Fields

Supervisor span records separate:

- `supervisor_input_tokens`: fresh input tokens after subtracting cached input;
- `supervisor_cached_input_tokens`: cached input tokens;
- `supervisor_output_tokens`: visible output tokens;
- `supervisor_reasoning_output_tokens`: reasoning output tokens, priced at the
  output-token rate unless a future billing source proves a different treatment;
- `worker_input_tokens`: local worker input tokens; and
- `worker_output_tokens`: local worker output tokens.

Local Ollama worker tokens are recorded as tokens but priced at zero cash cost.

## Public-Safety Boundary

Checkpoint files may live only under ignored runtime paths. Sanitized token
records exclude raw prompts, raw traces, provider URLs, headers, and personal
paths. The generated records store the Codex session filename as evidence but
do not copy the absolute session path.

## MP11 Next Iteration

The next MP11 benchmark iteration should use the existing
`qwen3-coder-next:latest` `appendix-a-opening-structure` worker output as the
delegated lane and run a small direct-supervisor baseline on the same page
bundle. The baseline, audit, repair, tracked-update, and GitHub hygiene work
must each be wrapped in supervisor-token checkpoints before any savings or loss
claim is made.
