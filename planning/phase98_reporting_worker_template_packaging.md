# Phase 98: Reporting-Worker Template Packaging

## Parent Issue
- Issue #: #600 (to be created on activation)

## Branch
- `feature/p98-reporting-worker-templates`

## Status
- **Active** – templates are being created.

## Goal
Package reporting‑worker templates and supervisor decision packets that proved useful in Phases 91/92.

## Completed Work
- Created `source_audit_decision_packet.md` template (Task P98.2).
- Created `supervisor_decision_packet_template.md` (Task P98.3).

## Remaining Tasks
- **P98.1** Audit existing reporting artifacts for reuse.
  - Review P91 source‑audit decision packet, P73 overlay catalog, and P70‑Ticket‑C worker result templates.
  - Document scope boundaries and identify reusable structures versus TSA23‑specific ones.

## Next Steps
- Perform the audit (P98.1) and update this note with findings.
- Once audited, create any additional templates or validation schemas needed.

## Audit Findings (P98.1)

The audit of existing reporting artifacts identified **reusable structures** that can be abstracted into generic templates for future reporting‑worker phases, as well as **TSA23‑specific elements** that should remain scoped to that experiment.

### Reusable Components
- **Decision packet JSON schema** – The top‑level keys in `p91_source_audit_decision_packet.json` (`packet_id`, `phase`, `generated_utc`, `quality_outcome`, `protocol_outcome`, `economics_governance_outcome`, etc.) form a stable contract that can be reused for any source‑audit worker.  A generic JSON Schema file can be extracted and referenced from the new `source_audit_decision_packet.md` template.
- **Protocol outcome breakdown** – The nested `defect_class_counts`, `functional_success_level_counts`, and `repair_effort_counts` sections provide a consistent way to report protocol‑level metrics.  These tables are already rendered in the markdown template and can be populated automatically from any worker JSON.
- **Economics governance note** – The `economics_governance_outcome` object contains wording about roadmap, changelog, issue, PR, and validation work that is applicable to all reporting workers regardless of domain.
- **Supervisor decision packet pattern** – The structure used in `supervisor_decision_packet_template.md` (decision summary, quality metrics table, protocol compliance notes, economics note, recommended actions) mirrors the content needed for any supervisor review of a worker report.  This can be turned into a reusable markdown include.
- **Worker result template fields** – The sections in `templates/worker_result.md` (`Final Status`, `Commands Run`, `Files Changed`, `Checks Run`, `Evidence`, `Blockers Or Errors`, `Notes For Supervisor`) are generic placeholders for any worker output and should be retained as‑is for future workers.

### TSA23‑Specific Elements
- **"sample_useful_yield"** metric – Calculated specifically for the TSA23 pilot; other pilots may use a different yield definition.
- **`accepted_record_scope_note` wording** – References “bounded P91 audit sample” which is unique to this run and should be replaced with context‑appropriate language in new phases.
- **References to specific artifact paths** (`benchmarks/document_library/p91_reporting_worker_draft_packet.json`, `p91_supervisor_source_audit_packet.json`) that are tied to the TSA23 data set.  Future templates should use placeholder paths (e.g., `<reporting_worker_draft_path>`).

### Action Items Derived from Audit
- Create a **JSON Schema** file (`schemas/source_audit_decision_packet_schema.json`) capturing the reusable keys identified above.
- Update `templates/source_audit_decision_packet.md` to reference the new schema and replace TSA23‑specific wording with placeholders.
- Add a short **validation guide** markdown (`docs/decision_packet_validation.md`) that shows how to validate a worker JSON against the schema using Python's `jsonschema` library.
- Ensure `templates/supervisor_decision_packet_template.md` mentions “generic protocol outcome” rather than TSA23‑specific counts.
- No changes needed for the `worker_result.md` template; it already serves as a generic scaffold.

## Audit Findings (P98.1)

The audit of existing reporting artifacts identified **reusable structures** that can be abstracted into generic templates for future reporting‑worker phases, as well as **TSA23‑specific elements** that should remain scoped to that experiment.

### Reusable Components
- **Decision packet JSON schema** – The top‑level keys in `p91_source_audit_decision_packet.json` (`packet_id`, `phase`, `generated_utc`, `quality_outcome`, `protocol_outcome`, `economics_governance_outcome`, etc.) form a stable contract that can be reused for any source‑audit worker.  A generic JSON Schema file can be extracted and referenced from the new `source_audit_decision_packet.md` template.
- **Protocol outcome breakdown** – The nested `defect_class_counts`, `functional_success_level_counts`, and `repair_effort_counts` sections provide a consistent way to report protocol‑level metrics.  These tables are already rendered in the markdown template and can be populated automatically from any worker JSON.
- **Economics governance note** – The `economics_governance_outcome` object contains wording about roadmap, changelog, issue, PR, and validation work that is applicable to all reporting workers regardless of domain.
- **Supervisor decision packet pattern** – The structure used in `supervisor_decision_packet_template.md` (decision summary, quality metrics table, protocol compliance notes, economics note, recommended actions) mirrors the content needed for any supervisor review of a worker report.  This can be turned into a reusable markdown include.
- **Worker result template fields** – The sections in `templates/worker_result.md` (`Final Status`, `Commands Run`, `Files Changed`, `Checks Run`, `Evidence`, `Blockers Or Errors`, `Notes For Supervisor`) are generic placeholders for any worker output and should be retained as‑is for future workers.

### TSA23‑Specific Elements
- **"sample_useful_yield"** metric – Calculated specifically for the TSA23 pilot; other pilots may use a different yield definition.
- **`accepted_record_scope_note` wording** – References “bounded P91 audit sample” which is unique to this run and should be replaced with context‑appropriate language in new phases.
- **References to specific artifact paths** (`benchmarks/document_library/p91_reporting_worker_draft_packet.json`, `p91_supervisor_source_audit_packet.json`) that are tied to the TSA23 data set.  Future templates should use placeholder paths (e.g., `<reporting_worker_draft_path>`).

### Action Items Derived from Audit
- Create a **JSON Schema** file (`schemas/source_audit_decision_packet_schema.json`) capturing the reusable keys identified above.
- Update `templates/source_audit_decision_packet.md` to reference the new schema and replace TSA23‑specific wording with placeholders.
- Add a short **validation guide** markdown (`docs/decision_packet_validation.md`) that shows how to validate a worker JSON against the schema using Python's `jsonschema` library.
- Ensure `templates/supervisor_decision_packet_template.md` mentions “generic protocol outcome” rather than TSA23‑specific counts.
- No changes needed for the `worker_result.md` template; it already serves as a generic scaffold.
