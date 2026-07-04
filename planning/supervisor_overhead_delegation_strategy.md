# Supervisor Overhead Delegation Strategy

## Context

The MP11 fixed-x8 bundle experiment showed a promising delegation signal, but
the measured paid-supervisor overhead still included substantial reporting and
orchestration cost. The overhead audit from `agent-delegation-lab` separated
benchmark-operation cost from task-quality work and showed that the largest
spans were:

- worker output summarization;
- worker run orchestration; and
- GitHub hygiene.

For future benchmark economics, GitHub hygiene should be excluded from the
core task-economics comparison. Repository governance can still require issue
and PR updates, but that is a separate governance-cost question rather than
part of the delegated task's intrinsic benefit-cost ratio.

## Keep GitHub Hygiene Out Of Benchmark Economics

GitHub workflow rituals are useful for repository discipline, but they do not
make the worker output better. They should be accounted for separately.

Recommended reporting split:

| Cost category | Included in task economics? | Rationale |
| --- | --- | --- |
| Worker run orchestration | Yes, but minimized | Required to execute the delegated task. |
| Worker output summarization | Yes, but should be delegated or scripted | Required to interpret the delegated task. |
| Source-level supervisor audit/repair | Yes | This is the real supervision cost. |
| GitHub issue/PR hygiene | No, tracked separately | Governance overhead, not task-quality work. |
| Changelog/roadmap sync | Separate or amortized | Governance/reporting overhead unless directly needed for the task. |

Future benchmark summaries should therefore report at least two totals:

```text
delegated_task_cost =
  orchestration
  + summarization
  + supervisor source audit/repair

repository_governance_cost =
  GitHub comments
  + PR updates
  + roadmap/changelog synchronization
```

This keeps the economic question honest: "Did delegation make the task itself
cheaper?" can be answered before debating whether the broader UBC-FRESH
governance ritual is too expensive.

## Delegating Worker Output Summarization

The worker-output summarization span is a strong candidate for delegation to a
local `gpt-oss:*` model. This task is different from high-level software
planning: it is bounded, evidence-oriented, and operates over already-sanitized
machine summaries.

Good local-worker summarization inputs:

- experiment summary JSON;
- experiment observation records;
- per-part status tables;
- token usage summaries;
- parse/error/anomaly counts;
- previous benchmark reference rows; and
- explicit questions to answer.

Bad local-worker summarization inputs:

- raw PDF text;
- raw provider traces;
- provider URLs or headers;
- broad project planning context;
- large unbounded chat transcripts; and
- authority to change tracked files directly.

The reporting worker should produce a draft packet, not a final conclusion:

```text
1. Compact factual summary.
2. Model/packaging comparison table.
3. Anomaly list.
4. Candidate interpretation.
5. Claims that require supervisor approval.
6. Recommended next audit target.
```

The paid supervisor should then review only that packet plus selected source
evidence, not the full raw output set.

## What Must Stay Supervisor-Owned

Delegating summarization does not mean delegating supervision.

The paid supervisor must still own:

- deciding whether a worker-generated interpretation is trustworthy;
- deciding whether a result is shape evidence, quality evidence, or economics
  evidence;
- deciding whether a benefit-cost claim is allowed;
- selecting which lane receives source-level audit;
- approving any tracked planning, benchmark, or issue-facing summary;
- rejecting plausible but unsupported worker claims; and
- deciding whether the next experiment changes strategy.

The supervisor should not spend paid tokens on:

- manually reformatting tables that scripts can write;
- reading raw outputs when scripts can extract counts and anomaly snippets;
- drafting routine GitHub progress comments;
- re-explaining stable workflow rituals; or
- ad hoc orchestration planning for a workflow shape that can be represented
  as a reusable graph.

## FreshForge Workflow Graphs For Orchestration Rituals

Worker orchestration is necessary, but it should not be reinvented by the paid
supervisor for every job. The better path is to express recurring Agent
Workbench rituals as FreshForge-style workflow graphs.

This aligns with the existing position in
`planning/freshforge_graph_dependency_opinion.md`:

```text
Agent Workbench agent semantics
  on top of
FreshForge graph records and validation
  around
project-native execution tools
```

The graph should define the work shape. Agent Workbench should interpret the
agent-specific semantics.

Example fixed-x8 bundle graph:

```text
prepare_manifest
  -> run_worker_parts
  -> validate_worker_outputs
  -> delegated_summary_draft
  -> supervisor_decision_packet
  -> supervisor_source_audit
  -> tracked_summary_update
```

Possible node ownership:

| Node | Likely owner | Notes |
| --- | --- | --- |
| `prepare_manifest` | script | Deterministic, no model needed. |
| `run_worker_parts` | script/orchestrator | Should run quietly and emit compact status. |
| `validate_worker_outputs` | script | Parse/schema/count/anomaly extraction. |
| `delegated_summary_draft` | local `gpt-oss:*` worker | Bounded reporting task over sanitized inputs. |
| `supervisor_decision_packet` | script + local worker draft | Should be compact and reviewable. |
| `supervisor_source_audit` | paid supervisor | Real supervision and quality control. |
| `tracked_summary_update` | script, supervisor-approved | Avoid hand-written repetitive prose. |

This graph can be reused across benchmark families. The supervisor should
choose or tune the graph, not reconstruct it from scratch.

## Why `gpt-oss` Is A Good Candidate For Reporting

The `gpt-oss:*` family may be better suited to reporting and synthesis than to
mutation-heavy software development. The fixed-x8 bundle test already suggests
that `gpt-oss:20b` can produce useful document-structure candidates, though it
also showed output-format risk in one lane.

Reporting tasks are a good fit because they can be:

- bounded to sanitized JSON/Markdown inputs;
- validated against required sections;
- constrained to short outputs;
- checked by the supervisor without rereading all worker outputs; and
- repeated cheaply when needed.

The first reporting-delegation test should probably use `gpt-oss:20b` before
`gpt-oss:120b`. If the smaller model produces reliable report drafts, the
larger model is unnecessary for this role. If the smaller model produces
format drift or weak interpretation, `gpt-oss:120b` becomes a reasonable
second test.

## Proposed Next Slice

The next implementation slice should attack the overhead directly:

1. Define a reusable reporting-worker ticket template.
   - Inputs: sanitized experiment summary JSON and prior-reference row.
   - Output: bounded Markdown or JSON decision packet.
   - Model: `gpt-oss:20b`.

2. Add a quiet batch-runner command or script.
   - Runs a directory of manifests.
   - Writes detailed logs under ignored runtime paths.
   - Prints only a compact status table.

3. Add a FreshForge-shaped orchestration graph template.
   - Represents the fixed-x8 benchmark ritual as reusable nodes.
   - Marks nodes as script-owned, local-worker-owned, or supervisor-owned.
   - Does not yet require full FreshForge execution.

4. Run a reporting-delegation A/B.
   - Baseline: paid supervisor summarizes a sanitized experiment packet.
   - Delegated: `gpt-oss:20b` drafts the report packet and the supervisor
     audits only the packet.
   - Compare paid supervisor cost and decision quality.

5. Keep GitHub hygiene out of the task economics.
   - Record it separately as governance overhead.
   - Use one compact comment only after the tranche.

## Success Criteria

This direction is working if:

- paid `worker_output_summarize` cost drops materially;
- supervisor source-level audit remains explicit and measured;
- local reporting-worker drafts are good enough to reduce supervisor reading
  and writing;
- FreshForge-shaped graph templates reduce ad hoc orchestration planning; and
- benchmark summaries distinguish task economics from governance overhead.

