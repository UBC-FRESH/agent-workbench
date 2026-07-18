# P114 VS Code Worker MCP breakthrough

Date: 2026-07-17

This note preserves the R22 milestone because it is the first accepted crack in
the VS Code Worker capability wall.

## Milestone insight

R22 proved that a nested VS Code Worker can reach a real configured MCP server
through deferred discovery:

1. The Worker emitted a native `tool_search_call`.
2. The host returned a native `tool_search_output` exposing namespace
   `mcp__p114_exec_probe` and tool `p114_exec`.
3. The Worker emitted a namespaced MCP `function_call` with namespace
   `mcp__p114_exec_probe`, name `p114_exec`, and arguments
   `{"operation":"inventory"}`.
4. The MCP server recorded exactly one `tools/call` and returned
   `P114_MCP_EXEC_HANDLER_REACHED`.
5. The Worker returned `P114_C4_MCP_ROUTING_DONE`.

The critical shape is not the provider-facing flat compatibility function name.
The child-facing call must preserve Codex's native MCP identity:

```text
namespace: mcp__p114_exec_probe
name:      p114_exec
```

The provider may still need the flat compatibility name
`mcp__p114_exec_probe__p114_exec`, but that name must be translated at the
adapter boundary. Forwarding the flat name into the child produced the R21
`unsupported call` failure.

## Why this matters

This rules in MCP as a viable subagent capability route. The earlier failures
were not proof that MCP cannot work in nested Workers. They were boundary-shape
failures:

- R20 reached native deferred MCP discovery but provider replay rejected native
  `tool_search_call` history.
- R21 replayed provider-flat MCP calls, but the nested host only dispatched the
  namespaced MCP shape.
- R22 repaired both edges: native child shape inside VS Code, flat provider
  shape only at the OpenAI-compatible provider boundary.

## Current boundary

R22 is accepted only as a no-mutation MCP routing proof. It did not prove patch
or file-mutation semantics. The target remained `before`, no shell calls ran,
and no `apply_patch` call ran.

## Crowbar plan

The next bounded proof is an env-gated MCP mutation route:

- keep the same R22 deferred-discovery path;
- expose the same `p114_exec` MCP tool;
- require operation `patch`;
- allow patch mode only when the MCP server receives
  `P114_MCP_PROBE_ALLOW_PATCH=1` and a literal
  `P114_MCP_PROBE_TARGET`;
- require the target to contain exactly `before\n`;
- write exactly `after\n`;
- return marker `P114_MCP_PATCH_HANDLER_REACHED`;
- require Worker terminal marker `P114_C4_MCP_PATCH_DONE`;
- reject any shell, `exec`, `apply_patch`, file-read, or extra host call.

Acceptance for the mutation proof requires all of the following:

- raw child session sequence: `tool_search_call` -> `tool_search_output` ->
  namespaced MCP `function_call`;
- adapter/provider sequence: no shell/patch tools, only the deferred MCP path;
- MCP log: exactly one `tools/call` with `{"operation":"patch"}`;
- target file after inspection: exactly `after\n`;
- terminal marker: `P114_C4_MCP_PATCH_DONE`;
- operator state restored after inspection.

## Boot-critical config guardrail

R23 staging exposed a config-editing failure mode: appending generated TOML
fragments can corrupt `~/.codex/config.toml` if line breaks are lost. Because
Codex parses this file during startup, a single malformed assignment can prevent
the host from booting.

All future staging helpers that edit Codex configuration must treat
`config.toml` as boot-critical:

- back up the file before every edit;
- make only the smallest targeted run-scoped change;
- build generated TOML as explicit lines, not fragile string concatenation;
- parse the entire written TOML file after the write;
- restore the backup immediately if parsing fails;
- re-read and print the modified config context from disk after a successful
  parse.

The R23 MCP and role-bridge staging scripts now include full-file TOML
validation and automatic restore on validation failure.

## R23 result

R23 accepted the bounded MCP patch proof. Fresh Worker
`019f730c-a338-7b52-904e-0fbdf9a8fb45` ran once with `fork_context:false` and
the generated ticket verbatim. The raw child session followed the intended
native route:

```text
tool_search_call
tool_search_output
function_call namespace=mcp__p114_exec_probe name=p114_exec arguments={"operation":"patch"}
function_call_output P114_MCP_PATCH_HANDLER_REACHED
message P114_C4_MCP_PATCH_DONE
```

The MCP log recorded exactly one `tools/call` for `{"operation":"patch"}`. The
target changed from exact `before\n` to exact `after\n`. No shell, `exec`,
`apply_patch`, custom-tool, file-read, or extra host call appeared in the raw
child session. Operator state was restored after inspection.

This extends the R22 discovery/routing breakthrough to a tightly bounded MCP
mutation handler.
