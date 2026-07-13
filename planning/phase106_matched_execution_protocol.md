# Phase 106 matched execution protocol

Phase 106 activates the already-validated P105 contract for one bounded live
comparison. It does not authorize a second document, provider change, model
installation, substantive TSA23 expansion, or release work.

## Gate order

1. Validate `benchmarks/document_library/p105_matched_benchmark_contract.json`
   with `scripts/validate_p105_matched_benchmark.py`.
2. Validate the P106 gate manifest and confirm the P104 pricing catalog resolves
   the exact paid Coordinator model and effective date.
   Launch native Codex only through `scripts/run_p106_native_codex.ps1`; this
   bootstraps the operator provider and registers the user-level role names
   `agent_workbench_ollama_supervisor` and `agent_workbench_ollama_worker`.
   Require provider-enforced structured output using the P89 required-field and
   allowed-`object_type` schema. Prompt instructions alone do not count as
   schema evidence; missing fields remain non-repairable output defects.
3. Capture a Coordinator token-span start checkpoint before the delegated lane.
4. Run one delegated attempt. Permit one repair only when the inspected result
   identifies a concrete deterministic defect. Stop if delegated bounded cost
   reaches `$0.125`, useful yield is below 90%, or a critical source-anchor
   defect is present.
5. Capture the delegated end checkpoint and inspect the complete ticket/result,
   heartbeat, archive manifest, token ledger, and provider evidence pair.
   Run `scripts/audit_p106_lane.py` against the ignored JSONL output and source
   text; its sanitized summary is the quality gate input.
6. Start the direct lane only after delegated quality and protocol gates pass.
   Use the identical source bundle, schema, audit, scoring, and repair rules.
7. Stop the complete phase at `$0.25` paid Coordinator cost, missing exact-model
   evidence, missing catalog pricing, stale-contaminated artifacts, or the
   second unsuccessful/protocol-noisy attempt in a lane.
8. Build the sanitized packet with `scripts/synthesize_p106_comparison.py` only
   after both lane summaries and catalog-backed token records validate.

## Verdict separation

- `quality_validated_candidate`: deterministic record and source-anchor audit
  accepts the lane output.
- `protocol_accepted_candidate`: authority, ticket, role, stop, and archive
  evidence obey the delegated/direct contract.
- `economics_usable`: paid Coordinator checkpoints, token classes, exact model,
  catalog source, effective date, and bounded cost are all inspectable.

Raw prompts, source text, provider details, transcripts, and model outputs stay
under ignored `runtime/` or `tmp/` paths. Only sanitized aggregate evidence may
be promoted into tracked planning or benchmark files.
