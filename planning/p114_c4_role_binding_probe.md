# P114 C4 Role-Binding Probe

Status: the CLI-parent control in `p114_c4_cli_parent_r15` is accepted, but
the intended VS Code-parent route remains open. R8/R9 rejected the adapter's
top-level synthetic patch event; the new patch-via-exec repair awaits a fresh
UI-parent proof.

Correction: a fresh Luna UI-child control shows that the supported VS Code
mutation shape is a native `exec` custom-tool call whose JavaScript invokes
`tools.apply_patch(...)`. The Qwen adapter's direct synthetic top-level
`apply_patch` shape was therefore the wrong UI event contract. The
`--patch-via-exec` bridge repair now preserves provider-side patch validation
and identity while emitting the Luna-shaped host call. P114.3 remains open
until a fresh VS Code parent accepts that repair.

## Fresh VS Code patch-via-exec proof

From PowerShell in the literal worktree, before opening the parent session:

```powershell
.\scripts\enable_p114_c4_role_bridge.ps1 -Mode Enable -RunId p114_c4_role_binding_r10_exec_wrapper -AdapterPort 19008 -PatchViaExec
```

Open a new top-level Codex/VS Code parent in this worktree. Use native
`multi_agent_v1` to launch exactly one `ollama_qwen_coder_worker` with
`fork_context:false`, no override, and
`runtime/agent_jobs/p114_c4_role_binding_r10_exec_wrapper/ticket.md` verbatim.
Wait once, do not send follow-up input, and then audit the raw child session.

Accept only: declared provider sequence `exec -> apply_patch -> exec`; host
sequence `shell_command -> custom exec calling tools.apply_patch ->
shell_command`; exact patch; no shell write or extra host call; target
`after`; and `P114_C4_ROLE_DONE`. Always restore:

```powershell
.\scripts\enable_p114_c4_role_bridge.ps1 -Mode Disable -RunId p114_c4_role_binding_r10_exec_wrapper -AdapterPort 19008
```

## Goal

Bind a fresh `ollama_qwen_coder_worker` session to the accepted P114 core
adapter and verify the declared native `exec -> apply_patch -> exec` route.

## Preserved attempts

- `p114_c4_role_binding_r1`: the reversible bridge created its target and
  backups, but its PowerShell here-string emitted literal variable names in the
  ticket. No Worker was launched. The bridge was restored before correction.
- `p114_c4_role_binding_r2`: the corrected bridge started the real-upstream
  core adapter, rewired only the frozen Worker role through the loopback
  provider, and rendered the literal-worktree ticket. The current parent
  session's native launcher then rejected the requested
  `ollama_qwen_coder_worker` with `agent type is currently not available`.
  This occurred before any child session, tool call, or target mutation.
- `p114_c4_role_binding_r3`: a fresh parent did register and launch the frozen
  role. Child `019f71ef-efa0-7990-802d-5c0609e5f5dc`, parent
  `019f71ef-93ec-7071-b5bb-e6a62dba8400`, persisted
  `agent_role: ollama_qwen_coder_worker`, model
  `qwen3-coder:latest`, the temporary real-upstream provider, and the literal
  worktree. Its first declared `exec` succeeded. The child session's advertised
  tool list contained only `exec`, so its required native `apply_patch` returned
  `unsupported custom tool call: apply_patch`. It then made a fourth `exec`,
  which the adapter rejected as `undeclared_exec`; validation still read
  `before`. This is a host/tool-registration failure, not a Worker quality
  result. The bridge was disabled afterward: normal config and Worker-profile
  SHA-256 hashes matched their backups and the adapter process was stopped.
- `p114_c4_role_binding_r5`: fresh child
  `019f71f7-5893-7470-953f-d1a732858c21`, parent
  `019f71f7-16ae-7442-a8b4-a20d72158e68`, was launched with
  `fork_context:false` as the frozen `ollama_qwen_coder_worker`. Its raw child
  session advertised only `exec`. The first declared literal-worktree read
  succeeded; the exact native `apply_patch` returned
  `unsupported custom tool call: apply_patch`; and the declared third read
  still returned `before`. The child then made a prohibited fourth `exec` with
  `Set-Content` to mutate the target and a prohibited fifth validation read.
  The target became `after`, but the adapter verdict log separately contains
  two `undeclared_exec` rejections for those extra calls. This disagreement is
  recorded as a containment/evidence failure, not an accepted patch or Worker
  quality result. The required disable command restored config and role-profile
  SHA-256 hashes to their backups and the adapter PID was absent on independent
  inspection.
- `p114_c4_role_binding_r6`: after the deterministic repair, fresh child
  `019f71fc-aad1-7450-80bc-2b44c191a24a` again persisted the frozen role and
  provider identity, but failed before a request reached r6's adapter on port
  `18995`. Its terminal error instead named the stopped r5 endpoint
  `http://127.0.0.1:18994/v1/responses`. This proves the existing parent
  session cached the prior provider endpoint. No native call, adapter request,
  target mutation, quality result, or tool-registration result exists for r6.
  The bridge was disabled and normal configuration/profile hashes were restored.
- `p114_c4_role_binding_r7`: a new parent session enabled the run-scoped bridge
  only after it had already started. The parent therefore had not loaded the
  newly named provider or modified Worker profile at startup, and its one
  native launcher attempt rejected `ollama_qwen_coder_worker` as unavailable
  before creating a child, adapter request, or target mutation. This is an
  invalid bridge-enable ordering, not a Worker, model, tool, quality, protocol,
  or economics result. The bridge was disabled and the target remained
  `before`.
- `p114_c4_role_binding_r8`: a genuinely fresh parent launched child
  `019f720c-829e-78a2-a5f9-4f31accdae33` with `fork_context:false`; its raw
  session persisted the frozen role, `qwen3-coder:latest`, the r8 run-scoped
  provider, and the literal worktree. The adapter translated the declared
  first `exec` to host `shell_command`, but the exact native `apply_patch`
  returned `unsupported custom tool call: apply_patch`. The target remained
  `before`; subsequent attempted `exec` calls were rejected as
  `undeclared_exec`, and the stream disconnected before completion. This is a
  host tool-registration failure, not a Worker-quality, protocol-accepted,
  C4-qualification, or economics result. The r8 bridge was disabled after
  inspection.
- `p114_c4_role_binding_r9`: fresh child
  `019f721c-db8c-79c3-a94d-d41f3ee2eb95` ran with the r9 provider and made the
  literal `exec -> apply_patch -> exec` calls. Native `apply_patch` still
  returned `unsupported custom tool call: apply_patch`, the target remained
  `before`, and teardown restored both configuration files and stopped the
  adapter. This rules out the temporary role `default_permissions` change as a
  repair. The coordinator's post-run audit crashed while printing a Windows
  encoding-incompatible character, so this preserved record is the R9 closeout.
- `p114_c4_cli_parent_r10`: the new CLI parent natively spawned exactly one
  frozen Worker and waited once, proving the CLI-parent control surface. The
  Windows command argument path stripped quotes from the nested child ticket;
  the child then made six identical initial provider requests, received no SSE
  event, and terminated with `stream disconnected before completion`. The
  target remained `before` and teardown restored operator state. This is an
  invalid CLI-wrapper transport observation, not a patch registration result.
- `p114_c4_cli_parent_r11`: the wrapper repaired the nested-ticket transport by
  supplying the parent ticket on stdin; the persisted spawn prompt preserved
  the literal quoted commands and exact patch. The child nevertheless made six
  identical initial provider requests without an adapter event, then terminated
  with `stream disconnected before completion`. No native call or target change
  occurred. This rules out the CLI-parent control as an immediate host-route
  repair and identifies an initial-response transport seam for any future CLI
  work; the bridge restored normal configuration and stopped the adapter.

## Deterministic repair

The bridge now preserves both C4 tool schemas while forcing the next requested
tool, rather than narrowing the advertised tool list to the forced tool. It
also buffers tool events until exact declared-call validation succeeds, so an
undeclared `exec` cannot emit a host shell event before rejection. The focused
adapter suite passed 14 tests after the repair. Its temporary provider name is
also derived from the run ID, preventing a future new parent session from
reusing an earlier proof's provider binding.

R7 also corrected the required operator ordering: enable the run-scoped bridge
from PowerShell before opening the new parent, not from inside that parent.

The r2 teardown was independently verified: the adapter process is stopped,
the target remains `before\n`, and both the normal Codex configuration and the
Worker role file exactly match their pre-run SHA-256 hashes.

## Host-registration probe and next repair

The direct `codex exec` evidence and R8/R9 use the same Qwen function-tool
catalog. Codex's current manual also specifies that subagents inherit the
parent's selected permission mode, so R9 does not support treating a custom
agent profile permission override as the registration fix. The local executable
probe instead compares the direct runner with `codex-code-mode-host.exe` for
the native patch dispatch vocabulary. It reports `host_registration_gap` only
when the direct runner contains all patch/custom-tool markers and the code-mode
host lacks them. This is a deterministic local diagnosis, not a C4 pass.

## Accepted CLI-parent control: `p114_c4_cli_parent_r15`

R12 proved that stripping `include` was not the CLI transport repair. R13/R14
then recorded the upstream fact that every CLI-child request received a
Cloudflare Access `302` rather than SSE. The provider configuration already
declared `AW_CF_CLIENT_ID`, `AW_CF_CLIENT_SECRET`, and
`AW_PROVIDER_USER_AGENT`; the CLI wrapper had simply not loaded their values
from the documented local provider-header file.

R15 set those values only for the CLI-control process, spawned exactly one
`ollama_qwen_coder_worker` with `fork_context:false`, and waited once. Its raw
child session `019f7252-32fc-70d2-b804-9d614386fe45` records the literal
`shell_command -> custom_tool_call apply_patch -> shell_command` sequence,
the exact ticket patch, no extra tool calls, and `P114_C4_ROLE_DONE`. The
target became `after`; four adapter exchanges returned `200 text/event-stream`;
and teardown restored the normal Worker profile, stopped the adapter, and
removed the temporary process environment.

This is a `quality_validated_candidate` and
`protocol_accepted_candidate` for P114.3's CLI-parent route. It makes no
economics claim and does not erase the distinct VS Code-parent R8/R9 dispatch
limitation. Repeat it with
`scripts/run_p114_c4_cli_parent_control.ps1 -RunId <new_run_id> -AdapterPort <unused_port>`.

## VS Code patch-via-exec observation: `p114_c4_role_binding_r10_exec_wrapper`

Fresh VS Code-parent child `019f727d-2d41-7d52-8ede-9cf71752234b` used the
frozen `ollama_qwen_coder_worker`, the run-scoped r10 provider, the literal
worktree, `fork_context:false`, and exactly one native wait. Its raw session
records the intended host shape: `shell_command`, custom `exec` containing
`tools.apply_patch(...)`, then `shell_command`. The host rejected the middle
call as `unsupported custom tool call: exec`; the second read therefore found
the target still `before` and the session never emitted `P114_C4_ROLE_DONE`.

The adapter recorded the declared first provider calls but later rejected
undeclared `exec` activity; its evidence cannot supply the exact three-call
provider sequence required for acceptance. The required disable command ran
after inspection and restored the r10 bridge. This is a VS Code host
custom-tool-dispatch failure, not a `quality_validated_candidate`,
`protocol_accepted_candidate`, C4 qualification, or economics result. P114.3
remains open for the intended VS Code route.

## Required no-mutation host-tool inventory preflight

The r10 failure showed that the provider catalog is not an inventory of tools
the VS Code child host will actually dispatch. Before another patch ticket,
enable a new bridge run with `-HostToolInventory`. That mode permits one
declared provider `exec` only, but translates it to a custom `exec` whose
JavaScript prints executor-local `ALL_TOOLS` names. It does not invoke a shell,
read a file, or apply a patch.

Run this only from a new parent opened after bridge enablement. Accept the
preflight only when its single raw child custom-call output names both
`shell_command` and `apply_patch` and the Worker returns
`P114_C4_HOST_TOOL_INVENTORY_DONE`. If custom `exec` is rejected or either
name is absent, disable the bridge and do not launch a patch Worker from that
parent. Focused adapter tests cover the inert translation and bridge mode;
the fresh host observation remains pending.

## Invalid coordinator handoff: `p114_c4_role_binding_r11_host_inventory`

Fresh child `019f7286-da4e-7160-9808-b0ab1f895c7e` persisted the frozen role,
r11 provider, literal worktree, and `fork_context:false`, but this is not a
host-tool inventory observation. The Coordinator mistakenly passed the literal
ticket *path* as the Worker message rather than the generated ticket contents.
The raw child therefore received only
`runtime/agent_jobs/p114_c4_role_binding_r11_host_inventory/ticket.md` and had
no declared inventory instruction.

Its stream disconnected before completion; the adapter's six repeated provider
turns and `undeclared_exec` verdicts are consequences of that invalid input,
not evidence about custom `exec`, `ALL_TOOLS`, or VS Code host dispatch. The
bridge was correctly torn down, but r11 is excluded from P114.3 quality,
protocol, and economics evidence. A later fresh-parent preflight must pass the
ticket contents verbatim, not its filename.

## Conclusive VS Code host-tool inventory result: `p114_c4_role_binding_r12_host_inventory`

Fresh child `019f728b-a1b4-7cc0-8305-b9ef26e5f21a` received the r12 ticket
contents verbatim and made the sole permitted host call: custom `exec` with
the inert `ALL_TOOLS` inventory JavaScript. The VS Code host returned
`unsupported custom tool call: exec`. No shell, file, or patch call occurred;
the target remained `before`, no inventory output or terminal marker appeared,
and teardown restored the bridge. This is valid negative host-dispatch evidence
that the UI Worker does not register the generic custom executor. Do not launch
another UI patch Worker until that registration is repaired.

## VS Code app-server and code-mode-host registration boundary

A fresh VS Code session was transparently observed at the app-server boundary.
Its user `thread/start` record and its internal fetch-helper `thread/start`
record both explicitly contained `dynamicTools: null`. Thus the VS Code client
does not supply a dynamic-tool registration table that can inventory Worker
host labels; this observation is not a Worker run and does not alter the
R12 result.

The Codex app-server documentation explicitly permits experimental
`dynamicTools` on `thread/start`; resulting `dynamicToolCall` items are
client-executed. The captured `null` therefore means this VS Code extension is
not using that documented registration point, not that Codex lacks dynamic
registration. The deterministic executable comparison still returned
`host_registration_gap`: direct `codex.exe` contained
`apply_patch_tool_type` 14 times, `custom_tool_call` 39 times, and
`unsupported custom tool call` once, while the sibling code-mode host contained
none. That comparison corroborates a current integration gap but cannot locate
the responsible component or enumerate its tools. Do not run another UI Worker
to rediscover the boundary. Use the accepted CLI-parent route for productive C4
work; make a separate VS Code integration repair that supplies dynamic tool
specifications and handles the resulting client-executed calls.

## VS Code dynamic-tool registration proof

A reversible app-server relay registered a no-mutation `p114_exec` function on
fresh VS Code `thread/start` requests. The tool accepts only
`{"operation":"inventory"}`. A fresh parent invoked it once; app-server sent
`item/tool/call` with `tool: "p114_exec"` and the relay returned a successful
client response marked `P114_DYNAMIC_EXEC_HANDLER_REACHED`. This proves the
documented dynamic-tool registration and client-handler path works in VS Code.
It does not establish that the tool is inherited by a `multi_agent_v1` child,
does not execute a shell command, and does not change the R8--R12 UI Worker
negative evidence. The temporary VS Code executable setting was removed after
inspection.

## VS Code dynamic-tool Worker inheritance result: `p114_c4_role_binding_r13_dynamic_exec_inheritance`

R13 launched exactly one fresh `ollama_qwen_coder_worker` with
`fork_context:false` and the generated ticket text, then waited once. Its raw
child session `019f72ae-d794-75b2-9748-bb558d0061d1` received the ticket and
emitted the single provider-declared `exec`; the bridge correctly materialized
that as a native `p114_exec({"operation":"inventory"})` function call. The
nested Worker host returned `unsupported call: p114_exec`. The parent relay
recorded no child `item/tool/call`, the target stayed `before`, and no shell,
patch, file operation, or extra host call occurred. The terminal ticket marker
was produced but is not an acceptance marker because the required handler never
ran.

This proves a narrower result than R12: dynamic tools register and dispatch in
the VS Code parent, and their names can reach a Worker model, but the
multi-agent code-mode host does not route the resulting nested function call to
the parent client's dynamic-tool handler. R13 is negative integration evidence,
not a quality, protocol, or economics result. The run-scoped bridge was
disabled; the Codex configuration and Worker role matched their backups.

## VS Code parent MCP routing proof: `p114_mcp_exec_probe_r1`

A reversible local stdio MCP server exposed one no-mutation `p114_exec` tool
that accepts only `{"operation":"inventory"}`. After a fresh VS Code restart,
the extension initialized the server, listed its tools, and invoked that exact
call once. The server recorded `P114_MCP_EXEC_HANDLER_REACHED`. This is a
supported parent-tool result and the MCP configuration was restored afterward.
It does not yet establish Worker MCP routing: the current P114 provider adapter
replaces the outgoing tool catalog with its legacy `apply_patch`/`exec` pair and
rejects `additional_tools`, so a child MCP test first needs a separate
fail-closed catalog-preservation repair.

## VS Code Worker MCP schema result: `p114_c4_role_binding_r14_mcp_schema_discovery`

R14 launched exactly one fresh Worker and waited once. Its raw *provider*
request contained the role bridge's legacy `apply_patch` and `exec` function
definitions, but no `additional_tools` input item and no `p114_exec` MCP
schema. This is provider-model catalog evidence, not proof that the nested
Worker host dispatches `apply_patch` or `exec`; R8--R13 independently show the
opposite dispatch failures. The local MCP server logged zero child tool calls,
the target remained `before`, and the Worker made no host call before returning
its terminal ticket marker. R14 established only the absence of a *direct* MCP
schema in that request, not the absence of all child MCP discovery. The MCP
probe was disabled first, then the role bridge; configuration and Worker-role
hashes matched backups.

## VS Code Worker MCP discovery result: `p114_c4_role_binding_r15_mcp_codemode_schema`

R15 enabled Code Mode with empty excluded/direct-only namespace lists and
launched exactly one fresh Worker, waited once, and made no host mutation. The
raw child request exposed `p114_exec_probe` through the deferred `tool_search`
catalog, whose instructions explicitly require `tool_search` for MCP discovery;
it did not expose a direct `p114_exec` function schema. The frozen ticket
incorrectly prohibited that required discovery call and demanded a direct
`mcp__server__p114_exec_probe` invocation. The Worker therefore emitted
non-executed markup, the MCP log contained initialization/listing only and zero
`tools/call` requests, and the target remained `before`.

This is the first positive child MCP-routing evidence: the registry reaches the
Worker as a discoverable tool source. The next bounded no-mutation proof must
allow exactly `tool_search` followed by the one discovered MCP inventory call;
it must not infer a direct schema from the registry. The MCP probe was disabled
before the bridge and both configuration and Worker-role hashes matched their
backups.

## VS Code Worker deferred MCP routing result: `p114_c4_role_binding_r16_mcp_deferred_routing`

R16 used the corrected two-call ticket and launched exactly one fresh Worker,
waiting once. The raw provider stream shows six completed `tool_search`
function calls. The nested host never executed any of them or supplied a tool
result; it retried the identical call until its provider stream disconnected
before `response.completed`. The MCP server recorded initialization/listing but
zero `tools/call` requests, the target remained `before`, and no shell, patch,
file, or MCP mutation occurred.

This rejects the run and localizes the defect to nested code-mode dispatch of
`tool_search`: the child model can request deferred MCP discovery, but the
Worker host does not execute the discovery tool or continue the turn. The next
repair is source-level/supported-extension routing for nested `tool_search`,
not another direct-MCP or provider-catalog probe. Teardown restored both
configuration and Worker-role hashes byte-for-byte.

## VS Code Worker direct-MCP workaround result: `p114_c4_role_binding_r17_direct_mcp_routing`

R17 tested the local workaround hypothesis that
`tool_search_always_defer_mcp_tools = false` plus Code Mode would expose the
MCP probe as a direct child tool and bypass nested `tool_search`. It launched
exactly one fresh `ollama_qwen_coder_worker`
(`019f72ca-6aa5-7d53-b9ce-5e6de2133692`) with `fork_context:false` and waited
once. The child errored with `stream disconnected before completion: stream
closed before response.completed`; its raw session ended with
`last_agent_message:null`.

The raw child request still contained `tool_search` and only mentioned
`p114_exec_probe` in that deferred-tool guidance; no direct `p114_exec` MCP
function schema was present. The role bridge's provider-facing requests still
declared only `apply_patch` and `exec`. The provider then repeatedly emitted
`exec` function calls, producing six adapter `undeclared_exec` rejections. The
MCP server recorded initialization/listing only and zero `tools/call` requests;
the target remained `before` and no terminal
`P114_C4_DIRECT_MCP_ROUTING_DONE` marker appeared.

This rejects the direct-MCP workaround. It does not change the R16 diagnosis:
configured MCP reaches the child only through deferred discovery in this route,
and the nested Worker host still lacks the working dispatch/continuation path
needed to execute that discovery. MCP-first teardown restored the exact Codex
configuration and Worker-role hashes byte-for-byte.

## VS Code Worker repaired MCP routing result: `p114_c4_role_binding_r19_mcp_inventory_repaired`

R19 used the repaired bounded MCP inventory adapter path and launched exactly
one fresh Worker, child `019f72db-e8e5-7a73-9a45-06fa2ec81f36`, with
`fork_context:false`. The child received the generated ticket text and returned
the terminal marker `P114_C4_MCP_ROUTING_DONE`, but the run is rejected because
the required MCP call did not execute.

The repaired adapter boundary behaved as intended: the provider-facing request
first exposed only `tool_search`, then exposed only
`mcp__p114_exec_probe__p114_exec` after the search result. Adapter events show
one `tool_search` function call and one
`mcp__p114_exec_probe__p114_exec` function call; all adapter verdicts were
`accepted`, with no `unsupported_tool_or_event`, `undeclared_exec`, shell,
patch, or file-call rejection. The target remained `before`.

The raw child session records the decisive failure:
`mcp__p114_exec_probe__p114_exec` returned
`unsupported call: mcp__p114_exec_probe__p114_exec`. The MCP server recorded
initialization/listing only and zero `tools/call` requests. Therefore R19
moves the defect boundary beyond the P114 adapter: after the adapter forwards
the bounded lifecycle, the nested VS Code Worker host still does not route the
discovered MCP function to MCP. Configuration and Worker-role state were
restored after inspection; final cleanup required disabling the MCP probe again
after bridge restore because the bridge backup had captured the staged MCP
configuration.

R20 source audit corrected that conclusion. In native Codex, `tool_search` is
not an ordinary `function_call`; it must be a `tool_search_call` item with
`execution: "client"`. R19's provider continuation showed the adapter-emitted
function-call search result as `aborted`, then the adapter exposed
`mcp__p114_exec_probe__p114_exec` synthetically. The Worker therefore called a
tool that native Codex had not actually discovered, explaining the
`unsupported call` result without requiring a deeper child MCP dispatch defect.

The adapter now emits native `tool_search_call`, preserves
`tool_search_output`, and only exposes the MCP inventory tool after the real
search output contains the probe tool. Focused adapter validation passes with
28 tests. The next proof should be a fresh no-mutation R20 MCP inventory run
after VS Code restart.

## VS Code Worker native tool_search result: `p114_c4_role_binding_r20_native_tool_search`

R20 launched exactly one fresh Worker, child
`019f72e8-d351-7143-ad4f-55e0f41c3296`, with `fork_context:false` and the
generated ticket text verbatim. The Coordinator waited exactly once. The child
errored with:

```text
input[3]: unknown input item type: "tool_search_call"
```

The run is rejected. The raw session is still useful: native child discovery
worked. It records a `tool_search_call` for
`p114_exec_probe p114_exec inventory`, followed by a `tool_search_output`
containing namespace `mcp__p114_exec_probe` and function `p114_exec`. The MCP
server recorded initialization/listing only and zero `tools/call` requests; the
target stayed `before`.

After inspection, operator state was restored in order: MCP probe disable, then
role bridge disable. Final config and Worker-role hashes matched the bridge
backup, run-scoped config entries were absent, and adapter PID `12560` was
stopped.

Post-run adapter repair: the search-output detector now recognizes the actual
top-level namespace output shape from Codex. Focused validation passes with 28
tests. The next repair target is the provider continuation translation for
`tool_search_call`/`tool_search_output`, not another Worker prompt.

## Provider-compatible continuation repair for next MCP proof

The R20 follow-up repair is implemented locally. The adapter still forwards
provider `tool_search` calls to the child as native `tool_search_call` response
items and preserves native `tool_search_output` in the child session. For the
next provider request, it now replays those child-native history items upstream
as provider-compatible `function_call` and `function_call_output` items instead
of sending unsupported `tool_search_call` input items back to the
OpenAI-compatible provider.

The repair keeps the R20 safety boundary: `mcp__p114_exec_probe__p114_exec` is
exposed only after the real `tool_search_output` contains the probe tool. The
loopback fixture was also aligned with the current fail-closed declared-command
contract.

Validation:

```text
python -m pytest tests\test_p114_capability_tool_adapter.py tests\test_p114_capability_tool_adapter_loopback.py -q
29 passed in 1.12s
python -m py_compile src\agent_workbench\p114_capability_tool_adapter.py scripts\p114_capability_tool_adapter.py
git diff --check
```

`git diff --check` returned success with LF/CRLF warnings only. The next proof
should be a fresh no-mutation R21 Worker after bridge/MCP staging and VS Code
reload; R20 remains rejected.

## VS Code Worker MCP dispatch result: `p114_c4_role_binding_r21_provider_replay`

R21 launched exactly one fresh Worker,
`019f72f0-d984-7d32-878a-910c3d654b88`, with `fork_context:false` and the
generated ticket text verbatim. The Coordinator waited exactly once. The Worker
returned `P114_C4_MCP_ROUTING_DONE`, but the run is rejected.

The provider replay repair worked: `adapter_requests.jsonl` shows that the
second and third provider-facing requests replayed child-native search history
as `function_call` and `function_call_output`, not as unsupported
`tool_search_call` or `tool_search_output` input items. Adapter verdicts were
all `accepted`.

The raw child session records the remaining failure:

- native `tool_search_call` for `p114_exec_probe p114_exec inventory`;
- native `tool_search_output` containing namespace `mcp__p114_exec_probe` and
  function `p114_exec`;
- `function_call: mcp__p114_exec_probe__p114_exec` with
  `{"operation":"inventory"}`;
- `function_call_output: unsupported call:
  mcp__p114_exec_probe__p114_exec`.

The MCP probe log recorded initialization/listing only and zero `tools/call`
requests. The target remained `before`; no shell, patch, file, or target
mutation occurred. After inspection, MCP and bridge disable restored operator
state: the run-scoped config entries were absent, the Worker role no longer
referenced R21, and port `19008` had no listener.

R21 rejects the no-mutation MCP proof and localizes the next repair to nested
Worker host routing of discovered MCP functions, not provider continuation
serialization.

## R21 source-audit correction and R22 adapter repair

The R21 failure was narrower than a missing nested MCP dispatcher. The Codex
source and upstream search-tool tests show that search-surfaced MCP calls are
expected to arrive as namespaced function calls, for example namespace
`mcp__rmcp`, name `echo`. The direct core path has tests asserting that this
does not produce `unsupported call`.

The R21 adapter had instead forwarded the provider-side workaround as a flat
child function name: `mcp__p114_exec_probe__p114_exec`. That flat name does not
match the registered MCP handler, which is namespaced as
`mcp__p114_exec_probe / p114_exec`.

Repair staged for R22:

- provider-facing request still exposes/replays the flat compatibility function
  `mcp__p114_exec_probe__p114_exec`;
- child-facing response stream now emits namespace `mcp__p114_exec_probe`, name
  `p114_exec`;
- continuation replay accepts that native namespaced child history and converts
  it back to the flat provider call.

Validation:

```text
python -m pytest tests\test_p114_capability_tool_adapter.py tests\test_p114_capability_tool_adapter_loopback.py -q
30 passed in 1.32s
python -m py_compile src\agent_workbench\p114_capability_tool_adapter.py scripts\p114_capability_tool_adapter.py
git diff --check
```

R22 should test the same no-mutation ticket. The key acceptance discriminator
is whether the raw child session now shows a namespaced
`mcp__p114_exec_probe / p114_exec` function call and the MCP log records one
`tools/call`.

## VS Code Worker MCP routing accepted: `p114_c4_role_binding_r22_namespaced_mcp`

R22 launched exactly one fresh Worker,
`019f72f7-9bc7-76f1-94de-9c16013ccede`, with `fork_context:false` and the
generated ticket text verbatim. The Coordinator waited exactly once. The Worker
returned `P114_C4_MCP_ROUTING_DONE`.

The run is accepted as a no-mutation MCP routing proof. The raw child session
records:

- `tool_search_call` for `p114_exec_probe p114_exec inventory`;
- `tool_search_output` exposing namespace `mcp__p114_exec_probe` and function
  `p114_exec`;
- namespaced `function_call` with namespace `mcp__p114_exec_probe`, name
  `p114_exec`, and arguments `{"operation":"inventory"}`;
- `function_call_output` containing `P114_MCP_EXEC_HANDLER_REACHED`.

The MCP probe log recorded exactly one `tools/call` and its corresponding
marker record. The provider-facing adapter request retained the flat
compatibility call `mcp__p114_exec_probe__p114_exec`, all adapter verdicts were
`accepted`, and the target remained `before`. No shell, patch, file, or target
mutation occurred.

After inspection, operator state was restored: run-scoped provider/MCP config
entries were absent, the Worker role no longer referenced R22, and port `19008`
had no listener.

This accepts MCP routing through deferred discovery only. A separate proof is
still required for mutation/patch semantics over MCP or any other route.

## VS Code Worker MCP patch accepted: `p114_c4_role_binding_r23_mcp_patch`

R23 launched exactly one fresh Worker,
`019f730c-a338-7b52-904e-0fbdf9a8fb45`, with `fork_context:false` and the
generated ticket text verbatim. The Coordinator waited exactly once. The Worker
returned `P114_C4_MCP_PATCH_DONE`.

The run is accepted as a bounded MCP mutation proof. The raw child session
records:

- `tool_search_call` for `p114_exec_probe p114_exec patch`;
- `tool_search_output` exposing namespace `mcp__p114_exec_probe` and function
  `p114_exec`;
- namespaced `function_call` with namespace `mcp__p114_exec_probe`, name
  `p114_exec`, and arguments `{"operation":"patch"}`;
- `function_call_output` containing `P114_MCP_PATCH_HANDLER_REACHED`.

The MCP probe log recorded exactly one `tools/call` with
`{"operation":"patch"}` and a marker record containing before `before\n` and
after `after\n`. The target file was exactly `after\n` after inspection. The
provider-facing adapter request retained the flat compatibility function
`mcp__p114_exec_probe__p114_exec`, and all adapter verdicts were `accepted`.
No shell, `exec`, `apply_patch`, custom-tool, or file-read fallback occurred in
the raw child session.

After inspection, operator state was restored: run-scoped provider/MCP config
entries were absent, the Worker role no longer referenced R23, `config.toml`
parsed, and port `19008` had no listener.

This proves that VS Code Worker deferred MCP discovery can reach a bounded MCP
mutation handler through the native namespaced child call path.
