# Phase 63 Bounded TSA23 Recipe Pilot

## Purpose

P63 is the first bounded live-pilot candidate for the P62 document-indexing
recipe. The phase must remain budget-gated: no live worker execution is allowed
until the P59 budget record validates and the maintainer accepts the declared
cost/attempt boundary.

## Selected Pilot Slice

Pilot corpus: `bc_tsr_tsa23_public_1995_present`

Selected document: `tsa23_2012_23tsdp12`

Document type: `data_package`

Reason for selection:

- It is part of the most recent TSA23 TSR cycle represented in the tracked
  corpus registry.
- It corresponds to the information-package/data-package style of document that
  is likely to contain structured modelling metadata.
- It already has a tracked sanitized chunk manifest from the P55 TSA23 setup.
- A three-chunk slice is large enough to exercise the P62 recipe but bounded
  enough for the first budgeted pilot.

Selected chunks:

- `tsa23_2012_23tsdp12::pages_001_008`
- `tsa23_2012_23tsdp12::pages_008_015`
- `tsa23_2012_23tsdp12::pages_015_022`

Selected page span: pages 1-22, with one-page overlap between adjacent chunks.

Raw text policy: the chunk text referenced by the manifest remains under
ignored `runtime/` paths. P63 tracked files may reference chunk IDs, page
ranges, source hashes, and character counts, but must not track raw extracted
text.

## Budget Gate

Tracked budget declaration:

- `benchmarks/document_library/tsa23_tsr/p63_bounded_tsa23_recipe_pilot_budget.json`

Default budget posture:

- maximum paid supervisor cash cost: USD 10.00;
- maximum live attempts: 1;
- stop on budget exceeded;
- stop on repeated failure;
- maintainer checkpoint required before any second attempt, repair expansion,
  broader page span, or additional model family.

This is intentionally conservative. The first P63 run should answer whether the
P62 recipe can produce useful quality/protocol/economics evidence on a bounded
slice, not whether the full TSA23 corpus can be indexed.

## Planned Execution Boundary

P63.1 is safe to complete before live execution by selecting the slice and
validating the budget record.

P63.2 is the live boundary. It should not start until the maintainer accepts the
budget declaration and the live command sequence is explicit.

P63.2-P63.4 must stay at task/subtask resolution in both `ROADMAP.md` and the
child issue bodies. This is not optional checklist decoration: the live recipe
run, outcome report, and scale decision all carry paid-supervisor cost risk, so
each task needs explicit subtasks, validation steps, and stop conditions before
it can be treated as implementation-ready.

For P63, a broad instruction such as "run the recipe" is not sufficient. The
execution task must separately track runtime ticket generation, dry-run
validation, model availability, the single live attempt, ignored raw evidence,
deterministic validation, allowed repair/normalization, and stop-rule handling.
The reporting task must separately track sanitized summaries, P60 outcome
fields, fact counts, hard-vs-soft defects, line-item economics, baseline
comparison, diagnostic evidence, and planning-note updates. The scale-decision
task must record the exact follow-on gate before any new live run can be
proposed.

## Expected Outcome Fields

The pilot summary must include:

- `quality_validated_candidate`;
- `protocol_accepted_candidate`;
- `economics_usable`;
- `final_decision`;
- `rejection_reasons`;
- accepted fact count;
- repaired fact count;
- rejected fact count;
- escalated fact count; and
- line-item paid supervisor token/cash cost.

## Stop Conditions

Stop immediately when:

- the budget validator fails;
- runtime manifests reference missing or tracked raw text;
- worker output is malformed in a way that prevents deterministic validation;
- the run exceeds the declared paid-supervisor budget;
- the first live attempt hits a protocol defect that requires reticketing; or
- maintainer checkpoint is triggered.

## P63.2 Execution Result

P63.2 used the single live attempt allowed by the P59 budget record.

Runtime setup:

- generated ignored runtime ticket:
  `runtime/document_library/tsa23_tsr/p63_bounded_tsa23_recipe_pilot/tickets/p63_section_map_typed_fact_ticket.md`;
- generated ignored SDK eval manifest:
  `runtime/document_library/tsa23_tsr/p63_bounded_tsa23_recipe_pilot/manifests/p63_section_map_typed_fact_manifest.json`;
- selected model: `qwen3.6:35b-a3b-q8_0`;
- model availability check passed through the configured provider path;
- eval dry run passed before provider contact.

Live attempt result:

- harness status: `blocked`;
- harness blocker: `model-call-failure`;
- observed error kind: `provider_524_model_call_failure`;
- parseable JSONL candidate records: 40;
- malformed lines: 2;
- valid chunk records: 39;
- invalid chunk ID records: 1;
- selected chunks covered: 3 of 3;
- source quote records over the 25-word soft target: 0.

Token and cost evidence:

- paid supervisor `ticket_build` span: USD 0.362627;
- paid supervisor `worker_run_orchestration` span: USD 0.052052;
- local worker tokens: 15432 input, 10886 output, USD 0.00 cash cost;
- tracked sanitized summary:
  `benchmarks/document_library/tsa23_tsr/p63_bounded_tsa23_recipe_pilot_execution_summary.json`;
- tracked sanitized report:
  `benchmarks/document_library/tsa23_tsr/phase63_bounded_tsa23_recipe_pilot_execution_results.md`.

Decision boundary:

The result is useful diagnostic evidence, but it is not an accepted candidate
and not usable economics evidence for a successful delegated run. The declared
single-attempt stop rule is now triggered. No retry, repair expansion, broader
page span, added model family, or budget increase is allowed without maintainer
checkpoint.
