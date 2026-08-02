# HPC vLLM agent provider — measured findings

Stop rediscovering this. Everything below was observed on real hardware during
one session, not inferred. Numbers come from instrumented runs; falsified
hypotheses are recorded alongside confirmed ones.

Scope: serving an OpenAI-compatible vLLM endpoint to VS Code Copilot custom
agents, from (a) a Slurm HPC allocation with H100 (Hopper, `sm_90a`) and (b) a
local workstation with a Blackwell-class GPU.

## Deployment gotchas (HPC, no system CUDA toolkit)

The `playbooks/vllm_blackwell/` profiles assume a workstation with a full
system CUDA 13 toolkit. On an HPC node with a CVMFS software stack, four
distinct failures appear in sequence. Each blocks startup.

| # | Symptom | Cause | Fix |
| --- | --- | --- | --- |
| 1 | `mkdir: cannot create directory '/srv/shared-data'` | Profiles hard-code a workstation shared mount | Override `VLLM_SHARED_CACHE`, `HF_HOME`, `HUGGINGFACE_HUB_CACHE`, `VLLM_CACHE_ROOT`, `TMPDIR` to scratch |
| 2 | `Cannot find any of ['quantization'] in the model's quantization config` | Old vLLM cannot parse a ModelOpt/NVFP4 checkpoint | Upgrade vLLM; the pinned cluster wheel was far behind |
| 3 | `nvrtc: error: failed to open libnvrtc-builtins.so.13.0` | Wheel-provided CUDA libs not on `LD_LIBRARY_PATH` | Add every `site-packages/nvidia/*/lib` dir to `LD_LIBRARY_PATH`; set `CUDA_HOME` to the `nvidia/cu13` package dir |
| 4 | `CUDA compiler and CUDA toolkit headers are incompatible` during FlashInfer JIT | FlashInfer JIT-compiles sampling kernels; headers mismatch on `sm_90a` | `VLLM_USE_FLASHINFER_SAMPLER=0` — falls back to the native sampler |

Additional version traps on an old vLLM: `--kv-cache-dtype bfloat16` is
rejected (only `auto`/fp8 variants), `--default-chat-template-kwargs` does not
exist, and the Qwen XML tool parser is absent. All three exist in current
versions. **A missing CLI flag usually means the vLLM version is wrong, not
that the option is unsupported in principle.**

`env-native.sh` hard-codes `python3.12` in its CUDA fallback path; the venv
built on the cluster used 3.11. Prefer discovering the version at runtime.

## Two process-management traps

**Slurm kills detached children.** Using `setsid`/`nohup` *inside* an `srun`
step does not survive: Slurm tears down the step cgroup when the step ends, so
the server dies silently and its log stays empty. Detach the **`srun` client on
the login node** instead:

```bash
setsid nohup ./serve-in-allocation.sh > serve.log 2>&1 < /dev/null &
```

**A stale SSH control master hangs every command.** With `ControlPersist` and no
`ServerAliveInterval`, a long-lived multiplexed connection can go half-dead:
TCP is broken but the master never notices, so new channels wait forever. Every
status command returns a timeout, including `ssh -O check`. This looks like a
cluster or job problem and is neither.

- Always set `ServerAliveInterval` / `ServerAliveCountMax` on long-lived hosts.
- Diagnose with `ps -o wchan` on the `[mux]` process, not by retrying.
- Status checks should be short, login-node-only commands with a hard
  `timeout`. Do not route routine status through `srun`; step creation blocks
  when the node is busy.

## Benchmark methodology — three ways to get fake numbers

1. **Prefix caching inflates concurrency results.** Identical prompts across
   concurrent requests hit the prefix cache, so prefill nearly vanishes. This
   produced an apparent 551 tok/s that fell to 445 tok/s with unique prompts —
   and made a higher concurrency look *faster* than a lower one, which is
   impossible. Randomize prompts per request when measuring.
2. **Streaming chunks are not tokens.** Counting SSE `delta.content` events
   undercounts badly, because multiple tokens arrive per chunk under load. This
   reported ~21 tok/s where the true value was ~93. Use `stream_options:
   {"include_usage": true}` and read `usage.completion_tokens`.
3. **Single runs contain transients.** One measurement showed a 57% regression
   that vanished on repeat; three repeats agreed within 0.2%. Repeat before
   believing any delta.

Use `ignore_eos: true` with a fixed `max_tokens` so every request emits exactly
the same token count.

## Measured throughput

Unique prompts, no cache assistance, `usage`-reported tokens.

**Dense ~27B (4-bit) on one H100, ~1.4k-token prompts:**

| Concurrency | Aggregate | Per-stream | TTFT |
| --- | --- | --- | --- |
| 1 | 86 tok/s | 97 tok/s | 0.31 s |
| 8 | 445 tok/s | 82 tok/s | 1.44 s |
| 16 | 633 tok/s | 66 tok/s | 2.50 s |

**Sparse MoE ~35B (FP8, ~3B active) on Blackwell, same prompts:**

| Concurrency | Aggregate | Per-stream | TTFT |
| --- | --- | --- | --- |
| 1 | 177 tok/s | 199 tok/s | 0.15 s |
| 8 | 735 tok/s | 110 tok/s | 0.45 s |
| 16 | 986 tok/s | 82 tok/s | 0.94 s |

**Large prompts (~60k tokens), dense 27B on H100:** TTFT 10 s at concurrency 1,
26 s at 4, 46 s at 8; aggregate output plateaus near 25 tok/s. Uncached prefill
measured ~6,100 tok/s.

## The single most valuable knob: `max_num_seqs`

It caps concurrent sequences. When set below the intended fan-out, requests
queue invisibly: aggregate throughput flatlines and TTFT climbs, while nothing
in the logs reports an error.

Raising it from 2 to 16 on the MoE host improved aggregate by **+166% at
concurrency 8** (276 → 735 tok/s) **and simultaneously cut TTFT from 3.03 s to
0.45 s**. Throughput and latency improved together, because the bottleneck was
queueing rather than compute.

Check the startup line `Maximum concurrency for N tokens per request: X` before
raising it; that value reflects available KV cache.

## Hypotheses that were tested and falsified

- **`--max-num-batched-tokens` is throttling prefill.** Raising it 8192 → 65536
  made TTFT *worse* at every concurrency (26 s → 39 s at 4) while aggregate
  stayed flat. Prefill was already compute-saturated; the knob only trades TTFT
  against decode rate. Common tuning advice that does not apply here.
- **`--async-scheduling` will raise throughput.** No measurable effect.
- **Setting `--kv-cache-dtype fp8_e4m3` will help.** No-op: the NVFP4 checkpoint
  already selected FP8 KV, visible as `Using KV cache scaling factor 1.0 for
  fp8_e4m3` at startup.

## Architecture dominates hardware

A ~35B **MoE** model with ~8 of 256 experts active (~3B active parameters)
decoded roughly **twice as fast** as a dense ~27B model — despite running on a
GPU with *lower* memory bandwidth. Decode is bandwidth-bound on *active*
weights, so total parameter count is a poor predictor of speed.

Practical consequence: for agent fan-out, a large sparse MoE gives capability
without proportional decode cost. Do not assume newer silicon explains a
performance gap; check `architectures` and expert counts in `config.json`
first.

### Confound resolved: the hardware conclusion was backwards

The comparison above was confounded — different models on different GPUs. The
confound was later removed by serving the **same** MoE checkpoint on both
classes of GPU:

| Same checkpoint, 16 concurrent | Aggregate | Per-stream | TTFT |
| --- | --- | --- | --- |
| Datacentre GPU (higher HBM bandwidth) | 1320 tok/s | 99.4 tok/s | 0.48 s |
| Workstation GPU | 986 tok/s | 81.5 tok/s | 0.94 s |

The datacentre GPU is about **34% faster on identical software**. The earlier
impression that the workstation was faster was entirely an artifact of it
running a sparse model while the datacentre node ran a dense one — the model
architecture was *masking a hardware deficit*.

**Rule: never attribute a cross-provider performance gap to hardware until the
same checkpoint has run on both.** Two variables changing at once will produce
a confident and wrong conclusion.

### MoE also wins on KV cache, not just decode

At an identical 131072 context on the same device, the ~35B MoE checkpoint
allocated **~2.94M KV tokens (~22x concurrency)** against the dense ~27B
checkpoint's **~1.37M (~10x)** — despite the MoE weights being *larger*
(~34.5 GiB vs ~20 GiB).

The cause is attention shape, not sparsity: the MoE checkpoint has 2 key/value
heads and hidden size 2048, versus 4 heads and 5120. KV cost per token scales
with those, so more of the device is left for cache. When sizing context, read
`num_key_value_heads` and `hidden_size` — parameter count alone predicts KV
capacity badly.

## Agent-mode capability depends on parser availability

Tool calling requires a tool-call parser shipped with vLLM. Current versions
include parsers for Qwen3, Gemma, gpt-oss, DeepSeek, Granite, Llama, Mistral,
Hermes and others. **A model family with a reasoning parser but no tool-call
parser is a poor agent worker** regardless of benchmark scores — the agent
picker in VS Code also hides models whose provider advertises no tool support.

Verify the exact registered parser string at launch; file names in the package
do not always match the accepted CLI value.

## Client-side configuration traps

- `context_length` in the client must be **below** the server's
  `max_model_len`. Advertising the exact value produced
  `400 ... 28673 input + 4096 output > 32768`. Leave a few thousand tokens of
  slack.
- Set the client `tool_calling` flag truthfully. Advertising `false` hides the
  model from the agent picker; advertising `true` without server-side tool
  support produces confusing runtime failures.
- Chain-of-thought leaking into `message.content` can be suppressed per request
  with `chat_template_kwargs: {"enable_thinking": false}` — no server restart
  needed.
- Check for local port collisions before binding a forward. A tunnel bound to a
  port already serving a different local model silently routes traffic to the
  wrong server, which presents as a model-quality problem.
- **Keep model ids unique across all client entries.** Serving the same
  checkpoint from two hosts under one id makes the picker ambiguous and breaks
  id-based references. Give each deployment a distinct `--served-model-name`
  (for example a location suffix) rather than reusing the checkpoint's name.
- A client entry pointing at a stopped server fails only at request time. After
  moving a provider, cancel the stale forward and update the client together;
  otherwise the editor shows a healthy-looking model that cannot answer.

## Allocation economics (opportunistic HPC account)

Interactive GPU partitions cap wall time (8 h observed) and bill per GPU. A
full-node 8-GPU request can consume several times a light user's monthly usage
in a single session, depressing fair-share priority for subsequent ordinary
jobs. Prefer the smallest GPU count that answers the question; MIG slices are
substantially cheaper per hour where the model fits.

Model weights and compile caches persist on scratch between allocations.
**Pre-stage large downloads in a CPU-only job** so that GPU hours are not spent
transferring files — but note the qualifier: this applies when a GPU job would
have to be *started* for the transfer. If a GPU allocation is already running
and billing wall-clock time, downloading inside it costs nothing additional and
avoids both queue wait and load on a shared login node. A ~36 GB checkpoint
staged to a parallel filesystem in under two minutes.

**One device cannot host two large models.** A ~27B 4-bit server at 0.85 memory
utilization occupied ~70 of ~81 GB, leaving no room for a second ~35 GB
checkpoint. Serving two models for comparison requires either separate GPUs or
sequential runs; "distinct ports" alone does not make them co-resident. Verify
free device memory before launching a second server rather than discovering it
as an out-of-memory failure.
