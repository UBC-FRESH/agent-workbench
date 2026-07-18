# P114 R7 Core-Adapter Recovery

Status: core-adapter acceptance passed. This note preserves the recovery path
from the R7 host-continuation blocker to the accepted fresh composite.

## Retained progress

- R6 passed: one literal-worktree native read, one native `apply_patch`, exact
  `before` to `after`, and terminal completion. Its raw run is
  `p114_native_read_mwe_r6_cached_id_fix_r9`.
- The core P114 adapter now rewrites accepted provider calls in
  `response.completed.response.output` to the same native custom-tool identity
  emitted in its streamed events. Focused core-adapter and loopback tests passed
  after this repair.
- The core adapter now has request capture and staged tool policy support. Its
  initial provider request can force the declared `exec` function and later
  stages can expose patch only after completed exec history.
- Provider `exec` is now translated to the direct host's standard
  `shell_command`; provider `apply_patch` remains the native custom tool.

## Verified live facts

- The original hand-written relay can perform read then native patch, but the
  direct host does not begin a further validation tool call after that patch.
- The registered C2-style Worker has shell capability but no native patch tool.
  The writable Qwen Worker likewise did not expose `apply_patch`; its terminal
  marker without mutation was rejected as invalid evidence.
- The repaired core adapter can force the provider to emit `exec`. Before the
  standard-exec translation, the direct host rejected it as
  `unsupported custom tool call: exec`.
- The earlier hand-written relay's post-freeform-patch continuation failure was
  a relay-path limitation, not an inherent host limitation. The core adapter's
  standard-exec event lifecycle is the working path.

## Current code and artifacts

- Core translation: `src/agent_workbench/p114_capability_tool_adapter.py`.
- Loopback host and staged policy: `scripts/p114_capability_tool_adapter.py`.
- Live runner: `scripts/run_p114_native_read_trial.ps1` with `-CoreAdapter`.
- Increment evidence: `planning/p114_p113_mwe_increment_log.md` and ignored
  `runtime/agent_jobs/p114_core_adapter_*` directories.

## Accepted fresh composite: `p114_core_adapter_acceptance_r14`

The repaired core adapter ran the complete literal-worktree composite from a
fresh run directory. It recorded exactly two declared native command
executions, separated by exactly one native `apply_patch` file change:

1. read `target/p114_host_proof.txt` and report the literal worktree;
2. apply the native patch from `before` to `after`;
3. run the declared read-only validation and capture exit status zero.

The target is `after\n`, the terminal agent output is `P114_CORE_DONE`, and
the focused adapter suite passed (`12 passed`). Raw event, request, verdict,
ticket, final-marker, and target artifacts are preserved under ignored
`runtime/agent_jobs/p114_core_adapter_acceptance_r14/`.

This satisfies the locked v1 data-plane delivery gate. It does not yet satisfy
the phase-wide repeated fresh-session battery, runtime-deployment proof, or C4
qualification decision.

## Deployment-proof increment: `p114_core_adapter_deployment_proof_r15`

The same accepted core route now persists its run-scoped deployment facts in
`deployment_proof.json`. R15 independently re-ran the composite and verified
the normal Codex configuration was unchanged by matching pre/post hashes; it
also recorded the run-local `CODEX_HOME`, configured provider/model, literal
worktree, and loopback adapter teardown. R19 then proved repair continuation,
and r20/r21/r22 passed the fresh three-session direct-MWE battery with the
artifact envelope. The remaining C4 role binding is host-plane work explicitly
outside the locked v1 adapter boundary.
