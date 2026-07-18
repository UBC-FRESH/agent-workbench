# P114 C4 Capability-Parity Preregistration

Status: P114.1 complete. This record was frozen before the direct-MWE live
Ollama outcomes.
It does not authorize live inference, provider changes, P107 resumption, P108,
or a claim of general Codex feature parity.

Parent issue: #661

Branch: `feature/p114-c4-ollama-capability-parity`

Machine-readable contract:
`benchmarks/document_library/p114_c4_capability_contract.json`

## Research question

Can the configured Codex-Ollama route support the minimum tool and session
semantics needed for the frozen P107.2 C4 source-audit workload, such that a
later C2/C4 comparison could attribute outcome differences to the Worker model
rather than to the bridge or host?

This phase evaluates route viability, not Qwen quality, ROI, or general
feature parity. A route failure remains an invalid treatment observation,
retained in the ledger with its evidence. It is never converted into a
model-quality failure or a model-cost result.

## Why a new phase is necessary

P113 proved a deliberately narrow run-local route for one native
`apply_patch` function call. The C4 attempt did not deploy that route: its
Worker encountered an unsupported patch call, then used shell-mediated writes
and failed deterministic validation. That is a bridge/host failure before a
valid quality evaluation, not evidence that Qwen is worse than the paid C2
Worker.

The historical C2 trace is also exploratory design evidence, not a clean
confirmatory comparator: a paid Worker read a test through the shared checkout
outside its declared worktree. Before a comparison, P107 will therefore require
fresh identically governed C2 and C4 blocks.

## Minimum required interface

P114 requires only the capabilities encoded in the contract: effective
identity, literal worktree binding, repository reads, native patching, declared
shell validation, tool-history continuation, repair continuation, result
artifact flow, role boundaries, and fail-closed unsupported tools.

Skills are intentionally outside this contract. Neither the frozen C4 ticket
nor the available paid C2 trace uses skills. If a later workload or comparator
uses them, the protocol must be amended and frozen before new observations.

## Frozen treatment and provenance rules

The C4 topology remains flat:

```text
Coordinator -> Luna Supervisor
Coordinator -> one Ollama Worker
Coordinator -> Terra Advisor
```

The Worker is `ollama_qwen_coder_worker` on `qwen3-coder:latest`; the frozen
P107.2 baseline, ticket, fixture, role profiles, model catalog, pricing
catalog, and configuration identity must be recorded before any live attempt.
All commands that act on code under test must identify the literal detached
worktree. Each counted result retains raw run evidence in ignored storage and a
public-safe manifest identifying the route, parentage, validation, and
outcome classification.

## Staged gate and stopping rule

P114.2 preserves the clean-process offline adapter checks. The original P114.3
scripted-provider deployment route is retained only as negative integration
evidence: it reached the bridge but did not register executable host tools. It
is not a live runtime gate and cannot establish P114.3 acceptance.

Runtime construction now begins with the verified P113-style direct MWE and
changes one variable at a time. R4 is the current last-known-good baseline:
one native patch changes the P114 proof target and returns the P114 marker.
R5 proves one standalone read, R6 combines that read with the existing patch,
and R7 adds one declared validation. Each must pass independently before a
repair continuation, artifact envelope, or composite battery is attempted. A
failed increment restores the last passing MWE configuration; it does not
trigger an automatic retry or broader redesign. The P114.3 pass rule will be
revised and re-frozen to this direct-MWE evidence before any live run is
counted toward P114.3.

Only after the complete direct MWE capability sequence passes may P114 run
three independent fresh candidate sessions through the composite
read-to-patch-to-test-to-repair-to-artifact task. All three must pass; a
shell-write substitute is not native-patch success. P114.5 then permits two
non-comparative C4 qualification observations.

Every bridge or host failure must retain its direct evidence and be repaired at
the component that caused it. Continue capability work until the route is
characterized; do not convert an integration failure into a model-quality or
economics result. Integration cost, operational treatment cost, and model-task
cost are recorded separately.

## Conditions for a publishable P107 comparison

P107 can resume only after every P114 stage passes and the new P107 protocol
predeclares randomized matched C2/C4 ordering, exclusions, retry rules, an
invalid-observation ledger, and cost definitions. It will start with at least
five matched pairs and expand toward ten if observed variability makes the
effect estimate unstable. Findings will be limited to this Windows/PowerShell
host, Codex version, configured route and model, topology, and frozen workload.
