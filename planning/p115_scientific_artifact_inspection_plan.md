# P115 Scientific Artifact-Inspection Bridge Pilot

## Decision

P115 is an active capability pilot after P118 completion. It is _not_ the
Codex SDK / CLI-parent / adapter route — those lanes are parked. P115 uses the
P118 **native Copilot Chat Agent Hub** with a single vLLM remote provider
(Qwen 3.6 27B) and custom agent profiles. Delegation is via `runSubagent` with
bounded profile instructions.

Its purpose is to answer a transport-independent question: *can a bounded
Qwen agent profile successfully inspect a frozen public-safe FRESH artifact
bundle and produce a provenance-bearing evidence report?* The pilot must derive
its surface from a real task family, not from a speculative catalog of tools.

## Why artifact inspection first

The current FRESH portfolio requires agents to understand and verify inputs
before they can safely propose code or run models:

- FEMIC and its instances use rebuild configurations, evidence reports,
  external-data declarations, geospatial preflight, and FreshForge workflows.
- BC-NPPD needs workbook, schema, source-policy, and evidence-confidence
  review.
- FABLE/Modelwright work uses workbooks, generated Python models, notebooks,
  scenario definitions, and validation outputs.
- FieldAtlas requires reproducible map-package manifests and later geospatial
  metadata.

Read-only inspection is common to those workflows and can produce a durable,
reviewable evidence artifact before considering model execution, data
materialization, research browsing, notebooks, geospatial commands, or
platform-specific build tools.

## Scope

P115 will:

1. Select one task family and a public-safe fixture bundle from a current FRESH
   project; the selection record must name the human task, source artifacts,
   expected evidence, verifier, and explicit exclusions.
2. Derive the necessary agent-profile instruction boundary from the frozen task.
3. Create a bounded inspection agent profile with explicit instructions on what
   to read, what to report (provenance, structural invariants, anomalies), and
   what to refuse (speculation, mutation).
4. Create deterministic validation fixtures (clean bundle, bundle with
   structural anomaly, bundle with provenance gap) so the pilot is observable.
5. Prove a delegated Qwen3-coder inspection agent (via `runSubagent`) can
   successfully inspect the fixture bundle and produce a provenance-bearing
   evidence artifact.

## Candidate task families

The phase selection task must compare these candidates before choosing one:

| Candidate | Likely artifact types | Deferred capability pressure |
| --- | --- | --- |
| FEMIC instance rebuild review | YAML, CSV, runbook/evidence text | later declared model-run and geospatial preflight |
| BC-NPPD evidence/workbook review | CSV, schema, XLSX, source notes | later source research and workbook normalization |
| FABLE scenario review | XLSX, generated Python, notebook outputs | later notebook execution and model validation |
| FieldAtlas map-package review | JSON/manifest, geospatial metadata | later geospatial parsing, rendering, location/device work |

The selected pilot must be reproducible from public-safe inputs and have a
small deterministic oracle. If no candidate satisfies those conditions, P115
stops with a documented negative selection decision.

## Tasks

### P115.1 — task-family selection and fixture freeze

- Record the candidate comparison, selected source project, public-safety
  decision, fixture hashes, expected output, validator, and non-go conditions.
- Define the exact human/model-worker question the inspection must answer.

### P115.2 — inspection agent profile

- Create a bounded agent profile (`.agent.md`) that declares:
  - What artifact types it can inspect (scoped to the P115.1 fixture family)
  - What it must report (provenance fields, structural invariants, anomalies)
  - What it must refuse (speculation beyond the artifact, modifying the artifact)
  - A canonical output format (structured markdown with provenance)
- The profile uses native Copilot Chat tools only (read_file, grep_search,
  file_search). No custom SDK tools, no MCP, no adapter.

### P115.3 — deterministic validation fixtures

- Create 2-3 validation fixtures with known properties:
  - A "clean" bundle (should pass all checks)
  - A bundle with a deliberate structural anomaly (should be detected)
  - A bundle with a subtle provenance gap (should be flagged)
- Add deterministic validation checks that can compare agent output against
  expected findings for each fixture.

### P115.4 — delegated inspection proof

- Use the P118 native Agent Hub route: `runSubagent` with the P115.2 inspection
  agent profile.
- Delegate the inspection ticket to the Qwen3-coder agent.
- Require: deferred discovery, one or more declared inspection calls, a
  provenance-bearing result, no shell or fallback-tool substitution.
- Compare agent output against the P115.3 fixtures and record where the agent
  succeeds, over-reports, or misses.

### P115.5 — decision and next capability gate

- Record quality, protocol, and economics separately.
- Promote exactly one next capability only when the pilot identifies a
  concrete unmet need: declared scientific run, report rendering/plotting,
  workbook transformation, document/PDF extraction, geospatial preflight,
  external-source research, or platform-specific build/test.

## Explicit exclusions

P115 does not authorize unrestricted shell, arbitrary recursive reads, source
materialization through DataLad/git-annex, model execution, network/browser
access, notebook kernels, geospatial mutation, GitHub mutation, provider or
configuration changes, Copilot SDK, CLI-parent routes, adapter scaffolding, or
custom MCP tools. Those are future, task-derived tranches requiring their own
grants and acceptance evidence.
