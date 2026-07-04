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

Before choosing models for a real run, consult `model_profiles/` and verify the
active Ollama inventory. Use a profile only for the task families and authority
levels it actually covers. If a model has no profile, start with a marker or
proposal-only probe rather than assigning project work directly.

## Scaffold A Real-Project Pilot

For a real development project, generate a bounded ticket, manifest, and
evidence-summary stub under that project's ignored runtime directory:

Before scaffolding, classify the candidate task with
`planning/task_delegation_taxonomy.md`. Prefer high-suitability task or subtask
bundles such as evidence intake, compatibility review, test-design proposal, or
documentation proposal. Keep implementation, GitHub closeout, and release work
supervisor-owned.

Also check the selected worker model's capability profile under
`model_profiles/`. Match the ticket to the profile's observed strengths and
recommended authority ceiling. Treat planned or partial profiles as a reason to
run a small probe first.

For candidate tasks that are not obvious, render a delegation recommendation
before scaffolding:

```powershell
agent-workbench decide task `
  --input tmp/agent_workbench/<phase>/<task>.decision.json `
  --output tmp/agent_workbench/<phase>/<task>.decision.md
```

Use `templates/delegation_decision_input.json` as the starting point. Treat the
report as supervisor decision support, not as permission for autonomous worker
execution.

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

## Review Worker Claims

When worker output includes factual claims, add claim disposition fields to the
sanitized evidence summary before rendering or synthesizing:

```json
{
  "accepted_claims": [
    "The worker returned all required proposal sections."
  ],
  "rejected_claims": [
    "The worker claimed user reports existed, but no issue or source was supplied."
  ],
  "needs_evidence_claims": [
    "A proposed CLI improvement may be useful, but needs a downstream example."
  ]
}
```

Use `templates/claim_review_checklist.md` before promoting worker claims into
tracked planning notes, issue comments, or PR descriptions.

Promote only the sanitized findings into tracked planning notes.

## Compare Existing Eval Summaries

To compare repeat/model outcomes from existing same-ticket eval summaries:

```powershell
agent-workbench compare eval `
  --input runtime/agent_jobs/p8_sdk_no_tool_eval/summary.json `
  --input runtime/agent_jobs/p9_structured_doc_eval/summary.json `
  --output runtime/model_comparison/eval_comparison.md
```

The comparison report summarizes classification counts, per-model consistency,
and per-run outcomes. Treat the report as evidence about the supplied ticket
families only, not as a broad model ranking.

When a repeated comparison changes the supervisor's model-selection judgment,
update or add a capability profile from sanitized evidence rather than relying
on the raw comparison output alone.

## Current Boundary

The CLI currently supports supervisor-side smoke checks, SDK same-ticket
evaluation, pilot scaffolding, evidence validation/rendering, and supervisor
decision-packet synthesis, local comparison of existing eval summaries, and
transparent rules-based delegation recommendations. It is ready for small
real-project trials where the supervisor prepares bounded worker tickets and
keeps raw evidence ignored.

It is not a VS Code extension, MCP server, hosted agent, dashboard, benchmark
service, or autonomous closeout system.
