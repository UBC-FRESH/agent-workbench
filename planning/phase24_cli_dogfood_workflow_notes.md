# Phase 24 CLI Dogfood Workflow Notes

Phase 24 dogfooded the package CLI on one no-tool worker evaluation workflow
from ticket through sanitized evidence rendering.

## Runtime Inputs

Ignored runtime files:

- `runtime/cli_dogfood/p24_ticket.md`
- `runtime/cli_dogfood/p24_manifest.json`
- `runtime/cli_dogfood/eval/summary.json`
- `runtime/cli_dogfood/eval/summary.md`
- `runtime/cli_dogfood/p24_evidence_summary.json`
- `runtime/cli_dogfood/p24_evidence_summary.md`

The tracked repository records only sanitized findings.

## Commands Verified

```text
python -m pip install -e .
agent-workbench smoke --report runtime/cli_dogfood/smoke_report.md
agent-workbench eval --manifest runtime/cli_dogfood/p24_manifest.json --dry-run
agent-workbench eval --manifest runtime/cli_dogfood/p24_manifest.json
agent-workbench evidence validate --input runtime/cli_dogfood/p24_evidence_summary.json
agent-workbench evidence render --input runtime/cli_dogfood/p24_evidence_summary.json --output runtime/cli_dogfood/p24_evidence_summary.md
```

## Sanitized Result

| Subject | Classification | Count | Notes |
| --- | --- | ---: | --- |
| `qwen3-coder:latest` | `exact-marker` | 1 | Provider-backed CLI run completed. |

The provider-backed CLI run returned the expected marker exactly once. The
evidence summary validated successfully and rendered to Markdown.

## Deployment-Readiness Decision

The package is now useful enough for small real-project trials:

- install the package from the Agent Workbench checkout;
- prepare a bounded no-tool or proposal-only ticket in ignored runtime space;
- run `agent-workbench smoke`;
- run `agent-workbench eval --dry-run`;
- run `agent-workbench eval` when provider inputs are present; and
- validate/render a sanitized evidence summary before promoting findings.

The package is not ready for autonomous tracked-file edits, GitHub closeout,
release actions, VS Code extension use, MCP tool serving, hosted-agent use, or
dashboard-style benchmarking.
