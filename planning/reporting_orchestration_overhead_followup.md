# Reporting And Orchestration Overhead Follow-Up

## Purpose

The MP11 delegated-document experiments showed that local worker calls can
produce useful structure evidence at zero cash cost, but the benchmark can still
lose if the paid supervisor spends too many tokens on orchestration,
summarization, and governance prose. Future experiments should separate task
economics from repository governance and should move bounded reporting work to
local workers wherever possible.

## Economics Boundary

GitHub issue comments, PR updates, branch hygiene, roadmap sync, and changelog
sync are governance costs. They may still be required by repository policy, but
they should not be included in the core delegated-task benefit-cost ratio.

The task-economics lane should include only:

- worker run orchestration required to execute the delegated job;
- worker output summarization required to understand the job result;
- supervisor source-level audit and repair required for real supervision; and
- direct supervisor baseline cost when the paid supervisor performs the same
  work without delegation.

Governance costs should be reported separately or amortized later.

## Delegatable Reporting Work

Worker-output summarization is a strong candidate for local delegation. The
summary worker should operate only on sanitized packets such as summary JSON,
model/package comparison tables, token records, anomaly counts, and prior
benchmark rows. It should not receive raw document text, provider traces,
headers, endpoint details, or broad project context.

The first reporting role should use `gpt-oss:20b` because reporting is a
bounded synthesis task rather than a broad mutation-heavy software task. The
worker should draft a compact decision packet, not make final claims.

Supervisor-owned work remains:

- deciding whether worker interpretation is trustworthy;
- deciding whether a result is shape evidence, quality evidence, or economics
  evidence;
- approving or rejecting net-savings claims;
- selecting and performing source-level audit targets; and
- approving tracked summaries.

## Orchestration As A Workflow Graph

Worker orchestration is real work, but it should not be ad hoc prompt-planned
for every benchmark. Agent Workbench should represent recurring benchmark
rituals as FreshForge-shaped workflow graphs:

```text
collect_sanitized_inputs
  -> run_worker_batch
  -> validate_worker_outputs
  -> draft_reporting_summary
  -> supervisor_review
  -> source_level_audit
  -> tracked_update
```

Node ownership should be explicit:

| Node | Owner | Cash-cost expectation |
| --- | --- | --- |
| `collect_sanitized_inputs` | Script | Near zero |
| `run_worker_batch` | Script | Near zero |
| `validate_worker_outputs` | Script | Near zero |
| `draft_reporting_summary` | Local worker | Zero cash |
| `supervisor_review` | Paid supervisor | Small, bounded |
| `source_level_audit` | Paid supervisor | Necessary supervision |
| `tracked_update` | Script plus supervisor approval | Minimized |

This structure lets the supervisor choose or tune a graph rather than
reinventing orchestration logic with paid tokens every time.

## Immediate Leads

The next useful implementation leads are:

1. Use `agent-workbench eval-batch` for quiet batch orchestration so detailed
   logs stay under ignored runtime paths and the supervisor sees only compact
   status.
2. Use a reporting-worker ticket template for local `gpt-oss:*` summaries over
   sanitized packets.
3. Track reporting-worker input/output tokens separately from paid supervisor
   source-audit tokens.
4. Treat source-level supervisor audit as the first-class supervision cost.
5. Keep GitHub hygiene outside the task-economics ledger until a separate
   governance-cost study is intentionally opened.

## Careful Opinion

This is the right direction. Delegating the original high-level planning problem
to local models was a weak starting point because it asked lower-reliability
workers to make broad judgment calls. Delegating bounded summarization over
sanitized experiment packets is much more promising: the inputs are structured,
the output can be section-validated, and the supervisor can audit the result
without rereading every raw worker output.

The workflow-graph idea also addresses the largest avoidable supervisor cost.
If orchestration is encoded as reusable graph structure, the paid supervisor no
longer has to spend tokens re-deriving the same run, validate, summarize, audit,
and report ritual. FreshForge should provide graph definition and validation
patterns; Agent Workbench should add agent roles, token accounting, model
selection, and evidence semantics on top.

The risk is premature automation. The next step should not be a full workflow
engine. It should be a small set of graph-shaped templates plus quiet commands
that make the supervisor's review surface smaller and more repeatable.
