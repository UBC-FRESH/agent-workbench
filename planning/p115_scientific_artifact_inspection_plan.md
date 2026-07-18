# P115 Scientific Artifact-Inspection Bridge Pilot

## Decision

P115 is the first forward-looking extension after P114. It is planned, not
active, and must not start until P114 has merged and closed and P107 has
finished, unless the maintainer explicitly authorizes a parallel phase.
Its purpose is to turn the proven minimal Worker data plane into a useful
scientific-workbench capability without attempting to build a generic agent
platform.

The initial capability is **grant-bound, read-only inspection of one frozen
public-safe FRESH model-instance artifact bundle**. The pilot must derive its
surface from a real task family, rather than from the historical Copilot SDK/UI
custom-tool catalog or a speculative catalog of MCP tools.

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
reviewable evidence artifact before P115 considers model execution, data
materialization, research browsing, notebooks, geospatial commands, or
platform-specific build tools.

## Scope

P115 will:

1. select one task family and a public-safe fixture bundle from a current FRESH
   project; the selection record must name the human task, source artifacts,
   expected evidence, verifier, and explicit exclusions;
2. derive the necessary Worker capability delta from the frozen task;
3. specify a package-level inspection grant with root containment, path allow
   lists, parser/type allow lists, output-size limits, content hashing,
   parser-version provenance, and stable denials;
4. implement only the required inspection handlers and deterministic fixtures;
   and
5. prove the frozen role-bound Ollama Worker can discover and use the tool in a
   fresh native session without shell or fallback-tool substitution.

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
stops with a documented negative selection decision rather than granting a
broader filesystem or shell capability.

## Tasks

### P115.1 — task-family selection and fixture freeze

- Record the candidate comparison, selected source project, public-safety
  decision, fixture hashes, expected output, validator, and non-go conditions.
- Define the exact human/model-worker question the inspection must answer.

### P115.2 — inspection grant and evidence contract

- Define the tool schema and grant record for declared artifacts only.
- Require path containment, type/parser allow lists, byte/row/page limits,
  hashes, parser identity, policy decision, and bounded result envelope.
- Add refusals for missing files, symlinks/outside-root paths, undeclared
  formats, oversized output, and unsupported parser failures.

### P115.3 — package implementation and deterministic tests

- Add the minimal package handler(s), policy checks, fixtures, and stable error
  behavior needed by the selected bundle.
- Keep compatibility translation in the P114 adapter and execution policy in
  package code; scripts only stage the run-scoped grant/configuration.

### P115.4 — fresh Worker inspection proof

- Use the accepted P114 fresh CLI-parent package route with exactly one
  `ollama_qwen_coder_worker`, `fork_context:false`, and a verbatim generated
  ticket.
- Require deferred discovery, one or more declared inspection calls, a
  provenance-bearing result, no fallback tool, and byte-for-byte restoration.

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
configuration changes, or a Copilot SDK/UI revival. Those are future,
task-derived tranches requiring their own grants and acceptance evidence.
