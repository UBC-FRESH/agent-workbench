# Phase 72: Copilot SDK Custom Agent Profiles

Phase 72 upgrades the SDK-owned Copilot bridge so Agent Workbench can launch and resume sessions with explicit custom agent profiles, selected agent names, SDK default-agent controls, subagent streaming, and conservative Agent Workbench custom tools.

## Governing Issues

- Parent phase issue: #473
- P72.1 Profile planning and manifest contract: #475
- P72.2 Profile parser and resolver: #474
- P72.3 SDK bridge launch integration: #476
- P72.4 Profile CLI and transcript evidence: #478
- P72.5 Custom tool registry and verification: #477

## Scope

- Extend `sdk.agent_profiles` in SDK session manifests.
- Parse `.agent.md` frontmatter and Markdown body into SDK custom-agent config dictionaries.
- Preserve VS Code-only profile fields in validation output while passing only SDK-supported fields to session creation and resume calls.
- Add profile validation and rendering commands.
- Register a small read-only/validation Agent Workbench tool set for workflow-aware sessions.
- Count custom-agent and subagent events in monitor and transcript evidence.

## Manifest Contract

The bridge reads `sdk.agent_profiles` from each SDK session manifest:

- `source_paths`: `.agent.md` profile files to load.
- `selected`: optional SDK `agent` name.
- `default_agent`: optional SDK default-agent config; v1 passes only `excluded_tools`.
- `custom_agents_local_only`: defaults to `true`.
- `include_sub_agent_streaming_events`: defaults to `true`.
- `custom_tools`: Agent Workbench custom SDK tools to register for the session.
- `task_overlay`: optional text or path appended to the selected profile prompt at runtime.

The bridge resolves profile source paths from the manifest directory, repo root, or current working directory. The source profile files remain unchanged; task overlays are applied only to the resolved SDK config.

## Custom Tool Policy

The v1 Agent Workbench custom tool registry is intentionally conservative:

- `agent_workbench_run_context`: returns public-safe run objective, issue IDs, stop rule, workspace root, and allowed artifact paths.
- `agent_workbench_result_contract`: returns required result/blocker paths and section/status expectations.
- `agent_workbench_validate_result`: validates that a result or blocker file uses the manifest contract.

Broad mutating Agent Workbench-specific tools stay out of P72. Mutating behavior should come from built-in SDK/editor/shell tools only when the profile and ticket explicitly allow them.

## Verification Plan

- Unit-test `.agent.md` parsing, selected-agent validation, unsupported field reporting, task overlays, profile tool coverage, and custom tool payloads.
- Unit-test SDK kwargs pass-through for create/resume configuration.
- Unit-test transcript accounting for `session.custom_agents_updated`, `subagent.*`, and assistant messages carrying agent metadata.
- Smoke-test `profile-validate` and `profile-render` against an ignored runtime manifest using the standard local supervisor profile.
- Keep live FEMIC dogfood as P70 evidence rather than claiming P72 alone proves downstream task quality.

## P72.5 Dogfood Evidence

P70 Ticket C ran through SDK session `6ebd387b-b23a-4ff1-8e22-5abc46a2cba0` with `agent-workbench-local-supervisor` selected. The run repaired the ignored FEMIC P108 supervisor result report by replacing the stale PR placeholder with PR #303, preserving the open parent issue #302 state, and recording the closed child issue set #297-#301.

Compared with P70 Ticket B, Ticket C produced visible subagent events, invoked the custom `agent_workbench_validate_result` tool, and after a bridge patch recorded a manifest-derived `session.custom_agents_updated` event so compact transcripts expose the selected profile. The comparison artifact remains ignored under `runtime/p70_ticket_c_p108_result_report/comparison.md`.
