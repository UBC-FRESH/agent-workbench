# P58-P64 Roadmap Tranche: Consolidation Before More Live Runs

## Summary

This tranche responds to the P57 overrun: local Copilot/Ollama supervision is
promising, but paid Codex coordination can erase the value if experiments keep
running after the learning signal is already visible. The next work therefore
consolidates evidence, enforces budget gates, and packages the successful
pre-materialized local-supervisor workflow before another large live benchmark.

Default posture: P55, P56, and P57 remain active until reconciled. No new large
Copilot/Ollama run should happen until the P58-P60 gates are implemented.

## Phase Sequence

| Phase | Purpose | Live worker runs |
| --- | --- | --- |
| P58 | Reconcile P55-P57 evidence and active-phase state | No |
| P59 | Enforce paid-supervisor budget gates and stop rules | No |
| P60 | Split quality, protocol, and economics outcomes | No |
| P61 | Package the pre-materialized local-supervisor workflow | Deferred |
| P62 | Define a reusable document-indexing recipe | No |
| P63 | Run one bounded TSA23 recipe pilot | Yes, only with P59 budget gate |
| P64 | Document deployment/operator environment | No |

## Design Commitments

- Treat P57's high-cost overrun as tuition already paid, not a normal iteration
  pattern.
- Do not chase perfect acceptance when a run has already produced the learning
  signal needed for the next engineering decision.
- Keep deterministic setup coordinator-owned by default.
- Let local supervisors own bounded audit, repair, validation, and compact
  reporting.
- Make deterministic validators the source of truth for artifact validity.
- Use FreshForge-compatible graphs as the structural workflow representation.
- Keep raw prompts, raw worker outputs, provider details, and raw PDF text in
  ignored runtime paths.

## Close/Defer Logic For Active Phases

P55 can close or defer once the current indexing evidence is normalized and the
next document-indexing work is moved into the P62/P63 recipe path.

P56 can close once authority signals, coordinator-review signals, and
nondelegable closeout surfaces are explicit in contracts and graph metadata.

P57 can close once the subagent/local-supervisor evidence is reconciled, the
pre-materialized workflow pattern is packaged or explicitly handed to P61, and
all future live-run expectations are moved behind P59 budget gates.

## Immediate Implementation Order

1. Implement P58 first using existing tracked and ignored evidence only.
2. Implement P59 budget declarations before any new live economics run.
3. Implement P60 outcome semantics so evidence summaries stop flattening
   useful-but-noisy runs into generic failure.
4. Package the stable local-supervisor path in P61.
5. Resume document-indexing work through P62/P63 only after the above gates are
   in place.
