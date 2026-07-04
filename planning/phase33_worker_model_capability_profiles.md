# Phase 33 Worker Model Capability Profiles

Phase 33 turns prior model-trial observations into reusable capability profiles
for delegation planning. The goal is not to rank local models globally. The
goal is to make supervisor model choice less vibes-based for Agent Workbench
ticket families.

## Phase Boundary

P33 is a documentation and planning phase. It does not run new model calls,
install new models, add the P34 decision engine, or delegate mutation authority
to worker models.

The phase adds:

- `templates/model_capability_card.md`;
- `model_profiles/qwen3-coder.md`;
- `model_profiles/qwen3-coder-next.md`;
- `model_profiles/gpt-oss-family-planned.md`; and
- playbook links that tell supervisors to consult capability profiles before
  assigning a worker model.

## Evidence Sources

The initial qwen profiles draw from sanitized tracked evidence already present
in the repository:

- `planning/phase4_ab_scoring_results.md`;
- `planning/phase5_custom_agent_model_switching_notes.md`;
- `planning/phase7_copilot_sdk_local_probe_env_notes.md`;
- `planning/phase8_sdk_same_ticket_eval_notes.md`;
- `planning/phase9_structured_doc_output_notes.md`; and
- `planning/phase10_patch_proposal_notes.md`.

Those notes show a useful split:

- VS Code Chat/custom-agent model selection was not reliable enough for
  qwen-family comparison claims.
- The Copilot SDK/Ollama harness gave explicit model selection and stable
  no-tool marker results in small samples.
- Both qwen profiles passed small structured-output trials.
- `qwen3-coder-next:latest` produced complete bounded patch proposals in the
  P10 sample, while `qwen3-coder:latest` omitted a required section.

These are narrow observations, not broad model rankings.

## `gpt-oss:*` Lane

The `gpt-oss:*` family should be tested soon because it may fail differently
from qwen-family workers. The first useful comparison is not "which model is
smartest." It is whether a non-qwen family changes stop compliance, evidence
discipline, loop risk, and proposal usefulness on the same tickets.

P33 records `model_profiles/gpt-oss-family-planned.md` as a planned comparison
lane. It intentionally does not claim installed-model evidence or capability
results. A later phase should verify the exact installed tag with `ollama list`
and then run the same ticket families through the SDK harness.

## How Profiles Feed P34

P34 should treat capability profiles as transparent input facts:

- model tag;
- profile status;
- evidence-supported task types;
- recommended authority ceiling;
- loop and stop-compliance risk;
- repeat-run requirement;
- confidence level; and
- default recommendation bias.

The first P34 decision engine should not infer model capability from family
name alone. If a profile is planned or partial, the decision should usually be
`defer`, `needs-human-decision`, or a very small L0/L1 probe.

## Closeout Notes

P33 keeps all raw model outputs, provider inputs, and endpoint details out of
tracked files. It uses existing sanitized planning notes as evidence and keeps
authority guidance aligned with `planning/delegation_policy.md` and
`planning/task_delegation_taxonomy.md`.
