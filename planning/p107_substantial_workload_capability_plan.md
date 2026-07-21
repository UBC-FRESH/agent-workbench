# P107 substantial-workload capability block

## Purpose

P107 needs to prove that the configured Agent Hub can measure economics on a
non-micro delegated development task. It does not attempt to measure complete
project lifecycles or establish a general policy from one block.

The output-projection C0 runs and the completed review-pack v1 run remain
instrumentation evidence. They prove the worktree-root launch, immutable
Advisor review, and session-bound accounting path. They are not the C0
reference for C1-C4: v1 still concentrates too much paid effort in setup,
teardown, and review relative to its implementation payload. The v1 run also
revealed that the installed Advisor role forced high reasoning despite a
medium request; that role configuration must be made observable and correct
before a protocol-valid baseline is claimed.

## Selected workload

`p107-run-evidence-dossier-v3` replaces the source-audit wrapper direction.
The v2 workbench is quality-valid instrumentation, but its cost was only about
1.21 times v1 despite a much larger test surface. It is not the economics
baseline. V3 is a single five-slice feature whose pieces require independent
data modeling, validation, reconciliation, analysis, and rendering.

1. **Dossier manifest.** Define a versioned manifest that names a run's
   heartbeat, token ledger, Advisor verdict, archive manifest, and result
   artifacts using safe relative paths and SHA-256 digests.
2. **Artifact validation.** Validate manifest shape, path containment, hashes,
   schemas, and required role/session identifiers with stable diagnostic codes.
3. **Cross-artifact reconciliation.** Reconcile run IDs, session lineage,
   timestamps, role identities, and outcome labels across the artifacts;
   produce deterministic conflict records rather than accepting contradictory
   evidence.
4. **Timeline and anomaly analysis.** Build a normalized event timeline and
   detect missing stages, stale heartbeats, unclosed roles, token-span gaps,
   and result/Advisor disagreement.
5. **CLI dossier rendering.** Add deterministic JSON and Markdown dossier
   outputs plus a strict validation command. Outputs must be public-safe,
   lexically ordered, and retain enough evidence to support a Coordinator's
   acceptance decision.

This is a realistic multi-module integration feature, not test-count inflation.

## Evaluation guardrail

V3's deterministic acceptance surface judges the resulting code, not the
Coordinator or Worker as if either were deterministic software. A frozen C0-C4
run may produce an incomplete, divergent, invalid, or accepted candidate; each
is empirical quality evidence about that native Agent Hub configuration.

After the block is frozen, the Coordinator must not revise the ticket, fixture,
test surface, prompt, or workload design to make an LLM pass. It must not
repair a configuration's submitted implementation outside that configuration's
ordinary task loop. Only a demonstrated defect in the native control layer
(wrong route/topology, lost boundary observation, or missing accounting) may
justify a control-layer repair, and that repair is a separate protocol finding,
not a quality repair. A comparison-changing repair requires a new frozen block
and a new C0 reference.

## Allowed implementation surface

- `src/agent_workbench/evidence_dossier.py` (new)
- `src/agent_workbench/evidence_dossier_validate.py` (new)
- `src/agent_workbench/cli.py`
- `tests/test_evidence_dossier.py` (new)
- `tests/test_evidence_dossier_validate.py` (new)
- `README.md`

## Frozen acceptance scope

Before a fresh C0 worktree is created, freeze a ticket and independent fixture
covering all five slices with synthetic, public-safe artifacts:

- valid and malformed dossier manifests, contained relative paths, and hashes;
- heartbeat, token, Advisor, archive, and result-artifact schema failures;
- contradictory run IDs, role/session lineage, outcome labels, and timestamps;
- normalized lexical timeline generation and all named anomaly classes;
- deterministic public-safe JSON and Markdown rendering;
- validation of intact dossiers plus stable rejection of tampered, missing,
  unexpected, malformed, and cross-artifact-inconsistent artifacts.

The focused suite must add at least **100** new focused test cases across the
two dossier test modules, with a combined collection floor recorded in the
frozen fixture. The fixture, ticket, prompts, model catalog, pricing catalog,
effective config, and rubric are frozen before C0 begins.

## Current implementation checkpoint (2026-07-20)

The current root contains an uncommitted implementation candidate for all five
V3 feature slices:

1. hash-bound manifest loading with typed artifact labels;
2. schema validation for heartbeat, token-ledger, Advisor-verdict, archive,
   and Worker-result artifacts;
3. deterministic run/session/lineage/outcome reconciliation;
4. normalized lifecycle timeline plus named anomaly records; and
5. deterministic JSON/Markdown rendering and `agent-workbench dossier`
   validation/render commands.

The public-safe fixture at
`tests/fixtures/p107_run_evidence_dossier_v3/` binds all five artifacts by
lowercase SHA-256. The two focused dossier modules currently collect `100`
passing cases plus one platform-dependent symlink skip. This is local quality
evidence only. It is not a C0-C4 observation, protocol qualification, or an
economics result.

Before any C0 launch, freeze the remaining ticket, prompts, model/pricing
catalogs, effective configuration, and Advisor rubric against this fixture,
then perform independent acceptance on the resulting frozen block.

### C0 preflight freeze (2026-07-20)

The ignored local block `runtime/agent_jobs/p107_v3_c0_freeze_20260720/` now
contains the hash-bound V3 ticket, fixture, corrected reset-consistent C0-C4
prompts, Terra/medium effective-session snapshot, model/pricing catalog copies,
and Advisor rubric. It validates against the clean pre-implementation baseline
`50a8a185556aeb81bf1142f7992c026871426920`.

The preflight validator accepts an explicit real checkout root for a freeze
block held outside the later C0 worktree; ordinary block validation retains its
contained-root rule. This materialization did not create a worktree or launch
C0. It supplies no quality/protocol/economics observation.

For C0-C4 pricing, model identity is bound by the frozen effective
configuration/role binding at native launch and its link to the new session.
Raw session model fields are corroboration when present, not the sole source of
truth. Unrelated native UI metadata such as title generation is excluded from
development-task economics and does not redefine the implementation model.

## Comparison boundary

One fresh C0 implements this v3 workload in a literal clean worktree under the
host-cwd preflight. C1-C4 reuse exactly the same frozen block, acceptance
fixture, allowed paths, and accounting contract. The only intended configuration
differences are the declared Agent Hub topology and model/provider choices.
The comparison deliberately observes stochastic agent behavior; it does not
normalize or repair that behavior into deterministic equivalence.

For delegated C1, C2, and C4 runs, the declared topology includes the
Coordinator-owned P116 control layer: bind the exact Worker session before it
uses tools, consume meaningful deltas, decide any intervention at the
Coordinator, and close the run after the Worker reaches its stop condition.
This is a control-plane condition, not a deterministic behavior requirement.

Record quality, protocol, and economics separately. C0 establishes a paid-cost
baseline only after accepted frozen-workload evidence, protocol-valid native
session settings and authority boundaries, uncontaminated run provenance, and
complete session-bound paid-role ledgers. A selective Sol consultation is not a
standing baseline requirement. Paid ROI is reported only when a later treatment
is eligible against that C0.

### C0 r3 eligible baseline (2026-07-20)

Fresh native C0 r3 session `019f80f3-03ae-7cd3-83a6-9feaae4efb5c` ran in a
clean worktree from the frozen baseline after the native default was set to
`gpt-5.6-terra` at `medium` reasoning with memories disabled. Its submitted
implementation passed the exact frozen acceptance command (`4 passed`), the
CLI accepted its intact dossier fixture and rejected a tampered manifest, and
the scoped diff passed `git diff --check`. No agents were spawned and no
commit, push, GitHub, or configuration mutation occurred during the run.

The raw native session's final cumulative token snapshot was priced against the
frozen catalog at `$2.0937575` for the Terra Coordinator development span.
Automatic UI title generation is unrelated host metadata and is excluded. C0 r3
is therefore the eligible baseline for C1 under this same accounting treatment.
This does not make any C1-C4 ROI claim.

### C1 comparable delegated observation (2026-07-20)

Fresh C1 root session `019f80fb-4baa-7752-9e56-cffa883088b5` spawned exactly
one `gpt_luna_worker` with `fork_context:false`; the Worker session
`019f80fb-aaff-7fd2-85b6-fbad62f8bbc9` made the scoped implementation edits.
The Terra Coordinator then independently reviewed the diff and ran the frozen
acceptance command. The submitted C1 feature passed `4` focused tests; its CLI
validated the intact fixture and rejected a tampered manifest.

Quality and protocol are accepted. The frozen pricing treatment gives
`$0.7909664` for the Terra Coordinator and `$0.4235984` for the Luna Worker,
`$1.2145648` total. Compared with C0's `$2.0937575`, this is a
`$0.8791927` (42.0%) paid-cost reduction with no observed quality regression.
This is one comparable C1 observation, not a general delegation policy.

This run did not activate P116. It is therefore retained as an unsupervised
Luna baseline observation; it is not evidence that the canonical supervised
route was usable.

### C2 failed Ollama-Worker observation (2026-07-20)

Fresh C2 root session `019f8101-8dcd-7783-9f85-23cc5713d959` spawned one
configured `ollama_worker` with `fork_context:false`. The Worker created only
two incomplete source files, did not create the required tests, fixture, or CLI
change, and never returned its required final report. The Terra Coordinator did
not implement a fallback; it shut the Worker down and independently confirmed
that the frozen test command could not collect its missing test files.

Quality is rejected. The intended one-Worker/no-fallback topology occurred, but
the missing Worker terminal result prevents protocol acceptance. Economics is
not usable for comparison: local Worker cost is unmeasured and the unaccepted
output cannot count as a cheap win. Preserve this as C2 quality evidence; do
not repair the candidate externally.

This run also did not activate P116: it produced zero control-layer events,
zero control-layer nudges, and zero control-layer repair directives. The
Coordinator manually polled the Worker, sent one ordinary nudge, then one
interrupt, and closed it. That is an unsupervised observation, not a control
layer result. The next slice is a fresh supervised C2 rerun on the same frozen
workload, with the exact P116 lifecycle bound before the Worker uses tools.
Its purpose is to establish whether the usable native route can surface and
act on meaningful workflow signals; it is not an attempt to force a pass.
