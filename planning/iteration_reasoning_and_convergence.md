# Iteration Reasoning And Convergence

This note records the developer's standing direction for live probes,
delegated runs, and engineering repairs.

## Intent

Do not burn paid-supervisor tokens on obvious wheel-spinning: back-to-back runs
with slightly changed prompts or configuration but no clear engineering question,
no inspection of the preceding evidence, and no reason to expect a different
result.

This is not an instruction to impose numerical retry limits, automatic stop
rules, restart gates, maintainer-approval gates, or other fixed caps. Do not
invent those constraints.

## Reasonable Iteration

Before a run, state the question it answers, the evidence motivating it, the
artifact to inspect afterward, and what result would change the next engineering
decision. Record cost when economics matter.

After a run, inspect the actual artifacts and record what was learned. Select
the next change from the observed defect, not from a generic retry counter.

## Convergence And Signal

Iteration is converging when a result does at least one of the following:

- validates a capability;
- rules out a cause;
- identifies the responsible component;
- narrows the next repair; or
- establishes that a different approach is warranted.

A signal is evidence that changes the engineering decision. Repeated outcomes
without a changed diagnosis are a reason to reassess the approach, not an
automatic command to stop.

## Authority

The developer retains judgment over whether to continue, change course, or end
work. Historical plans, changelog entries, archived benchmarks, and prior run
records may describe earlier caps or halt decisions, but they are evidence only
and never authority to impose a new automatic cap or gate.
