# Phase 78: Profile Evidence Review Contract Repair

Phase 78 repairs the profile-evidence-review task contract identified by P77
before another live SDK battery. P75 showed that the SDK controller can collect
replicated evidence, while P76 and P77 showed that result-validity weakness is
concentrated in profile-evidence-review and result-auditor-as-primary cells.

## Evidence From P77

The P77 repair plan found:

- top task-family target: `profile-evidence-review`;
- top profile target: `agent-workbench-result-auditor`;
- top weak treatment cell: `agent-workbench-result-auditor` /
  `release-readiness-review` / `profile-evidence-review`;
- recommended next lane: repair profile-evidence-review fixtures and
  result-auditor-as-primary behavior before another live battery.

The concrete contract defect is that P75 profile-evidence-review tickets asked
the worker to inspect profile-run summaries or compact transcripts for the same
run. Those artifacts are generated after the run, so they cannot be reliable
inputs to the worker during that run.

## Goal

Make profile-evidence-review tasks require a pre-existing review subject
artifact and make result-auditor primary-mode behavior explicit.

## Input Contract

A profile-evidence-review manifest must provide a public-safe, pre-existing
review subject path. The subject may be a profile-run summary, compact
transcript, aggregate report excerpt, or other sanitized evidence artifact
declared by the coordinator before the run starts.

The review subject must be separate from current-run result and blocker paths.
Current-run post-processing artifacts are not valid review subjects unless
they were produced by an earlier run and declared explicitly.

## Output Contract

The repaired ticket renderer should write Markdown that includes:

- treatment cell metadata;
- pre-existing review subject path and subject kind;
- current-run output paths;
- required Agent Workbench tool sequence;
- scoring rubric for controller health, result validity, and evidence
  sufficiency;
- final status vocabulary and allowed reasons for each status.

## Public-Safety Boundary

P78 must not promote raw transcripts, prompts, worker answers, provider
endpoints, credentials, tokens, personal absolute paths, or machine-specific
values into tracked files. Dogfood artifacts remain under ignored runtime
storage.

## Planned Tasks

- P78.1: Activate roadmap and planning surfaces (#502).
- P78.2: Implement the profile-evidence-review ticket contract (#503).
- P78.3: Repair result-auditor primary-mode profile behavior (#504).
- P78.4: Dogfood the repaired contract and close out (#505).

## Validation Boundary

P78 can prove that the ticket and manifest contract are no longer inherently
self-referential. It cannot prove improved live-agent performance by itself.
The next empirical step after P78 should be a matched replicated live battery
on repaired cells before model-lane expansion or FoundryTK runtime integration.

## P78 Outcome

P78 added `agent-workbench foundrytk profile-evidence-review-ticket`. The
command reads an SDK manifest and writes:

- a JSON profile-evidence-review contract;
- a Markdown ticket for the selected primary profile.

The repaired contract requires a pre-existing review subject path for
`profile-evidence-review` tasks. It rejects missing subjects, private-looking
subject paths, and subjects that point at current-run output paths. The ticket
separates the review subject from current-run result and blocker outputs and
includes a rubric for controller health, result validity, and evidence
sufficiency.

P78 also updated the standard `agent-workbench-result-auditor` profile so it
knows what to do when it is the selected primary profile: use Agent Workbench
run-context and result-contract tools when available, write exactly one
manifest-declared result or blocker with the constrained writer, validate the
written artifact when possible, and avoid broad search, subagent spawning,
tracked-file edits, commits, GitHub mutation, or whole-phase closeout claims.

Dogfooding rendered:

- manifest:
  `runtime/p78_profile_evidence_review_contract/manifests/p78_per_raud_release_repaired_r1.json`;
- contract:
  `runtime/p78_profile_evidence_review_contract/contracts/p78_per_raud_release_repaired_r1.json`;
- ticket:
  `runtime/p78_profile_evidence_review_contract/tickets/p78_per_raud_release_repaired_r1.md`.

The dogfood contract was valid and used the existing public-safe P75 profile
summary `runtime/p75_live_overlay_sdk_run_battery/profile_summaries/p75_mca_lsup_debug_r1.md`
as a pre-existing review subject. Inspection found no personal paths, provider
URLs, or token-like values in the generated ticket or contract.

The next empirical step should be a matched replicated live battery on repaired
profile-evidence-review cells. The repaired fixture removes a known
self-referential contract defect, but it does not by itself prove improved
result-auditor live performance.
