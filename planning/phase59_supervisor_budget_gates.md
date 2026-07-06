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

## Boundary

P59 validates budget declarations. It does not run another benchmark and does
not retrofit every existing launcher in one pass. Future live-run paths should
call this validator before claiming economics evidence.
