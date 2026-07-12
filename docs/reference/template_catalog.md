Template Catalog
===============

Agent Workbench provides reusable workflow graph templates in `templates/workbench_templates/`. These are non-executing metadata envelopes that declare node structure, provider assignments, dependency ordering, and governance annotations for target-project use.

**Promoted Templates (active)**:

- **document_artifact_audit_supervisor_graph**: Supervisor-led audit workflow with verification nodes (10 nodes). Used for systematic document artifact review cycles.
- **document_library_index_workflow**: Full document indexing pipeline (10 nodes). Turns public technical-document corpora into source-anchored metadata indexes through register→extract→verify steps.
- **patch_proposal_verification_graph**: Patch proposal and verification workflow (8 nodes). Manages structured patch submission, review, and acceptance cycles.
- **restricted_tool_trial_graph**: Restricted tool usage trial template (6 nodes). Provides a safe sandbox for testing worker tool access patterns before general deployment.

**Retired Templates**:

- These templates have been superseded by current workflow protocols or are no longer actively used. Details in `templates/workbench_templates/README.md`.

**Keep-as-Example**:

- Historical templates preserved as implementation examples but not recommended for direct use. See README for details.

**Not-in-Scope**:

- Templates designed for specific projects or contexts outside Agent Workbench's generic governance scope.

Full classification table and descriptions are maintained in `templates/workbench_templates/README.md`.
