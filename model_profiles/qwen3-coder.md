# qwen3-coder Capability Profile

## Model Identity

- Model tag: `qwen3-coder:latest`
- Model family: Qwen coder
- Provider or host class: configured Ollama worker host
- Profile status: `observed`
- Last reviewed: 2026-07-04

## Inventory Evidence

- Installed-model evidence: listed in `planning/ollama_worker_model_install_shortlist.md`.
- Inventory date or source: maintainer-provided installed-model inventory from
  the local Ollama worker host.
- Important caveat: supervisors must recheck the active `ollama list` inventory
  before assigning new work.

## Evidence Scope

- Observed ticket families:
  - VS Code Chat bridge tiny command/file probe.
  - Copilot SDK no-tool marker probe.
  - Copilot SDK repeated no-tool marker evaluation.
  - Copilot SDK structured Markdown output trial.
  - Copilot SDK patch-proposal trial.
- Harness or bridge path: VS Code Chat bridge and Copilot SDK/Ollama harness.
- Repeats observed: small samples only, usually two repeats per ticket family.
- Evidence surfaces:
  - `planning/phase4_ab_scoring_results.md`
  - `planning/phase5_custom_agent_model_switching_notes.md`
  - `planning/phase7_copilot_sdk_local_probe_env_notes.md`
  - `planning/phase8_sdk_same_ticket_eval_notes.md`
  - `planning/phase9_structured_doc_output_notes.md`
  - `planning/phase10_patch_proposal_notes.md`

## Observed Strengths

- Completed exact no-tool marker probes through the SDK harness in the P7 and
  P8 evidence.
- Produced the required structured Markdown sections in the P9 structured-output
  trial.
- Stayed inside allowed file and GitHub boundaries in the P4 tiny bridge probe.

## Observed Failure Modes

- P4 recorded a duplicate-command deviation in one VS Code Chat bridge run.
- P5 recorded visible repeated completion summaries in no-tool Copilot Chat
  custom-agent sessions.
- P10 recorded missing required `## Verification` sections in the
  patch-proposal ticket family.

## Loop And Stop-Condition Risk

- Loop risk: medium in VS Code Copilot Chat agent-mode sessions; lower in the
  SDK no-tool marker evidence observed so far.
- Stop-compliance notes: marker-only SDK runs were stable in the small P7/P8
  samples, but VS Code Chat runs showed duplicate-command and repeated-summary
  behavior.
- Recommended retry limit: one retry for proposal tasks, then split smaller or
  switch model if the same failure mode repeats.

## Ticket-Shape Sensitivity

- Good fit: no-tool marker probes, narrow structured-output tickets, and
  evidence intake with explicit source boundaries.
- Weak fit: patch proposals with multiple required sections unless the
  supervisor can tolerate retry and section repair.
- Avoid: tracked-file mutation, GitHub mutation, release closeout, parent phase
  closeout, or tickets where a repeated completion summary would create user
  confusion.

## Delegation Guidance

- Recommended default authority ceiling: L1 proposal-only.
- Suitable task types:
  - evidence intake;
  - structured documentation proposal;
  - roadmap review with explicit source files; and
  - low-risk issue triage drafts.
- Requires repeat run: yes for nontrivial proposal tasks.
- Requires independent claim review: yes.
- Suggested supervisor verification:
  - validate required sections;
  - reject unsupported completion claims;
  - compare accepted and rejected claims in the evidence summary; and
  - keep raw output ignored.

## Decision-Engine Inputs

- Default recommendation bias: `delegate` for high-suitability L1 proposal
  tasks, `split` for patch-proposal work, and `do-directly` for mutation or
  closeout work.
- Confidence: medium for marker and structured-output tasks; low for
  patch-proposal tasks.
- Primary economics benefit: may reduce supervisor reading and first-draft time
  on tightly bounded planning or documentation proposals.
- Primary cleanup risk: repeated prose, missing required sections, or plausible
  unsupported claims.

## Open Questions

- Does the repeated-summary behavior persist outside VS Code Chat when tickets
  are richer than marker probes?
- Can stricter ticket wording reduce missing-section failures in patch-proposal
  tasks?

## Public-Safety Review

- No private endpoint, header, token, or credential values.
- No personal absolute paths.
- No raw transcript excerpts.
- No broad claims beyond observed Agent Workbench evidence.
- Authority guidance stays inside the current delegation policy.
