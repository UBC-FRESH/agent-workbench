# Agent Workbench

Agent Workbench is a public UBC-FRESH sandbox for developing supervised
multi-agent development workflows across lab software projects.

The repository focuses on reusable workflow contracts: supervisor/worker agent
roles, prompt handoffs, evidence-based verification, issue discipline, and
public-safe planning notes. It now also includes a small local Python package
and CLI for supervisor-side smoke checks, same-ticket evaluation, pilot
scaffolding, sanitized evidence summaries, and supervisor decision packets.
Worker model capability profiles live under `model_profiles/` so supervisors
can choose worker models from observed task-family evidence rather than broad
model rankings.

## Local CLI

Install from a checkout:

```powershell
python -m pip install -e .
agent-workbench --help
```

Useful first commands:

```powershell
agent-workbench smoke
agent-workbench eval --manifest runtime/agent_jobs/example_manifest.json --dry-run
agent-workbench pilot pack-scaffold --project-root <target-project> --task evidence-intake="Summarize evidence"
agent-workbench evidence validate --input runtime/agent_jobs/example_evidence.json
agent-workbench evidence render --input runtime/agent_jobs/example_evidence.json --output runtime/agent_jobs/example_evidence.md
agent-workbench evidence synthesize --input-dir runtime/agent_jobs --output runtime/agent_jobs/decision_packet.md
```

Raw tickets, manifests, model outputs, and provider inputs should stay in
ignored runtime paths. Promote only sanitized findings into tracked planning
notes.

Current boundary: the package is a local supervisor tool. It is not a VS Code
extension, MCP server, hosted agent, dashboard, autonomous closeout system, or
permission to delegate tracked-file or GitHub mutation to workers.

See:

- `AGENTS.md` for the agent operating contract.
- `CONTRIBUTING.md` for contributor workflow rules.
- `ROADMAP.md` for the active phase/task plan.
- `CHANGE_LOG.md` for the append-only project narrative.
- `playbooks/cli_workflow.md` for the current CLI workflow.
- `playbooks/real_project_deployment.md` for real-project proposal-assist
  deployment.
- `model_profiles/` for evidence-scoped worker model capability notes.
