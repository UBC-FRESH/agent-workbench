# P107 Configuration Economics Research Program

## Purpose

P107 is a reproducible economic-performance data collection program, not a
one-shot delegation proof. Its practical question is whether carefully managed
Agent Hub configurations produce useful UBC-FRESH development work with less
paid cost and less maintainer steering than BAU.

## Comparator and units

BAU C0 is one fresh GPT Terra/Medium Coordinator working alone. The Coordinator
implements, validates, and repairs within its ordinary task loop. Sol is a
selective, non-mutating Advisor: consult it only for a concrete ambiguity or
failed verification whose decision value justifies the paid cost. It is not a
routine execution gate or a required member of every configuration.

An evaluation block freezes workload, starting commit, ticket, acceptance
fixture, rubric, prompt/configuration hashes, runtime version, environment
epoch, pricing catalog, native model catalog, and effective configuration
snapshot. It records SHA-256 values for each frozen copy and requires ambient
memories to be disabled. Any change opens a new block and requires a new C0.

Model identity comes from the authoritative native launch binding: either an
explicit raw-session model field, or the hash-bound pre-launch native
configuration/role binding linked to the session creation time and identity.
The latter is sufficient when the host omits the model from an individual raw
transcript. Exclude unrelated host UI metadata such as automatic conversation
title generation from development-task economics.

A treatment is comparable only when frozen acceptance passes, native protocol
evidence is accepted, contamination is false, accounting is complete, and an
eligible C0 exists in the same block. Otherwise record the observation and
spend as not comparable. A selective Sol consultation may inform a Coordinator
decision but is not a mandatory comparison gate.

## Mission guardrail: artifact checks are measurement, not behavior control

The deterministic acceptance fixture measures the repository artifact produced
by a native Agent Hub team. It does not require the LLM roles to behave like
deterministic software, and a non-passing implementation is not an invitation
for the outer coordinator to change the workload or repair the candidate until
it passes. Preserve that result as quality evidence for the configuration.

Self-validation and self-repair are valid only when performed by the evaluated
team within its ordinary frozen task loop, and their time and cost are part of
the observation. The outer controller may repair only a demonstrated native
route, authority-boundary, observation, or accounting failure. Such a repair
is a separate protocol/instrumentation result; if it changes the comparison
conditions, freeze a new block and obtain a new C0 reference.

## Initial configuration ladder

| ID | Topology | Delta under study |
| --- | --- | --- |
| C0 | Terra/Medium Coordinator alone | Direct paid lifecycle baseline. |
| C1 | Terra/Medium Coordinator to one Luna Worker, using Coordinator-owned P116 supervision | Does Luna displace Terra implementation work in the usable native route? |
| C2 | Terra/Medium Coordinator to one configured Ollama Worker, using Coordinator-owned P116 supervision | Can zero-marginal-cost execution displace Terra work in the usable native route? |
| C3 | Luna/Medium agent alone | Is cheap direct execution sufficient for this task class? |
| C4 | Luna/Medium Coordinator to one configured Ollama Worker | Can a mostly-free team complete work autonomously? |
| C4+ | C4 model lanes | One-variable Ollama Worker-model sequence on the fixed C4 topology. |

The Coordinator retains git, GitHub, PR, lifecycle, validation, and final
authority in every delegated configuration. C4 varies the paid Coordinator
model as well as using a configured Ollama Worker; it is not a disguised
Supervisor experiment. P107.1 remains prerequisite evidence only; it does not
choose a winner.

For C1, C2, and C4, the Coordinator must start and close the P116 run around
the exact Worker session, review meaningful deltas, and itself decide and send
any cue or interruption. This is not a separate Supervisor role and does not
make LLM behavior deterministic. It makes the native control route available
to the Coordinator that owns the task. Earlier C1 and C2 observations without
that route remain unsupervised diagnostics, not observations of this canonical
delegated configuration.

## C4 Ollama Worker sequence

C4 starts with `qwen3-coder:latest`, the accepted P107.1 Worker profile. On
the same fixed topology and frozen workload, later C4+ lanes may test only one
model change at a time, in this order when the live inventory confirms each:

1. `qwen3-coder:latest`;
2. `qwen3-coder-next:latest`, with persisted exact-model evidence because
   historical custom-agent runs could silently fall back to `qwen3-coder`;
3. `qwen3.6:35b-a3b-bf16`;
4. `qwen3.6:35b-a3b-q8_0`.

The last two have prior same-family quality evidence but are not substitutes for
the first C4 lane. Do not add an unobserved `gpt-oss` lane without a fresh live
inventory record and a separately declared configuration lane.

Every configuration includes a proportionate self-validation expectation at
each active role. Before reporting upward, a Worker, Supervisor, and
Coordinator identifies likely defects in its own output, runs the most useful
available in-scope checks, reports the evidence and residual uncertainty, and
may self-repair only while the local evidence shows convergence toward expected
acceptance. These local loops are measured treatment behavior: record their
iterations and cost. They are intended to prevent the Advisor from repeatedly
catching cheap, obvious defects, while retaining the Advisor as the independent
quality boundary.

This is an observed agent behavior, not a mechanism for imposing deterministic
equivalence. Once a role has submitted its terminal result, no external
Coordinator repair may convert that result into a quality pass for the same
configuration observation.

## Current comparison epoch

The self-validation and convergent-local-repair contract starts a new P107.2
comparison epoch. Earlier C0/C1/C2 observations remain useful behavioral and
cost evidence, but are not the baseline for this epoch. The first attempted C0
on `p107-provenance-audit-bundle-v1` is invalid because that workload was
already implemented at its starting commit. The later
`p107-source-audit-output-projection-v1` C0 runs are retained as instrumentation
evidence for root binding, immutable review, and token-ledger capture only; the
feature is too small to support the capability comparison. The first substantial
review-pack v1 observation is also instrumentation, not an eligible baseline:
its implementation payload remained too small relative to session overhead and
its installed Advisor role ran at high rather than the declared medium reasoning.
The actual P107 capability block is now
`p107-run-evidence-dossier-v3`, defined in
`planning/p107_substantial_workload_capability_plan.md`, then progresses through
C1-C4 only after the preceding configuration has a recorded outcome. The
fresh C0 r2 observation is retained as configuration evidence but is not yet an
eligible baseline; it cannot support a comparative ROI claim without its
separate quality, protocol, and accounting verdicts.

## Advisor gate

Each implementation role starts fresh. All initial delegate spawns use
`fork_context:false`. Sol consultation is exceptional rather than a standing
review state machine. When used, Sol receives a compact immutable packet,
does not edit or delegate, and returns advice about a concrete ambiguity or
verification failure.

There is no automatic numerical review, retry, or stop cap. The Coordinator
uses the recorded evidence to decide whether a further in-loop repair is
converging, whether the terminal result is an honest blocker, or whether the
configuration outcome should be recorded. A Sol consultation cannot authorize
an external repair of a terminal configuration result.

The active P107 run-evidence, accounting, and comparison validators mirror this
ladder. They require only the roles and direct spawn edges declared above, do
not require Advisor artifacts, and allow the normal uncommitted implementation
diff at the frozen starting commit. Historical P107.2 replay contracts remain
historical evidence rather than authority for the active C0-C4 sequence.

## Isolation, accounting, and ROI

Every run has a new worktree, fresh root session, unique session IDs, and
hash-frozen fixture/ticket/rubric/prompts. Implementation roles cannot read
another run's worktree, result, transcript, or Advisor verdict. A substantive
maintainer instruction after launch contaminates that observation; routine
launch approval is logged separately. The first block represents lifecycle
work with local commit/draft-PR artifacts, not remote GitHub mutation.

Record per role: uncached input, cached input, output, and reasoning token
classes; start/end checkpoints; model/provider/pricing identity; active/wait
time; and evidence confidence. Resolve the dated pricing catalog for every paid
role and calculate USD separately for each token class. Also record local
runtime/energy assumptions, adapter version, Advisor cost, review/repair/
transport counts, maintainer messages/minutes, and invalid-run spend.

Paid run cost is all paid Coordinator, Supervisor, Worker, and Advisor cost.
Paid ROI is C0 paid cost minus treatment paid cost, divided by C0 paid cost.
Full ROI is unknown unless local and external variable cost is known. Never
report unknown local cost as zero. A P107 comparison must report both the
token-class ledger and catalog-backed USD. Token totals explain why a
configuration costs what it costs; USD determines whether it is economically
better or worse.

## Gates and search policy

- G0: schemas, validators, negative tests, and synthetic replay pass.
- G1: workload is realistic, bounded, useful, and configuration-neutral.
- G2: C0 is Advisor-accepted with complete accounting within its declared soft
  review cap.
- G3: treatment has exact topology/model evidence, no contamination, Advisor
  acceptance, and complete accounting.
- G4: exploratory promotion requires positive paid ROI and no worse maintainer
  steering than C0.
- G5: practical promotion requires at least 20% paid ROI and no critical
  quality regression.
- G6: default-policy promotion requires replication in two independent blocks.

C0 establishes the reference only after separate quality, protocol, and
economics verdicts are accepted. If C1-C4 yield no accepted positive ROI,
pivot the workload, ticket, or delegation boundary on a stated decision and
obtain a new C0 rather than sweeping models. C5+ starts only as a separately
declared configuration sequence. No automatic failure count determines that
decision.

## Required implementation tranche

P107.2 builds the machinery: configuration/workload/evaluation-block registry,
run packet, immutable review bundle and verdict, accounting/observation/
comparison schemas, frozen rubric, role prompts, validators, and synthetic
offline replay. Validators reject topology drift, C2 Supervisor spawning,
Coordinator edits in C1-C4, session reuse, hash drift, cross-run context,
Advisor bypass, review depth beyond the declared cap, incomplete accounting,
ROI without eligible C0, and cheap-but-unaccepted wins.

P107.3 through P107.7 execute C0 through C4 one configuration per authorized
child issue. P107.8 synthesizes the tranche and decides whether C5+ is worth
authorizing.

## Tranche closeout — 2026-07-21

P107 closes as an exploration tranche, not as a final one-number ranking. The
accepted C0, C1, supervised C2, and C4+ observations retain their independent
quality, protocol, and economics evidence. They cannot be collapsed into a
single comparative result because the frozen workload, topology, and provider
conditions evolved between the observations.

The next decision is not another P107 model sweep. P118 starts a fresh
single-provider vLLM deployment boundary: one declared model across custom
Coordinator, Worker, and selective Advisor roles, serial intense execution, and
fresh task-level quality/protocol/economics records.
