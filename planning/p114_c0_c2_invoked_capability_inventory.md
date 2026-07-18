# P114 C0-C2 Invoked Capability Inventory

Status: evidence inventory for the Codex-Ollama adapter v1 scope decision.

Evidence sampled from preserved C0, C1, and C2 session manifests and raw
Coordinator, Advisor, Supervisor, and Worker session JSONLs. This is an
invocation inventory, not a list of tools merely advertised in session context.

| Capability | Roles/configurations with observed use | Adapter relevance |
| --- | --- | --- |
| `exec` invoking `tools.shell_command` | C1/C2 Coordinator, Luna Supervisor, and Luna Worker; C2 worker used it to read its fixed source and contract | must-have worker capability |
| bounded command-result continuation | C1/C2 Workers consumed command output before returning their task result | must-have worker capability |
| native `apply_patch` | not invoked by the sampled C0-C2 comparison tasks; independently proven by P113/R4 | candidate must-have productive capability, after `exec` parity |
| `spawn_agent`, `wait_agent`, `send_input` | Coordinator/Supervisor control plane in native delegation runs | not part of the remote Worker adapter v1; preserve as host-side role control |
| named skill invocation | none observed in the sampled C0-C2 role sessions | not a v1 implementation requirement |
| browser, GitHub, provider/configuration, file, image, or MCP tool | none observed in the sampled C0-C2 role sessions | nice-to-have only if a frozen workload produces call evidence |

## Scope implication

The adapter v1 target is not every tool in a Codex catalog. It is a fail-closed
Worker data-plane bridge for ticket-declared shell commands, command-output
continuation, and native patching. Native delegation remains a host-side
Coordinator/Supervisor capability. Skills remain Codex session context and do
not need a provider-bridge implementation until a frozen task invokes one.

## Evidence set

- C0 Coordinator and Advisor manifests:
  `runtime/agent_jobs/p107_2_c0_20260715_9f3c1a/`.
- C1 Coordinator, Luna Worker, and Advisor manifests:
  `runtime/agent_jobs/p107_2_c1_20260716_024127/`.
- C2 Coordinator, Luna Supervisor, Luna Worker, and Advisor manifests:
  `runtime/agent_jobs/p107_2_c2_20260716_035628_937/`.
- Earlier bounded C2 Luna Worker archive:
  `runtime/agent_jobs/p107_2_lane2_luna_supervisor_luna_worker/raw_sessions/`.

## Advisor v1 scope decision

Must-have:

- ticket-declared shell execution through `exec`;
- literal CWD/path and command-policy enforcement;
- command-result continuation with output, exit code, and stable history;
- native `apply_patch`, with no shell-write substitute;
- declared validation through the shell route; and
- a fresh composite read-to-patch-to-validate acceptance test.

Nice-to-have/deferred:

- repair/retry workflows beyond basic continuation;
- browser, GitHub, image, file, MCP, provider, and configuration tools;
- unobserved shell or patch variants;
- native delegation tools, which remain host-side Coordinator/Supervisor
  controls; and
- skills, which remain session context until a frozen Worker workload invokes
  one.
