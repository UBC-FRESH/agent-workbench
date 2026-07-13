# Phase 102: Native Codex + Remote Ollama Orchestration

## Objective

P102 makes native Codex the preferred orchestration host for a thin paid
Coordinator and a configured OpenAI-compatible Ollama provider for the default
Supervisor and Worker roles. It validates the delegation mechanism first; it
does not yet authorize a substantive document-extraction run.

## Configuration Boundary

The tracked project layer contains only generic role semantics:

- `.codex/config.toml` enables two spawned levels: Coordinator -> Supervisor
  -> Worker.
- `.codex/agents/ollama_supervisor.toml` and
  `.codex/agents/ollama_worker.toml` declare the role identity, expected model
  tag, provider identifier, sandbox policy, and authority boundary.
- The identifier `agent_workbench_ollama` is deliberately not a provider
  definition. A provider definition, endpoint, and Cloudflare Access headers
  belong in the operator's user-level Codex home and process environment.

This split follows Codex configuration behavior: project-scoped configuration
cannot define machine-local provider or authentication settings. A tracked
project must therefore never contain the endpoint, header values, or a copied
user-level provider configuration.

## Vertical-Slice Contract

The first live proof asks only whether the hierarchy works:

```text
paid Coordinator
  -> ollama_supervisor
       -> ollama_worker
```

The Worker returns a unique marker. The Supervisor independently verifies that
marker and returns a second marker. The Coordinator then inspects the persisted
evidence and records separate `quality_validated_candidate`,
`protocol_accepted_candidate`, and `economics_usable` verdicts.

The proof is allowed one Coordinator session, one Supervisor session, one
Worker session, and at most one repair after a concrete first failure. It must
not mutate tracked files, Git or GitHub state, provider configuration, or model
inventory. Runtime tickets, results, session archives, and token records remain
ignored local artifacts.

## Task Sequence

1. P102.1 (#606): validate the role profiles and document the local bootstrap
   boundary.
2. P102.2 (#607): add fail-closed validation for the role configuration and
   sanitized proof manifest.
3. P102.3 (#608): execute one bounded two-edge proof only after validation.
4. P102.4 (#609): inspect evidence and decide whether a separate substantive
   TSA23 native-hierarchy phase should be activated.

## Non-claims

The already accepted low-level endpoint and tool-loop probes do not prove
nested delegation. Neither the tracked profiles nor this planning note claim
that the Supervisor can yet spawn the Worker; that claim requires P102.3
evidence.

## R2 and R4 Proof Evidence

The ignored R2 and R4 marker runs established that native Codex can produce the
required two-edge thread shape, including a Supervisor that spawns a Worker and
independently reports the Worker's marker. R4 used distinct user-level role
names to avoid project/global agent-name ambiguity.

This is accepted only as a **nesting and role-selection** result. The persisted
session metadata for the spawned roles still reported the default `openai`
provider, so the evidence does not yet prove that the configured Ollama model
was selected. The next P102.3 step must add model/provider observability at the
spawned-session boundary before any free-worker economics or substantive TSA23
claim is made.
