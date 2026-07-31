# Sockeye (UBC ARC) cluster notes

## READ THIS FIRST — how SSH to Sockeye actually works

Sockeye requires **keyboard-interactive (MFA) authentication**. A coding agent
**cannot** complete that challenge. Any command that forces a *new* SSH
connection will fail with:

```text
gep@sockeye.arc.ubc.ca: Permission denied (keyboard-interactive).
```

This is **not** a broken key, a VPN problem, or a vLLM problem. It means the
command bypassed the existing authenticated session.

### The mechanism that makes it work: connection multiplexing

`~/.ssh/config` already defines:

```text
Host sockeye
  HostName sockeye.arc.ubc.ca
  User gep
  IdentityFile ~/.ssh/id_ed25519_sockeye
  IdentitiesOnly yes
  PreferredAuthentications publickey,keyboard-interactive
  ControlMaster auto
  ControlPath ~/.ssh/sockets/%r@%h:%p
  ControlPersist 8h
```

The human authenticates **once** (MFA included). That creates a master socket at
`~/.ssh/sockets/gep@sockeye.arc.ubc.ca:22`, which stays alive for 8 hours. Every
later `ssh sockeye` reuses it and needs **no authentication at all** — and
returns essentially instantly.

### Step 0 for every agent, every time

```bash
ssh -O check sockeye
```

- `Master running (pid=NNNN)` → you have zero-auth access. Proceed.
- `Control socket connect(...): No such file or directory` → **STOP.** Ask the
  human to run `ssh sockeye` in a terminal and complete MFA. Do not retry, do
  not improvise, do not sit and wait.

### Keeping the master alive (2026-07-30)

`ControlPersist` is now `yes` for all cluster hosts, so a newly created master
never expires on its own. Two things follow:

- `ControlPersist` is fixed **when the master starts**. Editing the config does
  not extend a master that is already running — it only affects the next one.
- The value is an **idle** timeout, so any periodic use resets it. A local
  keepalive loop (`ssh sockeye true` every 15 min, marker string
  `sockeye-mux-keepalive`) keeps a session alive across long queue waits
  without another MFA prompt.

Check for it with `pgrep -af sockeye-mux-keepalive` before assuming a master
died of old age.

### Rules

**DO** use the bare alias, with a timeout so failure is instant:

```bash
timeout 25 ssh sockeye 'hostname; squeue -u $USER'
```

**DO NOT** add option overrides. These defeat multiplexing and force a fresh
authentication that will be denied:

```bash
# ALL OF THESE BREAK IT:
ssh -F /home/gep/.ssh/config -o UserKnownHostsFile=/dev/null sockeye ...
ssh -o StrictHostKeyChecking=accept-new sockeye ...
ssh gep@sockeye.arc.ubc.ca ...        # different alias, may miss the socket
ssh -N -L 18001:127.0.0.1:18125 sockeye   # spawns a NEW connection -> denied
```

### Port forwarding without re-authenticating

Never open a second SSH process for a tunnel. Inject the forward into the
**live master** instead — it is instant and needs no auth:

```bash
# add a local forward
ssh -O forward -L 18001:127.0.0.1:18125 sockeye

# verify locally
ss -ltn | grep ':18001'
curl -s -m 5 http://127.0.0.1:18001/v1/models

# remove it when done
ssh -O cancel -L 18001:127.0.0.1:18125 sockeye
```

If `ssh -O forward` prints `mux_client_forward: forwarding request failed`
followed by a `Permission denied (keyboard-interactive)` line, the master was
dead or bypassed — go back to Step 0.

## Access and identity

- Host alias: `sockeye` → `sockeye.arc.ubc.ca`
- User: `gep`
- Key: `~/.ssh/id_ed25519_sockeye` (`IdentitiesOnly yes`)
- Second factor: required on every *new* connection; unavoidable for agents
- Observed login node: `login02`
- Project scratch: `/scratch/st-gep-1/gep/`

## MoE models cannot run on this stack (observed 2026-07-31)

The Sockeye V100s are sm70/Volta, which forces a bespoke vLLM **0.10.0** build
running inside an Apptainer sandbox. That build was compiled **without MoE
kernels**. Any mixture-of-experts model fails at engine startup:

```
AttributeError: '_OpNamespace' '_moe_C' object has no attribute 'topk_softmax'
```

`topk_softmax` is the expert-routing op. The failure occurs during
`determine_num_available_blocks` — startup profiling, before a single token is
served. Evidence: `runtime/p124-qwen3-coder-vllm.log`.

Also note `Compute Capability < 8.0 is not supported by the V1 Engine.
Falling back to V0.`

Consequences for model selection here:

| Model | Status |
| --- | --- |
| `qwen2.5-coder-7b-instruct` (dense) | works — currently served |
| `qwen3-coder-30b-a3b-instruct` (MoE) | **blocked** — `_moe_C.topk_softmax` missing |
| `qwen3-coder-next` (MoE, Qwen3Next) | **blocked** — arch absent from the 0.10.0 registry entirely |

Both MoE checkpoints are staged on scratch but are not loadable. Do not spend
staging time on them.

**Registry presence does not imply kernel support.** `Qwen3MoeForCausalLM`
*is* in the 0.10.0 registry; the architecture is recognized, the kernels are
not compiled. Check both before planning a swap.

## P124 provider topology (observed 2026-07-30)

The serving path has three independent layers. Diagnose them in this order.

| Layer | Where | Evidence |
| --- | --- | --- |
| GPU job holding the allocation | Slurm compute node (e.g. `se294`) | `squeue -u $USER` |
| vLLM server | compute node `127.0.0.1:8000` | `runtime/p124-vllm.log` |
| Loopback bridge | login node `127.0.0.1:18125` | `runtime/p124-bridge.py` |
| Client forward | laptop `127.0.0.1:18001` | `ss -ltn \| grep 18001` |

The full provider stack, its scripts, and its failure modes are documented in
[notes/operations/sockeye-loopback-bridge.md](../operations/sockeye-loopback-bridge.md).

The local Copilot custom model entry (`sockeye-qwen25-coder-7b`) points at
`http://127.0.0.1:18001/v1`, so the client forward must map **18001 -> 18125**.

## Scheduler behaviour (observed 2026-07-30)

- Account `st-gep-1-gpu`, partition `gpu`, 32 GB V100 nodes.
- GPU queue is heavily contended. A 4-GPU / 24 h job submitted at ~22:50 was
  scheduled to start **the next day at 18:05** on `se294`.
- `sbatch --test-only` estimates for *new* submissions were ~6 days out, i.e.
  **worse** than an already-queued job's backfill slot. An existing pending job
  has accrued priority; do not cancel and resubmit hoping for a better slot.
- `sbatch --test-only` requires `--chdir`, otherwise it fails with
  "Job cannot be submitted without the current working directory specified".
- Jobs that end with `State=TIMEOUT` in `sacct` simply used their full
  walltime. That is normal completion, not a crash.

Because queue waits are long, start the unattended watcher
(`p124-autostart.sh`) right after submitting rather than planning to bring the
provider up by hand.

### A live bridge does NOT mean a live model

Observed state on 2026-07-30:

- bridge process up for ~13h, listening on `127.0.0.1:18125`
- `squeue -u $USER` returned **no jobs**
- `curl http://127.0.0.1:18125/v1/models` returned `http=000`

The bridge is a long-lived forwarder that outlives the GPU allocation. When the
Slurm job ends, the bridge keeps listening but has nothing behind it. So:

- `http=000` on 18125 → the **GPU job is gone**, restart the allocation
- connection refused on 18001 → the **client forward is missing**, add it
- `Permission denied (keyboard-interactive)` → the **SSH master is dead**

## Triage order (fastest to slowest)

1. `ssh -O check sockeye` — master alive?
2. `timeout 25 ssh sockeye 'squeue -u $USER'` — is a GPU job running?
3. `timeout 25 ssh sockeye 'curl -s -m 5 -o /dev/null -w "%{http_code}\n" http://127.0.0.1:18125/v1/models'` — is the model answering on the login node?
4. `ss -ltn | grep ':18001'` — does the local forward exist?
5. `curl -s -m 5 http://127.0.0.1:18001/v1/models` — end-to-end.

Every one of these returns in seconds. If a command hangs, it is wrong — kill it
and re-read the error rather than waiting.

## Durable takeaway

Sockeye access is a **multiplexing** problem, not a credentials problem. The
human supplies MFA once; agents ride the existing master socket and inject
forwards with `ssh -O forward`. Adding `-o` flags, changing the alias, or
spawning `ssh -N -L` throws away that session and guarantees failure.
