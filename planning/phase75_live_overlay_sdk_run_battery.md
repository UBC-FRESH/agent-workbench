# Phase 75: Comparable Live Overlay-Selected SDK Run Battery

Phase 75 collects matched live SDK evidence before any deeper FoundryTK
integration, prompt optimization, agent optimization, model-selection, or
fine-tuning work. It exists because P74 deliberately kept FoundryTK outside the
runtime bridge and required comparable live overlay-selected SDK runs before
optimization decisions.

## Experiment Question

Can Agent Workbench collect public-safe, comparable live SDK evidence for
selected profiles and named task overlays strongly enough to support profile or
model-selection decisions?

## Required Comparison Shape

- Same bounded task across runs.
- Same result contract across runs.
- Same manifest and evidence path pattern across runs.
- Same profile-run summary renderer across runs.
- Same P74 evaluation dataset renderer across runs.
- Selected P73 profile and named task overlay recorded before and after every
  run.

## Factorial Design Requirement

P75.1 must produce a real factorial experiment design before live sessions
start. Three comparable runs are only the minimum smoke gate that proves the
evidence pipeline works; three runs are not enough to support a profile,
overlay, or model-selection recommendation.

The design must declare:

- factors: selected profile, named task overlay, model role or model family,
  task family, and retry or repetition lane where applicable;
- fixed factors versus exploratory factors;
- blocking variables, such as task family, run order, controller version,
  worker host inventory, and provider/session condition;
- replication count per treatment cell;
- randomization or rotation order so run order does not masquerade as a model
  or profile effect;
- planned minimum analyzable sample size and the rationale for that number;
- interim checkpoints that are allowed to stop the battery for repeated
  infrastructure failure without pretending the empirical comparison is
  complete;
- which comparisons are confirmatory enough to inform the next development
  step and which are only exploratory.

The initial target should be large enough to estimate repeatability and
interaction signals, not just produce one anecdote per profile. A reasonable
starting shape is a balanced matrix with repeated cells across at least:

- two selected profiles or model-role wrappers;
- two named overlays or task families;
- two model lanes when the live configured inventory supports them;
- three or more repetitions for each treatment cell that remains in scope after
  the P75.1 budget gate.

If that full matrix is too expensive or operationally noisy, P75.1 must narrow
the factors explicitly and preserve replication before launching live runs. The
phase should prefer a smaller factorial design with enough repeats to be useful
over a broad one-pass tour that cannot inform the next development decision.

## Activated P75.1 Run Matrix

P75.1 activates a balanced 24-run live SDK battery after a four-run smoke gate
that validates the instrumentation only. The smoke gate does not count as a
profile, overlay, or model-selection result unless those rows are later included
in the same randomized matrix and meet the same artifact and scoring contract.

Fixed factors:

- model lane: `operator-configured-copilot-sdk`
- provider/session condition: current GitHub Copilot SDK environment
- workspace: Agent Workbench checkout
- permission mode: `operator-configured`
- result contract: worker writes either `Final status: accepted-candidate`,
  `Final status: rejected-candidate`, or `Final status: blocked` in the result
  or blocker file, with a concise evidence list

Primary factors:

- selected profile:
  - `agent-workbench-local-supervisor`
  - `agent-workbench-result-auditor`
- named task overlay:
  - `existing-code-debugging`
  - `release-readiness-review`
- task family:
  - `manifest-contract-audit`
  - `profile-evidence-review`
- repetition:
  - `r1`
  - `r2`
  - `r3`

Exploratory factor held out of the first battery:

- model family: local worker inventory is not available in the active shell
  because `ollama list` is not on PATH. P75 therefore preserves replication by
  holding the model lane fixed instead of adding an unverifiable model factor.
  If two live configured model lanes become available later, use the same
  matrix as a second block rather than replacing within-cell replication.

Blocking variables recorded per run:

- run order
- controller version or git commit
- selected profile
- selected overlay
- task family
- provider/session condition
- worker host inventory status
- SDK manifest validation result
- SDK monitor latest status
- result status

Planned analyzable sample:

- target: 24 analyzable rows
- minimum for a P75 scale decision: 18 analyzable rows and at least two
  repetitions in every in-scope profile/overlay/task-family cell
- smoke gate: first four randomized rows, one from each profile/overlay pairing
  where possible, used only to confirm manifest, event-log, monitor,
  transcript, profile-run-summary, and dataset rendering

Rationale:

Twenty-four rows gives three repeated observations for every profile by overlay
by task-family treatment cell while holding the model lane fixed. That is still
small, but it is large enough to expose repeatability failures, interaction
signals, and profile/overlay sensitivity that a three-run anecdotal smoke test
cannot reveal. If the controller or provider becomes unstable, P75 should stop
as infrastructure evidence rather than degrade the matrix into one-pass
coverage.

Randomized run order uses seed `p75-2026-07-09`:

| order | run id | profile | overlay | task family | rep |
| --- | --- | --- | --- | --- | --- |
| 01 | `p75_mca_lsup_debug_r1` | `agent-workbench-local-supervisor` | `existing-code-debugging` | `manifest-contract-audit` | `r1` |
| 02 | `p75_per_raud_release_r1` | `agent-workbench-result-auditor` | `release-readiness-review` | `profile-evidence-review` | `r1` |
| 03 | `p75_per_lsup_release_r1` | `agent-workbench-local-supervisor` | `release-readiness-review` | `profile-evidence-review` | `r1` |
| 04 | `p75_mca_raud_debug_r1` | `agent-workbench-result-auditor` | `existing-code-debugging` | `manifest-contract-audit` | `r1` |
| 05 | `p75_per_raud_debug_r1` | `agent-workbench-result-auditor` | `existing-code-debugging` | `profile-evidence-review` | `r1` |
| 06 | `p75_mca_lsup_release_r1` | `agent-workbench-local-supervisor` | `release-readiness-review` | `manifest-contract-audit` | `r1` |
| 07 | `p75_mca_raud_release_r1` | `agent-workbench-result-auditor` | `release-readiness-review` | `manifest-contract-audit` | `r1` |
| 08 | `p75_per_lsup_debug_r1` | `agent-workbench-local-supervisor` | `existing-code-debugging` | `profile-evidence-review` | `r1` |
| 09 | `p75_per_lsup_debug_r2` | `agent-workbench-local-supervisor` | `existing-code-debugging` | `profile-evidence-review` | `r2` |
| 10 | `p75_mca_raud_release_r2` | `agent-workbench-result-auditor` | `release-readiness-review` | `manifest-contract-audit` | `r2` |
| 11 | `p75_mca_lsup_release_r2` | `agent-workbench-local-supervisor` | `release-readiness-review` | `manifest-contract-audit` | `r2` |
| 12 | `p75_per_raud_debug_r2` | `agent-workbench-result-auditor` | `existing-code-debugging` | `profile-evidence-review` | `r2` |
| 13 | `p75_mca_raud_debug_r2` | `agent-workbench-result-auditor` | `existing-code-debugging` | `manifest-contract-audit` | `r2` |
| 14 | `p75_per_lsup_release_r2` | `agent-workbench-local-supervisor` | `release-readiness-review` | `profile-evidence-review` | `r2` |
| 15 | `p75_per_raud_release_r2` | `agent-workbench-result-auditor` | `release-readiness-review` | `profile-evidence-review` | `r2` |
| 16 | `p75_mca_lsup_debug_r2` | `agent-workbench-local-supervisor` | `existing-code-debugging` | `manifest-contract-audit` | `r2` |
| 17 | `p75_mca_lsup_release_r3` | `agent-workbench-local-supervisor` | `release-readiness-review` | `manifest-contract-audit` | `r3` |
| 18 | `p75_per_raud_debug_r3` | `agent-workbench-result-auditor` | `existing-code-debugging` | `profile-evidence-review` | `r3` |
| 19 | `p75_per_lsup_release_r3` | `agent-workbench-local-supervisor` | `release-readiness-review` | `profile-evidence-review` | `r3` |
| 20 | `p75_mca_raud_debug_r3` | `agent-workbench-result-auditor` | `existing-code-debugging` | `manifest-contract-audit` | `r3` |
| 21 | `p75_per_lsup_debug_r3` | `agent-workbench-local-supervisor` | `existing-code-debugging` | `profile-evidence-review` | `r3` |
| 22 | `p75_mca_raud_release_r3` | `agent-workbench-result-auditor` | `release-readiness-review` | `manifest-contract-audit` | `r3` |
| 23 | `p75_mca_lsup_debug_r3` | `agent-workbench-local-supervisor` | `existing-code-debugging` | `manifest-contract-audit` | `r3` |
| 24 | `p75_per_raud_release_r3` | `agent-workbench-result-auditor` | `release-readiness-review` | `profile-evidence-review` | `r3` |

Runtime evidence root:

- `runtime/p75_live_overlay_sdk_run_battery/`

Per-run evidence paths:

- manifest: `runtime/p75_live_overlay_sdk_run_battery/manifests/{run_id}.json`
- ticket: `runtime/p75_live_overlay_sdk_run_battery/tickets/{run_id}.md`
- result: `runtime/p75_live_overlay_sdk_run_battery/results/{run_id}.md`
- blocker: `runtime/p75_live_overlay_sdk_run_battery/blockers/{run_id}.md`
- event log: `runtime/p75_live_overlay_sdk_run_battery/events/{run_id}.sdk_events.jsonl`
- status summary: `runtime/p75_live_overlay_sdk_run_battery/status/{run_id}.sdk_status.json`
- compact transcript: `runtime/p75_live_overlay_sdk_run_battery/transcripts/{run_id}.compact.md`
- profile summary: `runtime/p75_live_overlay_sdk_run_battery/profile_summaries/{run_id}.md`

P75.2 instrumentation repair:

- Live smoke rows showed that shell redirection and broad edit authority are
  not reliable or appropriate result-capture mechanisms across selected
  profiles.
- The SDK manifest therefore exposes a constrained
  `agent_workbench_write_result` custom tool for P75 runs. The tool may write
  only the manifest-declared result or blocker path, requires a `Final status:`
  line with an allowed status, rejects private-looking content, and validates
  the written artifact.

Public-safe aggregate outputs:

- matrix: `runtime/p75_live_overlay_sdk_run_battery/p75_run_matrix.json`
- dataset JSONL: `runtime/p75_live_overlay_sdk_run_battery/p75_profile_evaluation_dataset.jsonl`
- dataset preview: `runtime/p75_live_overlay_sdk_run_battery/p75_profile_evaluation_dataset.md`
- scale decision: `runtime/p75_live_overlay_sdk_run_battery/p75_scale_decision.md`

Task family contracts:

- `manifest-contract-audit`: inspect one SDK manifest and its rendered profile
  preview for schema, profile, overlay, path, control, and privacy-contract
  consistency; do not modify tracked files.
- `profile-evidence-review`: inspect one profile-run summary or compact
  transcript artifact and classify controller health, result validity, and
  evidence sufficiency; do not modify tracked files.

Budget and stop rules:

- Run the four-row smoke gate first, render the profile summaries and dataset
  rows for those rows, and continue only if the full evidence chain works.
- Continue toward all 24 rows unless a stop rule fires.
- Pause after two consecutive controller/provider failures with the same root
  cause in the same profile/overlay/task-family lane.
- Pause if fewer than three of the four smoke rows produce valid manifest,
  event-log, monitor, profile-summary, and dataset artifacts.
- Pause after eight rows if more than 25 percent of rows are invalid for
  reasons unrelated to worker answer quality.
- Allow one bounded repair/retry only when the failure identifies a concrete
  manifest, prompt, profile, or controller fix.
- Do not make a profile, overlay, or model-selection recommendation from fewer
  than 18 analyzable rows or fewer than two repetitions in any in-scope cell.

## Evidence Contract

Each run should produce or cite:

- SDK manifest;
- SDK event log;
- status summary;
- result or blocker file;
- profile-run summary;
- compact transcript review artifact when available;
- P74-compatible dataset row.

Raw transcript text, full prompts, credentials, private paths, endpoints, and
machine-specific values remain ignored local evidence and must not be promoted
into tracked planning files.

## Scoring Boundary

P75 preserves the P70/P74 split:

- result validity answers whether the worker output is substantively useful and
  independently verified;
- controller/session health answers whether the SDK/provider/session completed
  cleanly enough to count as protocol evidence.

A correct result with a controller error is not a clean accepted run. A clean
controller run with weak result content is not a quality success.

## Budget And Stop Rule

P75.1 must declare the concrete budget before launching live runs. Default
activation boundary:

- run at least the declared pilot smoke gate before any full-battery launch;
- run the declared factorial matrix unless the documented budget or stop rule
  fires;
- allow one bounded repair/retry only when the previous failure teaches a
  concrete manifest, prompt, or controller fix;
- stop after two repeated controller/provider failures in the same lane and
  record the blocker instead of chasing a cleaner run;
- never convert a stopped or underpowered battery into a profile/model
  recommendation; report it as infrastructure or design evidence instead.

## Follow-On Decision

P75.4 decides whether FoundryTK remains external guidance or whether evidence
supports a narrower next lane:

- optional tool provider;
- trace/evaluation runner integration;
- model-selection evidence source;
- prompt optimization;
- agent optimization;
- fine-tuning preparation.

No follow-on should be activated unless it cites concrete P75 dataset rows,
controller-health evidence, result-validity evidence, and remaining caveats.
