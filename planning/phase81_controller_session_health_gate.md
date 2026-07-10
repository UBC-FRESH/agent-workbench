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

## Outcome

P81 added `agent-workbench copilot-sdk health-gate`, a deterministic CLI report
over existing SDK manifests, status summaries, and event logs.

The command writes public-safe JSON and Markdown reports and exits with code
`2` when the generated gate decision is `no-go`. The report keeps
controller/session health separate from worker result quality by summarizing:

- manifest count and optional required-count shortfall;
- controller-health counts;
- row-level go/block decisions;
- sanitized repeated error signatures; and
- public-safe row reasons.

Dogfood against the 12 P80 smoke manifests wrote ignored artifacts under
`runtime/p81_controller_session_health_gate/` and produced:

- decision: `no-go`;
- manifest count: 12;
- required count: 12;
- controller health: 9 healthy, 3 error;
- repeated error signatures: `quota_exceeded` across 3 rows; and
- no matched personal paths, provider URLs, GitHub-token strings, raw quota
  messages, or request IDs in the rendered health-gate reports.

P81 therefore confirms that the P80 stop was a controller/session health block,
not repaired profile-evidence-review behavior evidence. The next empirical lane
remains the full P79/P80 repaired 48-row battery only after controller/session
quota health recovers and the health gate can pass.
