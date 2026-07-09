# Phase 73: Standard Agent Workbench Profile Catalog

Phase 73 will turn the first custom-agent bridge into a reusable catalog of standard Agent Workbench profiles and task overlays. The catalog remains `.github/agents/*.agent.md` first so VS Code custom-agent experiments and Copilot SDK sessions can share the same human-editable source files.

## Planned Standard Profiles

- `agent-workbench-local-supervisor`: qwen3.6 supervisor/orchestrator profile for bounded workflow graph and SDK delegation runs.
- `agent-workbench-result-auditor`: read-only auditor profile for checking worker outputs against contracts.
- `qwen3-coder-strict-worker`: bounded implementation worker.
- `qwen3-coder-next-strict-worker`: bounded implementation worker variant for model comparison.

## Planned Task Overlays

- repair-list execution;
- new Python module implementation;
- existing-code debugging;
- systematic refactor or sweep;
- documentation expansion;
- notebook or example authoring;
- release-readiness review.

## Tool Dimension

Phase 73 should treat profile tools as a first-class design surface:

- every standard profile declares the tools it expects;
- profile validation reports unknown, unsupported, or unregistered custom tools;
- custom tools are added only when the workflow contract needs them;
- broad mutating Agent Workbench-specific tools require a later explicit safety phase.

## Evidence Needed

Phase 73 should use compact transcripts, result quality, supervisor repair burden, and drift/stall metrics from P70 and P72 dogfood runs before standardizing model-role combinations.
