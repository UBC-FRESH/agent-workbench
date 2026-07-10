# Phase 83: Review-Subject Access Contract Repair

Phase 83 repairs the review-subject access contract for SDK
profile-evidence-review tasks.

P82 showed that the source review-subject artifacts exist and resolve from each
generated manifest's base path, but SDK workers could not reliably use those
declared artifacts through the run-context and custom-tool contract. The failure
mode was not sample size and not repeated provider quota exhaustion: it was
access semantics.

## Goal

Make declared review subjects readable through a stable public-safe custom-tool
interface before another repaired battery.

## Scope

- Add or extend custom SDK tooling so workers can resolve and read the declared
  review subject without filesystem search.
- Return public-safe metadata and bounded content from the declared subject.
- Reject missing, private-looking, current-run-output, or outside-allowed-root
  review subjects.
- Expose the repaired access interface in profile-evidence-review tickets and
  custom tool declarations.
- Dogfood the repair on both a deterministic fixture and a real P75
  profile-summary subject.

## Out Of Scope

- Rerunning the repaired 48-row battery.
- Model-lane expansion.
- Tracking raw transcripts, provider URLs, headers, credentials, personal paths,
  or raw worker blocker text.

## Contract Requirements

The repaired interface must prove:

- which review-subject path was declared;
- whether the path resolved from the manifest base;
- whether the resolved subject stays under allowed public-safe roots;
- whether the subject was read successfully;
- bounded public-safe content or summary from the subject; and
- enough stable metadata for a worker to cite the declared subject without
  searching the filesystem or inventing alternate paths.

## Planned Tasks

- P83.1: Define the review-subject access contract (#531).
- P83.2: Implement resolver/reader tool support (#532).
- P83.3: Dogfood review-subject access (#533).
- P83.4: Close out P83 and decide the next lane (#534).

## Next-Lane Rule

If P83 proves that workers can read declared review subjects through the
repaired interface, the next lane should be a small live access probe before
another health-gated repaired battery. If P83 cannot prove deterministic access,
repair manifest path semantics or runtime materialization before spending live
SDK runs.
