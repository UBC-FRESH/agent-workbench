# Workbench Template Envelopes

These templates are public-safe starter envelopes for reproducible
AI-assisted work. They are not workflow runners.

The envelope shape intentionally borrows FreshForge's graph vocabulary:

- `workflow`: named work bundle;
- `nodes`: bounded role/capability steps;
- `needs`: explicit dependencies between steps;
- `provider`: implementation namespace such as supervisor, local worker,
  FreshForge, project CLI, notebook, CI, or script;
- `inputs` and `outputs`: declared information flow;
- `artifacts`: source, generated, promoted, or rejected evidence; and
- `diagnostics`: validation, claim-review, or policy warnings.

Use them to organize:

- supervisor intent;
- source artifacts;
- worker tickets;
- generated artifacts;
- project-native commands;
- evidence summaries;
- claim review;
- token/cash accounting; and
- promoted outputs.

Execution stays with the target project's existing tools: FreshForge, project
CLIs, notebooks, Snakemake, GitHub Actions, Quarto, CI, release scripts, or
human review.

Template families:

**Graph templates (Promote):** `managed_delegate_loop_graph.json`, `document_library_index_workflow.json`, `document_library_whole_document_supervisor_graph.json`, `document_artifact_audit_supervisor_graph.json`
**Project-specific examples:** `mp11_fixed_x8_reporting_graph.json`, `freshforge_proposal_assist_graph.json`
**Task-envelope formats:** `software_task_template.md`, `paper_task_template.md`, `proposal_task_template.md`, `benchmark_task_template.md`
**Structural references (Retire):** `agentic_graph_envelope.json`, `agentic_workflow_graph.json`

See [Template Classification](#template-classification-p97) below for full details.

Copy the relevant template into an ignored target-project runtime path first.
Promote only sanitized findings into tracked project files.

## Template Classification (P97)

All 13 templates in this directory have been audited and classified:

| Category | Count | Files |
| --- | --- | --- |
| **Promote** | 4 | `document_library_index_workflow.json`, `managed_delegate_loop_graph.json`, `document_library_whole_document_supervisor_graph.json`, `document_artifact_audit_supervisor_graph.json` |
| **Retire** | 2 | `agentic_graph_envelope.json`, `agentic_workflow_graph.json` (overlapping examples, only value is structural reference) |
| **Keep-as-example** | 2 | `mp11_fixed_x8_reporting_graph.json`, `freshforge_proposal_assist_graph.json` (project-specific artifacts with hard-coded paths) |
| **Not-in-scope** | 4 | Markdown task-envelope templates (`software_task_template.md`, `paper_task_template.md`, `proposal_task_template.md`, `benchmark_task_template.md`) |

### Promote — Ready for Use

These four working templates capture real P88–P94 or P92 workflows. All use `target_project` placeholders and are generic enough for any public technical corpus.

**`document_library_index_workflow.json`** — Generic FreshForge-shaped workflow for turning public technical-document corpora into source-anchored metadata indexes. Covers corpus registration, text chunking, P59 budget/stop-rule gate, structure/content extraction passes, local self-audit, delegated repair iteration, deterministic convergence checking, P60 split outcome fields, paid supervisor audit calibration, and promoted index assembly. This is the canonical P88–P94 indexing recipe captured as a graph.

**`managed_delegate_loop_graph.json`** — Bounded local-worker extraction, self-audit, repair, convergence checking, and paid supervisor delta-review loop. Generic (uses `target_project` placeholders). Separates extractor, self-auditor, repairer, convergence-checker, and supervisor-auditor roles. This is the reusable orchestration layer — not document-indexing-specific.

**`document_library_whole_document_supervisor_graph.json`** — Whole-document delegated supervisor pilot: select document, materialize whole-doc ticket, run delegated doc supervisor, validate report, bounce once or audit seed, decide. Based on P92 whole-document review pattern where one supervisor handles an entire document instead of section-level tickets.

**`document_artifact_audit_supervisor_graph.json`** — FreshForge-compatible graph for a local Copilot supervisor that materializes, audits, repairs, and reports document-indexing artifact gates under Agent Workbench authority boundaries. Uses `runtime/agent_jobs/<job_id>_ticket.md` paths (generic). Captures the coordinator → supervisor ticket → materialize → audit → repair → report pattern distinct from the index graph.

### Retire — Structurally Useful Only

These two overlapping example graphs have no real workflow content beyond structural placeholders. Their only value is as examples of the JSON envelope format, which the README already documents. They are retained temporarily for backward compatibility and will be removed once all references are updated.

### Keep-as-Example — Project-Specific Artifacts

**`mp11_fixed_x8_reporting_graph.json`** — FreshForge-shaped non-executing graph for reducing paid supervisor reporting overhead in the MP11 fixed-x8 benchmark. Contains hard-coded path references to `benchmarks/mp11_document_metadata_index/x8_bundle_sequence_02/`. Not generic — ties to a specific MP11 benchmark run. Useful for demonstrating how graph templates are instantiated from generic to specific.

**`freshforge_proposal_assist_graph.json`** — FreshForge proposal-assist pilot graph with hard-coded FreshForge roadmap references (e.g., `#1`, `ROADMAP.md`, task IDs like `P1.1`). Not generic — project-specific. Useful as an example of a real-world instantiation.

### Task-Envelope Templates — Not Workflow Graphs

`software_task_template.md`, `paper_task_template.md`, `proposal_task_template.md`, and `benchmark_task_template.md` are planning/envelope formats, not workflow graphs. They use table-based structures with placeholder fields for project, issue, risk, critical path, role, and capability. Documented here for completeness but out of scope for P97 refactoring.

## Future Requirements

**JSON Schema validation for graph envelope format.** No existing schema to validate against; would require designing one first, writing validation tooling, and testing against all templates. This is a genuine future requirement (P98+) but should be tracked so it does not get forgotten.
