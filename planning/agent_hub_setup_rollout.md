# Agent Hub Setup Rollout

Status: interim documentation rollout on `docs/agent-hub-setup`

## Goal

Provide a canonical, self-starting setup path for a clean GitHub Copilot
installation in Windows VS Code Desktop or Linux code-server. The path must
identify the supported capability boundary instead of implying that stock
Copilot can reach the private custom-provider lane.

## Scope

- Tier 0: stock Copilot, repository instructions, and `.github/agents` discovery.
- Tier 1: user-scoped GitHub MCP setup.
- Tier 2: custom local or remote provider setup through the documented extension
  configuration surface.
- Tier 3: optional bridge and operator playbooks.
- Front-door links from `README.md`, `AGENTS.md`, and
  `.github/copilot-instructions.md`.
- Referential-integrity, profile-resolution, credential-hygiene, and smoke
  checklist documentation.

## Advisor Review

The plan was reviewed by the read-only Advisor using the Claude Opus 5 model
before implementation. The review changed the rollout in three ways:

- Make the playbook explicitly tiered rather than promising one universal
  install path.
- Treat Linux code-server as the only measured environment and mark Windows
  Desktop and higher tiers as unverified until manually tested.
- Link existing MCP, provider, bridge, and operator documents instead of
  duplicating their procedures.

The branch implementation also corrected an initial branch-cut defect: the
reference documents are full playbooks, not placeholder stubs.

## Acceptance

- `playbooks/agent_hub_setup.md` exists and documents all four tiers.
- All setup references resolve on disk and referenced agent profiles exist.
- Front-door documents point to the canonical setup playbook.
- Tracked rollout content contains no private hostnames, absolute user paths,
  endpoint credentials, or token values.
- Focused setup tests pass.
- Profile compatibility checks pass, excluding only the two known environment-
  coupled catalog checks whose tool inventory is unavailable in this runtime.
- A clean-environment manual smoke test remains explicitly pending for the PR
  consumer.

## Deferred

This interim PR does not claim successful Windows installation, Tier 1-3
runtime operation on a clean host, or custom-provider model availability. Nibi
vLLM deployment remains a separate operational lane.
