# Supervision Rubric Goal Programming

## Context

The early P55 supervisor A/B tests treated quote length as a hard failure when
`source_quote` exceeded the 25-word target. That made quote-length defects
dominate result reporting even when the underlying semantic extraction was
otherwise useful. This is too brittle for document metadata extraction.

Semantic knowledge extraction and structured index building are inherently
messy. The benchmark needs to distinguish hard trust failures from soft
objective misses.

## Scoring Direction

Future supervisor benchmarks should use a fuzzy multi-objective scoring rubric:

- hard constraints for defects that break trust or machine usability;
- soft penalty terms for preference misses and mild formatting drift;
- explicit weights so the relative importance of defects is visible and
  tunable; and
- side-by-side lane scores so Codex, Copilot/Ollama, SDK workers, and future
  workflow-graph supervisors can be compared without collapsing every issue
  into pass/fail.

## Hard Constraint Candidates

These should behave like near-hard constraints by carrying very large penalties:

- invalid JSON or unparsable output;
- missing required top-level fields;
- missing required task fields;
- invalid action/status labels;
- value type mismatch for a claimed repaired/found field;
- invalid source chunk ID when a source anchor is claimed;
- `found` status with a null value;
- invented source anchors or source quotes not traceable to supplied text, when
  that can be checked;
- unauthorized file edits, GitHub mutations, or tool use outside the ticket
  contract.

## Soft Objective Candidates

These should be scored as objective-function terms, not binary task failure:

- quote length above the target;
- quote missing for fields intentionally escalated to `needs_supervisor`;
- confidence lower than desired;
- extra supervisor escalations where a competent local supervisor might have
  made a clean decision;
- repaired-but-not-ideal evidence packaging;
- verbose reporting when the expected artifact still exists and parses.

## Quote Length Penalty

Quote length should use a soft exponential penalty around the target rather
than a hard threshold. One practical starting point:

```text
if words <= target:
    penalty = 0
else:
    excess = words - target
    penalty = weight * (exp(excess / scale) - 1)
```

Suggested defaults:

- target: `25` words;
- scale: `10`;
- weight: `1.0`.

This makes 26-30 words a small nuisance, not a catastrophic failure, while
quotes that balloon into paragraph excerpts are penalized quickly.

## Initial Weight Proposal

| Term | Weight | Rationale |
| --- | ---: | --- |
| parse failure | 1000 | no machine-readable artifact |
| missing required field | 200 | incomplete mission |
| invalid action/status | 100 | schema contract violation |
| value type mismatch | 120 | downstream JSON consumer risk |
| found/null contradiction | 120 | semantic contradiction |
| invalid chunk ID | 80 | source anchoring risk |
| missing chunk ID on found field | 30 | weaker verification surface |
| missing quote on found field | 20 | weaker verification surface |
| needs-supervisor escalation | 15 | acceptable but reduces autonomy |
| low confidence repaired field | 10 | weaker local-supervisor result |
| model provenance mismatch | 25 | self-reported model identity disagrees with bridge evidence |
| quote length excess | exponential | soft packaging defect |

The weights are intentionally editable. They represent current judgement, not a
settled scientific calibration.

## Model Provenance

Free-supervisor outputs must not be trusted as the source of truth for model
identity. In the P55 repair retry, the bridge observed
`qwen3.6:35b-a3b-bf16`, while the model wrote `qwen3-coder-next:latest` into
its JSON result. That did not invalidate the extraction content, but it did
prove that model self-reporting is unreliable enough to score separately.

For future Copilot/Ollama supervisor benchmarks:

- bridge-observed model identity is authoritative;
- self-reported model identity is recorded as diagnostic evidence only;
- mismatch is a soft provenance penalty unless the task itself depends on the
  model identity field; and
- model-comparison claims must use the bridge-observed model, not the JSON
  self-report.

## Benchmark Interpretation

The question is not whether a free local supervisor is as strong as Codex on a
single field. The real question is whether tightly scoped roles can keep a free
Ollama-backed Copilot agent close enough to target behaviour that it can act as
a shop foreman for larger chunks of UBC-FRESH work.

The useful success condition is:

- the free supervisor stays on task;
- completes the mission under the ticket contract;
- produces parseable artifacts;
- keeps hard-constraint penalties low;
- produces a tolerable soft-penalty score; and
- reduces paid supervisor involvement enough to matter at roadmap-phase scale.

## Next Test Shape

The next A/B test should be larger than the four-field Wave 10 repair prepass.
It should score both lanes with this rubric and report:

- total penalty;
- score out of 100;
- hard-constraint penalty;
- soft-objective penalty;
- per-field penalty terms;
- paid Codex supervisor token/cash line items;
- Copilot/Ollama supervisor cash cost as zero;
- whether the Copilot supervisor process remained contract-compliant; and
- whether quality is good enough to justify a repair/self-audit loop rather
  than immediate paid-supervisor intervention.
