# P113.1: One-Tool `apply_patch` Adapter Contract

Status: implementation contract for #649

## Decision

P113.2 may implement only a fail-closed adapter between Codex's custom
`apply_patch` tool and one provider function named `apply_patch`.  It is not a
general Responses proxy.  The adapter has no shell-write path and does not
translate MCP, Code Mode, or arbitrary custom tools.

## Request contract

For an initial request, the adapter must send exactly this function definition
and force its selection:

```json
{"type":"function","name":"apply_patch","parameters":{"type":"object","properties":{"patch":{"type":"string"}},"required":["patch"],"additionalProperties":false},"strict":true}
```

- `tools` contains this one definition only; `parallel_tool_calls` is `false`.
- The only accepted provider call has a non-empty unique `id` and `call_id`,
  `name == "apply_patch"`, and arguments that decode to an object with exactly
  one non-empty string key, `patch`.
- A run admits one call total. A second call, including a retry after a rejected
  first call, fails closed before patch mutation.
- The adapter never repairs malformed arguments, guesses a patch, or forwards
  an unsupported tool.

## Containment contract

The patch must have one complete `*** Begin Patch` / `*** End Patch` envelope
and only supported `Add`, `Update`, or `Delete File` operations. Each native
patch path must be repository-relative, normalized, and within an explicit
allowed root supplied by the controller. P113 fixtures use
`runtime/agent_jobs/p113_fixture`. Absolute paths, drive-qualified paths,
parent traversal, empty paths, and paths outside that root are rejected before
Codex's patch handler receives a custom-tool event. The adapter may validate
the declared patch paths; Codex remains the mutation authority.

## Stream and history contract

For the accepted call only, the adapter emits one `custom_tool_call` named
`apply_patch`, preserving the provider's `id` and `call_id`, with the decoded
patch as `input`. On the follow-up request it converts precisely that custom
call and its `custom_tool_call_output` back to `function_call` and
`function_call_output`; the original `id`, `call_id`, name, patch bytes, tool
result, and ordering are unchanged. The follow-up has `tools: []` and
`tool_choice: "none"`; it cannot invite another call.

## Threat model and fail-closed outcomes

| Threat | Required handling |
| --- | --- |
| Provider emits unsupported tool, invalid JSON, a non-object, extra argument, or non-string patch | Reject with `malformed_provider_call`; no custom-tool input completion or mutation. |
| Provider streams more than one call or retries after rejection | Reject with `call_limit_exceeded`; no mutation after the first observed call. |
| Patch targets an absolute, traversing, drive-qualified, or outside-root path | Reject with `path_outside_allowed_root`; no custom event or mutation. |
| Provider reuses or loses `id` / `call_id`, or history output does not pair with the call | Reject with `history_round_trip_invalid`; do not issue the follow-up. |
| Unexpected input tool or provider event | Reject with `unsupported_tool_or_event`; do not pass it through. |

The adapter records only a sanitized verdict, case identifier, event identity,
and failure code. Provider headers, prompts, raw Responses streams, and patch
contents remain ignored runtime evidence.

## Acceptance separation

- `quality_validated_candidate`: P113.2 passes the deterministic fixture
  validator and a native patch has the expected ignored-target diff.
- `protocol_accepted_candidate`: it also proves one call, containment, and
  round-trip identity from fresh raw evidence.
- `economics_usable`: out of scope for P113.1 and P113.2; P107 remains parked.

## Deterministic fixture gate

`benchmarks/p113_function_tool_adapter/adapter_contract_fixtures.json` is the
public-safe fixture corpus. Run:

```powershell
python scripts/validate_p113_function_tool_adapter_contract.py
```

The validator checks fixture integrity and invariant coverage. P113.2 must add
adapter-facing tests that execute the same cases; changing the fixture to make
an adapter pass is not acceptance evidence.
