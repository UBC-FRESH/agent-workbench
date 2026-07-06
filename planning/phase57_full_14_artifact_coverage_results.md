# P57 Full 14-Artifact Coverage Results

## Summary

Completed all three split batches from the P57 graph batch manifest using pre-materialized Copilot supervisor tickets. The full result combines the prior split_01+split_02 10-artifact package with split_03 v1 for 14 total source artifacts.

## Economics

- Total paid coordinator cost: `$0.190046`
- Paid coordinator cost per source artifact: `$0.013575`
- Source artifact count: `14`
- Fresh supervisor input tokens: `3778`
- Cached supervisor input tokens: `929152`
- Supervisor output tokens: `1488`
- Total Codex token delta: `934418`
- Local Copilot/Ollama cash cost: `$0.00`

## Behavior

- All child packages matched expected model `qwen3.6:35b-a3b-bf16`.
- All child packages used pre-materialized audit tickets.
- Copilot-side materializer command count was `0` across full coverage.
- Subagent tool use was observed in all child packages.
- All deterministic validators passed.

## Interpretation

Full 14-artifact coverage stayed accepted, but the summed per-artifact cost is higher than the 10-artifact package because split_03 was measured as a separate external span. The next optimization target is a single batch-level supervisor ticket or a single external span covering all three splits in one uninterrupted run.
