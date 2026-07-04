# Delegation Economics Strategy

Agent Workbench has proven that a supervised local-worker pattern can produce
useful proposal evidence on real UBC-FRESH project work. The next planning
problem is larger than bridge reliability or template quality: determine whether
the workflow can consistently reduce paid supervisor-token cost per useful
merged unit of work.

The core question is:

```text
Can a supervisor using Agent Workbench plus self-hosted Ollama workers complete
real project work with lower total paid-supervisor token/cash cost than the
supervisor would have spent doing the same work directly?
```

Worker success is not sufficient evidence. A worker result is valuable only if
the accepted value exceeds paid-supervisor setup tokens, review tokens, retry
tokens, cleanup tokens, and any practical context-switching friction.

## Decision Frame

For each candidate task bundle, the supervisor must decide:

```text
delegate(task_bundle, worker_model, protocol, authority_level)
```

The expected value of that decision can be approximated as:

```text
net benefit =
  direct paid-supervisor token cost
  - delegated paid-supervisor token cost
  - self-hosted worker token cost
  - probability_of_failure * expected paid-supervisor cleanup token cost
```

The primary unit is token-priced cash cost, not wall-clock minutes. Local worker
latency matters only when it creates real workflow friction or blocks the
developer; the supervisor agent does not burn much paid API cost while waiting.

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
- direct paid-supervisor input/output token estimate;
- delegated paid-supervisor input/output tokens;
- worker input/output tokens;
- token price assumptions;
- worker runtime and output classification;
- accepted, rejected, and needs-evidence claims;
- implementation and verification tokens after worker review;
- defects or cleanup caused by worker output, including cleanup token cost;
- whether delegation changed the final implementation decision; and
- supervisor judgment of likely direct-work token/cash counterfactual.

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

## Workbench Direction

The longer-term opportunity is not a generic agent framework. Agent Workbench
should become a reproducible workbench for supervised AI-assisted scientific and
software development.

That means the durable product is not a chat transcript or model wrapper. The
durable product is an artifact trail:

- task bundle;
- role and capability requested;
- implementation used, such as local worker, paid supervisor, human, script, or
  external workflow tool;
- evidence produced;
- claims accepted and rejected;
- verification performed;
- token/cash economics; and
- supervisor promotion decision.

Keep P35/P36 focused on proving the token/cash economics loop. Treat broader
role/capability/workflow abstractions as the P37+ tranche once real pilot data
exists.
