# P114.3 Scripted Host Proof Stop Record

Status: stopped pending maintainer review on 2026-07-17. P107 remains parked.

## Attempt ledger

| Attempt | Result | Classification |
| --- | --- | --- |
| `p114_host_proof_20260717_r1` | The harness invoked `codex exec -s workspace-write`; the known broken Windows sandbox setup failed before native tool execution. The adapter and scripted provider received local requests, but the detached-worktree target remained `before`. | invalid host-deployment observation; harness defect |
| `p114_host_proof_20260717_r2` | The repaired route bypassed the Windows sandbox, but the PowerShell `Start-Process` invocation split the prompt and Codex rejected a prompt word as an `exec` subcommand. No scripted provider or adapter request occurred; the target remained `before`. | invalid host-deployment observation; harness defect |

Both attempts used only run-local loopback provider and adapter processes. Neither
contacted Ollama, changed user configuration, or produced a model-quality,
quality, protocol, or economics observation.

## Stop decision

P114 preregistered one initial host-deployment attempt and one evidence-based
repair. Both are invalid before the native host tool lifecycle. Do not launch a
third P114.3 host attempt under the present protocol.

The runner has been corrected statically to preserve the prompt as one Windows
process argument and to refresh the child process before reading its exit code.
That code correction is not live evidence. A maintainer may authorize a new
bounded P114.3 attempt only by recording a fresh restart decision, its budget,
and the new run identifier. Until then, P114.3 is unproven, P114.4/P114.5 are
not authorized, and P107 remains parked.
