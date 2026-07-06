# P57 Multi-Split Scale Probe Results

## Summary

Ran split_01 v6 and split_02 v15 as a 10-artifact pre-materialized Copilot supervisor package under one external Codex token span. Both child graph runs accepted after deterministic verification.

## Economics

- Total paid coordinator cost: `$0.109171`
- Paid coordinator cost per source artifact: `$0.010917`
- Source artifact count: `10`
- Fresh supervisor input tokens: `2100`
- Cached supervisor input tokens: `525952`
- Supervisor output tokens: `961`
- Total Codex token delta: `529013`
- Local Copilot/Ollama cash cost: `$0.00`

## Behavior

- Both child runs matched expected model `qwen3.6:35b-a3b-bf16`.
- Both child runs used pre-materialized audit tickets.
- Copilot-side materializer command count was `0` across the batch.
- Both child runs observed the subagent tool.
- Split_02 needed inline JSON repair commands against the assigned runtime report; the bridge now classifies those as benign when they are bounded to allowed runtime report paths.

## Interpretation

The 10-artifact pre-materialized package reduced paid coordinator cost per source artifact below the previous five-artifact v5 result, which supports scaling this coordinator-owned setup boundary. The next test should either add split_03 for full 14-artifact coverage or move from sequential child tickets to a single batch-level supervisor ticket.
