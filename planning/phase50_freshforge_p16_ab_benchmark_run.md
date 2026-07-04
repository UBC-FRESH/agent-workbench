# Phase 50 FreshForge P16 A/B Benchmark Run

P50 is the first real phase-scale benchmark run. It stays open across multiple
iterations until the maintainer explicitly says it is done.

## Benchmark Target

- target repo: `UBC-FRESH/freshforge`
- target phase: FreshForge P16, provider result and validation evidence
  conventions
- direct lane worktree: `../freshforge-benchmark-p16-direct`
- delegated lane worktree: `../freshforge-benchmark-p16-delegated`
- benchmark record:
  `templates/benchmarks/freshforge_p16_phase_ab_benchmark.json`

## Iteration Policy

The direct-supervisor lane runs first. The supervisor performs the actual
FreshForge P16 implementation in the direct lane and records:

- files changed;
- commands run;
- verification results;
- GitHub issue or PR URLs touched;
- blockers or rework;
- paid supervisor token usage when available from Codex goal/report evidence.

The delegated lane runs later from the same recorded start commit using Agent
Workbench graph/delegation surfaces. It should not merely replay the direct lane
by hand.

## Current Iteration

Iteration 1 has produced one direct-supervisor FreshForge P16 branch and one
delegated Agent Workbench FreshForge P16 branch from the same start commit. The
phase remains open so the maintainer can inspect the outputs, compare the design
choices, and decide the next iteration.

P50 should not close after Iteration 1.

## Iteration 1 Direct-Lane Evidence

FreshForge direct lane:

- worktree: `../freshforge-benchmark-p16-direct`
- branch: `benchmark/p16-direct-supervisor`
- commit: `0ebf8a2` (`P16 add provider evidence records`)
- FreshForge parent issue: #113
- FreshForge child issues touched: #114, #115, #116, #117

Implemented:

- added `ProviderEvidence` as a generic optional provider-reported evidence
  record;
- added optional evidence tuples to `ProviderRunResult` and `NodeRunResult`;
- threaded provider evidence through `run_workflow(...)`;
- added evidence counts and compact evidence entries to `NodeRunSummary`;
- verified workflow evidence manifests include provider evidence through full
  run records and summaries;
- exported `ProviderEvidence` from the public package surface;
- updated provider and workflow-runner docs;
- updated FreshForge roadmap and changelog for P16 activation.

Verification:

- `python -m pip install -e .[dev]` refreshed the shared editable environment
  for the direct benchmark worktree;
- `python -m pytest tests/test_records.py tests/test_execution.py tests/test_evidence.py`
  passed with 13 tests;
- `python -m pytest` passed with 97 tests;
- `python -m ruff check .` passed;
- `sphinx-build -b html docs _build/html -W` passed;
- `python -m build` passed;
- `python -m twine check dist/*` passed;
- `git diff --check` passed;
- public-safety scan found only existing policy text;
- FreshForge `main` remained clean.

Token accounting note:

- The active Codex goal token counter reported 129,063 tokens after opening P50
  and completing this first direct-lane iteration.
- This is an interim P50 supervisor-token observation, not a final isolated
  direct-lane benchmark score. It includes P50 setup and the first implementation
  pass.

## Iteration 1 Delegated-Lane Evidence

FreshForge delegated lane:

- worktree: `../freshforge-benchmark-p16-delegated`
- branch: `benchmark/p16-agent-workbench-delegated`
- start commit: `5bce95b` (`P15 add durable evidence manifests (#112)`)
- commit: `c781775` (`P16 add delegated provider evidence mapping`)
- FreshForge parent issue: #113
- FreshForge child issues touched: #114, #115, #116, #117

Worker tickets:

- `p16-provider-evidence-review`
  - model: `qwen3-coder-next:latest`
  - classification: `structured-output`
  - input tokens: 2265
  - output tokens: 300
  - useful signal: prefer an optional opaque provider-owned evidence mapping,
    keyed by evidence type or URI, with FreshForge preserving the JSON shape but
    not interpreting domain semantics.
- `p16-fixture-evidence-proposal`
  - model: `qwen3-coder-next:latest`
  - classification: `missing-section`
  - input tokens: 2200
  - output tokens: 332
  - useful signal: proposed fixture-oriented checks for round-trip preservation,
    backward compatibility, and downstream documentation, but missed the
    required `## Verification` section.

Delegated worker-token subtotal:

- worker input tokens: 4465
- worker output tokens: 632
- worker cash cost: zero under the local Ollama lane

Implemented:

- added optional `evidence` mappings to `ProviderRunResult` and
  `NodeRunResult`;
- threaded provider evidence through `run_workflow(...)`;
- added evidence counts and compact evidence mappings to `NodeRunSummary`;
- verified workflow evidence manifests preserve the provider-owned evidence
  mapping;
- updated provider and workflow-runner docs around generic provider-owned
  evidence;
- updated FreshForge roadmap and changelog for the delegated benchmark branch.

Verification:

- `python -m pip install -e .[dev]` refreshed the shared editable environment
  for the delegated benchmark worktree;
- `python -m pytest tests/test_records.py tests/test_execution.py tests/test_evidence.py`
  passed with 12 tests;
- `python -m pytest` passed with 96 tests;
- `python -m ruff check .` passed;
- `sphinx-build -b html docs _build/html -W` passed;
- `python -m build` passed;
- `python -m twine check dist/*` passed;
- `git diff --check` passed;
- public-safety scan found only existing policy text.

Design contrast against the direct lane:

- The direct lane introduced a typed `ProviderEvidence` dataclass and exported
  it from the public package surface.
- The delegated lane followed the strongest worker recommendation more closely:
  keep provider evidence as an opaque JSON-compatible mapping and avoid adding a
  new public record class until downstream usage proves the shape is stable.
- Both lanes reached full FreshForge verification, so the next comparison should
  focus on API quality, downstream ergonomics, migration risk, and paid
  supervisor-token burden rather than pass/fail validation alone.

Token accounting note:

- The active Codex goal token counter reported 278,526 total tokens after the
  delegated implementation was verified and pushed.
- This total is not yet a clean delegated-lane-only score because it includes
  P50 setup, direct-lane implementation, delegated worker orchestration,
  delegated implementation, and this evidence update.
- The immediate instrumentation gap is supervisor-lane token segmentation: P50
  can currently observe the goal-level total, but it cannot yet attribute paid
  supervisor tokens cleanly to direct implementation versus delegated
  orchestration and cleanup.

## Iteration 1 A/B Comparison

Both lanes started from FreshForge commit `5bce95b`, produced substantive P16
code/docs/tests, and passed the same standard verification gates. This makes the
first comparison about design quality and delegation economics, not about
whether one lane failed basic validation.

Implementation footprint:

| Measure | Direct lane | Delegated lane |
| --- | ---: | ---: |
| Files changed | 10 | 9 |
| Insertions | 211 | 140 |
| Deletions | 4 | 4 |
| New public record class | yes | no |
| New public package export | yes | no |
| Full verification | passed | passed |

Design assessment:

- Direct lane strength: the `ProviderEvidence` dataclass gives downstream users
  an obvious typed affordance and makes common evidence fields discoverable.
- Direct lane weakness: it expands the public FreshForge API before there is
  enough downstream evidence that the chosen fields are stable. This may create
  migration pressure if P17/P18 or downstream packages need a different shape.
- Delegated lane strength: the opaque JSON-compatible mapping is smaller,
  preserves provider autonomy, and better fits the current FreshForge boundary:
  core should serialize provider evidence, not interpret scientific or domain
  meaning.
- Delegated lane weakness: the mapping is less self-documenting for provider
  authors and may lead to inconsistent keys unless follow-on docs or examples
  define a recommended convention.

Worker usefulness:

- The first worker output materially influenced the delegated design. It
  recommended a provider-owned evidence mapping rather than a typed FreshForge
  object, and that recommendation survived supervisor review and full
  verification.
- The second worker output was partially useful but protocol-imperfect: it
  suggested tests and documentation angles but missed the required verification
  section. This is useful evidence for Agent Workbench scoring because the
  output was not a total failure, but it was not fully compliant.

Token economics signal:

- Local worker usage was measured: 4465 input tokens and 632 output tokens at
  zero cash cost.
- Paid supervisor token attribution is still too coarse. The goal counter gives
  useful total progress evidence, but not a clean direct-lane versus
  delegated-lane split.
- P50 is therefore not yet a clean "we won" or "we lost" economics result. It
  is a partial methodological win: worker outputs influenced a viable design,
  but the current instrumentation cannot yet prove paid-token savings.

Recommendation for the next iteration:

- Treat the delegated mapping design as the current favored FreshForge P16
  promotion candidate because it is smaller, less committal, and better aligned
  with FreshForge's generic orchestration boundary.
- Do not discard the direct lane. Use its typed `ProviderEvidence` design as a
  pressure test for docs and examples: the mapping convention should remain
  easy enough to use that provider authors do not need a new public record class
  immediately.
- Run one more narrow P50 iteration before choosing a final FreshForge branch:
  ask workers to review the two concrete diffs and propose either "mapping",
  "typed record", or "hybrid", then have the supervisor choose and apply the
  final branch direction.

## Iteration 2 Worker Diff-Review Evidence

Ticket:

- evaluation id: `p16-diff-design-review`
- target worktree: `../freshforge-benchmark-p16-delegated`
- ticket path: ignored `tmp/agent_workbench/p16/p16-diff-design-review.ticket.md`
- manifest path: ignored
  `tmp/agent_workbench/p16/p16-diff-design-review.manifest.json`
- task: review the two actual P16 lane designs and choose exactly one of
  `mapping`, `typed record`, or `hybrid`

Runs:

| Model | Classification | Decision | Input Tokens | Output Tokens |
| --- | --- | --- | ---: | ---: |
| `qwen3-coder:latest` | `structured-output` | `mapping` | 2779 | 267 |
| `qwen3-coder-next:latest` | `structured-output` | `mapping` | 2785 | 275 |

Worker-token subtotal:

- worker input tokens: 5564
- worker output tokens: 542
- worker cash cost: zero under the local Ollama lane

Decision signal:

- Both models followed the section contract with no missing sections.
- Both independently selected `mapping`.
- Both identified the same main tradeoff: mapping preserves provider flexibility
  and avoids premature FreshForge public API commitment, while losing some
  static typing, IDE discoverability, and cross-provider consistency.

Supervisor interpretation:

- This reinforces the Iteration 1 recommendation: promote the delegated mapping
  lane as the current FreshForge P16 candidate.
- The worker consensus does not prove that a typed record will never be needed.
  It says not to commit FreshForge core to that public shape before P17/P18 or
  downstream provider usage creates stronger evidence.
- The next implementation move should be to sharpen the delegated branch docs
  and examples enough that provider authors get practical guidance without a
  new dataclass.

## Iteration 3 Delegated Candidate Refinement

FreshForge delegated lane:

- worktree: `../freshforge-benchmark-p16-delegated`
- branch: `benchmark/p16-agent-workbench-delegated`
- commit: `a4975a8` (`P16 refine delegated evidence mapping docs`)

Implemented:

- expanded provider documentation with a recommended evidence mapping example;
- documented stable provider-owned mapping keys, suggested entry fields, and
  the boundary that FreshForge core preserves mappings but does not validate
  provider semantics;
- clarified in workflow-runner docs that summaries expose evidence counts and
  compact mappings while full evidence manifests retain provider-owned details;
- strengthened the evidence-manifest test to prove provider-owned `uri` and
  `metadata` fields survive through run evidence and summaries;
- recorded the decision to defer a tracked example payload file until a
  downstream provider creates a real need.

Verification:

- `python -m pytest tests/test_evidence.py tests/test_execution.py tests/test_records.py`
  passed with 12 tests;
- `sphinx-build -b html docs _build/html -W` passed;
- `git diff --check` passed;
- `python -m pytest` passed with 96 tests;
- `python -m ruff check .` passed;
- `python -m build` passed;
- `python -m twine check dist/*` passed;
- public-safety scan found only existing policy text.

Current P50 position:

- The delegated mapping branch is now the active FreshForge P16 promotion
  candidate.
- The direct typed-record branch remains useful as a comparison artifact, but
  not as the favored branch to merge unless maintainer review rejects the
  mapping approach.
- P50 still needs an explicit maintainer decision before FreshForge PR/merge
  closeout.

## Iteration 4 Draft PR Review Surface

FreshForge draft PR:

- PR: UBC-FRESH/freshforge#118
- URL: `https://github.com/UBC-FRESH/freshforge/pull/118`
- title: `P16: Provider evidence mapping conventions`
- head: `benchmark/p16-agent-workbench-delegated`
- base: `main`
- draft: yes
- linked issue wording: `Refs #113`, not auto-close wording

Purpose:

- Turn the delegated mapping candidate into a real maintainer-review surface
  without closing FreshForge P16 or Agent Workbench P50.
- Preserve the explicit boundary that release, tag, publish, issue closure, PR
  readiness, and merge remain supervisor/maintainer-owned.

PR verification:

- GitHub Actions `Python 3.11`: passed
- GitHub Actions `Python 3.12`: passed

Current P50 position after PR creation:

- The delegated mapping branch is no longer just a local benchmark artifact; it
  is now a draft PR candidate with passing CI.
- P50 remains open because the user has not said the phase is done, the PR is
  still draft, child issues remain open, and token-economics attribution is not
  fully resolved.

## Iteration 5 Token-Economics Checkpoint Ledger

The P50 token-economics evidence now has two different confidence levels:

- high-confidence local worker usage from Copilot SDK/Ollama event metadata; and
- lower-confidence paid supervisor usage from the cumulative Codex goal token
  counter.

Worker-token ledger:

| Iteration | Worker Input Tokens | Worker Output Tokens | Cash Cost |
| --- | ---: | ---: | ---: |
| Initial delegated proposal tickets | 4465 | 632 | 0 |
| Diff-review worker tickets | 5564 | 542 | 0 |
| Total measured worker usage | 10029 | 1174 | 0 |

Supervisor goal-token checkpoints:

| Checkpoint | Cumulative Goal Tokens | Delta Since Previous | Attribution Confidence |
| --- | ---: | ---: | --- |
| After direct lane implementation | 129063 | 129063 | low: includes P50 setup plus direct lane |
| After delegated lane implementation | 278526 | 149463 | low: includes delegated orchestration, implementation, and reporting |
| Before token-ledger update | 584722 | 306196 | low: includes comparison, worker review, candidate refinement, draft PR, GitHub comments, and reporting |

Interpretation:

- Worker usage is now measured cleanly enough for P50: 10029 input tokens and
  1174 output tokens, all in the zero-cash local Ollama lane.
- Paid supervisor usage is still not attributable cleanly by lane. The goal
  counter proves this P50 experiment has consumed substantial paid-supervisor
  context, but it does not provide input/output split or per-iteration
  segmentation.
- The observed supervisor-token deltas are therefore not suitable for a final
  cash win/loss claim. They are suitable for identifying the immediate process
  problem: the supervisor is still carrying too much orchestration, verification,
  GitHub hygiene, and reporting overhead.
- The practical lesson is not "delegation won" yet. The stronger conclusion is:
  delegated workers produced useful design signal at negligible cash cost, but
  the current supervisor workflow has not yet driven paid-token cost toward
  near-zero.

Next instrumentation requirement:

- Future phase-scale benchmarks need explicit supervisor checkpoint calls before
  and after each lane, and they need input/output split when the agent surface
  exposes it.
- Until that exists, P50 should report goal-token checkpoints and deltas as
  approximate process evidence, not as precise cost accounting.
- Implemented follow-up: `agent-workbench supervisor-tokens
  latest|checkpoint|span|synthesize` now reads local Codex session
  `token_count` events, writes ignored start/end checkpoints, and derives
  sanitized `.tokens.json` records with fresh input, cached input, output, and
  reasoning-output deltas.
- Updated benchmark rule: no future benchmark iteration may claim economics
  evidence unless every supervisor-owned subtask has named start/end
  supervisor-token checkpoints.

## Iteration 6 Agent Workbench Draft PR Review Surface

Agent Workbench draft PR:

- PR: UBC-FRESH/agent-workbench#346
- URL: `https://github.com/UBC-FRESH/agent-workbench/pull/346`
- title: `P50: FreshForge P16 A/B benchmark evidence`
- head: `feature/p50-freshforge-p16-ab-benchmark-run`
- base: `main`
- draft: yes
- linked issue wording: `Refs #340`, not auto-close wording
- check state: no checks reported for this branch

Purpose:

- Turn the accumulated P50 benchmark evidence into a real Agent Workbench review
  surface without closing P50.
- Keep the FreshForge candidate PR and the Agent Workbench evidence PR separate:
  FreshForge PR #118 reviews the package change, while Agent Workbench PR #346
  reviews the benchmark evidence and delegation process.

Current P50 position after Agent Workbench PR creation:

- FreshForge PR #118 is open, draft, clean, and CI-passing.
- Agent Workbench PR #346 is open, draft, and clean, with no checks configured.
- P50 remains open because the maintainer has not said the phase is done,
  child issues remain open, and the economics ledger is still checkpoint-level
  rather than final lane-local accounting.

## Iteration 7 Benchmark Target Reassessment

The FreshForge P16 A/B test produced useful process evidence, but it is not the
best next place to mine for high-return delegation economics.

The key maintainer feedback is that broad API-design and architecture-choice
tasks are a low-yield benchmark target for the current open Ollama worker
models. The project already has enough evidence that these models struggle with
wide-context design judgment. Continuing to benchmark that task shape would
mostly prove a known weakness.

The higher-potential delegation target is input-heavy, chunkable, evidence-rich
work where paid supervisor tokens would otherwise be spent grinding through
large source material. A concrete candidate is MP11 document metadata indexing:

- source: `Tree Farm Licence 6 Management Plan 11`;
- source package: `tfl6_mp11_202606_public_pdf`;
- page count: `475`;
- source class: long public PDF with structure, appendices, tables, figures,
  claims, and page-anchored metadata;
- expected delegation advantage: local Ollama workers can spend large numbers
  of zero-cash input tokens on exported page/chunk text, while the paid
  supervisor audits samples, validates schema, and decides whether the index is
  useful.

Created a separate benchmark sandbox so this work does not contaminate
Agent Workbench, FreshForge, or FEMIC:

- repository: `UBC-FRESH/agent-delegation-lab`;
- URL: `https://github.com/UBC-FRESH/agent-delegation-lab`;
- local clone: `../agent-delegation-lab`;
- P0 issue: `https://github.com/UBC-FRESH/agent-delegation-lab/issues/1`;
- P1 issue: `https://github.com/UBC-FRESH/agent-delegation-lab/issues/2`.

The new lab repo is now the preferred next benchmark surface for high-volume
delegation experiments. P50 should preserve the FreshForge P16 evidence but
should not keep spending paid supervisor tokens on broad API-design delegation
unless there is a specific reason to compare against that known-difficult task
class.
