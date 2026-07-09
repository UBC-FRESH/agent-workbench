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

## Initial Run Matrix

P75.1 will finalize the matrix before live sessions start. The starting target
is at least three comparable live SDK run attempts:

- baseline selected profile with one named overlay;
- alternate selected profile or model role with the same named overlay;
- repeat or contrast run that tests whether the observed behavior is stable
  enough to compare.

The matrix may stop after two attempts only if the same controller/provider
blocker repeats and the recorded P75 stop rule says further paid-supervisor
coordination would be wasteful.

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

- run at most three planned live attempts before the first comparison decision;
- allow one bounded repair/retry only when the previous failure teaches a
  concrete manifest, prompt, or controller fix;
- stop after two repeated controller/provider failures in the same lane and
  record the blocker instead of chasing a cleaner run.

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
