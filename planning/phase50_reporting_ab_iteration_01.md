# Phase 50 Reporting A/B Iteration 01

## Purpose

This iteration tests whether worker-output reporting can be moved from paid
supervisor tokens to a local reporting worker without losing the supervision
boundary. It uses the MP11 fixed-x8 benchmark packet from `agent-delegation-lab`
and keeps raw tickets, raw outputs, provider details, and token checkpoints in
ignored runtime paths.

## Input Boundary

The sanitized packet covers the fixed MP11 x8 page definition:

- pages: 46-141;
- reused direct-supervisor structure baseline: `$1.228648`;
- local worker cash cost: zero for Ollama runs;
- existing measured delegated benchmark-operation rollup: `$0.632602`;
- source-level audit/repair: not yet allocated.

GitHub issue comments, PR updates, branch cleanup, roadmap edits, and changelog
sync are excluded from the task-economics lane.

## Local Reporting Worker Result

The local reporting-worker ticket used `gpt-oss:20b` over sanitized summaries
only. The run validated as `structured-output` after the evaluator was fixed to
match bare required section names to Markdown headings.

Observed local reporting-worker usage:

| Model | Worker input tokens | Worker output tokens | Cash cost |
| --- | ---: | ---: | ---: |
| `gpt-oss:20b` | 5746 | 1240 | `$0.000000` |

The draft correctly preserved:

- page range;
- direct baseline cost;
- measured delegated benchmark-operation cost;
- zero cash cost for local worker tokens;
- the no-final-savings boundary before source-level audit/repair; and
- the two most important anomaly audit targets.

## Supervisor Review Result

The paid supervisor accepted the local draft as a useful reporting draft, not as
a final benchmark conclusion.

Required repairs:

- Replace "potential savings" framing with "pre-audit benchmark-operation
  delta."
- Distinguish clean execution from high record yield:
  - `x8-4x24` gpt-oss is the cleanest execution lane;
  - `x8-2x48` qwen is the highest-yield clean parse lane.
- State explicitly that GitHub hygiene is excluded from task economics.

## Token Accounting Lesson

The first attempt to measure direct-supervisor reporting and delegated-report
review started both token spans from the same checkpoint. That produced
overlapping token records. The raw measured interval was real, but the two
named records must not be summed as independent costs.

Usable combined interval:

| Span interpretation | Fresh input | Cached input | Output | Reasoning output | Supervisor USD |
| --- | ---: | ---: | ---: | ---: | ---: |
| combined reporting comparison interval | 8892 | 300160 | 2485 | 596 | `$0.111223` |

This combined interval includes direct supervisor baseline writing plus
delegated-report review. It is useful as an upper bound for this reporting
comparison slice, but it does not prove the isolated cost of either lane.

Agent Workbench now fails closed on duplicate token `record_id` values and
duplicate Codex checkpoint intervals during token synthesis, so overlapping
span records cannot be silently mistaken for additive costs.

## Economics Interpretation

The reporting-worker direction remains promising because the local worker
performed the high-volume reporting draft for zero cash cost and the supervisor
only had to review/repair a compact packet.

However, the precise reporting A/B cost delta is not yet proven. The next run
must use sequential, non-overlapping checkpoints:

```text
direct_reporting_baseline.start
direct_reporting_baseline.end
delegated_reporting_review.start
delegated_reporting_review.end
```

Only then can the benchmark calculate:

```text
reporting_delta =
  direct_supervisor_reporting_cost
  - delegated_reporting_review_cost
```

The source-level audit/repair cost remains the next nondelegable task cost.

## Next Action

Run a corrected reporting A/B with separate start/end checkpoints for each lane,
then run a narrow source-level audit on the highest-value anomaly target:
`x8-4x24` with `qwen3-coder-next:latest`, part02 pages 70-93.

## Corrected AB02 Result

A corrected sequential checkpoint run was completed after the overlap lesson.
This run measured direct reporting and delegated-report review as separate
non-overlapping supervisor spans.

| Lane | Fresh input | Cached input | Output | Reasoning output | Supervisor USD |
| --- | ---: | ---: | ---: | ---: | ---: |
| direct supervisor reporting baseline | 1480 | 262912 | 775 | 28 | `$0.059842` |
| delegated `gpt-oss:20b` report review | 1396 | 265472 | 480 | 23 | `$0.055943` |

Isolated reporting delta:

```text
$0.059842 - $0.055943 = $0.003899
```

This is a small savings signal for the delegated-reporting lane, not a broad
workflow win. It excludes GitHub hygiene and does not include the still-required
source-level audit/repair span. It also assumes the reporting worker draft is
available through the scripted local-worker lane at zero cash cost.

The practical lesson is that reporting delegation probably helps most when the
reporting packet is much larger than this compact fixed-x8 summary. For small
summaries, the savings exist but are marginal.
