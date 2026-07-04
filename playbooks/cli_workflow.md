# CLI Workflow Playbook

The `agent-workbench` package is a local supervisor-side command surface for
bounded worker-agent experiments. It does not grant workers tracked-file,
GitHub, release, or closeout authority.

## Install From A Checkout

From the Agent Workbench repository root:

```powershell
python -m pip install -e .
agent-workbench --help
agent-workbench --version
```

Use the same virtual environment for local dogfood work where possible. If a
supervisor runs the command from another project checkout, pass the Agent
Workbench checkout explicitly:

```powershell
agent-workbench --repo-root <agent-workbench-checkout> smoke
```

## Smoke The Local Command Surface

```powershell
agent-workbench smoke
```

This runs the local command-surface smoke checker. It does not contact the model
provider.

## Plan A Same-Ticket Evaluation

Create an ignored runtime manifest that points to an ignored ticket and local
provider inputs. Then run:

```powershell
agent-workbench eval --manifest runtime/agent_jobs/example_manifest.json --dry-run
```

The dry run should show redacted provider values and should not contact the
model provider.

## Run A Same-Ticket Evaluation

When the configured provider inputs are present:

```powershell
agent-workbench eval --manifest runtime/agent_jobs/example_manifest.json
```

Raw model outputs and run summaries should stay under ignored runtime paths.

## Validate And Render Sanitized Evidence

Create a sanitized evidence summary JSON that references only repo-relative
runtime paths. Then run:

```powershell
agent-workbench evidence validate --input runtime/agent_jobs/example_evidence.json
agent-workbench evidence render --input runtime/agent_jobs/example_evidence.json --output runtime/agent_jobs/example_evidence.md
```

Promote only the sanitized findings into tracked planning notes.

## Current Boundary

The CLI currently supports supervisor-side smoke checks, SDK same-ticket
evaluation, evidence validation, and evidence rendering. It is ready for small
real-project trials where the supervisor prepares a bounded worker ticket and
keeps raw evidence ignored.

It is not a VS Code extension, MCP server, hosted agent, dashboard, benchmark
service, or autonomous closeout system.
