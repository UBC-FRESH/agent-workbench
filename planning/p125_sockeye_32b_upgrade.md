# P125.x — Sockeye 32B Dense Model Upgrade

Parent issue: #769
Child issue: **not yet filed** — intended ID P125.3. GitHub write tools
(`mcp_github-mcp-se_create_issue`) are disabled in this environment; the body
is drafted and ready to file once they are enabled.
Branch: `feature/p125-popup-provider-framework`
Status: planned — not started
Author context: developer green-lit 2026-07-31 after the MoE route was ruled out

## Why

The Sockeye provider currently serves `qwen2.5-coder-7b-instruct` on **one**
V100 while the job holds **four**. Measured startup profile (job 12427107):

| Component | Size |
| --- | --- |
| model weights | 14.25 GiB |
| PyTorch activation peak | 4.35 GiB |
| non-torch | 0.09 GiB |
| KV cache | 9.87 GiB |
| **total** | **28.56 GiB of 32 GiB (1 GPU)** |

GPUs 1–3 sat at 4 MiB / 0% for the life of the job. Of 128 GiB allocated VRAM,
~29 GiB is used.

Two open defects trace back to model capability, not configuration:

- **Tool calling does not work.** Config is correct end-to-end
  (`--enable-auto-tool-choice --tool-call-parser hermes`, and the checkpoint's
  template emits `<tools>` plus explicit `<tool_call></tool_call>`
  instructions). The 7B at fp16 still returns markdown-fenced JSON, so
  `tool_calls` is empty. Recorded as defect 9, `tool_calling_verified: false`.
- **Undersized for the hardware.** A 32B dense model fits the *existing*
  allocation at TP=4.

`Qwen2.5-Coder-32B-Instruct` is the flagship of this family, is **dense** (so
the `_moe_C.topk_softmax` block that killed both MoE candidates does not
apply), and is far more likely to emit correct tool-call format.

## Goal

Serve `Qwen2.5-Coder-32B-Instruct` on Sockeye at TP=4, and determine by
measurement whether it emits valid `tool_calls`.

Success is a *measurement*, not an outcome. "32B also fails tool calling" is a
valid, recordable result that closes the question.

## Non-goals

- Throughput, latency, or quality benchmarking.
- Any change to the Slurm allocation shape (see "Deferred" below).
- Any change to `settings.json` beyond the model entry needed to test.
- Promoting Sockeye to a Coordinator-tier endpoint. Even at 32K context it is
  Worker-tier; the local Ornith is configured at 250K.

## Known facts (verified 2026-07-31)

| Fact | Value | How verified |
| --- | --- | --- |
| Valid TP degrees | 1, 2, 4 | `heads: 32`, `kv_heads: 4`; TP=3 excluded |
| vLLM version | 0.10.0, custom sm70 build, Apptainer | `llm_engine.py` init log |
| Engine | V0 (Compute Capability < 8.0 forces fallback) | startup warning |
| Scratch free | 4.9T, used 131.8G, no hard quota | `df` / `lfs quota` |
| SLURM_TMPDIR free | 1.5T, 27G used | `df $SLURM_TMPDIR` |
| 7B download method | `huggingface_hub`, 14 files, ~42s | `p124-qwen2.5-coder-download.log` |
| Current job | 12427107, ~8h22m elapsed of 24h | `squeue` |

## Risks

**R1 — sm70 kernel coverage for 32B is unverified.** This is the same class of
assumption that sank the 30B MoE. Registry presence proved the architecture was
*recognized*, not that kernels were *compiled*. Qwen2 dense is a much older,
better-trodden path than Qwen3 MoE, but it is still unproven on this build.
*Mitigation:* R1 is settled by the load itself. Do not stage 64GB before the
architecture check in Step 1.

**R2 — TP=4 is unproven on this stack.** Every successful run here has been
TP=1. The serve script header explicitly warns TP>1 "added NCCL/multiproc
failure modes". The one archived TP=4 attempt failed — on MoE kernels, not
NCCL, so it is not evidence either way about NCCL.
*Mitigation:* Step 4 is the first real TP=4 test. Capture NCCL errors
distinctly from kernel errors.

**R3 — outage window.** 32B at TP=4 needs all four GPUs, so qwen2.5 must stop.
Dual-port is impossible (established: only 3 GPUs free, and TP=2 leaves <1GiB
for KV cache). There is no zero-downtime path.
*Mitigation:* qwen2.5 stays staged in `$SLURM_TMPDIR` (15G, do **not** delete).
Rollback is re-running the existing `p124-serve-in-job.sh` unchanged.

**R4 — walltime.** ~15h remain on job 12427107. Download + stage + load must
fit, or the job ends mid-work.
*Mitigation:* Step 0 re-checks remaining walltime. Abort if under 3h.

**R5 — context/KV tradeoff.** 32B fp16 ≈ 64 GiB over 4×32 GiB leaves ~16 GiB
weights per GPU, so less KV headroom per GPU than the 7B enjoyed. `max_model_len`
may need to drop below 32768.
*Mitigation:* Step 4 starts at 16384 and raises only if the profile allows.

## Plan

### Step 0 — Preconditions (read-only, no risk)

- [ ] Confirm job 12427107 still RUNNING with >3h walltime remaining
- [ ] Confirm qwen2.5 still serving and `verify.sh` passes (rollback baseline)
- [ ] Record current `squeue`, `nvidia-smi`, and endpoint state as the
      restore-target evidence

Abort if walltime is short. Do not start a 64GB download against a job about to
expire.

### Step 1 — Architecture support check (read-only, no risk)

- [ ] Confirm `Qwen2ForCausalLM` is in the vLLM 0.10.0 registry
- [ ] Confirm `transformers 4.53.3` in the container resolves the 32B config

**Gate: if the architecture is absent, STOP.** Record the finding and close the
question. Do not download.

This step exists because skipping its equivalent is what cost us the MoE
attempt. It is cheap; run it first.

### Step 2 — Download to scratch (non-destructive, no downtime)

- [ ] Download `Qwen/Qwen2.5-Coder-32B-Instruct` to
      `/scratch/st-gep-1/gep/vllm-deployment/models/qwen2.5-coder-32b-instruct`
      using the same `huggingface_hub` method as the 7B
- [ ] Verify shard count and total size (~64GB) against the repo manifest
- [ ] Confirm `config.json` reports `Qwen2ForCausalLM` and
      `num_attention_heads` / `num_key_value_heads` divisible by 4

qwen2.5-7B keeps serving throughout. Interruptible with no consequence.

### Step 3 — Stage to node-local (non-destructive, no downtime)

- [ ] rsync scratch → `$SLURM_TMPDIR/p124-models/qwen2.5-coder-32b-instruct`
- [ ] Write the `.staged` marker only on success
- [ ] Verify **both** models present; 7B must remain staged for rollback

Reuse the pattern in `p125-stage-30b.sh`. Note that script was killed with
`pkill` in an ssh one-liner, which ate the ssh session — see
`notes/clusters/sockeye.md`. Prefer `scancel` on the step, or run
`pkill` inside a script rather than inline.

### Step 4 — Cut over (DOWNTIME BEGINS)

- [ ] Stop the vLLM serving qwen2.5 inside the allocation
- [ ] Launch 32B: TP=4, `--dtype half`, `--gpu-memory-utilization 0.90`,
      `--max-model-len 16384`, `--enable-auto-tool-choice`,
      `--tool-call-parser hermes`, `--served-model-name qwen2.5-coder-32b-instruct`
- [ ] Watch for the memory-profiling line and record weights / activation /
      KV-cache split
- [ ] Distinguish failure modes explicitly:
      - missing kernel symbol → R1, architecture unsupported → rollback
      - NCCL / multiproc error → R2, TP problem → consider TP=2 (likely OOM)
      - OOM → lower `--gpu-memory-utilization` or `--max-model-len`

The allocation is held by `sleep infinity`, so the GPUs are **not** lost on a
failed launch. Only the server is affected.

### Step 5 — Verify (the actual point of this work)

- [ ] `/v1/models` reports `qwen2.5-coder-32b-instruct`
- [ ] `verify.sh` passes against the bridge port
- [ ] **Tool-call test** — send a `read_file` tool definition and assert
      `tool_calls` is **non-empty**. This is the decisive measurement.
- [ ] Update `tool_calling_verified` in the launch profile with the result,
      pass **or fail**
- [ ] If tool calls work: update the Keklick `settings.json` entry — `id` must
      equal `--served-model-name` exactly, `context_length` must match
      `--max-model-len` (defect 7; the current entry says 16384 against a
      32768 server)

### Step 6 — Rollback (only if Step 4 or 5 fails)

- [ ] Stop the 32B server
- [ ] Re-run `p124-serve-in-job.sh` unchanged — 7B is still staged
- [ ] Confirm `verify.sh` passes
- [ ] Record the failure mode in `notes/clusters/sockeye.md`

Rollback must be exercised on any failure. Do not leave the provider down.

### Step 7 — Record

- [ ] Update `notes/clusters/sockeye.md` with the outcome either way
- [ ] Add/update the launch profile
      `playbooks/popup_provider/profiles/qwen25-coder-32b.yaml`
- [ ] Update the target descriptor if TP or memory findings change it
- [ ] `CHANGE_LOG.md` entry with Quality / Protocol / Economics separated

## Stop conditions

Stop and escalate to the developer if:

- Step 1 shows the architecture is unsupported (question closes, no download)
- Step 4 fails twice — one bounded repair, then stop, per `AGENTS.md`
- Rollback does not restore a working provider
- Remaining walltime drops below 1h mid-procedure

## Deferred (explicitly out of scope)

- **Right-sizing the allocation.** Billing is `MAX_TRES` over
  `CPU=1.0,Mem=5.00G,gres/gpu=6.0`; the 120G memory request bills 600 while 4
  GPUs bill 24. Memory is the cost lever, not GPUs — and this work *uses* all
  four GPUs, so the GPU count is no longer waste. Revisit memory sizing on the
  next allocation, not this one.
- **Preflight gates.** `preflight/check.py` still models VRAM only: no kernel
  support gate (defect 10), no allocation cost gate (defect 11). This plan
  performs those checks manually.
- **Coordinator-tier endpoint.** Out of reach at this context length.

## Evidence to retain

Startup memory profile, the tool-call request/response pair (both the
pre-change 7B failure and the 32B result), `verify.sh` JSON output, and the
final `squeue` / `nvidia-smi` state. Keep raw logs local; promote only
sanitized findings.