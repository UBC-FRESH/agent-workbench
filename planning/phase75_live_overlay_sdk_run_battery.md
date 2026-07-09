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
