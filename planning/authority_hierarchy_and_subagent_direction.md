# Authority Hierarchy And Subagent Direction

This note captures the emerging Agent Workbench design direction: treat
multi-agent development as a hierarchical authority system, not as a flat pool
of interchangeable model calls.

The goal is to reduce paid supervisor-token spend while preserving project
quality, reproducibility, and UBC-FRESH workflow discipline. The useful
question is not whether a local model is globally as good as a paid Codex
supervisor. The question is whether carefully scoped local agents can own
larger parts of the development process when their authority, context, tools,
termination signals, and audit surfaces are explicitly constrained.

## Authority Levels

### Developer

The developer is the top-level authority. This is normally the human project
lead.

Responsibilities:

- define project purpose, users, constraints, and success criteria;
- choose high-level research and engineering direction;
- decide which risks are acceptable;
- approve phase-scale roadmap direction;
- pay the paid-agent token bill;
- decide when a local-agent result is good enough for real project use.

The developer should not spend attention on repeated low-level status polling
or mechanical orchestration once the workflow contract is mature enough to
delegate that work.

### Deputy Developer / Coordinator

The coordinator is the paid high-capability agent lane today. In the current
prototype, this is Codex. In the target system, this role may eventually be a
free custom Copilot/Ollama agent when evidence shows that it can hold the role
reliably.

Responsibilities:

- translate developer intent into roadmap phases, planning notes, issue
  structure, and workflow tickets;
- decide which FreshForge-backed workflow graph applies to a phase or task;
- prepare bounded job tickets for supervisor agents;
- define acceptance gates and scoring rubrics;
- inspect compact supervisor reports rather than raw worker transcripts;
- own final escalation to the developer when the workflow is ambiguous or
  risky.

The coordinator should avoid reinventing orchestration rituals for every job.
Recurring work should become explicit workflow graph structure.

### Supervisor

The supervisor is the near-term free-agent target: a Copilot Chat agent using a
local Ollama model, currently most promising with Qwen3.6-style models.

Responsibilities:

- accept a coordinator-issued job ticket;
- identify whether the ticket maps to an existing Agent Workbench/FreshForge
  workflow graph;
- run the workflow graph within its permission boundary;
- launch worker jobs or subagents for bounded nodes;
- run validation and local repair loops;
- decide when to retry, repair, escalate, abort, or declare job completion;
- produce a compact QA/QC report for coordinator review.

The supervisor must stay in lane. It should not mutate GitHub state, merge
pull requests, close roadmap phases, or broaden the task without a ticket that
explicitly grants that authority.

### Workers

Workers are task-specialized local agents or model calls. They may run through
the Agent Workbench SDK path, Copilot Chat subagents, or later tool-enabled
agent shells.

Responsibilities:

- execute one bounded node;
- use only the context and tools assigned to that node;
- produce structured outputs with explicit uncertainty;
- stop when the ticket says to stop;
- avoid claims about workflow completion outside the node boundary.

Workers are replaceable implementation choices. A document-understanding node
may use Qwen3.6, a JSON-repair node may use Qwen3-Coder-Next, and a validation
critic node may use a different model family. The workflow contract should make
model choice configurable without changing authority semantics.

## Job-End Signals

Supervisor workflows need explicit end-state signals so the coordinator does
not waste paid tokens polling status or interpreting vague summaries.

Initial signal set:

- `job_complete`: workflow ran to the requested acceptance gate;
- `job_complete_with_caveats`: useful output exists, but caveats remain;
- `needs_coordinator_review`: supervisor cannot decide safely;
- `needs_developer_decision`: the issue is a product/research judgment;
- `job_failed`: workflow failed after allowed retries;
- `job_aborted`: supervisor stopped because continuing would violate the
  ticket, cost guardrail, or authority boundary;
- `job_partially_complete`: some graph nodes completed and later nodes were
  skipped or blocked.

Each signal must be paired with evidence, not prose alone.

## Workflow Graph Implication

The FreshForge-style workflow graph should become the structure that connects
authority levels:

```text
developer intent
  -> coordinator phase packet
  -> supervisor workflow graph activation
  -> worker/subagent node execution
  -> local audit and repair loop
  -> supervisor QA/QC packet
  -> coordinator acceptance or escalation
```

Graph nodes should declare:

- owner role: script, worker, supervisor, coordinator, or developer;
- allowed tools and files;
- input artifacts;
- output artifacts;
- scoring or validation gate;
- retry and repair policy;
- escalation signal.

This keeps orchestration reusable and makes supervisor cost easier to compress.
The paid coordinator should choose or amend a graph, not narrate ad hoc process
from scratch for every job.

## Subagent Direction

VS Code subagents are a promising implementation surface for the supervisor and
worker layers. They support focused work in isolated contexts, custom-agent
instructions, restricted tool lists, explicit subagent allow-lists, and
coordinator/worker orchestration patterns.

Near-term hypothesis:

> A custom Copilot supervisor agent can run a bounded Agent Workbench workflow
> and delegate selected nodes to custom subagents, while the paid Codex
> coordinator only inspects compact evidence and intervenes on escalations.

The first useful subagent spike should not try to automate a whole roadmap
phase. It should prove the following in a small workflow:

- custom supervisor agent can invoke a named subagent;
- subagent receives only the node-specific context;
- subagent uses the intended model and tool boundary;
- supervisor receives a compact result;
- supervisor can request one repair loop;
- final artifacts are written under ignored runtime paths;
- coordinator can verify the result from persisted evidence.

## Recent Evidence

The P55 seven-field supervisor A/B trial is the first positive evidence for
this direction. A free Copilot supervisor running a local Qwen3.6 model
completed a bounded adjudication task after the ticket was hardened with:

- explicit Agent Workbench workspace root;
- absolute source and output paths;
- one output artifact;
- one existence-check command;
- no GitHub or tracked-file authority;
- soft quote-length scoring instead of hard failure.

The retry result was contract-compliant and scored competitively with the paid
Codex supervisor on the bounded seven-field slice. The failed first ticket also
showed that ambiguous workspace roots and brittle path contracts can erase the
economics advantage. Ticket structure is therefore part of the system, not
mere prompt decoration.

## Near-Term Roadmap Implications

P56 should formalize the authority model, job-end signals, ticket contracts,
and coordinator/supervisor/worker graph mapping.

P57 should test VS Code custom agents and subagents as a real supervisor-worker
implementation surface, using ignored runtime artifacts and one narrow
document-indexing or repo-maintenance workflow.

Success for these phases is not full autonomy. Success is evidence that:

- the free supervisor stays inside its authority boundary;
- subagents reduce coordinator context and paid-token cost;
- repair/audit loops can run locally before paid supervisor inspection;
- final evidence is compact enough for coordinator review;
- failures terminate cleanly instead of looping.
