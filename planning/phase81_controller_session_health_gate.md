# Phase 81: Controller/Session Health Gate

Phase 81 adds a deterministic controller/session health gate for live SDK
batteries.

P80 stopped before the full repaired profile-evidence-review battery because
the smoke gate observed repeated provider quota-exceeded SDK event errors. That
was the correct stop decision, but it also means the next empirical battery
needs a public-safe go/no-go gate before spending more rows.

## Goal

Make controller/session health a pre-execution gate for live SDK batteries.

The gate should protect the P79/P80 repaired 48-row factorial design. It should
not reduce the sample size or treat a smaller retry as equivalent evidence.

## Inputs

The P81 gate reads existing local SDK artifacts:

- one or more SDK session manifests;
- each manifest's status summary when present;
- each manifest's SDK event log when present; and
- existing manifest validation output.

The gate must not contact the live provider, create new SDK sessions, send
prompts, or retry worker tasks.

## Outputs

Expected outputs:

- public-safe JSON health-gate summary;
- public-safe Markdown health-gate report;
- row-level health classifications for each manifest;
- aggregate controller/session health counts;
- repeated error-signature counts; and
- a go/no-go decision.

## Public-Safety Boundary

Tracked outputs may include run IDs, phase IDs, issue numbers, status labels,
counts, sanitized error signatures, and repo-relative artifact paths.

Tracked outputs must not include raw transcripts, full prompts, worker answers,
provider URLs, headers, credentials, personal paths, or raw SDK event payloads.

## Go/No-Go Semantics

The health gate passes only when:

- every row has readable manifest evidence;
- status evidence is present for every row;
- no row has controller/session health classified as `error`;
- no repeated provider/controller error signature appears; and
- the required manifest count, when specified, is satisfied.

The health gate blocks execution when:

- any manifest is invalid or unreadable;
- any status summary or event log needed for health classification is missing;
- any row reports controller/provider errors; or
- any error signature repeats across rows.

Blocked health gates are controller/session evidence, not worker-quality
evidence. A blocked gate does not authorize narrowing the repaired battery
design.

## Planned Tasks

- P81.1: Define the health-gate contract (#519).
- P81.2: Implement the deterministic health-gate command (#520).
- P81.3: Dogfood the gate against P80 smoke evidence (#521).
- P81.4: Close out P81 and decide the next lane (#522).

## Next-Lane Rule

If P81 can classify P80 smoke evidence and deterministically block on the
observed quota/controller errors, then the next empirical lane remains the full
P79/P80 repaired 48-row battery after controller/session quota health recovers.

If P81 cannot produce a stable public-safe health decision from existing SDK
artifacts, repair the health-gate inputs and SDK summary contract before
another live battery.
