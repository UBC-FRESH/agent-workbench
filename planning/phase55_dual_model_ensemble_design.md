# Phase 55 Dual-Model Typed Fact Ensemble Design

P55's earlier extraction waves tested broad structure-record generation. The
next useful experiment should test a different architecture: two local models
produce independent typed fact JSON candidates from the same source chunks, a
deterministic comparison step identifies field-level agreement/disagreement,
and a later verifier reviews only disagreements, missing values, and weak
provenance.

## Why This Is Different

The current `structure_chunk` workflow asks a model to discover interesting
records. That is useful for section-map behavior, but it leaves too much room
for vague records, inconsistent field names, and hidden omissions.

The ensemble workflow asks each model to populate the same versioned field set.
That makes agreement, disagreement, missing evidence, and repair burden
measurable.

## Candidate Workflow

1. Extract text from PDF pages into ignored runtime chunks.
2. Select a bounded source bundle from one document.
3. Run candidate extraction with `qwen3.6:35b-a3b-bf16`.
4. Run candidate extraction with a second document-understanding model.
5. Parse both strict JSON candidates.
6. Compare field-by-field:
   - both found and normalized value matches;
   - both missing;
   - one found and one missing;
   - both found but value/unit/page/provenance differs;
   - malformed or unparseable candidate.
7. Send only disagreements, missing-high-priority fields, and weak-provenance
   fields to a verifier model.
8. Supervisor audits a compact final packet instead of rereading every raw
   candidate field.

## Verifier And Repair Role Split

Wave 8 showed that the role name "verifier" is too broad. There are at least
three different workflow nodes:

- **Strict verifier:** returns machine-parseable verdict JSON for disputed
  fields. This node is schema-sensitive and should be evaluated on exact field
  coverage, parseability, quote discipline, and chunk-ID validity.
- **Validation critic:** reviews a failed or suspicious candidate/verifier
  output and prepares concise repair instructions. This node may benefit from
  explicit reasoning ability, but its output should be treated as instructions,
  not as the final machine artifact.
- **Repair executor:** applies repair instructions to produce strict JSON. This
  is closer to a coding/formatting task and may be better suited to a
  coding-tuned model such as `qwen3-coder-next:latest`.

The first DeepSeek-R1 Wave 8 test is evidence for this split. DeepSeek-R1 did
not reliably emit the strict verifier schema: one attempt used verdict labels
as field keys, and the stricter skeleton rerun produced malformed JSON. That
does not rule it out as a validation critic; it argues against using it as the
final strict JSON writer without a repair executor downstream.

## Current Model Reality

The preferred target pairing is `qwen3.6:35b-a3b-bf16` plus a GLM 5.2-family
document model. The current local Ollama catalog exposes Qwen3.6 BF16 but does
not expose a GLM model. Until GLM is installed, P55 uses `gpt-oss:120b` as the
installed large local comparison model for the first ensemble harness test.

The battery records both:

- `wave7_ensemble_secondary_model`: the currently runnable second model;
- `wave7_planned_secondary_model`: the intended GLM-family swap-in.

Current verifier/repair candidates:

- `qwen3.6:35b-a3b-bf16`: best current strict verifier candidate from Wave 8;
- `deepseek-r1:latest`: validation critic candidate for repair-instruction
  generation;
- `qwen3-coder-next:latest`: repair executor candidate for strict JSON repair.

## First Typed Field Set

The first typed candidate schema is deliberately small. It is not the final TSR
metadata schema. It exists to test candidate generation, comparison, and
provenance discipline.

Fields:

- `tsa_name`
- `tsa_number`
- `document_title`
- `determination_year`
- `aac_value`
- `aac_units`
- `aac_effective_date`
- `thlb_area`
- `total_area`
- `inventory_reference_year`
- `base_case_harvest_forecast`
- `sensitivity_cases`
- `major_land_base_constraints`
- `major_management_assumptions`
- `decision_rationale`

Each field must include `status`, `value`, `units`, `page_anchor`, `chunk_id`,
`source_quote`, and `confidence`.

## Public-Safety Boundary

Raw source chunks, candidate JSON, source quotes, and provider details remain
under ignored `runtime/` paths. Tracked outputs may record only sanitized
aggregate metrics and comparison classifications unless a maintainer
explicitly approves publishing selected public source quotes.

## Success Signal

The first ensemble run is useful if:

- both candidate JSON objects parse;
- field coverage can be compared without supervisor rereading raw outputs;
- disagreements are localized enough to form a compact verifier ticket;
- the workflow shows whether dual local workers reduce paid supervisor audit
  scope compared with a single broad extraction pass.

## Expected Failure Modes

- One model returns prose or JSONL instead of one JSON object.
- Models agree on a wrong value because the source bundle lacks enough context.
- Models disagree because one inferred from outside knowledge.
- Source quotes exceed the quote-length contract.
- The comparison step hides important differences by over-normalizing values.

These failures are still useful if they are captured as structured evidence.
