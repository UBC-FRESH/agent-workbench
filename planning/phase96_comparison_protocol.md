# Phase 96 Comparison Protocol

This document defines the boundary, rules, and protocol for a recipe-stability
model-lane comparison in Phase 96 (Yield And Audit-Cost Model Comparison).

**Status:** draft — to be reviewed before P96.3 run execution.

## Framing: Recipe-Stability Confirmation, Not Deep Ranking

Per the P87-P92 strategic arc and the key Advisor insight from 2026-07-11, this
comparison is **not** a deep model-lane ranking or a broad evaluation of model
quality. It is a bounded recipe-stability confirmation: does swapping one
component of the indexing recipe (model lane) produce a materially different
yield or audit cost when run through the exact same ticket shapes, corpus slice,
and validation protocol?

If the strategic arc were wrong and profile-evidence-review batteries are the
right approach, P96 will demonstrate that only if the yield difference is large
enough to justify sustained battery investment. In practice the comparison asks:
"Is the current recipe stable, or does another lane produce a clear improvement?"

## Strategic Arc Constraints (from p87_p92)

1. **ROI is the north star.** The metric of success is `reduce paid supervisor
   cost per useful, source-backed unit of real project work`. Any comparison must
   answer this question, not just "which model gets more accepted records?"

2. **Profile-batteries are support evidence only.** They are not the product lane.
   A P96 comparison that becomes a profile-evidence-review-in-disguise violates
   the arc's pivot decision.

3. **P93-P96 is the scale and index-usability tranche.** P96 sits inside this
   tranche: it scales understanding (which lane works best) to enable the
   index-retrieval surface built in P95 to become reliable for downstream agents.

4. **No deep model-lane ranking.** Only compare lanes where they directly affect
   accepted-record yield or supervisor audit cost. Pure latency, throughput, or
   quality-appeal claims are out of scope.

## Comparison Boundary

### What IS in scope

- **Accepted-record yield difference:** raw count and percentage of accepted
  records per lane on identical input.
- **Repairable-record yield difference:** raw count and percentage of repairable
  records per lane (records that failed initial review but could be repaired with
  known fixes).
- **Supervisor audit cost per lane:** measured in auditor-token spans for reviewing
  the output of each lane on identical input.
- **Rejection rate difference:** raw count and percentage of rejected records per
  lane.

### What is NOT in scope

- **Pure latency or throughput measurements.** If one model runs faster but
  produces fewer accepted records, P96 does not decide for it.
- **Broad qualitative quality assessments.** Human-judged aesthetics, prose
  quality, or "which reads better" are out of scope unless they map to a
  concrete yield/repair/audit-cost metric.
- **Multi-document comparisons in the first run.** P96.3 targets exactly one
  document and one chunk set. Scale only after the single-run verdict is
  documented and accepted.
- **Model training or fine-tuning analysis.** P96 compares existing model
  versions available on the configured worker host, not training hypotheses.

## Model Identity Verification Requirement

Per `planning/delegation_policy.md` § **Model Attribution Risk** (added 2026-07-11):

- The `model:` frontmatter in `.agent.md` files is **not** proof of model
  selection for local/self-hosted agents.
- A P96 comparison run **must** independently verify which model produced each
  lane's output via:
  - Persisted session evidence (event logs, tool invocations), or
  - A Copilot Chat `ollama` provider model-list snapshot from VS Code showing
    the expected model in the configured remote host inventory.
- If model identity cannot be independently verified for a lane, that lane's
  data must be marked `model_unverified` and excluded from the final verdict.

In this workspace, Ollama is remote via the VS Code extension. Do not rely on
local `localhost:11434` probes from this terminal session.

This is non-negotiable: without independent model verification, P96 evidence
becomes unverifiable and any verdict is meaningless.

## Yield Measurement Protocol

### Input Specification

- Exactly **one document** selected from a public corpus already in the
  `benchmarks/document_library/` path.
- The document must be one that has existing records in the promoted index or
  equivalent (i.e., already processed by P87-P94 recipe).
- Chunk boundaries must match the indexing recipe's chunking strategy from P89.

### Output Classification Per Record

Each record produced by a lane is classified into one of three buckets:

| Category | Definition | Measurement |
| --- | --- | --- |
| `accepted` | Passed initial review without repair needed | Count + percentage of total processed |
| `repairable` | Failed initial review but has a deterministic or near-deterministic fix path | Count + percentage of total processed |
| `rejected` | Failed and no clear repair path exists | Count + percentage of total processed |

### Yield Metrics Computed Per Lane

```
yield_accepted = accepted_count / total_processed
yield_repairable = repairable_count / total_processed
yield_rejected = rejected_count / total_processed
yield_total_useful = yield_accepted + yield_repairable
```

## Audit-Cost Measurement Protocol

### Supervisor Token Checkpoints

For each lane, the supervisor must measure:

- **Input tokens consumed** by the supervisor during review (reading candidate records).
- **Output tokens produced** by the supervisor during review (decisions, repairs, rejections).
- **Total auditor spans:** total token cost across all supervisor subtasks that touch this lane's output.

### Audit-Cost Metrics Computed Per Lane

```
audit_cost_per_accepted = total_supervisor_tokens / accepted_count
audit_cost_per_useful = total_supervisor_tokens / (accepted_count + repairable_count)
```

## Verdict Categories and Thresholds

After collecting yield and audit-cost data for both lanes, the verdict falls into
one of three categories:

### Category 1: Recommend Same Lane

- The baseline lane has **equal or better** accepted-record yield.
- The baseline lane has **equal or lower** audit cost per useful record.
- No clear improvement path from switching lanes.

**Implication:** Keep the current recipe. Do not invest in migrating to the
candidate lane unless a future comparison identifies a different variable (ticket
shape, corpus slice) that favors it.

### Category 2: Switch Lane

- The candidate lane has **statistically meaningful higher accepted-record yield**
  AND **equal or lower audit cost per useful record**.
- "Statistically meaningful" means the difference exceeds 5 percentage points in
  accepted-record yield OR a 15% reduction in audit cost per useful record —
  whichever is harder to dismiss as noise for the document size involved.

**Implication:** Adopt the candidate lane for P97+ indexing work. Document the
migration decision and update relevant recipe files before proceeding.

### Category 3: Insufficient Evidence

- The yield difference is too small (below the thresholds above) OR the audit-cost
  data is too sparse to draw a conclusion OR model identity was unverified for
  one lane.

**Implication:** Close P96 as diagnostic-only. Do **not** authorize broad scale-up
of either lane for production indexing without further evidence. The phase still
produces value by confirming the comparison protocol works and establishing a
baseline dataset for future runs.

## Outcome Semantics (P60 Framework)

Each comparison run must produce artifacts classified into three P60 outcome
semantics:

| Category | Definition | What It Means For P96 |
| --- | --- | --- |
| `quality_validated_candidate` | The lane's output passes the classification schema and yield measurement rules | Lane produced records that can be measured |
| `protocol_accepted_candidate` | The run obeyed all boundary, verification, and evidence requirements | Run was clean — no confounding variables |
| `economics_usable` | Yield + audit-cost data are captured at correct boundaries with verified model identity | Data is fit for verdict decision |

All three must be true for a verdict to carry weight. If only one or two are met,
the result moves to "insufficient evidence" regardless of yield differences.

## Run Manifest Requirements

Before P96.3 executes, a run manifest must be created with all critical variables
fixed and declared:

```yaml
phase: p96
run_id: <unique-id>
baseline_lane:
  model_name: qwen3.6:35b-a3b-bf16   # example — replace with actual
  verification_method: copilot_chat_ollama_provider_list_snapshot
candidate_lane:
  model_name: <to-be-selected>        # P96.2 fills this in
  verification_method: copilot_chat_ollama_provider_list_snapshot
corpus_document: <document-id>         # e.g., tsa23_2012_23tsdp12
chunk_boundaries: <matching-recipe>    # from P89 recipe
ticket_shape: <exact-ticket-grammar>   # identical for both lanes
yield_threshold_pct: 5                 # minimum meaningful difference
audit_cost_threshold_pct: 15           # minimum meaningful reduction
expected_output_format: yield_per_lane + audit_cost_per_lane + verdict
```

## Next Steps

| Task | Issue | Owner | Status |
| --- | --- | --- | --- |
| P96.1 Define boundary and protocol | #586 | This document | Complete |
| P96.2 Select model lane to compare | #587 | Supervisor worker | Pending |
| P96.3 Run bounded comparison | #588 | Supervisor worker | Pending |
| P96.4 Render verdict | #589 | Coordinator | Pending |

## References

- `planning/p87_p92_real_project_roi_roadmap.md` — Strategic arc and evidence base
- `planning/delegation_policy.md` § Model Attribution Risk — Model identity verification rules
- `ROADMAP.md` — Phase 96 section with issue links and status
- P60 outcome semantics (from `planning/phase0_governance_notes.md`)
