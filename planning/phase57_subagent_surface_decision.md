# Phase 57 Subagent Surface Decision

Phase 57 tested whether VS Code custom agents and subagents should become a
preferred implementation surface for the Agent Workbench hierarchy:

1. developer;
2. coordinator;
3. local supervisor;
4. worker or subagent.

The answer is split.

## Decision

Use VS Code custom-agent Copilot Chat as a preferred experimental surface for
local-supervisor orchestration.

Do not treat VS Code subagents as a trusted standalone worker surface yet.
Subagents may be used for bounded advisory nodes only when the workflow also
includes:

- deterministic source-fact and decision validators;
- explicit supervisor repair or replacement authority;
- structured subagent outcome reporting;
- one-shot command discipline;
- runtime mutation guardrails; and
- tracked sanitized coordinator evidence.

## Evidence

The strongest current evidence is the five-artifact P57 split 02 sequence.

Accepted economics datapoints:

| Run | Status | Paid coordinator cost | Per artifact | Key change |
| --- | --- | ---: | ---: | --- |
| v4 | accepted candidate | `$0.146603` | `$0.029321` | structured subagent outcome contract |
| v7 | accepted candidate | `$0.120379` | `$0.024076` | clean no-rerun token span |
| v8 | accepted candidate | `$0.092783` | `$0.018557` | score consistency gate |

The cost trend is encouraging, but it should be interpreted carefully. The
measured cost drop came from packaging and verifier hardening, not from better
subagent judgment.

## What Worked

The local Copilot supervisor repeatedly completed graph-shaped work:

- ran exact materializer commands;
- invoked a named auditor subagent;
- wrote runtime audit and graph reports;
- ran authority, document-audit, and graph-report validators;
- repaired bounded report defects;
- avoided delete commands after guardrail hardening;
- emitted final markers; and
- produced coordinator-facing evidence.

This supports the core Agent Workbench hierarchy idea: paid coordinator effort
can be reduced when recurring supervision rituals are packaged as reusable
workflow graphs plus deterministic validators.

## What Did Not Work Cleanly

The auditor subagent repeatedly made wrong gate decisions. In v8, it returned
`ready_to_scale` for four items where deterministic rules required
`needs_coordinator_review`.

That means the evidence does not support trusting this subagent role directly.
The useful system behavior came from:

- local supervisor containment;
- deterministic validators;
- repair loops; and
- compact coordinator review packets.

## Operating Rule

For near-term Agent Workbench phases, classify subagent outputs as advisory
unless a node-specific benchmark proves otherwise.

Default node policy:

- `script` nodes may be trusted when deterministic and tested.
- `worker_subagent` nodes are advisory.
- `supervisor` nodes may repair or replace worker output.
- `coordinator` nodes own benchmark conclusions and tracked summaries.
- `developer` authority remains outside model control.

## Next Phase Implication

The next useful tranche should move from P57 spike evidence to reusable
deployment surfaces:

- a supervisor job launcher that emits the correct graph ticket, bridge command,
  token span, validators, and sanitized summary path;
- deterministic scoring and acceptance functions owned by scripts, not models;
- a benchmark registry that records cost and quality tuples by graph node type;
  and
- a larger real-document workflow where the free local supervisor manages
  multiple advisory worker nodes under validator control.

The goal is not to make weak workers look good. The goal is to package work so
weak or uneven local workers can still contribute useful zero-cash labor inside
a workflow that keeps paid coordinator effort low and evidence quality high.
