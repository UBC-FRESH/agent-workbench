# P107 C4 Package-Route Re-entry Packet

Status: ready for P114 closeout; do not start a comparable P107 run until the
P114 branch and parent issue have completed their governed closeout.

## Decision

The baseline `qwen3-coder:latest` C4 Worker may enter P107 through the fresh
Codex CLI-parent package-MCP route after P114 closes. This is a transport and
authority decision. It does not predict that the Worker will solve a workload
deterministically.

## Admitted route

- One fresh Codex CLI parent rooted in the literal run worktree.
- Exactly one `ollama_qwen_coder_worker` child with `fork_context:false`.
- Deferred discovery followed by namespaced package MCP calls only.
- Grant-bound `read_file`, `apply_patch`, and `exec` tools with root
  containment, policy/outcome JSONL logs, and byte-for-byte config and Worker
  role restoration.

The three-row P114.4 package battery proves bounded package `exec` and
`apply_patch` through the route. P114.5 r10 and r12 independently prove the
task-specific data-plane profile: the Worker discovered and used namespaced
`read_file`, `apply_patch`, and `exec`; attempted out-of-grant commands were
denied rather than executed; changed paths stayed in grant; and restoration
completed.

## Verdict separation

| Dimension | Verdict | Evidence use |
| --- | --- | --- |
| Bridge/protocol | admitted | P114.4 battery plus P114.5 r10 and r12 raw route, MCP, and restoration evidence |
| P107 workload quality | not established by P114 | r10/r12 frozen-workload failures are retained as ordinary Worker-quality observations |
| Economics | not assessed | no accepted P107 checkpoint/token-ledger boundary exists |

An out-of-grant request is evidence that the bridge denied excess authority.
It is not evidence that the route silently executed it, and it does not turn a
P107 workload-quality result into a bridge failure.

## P107 authorization and limits

P107 may run its baseline C4 configuration suite only after P114 governed
closeout. Preserve the exact role, provider, route, worktree identity, raw
child trace, bridge event log, and restoration evidence for every row.

P107 must report task quality independently from bridge/protocol behavior.
P107.2 economics remains inactive until a clean, accepted checkpoint and
token-ledger boundary is captured. P108 remains inactive. Every additional
C4+ profile needs its own fresh package-route protocol admission observation
before entering a comparison.
