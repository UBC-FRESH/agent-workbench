# Phase 25 Real-Project Pilot Scaffold Notes

Phase 25 adds the first deployment-oriented Agent Workbench command:

```text
agent-workbench pilot scaffold
```

The command creates a bounded worker ticket, SDK evaluation manifest, and
evidence-summary stub under an ignored runtime directory for a target project
root. This reduces setup friction when a supervisor wants to try self-hosted
Ollama worker assist on a real development task.

## Supported Modes

- `marker`: no-tool worker should return one exact marker line.
- `proposal`: no-tool worker should return a bounded proposal with
  `## Rationale`, `## Proposal`, and `## Verification` sections.

Both modes forbid tools, commands, file edits, GitHub mutation, and tracked-file
mutation.

## Usage Shape

```powershell
agent-workbench pilot scaffold `
  --project-root <target-project> `
  --task-id p25-example `
  --title "Draft bounded worker proposal" `
  --mode proposal
```

Then run:

```powershell
agent-workbench eval --manifest <generated-manifest> --dry-run
agent-workbench evidence validate --input <generated-evidence-json>
```

If provider inputs are configured in the target project, the supervisor can run
the generated manifest without `--dry-run`.

## Boundary

The scaffold does not run the worker. It creates supervisor-reviewed inputs for
a later run. Raw outputs stay under ignored runtime paths, and tracked findings
must still be promoted manually after supervisor review.
