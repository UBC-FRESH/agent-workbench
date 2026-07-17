# P114.2 Offline Multi-Tool Bridge Conformance

Status: completed offline on 2026-07-17. This is not a live Worker result and
does not qualify C4 or resume P107.

## Implemented capability surface

`agent_workbench.p114_capability_tool_adapter` is a separate P114 adapter. It
does not alter P113's accepted one-tool control. It accepts only two upstream
function names:

- `apply_patch`, translated to native Codex `apply_patch`; and
- `exec`, translated to native Codex `exec` containing a bounded
  `tools.shell_command` request.

The adapter does not execute a shell command or apply a patch. Codex remains
the authority for both. `exec` requires a nonempty command, an in-worktree
directory, and a timeout from 1 through 120,000 milliseconds. The bridge
rejects unsupported calls, malformed arguments, path escapes, unknown history,
and additional tool injection before emitting a native tool completion.

## Deterministic evidence

The unit and clean-process loopback tests cover the preregistered P114.2
interface:

| Capability | Offline evidence |
| --- | --- |
| repository read and declared shell validation | `exec` function converts to a bounded native `tools.shell_command` program |
| native patch | strict `patch` and observed freeform `command` envelopes are validated and converted to native `apply_patch` |
| literal worktree containment | patch paths and `exec.workdir` are rejected outside the declared root |
| tool history and repair continuation | call IDs and original provider arguments are retained across a follow-up request while both functions remain available |
| unsupported tools | unknown functions and injected additional tools fail closed |
| host containment | the loopback host listens only on `127.0.0.1`, accepts only Responses paths, and contains no command-execution subprocess |

The clean-process test runs the loopback bridge as a separate Python process
against a local scripted provider. It establishes one sequential `exec` then
`apply_patch` response, returns native custom-tool events, and sends the
completed call/output history plus a repair message back through the bridge.
No external provider endpoint, credentials, user configuration, Codex session,
or model inference is involved.

## Remaining gate

P114.3 must prove this same route in a fresh Codex host session using a
scripted provider: run-scoped configuration, selected Worker role, model and
provider identity, literal worktree binding, native host execution, result
artifact flow, adapter teardown, and restoration of normal configuration.
Only after that proof may P114.4 be considered.
