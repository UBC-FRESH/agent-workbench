Roadmap Overview
==============

Agent Workbench follows a phase/task/subtask workflow documented in `ROADMAP.md`. Below is a summary of completed and active phases. For the complete issue tracker map with parent issues, branches, and status, see `ROADMAP.md` in the repository root.

## Phase Progression

**P0–P100 (Foundation)**: Governance scaffold, worker protocol templates, SDK probes, structured evidence, CLI surface, document library indexing, authority hierarchy, delegated workflow lanes, economics model, benchmark infrastructure, Sphinx documentation, and public alpha readiness review. This tranche established the supervisor-worker contract, the evidence store, the CLI dogfood workflow, and the published docs site at <https://ubc-fresh.github.io/agent-workbench/>.

**P101–P117 (Integration and Control Layer)**: A focused build of mature capabilities built on the foundation:

| Phase | Topic | Status |
| --- | --- | --- |
| P101 | Sphinx technical documentation and GitHub Pages | Complete — live site, CI passing |
| P102 | Native Codex + remote Ollama orchestration | Complete (qualified) |
| P103 | Paid Coordinator economics trial | Complete (qualified) |
| P104 | Canonical model pricing and economics provenance | Complete |
| P105 | Matched public-corpus benchmark contract | Complete |
| P106 | Matched direct-vs-delegated execution | Complete (qualified) |
| P107 | Economics decision and delegation policy | Complete (bounded tranche) |
| P111 | Native recursive Codex UI delegation | Complete |
| P113 | Codex-Ollama function-tool adapter sandbox | Complete |
| P114 | Codex-Ollama C4 capability parity and viability | Complete |
| P116 | Event-driven supervision control plane | Complete — bounded in-session control layer |
| P117 | Run-scoped supervision daemon | Complete — bounded run-scoped proof |

This tranche delivered Codex integration, a function-tool adapter, event-driven supervision, and a run-scoped daemon. A key design decision was to keep the control layer bounded: no autonomous or unattended runtime claims.

## Current Active Phase

**P118 — FRESH vLLM Agent** (parent issue #718; branch `feature/p118-fresh-vllm-agent`)

Goal: establish a usable native VS Code Copilot Agent Hub deployment in which **one configured remote vLLM model** serves the Coordinator, Supervisor, Worker, and Advisor roles through distinct custom-agent instructions. Role separation comes from bounded authority and instructions, not from different underlying models.

The GPU constraint means this is a **serial single-model deployment**: at most one intensive child may be actively reasoning at a time. Parallel fan-out will overflow VRAM.

### P118 Tasks

| Task | Description | Status |
| --- | --- | --- |
| P118.1 | Provider and role-profile contract | Complete — merged via PR #714 |
| P118.2 | Serial single-model operating contract | Complete |
| P118.3 | Productive bounded ticket | In progress |
| P118.4 | Selective Advisor and recovery behavior | Planned |
| P118.5 | Deployment decision | Planned |

### Key Design Principles

- **Single model, serial inference**: One Qwen 3.6 27B model on a single GPU. Zero marginal token price is not a claim of zero GPU, hosting, or opportunity cost.
- **Role separation by authority**: Coordinator, Supervisor, Worker, and Advisor are instruction-bound roles sharing the same model.
- **One bounded repair**: If verification fails, issue exactly one concrete repair follow-up. If that fails, escalate — do not retry indefinitely.
- **Quality, protocol, economics reported separately**: Never collapse these into one vague verdict.

## Upcoming Phases

No phases beyond P118 are currently planned in the roadmap. P118.5 (deployment decision) will determine whether the single-model Agent Hub profile becomes the default or requires a named paid-model fallback for specific task classes. Future phases will be added to `ROADMAP.md` as decisions are made.
