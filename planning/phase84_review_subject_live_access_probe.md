# Phase 84: Review-Subject Live Access Probe

Phase 84 verifies the repaired review-subject access contract in one live SDK
profile-evidence-review run.

P83 proved deterministic access through `agent_workbench_review_subject` for
both a fixture subject and a real P82 manifest pointing to a P75 profile-summary
subject. The remaining risk is live worker behavior: a worker may still ignore
the declared access tool, search alternate paths, or fail to cite the declared
subject even though the tool contract is available.

## Goal

Run one small live SDK probe that asks a profile-evidence-review worker to use
`agent_workbench_review_subject` before spending another health-gated repaired
battery.

## Scope

- Build one public-safe live probe manifest from existing P82/P75 evidence.
- Preserve the P83 review-subject access contract in the run context and result
  contract.
- Require the worker to use the declared review-subject tool when available.
- Collect result or blocker evidence from exactly one live SDK worker run.
- Render a concise public-safe probe summary under ignored runtime storage.
- Record whether the next lane can return to a repaired battery or needs
  another targeted access-contract repair.

## Out Of Scope

- Rerunning the 48-row repaired battery.
- Model-lane expansion.
- Publishing raw transcripts, provider URLs, headers, credentials, personal
  paths, or raw worker blocker text.
- Treating a single probe as repaired profile-evidence-review behavior evidence.

## Success Criteria

The probe supports returning to a repaired battery only if:

- live health is sufficient to start the run;
- the manifest exposes `agent_workbench_review_subject`;
- the live worker returns a result or blocker artifact;
- the artifact explicitly references the declared review subject or the
  review-subject tool contract; and
- no public-safety scan finds personal paths, URLs, tokens, provider request
  identifiers, or raw provider error details in tracked summaries.

If the worker ignores the declared access tool or cannot consume the declared
subject, the next lane remains targeted access-contract repair rather than a
full battery rerun.

## Planned Tasks

- P84.1: Define the live access probe contract (#539).
- P84.2: Prepare the live probe manifest and ticket (#540).
- P84.3: Run and evaluate the live SDK access probe (#537).
- P84.4: Close out P84 and decide the next lane (#538).
