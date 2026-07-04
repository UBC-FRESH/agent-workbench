# Phase 45 Per-Node Token Economics

## Purpose

P45 attributes token/cash economics to graph nodes so Agent Workbench can ask
which node classes actually reduce paid supervisor token spend.

The governing cost signal remains token-priced cost, not wall-clock time.

## Record Shape

Sanitized token/cost records now support graph-node scope fields:

- `scope.graph_id`;
- `scope.node_id`; and
- `scope.node_kind`.

Records may also include a sanitized `counterfactual` block:

- `counterfactual.direct_supervisor_input_tokens`;
- `counterfactual.direct_supervisor_output_tokens`.

The counterfactual block estimates what a direct paid-supervisor implementation
would have consumed. Actual delegated usage remains in `usage`.

## Command

```powershell
python -m agent_workbench tokens graph-synthesize --input-dir templates/token_examples --output runtime/token_graph/p45_graph_synthesis.md
```

The command validates sanitized token/cost records, requires `scope.graph_id`
and `scope.node_id`, and renders a graph-node economics table with actual cost,
direct counterfactual cost, and expected net savings.

## Boundary

P45 does not ingest raw traces, prompts, provider URLs, headers, or credentials.
It also does not execute graph nodes. It only summarizes sanitized records that
the supervisor has already approved for tracking or local analysis.

## Policy Feedback

The graph synthesis output is suitable as input to future policy tuning:

- positive node classes can become stronger delegation candidates;
- negative node classes can be downgraded or split smaller; and
- unknown counterfactuals remain explicitly unknown instead of being guessed.

## Verification Notes

The example synthesis command produced two graph-node records for the
FreshForge proposal-assist pilot:

- `worker_evidence_intake`: actual cost `0.004800`, direct counterfactual
  `0.022000`, net savings `0.017200`.
- `worker_cli_proposal`: actual cost `0.006200`, direct counterfactual
  `0.027400`, net savings `0.021200`.

The combined example report shows total actual cost `0.011000`, total direct
counterfactual cost `0.049400`, and expected net savings `0.038400`.
