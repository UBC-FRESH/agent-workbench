# P114 C2 Luna Worker Capability Inventory

Status: observed baseline for P114 adapter work.

Source session: `019f62cf-02e8-7630-a8f1-c227dbd46e46`, the `gpt_luna_worker`
child in the preserved C2 lane archive
`runtime/agent_jobs/p107_2_lane2_luna_supervisor_luna_worker/raw_sessions/luna_worker.jsonl`.

## Observed invocation surface

| Capability | C2 evidence | P114 state |
| --- | --- | --- |
| bounded shell execution | one completed native `exec` custom call using `tools.shell_command`; it read the fixed source and contract from the literal workspace root | R5 now proves one translated native read command; next prove the exact C2 `exec` envelope with bounded workdir and read-only command policy |
| native patch | not invoked by this C2 task | P113/R4 proved one native `apply_patch`; retain as the next productive capability after C2 `exec` parity |
| tool-result continuation | C2 consumed the shell result and returned eight JSONL records | R5 proves one shell result and terminal response; R6 must prove the continuation boundary before a combined read/patch claim |
| skills | no skill invocation occurred | not a P114 runtime requirement until a frozen C2 workload actually invokes a named skill |
| file, browser, GitHub, provider, or subagent tools | no invocation occurred | out of scope for this parity gate |

The profile exposed a larger skill catalog, but availability is not evidence of
use. P114 will implement the observed C2 surface first, then add only
capabilities demonstrated by a frozen C2 workload.

## Build order

1. Reproduce the exact C2 `exec` request shape: approved PowerShell command,
   literal in-worktree `workdir`, one native command completion, and terminal
   worker output.
2. Generalize that proof into a fail-closed command policy limited to the
   ticket-declared command list and literal worktree.
3. Reintroduce the already-proven native patch path after the successful C2
   shell proof, with no shell-write substitute accepted.
4. Add history/repair and declared validation only after the preceding native
   capabilities pass independently.
5. Add a skill only when a fresh, frozen C2 worker session actually invokes it;
   record its exact name, inputs, outputs, authority, and deterministic proof.
