# Delegation Economics Strategy

Agent Workbench has proven that a supervised local-worker pattern can produce
useful proposal evidence on real UBC-FRESH project work. The next planning
problem is larger than bridge reliability or template quality: determine whether
the workflow can consistently reduce paid supervisor-token cost per useful
merged unit of work.

The core question is:

```text
Can a supervisor using Agent Workbench plus self-hosted Ollama workers complete
real project work with lower total paid-supervisor effort than the supervisor
would have spent doing the same work directly?
```

Worker success is not sufficient evidence. A worker result is valuable only if
the accepted value exceeds delegation setup, review, retry, cleanup, and
context-switching costs.

## Decision Frame

For each candidate task bundle, the supervisor must decide:

```text
delegate(task_bundle, worker_model, protocol, authority_level)
```

The expected value of that decision can be approximated as:

```text
net benefit =
  avoided paid-supervisor effort
  - delegation setup effort
  - supervisor verification effort
  - retry and context-switching effort
  - probability_of_failure * expected_cleanup_cost
```

The task-bundle dimension follows the UBC-FRESH planning hierarchy:

```text
project -> phase -> task -> subtask
```

Very small bundles lose to overhead. Very large or ambiguous bundles lose
because worker failure risk and cleanup cost rise. The useful operating zone is
between those extremes and will vary by task type, worker model, ticket shape,
project maturity, and authority level.

## Optimization Variables

The supervisor has agency over several variables:

- task type and task size;
- worker model selection from the installed Ollama inventory;
- ticket structure and specificity;
- number of repeated worker runs;
- authority level, from no-tool proposal work through restricted tool use;
- acceptance and claim-review strictness;
- retry limits and bailout thresholds; and
- whether to split, merge, defer, or do the task directly.

The larger project roadmap remains developer-defined. Agent Workbench optimizes
within that roadmap rather than replacing developer judgment about project
importance, schedule, or scientific/software priorities.

## Evidence Needed

The next phases should collect evidence for whether the system can win on real
work, not merely whether workers can generate plausible responses.

Useful evidence includes:

- task type and roadmap level;
- selected worker model and protocol;
- supervisor setup effort;
- worker runtime and output classification;
- supervisor verification effort;
- accepted, rejected, and needs-evidence claims;
- implementation effort after worker review;
- defects or cleanup caused by worker output;
- whether delegation changed the final implementation decision; and
- supervisor judgment of likely direct-work counterfactual.

The first target is not global optimality. The first target is a credible,
repeatable argument that some non-trivial classes of UBC-FRESH development work
produce positive net benefit when delegated under disciplined supervision.

## Analogy

The problem resembles parallelizing single-threaded code: parallel workers help
only when speedup exceeds coordination overhead. Agent delegation adds more
dimensions because worker reliability, prompt quality, model fit, verification
cost, and cleanup risk all vary across tasks.

## Strategic Implication

The roadmap should pivot from building isolated bridge features toward an
empirical delegation policy:

- define the economics model;
- classify task types and delegation suitability;
- record per-model capability profiles;
- build a rules-based delegation decision engine;
- pilot the decision engine on real projects; and
- tune policy from observed outcomes.

Machine-learning policy optimization is premature until enough real delegation
records exist. Rules and transparent scoring should come first.
