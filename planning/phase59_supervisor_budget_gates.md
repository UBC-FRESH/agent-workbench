# Phase 59 Supervisor Budget Gates

P59 turns the P57 cost-overrun lesson into a concrete budget declaration
surface. It does not launch live Copilot/Ollama jobs.

## Implemented Surface

Tracked template:

- `templates/supervisor_budget_declaration.json`

Validation module:

- `src/agent_workbench/budget.py`

CLI command:

```powershell
python -m agent_workbench.cli supervisor budget validate --input templates\supervisor_budget_declaration.json
```

The command validates:

- experiment question;
- maximum paid-supervisor cash budget;
- maximum paid-supervisor attempt count;
- required checkpoint spans;
- stop condition;
- maintainer checkpoint;
- summary status fields; and
- public-safety posture.

## Required Status Fields

Budget records must expose:

- `budget_declared`
- `budget_exceeded`
- `attempt_count`
- `stop_rule_triggered`
- `maintainer_checkpoint_required`

These fields are intentionally simple. P60 can split outcome semantics more
deeply, but P59 gives every future live benchmark a minimum budget gate and a
place to record when another paid attempt is forbidden.

## Enforcement Hook

The existing packaged document-audit graph live path now requires a valid
budget record unless it is run as a dry run:

```powershell
python -m agent_workbench.cli supervisor run-document-audit-graph --budget-record templates\supervisor_budget_declaration.json ...
```

The graph summary path also requires a budget record before rendering a summary
as economics evidence:

```powershell
python -m agent_workbench.cli supervisor summarize-document-audit-graph --budget-record templates\supervisor_budget_declaration.json ...
```

This is not a new live experiment. It is a fail-closed gate on existing
P57-era launcher surfaces.

## Boundary

P59 validates budget declarations and wires the existing graph audit launcher
and summarizer to require them for live/economics use. It does not run another
benchmark. Future live-run paths beyond this graph audit lane should call this
validator before claiming economics evidence.
