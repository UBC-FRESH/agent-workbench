# Agent Workbench — Public Alpha Readiness Review

Date: 2026-07-12
Phase: P100
Author: coordinator (paid lane, thin-router contract)
Status: draft — awaiting maintainer review

---

## What Is Ready For External Review

**Governance and workflow contract** (P0-P19, P56, P66-P68): The authority hierarchy, delegation trust levels, supervisor/worker ticket protocol, file-based handoff, and evidence promotion rules are documented, stable, and in active use. `AGENTS.md` and `planning/delegation_policy.md` form a coherent public contract.

**Local CLI surface** (P21-P29, P56, P59, P65-P69, P76-P77, P95, P99): The `agent-workbench` package is installable from source (`pip install -e .`), provides a working help surface, and wraps the major supervisor workflows: evidence validation/synthesis, authority validation, economics dashboard, retrieval, pilot scaffolding, and model comparison. These commands have focused tests and have been dogfooded on real corpus artifacts.

**Reusable workflow graph templates** (P39, P43, P97): Four promoted graph templates in `templates/workbench_templates/` represent real-tested workflows — document library indexing, whole-document supervisor, document artifact audit, and managed delegate loop. These are FreshForge-compatible JSON artifacts validated through the graph command surface.

**Reporting and decision packet templates** (P91, P98): `templates/source_audit_decision_packet_template.md` and `templates/roi_decision_template.md` are generalized from the TSA23 real-corpus pilot. These can be applied to public technical document indexing tasks beyond the original corpus.

**Real-corpus document indexing pilot evidence** (P88-P94): The TSA23 2012 100 Mile House data package (`tsa23_2012_23tsdp12`) was indexed through a full extraction, source-audit, and provenance-promotion pipeline. 47 records were promoted with source anchors, model lane metadata, audit status, and provenance chain. This is the project's primary real-world evidence of the workflow delivering usable output.

**Retrieval and use-case layer** (P95): `agent-workbench retrieve` provides page-range lookup and full-document provenance trace against the promoted index, with a documented query contract and modelling-agent usage example.

**Sphinx documentation + GitHub Pages** (P101): Technical reference documentation is live at https://ubc-fresh.github.io/agent-workbench/ with CI/CD passing.

---

## What Remains Experimental

**Whole-document supervisor delegation shape** (P92): The whole-document supervisor approach (one delegated supervisor job over the full document, rather than a chunk-by-chunk pipeline) produced a quality-valid 28-record candidate. However, the economics are not yet proven: the measured coordinator token span was 449,382 tokens (447,232 cached-input), which exceeds the chunk-pipeline baseline of ~236,008 cached-input tokens for the same document. Reduced cached-context overhead is a prerequisite before the whole-doc shape produces positive economics.

**Profile/model comparison battery** (P75-P85): The repaired profile-evidence-review battery (P85) demonstrated that the review-subject access repair eliminated blocked results (47 accepted-candidate / 48 rows). However, this evidence is scoped to synthetic `profile-evidence-review` tasks over existing P75 profile summaries. It does not generalize to real-project task families without a new matched battery.

**Model lane comparison** (P96): The quantization-variant comparison (`qwen3.6:35b-a3b-q8_0` vs `qwen3.6:35b-a3b-bf16`) produced a partial signal from one bounded probe. The verdict is `attempted_with_partial_signal` — not sufficient for a broad model recommendation.

**Indexed-cost metric at scale** (P99): The indexed-cost metric formula (paid-supervisor tokens per promoted record by stage) is defined and implemented in `src/agent_workbench/economics.py`. The metric has been applied to P90-P92 pilot data. Full stage-level attribution for the complete 47-record promoted index was not completed, and the chunk-pipeline token baseline (~236,008 cached-input) is a minimum estimate rather than a complete account.

**FreshForge integration** (P41-P46): The optional `graph` dependency extra enables structural workflow validation via FreshForge. The integration has been tested and keeps FreshForge optional. Whether FreshForge becomes a recommended dependency for new users has not been decided.

---

## What Should Not Be Assumed Production-Ready

**The TSA23 index is a research pilot, not a production index**: The 47 promoted records cover one bounded document slice (pages 1-41 of one data package). The source audit sampled 16 of those records. No claim should be made that the full 47 records are audit-complete without expanding the source audit.

**The economics model is illustrative, not certified**: The delegation economics model (P31, P99) provides a vocabulary and formula for token/cash cost accounting. Measured values from P90-P92 are evidence-grounded estimates, not audited financials. Stage attribution is incomplete. External users should treat indexed-cost figures as directional indicators, not certified benchmarks.

**Worker model behavior claims are task-scoped**: All model behavior observations in this project are scoped to specific ticket families (structured documentation output, patch proposal, evidence review, document extraction) and the specific Ollama models tested. Do not generalize observed failure modes, strengths, or consistency rates to other models or task types.

**The SDK bridge requires a specific Ollama/provider setup**: The `agent-workbench copilot-sdk` commands and the Ollama worker delegation paths require a Cloudflare-gated Ollama endpoint with specific model inventory. These cannot be reproduced without equivalent infrastructure. The workflow contract documents are fully public-safe; the execution path requires operator-side setup.

**P100 does not constitute a security review**: This readiness review checks public-safety boundaries (no credentials, no private paths, no raw transcripts in tracked files). It does not constitute a security audit of the package code, dependency chain, or deployment environment.

---

## ROI Thesis Statement

Agent Workbench's working ROI hypothesis is: for bounded, well-scoped supervisor-worker tasks (structured output extraction, evidence review, repair proposals, documentation drafts), free local Ollama worker tokens can substitute for paid coordinator tokens in ways that produce net positive value — where value is measured as useful, source-backed promoted records per paid-coordinator token.

The strongest supporting evidence comes from the P90/P91 chunk pipeline, where 47 records were promoted and a bounded 16-record source audit showed 8 accepted and 7 repairable records, with supervisor source-audit effort estimated at fewer paid tokens than directly producing equivalent records from scratch.

The thesis remains unproven at scale. P92 showed that a naive whole-document delegation approach increased, not decreased, coordinator token cost. The roadmap priority before broader adoption is reducing cached-context and launch overhead in the whole-document delegation shape.

The thesis does not claim that delegation always saves money. The P31 economics model explicitly defines conditions under which delegation is net-negative: tasks that are too small (setup overhead exceeds savings), too large (cleanup and repair exceed savings), or in task families where worker accuracy is too low.

---

## Indexed-Cost Metric Summary

The P99 indexed-cost metric is defined as: **paid-supervisor tokens per promoted record**, broken down by stage:
- **Extraction stage**: coordinator tokens spent on ticket design, launch, and monitoring worker extraction runs
- **Repair-prepass stage**: coordinator tokens spent reviewing and applying deterministic repair
- **Audit stage**: coordinator tokens spent on source audit decisions
- **Index-assembly stage**: coordinator tokens spent on provenance validation and schema promotion

Measured approximate values from the TSA23 tsa23_2012_23tsdp12 pilot (P90-P94):
- Chunk-pipeline coordinator token baseline: ~236,008 cached-input tokens (minimum; stage attribution incomplete) for 47 promoted records → approximately 5,000 cached-input tokens per promoted record
- Whole-document pilot (P92): 449,382 total tokens (447,232 cached-input) for 28-record candidate → approximately 16,000 cached-input tokens per candidate record (not yet accepted; economics not proven)

The `agent-workbench economics render` command is available to compute and render these tables from accounting and token record inputs.

**Caution**: these figures are directional estimates from one pilot. They do not include baseline costs for direct supervisor implementation of the same work, so net savings are not yet computed.

---

## Open Questions For External Reviewers

1. **Workflow portability**: Does the document-indexing recipe (P62/P89) transfer to non-forestry technical corpora without major ticket redesign? The P93 second-corpus application suggested yes, but evidence is limited.

2. **Economics threshold for adoption**: At what indexed-cost value (paid tokens per promoted record) would the workflow become worth adopting for a project that currently has no document indexing? Is the current ~5,000 cached-input tokens per record compelling?

3. **Governance overhead**: Is the AGENTS.md authority hierarchy and ticket protocol the right level of formality for a public alpha user? What friction does it introduce for first-time adopters?

4. **Model portability**: The workflow was developed and tested on Cloudflare-gated Ollama models (qwen3.6, qwen3-coder families). What changes are needed to support other OpenAI-compatible endpoints, including cloud-hosted models?

5. **FreshForge dependency**: Should the graph validation and workflow graph templates be usable without FreshForge as a hard dependency, and is the current optional-extra design the right trade-off?

---

## Confidence Level

**Overall confidence in public-alpha readiness: MEDIUM-HIGH**

- The governance documents, workflow protocol, and CLI surface are stable and well-tested. Confidence is HIGH for these.
- The real-corpus pilot produces evidence-grounded, source-backed records with a documented provenance chain. Confidence is HIGH that the workflow produces useful output for the target corpus class.
- The economics model is well-structured but stage-level attribution is incomplete. Confidence is MEDIUM that the indexed-cost figures represent a fair estimate.
- Whole-document delegation economics are unproven (P92 cost exceeded chunk-pipeline baseline). Confidence is LOW that this shape is production-suitable without further optimization.
- Model comparison evidence is limited to one quantization-variant probe (P96). Confidence is LOW for model selection guidance beyond the tested qwen3.6 variants.

The project is ready for external review of its governance model, workflow protocol, CLI surface, and real-corpus pilot evidence. It is not ready for broad production adoption without operator-specific infrastructure setup, further economics attribution, and expansion of the source audit.
