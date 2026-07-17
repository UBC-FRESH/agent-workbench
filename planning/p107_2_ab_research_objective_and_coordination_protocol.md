# Superseded P107.2 A/B Research Objective and Coordination Protocol

> Superseded by [P107 Configuration Economics Research Program](p107_economics_research_program.md).
> Retained as history of the rejected Retail-baseline design.

## Status and purpose

This is a planning correction recorded before any further live P107.2
execution. It is deliberately more important than the current narrow
P107.2 proof prompt. It captures the maintained research question, the
meaning of the Agent Hub roles, and the requirements for an informative A/B
comparison.

It does not authorize a live run, change model/provider configuration, create
GitHub state, or claim that economics have been measured.

## The point of Agent Workbench

Agent Workbench exists to determine whether a supervised multi-agent
development workflow can make UBC-FRESH development work more useful, less
expensive, and less demanding of the maintainer's attention than relying on
one out-of-the-box retail Codex agent.

The project is not principally about proving any of the following in
isolation:

- that a local Worker can emit structured JSON;
- that one recursive spawn edge exists;
- that a particular prompt satisfies a formatting rubric;
- that a model can make a patch in a toy fixture; or
- that token counts can be recorded.

Those are enabling observations. They matter only insofar as they help answer
the central practical question:

> Can the complete Agent Workbench system deliver equally useful real
> development work with less paid-token spend and less maintainer steering
> burden than a single retail Codex agent?

The current practical problem is not merely model capability. A single retail
agent requires the maintainer to repeatedly restore context, identify the
next useful step, notice failures, correct its course, review its work, and
carry the project forward. That absorbs paid tokens and maintainer attention.
Agent Workbench is intended to make a thin paid coordination layer actively
manage lower-cost local Worker effort so that the maintainer is not manually
dragging one agent through every recovery and implementation step.

## Agent Hub responsibility model

The expected treatment hierarchy is:

~~~
Maintainer
  -> Coordinator
       -> Supervisor
            -> local Worker
~~~

The roles are not interchangeable.

### Maintainer

The maintainer owns the real project objective, chooses whether a line of work
is worth pursuing, and authorizes scope/budget changes. The maintainer is not
the routine acceptance reviewer in the planned A/B test.

### Coordinator

The Coordinator owns the Workbench lane's outcome. It is not a passive
transcript collector and is not an external contaminant to that lane.

It must:

1. give the Supervisor a self-contained task and acceptance contract;
2. inspect actual artifacts, diffs, test output, and raw session evidence;
3. reject unacceptable results with a concrete defect packet;
4. direct the Supervisor to obtain a bounded repair from its Worker;
5. independently revalidate after every response; and
6. stop only at the declared lane limit or a verified acceptance result.

The paid token/time cost of this active management is part of the Workbench
treatment and must be measured. It is exactly the capability whose value is
under study.

The Coordinator must not silently implement a Worker-owned task itself. Doing
so creates a different system and obscures whether the delegation hierarchy
provided useful leverage.

### Supervisor

The Supervisor manages the Worker, rather than merely relaying Worker prose.
It must inspect the task result, distinguish a Worker final message from
verified acceptance, report specific evidence to the Coordinator, and carry a
Coordinator-issued defect packet back to the Worker for a bounded repair.

### Worker

The Worker performs the narrowly delegated implementation or analysis. Its
prose final response is untrusted evidence. A Worker failure is expected input
to the supervisory control loop, not by itself a reason to end the Workbench
lane.

## Why earlier P107.2 wording is unsuitable for the A/B question

The existing fresh P107.2 prompt was designed as a narrow recursive proof. It
therefore says, in effect, “one chain and no retry,” limits the Supervisor to
one spawning action, asks it to return only the Worker session ID/final
response, and tells the Coordinator to inspect logs after the Supervisor has
ended.

That wording measures a one-shot Worker relay. It does not exercise the
Coordinator/Supervisor recovery loop and therefore cannot establish whether
Agent Workbench reduces real development cost or maintainer effort.

In particular, these formulations must not be reused unchanged for the A/B
implementation run:

- “run exactly one native chain and no retry”;
- “first and only agent-management action” without an explicit repair path;
- “return only its session ID and exact final response”; and
- a Coordinator instruction limited to post-run recording.

For a true Workbench treatment, the Coordinator must remain responsible for
artifact-driven acceptance and bounded remediation. Protocol fidelity is
important, but it is supporting evidence, not the research outcome.

## Informative A/B design

### Unit of comparison

Compare two whole development systems on one realistic, bounded, generic
feature resembling work that might arise in a UBC-FRESH software project. The
feature must be independently useful; it must not be a pure delegation
demonstration.

The proposed provenance/source-audit CLI is a suitable candidate only when
the test is rebuilt from a clean common baseline and the acceptance fixture is
frozen before either lane begins.

### Common controls

Both lanes must receive:

- the identical clean starting commit;
- isolated clean worktrees created from that commit;
- the same self-contained implementation ticket;
- the same permitted file list and command boundaries;
- an immutable, Coordinator-owned acceptance fixture and test command;
- the same practical usability rubric; and
- a fresh Codex session for the lane, so neither lane inherits conversational
  context from setup, the other lane, or a prior repair.

The acceptance fixture is not editable by either implementation lane. It is
the common external criterion, not an artifact that each agent is allowed to
author and then pass.

### Retail baseline

The Retail lane is one fresh, standard, out-of-the-box retail Codex agent.
It receives the common ticket. It may implement, test, and revise its work
within the ticket boundary.

### Agent Workbench treatment

The Workbench lane is one fresh Coordinator session followed by the native
Coordinator -> Luna Supervisor -> local Qwen Coder Worker hierarchy. Each
spawned role starts with no inherited conversational context and therefore
receives a complete self-contained instruction.

The Coordinator has an active control-loop responsibility. It must verify
actual artifacts and direct the Supervisor through bounded Worker repairs when
the acceptance evidence identifies a concrete defect.

### Independent reviewer

The reviewer is the Advisor subagent, not the maintainer and not the
Workbench Coordinator. The Advisor is lane-neutral:

- it runs the frozen acceptance suite;
- applies the same concise practical-usability rubric to each final diff;
- writes a concrete evidence-based defect packet if the result is
  unacceptable; and
- does not implement, modify, or manage either lane's work.

The Advisor must be spawned in a new Codex session for each lane review so
that its judgment begins from a fresh context window. Its review instructions
must identify the exact baseline, immutable acceptance fixture, lane worktree,
and output format.

### Review and repair rounds

Allow up to three Advisor review rounds in each lane.

For every round:

1. Advisor reviews the actual lane artifact with the common fixture and rubric.
2. If accepted, the lane ends.
3. If rejected, Advisor emits a defect packet containing exact failed command
   output, affected paths/behavior, and the acceptance condition for repair.
4. Retail receives that packet directly as its next bounded correction.
5. Workbench Coordinator receives that packet and directs Luna; Luna delegates
   a bounded Worker repair and verifies the returned artifact before replying.
6. Advisor conducts the next review from a fresh Codex session.

The same maximum of three review rounds applies to each lane. Review rounds,
repair attempts, token spans, elapsed time, and all human-maintainer
interventions must be recorded separately. A lane may stop earlier for
acceptance or a declared non-recoverable blocker.

## Decision record and interpretation

For each lane, record:

- verified useful completion: frozen tests plus Advisor practical-usability
  acceptance;
- all paid-session token spans and elapsed time, with session identifiers;
- any available cash estimate and its pricing provenance;
- local Worker runtime/cost data separately from paid costs;
- count, kind, and contents of Advisor defect packets;
- count and kind of Coordinator/Supervisor interventions;
- count of maintainer interventions;
- whether each repair succeeded; and
- raw session-log and diff/test-output locations.

The comparison is outcome-first:

1. A lane that cannot deliver a useful feature loses regardless of token cost.
2. If both lanes deliver useful features, compare paid cost and maintainer
   steering burden.
3. Workbench coordination cost is part of the Workbench result, not an
   exclusion or a third lane.
4. Do not infer economic value from isolated Worker success, one clean spawn,
   or formatting compliance alone.

## Operating guardrail

When an unacceptable Worker result arrives, the Coordinator's required next
question is:

> What exact evidence shows the defect, and what bounded instruction must the
> Supervisor give the Worker to repair it?

It is not:

> Has the Worker emitted a final response that permits the run to be recorded?

This distinction is the practical point of the Agent Hub structure and must
remain visible in any future P107.2 ticket, prompt, run packet, or review.
