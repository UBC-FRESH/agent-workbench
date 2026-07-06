# Phase 64 Deployment Environment And Operator Playbook

## Purpose

P64 turns the P55-P63 local-supervisor lessons into a public-safe operator
playbook for running Agent Workbench in VS Code or code-server with a configured
local Ollama worker host.

This phase is deliberately non-live. It does not run Copilot Chat, call local
models, benchmark workers, or change provider configuration. Its job is to make
future local-supervisor runs less dependent on chat memory and less likely to
burn paid supervisor tokens rediscovering setup and failure boundaries.

## Evidence Carried Forward

- P55 showed that document-indexing workflows are sensitive to ticket shape,
  model role, output contract, and repair/verification stages.
- P57 showed that a local Copilot/Ollama supervisor can perform useful bounded
  work when the ticket is pre-materialized and the allowed action surface is
  narrow.
- P59 made budget records and stop rules mandatory when economics claims are
  involved.
- P60 separated quality, protocol, and economics outcomes so noisy runs are not
  overpromoted.
- P61 packaged the local-supervisor workflow boundary.
- P63 confirmed that document-indexing pilots need explicit do-not-run gates
  when provider failures, malformed output, or invalid source identifiers appear.

## Supported Deployment Posture

The supported posture is a local-supervisor workflow:

- the coordinator/supervisor prepares deterministic inputs, budgets, and
  run IDs;
- VS Code or code-server hosts the visible local-supervisor interaction;
- Copilot Chat uses a configured Ollama-backed model provider;
- raw tickets, transcripts, provider details, and model outputs stay under
  ignored runtime paths;
- deterministic validators inspect artifacts before any acceptance claim; and
- paid Codex supervision is reserved for planning, audit, escalation, and
  closeout decisions.

P64 does not document private endpoints, hostnames, access headers, credentials,
personal paths, or workstation-specific setup details. Operators should keep
those details in local configuration, secret stores, or ignored notes.

## Playbook Artifact

The durable playbook is `playbooks/deployment_environment_operator.md`.

That playbook should be read with:

- `playbooks/vscode_chat_bridge.md` for bridge command details;
- `playbooks/real_project_deployment.md` for proposal-assist deployment on
  target projects; and
- `playbooks/document_indexing_recipe.md` for the document-indexing workflow
  recipe.

## Closeout Boundary

P64 is complete when:

- the operator playbook documents the environment shape;
- pre-run, launch, evidence, post-run, and do-not-run checklists are present;
- troubleshooting guidance covers stale sessions, wrong roots, wrong models,
  loop cancellation, provider/model failures, and restart decisions;
- the tracked docs avoid private deployment details; and
- roadmap, changelog, issues, and PR body agree.
