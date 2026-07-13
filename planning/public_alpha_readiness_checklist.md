# Agent Workbench — Public Alpha Readiness Checklist

Date: 2026-07-12
Phase: P100
Compiled by: coordinator (paid lane, thin-router contract)
Status: draft — awaiting maintainer review before public release

---

## 1. Public-Safety

- [x] **PASS** No credentials or tokens in tracked files — `.gitignore` covers `runtime/`, `tmp/`, `local/`, `outputs/` and CF credential files; `runtime/local_provider_headers.json` is not tracked
- [x] **PASS** No personal home-directory paths in tracked files — all tracked docs use repo-relative paths or `<workspace-root>` placeholders
- [x] **PASS** No raw private transcripts in tracked files — raw session transcripts go only to `runtime/` and `tmp/` (ignored)
- [x] **PASS** No unintended project-specific contamination — FEMIC/FreshForge references in tracked files are public-safe cross-project examples only; no proprietary model outputs or private issue URLs
- [x] **PASS** `.gitignore` covers all scratch areas — `runtime/`, `tmp/`, `local/`, `outputs/`, `.venv/`, `_build/`, `*.pyc` all excluded

---

## 2. Templates and Schema

- [x] **PASS** `templates/supervisor_ticket.md` — present; defines current-state, task-boundary, allowed/forbidden actions, and evidence requirements
- [x] **PASS** `templates/worker_result.md` — present; defines command/file/check/GitHub evidence and final status
- [x] **PASS** `templates/evidence_summary.schema.json` — present; defines required summary fields (P17)
- [x] **PASS** P98 reporting-worker templates — `templates/source_audit_decision_packet_template.md` and `templates/roi_decision_template.md` present (P98)
- [x] **PASS** P97 graph templates (4 promoted) — `templates/workbench_templates/` contains:
  - `document_library_index_workflow.json`
  - `document_library_whole_document_supervisor_graph.json`
  - `document_artifact_audit_supervisor_graph.json`
  - `managed_delegate_loop_graph.json`
  - README with classification table and instantiation guide
- [x] **PASS** P95 query schemas — `templates/query_schemas/` contains page-range, full-doc-trace, and response schemas

---

## 3. CLI Surface

- [x] **PASS** `agent-workbench --help` and `--version` — available after editable install (`pip install -e .`)
- [x] **PASS** `agent-workbench smoke` — wraps `scripts/check_command_surfaces.py` (P22)
- [x] **PASS** `agent-workbench evidence validate/render/synthesize` — P23/P27
- [x] **PASS** `agent-workbench authority validate/render` — P56
- [x] **PASS** `agent-workbench economics render` — P99; takes accounting + token records, produces indexed-cost Markdown table
- [x] **PASS** `agent-workbench retrieve` — P95; `list-docs`, `page-range`, `trace` operations against promoted index
- [x] **PASS** `agent-workbench pilot scaffold/pack-scaffold` — P25/P27
- [x] **PASS** `agent-workbench compare eval` — P29
- [x] **PASS** `agent-workbench graph validate` — P41 (requires optional `graph` extra)
- [x] **PASS** `agent-workbench copilot-sdk health-gate/profile-validate/catalog-validate` — P81/P72/P73
- [x] **PASS** `agent-workbench foundrytk profile-evaluation-aggregate/profile-contract-repair-plan` — P76/P77
- [~] **PARTIAL** `agent-workbench benchmark prepare-worktrees` — present (P49) but the benchmark workflow it supports (FreshForge P16 A/B) was concluded without a decisive winner (P50 qualified)

---

## 4. ROI Thesis and Indexed-Cost Metric

- [x] **PASS** ROI thesis is stated in public-safe language — `planning/delegation_economics_vision.md` (P31) defines the cost/benefit model: avoid paid supervisor tokens by delegating bounded tasks to free local Ollama workers; net benefit = avoided supervisor cost − (delegation overhead + verification + cleanup)
- [x] **PASS** Indexed-cost metric defined — P99 defines paid-supervisor tokens per promoted record by stage (extraction, repair-prepass, audit, index-assembly); implemented in `src/agent_workbench/economics.py`
- [x] **PASS** Real-corpus extraction evidence tracked — P88-P94 TSA23 `tsa23_2012_23tsdp12` pilot:
  - 47 records promoted with provenance (P94)
  - P91 source audit: 8 accepted (recalibrated: 7 repairable, 1 rejected from 16-record sample)
  - P92 whole-doc pilot: 28-record quality-valid/protocol-accepted candidate; economics not yet proven at scale
- [x] **PASS** Decision packet shape separates outcome dimensions — P60 semantics applied: `quality_validated_candidate`, `protocol_accepted_candidate`, `economics_usable` are distinct fields in decision packets
- [~] **PARTIAL** Indexed-cost value measured but attribution incomplete — P92 measured 449,382 coordinator tokens for one whole-doc run; P90/P91 chunk pipeline measured ~236,008 cached-input tokens minimum; full stage-level attribution across all promoted records was not completed; P96 model comparison produced partial signal only

---

## 5. Governance

- [x] **PASS** `AGENTS.md` — current authority hierarchy (developer → coordinator → supervisor → worker), delegation trust levels L0-L6, paid-supervisor cost discipline, file-based handoff protocol, planning workflow
- [x] **PASS** `planning/delegation_policy.md` — L0-L6 trust levels with productive-delegation mode defined
- [x] **PASS** `ROADMAP.md` and `CHANGE_LOG.md` synchronized — P88-P99 and P101 recorded; issue/PR references present for all complete phases; P100 active
- [x] **PASS** Nondelegable supervisor actions documented — `AGENTS.md` lists tracked-file commits, branch pushes, PR creation, PR merge, issue closure, release publication, model/provider config changes as nondelegable
- [x] **PASS** Paid-supervisor cost discipline rules present — `AGENTS.md` includes budget declaration requirements, one-failed-run repair limit, consolidation preference over repeated runs

---

## Summary

| Area | Status | Notes |
|------|--------|-------|
| Public-Safety | **PASS** | All 5 items pass |
| Templates and Schema | **PASS** | All 6 items pass |
| CLI Surface | **PASS / PARTIAL** | 11 pass, 1 partial (benchmark workflow qualified) |
| ROI Thesis | **PASS / PARTIAL** | 4 pass, 1 partial (stage-level attribution incomplete) |
| Governance | **PASS** | All 5 items pass |

**Overall readiness verdict**: PASS WITH NOTED LIMITATIONS — suitable for public alpha with the limitations documented in the review note.
