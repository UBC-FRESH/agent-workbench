# Phase 97 Activation: Reusable Workflow Graph Packaging

## Phase Overview

Parent issue: #592 (to be created on activation)
Branch: `feature/p97-reusable-workflow-graphs`
Status: **pending Advisor review** — planning and audit documented below; no implementation until after Advisor review.

Goal: package repeatable workflow graph templates for successful Agent Workbench
real-project workflows, establishing the reusable workflow graph catalog that every
future phase (P98+ real-project pilots, model comparisons, cross-project evaluations)
draws from. Starting with the P88-P94 document-indexing recipe and
the P92 whole-document delegated supervisor pattern.

## Pre-Implementation Graph Template Audit (2026-07-12)

Full inventory of existing templates in `templates/workbench_templates/`:

| File | Workflow ID | Status | Description |
| --- | --- | --- | --- |
| `agentic_graph_envelope.json` | `example-agentic-workbench-graph` | **Example/template only** | FreshForge-style graph envelope for supervised agent-assisted work. Generic but abstract — no real P90-P94 detail, meant as a structural reference for graph shape (nodes, needs, provider, artifacts). |
| `agentic_workflow_graph.json` | `example_agentic_workbench_graph` | **Example/template only** | FreshForge-compatible graph for supervised agent-assisted work. Very similar to `agentic_graph_envelope.json` — slightly more detailed with parameter-level metadata but still abstract with no real document-indexing content. Two example graphs exist; they overlap and serve as structural references rather than executable templates. |
| `managed_delegate_loop_graph.json` | `managed_delegate_loop_workflow` | **Working generic template** | Bounded local-worker extraction, self-audit, repair, convergence checking, and paid supervisor delta-review loop. Generic (uses `target_project` placeholders). Separates extractor, self-auditor, repairer, convergence-checker, and supervisor-auditor roles. README says this is "the generic loop shape behind that document workflow" — it's the reusable orchestration layer, not document-indexing-specific. |
| `document_library_index_graph.json` | `document_library_index_workflow` | **Working TSA23-derived template** | Generic FreshForge-shaped workflow for turning public technical-document corpora into source-anchored metadata indexes. Covers corpus registration, text chunking, P59 budget/stop-rule gate, structure/content extraction passes, local self-audit, delegated repair iteration, deterministic convergence checking, P60 split outcome fields, paid supervisor audit calibration, and promoted index assembly. Uses `target_project` placeholders — reusable for any public technical corpus beyond TSA23. This is the canonical P88-P94 indexing recipe captured as a graph. |
| `document_library_whole_document_supervisor_graph.json` | `document_library_whole_document_supervisor_pilot` | **Working P92-derived template** | Whole-document delegated supervisor pilot — select document, materialize whole-doc ticket, run delegated doc supervisor (custom-agent skin: `document-metadata-extraction-supervisor`), validate report, bounce once or audit seed, decide. Specific to the P92 graph-shaped delegation pattern where one supervisor handles an entire document instead of section-level tickets. |
| `document_artifact_audit_supervisor_graph.json` | (no workflow.id defined in source — inferred from name) | **Working generic template** | FreshForge-compatible graph for a local Copilot supervisor that materializes, audits, repairs, and reports document-indexing artifact gates under Agent Workbench authority boundaries. Abstracts the coordinator → supervisor ticket → materialize → audit → repair → report pattern. |
| `mp11_fixed_x8_reporting_graph.json` | `mp11_fixed_x8_reporting_delegation` | **Project-specific (keep as example)** | FreshForge-shaped non-executing graph for reducing paid supervisor reporting overhead in the MP11 fixed-x8 benchmark. Contains hard-coded path references to `benchmarks/mp11_document_metadata_index/x8_bundle_sequence_02/`. Not generic — ties to a specific MP11 benchmark run. Should be categorized as "keep-as-example" (project-specific artifact showing how this graph shape was applied). |
| `software_task_template.md` | N/A (Markdown envelope) | **Generic template** | Software task workbench envelope with placeholder fields for project, issue, risk, critical path, role, capability. Table-based graph envelope structure. Generic but not a workflow graph — it's a task-level planning/envelope format. Not directly relevant to P97's graph packaging goal. |
| `paper_task_template.md` | N/A (Markdown envelope) | **Generic template** | Paper/research task workbench envelope. Similar structure to `software_task_template.md`. Same assessment: not a workflow graph, just an envelope format. |
| `proposal_task_template.md` | N/A (Markdown envelope) | **Generic template** | Proposal task workbench envelope. Same as above. |
| `benchmark_task_template.md` | N/A (Markdown envelope) | **Generic template** | Benchmark task workbench envelope. Not a workflow graph. |

### Template Classification Decision Matrix

Based on the audit:

| Category | Count | Files |
| --- | --- | --- |
| **Promote** | 4 | `document_library_index_graph.json`, `managed_delegate_loop_graph.json`, `document_library_whole_document_supervisor_graph.json`, `document_artifact_audit_supervisor_graph.json` |
| **Retire** | 2 | `agentic_graph_envelope.json`, `agentic_workflow_graph.json` (overlapping examples, only value is structural reference in README) |
| **Keep-as-example** | 2 | `mp11_fixed_x8_reporting_graph.json`, `freshforge_proposal_assist_graph.json` (project-specific artifacts with hard-coded paths) |
| **Not-in-scope** | 4 | Markdown task-envelope templates (not workflow graphs) |

These four promoted templates represent the complete canonical graph family for Agent Workbench document-library and audit workflows — extraction loop, whole-document supervisor, artifact audit supervisor, and the full indexing pipeline.

## Scope Definition (Post-Audit)

P97 will NOT create new graph templates from scratch. Instead:

1. **Audit & classify** every existing template in `templates/workbench_templates/` — 13 files, classified as above (4 promote / 2 retire / 2 keep-as-example / 4 not-in-scope)
2. **Consolidate** the two example-only graphs (`agentic_graph_envelope.json`, `agentic_workflow_graph.json`) — merge useful metadata patterns into README, remove duplicate files
3. **Verify** that the four working templates are truly generic (no hard-coded paths like in `mp11_fixed_x8_reporting_graph.json` or `freshforge_proposal_assist_graph.json`) and pass public-safety scan
4. **Rename/verify** `document_library_index_graph.json` → `document_library_index_workflow.json` (the internal `workflow.id` is already `document_library_index_workflow`; the filename mismatch was a drafting artifact). No duplicate file creation — rename in-place and update README references.
5. **Update README.md** with:
   - Clear classification table (promote / retire / keep-as-example) — 4 promote, 2 retire, 2 keep-as-example
   - Description of each template's role in the graph family
   - Public-safety and validation requirements for using templates
   - Note about JSON Schema validation as a future requirement (P98+)
6. **Write minimal instantiation guide** in `playbooks/` connecting the canonical index workflow to the existing playbook

### Explicit Out-of-Scope for P97

- **JSON Schema validation for graph envelope format** — no existing schema to validate against; would require designing one first, writing validation tooling, and testing against all templates. This is a genuine future requirement but belongs in P98+ as its own task. Document the requirement in README under "future requirements" so it does not get forgotten.
- **Creating a second workflow graph family** (e.g., software-development graphs) — that is future work.
- **Refactoring Markdown task-envelope templates** — these are not workflow graphs.
- **Implementing a graph-runner or execution engine** — these templates remain non-executing metadata envelopes only, per AGENTS.md guidance and README documentation.

## P97 Tasks (Pending Advisor Approval)

### P97.1 Audit existing graph templates for reuse (#593 — child issue TBD)
- Read every file in `templates/workbench_templates/` (13 files total)
- Classify each as "promote", "retire", or "keep-as-example" based on: is it generic, does it capture a real P88-P94 workflow, does it contain project-specific contamination?
- Document classification in planning note and README
- **Deliverable**: `planning/phase97_graph_audit.md` (this document) + updated README

### P97.2 Rename/verify existing graph as `document_library_index_workflow.json` (#594 — child issue TBD)
- Under `templates/workbench_templates/`
- **Rename** `document_library_index_graph.json` → `document_library_index_workflow.json` (the internal `workflow.id` is already `document_library_index_workflow`; the filename mismatch was a drafting artifact, not a design decision)
- **Verify** all node-level metadata preserved: budget gates, extraction passes, audit, repair, convergence, supervisor calibration, promoted index assembly
- **Confirm** genericness — no hard-coded paths (unlike `mp11_fixed_x8_reporting_graph.json`), all `target_project` placeholders intact
- **Update** README references from old filename to new one
- **Public-safety scan**: no raw document references, no credentials, no project-specific contamination
- **Deliverable**: one canonical JSON file at `templates/workbench_templates/document_library_index_workflow.json` (renamed in-place, not a new creation)

### P97.3 Write minimal instantiation guide (#595 — child issue TBD)
- How to select a corpus, run extraction, audit, promote — referencing the graph template
- Cross-reference with the existing `playbooks/document_indexing_recipe.md` playbook
- Markdown guide under `templates/` or promoted into `playbooks/` depending on content scope
- **Deliverable**: one Markdown file in `playbooks/`

## Validation Gate Before Implementation

Before writing any code or templates:
1. This planning document must be reviewed by Advisor (this is that step)
2. After Advisor feedback, revise plan as needed
3. Only then create parent issue #592 and child issues on GitHub
4. Activate feature branch from main
5. Implement tasks P97.1 → P97.2 → P97.3 in order

## Open Questions for Advisor

1. The two example graphs (`agentic_graph_envelope.json`, `agentic_workflow_graph.json`) are structurally identical with minor differences in node-level metadata. Is retiring both and merging useful patterns into README the right call, or should one be kept as the "canonical example" of graph shape?
2. `document_library_index_graph.json` already exists and captures the full P88-P94 workflow. Do we need a separate canonical file (P97.2), or is that existing file sufficient if verified for genericness?
3. The MP11 reporting graph (`mp11_fixed_x8_reporting_graph.json`) has hard-coded benchmark run paths. Should we produce a sanitized, parameterized version of it as a second example template, or leave it strictly as-is in `examples/`?
4. Is there value in adding JSON Schema validation (`.jsonschema`) for the graph envelope format itself, so future templates can be validated automatically?

---

*This planning document is pending Advisor review before any implementation begins.*
