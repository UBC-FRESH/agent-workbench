# P107 Configuration Economics Research Program

## Purpose

P107 is a reproducible economic-performance data collection program, not a
one-shot delegation proof. Its practical question is whether carefully managed
Agent Hub configurations produce useful UBC-FRESH development work with less
paid cost and less maintainer steering than BAU.

## Comparator and units

BAU C0 is one fresh GPT Luna/High Coordinator plus a fresh Sol/Medium Advisor.
The Advisor persists within that run across reviews. The Coordinator implements,
validates, and repairs itself. The Advisor is a
non-mutating Developer pro tem; its cost is included in C0 and every treatment.

An evaluation block freezes workload, starting commit, ticket, acceptance
fixture, rubric, prompt/configuration hashes, runtime version, environment
epoch, pricing catalog, native model catalog, and effective configuration
snapshot. It records SHA-256 values for each frozen copy and requires ambient
memories to be disabled. Any change opens a new block and requires a new C0.

A treatment is comparable only when deterministic acceptance passes, the
Advisor accepts it, contamination is false, accounting is complete, and an
eligible C0 exists in the same block. Otherwise record the observation and
spend as not comparable.

## Initial configuration ladder

| ID | Topology | Delta under study |
| --- | --- | --- |
| C0 | Luna/High Coordinator plus Sol/Medium Advisor | BAU control: Coordinator does the job. |
| C1 | Coordinator to Luna Light Worker plus Advisor | Flat paid Worker delegation. |
| C2 | Coordinator to Luna Supervisor and Coordinator to Luna Light Worker plus Advisor | Flat supervisory assistance; Supervisor cannot spawn. |
| C3 | Coordinator to Luna Supervisor to Luna Light Worker plus Advisor | Nested delegation. |
| C4 | Coordinator to Luna Supervisor and Coordinator to Ollama Worker, plus Advisor | Flat depth-1 supervision with a local Worker: the C2 topology with only the Worker provider/model changed. |
| C4+ | C4 model lanes | One-variable Ollama Worker-model sequence on the fixed C4 topology. |

The Coordinator retains git, GitHub, PR, lifecycle, validation, and final
authority in every configuration. C2 isolates lower-cost supervisory
planning/review from nested delegation. C4 preserves that flat depth-1 shape:
the Supervisor and Ollama Worker are direct Coordinator children, and the
Supervisor never spawns. P107.1 remains prerequisite evidence only; it does
not choose a winner.

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
inventory record and separate authorization.

Every configuration includes a proportionate self-validation expectation at
each active role. Before reporting upward, a Worker, Supervisor, and
Coordinator identifies likely defects in its own output, runs the most useful
available in-scope checks, reports the evidence and residual uncertainty, and
may self-repair only while the local evidence shows convergence toward expected
acceptance. These local loops are measured treatment behavior: record their
iterations and cost. They are intended to prevent the Advisor from repeatedly
catching cheap, obvious defects, while retaining the Advisor as the independent
quality boundary.

## Current comparison epoch

The self-validation and convergent-local-repair contract starts a new P107.2
comparison epoch. Earlier C0/C1/C2 observations remain useful behavioral and
cost evidence, but are not the baseline for this epoch. The rerun begins with a
fresh C0 on the frozen provenance-audit bundle workload, then progresses through C1-C4
only after the preceding configuration has a recorded outcome. The current C2
self-validation observation is pre-epoch evidence and cannot support a
comparative ROI claim.

## Advisor gate

Each implementation role starts fresh; the root Coordinator and one
Sol/Medium Advisor stay alive across their own run's repairs and Advisor
gates. All initial delegate spawns use `fork_context:false`; later Advisor
reviews use `send_input` to that same Advisor session.

The state machine is implement, Coordinator precheck, compact immutable initial
packet, one fresh Advisor, then Advisor hard wait. Later reviews send compact
immutable repair deltas to the same Advisor. Advisor output is accept, defect
packet, or verified blocker.

Advisor review depth is a measured control parameter. The current block has an
exact three-review cap: initial review plus up to two repair-and-rereview
cycles. Only schema-valid Advisor output counts. The Coordinator may end earlier
only for acceptance or a verified blocker; an extension needs recorded
maintainer authorization and starts a new declared cap epoch.

For C1-C4, a schema-valid `defect_packet` is a command to the Coordinator to
coordinate recovery, not merely a rejection record: the Coordinator issues a
bounded evidence-based repair ticket to the responsible delegated role, verifies
the repaired artifact, and returns a compact immutable repair delta to the
persistent Advisor.
The Coordinator may correct only its own review/evidence metadata directly; it
must never make a Worker-owned implementation repair. A terminal Advisor
transport failure is not a defect packet and therefore neither consumes nor
opens a repair cycle.

While awaiting an Advisor verdict, the Coordinator may only wait and record
non-mutating metadata. It must not nudge, time out, infer a verdict from
silence, repair, spawn implementation roles, accept, reject, or end the lane.
Repeated waits are allowed. A terminal review-transport failure pauses the gate;
the same immutable bundle may be relaunched without consuming a review.

The Advisor reviews a compact Coordinator-produced packet containing only the
ticket identity/hash, diff or changed-path hash, focused frozen acceptance
output, scope/contamination status, and prior defect id when applicable. The
initial packet is capped at 16,000 estimated input tokens; repair deltas at
4,000. It does not inspect a mutable lane, edit, delegate, or repair.
Acceptance requires deterministic success, no critical defect, correctness at
least 3/4, and total rubric score at least 8/10.

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

C0 establishes the reference. Two failures from the same mechanism stop that branch.
If C1-C4 yield no accepted positive ROI, pivot workload/ticket/delegation
boundary and obtain a new C0 rather than sweeping models. C5+ needs tranche
synthesis authorization.

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
