# gpt-oss Family Planned Capability Profile

## Model Identity

- Model tag: `gpt-oss:*`
- Model family: GPT OSS
- Provider or host class: configured Ollama worker host
- Profile status: `planned`
- Last reviewed: 2026-07-04

## Inventory Evidence

- Installed-model evidence: not recorded in tracked Agent Workbench evidence for
  this profile.
- Inventory date or source: pending a fresh `ollama list` verification in the
  active worker environment.
- Important caveat: do not assign `gpt-oss:*` worker tickets until the exact
  installed model tag is verified.

## Evidence Scope

- Observed ticket families: none recorded in this profile.
- Harness or bridge path: planned for the Copilot SDK/Ollama harness.
- Repeats observed: none recorded.
- Evidence surfaces:
  - `planning/ollama_worker_model_install_shortlist.md`
  - future P33+ model capability updates
  - future P35+ real-project pilot accounting

## Planned Comparison Questions

- Does a `gpt-oss:*` variant stop more cleanly than qwen-family models on
  marker-only and no-tool structured-output tickets?
- Does it produce better or worse evidence discipline on proposal-only tickets?
- Does it invent tool or GitHub success less often than qwen-family workers?
- Does it provide enough first-draft value to offset supervisor verification
  cost on real-project planning tasks?

## Initial Delegation Guidance

- Recommended default authority ceiling: L0 no-tool or L1 proposal-only after
  install verification.
- Suitable task types before evidence exists:
  - marker probes;
  - structured-output dry runs; and
  - no-tool proposal comparisons against an already-tested qwen ticket.
- Requires repeat run: yes.
- Requires independent claim review: yes.
- Suggested supervisor verification:
  - run the same ticket against a qwen baseline;
  - render a comparison report with `agent-workbench compare eval`;
  - record accepted, rejected, and needs-evidence claims; and
  - update this profile only from sanitized evidence.

## Decision-Engine Inputs

- Default recommendation bias: `defer` until installed and tested.
- Confidence: low.
- Primary economics benefit: possible non-qwen family contrast for tasks where
  qwen workers loop, omit sections, or overfit ticket wording.
- Primary cleanup risk: unknown model-specific failure modes.

## Open Questions

- Which exact `gpt-oss:*` tags are practical on the active Ollama worker host?
- Are smaller variants good enough for high-volume proposal-assist work?
- Do larger variants reduce verification cost enough to justify latency?

## Public-Safety Review

- No private endpoint, header, token, or credential values.
- No personal absolute paths.
- No raw transcript excerpts.
- No broad claims beyond observed Agent Workbench evidence.
- Authority guidance stays inside the current delegation policy.
