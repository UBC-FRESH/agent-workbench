# Sockeye loopback bridge for a private vLLM provider

This note captures the concrete loopback-bridge pattern used for the Sockeye-backed vLLM provider so later agents do not need to rediscover the same SSH-forwarding setup from first principles.

## What the local client needs

The custom Copilot model entry points at a local URL, and its `id` must match
the server's `--served-model-name` exactly:

```json
{
  "id": "qwen2.5-coder-7b-instruct",
  "configId": "sockeye-qwen25-coder-7b",
  "displayName": "Qwen2.5-Coder 7B Instruct (Sockeye)",
  "baseUrl": "http://127.0.0.1:18001/v1",
  "apiMode": "openai",
  "context_length": 32768
}
```

That means the client must have a real local listener on port `18001`, even though the model server itself is private and runs on the Sockeye side.

## Authentication prerequisite

Sockeye requires keyboard-interactive (MFA) authentication, which an agent
cannot complete. Access works only by reusing the multiplexed master session
that the human already authenticated. Full rules are in
[notes/clusters/sockeye.md](../clusters/sockeye.md).

Always start here:

```bash
ssh -O check sockeye
```

- `Master running (pid=NNNN)` → zero-auth access; proceed.
- no socket → stop and ask the human to run `ssh sockeye` and complete MFA.

## Architecture

vLLM binds to **compute-node loopback** only. The login node cannot reach that
directly, so the stack borrows the job's own namespace with `srun --overlap`.
Three hops, each independently breakable:

```
laptop 127.0.0.1:18001
   |  ssh -O forward (local forward on the live master)
login node 127.0.0.1:18125        <- p124-bridge.py
   |  srun --overlap into the running allocation
compute node 127.0.0.1:8000       <- vllm serve
```

The forward is **not** symmetric: local `18001` maps to remote `18125`.

## Scripts (on the cluster, under `vllm-deployment/runtime/`)

| Script | Runs on | Purpose |
| --- | --- | --- |
| `p124-serve-in-job.sh` | compute node | stages the model to `$SLURM_TMPDIR`, prepares the sm70 runtime, runs `vllm serve` |
| `p124-bridge.py` | login node | relays `18125` into the allocation; **auto-discovers** the job id |
| `p124-autostart.sh` | login node | waits for the allocation, starts vLLM, then starts the bridge |

The allocation itself is held by an sbatch script whose payload is
`sleep infinity`. That is deliberate: the allocation outlives any individual
server restart, so the launcher can be re-run via `srun --overlap` without
losing the (expensive) GPU reservation.

## Normal bring-up

```bash
# 1. submit the allocation (from the cluster scratch dir)
sbatch sockeye-gpu32-4gpu-24h.sh

# 2. start the watcher; it does everything else when the job lands
cd vllm-deployment/runtime
nohup setsid ./p124-autostart.sh > p124-autostart.log 2>&1 &

# 3. once the watcher reports SUCCESS, add the client forward
ssh -O forward -L 18001:127.0.0.1:18125 sockeye
```

Progress lives in `p124-autostart.log`, `p124-vllm.log`, `p124-bridge.log`.

## PoC flaws that were fixed (2026-07-30)

These were real footguns in the first prototype. Do not reintroduce them.

| Flaw | Why it hurt | Fix |
| --- | --- | --- |
| Bridge hardcoded `--jobid=12409346` | silently dead the moment that job ended; every new job needed a hand-edit | job id is discovered from `squeue` at runtime and re-resolved on error |
| Bridge sent `srun` stderr to `/dev/null` | failures were invisible; looked identical to a dead model | stderr is captured to `p124-bridge.log` |
| Bridge tunneled blindly with no allocation | connections hung instead of failing | refuses with `no running allocation` |
| `--tensor-parallel-size 4` for a 7B model | 15G fp16 fits one 32G V100; TP=4 added NCCL/multiproc failure modes for nothing | TP=1 |
| Staging and launching were manual `srun` steps | with multi-hour queue waits, a human had to be present when the job landed | `p124-autostart.sh` does it unattended |
| Compat wheel surgery re-ran on every start | slow, and every restart re-risked a fragile step | guarded by a `/work/.compat-ok` marker |
| No tool-call parser | Copilot agent mode could not parse tool calls | `--enable-auto-tool-choice --tool-call-parser hermes` |
| Client claimed 131072 context, server served 16384 | oversized prompts rejected at request time | server `--max-model-len 32768`, client `context_length` matched |

## Client settings must match the server

The Copilot custom-model `id` must equal vLLM's `--served-model-name`
(`qwen2.5-coder-7b-instruct`). A mismatch fails the request even with a
perfect tunnel. Likewise `context_length` must not exceed `--max-model-len`.

## Verification steps

```bash
ss -ltn | grep ':18001'
curl -s -m 5 http://127.0.0.1:18001/v1/models
```

A successful response from `/v1/models` means the loopback bridge is working.

## Common failure modes

| Symptom | Real cause | Fix |
| --- | --- | --- |
| `Permission denied (keyboard-interactive)` | SSH master dead or bypassed by extra flags | human re-auths with `ssh sockeye` |
| `mux_client_forward: forwarding request failed` | same as above | `ssh -O check sockeye` first |
| `no running allocation` in bridge log | job ended or not started yet | check `squeue`; resubmit if needed |
| `http=000` from remote port 18125 | GPU job gone, or vLLM still loading (takes minutes) | check `p124-vllm.log` |
| connection refused on local 18001 | forward not installed | `ssh -O forward -L ...` |
| 404 / model-not-found | client `id` != `--served-model-name` | align the settings entry |

A live bridge process does **not** mean a live model. The bridge outlives the
Slurm allocation, so it keeps listening with nothing behind it.

## `pkill -f` self-match warning

Running `pkill -f p124-bridge.py` inside an `ssh` one-liner kills the remote
shell too, because the pattern matches that shell's own command line. The
session dies with exit 255. Use a bracket pattern (`'[p]124-bridge'`) when
matching from a command line that contains the string.

## Practical rule of thumb

Diagnose in this order, and never wait on a hanging command:

1. SSH master alive?
2. Slurm job running?
3. Remote port 18125 answering?
4. Local forward present?
5. Client URL responding?

Every check returns in seconds. If something hangs, it is wrong — kill it and
read the error instead of waiting.
