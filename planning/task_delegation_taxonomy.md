# Task Delegation Taxonomy

Phase 32 defines the first shared vocabulary for deciding which UBC-FRESH
development task bundles are good candidates for worker delegation.

This taxonomy supports the P31 delegation economics model. It does not replace
supervisor judgment, model capability profiles, or project-specific priorities.
It gives supervisors a consistent way to classify candidate work before running
proposal workers.

## Planning Levels

Agent Workbench uses the UBC-FRESH project planning hierarchy:

```text
project -> phase -> task -> subtask
```

Delegation usually works best at the task or subtask level. Whole phases are
usually too broad for worker execution, but workers can help review, decompose,
or critique phase plans.

| Planning level | Typical delegation use | Default stance |
| --- | --- | --- |
| Project | Compare broad strategy or identify candidate pilot lanes. | Supervisor-owned; worker proposal only. |
| Phase | Review scope, split tasks, identify risks, draft acceptance criteria. | Split before delegation. |
| Task | Generate proposal evidence, review contracts, draft tests, inspect docs. | Best default unit for L1 work. |
| Subtask | Produce bounded text, checklist, analysis, or patch proposal. | Good when context is explicit. |
| Closeout | Verify evidence, merge PRs, close issues, publish releases. | Nondelegable by default. |

## Suitability Levels

| Suitability | Meaning | Typical action |
| --- | --- | --- |
| High | Worker output is likely useful and cheap to verify. | Delegate with L1 proposal-only ticket. |
| Medium | Worker output may help, but needs tighter framing or repeat runs. | Split, constrain, or compare models. |
| Low | Worker output may be noisy, risky, or expensive to verify. | Use only for brainstorming or do directly. |
| Avoid | Failure or cleanup risk dominates expected value. | Keep in supervisor lane. |

High-suitability tasks have explicit source material, clear output shape,
limited authority needs, and low cleanup cost. Avoid-suitability tasks require
hidden context, tracked-file mutation, GitHub/release authority, private data,
or broad architectural judgment.

## Task Type Matrix

| Task type | Description | Good planning level | Default suitability | Default authority | Expected worker value | Main risk |
| --- | --- | --- | --- | --- | --- | --- |
| Evidence intake | Summarize supplied issues, roadmaps, docs, logs, or local evidence. | Task or subtask | High | L1 proposal-only | Fast breadth-first synthesis and gap spotting. | Unsupported claims or missed caveats. |
| Compatibility map | Classify friction by owner, boundary, or existing API surface. | Task | High | L1 proposal-only | Helps separate core, provider, supervisor, and deferred concerns. | Overconfident ownership assignments. |
| Contract/schema proposal | Propose fields, record shapes, output formats, or API boundaries. | Task | Medium-high | L1 proposal-only | Produces candidate contracts and alternatives. | Invented fields not supported by current code. |
| Test-design proposal | Draft unit, CLI, docs, smoke, and regression test plans. | Task or subtask | High | L1 proposal-only | Usually cheap to verify against code and roadmap. | Platform-fragile or overbroad tests. |
| Documentation proposal | Draft docs outline, acceptance criteria, examples, or explanatory text. | Subtask | Medium-high | L1 proposal-only | Produces useful prose scaffolds. | Bland content or hidden unsupported assumptions. |
| Roadmap review | Review phase/task sequencing, scope boundaries, and acceptance criteria. | Phase or task | Medium | L1 proposal-only | Helps find missing tasks and scope creep. | Too abstract unless supplied concrete roadmap text. |
| Issue triage | Suggest child issues, labels, issue body sections, or closeout checklist. | Task | Medium | L1 proposal-only | Drafts structure for supervisor to post. | Worker may assume GitHub state it did not verify. |
| Patch proposal | Propose a code change or diff without mutating tracked files. | Subtask | Medium | L1 proposal-only | Can identify likely edit locations and edge cases. | Patch may be stale, partial, or untested. |
| Mechanical text edit | Apply or propose rote formatting in ignored scratch artifacts. | Subtask | Medium | L2 supervisor-applied mutation only | Useful when supervisor tooling can constrain target. | Direct tracked-file edits are still forbidden. |
| Restricted sandbox trial | Use approved tools in ignored runtime paths. | Subtask | Low-medium | L3 restricted sandbox | Can test narrow tool behavior. | Tool overreach or hard-to-verify side effects. |
| Implementation mutation | Edit tracked code, docs, tests, or package metadata. | Subtask | Low | Supervisor-owned by default | Worker may inform design, not own mutation. | Cleanup cost and regression risk. |
| GitHub hygiene | Draft comments, PR body text, or issue body updates. | Subtask | Medium for drafts; avoid for mutation | L1 drafts only | Can produce paste-ready text. | Actual posting/closure must be supervisor-owned. |
| Release closeout | Version bumps, tags, artifact checks, PyPI/GitHub releases. | Closeout | Avoid | L6 nondelegable | Worker can draft checklist only. | High consequence and stateful external systems. |
| Parent phase closeout | Merge PR, close parent issue, sync main, delete branch. | Closeout | Avoid | L6 nondelegable | Worker can draft state machine only. | False completion claims or bad GitHub state. |
| Domain interpretation | Interpret forestry, energy, model validation, or project science outputs. | Task | Low unless source is explicit | L1 proposal-only | May surface questions. | Domain mistakes can look plausible. |

## Good Delegation Candidates

Delegate when most of these are true:

- the task uses supplied public-safe text or repo-local evidence;
- the requested output is bounded Markdown, JSON-like structure, or a patch
  proposal;
- the supervisor can verify the output cheaper than producing it from scratch;
- raw worker artifacts can stay under ignored runtime paths;
- tracked-file and GitHub mutation are not required;
- the ticket can list required sections and forbidden claims; and
- failure can be rejected without cleanup.

Examples:

- summarize downstream friction from a roadmap and planning note;
- propose evidence manifest fields from existing run records;
- draft compatibility tests for a CLI option;
- identify which worker claims need proof before promotion;
- compare two possible task splits for a phase.

## Poor Delegation Candidates

Do not delegate when any of these are true:

- private data, credentials, endpoint details, or raw transcripts must be
  exposed to the worker;
- success requires tracked-file mutation by the worker;
- success requires GitHub issue edits, issue closure, PR creation, PR merge, or
  release publication by the worker;
- the output cannot be independently verified;
- failure would create hidden repo state that is expensive to unwind;
- the task depends on broad unstated project context; or
- a false positive would be more expensive than direct supervisor work.

Examples:

- merge a PR and close a phase;
- publish a package release;
- decide domain-science correctness from incomplete evidence;
- run broad implementation with ambiguous acceptance criteria;
- change model/provider configuration.

## Split-Or-Supervise-More Cases

Some task bundles are not bad candidates, but they are too broad as written.
Split or tighten the ticket when:

- the task covers more than one roadmap task;
- the output mixes evidence intake, implementation design, and closeout;
- the worker would need to infer current GitHub state;
- the task asks for both proposal and mutation;
- repeated runs are needed to judge consistency;
- multiple models may have different strengths; or
- the likely useful answer is a list of candidate subtasks, not a final result.

Split examples:

- "finish P15" becomes manifest-field proposal, compatibility-test proposal,
  downstream-consumption proposal, then supervisor implementation.
- "review FreshForge P16" becomes provider evidence-field proposal,
  provider-boundary risk review, and docs/test acceptance proposal.
- "clean up roadmap" becomes stale-status audit, issue-map consistency review,
  and wording proposal.

## Authority Defaults

Use the trust levels from `planning/delegation_policy.md`.

| Task type | Default maximum level | Notes |
| --- | ---: | --- |
| Evidence intake | L1 | No-tool proposal with claim review. |
| Compatibility map | L1 | Supervisor owns final ownership calls. |
| Contract/schema proposal | L1 | Worker proposes; supervisor checks current code. |
| Test-design proposal | L1 | Worker proposes; supervisor implements and runs tests. |
| Documentation proposal | L1 | Supervisor edits tracked docs. |
| Roadmap review | L1 | Supervisor updates roadmap and issues. |
| Issue triage | L1 | Worker drafts; supervisor uses `gh`. |
| Patch proposal | L1 | No tracked mutation by worker. |
| Mechanical text edit | L2 | Only through supervisor-owned tooling and allowed sandbox targets. |
| Restricted sandbox trial | L3 | Ignored runtime paths only, with observed tool evidence. |
| Implementation mutation | Supervisor-owned | Treat worker output as proposal evidence. |
| GitHub hygiene | L1 for drafts; L5 forbidden | `gh` mutation is supervisor-owned. |
| Release closeout | L6 forbidden | Supervisor-only. |
| Parent phase closeout | L6 forbidden | Supervisor-only. |
| Domain interpretation | L1 | Use as question generation unless source evidence is explicit. |

## Candidate Restricted-Tool Experiments

Future restricted-tool trials may be useful for:

- reading ignored runtime artifacts and summarizing them;
- writing generated drafts under ignored `tmp/` or `runtime/` paths;
- running read-only CLI help or smoke commands in a sandbox;
- comparing two worker result files; and
- producing a patch proposal file that the supervisor applies manually.

These remain trials. They do not change the default prohibition on tracked-file
mutation, GitHub mutation, release work, or phase closeout.

## Supervisor Checklist

Before launching a worker ticket, answer:

1. What task type is this?
2. What roadmap level is it: phase, task, or subtask?
3. What is the default suitability level?
4. What authority level is allowed?
5. What evidence will prove the worker result is useful?
6. What would cleanup cost if the worker is wrong?
7. Is the task too small, too broad, or missing context?
8. Would doing it directly be cheaper?

If those answers are unclear, refine the task before delegation.
