# Phase 26 Cross-Project Eval Notes

Phase 26 adds explicit cross-project evaluation support for the package CLI.
This is needed before using Agent Workbench against FreshForge or other adjacent
real development projects.

## Command Shape

```powershell
agent-workbench eval `
  --project-root <target-project> `
  --manifest tmp/agent_workbench/pilots/example.manifest.json `
  --dry-run
```

When `--project-root` is provided, manifest-relative ticket, output, provider,
and evidence paths resolve from the target project root. The Agent Workbench
evaluation script and probe script stay anchored to the Agent Workbench checkout.

## Implementation Note

The wrapper materializes a private manifest copy beside the target manifest:

```text
<manifest-directory>/materialized_manifests/
```

inside the target project. This keeps all generated eval artifacts inside the
same ignored project-local artifact tree chosen by the supervisor. The
materialized manifest rewrites the probe script path to the Agent Workbench
checkout and uses the active Python interpreter for the probe process. The
original target-project manifest remains unchanged.

Pilot scaffolds also place the provider scratch `base_directory` under the
chosen output directory, so a supervisor can keep tickets, outputs,
materialized manifests, and SDK scratch state in one ignored target-project
tree.

## Boundary

This change does not grant workers any new authority. It only makes
supervisor-owned no-tool and proposal-only evaluations usable across project
roots.
