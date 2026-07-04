# Delegation Economics Vision

Agent Workbench should now shift from proving that worker agents can do useful
work to proving that worker delegation can produce positive net value on real
UBC-FRESH projects.

The important question is not whether a local Ollama-backed worker can generate
a plausible answer. That has already been demonstrated. The important question
is whether a supervisor using Agent Workbench can complete useful project work
with less paid supervisor-token effort than the supervisor would have spent
doing the work directly.

## Core Objective

Agent Workbench should help answer this question:

```text
When should a paid supervisor agent delegate a task bundle to a self-hosted
worker model, and when is delegation likely to cost more than it saves?
```

The desired outcome is not full autonomy. The desired outcome is a disciplined
supervisor-worker system that consistently finds task bundles where local
worker effort is cheaper than direct paid-supervisor effort after all overhead
and risk are counted.

## Why Simple Worker Success Is Not Enough

A worker run can look successful and still be economically bad.

Delegation loses value when:

- the task is so small that ticket-writing and review cost more than direct
  execution;
- the task is too broad or ambiguous for the worker model;
- the worker produces plausible but unsupported claims;
- supervisor verification becomes as expensive as doing the task directly;
- failures require cleanup, rollback, or patch-forward repair;
- repeated retries burn supervisor attention without producing usable output;
  or
- the supervisor eventually gives up and does the task directly after already
  paying delegation overhead.

A successful delegation is therefore not just a correct worker output. It is a
correct or useful worker output whose total supervised workflow cost is lower
than the direct-work counterfactual.

## Working Net-Benefit Model

The first planning model can be simple and explicit:

```text
expected net benefit =
  avoided paid-supervisor effort
  - delegation setup effort
  - supervisor verification effort
  - retry and context-switching effort
  - probability_of_failure * expected_cleanup_cost
```

This does not need to be perfectly calibrated at first. It needs to be concrete
enough that the supervisor can compare candidate delegation decisions and learn
from real outcomes.

## Decision Variables

The supervisor controls several variables that affect the outcome:

- task type;
- task size;
- roadmap level: phase, task, or subtask;
- worker model;
- ticket structure;
- number of repeated worker runs;
- authority level;
- allowed tools and files;
- claim-review strictness;
- retry limits;
- bailout threshold; and
- whether the task should be split, merged, deferred, delegated, or done
  directly.

The developer controls the larger project roadmap and priority structure.
Agent Workbench should optimize within that roadmap rather than attempting to
replace project-level judgment.

## Task Bundle Framing

UBC-FRESH projects already organize work as:

```text
phase -> task -> subtask
```

That hierarchy should become part of Agent Workbench's delegation model. A
candidate delegation is not just "ask a worker to do something"; it is a choice
to delegate a specific task bundle at a specific planning level to a specific
worker model under a specific protocol.

The useful region is likely a Goldilocks zone:

- too small: overhead dominates;
- too large: failure and cleanup risk dominate;
- just right: worker effort narrows, drafts, reviews, or proposes enough useful
  work that supervisor verification is cheaper than direct execution.

## Model-Specific Fit

Different local worker models should not be treated as interchangeable.

Agent Workbench should build evidence-scoped capability profiles for each
installed model, including:

- task types where the model has produced useful outputs;
- task types where it fails or loops;
- ticket shapes that improve reliability;
- output formats it follows well;
- authority levels that appear safe;
- failure modes that require early stop conditions; and
- model-specific retry or repeat-run guidance.

The goal is not to rank models globally. The goal is to choose a good
task-model-protocol combination for the work actually in front of the
supervisor.

## Evidence Program

The next development phase should collect data that helps answer whether
delegation is economically useful.

Each real-project pilot should record:

- project and roadmap location;
- task type and size;
- selected worker model;
- protocol and authority level;
- setup effort;
- worker runtime and output classification;
- verification effort;
- accepted, rejected, and needs-evidence claims;
- cleanup or repair effort;
- whether the worker changed the supervisor's decision;
- estimated direct-work counterfactual; and
- final supervisor judgment of net benefit.

The first target is not global optimality. The first target is evidence that
some non-trivial task classes reliably produce positive net benefit.

## Near-Term Roadmap Implication

The next Agent Workbench tranche should focus on delegation economics rather
than more bridge mechanics:

- define the cost and risk model;
- classify task types and suitability;
- create worker model capability profiles;
- implement a transparent rules-based delegation recommender;
- run real-project pilots with explicit accounting; and
- tune the policy based on observed outcomes.

Machine-learning policy optimization should wait. A transparent rules-based
system is easier to audit, easier to debug, and better aligned with the current
amount of evidence. Once enough real delegation records exist, an ML policy or
hyperparameter optimizer may become worth testing.

## Parallelization Analogy

The closest engineering analogy is parallelizing code. Parallel execution helps
only when the speedup exceeds the overhead of coordination, synchronization,
debugging, and failure handling.

Agent delegation has the same structure, but with more dimensions:

- model capability;
- task ambiguity;
- ticket quality;
- authority level;
- verification cost;
- cleanup risk;
- project criticality; and
- supervisor attention.

Agent Workbench should make those dimensions explicit enough that the
supervisor can make better delegation decisions over time.
