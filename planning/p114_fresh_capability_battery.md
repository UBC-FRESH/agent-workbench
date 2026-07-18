# P114 Fresh Capability Battery

Status: accepted for the direct-MWE and Cloudflare-authenticated CLI-parent C4
routes on 2026-07-17. It does not resume P107 or make an economics claim.

## Frozen row contract

Each row is a new `codex exec` session with a run-local `CODEX_HOME`, literal
P114 worktree, the core adapter, and the same five-call sequence:

1. declared native read;
2. native defect patch;
3. declared validation returning exit 17;
4. native repair patch;
5. declared final validation returning exit zero.

Every accepted row must retain the ticket, result, heartbeat, archive manifest,
deployment proof, adapter logs, Codex events, terminal marker, and target
content. It must show three command executions with exit codes `0, 17, 0`, two
native file changes, `after\n`, and its declared terminal marker. Shell writes
and extra tool calls invalidate the row.

## Rows

| Row | Run id | State |
| --- | --- | --- |
| 1 | `p114_core_adapter_envelope_r20` | passed |
| 2 | `p114_core_adapter_battery_r21` | passed |
| 3 | `p114_core_adapter_battery_r22` | passed |

The deterministic verifier accepted all three rows and recorded three distinct
fresh thread IDs in ignored
`runtime/agent_jobs/p114_direct_mwe_battery_report.json`. The direct-MWE
battery remains distinct from qualification observations.

## C4 CLI-parent rows

The frozen `ollama_qwen_coder_worker` repeated the same five-call contract
through the accepted CLI-parent route. Each run loaded the documented
Cloudflare Access service-token environment, used `fork_context:false`, and
restored the bridge and temporary environment afterward.

| Row | Run id | Child session | State |
| --- | --- | --- | --- |
| 1 | `p114_c4_capability_battery_r23` | `019f7262-ec00-7b70-9b3a-601342d2ee86` | passed |
| 2 | `p114_c4_capability_battery_r24` | `019f7263-7922-7f12-9e72-44fd6797b878` | passed |
| 3 | `p114_c4_capability_battery_r25` | `019f7264-0063-7923-8a3b-024d51e591ac` | passed |

The C4 verifier accepted all three rows in ignored
`runtime/agent_jobs/p114_c4_capability_battery_report.json`. Each raw child
session records exactly `shell_command -> apply_patch -> shell_command ->
apply_patch -> shell_command`, exit codes `0, 17, 0`, target `after\n`, and
`P114_C4_BATTERY_DONE`. This is a `quality_validated_candidate` and
`protocol_accepted_candidate` for P114.4's CLI-parent route. It makes no
economics claim and does not assert that the old VS Code-parent dispatch host
has been repaired.
