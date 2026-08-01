# P126: Agent Hub Core Roles and Overlays

Date: 2026-08-01

Parent issue: [#773](https://github.com/UBC-FRESH/agent-workbench/issues/773)

Branch: `feature/p126-agent-hub-core-roles`

Status: active

## Decision

Agent Hub has four core role definitions: Coordinator, Supervisor, Worker, and
Advisor. These are the portable operating roles and are the only default role
profiles the Hub needs to explain or install.

Specialized behavior is expressed as overlays applied to one of the four core
roles. A document-extraction supervisor, repair worker, or provider probe is a
specialized behavior package, not a new model-named core role. Overlays may add
instructions, tools, constraints, or acceptance criteria without duplicating
the authority definition of the underlying role.

Model/provider selection remains a deployment concern. Core role names and
overlay names must not encode a model family or provider. Detailed operator
model configuration is deliberately deferred until the four-role catalog and
overlay mechanism are stable.

## Goal

Restore a small, comprehensible Agent Hub surface in which role authority is
defined once and specialization composes through overlays. Keep model/provider
choices explicit enough for an operator to control, without turning every
model experiment into a new profile family or introducing a configuration
framework before it is needed.

## Scope

- Define exactly four default core profiles: Coordinator, Supervisor, Worker,
  and Advisor.
- Rename or remove model-family profile names and references.
- Recast document extraction, repair, auditing, and provider probes as opt-in
  overlays or separate experiments rather than default core roles.
- Make the existing overlay catalog discoverable and composable with a core
  role.
- Keep model/provider bindings out of profile names and document them as
  deployment-specific choices.
- Add focused tests for the four-role catalog, overlay discovery, and the
  absence of model-family names in core profile names.
- Update setup documentation, clean-session smoke guidance, changelog, and
  roadmap synchronization.

## Out of scope

- Selecting a universal model or provider for all operators.
- Changing the Keklick extension or implementing a provider.
- Publishing endpoint details, credentials, headers, or lab paths.
- Reworking unrelated historical experiment scripts that intentionally record
  the model used in that experiment.
- Deploying or validating Nibi, Sockeye, or another cluster service.

## Work breakdown

### Core roles

- Use one Coordinator, Supervisor, Worker, and Advisor definition.
- Remove model-family words from core profile filenames, `name` fields, and
  authority prose.
- Keep role-specific model defaults as deployment documentation, not as role
  identity.

### Overlays

- Treat extraction, repair, audit, notebook, documentation, and release
  behaviors as overlays.
- Define how an overlay names its target core role and what it adds.
- Keep provider probes outside the default core-role install.

### Documentation and verification

- Document the four-role model and overlay composition in the setup guide.
- Add tests that fail when core profile names encode a model family/provider.
- Verify that the default installer exposes the four core roles and does not
  silently install experimental provider probes.

## Acceptance criteria

- Default Agent Hub role profile filenames and `name` fields are model-neutral.
- Canonical generic profiles do not hard-code a model/provider alias.
- The default Agent Hub catalog exposes only Coordinator, Supervisor, Worker,
  and Advisor as core roles.
- Specialized behavior is represented by overlays with an explicit target core
  role.
- Core role filenames and `name` fields contain no model family or provider.
- Provider-specific probes are excluded from the default core-role install.
- Existing installer conflict protection and idempotency remain intact.
- Focused tests, `git diff --check`, and an installed-profile audit pass.
- No private endpoint, credential, header, or absolute operator path enters
  tracked content.

## Verification commands

```bash
python -m pytest tests/test_agent_hub_profile_installer.py tests/test_copilot_agent_profiles.py tests/test_agent_hub_setup_playbook.py -q
git diff --check
python scripts/install_agent_hub_profiles.py --check
```

## Closeout

Synchronize `ROADMAP.md`, `CHANGE_LOG.md`, the parent issue checklist, and this
planning note. Attach the focused test output and core/overlay catalog audit
before requesting phase closeout. Do not close the parent issue until the phase
branch has merged into `main`.
