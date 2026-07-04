# P50 Experiment Observation Records

Agent Workbench now needs persistent experiment observations, not just local
run summaries. The goal is to collect enough comparable records to tune default
delegation behavior, set guardrails, and eventually support hyperparameter or
policy optimization.

## Record Unit

One experiment observation represents one model/protocol/task-scale run.

The record captures:

- experiment series and project phase;
- task family, scale factor, page/word/character size;
- model and provider class;
- protocol parameters such as authority level, timeout, and audit strategy;
- outcome counts;
- worker token counts;
- supervisor cost;
- direct-baseline or counterfactual cost;
- net savings; and
- links to sanitized evidence, token records, and planning notes.

Raw inputs, raw worker outputs, raw traces, provider URLs, headers, credentials,
and personal paths remain excluded.

## Command Surface

Validate a record:

```powershell
agent-workbench experiments validate --input <record.experiment.json>
```

Render a record:

```powershell
agent-workbench experiments render `
  --input <record.experiment.json> `
  --output <record.experiment.md>
```

Synthesize a series:

```powershell
agent-workbench experiments synthesize `
  --input-dir <experiment-record-dir> `
  --output <series-summary.md>
```

## Immediate Use

The MP11 scale sequence should write one observation per scale factor:

- x2;
- x4;
- x8; and
- x16.

The first sequence should use long local-worker timeouts and should not classify
a run as failed unless there is concrete stall or provider-failure evidence.

The useful output series is the tuple:

```text
(scale_factor, input_pages, input_words, worker_input_tokens,
 worker_output_tokens, records_produced, parse_status,
 supervisor_cost_usd, direct_baseline_cost_usd, net_savings_usd,
 benefit_cost_ratio)
```

This is intentionally compact enough to mine later.
