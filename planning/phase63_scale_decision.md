# Phase 63 Scale Decision Draft

## Decision Status

Status: pending maintainer acceptance

Recommended decision: pause the P63 live TSA23 recipe lane and adjust the
workflow before any repeat or scale-up.

Do not scale to a larger page range, additional TSA23 documents, additional
model families, or a direct-supervisor baseline from the current P63 state.

## Evidence Base

P63.2 executed the single live attempt allowed by the budget gate.

P63.3 converted that runtime evidence into tracked sanitized summaries:

- `benchmarks/document_library/tsa23_tsr/p63_bounded_tsa23_recipe_pilot_execution_summary.json`
- `benchmarks/document_library/tsa23_tsr/phase63_bounded_tsa23_recipe_pilot_execution_results.md`

Observed candidate signal:

- 40 parseable candidate records;
- all 3 selected chunks covered;
- 39 valid chunk records;
- 1 invalid chunk-ID record;
- 2 malformed or truncated JSONL lines;
- no source quotes over the 25-word soft target.

Observed blocker:

- harness status: `blocked`;
- harness blocker: `model-call-failure`;
- observed error kind: `provider_524_model_call_failure`;
- protocol noise: preamble plus fenced JSON output despite JSONL-only ticket.

Outcome semantics:

- `quality_validated_candidate`: false;
- `protocol_accepted_candidate`: false;
- `economics_usable`: false;
- `final_decision`: `stop_after_single_attempt_model_call_failure`.

Fact review counts:

- accepted: 0;
- repaired: 0;
- rejected: 1;
- escalated: 0;
- unresolved: 39.

Measured cost:

- paid supervisor cost across four captured spans: USD 0.811920;
- local worker cost: USD 0.00;
- direct-supervisor baseline: not run;
- cost comparison decision: `not_comparable`.

## Maintainer-Facing Value

The pilot did produce value:

- It proved the P62 recipe can be instantiated into a reproducible ignored
  runtime ticket and SDK eval manifest from tracked public-safe inputs.
- It showed that the Qwen3.6 Q8 local model can extract plausible, source-
  anchored TSA23 structure and typed facts from a 22-page information-package
  slice.
- It exposed concrete defects in the current execution lane before scaling:
  provider/proxy 524 failure, protocol-noisy fenced output, invalid chunk-ID
  generation, and incomplete/truncated JSONL.
- It measured the paid-supervisor cost of setup, orchestration, reporting, and
  tracked update separately enough to support future workflow tuning.

The pilot did not produce enough value to justify scale-up yet:

- No candidate records are accepted because no source audit or repair pass was
  run after the stop rule.
- Economics evidence is diagnostic rather than a win/loss comparison because
  the run failed before a quality-valid delegated candidate existed.
- Running a direct paid-supervisor baseline now would answer a different
  question and would burn paid tokens after the declared maintainer checkpoint.

## Recommended Next Move

Pause P63 live execution and use the result to adjust the recipe before any
repeat.

The next live repeat, if approved, should change the execution shape rather than
rerun the same large all-in-one ticket:

- split the 22-page slice into smaller section-level tickets;
- reduce maximum response size per worker call;
- make strict JSONL validation/repair a deterministic postprocessor or a
  separate bounded local repair node;
- tighten chunk-ID handling by supplying an explicit enum and rejecting unknown
  IDs before any source audit;
- test whether the provider 524 is caused by response length, proxy timeout,
  SDK transport, or model runtime behavior before larger document-indexing
  runs;
- keep the direct-supervisor baseline deferred until there is a quality-valid
  delegated candidate worth comparing.

## Follow-On Gate

No follow-on live run is authorized by P63 as currently executed.

A future repeat must have a new explicit gate with:

- phase or task identifier: a new issue or explicitly approved continuation;
- budget record: new or amended P59 budget declaration;
- maximum live attempts: 1 unless the maintainer explicitly approves more;
- model lane: one named model and provider path;
- document slice: same `tsa23_2012_23tsdp12` pages 1-22 unless otherwise
  approved;
- ticket shape: smaller section-level tickets, not the same all-in-one ticket;
- stop rule: stop on provider failure, malformed output, invalid chunk IDs, or
  missing token spans;
- acceptance target: at least one quality-valid candidate packet before any
  direct-supervisor baseline is run.

## P63 Closeout Boundary

P63 should not merge or close until the maintainer accepts one of these options:

- pause the lane and merge P63 as diagnostic evidence;
- adjust the recipe and open a follow-on phase;
- repeat the bounded slice under a new explicit budget gate; or
- abandon this TSA23 indexing lane for now.
