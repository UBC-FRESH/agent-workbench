# qwen3-coder-next Capability Profile

## Model Identity

- Model tag: `qwen3-coder-next:latest`
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
  - Copilot SDK no-tool marker probe.
  - Copilot SDK repeated no-tool marker evaluation.
  - Copilot SDK structured Markdown output trial.
  - Copilot SDK patch-proposal trial.
- Harness or bridge path: Copilot SDK/Ollama harness for reliable model
  selection; VS Code Chat custom-agent frontmatter is not accepted as
  model-selection evidence.
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
- Produced complete bounded patch proposals in the P10 trial, including the
  required `## Rationale`, `## Patch`, and `## Verification` sections.

## Observed Failure Modes

- P4 and P5 showed that VS Code Chat/custom-agent model selection could resolve
  to `qwen3-coder:latest` even when `qwen3-coder-next:latest` was requested.
  Those runs are blocked for qwen3-coder-next model-comparison claims.
- No broad failure mode is established from the small SDK samples. This profile
  should not be read as a general reliability claim.

## Loop And Stop-Condition Risk

- Loop risk: not established in the SDK evidence; treat as unknown-to-medium
  until richer repeated runs are available.
- Stop-compliance notes: P7/P8 marker and P9/P10 structured outputs were stable
  in the small SDK samples.
- Recommended retry limit: one retry for structured-output failures, then
  compare with another installed model or split the ticket.

## Ticket-Shape Sensitivity

- Good fit: no-tool marker probes, structured Markdown responses, and bounded
  patch-proposal tickets where the worker proposes but does not apply changes.
- Weak fit: broad architecture recommendations unless the supervisor provides
  explicit source files and acceptance criteria.
- Avoid: tracked-file mutation, GitHub mutation, release closeout, parent phase
  closeout, or tickets that require hidden private context.

## Delegation Guidance

- Recommended default authority ceiling: L1 proposal-only.
- Suitable task types:
  - patch proposal;
  - documentation proposal;
  - test-design proposal;
  - evidence intake; and
  - compatibility review.
- Requires repeat run: yes for tasks that will materially affect supervisor
  implementation decisions.
- Requires independent claim review: yes.
- Suggested supervisor verification:
  - require all ticket sections;
  - inspect proposed patches without applying them automatically;
  - validate claims against source files; and
  - synthesize accepted/rejected claims before promotion.

## Decision-Engine Inputs

- Default recommendation bias: `delegate` for high-suitability L1 proposal
  tasks, `split` for broad planning tasks, and `do-directly` for mutation or
  closeout work.
- Confidence: medium for marker, structured-output, and bounded patch-proposal
  tasks observed through the SDK harness.
- Primary economics benefit: may generate more complete first-pass proposals
  than the older qwen profile on bounded patch-proposal tasks.
- Primary cleanup risk: overgeneralizing from small samples or accidentally
  trusting VS Code custom-agent model-selection claims.

## Open Questions

- Does the model stay stable on larger real-project proposal packs?
- Does it preserve evidence fidelity when asked to summarize multiple project
  sources?
- How does it compare with non-qwen `gpt-oss:*` variants on the same ticket
  families?

## Public-Safety Review

- No private endpoint, header, token, or credential values.
- No personal absolute paths.
- No raw transcript excerpts.
- No broad claims beyond observed Agent Workbench evidence.
- Authority guidance stays inside the current delegation policy.
