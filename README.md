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
model rankings. A rules-based `decide` command renders transparent delegation
recommendations from inspectable JSON inputs. A pilot `accounting` command
validates, renders, and synthesizes token/cash records from real-project
delegation experiments. A `policy tune` command turns those records into
transparent rules-based tuning guidance. A `workflow` command validates and
renders artifact-first workflow step records. A `roles` command validates and
renders role/capability/implementation records so model swaps do not rewrite
the workflow contract. An optional `graph` command validates FreshForge-compatible
agentic workflow graphs when Agent Workbench is installed with the graph extra.

Agent Workbench is not a workflow orchestration framework. Real project work
should continue to run through project-native tools such as FreshForge,
Snakemake, notebooks, GitHub Actions, or project CLIs. Agent Workbench records
delegation decisions, artifacts, claims, verification, and token/cash economics
around those tools.

Token/cost observability is optional. Sanitized usage records can be validated
and summarized, but raw prompts, traces, provider URLs, headers, and personal
paths stay out of tracked files.

## Local CLI

Install from a checkout:

```powershell
python -m pip install -e .
agent-workbench --help
```

Install graph validation support:

```powershell
python -m pip install -e ".[graph]"
```

Useful first commands:

```powershell
agent-workbench smoke
agent-workbench eval --manifest runtime/agent_jobs/example_manifest.json --dry-run
agent-workbench pilot pack-scaffold --project-root <target-project> --task evidence-intake="Summarize evidence"
agent-workbench evidence validate --input runtime/agent_jobs/example_evidence.json
agent-workbench evidence render --input runtime/agent_jobs/example_evidence.json --output runtime/agent_jobs/example_evidence.md
agent-workbench evidence synthesize --input-dir runtime/agent_jobs --output runtime/agent_jobs/decision_packet.md
agent-workbench decide task --input runtime/agent_jobs/example_decision.json --output runtime/agent_jobs/example_decision.md
agent-workbench accounting validate --input runtime/agent_jobs/example.accounting.json
agent-workbench accounting synthesize --input-dir runtime/agent_jobs --output runtime/agent_jobs/accounting_synthesis.md
agent-workbench policy tune --input-dir runtime/agent_jobs --output runtime/agent_jobs/policy_tuning.md
agent-workbench workflow validate --input templates/workflow_step_record.json
agent-workbench roles validate --input templates/role_capability_implementation.json
agent-workbench tokens validate --input templates/token_cost_record.json
agent-workbench graph validate --input templates/workbench_templates/agentic_workflow_graph.json --agent-metadata
agent-workbench graph render --input templates/workbench_templates/freshforge_proposal_assist_graph.json --output runtime/graph_render/freshforge_proposal_assist.md --agent-metadata
agent-workbench graph decide --input templates/workbench_templates/freshforge_proposal_assist_graph.json --output runtime/graph_decisions/freshforge_proposal_assist.md --agent-metadata
```

Raw tickets, manifests, model outputs, and provider inputs should stay in
ignored runtime paths. Promote only sanitized findings into tracked planning
notes.

Current boundary: the package is a local supervisor tool. It is not a VS Code
extension, MCP server, hosted agent, dashboard, autonomous closeout system, or
permission to delegate tracked-file or GitHub mutation to workers. It is also
not a replacement workflow engine for FreshForge or other project-native
execution systems.

See:

- `AGENTS.md` for the agent operating contract.
- `CONTRIBUTING.md` for contributor workflow rules.
- `ROADMAP.md` for the active phase/task plan.
- `CHANGE_LOG.md` for the append-only project narrative.
- `playbooks/cli_workflow.md` for the current CLI workflow.
- `playbooks/real_project_deployment.md` for real-project proposal-assist
  deployment.
- `model_profiles/` for evidence-scoped worker model capability notes.
- `templates/workbench_templates/` for FreshForge-style graph envelopes around
  agent-assisted project work.
