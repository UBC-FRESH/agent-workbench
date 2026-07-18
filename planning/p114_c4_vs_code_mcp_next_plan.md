# P114.3 VS Code MCP Routing Next Plan

Status: active follow-up plan after R16/R17.

Scope: intended VS Code-parent route only. The CLI-parent route remains the
accepted productive P114.3/P114.4 route; this note does not alter that result,
resume P107, activate P108, or make an economics claim.

## Advisor correction

R16 and R17 should not yet be treated as conclusive proof that the nested
Worker host cannot dispatch MCP `tool_search`. The current P114 role bridge
and adapter may still be blocking the relevant lifecycle before the host gets a
fair dispatch opportunity.

The binary string comparison between `codex.exe` and
`codex-code-mode-host.exe` is corroborating context only, not decisive
registration evidence. The code-mode host may delegate implementation back to
Codex core and need not embed every native tool string itself.

## R18 no-mutation boundary audit

Run no Worker. Use existing R16/R17 evidence only.

Artifacts to inspect:

- `runtime/agent_jobs/p114_c4_role_binding_r16_mcp_deferred_routing/adapter_raw_requests.jsonl`
- `runtime/agent_jobs/p114_c4_role_binding_r16_mcp_deferred_routing/adapter_requests.jsonl`
- `runtime/agent_jobs/p114_c4_role_binding_r16_mcp_deferred_routing/adapter_events.jsonl`
- `runtime/agent_jobs/p114_c4_role_binding_r16_mcp_deferred_routing/adapter_verdicts.jsonl`
- R16 child session JSONL under `%USERPROFILE%/.codex/sessions/`
- `runtime/agent_jobs/p114_mcp_exec_probe_r4_deferred/mcp_calls.jsonl`
- The same R17 artifacts under `p114_c4_role_binding_r17_direct_mcp_routing`
  and `p114_mcp_exec_probe_r5_direct`

Boundary matrix to record:

- Whether the host-side raw request advertised `tool_search`.
- Whether the adapter preserved `tool_search` in the provider-facing request.
- Whether the provider emitted `tool_search`, `exec`, or another tool.
- Whether the adapter forwarded that call or rejected it.
- Whether the host ever received a tool result opportunity.
- Whether the MCP server received `tools/call`.
- Component identities: VS Code extension version, Codex CLI version, and
  SHA-256 hashes for `codex.exe` and `codex-code-mode-host.exe`.

Decision signal:

- If the adapter rejected or rewrote the lifecycle before host dispatch, repair
  the adapter before another live Worker.
- Only investigate the nested host after evidence shows the adapter forwarded
  a complete lifecycle and the host then rejected or dropped it.

### R18 findings

R18 used only existing R16/R17 artifacts. No Worker was launched.

Component identities:

- VS Code extension: `openai.chatgpt-26.707.91948-win32-x64`
- Codex CLI version in both child sessions: `0.144.5`
- `codex.exe` SHA-256:
  `EFDB3540EF74B9909408C8D38DA79483454797B36F471E3E004FC2BF2B70E22A`
- `codex-code-mode-host.exe` SHA-256:
  `5D7DB48DEE5E82AE23E98E33C3421F2774DC50C52C53374685D616997844116F`

Boundary matrix:

| Boundary | R16 deferred MCP | R17 direct-MCP workaround |
| --- | --- | --- |
| Raw host-side request advertised `tool_search` | yes; raw catalog had 15 tools including `tool_search` | yes; raw catalog had 15 tools including `tool_search` |
| Adapter provider-facing request preserved `tool_search` | no; provider catalog was `apply_patch,exec` | no; provider catalog was `apply_patch,exec` |
| Provider emitted | `tool_search` function calls | `exec` function calls |
| Adapter forwarded emitted call | no; six `rejected:unsupported_tool_or_event` verdicts | no; six `rejected:undeclared_exec` verdicts |
| Host received tool-result opportunity | no evidence | no evidence |
| MCP server received `tools/call` | no; initialize/list only | no; initialize/list only |
| Child final message | none; `last_agent_message:null` | none; `last_agent_message:null` |

Relevant adapter boundaries:

- `src/agent_workbench/p114_capability_tool_adapter.py` currently defines
  `TOOLS = [PATCH_TOOL, EXEC_TOOL]`.
- `translate_request` rejects `additional_tools` and replaces the outgoing
  `tools` catalog with the two-tool P114 catalog.
- `parse_provider_call` and the streaming translator accept only
  `apply_patch` and `exec`; `tool_search` is rejected as
  `unsupported_tool_or_event`.
- The role-bridge wrapper's `--forced-tool` choices are currently only
  `exec` and `apply_patch`.

R18 decision: repair the bounded adapter/bridge MCP inventory path before any
new Worker proof. The current evidence has not yet reached the point where the
nested Worker host fairly receives and drops a forwarded `tool_search`
lifecycle.

## Preferred repair: bounded MCP inventory mode

Add an explicit adapter/bridge mode for MCP inventory.

Required behavior:

- Preserve or translate incoming `tool_search` without replacing it with only
  the legacy `apply_patch`/`exec` catalog.
- Allow exactly one `tool_search(query, limit)`.
- Allow exactly one resulting `p114_exec_probe.p114_exec` call with arguments
  `{"operation":"inventory"}`.
- Preserve item IDs, call IDs, streamed argument events, completed output, and
  continuation history.
- Reject unrelated tools, mutation arguments, second MCP calls, shell calls,
  `exec`, `apply_patch`, file access, and undeclared behavior.

Offline tests before any live run:

- Captured R16-style `tool_search` lifecycle passes through intact.
- Search output survives the continuation request.
- One exposed MCP inventory call passes through.
- Unknown tools still fail closed.
- Completed response output uses the same identities as streamed events.

### Implementation status

Initial bounded adapter repair is implemented locally:

- `src/agent_workbench/p114_capability_tool_adapter.py` adds a narrow
  `mcp_inventory` path that exposes `tool_search` first, then
  `mcp__p114_exec_probe__p114_exec` after the `tool_search` result.
- The stream translator now forwards only those two MCP-routing function calls
  as native function calls instead of rejecting them as unsupported custom
  events.
- `scripts/p114_capability_tool_adapter.py` wires the mode through
  `--mcp-inventory-route`.
- `scripts/enable_p114_c4_role_bridge.ps1 -McpInventory` enables that route.
- Focused tests cover initial catalog narrowing, continuation after
  `tool_search`, exact inventory-call forwarding, invalid MCP arguments, and
  existing fail-closed behavior.

Verification: `python -m pytest tests\test_p114_capability_tool_adapter.py -q`
passes with 26 tests. This is offline adapter evidence only; no R19 Worker has
been launched.

### R19 live result

R19 launched one fresh `ollama_qwen_coder_worker`
(`019f72db-e8e5-7a73-9a45-06fa2ec81f36`) with `fork_context:false` after the
repaired MCP inventory adapter path was staged and VS Code was restarted. The
child returned `P114_C4_MCP_ROUTING_DONE`, but the run is rejected.

Evidence:

- Raw provider-facing requests changed as intended: request 1 exposed only
  `tool_search`; requests 2 and 3 exposed only
  `mcp__p114_exec_probe__p114_exec`.
- Adapter events show one `tool_search` function call followed by one
  `mcp__p114_exec_probe__p114_exec` function call, then the terminal message.
- Adapter verdicts contain only `accepted`; the adapter no longer rejected or
  rewrote the bounded lifecycle.
- The raw child session records
  `function_call_output` for `mcp__p114_exec_probe__p114_exec` with output
  `unsupported call: mcp__p114_exec_probe__p114_exec`.
- The MCP server log contains initialization/listing only and zero
  `tools/call` requests.
- The target remained `before`.

R19 therefore moves the defect boundary: the adapter repair worked far enough
to present the nested host with the bounded MCP function, but the nested Worker
host did not dispatch that function to MCP. The next repair is no longer the
P114 adapter; it is the spawned-child code-mode/MCP dispatch path or an
extension integration path that registers and routes the MCP function for child
threads.

Restore note: disabling the bridge after MCP teardown reintroduced the MCP
configuration because the bridge backup was taken after MCP staging. The final
operator cleanup disabled the MCP probe again after bridge restore. Final
hashes matched the original MCP backup and Worker-role backup, run-scoped
config entries were absent, and adapter PID `29000` was stopped.

## R20 source audit and adapter correction

The installed Codex binary reports version `0.144.5`; the matching upstream tag
is `rust-v0.144.5`. A source audit of that tag found the exact `unsupported
call` generation in `core/src/tools/registry.rs`: Codex emits that response when
the runtime registry has no executor for the model's function name.

The same audit found the concrete adapter error left by R19. Codex does not
parse `tool_search` as an ordinary `function_call`; it has a dedicated
`tool_search_call` response item with `execution: "client"` and object
arguments. The R19 adapter exposed provider `tool_search` as a normal function
call, which the raw provider request later showed as a `function_call_output`
of `aborted`. The adapter then exposed `mcp__p114_exec_probe__p114_exec`
synthetically anyway, so the model could request the MCP tool even though native
Codex had not completed real tool discovery. That explains the apparent
contradiction where the provider saw the MCP tool but the child session returned
`unsupported call`.

Implemented repair:

- `src/agent_workbench/p114_capability_tool_adapter.py` now converts provider
  `function_call: tool_search` into native `tool_search_call` events.
- MCP inventory continuation now preserves native `tool_search_call` and
  `tool_search_output` history.
- The adapter exposes `mcp__p114_exec_probe__p114_exec` only after a real
  `tool_search_output` contains the target tool, including namespace-shaped MCP
  search results.
- Focused tests now cover native `tool_search_call`, namespace-shaped MCP
  search output, and the no-hit case where the MCP tool must not be exposed.

Validation:

```text
python -m py_compile src\agent_workbench\p114_capability_tool_adapter.py scripts\p114_capability_tool_adapter.py
python -m pytest tests\test_p114_capability_tool_adapter.py -q
28 passed in 0.18s
```

Next action: stage a fresh no-mutation R20 MCP inventory proof after VS Code
restart. Accept only if the child session records native `tool_search_call`,
native `tool_search_output` with the probe tool, a real MCP `tools/call`, and
then `P114_C4_MCP_ROUTING_DONE`. If R20 still returns `unsupported call` after
native `tool_search_output`, resume the source/extension repair path below.

## R20 live proof result

R20 launched exactly one fresh `ollama_qwen_coder_worker`
(`019f72e8-d351-7143-ad4f-55e0f41c3296`) with `fork_context:false`, no model,
reasoning, or service-tier override, and the generated ticket text verbatim.
The Coordinator waited exactly once. The child errored:

```text
input[3]: unknown input item type: "tool_search_call"
```

R20 is rejected, but it moved the evidence forward:

- The raw child session contains a native `tool_search_call` with query
  `p114_exec_probe p114_exec inventory`.
- The raw child session then contains a native `tool_search_output` whose tools
  include namespace `mcp__p114_exec_probe` and function `p114_exec`.
- No MCP `tools/call` was executed; the MCP log contains initialize/list
  requests only.
- The target file remained `before`.
- Adapter verdicts are accepted until the provider returned HTTP 400.

Post-run repair: the adapter detector now recognizes the actual Codex
namespace-shaped `tool_search_output` form:
`{"type":"namespace","name":"mcp__p114_exec_probe","tools":[...]}`. Focused
validation remains green with 28 adapter tests and Python compile.

Current boundary: native child-side deferred MCP discovery works, but the
OpenAI-compatible upstream rejects `tool_search_call` when it is replayed in
the next provider request. The next repair is a provider-compatibility
translation for continuation history: keep native `tool_search_call` and
`tool_search_output` in Codex child history, but send an upstream-compatible
representation to the Ollama provider while preserving enough local state to
expose the MCP inventory tool on the next request.

## R21 readiness repair: provider-compatible native discovery replay

The continuation-history repair is now implemented locally. The adapter still
emits native `tool_search_call` and `tool_search_output` to the Codex child, so
the child session can prove real deferred discovery. On the next outbound
provider request, those same native history items are replayed upstream as
ordinary provider-compatible `function_call` and `function_call_output` items.
The serialized search output preserves the returned namespace/tool inventory,
and the adapter still exposes `mcp__p114_exec_probe__p114_exec` only when that
real search output contains the probe tool.

Focused validation:

```text
python -m pytest tests\test_p114_capability_tool_adapter.py tests\test_p114_capability_tool_adapter_loopback.py -q
29 passed in 1.12s
python -m py_compile src\agent_workbench\p114_capability_tool_adapter.py scripts\p114_capability_tool_adapter.py
git diff --check
```

`git diff --check` returned success with only the repo's existing LF/CRLF
warnings. The next live step is one fresh no-mutation R21 run after staging the
bridge and MCP probe, followed by VS Code reload. Do not count R21 unless the
raw child records native discovery, the provider request no longer contains
unsupported `tool_search_call` input items, the MCP server records exactly one
`tools/call` with `{"operation":"inventory"}`, and the Worker returns
`P114_C4_MCP_ROUTING_DONE`.

## R21 live proof result: provider replay repaired, nested MCP dispatch still missing

R21 launched exactly one fresh `ollama_qwen_coder_worker`, child
`019f72f0-d984-7d32-878a-910c3d654b88`, with `fork_context:false` and the
generated ticket text verbatim. The Coordinator waited exactly once. The
Worker returned `P114_C4_MCP_ROUTING_DONE`, but the run is rejected because the
required MCP `tools/call` did not execute.

Verified evidence:

- Raw child session:
  `C:\Users\gep\.codex\sessions\2026\07\17\rollout-2026-07-17T18-56-59-019f72f0-d984-7d32-878a-910c3d654b88.jsonl`.
- The child recorded native `tool_search_call` followed by native
  `tool_search_output` containing namespace `mcp__p114_exec_probe` and
  function `p114_exec`.
- The next child host call was `function_call:
  mcp__p114_exec_probe__p114_exec` with `{"operation":"inventory"}`.
- The host returned `function_call_output`:
  `unsupported call: mcp__p114_exec_probe__p114_exec`.
- The provider-facing adapter requests no longer replayed unsupported
  `tool_search_call` input. They replayed the search history upstream as
  `function_call` and `function_call_output`.
- Adapter verdicts were all `accepted`.
- The MCP probe log recorded initialize/list operations only and zero
  `tools/call` requests.
- The target file stayed `before`.
- Operator state was restored after inspection: the run-scoped provider and MCP
  config entries were absent, the Worker role no longer referenced R21, and
  port `19008` had no listener.

R21 therefore closes the provider-replay defect from R20 and restores the
boundary to nested Worker MCP function dispatch: deferred discovery reaches the
child, but the spawned Worker host still does not route the discovered
`mcp__p114_exec_probe__p114_exec` function to MCP.

## R22 readiness repair: preserve native MCP namespace on child calls

The source audit refined the R21 diagnosis. Upstream Codex already has a
working path for search-surfaced MCP tools, but the function call must arrive
as a namespaced response item: namespace `mcp__<server>`, name `<tool>`.
`core/tests/suite/search_tool.rs` asserts this shape with
`ev_function_call_with_namespace(...)` and explicitly checks that
search-surfaced MCP calls do not fall through to `unsupported call`.

R21 did not use that native shape. The adapter exposed the provider workaround
as a flat function named `mcp__p114_exec_probe__p114_exec`, and forwarded the
same flat name into the child session. Core therefore resolved it as a plain
tool name, while the registered MCP handler was
`ToolName::namespaced("mcp__p114_exec_probe", "p114_exec")`. That explains the
observed child output:

```text
unsupported call: mcp__p114_exec_probe__p114_exec
```

The adapter now keeps the provider-side flat workaround but translates it to
the native child shape:

```json
{"type":"function_call","namespace":"mcp__p114_exec_probe","name":"p114_exec"}
```

Continuation replay maps that namespaced child history back to the flat
provider call so the upstream Ollama-compatible provider does not need native
namespace support.

Focused validation:

```text
python -m pytest tests\test_p114_capability_tool_adapter.py tests\test_p114_capability_tool_adapter_loopback.py -q
30 passed in 1.32s
python -m py_compile src\agent_workbench\p114_capability_tool_adapter.py scripts\p114_capability_tool_adapter.py
git diff --check
```

`git diff --check` returned success with LF/CRLF warnings only. The next live
step is a fresh no-mutation R22 proof after bridge/MCP staging and VS Code
reload. Accept only if the child records native `tool_search_call`,
`tool_search_output`, namespaced `function_call` with namespace
`mcp__p114_exec_probe` and name `p114_exec`, exactly one MCP `tools/call`, the
target remains `before`, and terminal marker `P114_C4_MCP_ROUTING_DONE`
appears.

## R22 live proof result: accepted no-mutation Worker MCP routing

R22 launched exactly one fresh `ollama_qwen_coder_worker`, child
`019f72f7-9bc7-76f1-94de-9c16013ccede`, with `fork_context:false` and the
generated ticket text verbatim. The Coordinator waited exactly once. The
Worker returned `P114_C4_MCP_ROUTING_DONE`.

R22 is accepted as a no-mutation MCP routing proof. Verified evidence:

- Raw child session:
  `C:\Users\gep\.codex\sessions\2026\07\17\rollout-2026-07-17T19-04-22-019f72f7-9bc7-76f1-94de-9c16013ccede.jsonl`.
- Native child sequence:
  `tool_search_call` -> `tool_search_output` -> namespaced `function_call`
  -> `function_call_output`.
- Search query: `p114_exec_probe p114_exec inventory`.
- Search result exposed namespace `mcp__p114_exec_probe` and function
  `p114_exec`.
- MCP call shape was native namespaced:
  namespace `mcp__p114_exec_probe`, name `p114_exec`, arguments
  `{"operation":"inventory"}`.
- MCP probe log recorded exactly one `tools/call` plus the marker record
  `P114_MCP_EXEC_HANDLER_REACHED`.
- Function output returned the handler marker to the child.
- Provider-facing adapter requests retained the flat compatibility call
  `mcp__p114_exec_probe__p114_exec`.
- Adapter verdicts were all `accepted`.
- Target file stayed `before`.
- No shell, patch, file, or target mutation occurred.
- After inspection, MCP and bridge disable restored operator state: run-scoped
  config entries were absent, the Worker role no longer referenced R22, and
  port `19008` had no listener.

This proves the VS Code Worker can route a discovered MCP tool through deferred
`tool_search` when the child-facing function call preserves Codex's native MCP
namespace shape. It is not a patch/mutation proof.

## R19 live proof gate

Permit one fresh no-mutation Worker only after the offline repair tests pass.

Accept only if all are true:

- Exactly one `tool_search`.
- Exactly one returned search result exposing `p114_exec_probe`.
- Exactly one MCP `tools/call` with `{"operation":"inventory"}`.
- Complete streamed and completed lifecycles with matching IDs.
- Child receives the result and returns the terminal marker.
- Zero adapter rejections, unsupported calls, shell calls, patches, file calls,
  or target changes.

Only after R19 passes may a separate mutation proof be considered. A successful
MCP inventory proof alone does not prove patch capability.

## Source or extension repair path

If the repaired adapter forwards the complete lifecycle but the VS Code child
still fails, add an exact-topology regression against the relevant Codex source
version:

```text
app-server or VS Code parent
  -> multi_agent_v1 spawn, fork_context:false
  -> child with Code Mode plus deferred MCP
  -> tool_search
  -> one MCP inventory call
  -> result continuation
  -> terminal marker
```

Likely source areas:

- `core/src/tools/handlers/tool_search.rs`
- `core/src/tools/handlers/multi_agents_common.rs`
- `core/src/tools/code_mode/delegate.rs`
- `core/src/tools/code_mode/mod.rs`
- `code-mode-host/src/delegate.rs`

Build staged patched binaries side-by-side and point VS Code's development
`chatgpt.cliExecutable` setting at that staging build. Do not replace installed
extension binaries.

## Stop conditions

- Do not repeat R16/R17 prompt or configuration experiments without a code
  change that directly addresses the failed boundary.
- Stop immediately if the adapter still rejects or rewrites `tool_search`.
- Stop after one changed-code live attempt if any lifecycle boundary is missing.
- If an exact upstream spawned-child regression fails, classify a Codex
  core/code-mode defect and repair there.
- If the upstream regression passes with staged binaries but VS Code fails,
  classify VS Code extension launch/client integration.
- If VS Code cannot run the staged sibling binaries, freeze an upstream issue
  packet and retain the CLI-parent route as the accepted P114.3/P114.4 route.
