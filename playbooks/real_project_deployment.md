# Real-Project Deployment Playbook

Use this playbook to deploy Agent Workbench on a real UBC-FRESH project while
keeping worker agents in a proposal-assist role.

## 1. Select The Target

Start only when there is a real project issue, roadmap phase, or maintainer
request that can benefit from worker proposal assistance.

Classify the candidate task bundle with
`planning/task_delegation_taxonomy.md` before scaffolding tickets. Prefer task
or subtask bundles with high or medium suitability. Split whole-phase requests
before delegation.

Select a worker model from `model_profiles/` after classification. A model
profile is usable only for the task families, harnesses, and authority levels it
actually covers. If the selected model profile is planned, partial, or missing,
run a marker or no-tool proposal probe before using it on project work.

For non-obvious cases, render a supervisor-side decision report before
scaffolding tickets:

```powershell
agent-workbench decide task `
  --input tmp/agent_workbench/<phase>/<task>.decision.json `
  --output tmp/agent_workbench/<phase>/<task>.decision.md
```

Use the result to decide whether to delegate, split the task, defer until model
evidence exists, or keep the work in the supervisor lane.

Supervisor checks:

- target project is clean on the intended base branch;
- governing issue or roadmap phase is identified;
- task type, planning level, and default worker authority are identified;
- selected model profile supports the proposed task shape;
- any decision report recommendation has been reviewed by the supervisor;
- target project has an ignored local work area such as `tmp/`;
- provider credentials and endpoints are already configured outside tracked
  files; and
- worker authority can remain no-tool or proposal-only.

Stop if the task requires private data exposure, immediate tracked-file
mutation by a worker, GitHub closeout by a worker, or broad unsupervised
implementation.

## 2. Scaffold A Proposal Pack

Create bounded worker tickets under an ignored target-project path:

```powershell
agent-workbench pilot pack-scaffold `
  --project-root <target-project> `
  --output-dir tmp/agent_workbench/<phase> `
  --mode proposal `
  --task evidence-intake="Summarize the supplied evidence" `
  --task implementation-proposal="Propose a bounded implementation slice" `
  --task docs-acceptance="Propose docs, tests, and acceptance checks"
```

Review each generated ticket before running workers. Add project-specific
context directly to the ignored ticket files, not to tracked Agent Workbench
docs.

## 3. Run Workers

Run each manifest with the target project as the project root:

```powershell
agent-workbench eval `
  --project-root <target-project> `
  --manifest tmp/agent_workbench/<phase>/<task>.manifest.json
```

Worker boundaries:

- no tools unless a later phase explicitly approves a restricted-tool trial;
- no tracked-file edits;
- no GitHub mutation;
- no release or closeout authority; and
- no claims of completion without supervisor verification.

## 4. Prepare Evidence Summaries

Populate each evidence summary with sanitized supervisor review:

- source runtime paths;
- classification outcomes;
- verification commands or inspections;
- supervisor decision;
- `accepted_claims`;
- `rejected_claims`; and
- `needs_evidence_claims`.

Validate and render each summary:

```powershell
agent-workbench evidence validate --input <summary.evidence.json>
agent-workbench evidence render --input <summary.evidence.json> --output <summary.evidence.md>
```

Use `templates/claim_review_checklist.md` before promoting worker claims.

## 5. Synthesize The Decision Packet

Create one supervisor packet:

```powershell
agent-workbench evidence synthesize `
  --input-dir tmp/agent_workbench/<phase> `
  --output tmp/agent_workbench/<phase>/supervisor_decision_packet.md
```

The packet is an input to supervisor judgment. It is not proof that worker
claims are true.

## 6. Optional Model/Repeat Comparison

When multiple models or repeats were run for the same ticket family, compare
existing eval summaries:

```powershell
agent-workbench compare eval `
  --input tmp/agent_workbench/<phase>/eval/<task>/summary.json `
  --output tmp/agent_workbench/<phase>/eval_comparison.md
```

Use the comparison only for that ticket family. Do not promote broad model
rankings.

Promote stable findings into `model_profiles/` only after supervisor review.
Record whether the comparison changes the recommended model, retry limit,
authority ceiling, or stop condition for that task family.

## 7. Pilot Accounting

For real-project pilots, create one sanitized accounting record per task/model
run using `templates/pilot_accounting_record.json` as the starting point.

Each record should include:

- paid supervisor input/output token counts and prices;
- worker input/output token counts and prices;
- verification, cleanup, and retry token counts;
- accepted, rejected, and needs-evidence claim counts;
- whether worker output changed the supervisor decision; and
- a final outcome classification.

Validate and render each record:

```powershell
agent-workbench accounting validate --input <pilot.accounting.json>
agent-workbench accounting render `
  --input <pilot.accounting.json> `
  --output <pilot.accounting.md>
```

Synthesize the pilot batch:

```powershell
agent-workbench accounting synthesize `
  --input-dir tmp/agent_workbench/<phase> `
  --output tmp/agent_workbench/<phase>/pilot_accounting_synthesis.md
```

Use this synthesis to distinguish useful imperfect proposals from costly
failures. Do not treat net savings as stable until the pilot set includes varied
task/model/protocol records.

## 8. Supervisor Promotion

Only the supervisor may mutate tracked project files, GitHub issues, branches,
pull requests, releases, or closeout state.

Promotion gate:

- accepted claims are evidence-supported;
- rejected claims are excluded or explicitly recorded as rejected;
- needs-evidence claims are deferred;
- implementation scope is bounded;
- target project verification commands are known; and
- raw worker outputs remain ignored.

## 9. Cleanup

Keep raw tickets, manifests, model outputs, and provider scratch state under the
target project's ignored local work area. Do not commit them.

Tracked promotion may include:

- sanitized planning notes;
- roadmap/changelog updates;
- code/docs/tests implemented by the supervisor; and
- issue or PR comments written by the supervisor.

Before closeout, run the target project's normal verification and check:

```powershell
git status --short --branch
git diff --check
```

Search tracked files for private paths, credentials, raw transcript fragments,
and unrelated project contamination.

## 10. Stop Conditions

Stop worker use and keep work in the supervisor lane when:

- workers loop or repeat completion claims;
- workers invent unsupported evidence;
- tickets require hidden context not safe to provide;
- outputs contain private paths, credentials, or raw transcript material;
- worker suggestions require broad architecture decisions;
- model behavior varies across repeats in a way that affects correctness; or
- the next action is tracked-file mutation, GitHub mutation, release, or
  closeout.
