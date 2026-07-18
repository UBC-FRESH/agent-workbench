# P114 MWE Build Plan

Status: active.

## Keep

- The P114 capability contract remains the definition of the finished route.
- The P114.2 adapter tests remain the offline conformance suite.
- The P113 one-patch adapter, isolated `CODEX_HOME`, remote `/v1` provider,
  direct `codex exec`, and sandbox bypass are the verified runtime core.
- `p114_p113_mwe_r4` is the last-known-good runtime baseline. It proves one
  native `apply_patch` changes only `p114_host_proof.txt` from `before` to
  `after`, then returns `P114_MWE_DONE`.
- R2 and R3 remain immutable evidence for the earlier target and marker
  increments.
- The observed C2 Luna Worker capability inventory in
  `planning/p114_c2_worker_capability_inventory.md` is the parity source of
  truth. Do not implement merely available skills or tools without C2 call
  evidence.

## Replace

- Do not use the scripted provider plus generic VS Code worker as the runtime
  deployment gate. R1-R4 show that it can translate calls while host execution
  remains unavailable.
- Do not add `exec`, a second tool, a repair turn, or a composite task until
  the immediately preceding direct-MWE increment passes.
- Do not invoke the Windows sandbox from this runner. It is opt-in only through
  `-UseWindowsSandbox`; the default is the known working bypass.
- Retire `p114_scripted_provider.py`, `run_p114_scripted_host_proof.ps1`, and
  `enable_p114_native_bridge.ps1` as live runtime gates. Retain their results
  as offline conformance and negative-integration evidence; do not delete or
  reinterpret them as host execution.

## Build sequence

1. Reproduce the exact C2 bounded `exec` call through the native shell-command
   route: literal worktree, declared read-only command, one command completion,
   and terminal worker output.
2. Generalize that C2 proof to a fail-closed ticket-declared command policy.
3. Reintroduce the already-proven native patch after the C2 shell proof. Require
   one read, one native patch, stable call/output history, exact `before` to
   `after`, and no validation or repair. A shell-write substitute is invalid.
4. Add one focused declared validation after the combined read/patch proof. Capture its exit code and
   output while retaining the preceding call/output history. Do not add repair.
5. Add one compact repair continuation only after the preceding capabilities pass independently.
6. Add the ticket/result/heartbeat/archive artifact envelope and flat-role
   authority checks.
7. Run the composite fresh capability battery only after every preceding direct
   increment has a passing artifact.

## Iteration discipline

Change one named variable per attempt. On failure, preserve raw evidence,
record the changed variable and exact host/provider/adapter state, and use the
result to diagnose the responsible component before selecting the next change.
Treat a wrong CWD, changed provider/model/catalog, non-isolated configuration,
sandbox drift, shell-write fallback, unsupported-tool fallback, path escape,
missing native completion, or filesystem state inconsistent with tool evidence
as invalid evidence. These are diagnostic facts, not automatic caps on further
engineering work.

## Current restore point

`p114_core_adapter_acceptance_r14` is the v1 data-plane restore point. The
core adapter completed the full declared `exec -> native apply_patch -> exec`
composite in the literal worktree: two native commands, one native file change,
validation exit code zero, target `after\n`, and `P114_CORE_DONE`. The focused
adapter suite passed (`12 passed`).

## Next interim goal

The direct-MWE route has now passed its three fresh-session composite battery
with run-scoped configuration, teardown, repair continuation, and artifact
envelope evidence. This completes the locked v1 data-plane adapter delivery
gate. Binding the route to the frozen C4 Worker role requires separate
host-plane provider/configuration or native-delegation work, which is outside
this v1 boundary. The direct-MWE result cannot by itself complete P114.3,
qualify C4, resume P107, or make an economics claim.

## Locked v1 boundary

P114 v1 is a fail-closed remote Worker data-plane adapter. Its delivery gate is
ticket-declared `exec`, literal containment, command-result continuation,
native `apply_patch`, declared validation, and one fresh composite acceptance
test. Native delegation tools stay in the Coordinator/Supervisor host plane.
Skills remain Codex session context and are deferred until a frozen Worker task
actually invokes one. Browser, GitHub, image, file, MCP, provider, and
configuration tools are outside v1.
