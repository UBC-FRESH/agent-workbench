# P97.3 Workflow Graph Instantiation Guide (Draft)

**Status:** draft — temporary markdown, pending translation to RST for Sphinx docs
**Scope:** How a target project instantiates and uses a reusable workflow graph template from Agent Workbench
**Reference template:** `document_library_index_workflow.json` in `templates/workbench_templates/`

---

## Purpose

A **workflow graph template** is a non-executing metadata envelope. It declares what nodes should exist, what each node's provider and outputs are, dependency ordering (`needs`), and governance annotations — but it does NOT execute anything. Target-project tooling (or the project's own runner) interprets the graph and carries out actual work.

This guide walks through the instantiation lifecycle: select a corpus, run extraction, audit, promote, using the document library index workflow as the canonical example.

---

## 1. Select or Create a Corpus

Every document-indexing workflow starts with a corpus — a collection of public documents that the target project owns or has rights to process.

**Corpus requirements:**
- Public-safe content (no personal data, credentials, private paths)
- Documents in a known format (PDF, plain text, HTML, etc.)
- A manifest or directory structure the extraction tooling can enumerate

**Example corpus layout:**
```
target_project/benchmarks/document_library/
  ├── corpus_registry.json          # Created by P1 of workflow
  └── <document_id>/
      ├── source.pdf                # Raw document (ignored from git)
      └── metadata.yaml             # Document-level metadata
```

---

## 2. Node 1 — Register Corpus Documents

**Template node ID:** `register_corpus_documents`
**Provider:** `agent_workbench.script.registry`
**Node kind:** `script_prepare`

This first node creates or updates a corpus registry with document provenance, SHA256 hashes, document type, management unit, and extraction status.

**What the target project must do:**
1. Ensure the target project has (or installs) the `agent_workbench.script.registry` script/module, or maps this node to an equivalent native script.
2. Run the registration step against the corpus directory. The output is a `corpus_registry.json` that will be promoted as a tracked file.

**Governance boundaries (from template):**
- Script may register sanitized document metadata only
- Raw documents and extracted text stay outside tracked Agent Workbench files

---

## 3. Node 2 — Extract Text Chunks

**Template node ID:** `extract_text_chunks`
**Provider:** `target_project.text_extraction`
**Node kind:** `project_native_extraction`

This node depends on Node 1 (`register_corpus_documents`). It extracts document text into page or section chunks and writes a tracked sanitized chunk manifest.

**What the target project must do:**
1. Provide or configure a native text extraction tool (the template uses `target_project.text_extraction` as a provider placeholder — replace with actual implementation).
2. The extraction tool should write:
   - A **sanitized chunk manifest** promoted to tracked files (e.g., `chunk_manifest.json`)
   - **Raw text chunks** kept in ignored storage (`runtime/` or `.gitignore`d paths)

**Governance boundaries:**
- Target-project tooling extracts text and writes ignored raw chunks plus a sanitized manifest
- Raw text policy: "ignored or data-managed outside Agent Workbench"

---

## 4. Node 3 — Declare Budget and Stop Rules

**Template node ID:** `declare_budget_and_stop_rules`
**Provider:** `agent_workbench.supervisor.budget`

This is a governance gate that validates P59-style budget declarations before any live worker call that may support economics claims. It does not process documents; it ensures the run has declared spending limits and stop conditions.

---

## 5. Audit and Verify

After running Nodes 1–2 (and through Node 3's governance gate), the supervisor should:
- Verify `corpus_registry.json` exists and is valid JSON
- Verify all chunk manifests exist for registered documents
- Inspect promoted files for private data leakage
- Run deterministic validators if available

---

## 6. Promote Artifacts

Promoted artifacts (those marked `"kind": "promoted"` in the template) become tracked files in the target project:
- `corpus_registry.json` — document registry with provenance
- `<document_id>/chunk_manifest.json` — per-document chunk manifests

These promoted files are what downstream nodes (or external tools) consume. They are public-safe and version-controlled.

---

## Mapping to Your Project

To adapt this workflow graph template for your own target project:

1. **Replace provider values** — Change `"agent_workbench.script.registry"` or `"target_project.text_extraction"` to your actual script/module/provider names.
2. **Adjust artifact paths** — Update `"path_or_reference"` values in the `artifacts` arrays to match your project's directory structure.
3. **Add domain-specific nodes** — Insert additional nodes for tasks like "build index," "run retrieval benchmark," or "evaluate quality."
4. **Keep governance annotations** — Preserve `parameters.agent_workbench` sections that declare `node_kind`, `execution_boundary`, `token_accounting`, and `public_safety`. These are what make the graph template self-documenting for supervisors.

---

## Quick Reference: Promoted Template Roles

| Template ID | Role | Node Count |
|---|---|---|
| `document_artifact_audit_supervisor_graph` | Supervisor-led audit with verification nodes | 10 |
| `document_library_index_workflow` | Full document indexing pipeline (this guide) | 10 |
| `patch_proposal_verification_graph` | Patch proposal and verification workflow | 8 |
| `restricted_tool_trial_graph` | Restricted tool usage trial | 6 |

---

**Next steps for Sphinx integration:** Convert this markdown to RST, inject into `docs/guides/` directory as part of Phase 101 docs scaffold.
