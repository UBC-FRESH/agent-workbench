# P107.2 Ollama Worker Apply-Patch Compatibility

Status: resolved by P113; capability, containment, and bounded first-call
reliability accepted as candidates

## Purpose

This is the relevant P107.2 planning record for P113. It explains why P107 is
parked and what P113 must harden before a productive Ollama Worker can be
considered.

## Confirmed boundaries

- Native Codex children can run configured Ollama-backed models.
- A GPT-based child can patch through Code Mode, where custom `exec` invokes
  Codex's native patch handler.
- Code Mode sends `additional_tools`; the configured stock Ollama Responses
  provider rejects that input item before inference.
- Codex 0.144.2 rejects `apply_patch_tool_type: "function"`; the accepted
  value is `"freeform"`.
- Under supported non-Lite/freeform metadata, `shell_command` is advertised as
  a standard function while `apply_patch` is advertised as a custom tool.
- The provider rejects the separate `reasoning` field in this route unless it
  is removed by a narrow local adapter.

## Capability proof

A real Qwen native child completed a bounded ignored-file edit through this
specific path:

```text
Qwen standard function_call(apply_patch)
  -> narrow adapter
  -> Codex custom_tool_call(apply_patch)
  -> native Codex patch handler
  -> translated function-call history
  -> normal child completion
```

The raw child session recorded the standard function call, the translated
custom call, `patch_apply_end` with success, the expected diff, and a terminal
completion marker. No shell-writing fallback produced that accepted edit.

## Resolved P113 blockers

P113 established the following bounded adapter contract:

| Blocker | Required proof |
| --- | --- |
| First-call validity | Exactly one valid patch call, without malformed retries. |
| Containment | Outside-root paths, extra calls, and unsupported tools fail before mutation. |
| History fidelity | Call IDs and tool results round-trip deterministically through follow-up completion. |
| Failure behavior | Malformed provider output yields a precise fail-closed result. |

## Explicit non-solutions

- Do not build a general Responses, Code Mode, or MCP translation layer.
- Do not call shell-mediated writes native patch success.
- Do not resume P107 economics or activate P108 from the capability proof.
- Do not start a Codex fork unless the constrained adapter cannot meet the
  reliability and containment contract.

## P107 implication

P113 owns and completed the narrow `apply_patch(patch: string)` adapter,
deterministic translation/containment tests, and fresh native-worker reliability
evidence. Its final decision permits a separate P107-resume decision; it does
not run P107 economics or activate P108.
