# P118 FRESH vLLM Agent

## Goal

Establish a usable native VS Code Copilot Agent Hub deployment in which one
configured remote vLLM coding model serves the Coordinator, Worker, and
selective Advisor roles through distinct custom-agent instructions. The point
is productive development work with one locally controlled model service, not
a model sweep or a ritualized benchmark.

## Starting premise

The configured remote vLLM provider serves one custom Qwen 3.6 27B coding
model. Role separation comes from bounded authority, instructions, tool
permissions, and session topology—not from pretending the underlying model is
deterministic or that role labels create different models.

**GPU Constraint (2026-07-21):** The single configured model is consuming
near-maximum GPU VRAM on the host (by design). No additional models should be
loaded or attempted on that GPU. P118 is strictly a single-model deployment:
every role—Coordinator, Supervisor, Worker, and Advisor—uses the one installed
model. Serial inference is not a preference; it is a hardware requirement.
Do not schedule parallel reasoning children, and do not attempt to load
alternate models until the host capacity changes.

P118 keeps intense inference serial: at most one implementation or review child
may be actively reasoning at a time. A Coordinator may wait, inspect a
completed result, or send one concise follow-up; it must not start parallel
intense children against the single-model service.

## Scope

1. Define machine-local provider binding and three custom Copilot agents:
   Coordinator, Worker, and selective read-only Advisor, all pinned to the same
   provider/model alias and medium reasoning by default.
2. Define the serial operating contract: one active implementation child,
   explicit completion/handoff, no speculative duplicate agents, and no hidden
   paid fallback. Luna or another Copilot model is an explicit operator choice,
   not an automatic recovery path.
3. Exercise the profiles on ordinary bounded development tickets in the native
   Agent Hub. The Coordinator must delegate, inspect delivery, validate, and
   either accept or issue one fact-specific follow-up rather than recreate the
   Worker task itself.
4. Retain P116 as an optional Coordinator-owned observation/cue mechanism. It
   is used only when a live bounded Worker needs a concrete nudge; a productive
   Worker does not require a ceremonial Supervisor turn.
5. Record each run's quality, protocol, and economics separately. Economics
   includes paid Copilot spans when used and provider-side/local inference usage
   where available. Zero marginal token price is not a claim of zero GPU,
   hosting, or opportunity cost.

## Out of scope

- Parallel high-intensity multi-agent fan-out against the single provider.
- A new SDK/app-server control substitute, autonomous daemon, or P107 retest.
- Treating a failed model response as a reason to narrow the task until it
  passes.
- Publishing provider URLs, credentials, private session logs, or server
  details in tracked files.

## Tasks

### P118.1 Provider and role-profile contract

- Verify the configured vLLM endpoint/model identity locally without tracking
  credentials.
- Add role configs with distinct authority and concise role directives, while
  retaining one model alias and medium reasoning.
- Validate that the native session records the selected role/model binding.

### P118.2 Serial single-model operating contract

- Encode one-active-intense-child limits in the Coordinator and Worker
  directives.
- Define Worker delivery, Coordinator verification, and one bounded repair
  handoff; define Advisor use only for a concrete ambiguity.
- Add a concise operator launch/checklist that works in the VS Code UI.

### P118.3 Productive bounded ticket

- Select one ordinary repository task with objective acceptance and an allowed
  implementation surface.
- Run Coordinator-to-Worker delivery under the serial contract.
- Independently inspect the diff and validation result; preserve failed or
  incomplete output without external implementation substitution.

### P118.4 Selective Advisor and recovery behavior

- Exercise a real ambiguity or failed validation only if one naturally occurs;
  do not manufacture it.
- Confirm that an Advisor response remains advisory and that the Coordinator
  owns the follow-up decision.
- Confirm P116 cue delivery only when live evidence makes it useful.

### P118.5 Deployment decision

- Summarize usable/blocked behavior for direct work, one delegated task, and
  any selective review.
- Report quality, protocol, and economics separately, including whether the
  single-model configuration avoids paid model spans for that run.
- Decide whether this becomes the default native Agent Hub profile or requires
  a named paid-model fallback for specific task classes.

## Acceptance

- Native custom-agent selection binds all participating roles to the declared
  vLLM model alias and records enough identity evidence to audit that claim.
- No more than one intensive child runs at once.
- At least one bounded ticket is delivered, independently validated, and
  classified honestly.
- Any recovery is a bounded response to observed evidence, not a substitute
  implementation by the Coordinator.
- Quality, protocol, and economics are reported independently.
