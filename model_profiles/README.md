# Worker Model Capability Profiles

This directory contains public-safe capability profiles for worker models used
with Agent Workbench. Profiles summarize observed behavior from bounded tickets,
not general model quality.

Use these profiles when selecting a worker model for proposal-assist tasks.
Before assigning a model, the supervisor should check:

- whether the model is installed in the active Ollama inventory;
- whether the profile has evidence for the relevant task type;
- whether the recommended authority ceiling fits the intended ticket;
- whether repeated runs are recommended; and
- whether the profile records known loop, stop-compliance, or evidence-fidelity
  risks.

Profile claims must stay tied to observed Agent Workbench evidence. If a model
is installed but has not been tested on a task family, record that gap instead
of treating the model as equivalent to another member of its family.

Current profiles:

- `qwen3-coder.md`
- `qwen3-coder-next.md`
- `gpt-oss-family-planned.md`

Template:

- `templates/model_capability_card.md`
