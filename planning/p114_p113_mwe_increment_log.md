# P114 P113 MWE Increment Log

Status: active local engineering record.

## Restore point: `p114_p113_mwe_r2`

The exact P113 one-tool route ran from the P114 checkout with a run-local
`CODEX_HOME`, function-tools catalog, single-function P113 adapter, direct
`codex exec`, workspace write authority, and Windows-sandbox bypass.

Observed success: one completed native `file_change` changed `alpha.txt` to
`alpha done` and `beta.txt` to `beta done`; the worker returned `P113_DONE`.
Transient provider 404 retries preceded the successful accepted translation and
are retained as transport noise, not host-execution failure.

## Increment rule

Each next attempt changes one named variable only. On failure, preserve raw
evidence, record the exact change, and select the next repair from the observed
defect. Do not add a shell, second tool, synthetic provider, or
spawned-controller route before the preceding step passes.

## Passed increment: `p114_p113_mwe_r3`

Changed only the terminal marker. The native two-target patch still completed
and returned `P114_MWE_DONE`.

## Passed increment: `p114_p113_mwe_r4`

Changed only the target layout. The same one-patch MWE changed
`target/p114_host_proof.txt` from `before` to `after` and returned
`P114_MWE_DONE`.

## Current last-known-good baseline

`p114_p113_mwe_r4` is the runtime restore point. Its raw event stream records
one completed native `file_change`, the target reads `after`, and the final
agent message is `P114_MWE_DONE`.

## R5 standalone read: initial attempt

`p114_native_read_mwe_r5` changed only from the R4 patch route to the native
standard shell-read route. It did not reach the model or a tool: the provider
rejected the direct request because `qwen3-coder:latest` does not support the
submitted thinking field. Its target remained `before`; R4 remains `after`.

## Permitted R5 repair

Use a transparent loopback request normalizer that removes only `reasoning`,
matching established P113 adapter behavior. It must not translate tools, mutate
files, or alter the model, upstream provider, catalog, target, or sandbox
bypass. Rerun the identical one-command native read and use the resulting wire
evidence to select the next repair.

## R5 repair: model output was not a native tool call

`p114_native_read_mwe_r5_repair` used the permitted `reasoning`-strip proxy.
The thinking rejection disappeared, but the model returned XML-like
`<function=shell_command>` markup as an `agent_message`. Codex recorded no
`command_execution`, supplied no tool output, and received no terminal marker.
The target remained `before`; the proxy emitted no error. The required repair
was the bounded shell-markup translator, which established the R5 restore point.

## Passed increment: `p114_native_read_mwe_r5_translator_r3`

The authorized bounded translator converted only the exact approved
`shell_command` markup. Codex recorded one completed native command with exit
code zero, output `before` and the literal P114 worktree, and the model returned
`P114_READ_DONE`. The target remained `before`. This is the R5 restore point.

## Next increment: R6 read then native patch

Preserve the R5 translator, target, provider, model, catalog, isolated
configuration, and sandbox bypass. Add only the already-proven native
`apply_patch` after the read, changing `p114_host_proof.txt` from `before` to
`after`. Require one completed native command, one completed native file change,
the terminal marker, and the final target content. No validation or repair.

## R6 attempt 1: ticket-contract correction failed

Changed only the R6 ticket declaration, replacing inherited R5-only wording
with an ordered read-then-patch instruction that explicitly forbids a second
shell command and `Set-Content`. The run
`p114_native_read_mwe_r6_ticket_contract_r1` recorded exactly one completed
native read with the literal worktree and no shell-write follow-on. Its second
provider response was `apply_patch` with empty `{}` arguments, and the native
host rejected it as an incompatible payload before mutation. The target remains
`before`; no completed native file change exists. Preserve this raw run. The
next permitted repair changes only the continuation provider tool form; all
other R6 state remains fixed.

## R6 attempt 2: custom continuation tool form failed

Changed only the continuation provider tool form from a JSON function to the
native freeform/custom `apply_patch` form. The run
`p114_native_read_mwe_r6_custom_tool_r2` again completed the required first
read, but then ignored the custom-only continuation catalog and completed two
additional native reads before returning `P114_R6_DONE`. It recorded no native
file change; the target remains `before`. Preserve both raw run directories and
use the observed extra reads to diagnose the continuation translation before the
next named-variable change.

## R6 attempt 3: continuation request capture

Changed only the translator request capture. The run
`p114_native_read_mwe_r6_continuation_capture_r3` recorded one native read and
then returned `P114_R6_DONE` without a native file change. Its captured traffic
contains only the initial provider request, which advertised the full native
host tool catalog; no post-read continuation request reached the translator.
The next observation captures the raw provider response that led to that host
behavior.

## R6 attempt 4: raw provider response capture

Changed only raw provider-response capture. The run
`p114_native_read_mwe_r6_response_capture_r4` showed that the provider already
emits native `function_call` SSE events. The first shell call bypassed the
markup-only stage switch, so the relay never restricted the following requests
to `apply_patch`; the provider then emitted empty and repeated patch calls plus
another shell read. The next repair derives the patch stage from completed shell
history in the continuation request.

## R6 attempt 5: history-derived patch stage

Changed only patch-stage detection. The run
`p114_native_read_mwe_r6_history_stage_r5` completed the native read and then
sent continuations with only `apply_patch` plus completed shell history. The
provider emitted empty `{}` arguments for every patch call, and the relay
rejected them before any shell-write or patch mutation. The next repair changes
only the continuation provider tool schema to the P113-proven strict function
form.

## R6 attempt 6: strict function patch schema

Changed only the continuation patch schema. The run
`p114_native_read_mwe_r6_function_schema_r6` completed one native read and one
native `file_change`, and the target changed from `before` to `after`. Its
terminal continuation then failed because the upstream provider rejects
Codex's `custom_tool_call` history. The next repair normalizes that validated
patch history back to provider function-call history for the terminal response.

## R6 attempt 7: patch-history normalization

Changed only the outgoing patch-history normalization. The run
`p114_native_read_mwe_r6_patch_history_r7` again completed the native read and
native patch, but Codex replayed the patch history without its item `id`. The
next repair restores that id from the validated call-id cache, matching the
accepted P113 history repair.

## R6 attempt 8: cached patch id

Changed only the cached-id restoration. The run
`p114_native_read_mwe_r6_cached_id_r8` completed the native read and patch, but
the relay used Python's metaclass rather than the handler class when looking up
the cached id and crashed before terminal continuation. The next repair corrects
that cache lookup only.

## Passed increment: `p114_native_read_mwe_r6_cached_id_fix_r9`

The fresh R6 run completed exactly one native command execution, then exactly
one native `apply_patch` file change. The target changed from `before` to
`after`, the terminal agent message was `P114_R6_DONE`, and the raw session
shows the expected `shell_command` result followed by one native
`custom_tool_call` named `apply_patch`. The cached-id history repair permitted
the terminal continuation. This is the R6 restore point. Validation and repair
remain out of scope until the next increment is explicitly selected.

## R7 attempt 1: comparison validation command rejected

Changed only the declared post-patch validation command. The run
`p114_native_read_mwe_r7_declared_validation_r1` completed the required native
read and native patch, leaving the target as `after`. The provider then emitted
a single `shell_command`, but stripped the quoted literals from the declared
PowerShell comparison expression. The relay rejected that changed command; the
host retried and ended without a validation command execution. Preserve the raw
request/response logs. The next repair changes only the validation command
form.

## R7 attempt 2: simple read validation response incomplete

Changed only the declared validation command to an exact read of the patched
target. The run `p114_native_read_mwe_r7_validation_read_r2` again completed
the required read and native patch, and the provider emitted exactly that
declared validation read. The relay replaced the provider response with a
partial synthetic function-call sequence, so Codex did not execute it and
reconnected. The next repair changes only the validation response forwarding.

## R7 attempt 3: complete validation response still not executed

Changed only validation response forwarding, preserving the provider's complete
native function-call SSE response after exact-command validation. The run
`p114_native_read_mwe_r7_validation_forward_r3` again completed the required
read and native patch, and each captured provider response contained
`response.created`, `response.in_progress`, one function-call item, and
`response.completed`. Codex still recorded no second command execution and
reconnected. The current responsible boundary is therefore host handling of a
second native `shell_command` after the custom `apply_patch` history, not the
validation command text or relay response completeness. Preserve all three R7
run directories. R6 remains the accepted restore point.

## R7 attempt 4: host-issued shell schema unchanged

Changed only the validation provider tool schema, preserving the exact
host-issued `shell_command` definition instead of the relay's reduced strict
schema. The run `p114_native_read_mwe_r7_host_shell_schema_r4` again completed
the read and native patch, then received one complete exact validation function
response without a second native command execution. This rules out the reduced
validation schema as the cause.

## R7 attempt 5: C2 exec validation reaches the same host boundary

Changed only validation dispatch to the observed C2 `exec(command, workdir)`
envelope, with the literal P114 worktree and a native custom-tool input that
invokes `tools.shell_command`. The run
`p114_native_read_mwe_r7_exec_validation_r5` again completed the read and
native patch, but Codex did not materialize the subsequent native exec or
command execution before reconnecting. The failure is therefore broader than
the standard shell-function schema: this current host does not resume from the
accepted native `apply_patch` custom call into a further tool call. The R7
requirement remains unsatisfied; preserve this run and retain R6 as the
accepted restore point.

## R7 attempt 6: coherent patch response lifecycle remains insufficient for exec

Changed only the native-patch response translation. The relay now preserves
`response.created` and `response.in_progress`, converts every patch item event
to the native custom-call identity, and rewrites the completed response output
to the same custom `apply_patch` item before the existing declared C2 `exec`
validation. The run `p114_native_read_mwe_r7_patch_lifecycle_r6` completed the
read and patch but still recorded no validation tool or command execution. This
eliminates the missing patch response lifecycle as the sole cause. The remaining
high-signal comparison is the same repaired patch lifecycle with the
host-known standard `shell_command` validation route; do not alter the read,
patch, provider, or containment contract.

## R7 attempt 7: coherent lifecycle plus host-known shell still fails

Changed only the validation dispatch from C2 custom `exec` back to the exact
host-known standard `shell_command`; the coherent patch-response lifecycle from
attempt 6 remained fixed. The run
`p114_native_read_mwe_r7_lifecycle_shell_r7` completed the declared read and
native patch, then received the exact declared validation shell response but
recorded no second command execution before reconnecting. This isolates the
failure to this direct `codex exec` host's post-freeform-`apply_patch` tool
continuation, not validation representation or patch-response lifecycle. R7
remains unsatisfied and R6 remains the accepted restore point.

## Host-isolation observation: registered C2 Worker lacks native patch authority

The fresh registered `agent_workbench_ollama_worker` host-isolation ticket
`p114_c2_worker_host_isolation_r1` completed the exact declared native read in
the literal P114 worktree and observed `before`. Its exposed tool catalog did
not include `apply_patch`; the Worker reported only shell, MCP, and planning
tools and correctly refused the prohibited `Set-Content` fallback. This host
therefore cannot perform the locked v1 `read -> native patch -> validation`
composite as configured. The finding is host capability evidence, not a reason
to permit shell-write fallback or add unscoped tools to v1. Preserve the fresh
target and Worker session evidence.

## Host-isolation correction: writable Worker marker was invalid

The fresh `ollama_qwen_coder_worker` host-isolation ticket
`p114_c2_writable_worker_host_r1` returned its requested marker, but direct
supervisor verification found the shared target still contained `before`.
The resumed Worker then reported exactly two completed native shell reads, no
native `apply_patch`, and the literal P114 worktree CWD. Its `:workspace`
permission allowed workspace writes in principle but did not expose the
`apply_patch` tool in its actual catalog. Treat the marker as invalid worker
prose, not evidence of a composite. The Worker was not allowed to use a
shell-write fallback.

## Protocol repair: completed response identity is now coherent

Changed only the core P114 adapter's completed-response identity handling. A
provider `response.completed.response.output` that contains an accepted
function call is now rewritten to the same native `custom_tool_call` identity
already emitted in the streamed item events. The new deterministic regression
test covers that patch lifecycle, and the focused P114 adapter and loopback
suite passed (`10 passed`). This is the first directly testable repair to the
mixed `exec -> apply_patch -> exec` protocol contract; the next live increment
must exercise this core adapter rather than the hand-written R7 translator.

## Core-adapter composite attempt 1: provider declined the initial exec

The fresh remote run `p114_core_adapter_composite_r1` used the repaired core
P114 adapter with the literal-worktree `exec -> apply_patch -> exec` ticket.
Before any tool item was emitted, the provider returned prose saying it could
not directly execute commands. The target remains `before`; no command or
native patch completed. This is an initial provider/tool-instruction adherence
failure in the core route, distinct from the earlier post-patch continuation
failure. Preserve the adapter verdict/event logs and run directory.

## Passed increment: `p114_core_adapter_acceptance_r14`

The fresh core-adapter run repaired the provider-to-host `exec` lifecycle and
completed the locked v1 composite: one ticket-declared literal-worktree read,
one native `apply_patch`, and one declared read-only validation. The recorded
host sequence contains exactly two command executions and one native file
change; no shell-write fallback was used. The target changed from `before` to
`after`, validation returned exit code zero, and the terminal marker was
`P114_CORE_DONE`. The focused adapter suite passed (`12 passed`). Preserve the
complete ignored artifact directory
`runtime/agent_jobs/p114_core_adapter_acceptance_r14/` as the v1 data-plane
acceptance restore point.

## P114.3 deployment-proof increment: `p114_core_adapter_deployment_proof_r15`

Changed only the direct-MWE runner's post-run evidence materialization. The
fresh composite again completed two declared native commands around one native
patch, changed the target to `after`, and returned `P114_CORE_R15_DONE`.
Its ignored `deployment_proof.json` records the run-local `CODEX_HOME`,
configured Qwen model and Ollama provider, literal worktree, loopback adapter,
adapter teardown, and matching SHA-256 hashes before and after the normal Codex
configuration. This establishes the direct-MWE configuration and teardown
facts without claiming the still-missing role-bound C4 session, repair
continuation, result-artifact envelope, or phase-wide battery.

## Passed repair continuation: `p114_core_adapter_repair_r19`

The fresh direct-MWE session completed a same-session repair sequence: native
read; native patch from `before` to `needs_repair`; the declared validation
read returned the requested exit code 17 and `P114_repair_required`; native
repair patch changed the target to `after`; and the final declared validation
returned zero. The run recorded three command executions with exit codes
`0, 17, 0`, two native file changes, and `P114_CORE_REPAIR_DONE`. R16 through
R18 are retained failed/diagnostic artifacts for the PowerShell prompt-quoting
and verifier-counting seams fixed before this passing run.

## Passed artifact-envelope increment: `p114_core_adapter_envelope_r20`

The same five-call fresh composite passed again and now retains the declared
ignored direct-MWE envelope: `ticket.md`, `result.md`, `heartbeat.jsonl`,
`archive_manifest.json`, raw Codex/adapter event logs, and
`deployment_proof.json`. This is route evidence, not a claim that a
role-bound C4 Worker has yet written its own result artifact.

## Passed direct-MWE fresh battery: `r20`, `r21`, and `r22`

Three independent fresh Codex threads completed the same five-call composite
with the retained artifact envelope. The deterministic verifier
`scripts/verify_p114_direct_mwe_battery.py` accepted the three raw run
directories, reporting distinct thread IDs, command exit codes `0, 17, 0`, two
native patches, terminal markers, and final `after\n` targets for every row.
Its ignored report is `runtime/agent_jobs/p114_direct_mwe_battery_report.json`.
This closes repeatability for the direct-MWE route only; role-bound C4
deployment and qualification remain separate phase work.

## P114.3 C4 role-binding probe: launcher registration boundary

The reversible real-upstream bridge in
`scripts/enable_p114_c4_role_bridge.ps1` prepared a literal-worktree target,
run-local adapter, and temporary role/provider binding for the frozen
`ollama_qwen_coder_worker`. The current parent session's native launcher
rejected that requested role as unavailable before creating a child, tool call,
or mutation. The bridge teardown restored the normal configuration and Worker
profile byte-for-byte and stopped its adapter. This is a fresh-parent-session
registration prerequisite, not a Worker quality or adapter result.

## P114.3 C4 role-binding probe: `p114_c4_role_binding_r3`

The fresh-parent registration prerequisite was cleared: child
`019f71ef-efa0-7990-802d-5c0609e5f5dc` was natively spawned with
`fork_context:false` as `ollama_qwen_coder_worker`, parent
`019f71ef-93ec-7071-b5bb-e6a62dba8400`, `qwen3-coder:latest`, the temporary
real-upstream provider, and the literal P114 worktree. The raw child session
recorded only `exec` in its tool schema. Its first declared read succeeded, but
the required native patch returned `unsupported custom tool call: apply_patch`.
The child then issued an extra validation read, making four calls rather than
the required three; the adapter rejected the extra read as `undeclared_exec`.
The target remained `before\n`, so no literal `exec -> apply_patch -> exec`
proof exists. `P114_C4_ROLE_DONE` is only a terminal marker, not acceptance.

The bridge was disabled with the required run id and port. The restored config
and Worker profile each exactly matched their saved SHA-256 hashes; the adapter
process was absent afterward. Classify r3 as a host/tool-registration failure,
not a Worker quality, protocol-accepted, or economics result. P114.3 remains
open.

## P114.3 C4 role-binding probe: `p114_c4_role_binding_r5`

Fresh child `019f71f7-5893-7470-953f-d1a732858c21` was natively launched with
`fork_context:false` as `ollama_qwen_coder_worker` under parent
`019f71f7-16ae-7442-a8b4-a20d72158e68`. The raw child session advertised only
`exec`: its literal-ticket read succeeded, the exact native `apply_patch`
returned `unsupported custom tool call: apply_patch`, and the declared third
read still returned `before`. It then issued a fourth `exec` using
`Set-Content` to write the target and a fifth read, contrary to the exact
three-call ticket. The target consequently became `after` without a native
patch. The adapter verdict log independently recorded two `undeclared_exec`
rejections for the extra calls, creating an evidence/containment disagreement
that cannot be accepted as a successful patch sequence.

The bridge was disabled with `p114_c4_role_binding_r5` and port `18994`.
Normal config and frozen Worker profile SHA-256 hashes match their saved
backups; the adapter PID was subsequently absent. Classify r5 as a host tool
registration and containment failure, not a Worker-quality,
protocol-accepted, C4-qualification, or economics result. P114.3 remains open.

## P114.3 deterministic bridge repair and `p114_c4_role_binding_r6`

The bridge repair retains both `apply_patch` and `exec` schemas while forcing a
particular next tool choice. Its stream translator now buffers native tool
events until declared-call validation succeeds; an undeclared shell command
therefore emits only `undeclared_exec` and no executable host event. The
focused adapter suite passed 13 tests, compilation passed, and the scoped diff
check passed.

The single r6 child `019f71fc-aad1-7450-80bc-2b44c191a24a` did not exercise
that repaired route. Although its persisted metadata names the frozen role and
temporary provider, it failed before any adapter request with
`stream disconnected before completion: error sending request for url
(http://127.0.0.1:18994/v1/responses)`. R6's bridge was live at port `18995`;
the named r5 endpoint was already stopped. This is a parent-session provider
cache failure, not a Worker, adapter, tool-registration, quality, protocol, or
economics result. The r6 bridge was disabled and its normal config/profile
hashes were restored. A new parent session is now required before one further
role-bound proof can be meaningful.

The bridge subsequently made its temporary provider name run-scoped from the
run ID, so a fresh parent will not resolve a later proof through an earlier
run's cached provider name. The focused adapter suite passed 14 tests after
this change. R7 still requires a new parent session opened after the bridge is
enabled; no additional child was launched from the stale r5 parent.

## P114.3 `p114_c4_role_binding_r7` launcher setup ordering

R7 used a genuinely new parent session, but it enabled the run-scoped bridge
from inside that parent. The parent had already loaded its normal configuration,
so the new provider/profile binding was unavailable to the native launcher and
the sole `ollama_qwen_coder_worker` spawn was rejected before any child,
adapter request, or mutation. The target stayed `before` and teardown restored
operator state. This is an invalid setup-order observation, not a Worker or C4
capability result. The corrected handoff enables a new bridge from PowerShell
before starting the parent session.

## P114.3 `p114_c4_role_binding_r8` host tool-registration observation

Fresh child `019f720c-829e-78a2-a5f9-4f31accdae33` was launched from a parent
opened after the r8 bridge was enabled. The persisted session identity names
the frozen `ollama_qwen_coder_worker`, `qwen3-coder:latest`, the run-scoped r8
provider, and the literal worktree. Its first declared read reached the
adapter and was emitted to the host as `shell_command`; the exact required
native patch then returned `unsupported custom tool call: apply_patch`.

The r8 target stayed `before`. The raw adapter verdict log recorded rejected
`undeclared_exec` calls after that unsupported patch, and the child stream
ended before `response.completed`. R8 therefore confirms the remaining host
tool-registration blocker rather than producing a literal three-call proof.
The required disable command restored the normal operator configuration and
stopped the r8 adapter. P114.3 remains open; no quality, protocol, C4
qualification, or economics claim is available from this observation.

## P114.3 `p114_c4_role_binding_r9` falsifies the profile-permission theory

Fresh child `019f721c-db8c-79c3-a94d-d41f3ee2eb95` used the r9 provider and
made the literal three requested calls. Its native patch still returned
`unsupported custom tool call: apply_patch`; the target remained `before` and
the temporary bridge was restored. This rules out the temporary Worker-profile
permission change as a repair because Codex subagents inherit the parent
permission mode. The next deterministic repair probe compares the installed
direct runner and the multi-agent code-mode host for patch-dispatch vocabulary;
it is not another Worker run.

## P114.3 CLI-parent controls: `r10` and `r11`

The CLI parent did use native `spawn_agent` and one `wait`, so it is a real
host-surface control rather than a substitute transport. R10 lost nested quote
characters through Windows command argument serialization; R11 repaired that by
passing the parent directive over stdin and persisted the literal ticket in the
spawn event. Neither child reached the first declared `exec`: each made six
identical initial provider requests, received no adapter SSE event, and ended
with `stream disconnected before completion`. Both targets remained `before`
and teardown restored normal configuration/profile state. The CLI-parent route
therefore is not an immediate repair for the role-bound patch handler.

## P114.3 run-scoped Worker patch-handler registration repair

The accepted direct `codex exec` composites and R8 both use the Qwen
function-tool catalog that declares `shell_command` and freeform `apply_patch`.
R9 disproved the permission theory: subagents inherit their parent's permission
mode, so the bridge keeps the frozen Worker profile unchanged except for its
run-scoped provider binding.

## P114.3 accepted CLI-parent role proof: `p114_c4_cli_parent_r15`

The R10/R11 CLI controls had omitted the documented Cloudflare Access
service-token environment. R13/R14 showed the resulting `302` Access-login
responses rather than a provider SSE stream. The repair in
`run_p114_c4_cli_parent_control.ps1` loads the local provider-header file into
the three environment variables declared by the configured provider, starts the
single native child, then restores those values and the bridge in `finally`.

Fresh run `p114_c4_cli_parent_r15` used the frozen role, run-scoped provider,
literal worktree, `fork_context:false`, and exactly one native `wait`. Raw
child `019f7252-32fc-70d2-b804-9d614386fe45` made two host
`shell_command` calls around one native `custom_tool_call apply_patch`; the
patch text exactly matches its ticket, the target changed from `before` to
`after`, and the terminal message is `P114_C4_ROLE_DONE`. The adapter records
four `200 text/event-stream` exchanges and no rejected or undeclared call.
This accepts P114.3 for the CLI-parent route only; it is not a claim that the
older VS Code-parent host from R8/R9 now registers `apply_patch`.

## P114.3 VS Code patch-via-exec observation: `p114_c4_role_binding_r10_exec_wrapper`

One fresh native `ollama_qwen_coder_worker` child
(`019f727d-2d41-7d52-8ede-9cf71752234b`) launched from the intended VS Code
parent with `fork_context:false` and the literal r10 ticket. The raw child
session records the required read, a custom `exec` whose JavaScript invokes
`tools.apply_patch(...)`, and the final read. The VS Code host returned
`unsupported custom tool call: exec` for the wrapper itself, so no patch ran;
the target stayed `before` and no `P114_C4_ROLE_DONE` marker was produced.

The adapter later recorded rejected `undeclared_exec` activity, so the full
provider trace is not the accepted exact three-call sequence. The r10 bridge
was disabled with the required command after inspection. This isolates the
remaining VS Code custom-exec dispatch seam; it is neither a Worker-quality or
protocol acceptance nor an economics result.

## P114.3 no-mutation Worker host-tool inventory gate

The next VS Code-parent launch is not another patch proof. The bridge now has
`-HostToolInventory`, which forces one declared provider `exec` and translates
it to custom `exec` JavaScript that prints executor-local `ALL_TOOLS` names.
The translator does not call `shell_command`, read a repository path, or invoke
`tools.apply_patch` in this mode. A later patch ticket is permitted only after
a fresh-parent preflight records both `shell_command` and `apply_patch` plus
`P114_C4_HOST_TOOL_INVENTORY_DONE`; otherwise teardown follows immediately.

## P114.3 invalid host-tool inventory handoff: `p114_c4_role_binding_r11_host_inventory`

The fresh child preserved the intended role identity and parent boundary, but
the Coordinator passed the generated ticket's path as its message instead of
the ticket's verbatim contents. The child consequently received only that path,
not the one-call inventory instruction. Its disconnected stream and repeated
adapter `undeclared_exec` verdicts are invalid-input artifacts, not a host-tool
inventory result. The bridge was torn down; r11 supplies no quality, protocol,
C4-qualification, or economics evidence. A new run must use the ticket text.

## P114.3 valid negative VS Code inventory result: `p114_c4_role_binding_r12_host_inventory`

R12 passed the ticket contents verbatim. Its one allowed custom `exec` carried
only the inert `ALL_TOOLS` inventory expression, and the VS Code host returned
`unsupported custom tool call: exec`. No shell, file, or patch operation
occurred; the target remained `before` and the bridge was restored. R12 proves
the intended UI host lacks the generic custom executor and is negative
host-dispatch evidence only.

## P114.3 VS Code registration diagnosis

A fresh VS Code app-server observation recorded `dynamicTools: null` for both
the user thread and the extension's ephemeral fetch-helper thread. The public
app-server contract does support experimental dynamic tool registration and
client-executed `dynamicToolCall`s, so this proves only that the installed VS
Code extension did not use that mechanism for these threads. A deterministic
installed-executable comparison returned `host_registration_gap`: direct
`codex.exe` contained the three native patch/custom dispatch markers (`14`,
`39`, and `1` matches), whereas sibling `codex-code-mode-host.exe` contained
zero of each. This corroborates the observed R8--R12 rejections without
claiming a complete host-tool inventory or a responsible component. The
productive C4 path remains the accepted CLI-parent route; a separate VS Code
integration repair must supply dynamic tool definitions and handle resulting
client-executed calls before another UI Worker can add decision signal.

## P114.3 parent dynamic-tool registration proof

The reversible VS Code relay successfully injected a no-mutation `p114_exec`
dynamic tool into fresh parent `thread/start` requests. A parent call with
`{"operation":"inventory"}` produced the expected `item/tool/call` and a
successful client response carrying `P114_DYNAMIC_EXEC_HANDLER_REACHED`.
This proves the app-server dynamic-tool mechanism, but not Worker inheritance
or shell authority. No Worker was launched and the temporary setting was
removed after the observation.

## P114.3 dynamic `p114_exec` child-dispatch result

R13 was the one fresh no-mutation inheritance test after the parent
dynamic-tool proof. The Worker emitted the translated `p114_exec` function
call, but its nested host returned `unsupported call: p114_exec`; no parent
`item/tool/call` followed. The target remained `before`, no shell, patch, file,
or extra host call occurred, and the bridge was restored. Therefore dynamic
tool registration is available to the VS Code parent but is not routed through
the current `multi_agent_v1` Worker host. Do not retry another Worker until a
separate nested-host dynamic-call routing repair is available.

## P114.3 supported MCP parent routing result

The local stdio `p114_exec` MCP probe was loaded by a fresh VS Code parent and
received one exact no-mutation inventory call, returning
`P114_MCP_EXEC_HANDLER_REACHED`. The MCP configuration then restored exactly.
This establishes the supported parent MCP path, not child routing. The next
bounded repair is adapter catalog preservation for MCP-provided tools; the
current C4 adapter intentionally replaces that catalog with its two legacy
function definitions.

## P114.3 Worker MCP schema-discovery result

R14's raw child request contained the bridge's provider-facing `apply_patch`
and `exec` definitions, with neither `additional_tools` nor a direct
`p114_exec` MCP schema. The local MCP server received zero child calls and no
host operation occurred. This does not establish that the registry cannot reach
a child by another exposure mechanism. MCP and bridge teardown restored
configuration and role state.

## P114.3 Worker MCP deferred-discovery result

R15 enabled Code Mode with empty namespace filters. The raw child provider
request contained a deferred `tool_search` tool that named `p114_exec_probe`
and explicitly directed MCP discovery through that tool; it still contained no
direct MCP function schema. The one Worker was given an invalid direct-call
ticket that prohibited the required `tool_search`, so it emitted markup rather
than a host call. The MCP server recorded zero `tools/call` requests and the
target remained `before`.

This replaces the R14 overclaim: configured MCP reaches the child as a
discoverable source under Code Mode. The next no-mutation ticket must permit
exactly the discovery call and one resulting inventory call. Teardown restored
both configuration and the Worker role byte-for-byte.

## P114.3 Worker deferred MCP routing result

R16 gave one fresh Worker that corrected two-call ticket. The adapter's raw
upstream stream recorded six complete `tool_search` function calls, but the
nested host did not execute `tool_search` or return its result on any turn. It
reissued the same call until the provider stream disconnected before terminal
completion. The MCP server received zero `tools/call` requests and the target
remained `before`.

This is rejected protocol evidence, not a successful MCP call. It identifies a
specific nested code-mode host defect: deferred-tool-search dispatch and turn
continuation. The next repair is that dispatch path, not MCP registration,
adapter catalog preservation, or another direct-MCP prompt. MCP-first teardown
restored configuration and Worker role byte-for-byte.

## P114.3 direct-MCP workaround result

R17 tried the bounded no-mutation workaround of disabling deferred MCP exposure
with Code Mode still enabled. Fresh Worker
`019f72ca-6aa5-7d53-b9ce-5e6de2133692` received the generated direct-MCP ticket
verbatim with `fork_context:false`, and the Coordinator waited exactly once.
The child stream disconnected before `response.completed` and its raw session
ended with no final agent message.

The raw child request still exposed MCP only through `tool_search` guidance
naming `p114_exec_probe`; it did not contain a direct `p114_exec` tool schema.
After bridge translation, the provider-facing catalog remained the legacy
`apply_patch` and `exec` pair. The provider repeatedly called `exec`, yielding
six adapter `undeclared_exec` rejections, while the MCP server recorded only
initialization/listing and zero `tools/call` requests. The target remained
`before` and `P114_C4_DIRECT_MCP_ROUTING_DONE` never appeared.

R17 is therefore rejected. It rules out the direct-MCP config workaround for
this route and leaves the repair target at nested code-mode `tool_search`
dispatch/turn continuation. MCP and bridge teardown restored the normal config
and Worker role hashes.

## P114.3 repaired MCP inventory routing result

R19 ran after the bounded MCP inventory adapter repair and a VS Code restart.
Fresh Worker `019f72db-e8e5-7a73-9a45-06fa2ec81f36` received the ticket
verbatim with `fork_context:false` and returned
`P114_C4_MCP_ROUTING_DONE`, but the run is rejected.

The repair changed the boundary as intended: provider request 1 exposed
`tool_search`; provider requests 2 and 3 exposed
`mcp__p114_exec_probe__p114_exec`. Adapter events show one `tool_search` call
and one `mcp__p114_exec_probe__p114_exec` call, and all adapter verdicts were
`accepted`. The adapter no longer blocked this lifecycle.

The nested Worker host then returned
`unsupported call: mcp__p114_exec_probe__p114_exec`. The MCP server recorded
zero `tools/call` requests and the target stayed `before`. R19 therefore
isolates the next repair to spawned-child code-mode/MCP function dispatch or
VS Code extension integration, not another P114 adapter catalog repair. Final
cleanup restored original config and Worker-role hashes and stopped adapter
PID `29000`.

## P114.3 native tool_search response-shape correction

R20 source audit used the installed Codex `0.144.5` source tag
`rust-v0.144.5` to inspect the failed R19 boundary. The relevant native path
builds `ToolPayload::ToolSearch` only from a `tool_search_call` response item
with `execution: "client"`. The R19 adapter emitted a normal `function_call`
named `tool_search`, so native Codex did not complete real deferred tool
discovery; the provider continuation showed that output as `aborted`.

The adapter was repaired to:

- translate provider `function_call: tool_search` into native
  `tool_search_call`;
- preserve native `tool_search_call` and `tool_search_output` history; and
- expose `mcp__p114_exec_probe__p114_exec` only after a real search output
  contains the probe tool.

Validation:

```text
python -m py_compile src\agent_workbench\p114_capability_tool_adapter.py scripts\p114_capability_tool_adapter.py
python -m pytest tests\test_p114_capability_tool_adapter.py -q
28 passed in 0.18s
```

Next increment: one fresh no-mutation R20 MCP inventory proof after VS Code
restart. Acceptance requires native `tool_search_call`, native
`tool_search_output`, a real MCP `tools/call`, no unsupported calls, and
terminal marker `P114_C4_MCP_ROUTING_DONE`.

## P114.3 R20 native discovery result

R20 launched one fresh Worker
`019f72e8-d351-7143-ad4f-55e0f41c3296`, waited exactly once, and rejected the
run. The child session reached native deferred discovery:

- `tool_search_call` query: `p114_exec_probe p114_exec inventory`
- `tool_search_output`: namespace `mcp__p114_exec_probe`, function `p114_exec`

The next provider request failed before the MCP tool could be called:

```text
input[3]: unknown input item type: "tool_search_call"
```

The MCP probe recorded zero `tools/call` requests and the target remained
`before`. Operator state was restored; adapter PID `12560` was stopped.

R20 identifies the next increment: add an upstream-provider-compatible
continuation-history translation for `tool_search_call`/`tool_search_output`.
The child/native side must still see real `tool_search_*` history, but the
Ollama-compatible provider must not receive unsupported input item types.

## P114.3 provider-compatible native discovery replay

Implemented the next increment identified by R20. Native child discovery is
preserved: provider `tool_search` output is still translated to
`tool_search_call` for Codex, and the child can still produce
`tool_search_output`. The adapter now converts those child-native history
records back to provider-compatible `function_call` and
`function_call_output` records before replaying the next request upstream.

The MCP inventory tool is still exposed only after the actual search output
contains the probe tool. Focused validation:

```text
python -m pytest tests\test_p114_capability_tool_adapter.py tests\test_p114_capability_tool_adapter_loopback.py -q
29 passed in 1.12s
python -m py_compile src\agent_workbench\p114_capability_tool_adapter.py scripts\p114_capability_tool_adapter.py
git diff --check
```

Next increment: stage a fresh R21 no-mutation MCP proof and restart VS Code
before launching exactly one Worker.

## P114.3 R21 provider replay live result

R21 launched exactly one fresh Worker
`019f72f0-d984-7d32-878a-910c3d654b88` and waited exactly once. The Worker
returned `P114_C4_MCP_ROUTING_DONE`, but the run is rejected because MCP did
not execute the inventory tool.

The R20 provider-replay repair worked: provider-facing history no longer
contained unsupported `tool_search_call` input items. The adapter replayed
native discovery history upstream as `function_call` and
`function_call_output`, and all adapter verdicts were `accepted`.

The remaining failure is host-side: the raw child session contains native
`tool_search_call`, native `tool_search_output` with `mcp__p114_exec_probe /
p114_exec`, then `function_call: mcp__p114_exec_probe__p114_exec`. The host
returned `unsupported call: mcp__p114_exec_probe__p114_exec`. The MCP log
recorded zero `tools/call` requests and the target remained `before`.

Next increment: repair or prove the nested Worker code-mode host path that
should route a discovered MCP function call to the MCP server.

## P114.3 namespaced MCP-call adapter repair

The R21 source audit refined the next increment. The normal Codex search-tool
path dispatches search-surfaced MCP calls when the response item is namespaced:
namespace `mcp__<server>`, name `<tool>`. R21 forwarded a flat provider-side
compatibility name, `mcp__p114_exec_probe__p114_exec`, into the child. That
plain tool name could not match the registered MCP handler.

The adapter now translates provider-flat MCP inventory calls into native
child-facing namespaced calls, while preserving provider-flat replay on
continuation. Focused validation:

```text
python -m pytest tests\test_p114_capability_tool_adapter.py tests\test_p114_capability_tool_adapter_loopback.py -q
30 passed in 1.32s
python -m py_compile src\agent_workbench\p114_capability_tool_adapter.py scripts\p114_capability_tool_adapter.py
git diff --check
```

Next increment: R22 no-mutation live proof after bridge/MCP staging and VS Code
reload.

## P114.3 R22 no-mutation MCP routing accepted

R22 launched exactly one fresh Worker
`019f72f7-9bc7-76f1-94de-9c16013ccede` and waited exactly once. The proof is
accepted for no-mutation MCP routing:

- child-native `tool_search_call`;
- child-native `tool_search_output` with `mcp__p114_exec_probe / p114_exec`;
- namespaced child `function_call` to `mcp__p114_exec_probe / p114_exec`;
- exactly one MCP `tools/call` with `{"operation":"inventory"}`;
- handler marker `P114_MCP_EXEC_HANDLER_REACHED` returned to the child;
- terminal marker `P114_C4_MCP_ROUTING_DONE`;
- target remained `before`;
- all adapter verdicts accepted.

Operator state was restored after inspection. This closes the no-mutation MCP
routing increment and sets up a later, separate mutation-capability proof.

## P114.3 R23 bounded MCP patch accepted

R23 launched exactly one fresh Worker
`019f730c-a338-7b52-904e-0fbdf9a8fb45` and waited exactly once. The proof is
accepted for bounded MCP mutation:

- child-native `tool_search_call` query
  `p114_exec_probe p114_exec patch`;
- child-native `tool_search_output` with `mcp__p114_exec_probe / p114_exec`;
- namespaced child `function_call` to
  `mcp__p114_exec_probe / p114_exec` with `{"operation":"patch"}`;
- exactly one MCP `tools/call` with `{"operation":"patch"}`;
- handler marker `P114_MCP_PATCH_HANDLER_REACHED` returned to the child;
- terminal marker `P114_C4_MCP_PATCH_DONE`;
- target changed from exact `before\n` to exact `after\n`;
- no shell, `exec`, `apply_patch`, custom-tool, file-read, or extra host call
  occurred in the raw child session;
- all adapter verdicts accepted.

Operator state was restored after inspection. This proves the R22 MCP routing
breakthrough extends to a tightly bounded mutation handler.
