# Agent Workbench Project History — Origin to Convergence

## Provenance

This narrative is maintained by the coordinator and updated at each major
inflection point. It is the canonical orientation document for freshly-spawned
agents. **Last updated: 2026-07-21.**

---

## Origin: The Token Crisis (mid-2026)

The UBC-FRESH research lab, led by the PI (principal investigator / human
developer), was building a forest estate modelling system called **FEMIC** for
graduate student thesis research. FEMIC requires parsing and indexing hundreds
of pages of complex technical documents—30 years of "Timber Supply Review" and
"Annual Allowable Cut Level Determination" reports for Timber Supply Area 23
(TSA 23) in British Columbia, Canada. These documents vary wildly in structure
and format across cycles (1995, 2001, 2006, 2012) and require detailed, accurate
metadata indexing that is efficiently machine-searchable.

The PI was using a single GPT-5.5/5.6 coding agent in the VS Code Codex Chat
extension on a Windows 11 laptop. The work was producing good results, but the
OpenAI API token costs were unsustainable for the scope: grinding through
thousands of pages of PDFs in divergent formats, building detailed metadata
indices, and iterating on quality burned through tokens at a rate that outpaced
available funding. Unlike graduate student stipends or hardware grants,
dedicated LLM token funding is extremely hard to secure.

**Motivation:** Can we do this same high-quality document parsing and indexing
work using open-weight models running on lab-owned hardware, eliminating per-
token marginal cost entirely?

## Hardware Advantage

The lab has significant compute infrastructure: a dev server with 768 GB RAM,
dual Xeon Gold CPUs (72 logical cores), and an **NVIDIA RTX PRO 6000 Blackwell**
GPU. The PI also has a research grant earmarked for hardware procurement
(could buy 5-8 more machines). The hardware cost is fixed and amortizable; the
token cost is variable and unbounded.

---

## Era 1: Foundation and Bridge Exploration (P0–P54)

**Planning notes:**
[`delegation_economics_vision.md`](planning/delegation_economics_vision.md),
[`phase6_copilot_sdk_ollama_spike_notes.md`](planning/phase6_copilot_sdk_ollama_spike_notes.md)

**Goal:** Establish the Agent Workbench governance and prove that a remote,
self-hosted Ollama model can participate in an agent workflow.

First attempt: set up an Ollama server on the dev server, expose it as a system
service, pipe through a Cloudflare zero-trust tunnel, and connect the VS Code
Ollama extension to translate Ollama traffic to Copilot's API format for tool
and skill discovery.

**Result:** The bridge worked, but open-weight models proved substantially
weaker than frontier closed models for the delegation workloads under test.
Conversations stalled frequently. The Copilot SDK bridge was unstable.

Throughout this era, the Workbench built its governance surface:
- **P0–P5** — Governance scaffold, worker protocol templates, bridge prototypes
- **P6–P12** — Copilot SDK Ollama feasibility, structured output trials, tool-trials
- **P13–P40** — GitHub workflows, packaging, evidence schema, token-cost ingestion
- **P41–P54** — FreshForge graph integration spike (later abandoned), managed
  delegation workflows, document-library pilot

**Lesson:** Proof-of-concept success ≠ economic viability. A worker can produce
plausible output and still cost more (in supervisor verification and repair)
than direct execution.

## Era 2: Real-Project Pilot on TSA23 (P55–P70)

**Planning notes:**
[`phase55_tsa23_indexing_battery.md`](planning/phase55_tsa23_indexing_battery.md),
[`phase63_bounded_tsa23_recipe_pilot.md`](planning/phase63_bounded_tsa23_recipe_pilot.md),
[`phase70_femic_p108_repair_dogfood.md`](planning/phase70_femic_p108_repair_dogfood.md)

**Goal:** Test the document-indexing workflow on real TSA23 corpus data and
measure delegation economics against a paid-superivisor baseline.

**P55** ran the first real TSA23 document-indexing experiment against 2012 TSR
documents. It exposed real failure modes: provider 524 (model call failure),
fenced output, malformed JSONL, invalid chunk IDs.

**P63** ran a bounded recipe pilot on a repeat slice. **P90–P92** attempted
whole-document extraction and supervision. **P95** tested index retrieval
usability. **P96** compared model lanes (bf16 vs q8_0 quantization).

**P70** dogfood-tested the task-level delegation controller on real FEMIC P108
cleanup tasks in the sister FEMIC repository, proving the Workbench could
manage cross-project cleanup work.

**Result:** The indexing workflow produces quality-valid output on bounded
slices but struggles at scale. Economics are directionally favorable but not
yet proven at the confidence threshold for full deployment.

## Era 3: Economics Measurement and Decision Framework (P71–P107)

**Planning notes:**
[`p107_economics_research_program.md`](planning/p107_economics_research_program.md),
[`p107_substantial_workload_capability_plan.md`](planning/p107_substantial_workload_capability_plan.md),
[`delegation_policy.md`](planning/delegation_policy.md)

**Goal:** Replace gut-feeling delegation decisions with frozen evaluation blocks,
catalog-backed pricing, and three-dimension verdicts (quality, protocol,
economics).

**P88** created the real-corpus benchmark registry. **P89** built the document-
indexing recipe v2 with 120-ticket dry-run materialization. **P91** ran source
audit decision packets. **P94** promoted project-owned indices.

**P104** established canonical model pricing and economics provenance
([`model_profiles/pricing_catalog.json`](model_profiles/pricing_catalog.json)).

**P106** ran matched direct-vs-delegated execution. Quality validated, but
protocol and economics were not accepted.

**P107** is the crown jewel: a reproducible economic-performance data collection
program with frozen evaluation blocks (C0–C4 configurations), native protocol
evidence, and catalog-backed accounting. P107 was closed as a *bounded tranche*
with accepted observations recorded but no final cross-epoch ROI claim.

**Key artifact:** The [`p107_economics_research_program.md`](planning/p107_economics_research_program.md)
planning note defines the configuration ladder (C0: paid coordinator alone;
C1: paid coordinator → Luna worker; C2: paid coordinator → Ollama worker;
C3: Luna alone; C4: Luna coordinator → Ollama worker) and the measurement
protocol.

**Result:** Measurement before claims. The framework is in place.

**Note (P118 pivot):** The economics dimension was designed for the multi-model
era (paid coordinator vs. free worker). After P118's pivot to single-model
vLLM on lab-owned GPU with zero marginal token cost, the economics question is
largely moot. The P107 framework remains a historical artifact and a reference
for other labs still running paid-vs-free topologies, but it no longer governs
Agent Workbench's own operating decisions.

## Era 4: Native Codex and Capability Parity (P102–P117)

**Planning notes:**
[`native_codex_remote_ollama_findings.md`](planning/native_codex_remote_ollama_findings.md),
[`phase113_codex_ollama_function_tool_adapter.md`](planning/phase113_codex_ollama_function_tool_adapter.md),
[`p114_vs_code_worker_mcp_breakthrough.md`](planning/p114_vs_code_worker_mcp_breakthrough.md),
[`p116_event_driven_supervision_control_plane_plan.md`](planning/p116_event_driven_supervision_control_plane_plan.md)

**Goal:** Escape the Copilot SDK dependency and prove that Ollama workers can
use tools natively, on par with paid agents.

**P102** proved native Codex can use a remote Ollama provider directly through
its Responses API, removing Copilot from the critical path. The Copilot-specific
bridge is no longer a prerequisite for free-model delegation.

**P111** proved native recursive UI delegation works in the Codex Chat
experience.

**P113** built a Codex-Ollama `apply_patch` function-call adapter sandbox,
proving that Ollama workers can execute native patch operations through a
custom function-tool bridge. PRs #652 and #653.

**P114** ran a comprehensive capability parity battery. Three independent
composite observations (r3, r4, r5) passed. **P114 admitted the C4 package
route as baseline-valid** for P107 reentry. The Codex-Ollama adapter route was
proven to work; it was abandoned later for *strategic* reasons (P118's single-
model architecture), not because P114 proved it couldn't work.

**P116** established the bounded native in-session supervision control layer.
**P117** proved a run-scoped supervision daemon.

**Result:** The Ollama adapter route was technically viable but architecturally
fragile—six independently fragile layers made failures hard to localize. The
project needed a simpler foundation.

## Era 5: Convergence — Single-Model vLLM Agent Hub (P118–P119)

**Planning notes:**
[`p118_fresh_vllm_agent_plan.md`](planning/p118_fresh_vllm_agent_plan.md),
[`p119_blackwell_vllm_concurrency_profile.md`](planning/p119_blackwell_vllm_concurrency_profile.md)

**Goal:** Replace the multi-model, multi-adapter architecture with one model,
one GPU, bounded roles, native delegation.

The PI compiled a custom Qwen 3.6 27B "coder" variant optimized for the
Blackwell GPU, deployed it through vLLM (not Ollama) with concurrency support
for up to 8 concurrent sessions, and built a custom vLLM→Copilot extension.

**P118** established the single-model operating contract:
- One configured remote vLLM model serves Coordinator, Supervisor, Worker,
  and Advisor roles through distinct bounded instructions
- Role separation comes from authority and instruction, not from deploying
  different models
- Concurrency contract: 2-4 parallel agents for independent work, serial for
  coupled or mutating work
- **P118.1** (merged PR #714): Provider binding and role-profile contract,
  AGENTS.md de-bloat from ~450 to ~70 lines
- **P118.6**: Read-only concurrency validated (3 parallel read_file probes,
  no failures)
- **P118.6.2**: Tool-intensive concurrency stress test — 4 parallel probes
  using `grep_search`, `file_search`, and `read_file` across 190+ files with
  18+ tool invocations, no degradation observed. Coupled mutating-work
  concurrency (parallel file edits) remains deferred to future phases

**P119** packaged the sanitized Blackwell vLLM lab as a deployment playbook
([`playbooks/vllm_blackwell/`](playbooks/vllm_blackwell)). PR #720.

**Result:** The architecture that emerged is dramatically simpler than anything
attempted in Eras 1-4. One model, one GPU, bounded roles, native `runSubagent`
delegation. **The economics dimension that drove Eras 1-3 is now moot** — zero
marginal token cost on lab-owned GPU means the paid-vs-free question no longer
governs our operating decisions.

## Supporting Infrastructure

Parallel to the main arc, several phases built supporting infrastructure:

- **P56** — Authority hierarchy and supervisor contract scaffold
  ([`authority_hierarchy_and_subagent_direction.md`](planning/authority_hierarchy_and_subagent_direction.md))
- **P97** — Reusable workflow graph packaging
- **P98** — Reporting-worker template packaging
- **P99** — Economics dashboard and indexed-cost metric
  ([`src/agent_workbench/economics.py`](src/agent_workbench/economics.py))
- **P100** — Public alpha readiness review
- **P101** — Sphinx documentation and GitHub Pages
  (live at https://ubc-fresh.github.io/agent-workbench/)
- **P115** — Scientific artifact-inspection bridge pilot (23 passing tests,
  delegated inspection via `runSubagent` with bounded `femic-rebuild-inspector`
  profile). This replaced the P114 adapter route and proved `runSubagent` with
  bounded profiles is the production delegation path.

## Present State (2026-07-21)

- **Operating model:** Single Qwen 3.6 27B vLLM model on Blackwell GPU
- **Delegation path:** Native Agent Hub (`runSubagent` with bounded profiles)
- **Supervision:** Coordinator → Supervisor → Worker, all same model
- **Delegation transport:** Ollama SDK deprecated; native Agent Hub is the default
- **Target workload:** FEMIC TSA23 document indexing
- **Next phases:** P108 (TSA23 slice preparation, activated), P109 (productive
  delegated pilot), P110 (alpha readiness refresh)
- **Repository:** Clean main branch, zero open issues
- **Economics status:** The P107 economics framework (paid vs. free token
  comparison) is no longer a governing dimension for our own work. P118's pivot
  to single-model vLLM on lab-owned hardware means zero marginal token cost.
  The framework remains a historical artifact and reference for other labs
  running paid-vs-free topologies.

## Lessons Learned

1. **Follow the seam, not the plan.** The working architecture (single-model
   vLLM) was not the planned architecture (multi-model Ollama bridge). The path
   to it required 118+ phases across multiple development eras, with several
   revisits and course corrections.

2. **Authority beats capability.** *(P56, P118)* Bounded instructions, tool
   permissions, and explicit constraints create more discipline than model
   quality alone.

3. **Dead weight compounds.** The Ollama adapter and Copilot SDK bridge were
   hooks in dead-end chains. Recognizing dead weight early is more valuable than
   perfecting it.

4. **Simple beats clever.** One model, one GPU, bounded roles, native
   delegation. The complexity was in the get-there path, not the destination.

5. **Measurement before claims.** *(P107)* Frozen evaluation blocks and three-
   dimension verdicts (quality, protocol, economics) prevented premature
   conclusions.

6. **One phase at a time.** Concurrent sessions editing shared files (CHANGE_LOG,
   ROADMAP) create merge debt. `git rebase --onto main <fork-point>` is the
   correct pattern for replaying only divergent commits.

---

## Forward-Looking Notes

### Domain-Specific Agent Profiles

P118's single-model stack means adding a new worker profile costs zero
(instructions, not model deployment). The plan is to define domain-specific
profiles on-demand during P109+ rather than speculating now:
*document-metadata-extractor*, *UBC-FRESH-dev-workflow-auditor*, *new-dev-
phase-planner*, *github-workflow-expert*, *project-documentation-editor*, etc.
A profile becomes persistent (`.agent.md`) when the pattern repeats across
2+ phases. P115's `femic-rebuild-inspector` is the precedent.

### FreshForge / MCP Re-Entry

The FreshForge graph workflow vehicle is parked, not dead. The P46 decision
(no dependency until delegation transport was proven) is now satisfied —
`runSubagent` with bounded profiles is proven. A plausible re-entry path: a
custom MCP server exposing graph-traversal, dependency-resolution, and workflow-
state tools, with skills assigning those tools to specific agent roles. This is
a P120+ question, not a P108-P110 blocker.

### Economics (P107) — Historical Artifact

The P107 economics framework was designed for the multi-model era (paid
coordinator vs. free Ollama worker). After P118's pivot to single-model vLLM
on lab-owned GPU with zero marginal token cost, the economics dimension is no
longer a governing question for Agent Workbench's own operating decisions. The
P107 framework remains useful as a historical reference and as a template for
other labs still running paid-vs-free topologies.

---

## References

| Topic | Artifact |
| --- | --- |
| Project purpose | [`AGENTS.md`](AGENTS.md) |
| Authority hierarchy | [`planning/authority_hierarchy_and_subagent_direction.md`](planning/authority_hierarchy_and_subagent_direction.md) |
| Delegation economics | [`planning/delegation_economics_vision.md`](planning/delegation_economics_vision.md), [`planning/p107_economics_research_program.md`](planning/p107_economics_research_program.md) *(historical artifact, no longer governing post-P118)* |
| Delegation policy | [`planning/delegation_policy.md`](planning/delegation_policy.md) |
| Operating contract | [`AGENTS.md`](AGENTS.md) concurrency section, [`planning/p118_fresh_vllm_agent_plan.md`](planning/p118_fresh_vllm_agent_plan.md) |
| Blackwell deployment | [`playbooks/vllm_blackwell/`](playbooks/vllm_blackwell/) |
| TSA23 corpus | [`benchmarks/document_library/tsa23_tsr/corpus_registry.json`](benchmarks/document_library/tsa23_tsr/corpus_registry.json) |
| Model pricing | [`model_profiles/pricing_catalog.json`](model_profiles/pricing_catalog.json) |
| Economics module | [`src/agent_workbench/economics.py`](src/agent_workbench/economics.py) |
| Documentation | https://ubc-fresh.github.io/agent-workbench/ |
| FEMIC context | External project (not tracked in this repo) |
| Agent profiles | [`.github/agents/`](.github/agents/) |