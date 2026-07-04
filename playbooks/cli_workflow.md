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

## Scaffold A Real-Project Pilot

For a real development project, generate a bounded ticket, manifest, and
evidence-summary stub under that project's ignored runtime directory:

```powershell
agent-workbench pilot scaffold `
  --project-root <target-project> `
  --task-id example-proposal `
  --title "Draft a bounded proposal for supervisor review" `
  --mode proposal `
  --output-dir tmp/agent_workbench/pilots
```

Then dry-run the generated manifest:

```powershell
agent-workbench eval `
  --project-root <target-project> `
  --manifest tmp/agent_workbench/pilots/example-proposal.manifest.json `
  --dry-run
```

Use `--mode marker` for a stop-behavior check and `--mode proposal` for a
bounded planning/proposal worker task.

When `--project-root` is supplied, manifest-relative ticket, output, provider,
and evidence paths resolve from the target project root. Agent Workbench still
uses its own checkout for the evaluation harness scripts.

## Scaffold A Real-Project Proposal Pack

For several proposal-only worker tickets, scaffold the pack in one command:

```powershell
agent-workbench pilot pack-scaffold `
  --project-root <target-project> `
  --output-dir tmp/agent_workbench/pilots `
  --mode proposal `
  --task evidence-intake="Summarize evidence for supervisor review" `
  --task cli-proposal="Propose a bounded CLI improvement" `
  --task docs-proposal="Propose docs and acceptance checks"
```

Each task gets its own eval output directory and Copilot SDK scratch directory,
so repeated worker runs do not overwrite each other's raw outputs.

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

To synthesize several reviewed evidence summaries into one supervisor decision
packet:

```powershell
agent-workbench evidence synthesize `
  --input-dir tmp/agent_workbench/pilots `
  --output tmp/agent_workbench/pilots/supervisor_decision_packet.md
```

Synthesis validates every input summary first. Invalid or private-looking
evidence stops the packet rather than being silently promoted.

Promote only the sanitized findings into tracked planning notes.

## Current Boundary

The CLI currently supports supervisor-side smoke checks, SDK same-ticket
evaluation, pilot scaffolding, evidence validation/rendering, and supervisor
decision-packet synthesis. It is ready for small real-project trials where the
supervisor prepares bounded worker tickets and keeps raw evidence ignored.

It is not a VS Code extension, MCP server, hosted agent, dashboard, benchmark
service, or autonomous closeout system.
