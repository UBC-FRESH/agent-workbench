# Phase 29 Repeat-Run And Model Comparison

Phase 29 adds a local comparison report for existing same-ticket evaluation
summaries. It does not run new provider-backed benchmarks or rank models
broadly.

## Command

```powershell
agent-workbench compare eval `
  --input runtime/agent_jobs/p8_sdk_no_tool_eval/summary.json `
  --input runtime/agent_jobs/p9_structured_doc_eval/summary.json `
  --output runtime/model_comparison/report.md
```

The report includes:

- classification counts by evaluation and model;
- per-model consistency across repeats;
- per-run status, blocker, classification, and result file; and
- a supervisor-use boundary that limits conclusions to the supplied ticket
  family and summaries.

## Boundary

This command summarizes evidence that already exists. It does not install
models, select a best model, run new probes, or promote broad model rankings.
