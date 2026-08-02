# P122.4 — Tensor parallelism on a differently-shaped model

Status: planned
Parent phase: P122
Predecessors: #775 (single-GPU acceptance), #776 (capacity + multi-GPU)
Harness: `scripts/bench_capacity.py`, `scripts/agent_path_probe.py`

## Why this task exists

P122.3 measured tensor parallelism at **4.4x slower** than a single device on
the checkpoint in hand, even after the FlashInfer JIT blocker was fixed and
compilation restored. The explanation offered was architectural: that checkpoint
is a sparse MoE with `hidden_size` 2048 and 2 key/value heads, so sharding
already-small tensors leaves each device too little work to hide the per-layer
all-reduce.

**That explanation is currently untested.** It is the surviving hypothesis from
a single measurement on a single model, which is exactly the shape of reasoning
that has been wrong repeatedly in this phase. If it is right, tensor parallelism
should behave very differently on a model with large dense tensors. If it is
wrong, the cost lies somewhere else — the vLLM TP implementation, this build, or
the interconnect configuration — and the "prefer independent replicas" guidance
needs qualifying.

The point of this task is to find out which.

## The decision rule this replaces

"Use tensor parallelism when the model does not fit" is the wrong rule. The
better one, from P122.3's long-context work:

> Use tensor parallelism when the model does not fit **with enough KV cache for
> the context length you actually serve.**

A ~73 GB checkpoint technically fits on an 80 GB device, but leaves only a few
GB for KV cache — near-useless for agent workloads at 32k context. Sharding it
across two devices leaves roughly 60+ GB for cache. That, not the weight fit, is
the real justification.

## Candidates

Sizes and architecture fields below were read from the model repositories, not
recalled. `hidden` is `hidden_size`; `kv` is `num_key_value_heads`.

| Candidate | Weights | Architecture | hidden | kv | experts | Role in this test |
| --- | --- | --- | --- | --- | --- | --- |
| Llama-3.3-70B-Instruct FP8 | 72.7 GB | dense `LlamaForCausalLM` | 8192 | 8 | — | **Primary.** Largest tensors available in range; the strongest test of the hypothesis |
| Qwen3-32B FP8 | 34.3 GB | dense `Qwen3ForCausalLM` | 5120 | 8 | — | Dense control that fits comfortably on one device; isolates TP cost from memory pressure |
| Qwen3-Next-80B-A3B FP8 | 82.1 GB | MoE `Qwen3NextForCausalLM` | 2048 | 2 | 512 | **Negative control.** Same shape as the P122.3 checkpoint; should reproduce the poor TP result |
| Nemotron-3-Super-120B-A12B FP8 | 128.4 GB | MoE `NemotronHForCausalLM` | 4096 | 2 | 512 | Genuinely does not fit on one device; intermediate hidden size |
| GLM-4.5-Air FP8 | 112.6 GB | MoE `Glm4MoeForCausalLM` | 4096 | 8 | 128 | MoE with 8 kv heads — separates "sparse" from "narrow" as the cause |

Out of range for two 80 GB devices: several checkpoints in the 235B-480B class,
and a 397B variant of the P122.3 family. Not candidates here.

### Why this set

The candidates vary `hidden_size` from 2048 to 8192 and kv heads from 2 to 8
while spanning dense and sparse. That is what makes the hypothesis falsifiable
rather than merely illustrated:

- If TP efficiency tracks `hidden_size`, the tensor-shape explanation holds.
- If the 80B MoE (hidden 2048, kv 2) reproduces ~4.4x while the 70B dense
  (hidden 8192, kv 8) does not, that is close to a controlled result.
- If **all** of them are slow, the explanation is wrong and the cost is in the
  implementation or environment, not the model.

GLM-4.5-Air is the interesting tiebreaker: sparse like the failing case, but
with 8 kv heads and hidden 4096. If sparsity per se were the problem it should
be slow; if narrowness is the problem it should be closer to the dense models.

## Adjacent candidate: hybrid attention/SSM (separate track)

Not a tensor-parallelism candidate — it fits comfortably on one device, and its
narrow shape (`hidden` 2688, 2 kv heads) resembles the checkpoint that produced
the 4.4x result, so tensor parallelism would likely be poor on it too.

It is listed here because it attacks a **different and arguably more important**
problem, and because the hardware work above cannot.

| Candidate | Weights | Architecture | hidden | kv | experts | Context |
| --- | --- | --- | --- | --- | --- | --- |
| Nemotron-3-Nano-30B-A3B FP8 | 32.7 GB | `NemotronHForCausalLM` | 2688 | 2 | 128 | 262144 |
| Nemotron-Nano-9B-v2 FP8 | 10.3 GB | `NemotronHForCausalLM` | 4480 | 8 | — | 131072 |
| Nemotron-3-Nano-4B FP8 | 5.3 GB | `NemotronHForCausalLM` | 3136 | 8 | — | 262144 |

The 30B variant is a **hybrid**. Its `hybrid_override_pattern` describes 52
layers as 23 recurrent (Mamba), 23 expert feed-forward, and **only 6 attention
layers**. Supporting fields include `mamba_num_heads` 64, `ssm_state_size` 128,
`conv_kernel` 4, and `use_mamba_kernels` true.

Why that matters here. P122.3 established two things: capacity at agent-sized
context is the binding constraint, and **tripling the KV cache did not move the
collapse at all**. Those results say the problem cannot be solved by buying more
cache. A model where only 6 of 52 layers maintain a KV cache at all has a
fundamentally different memory-versus-context curve, because recurrent layers
carry fixed-size state rather than a cache growing with sequence length.

That is a structural attack on the measured bottleneck rather than a hardware
one, which is why it deserves its own track rather than a footnote.

It also closes a gap recorded in the P122 planning note: every checkpoint
compared so far has come from one model family, so no result to date separates
family-specific behaviour from general behaviour. This is a genuinely different
architecture.

**Explicitly untested.** The reasoning above is read from configuration files,
not measured. Whether the hybrid delivers better long-context concurrency *in
this serving stack* depends on kernel support and scheduler behaviour, and
`mamba_ssm_cache_dtype: float32` hints at real memory cost in the recurrent
state. It could underperform for implementation reasons unrelated to the
architecture's promise. Treat the above as a motivated hypothesis with a cheap
test, not a prediction.

Suggested test, roughly one allocation on a single device:

1. Serve the 30B hybrid alone; record KV cache size and reported maximum
   concurrency, and compare against the same figures for the current checkpoint.
2. Run the crossed grid from P122.3 — 16 / 32 / 64 streams at ~32k prompts — and
   compare directly against the recorded collapse there.
3. Run `scripts/agent_path_probe.py` and `scripts/tool_loop_probe.py`; a
   different architecture means tool-call parsing and streaming behaviour must
   be re-verified rather than assumed.
4. If long-context concurrency is materially better, follow with a quality
   spot-check before treating it as an agent-lane candidate. Serving capacity is
   not usefulness.

## Larger-scale track: an eight-device frontier coder model

A separate and much larger commitment. Listed here so the sizing work is not
repeated, not because it belongs in the same allocation.

| Field | Value |
| --- | --- |
| Weights | 482.1 GB |
| Architecture | `Qwen3MoeForCausalLM` |
| hidden / layers | 6144 / 62 |
| attention heads / kv heads | 96 / 8 |
| experts | 160, 8 active |
| context | 262144 |

### Feasibility, verified rather than assumed

- The cluster has **29 nodes offering eight H100 devices each**, with an
  eight-hour interactive limit. This is a **single-node** job; no multi-node
  networking is involved.
- Eight devices give 640 GB raw, about 544 GB usable at 0.85 utilisation.
  Weights take 482 GB, leaving roughly **62 GB for KV cache**.
- Six devices (~408 GB usable) do not fit at all. Eight is the minimum.
- Scratch has ample room: 89 GiB used of a 1024 GiB quota, against a 482 GB
  download.

### Why this model is a better parallelism candidate than anything tested

`hidden_size` 6144 with 8 kv heads, against the 2048 and 2 that produced the
4.4x penalty. If the tensor-shape hypothesis above holds, this is precisely the
regime where tensor parallelism should behave well. A poor result here would be
strong evidence against that hypothesis, so the two tracks inform each other.

### Run the cheap track first

P122.4's two-device work costs one short allocation and would indicate whether
wide-tensor models parallelise acceptably on this stack. Learning that from a
72 GB model is far cheaper than learning it from a 482 GB one after an
eight-device, eight-hour commitment.

### Risks specific to this track

- **Download is the dominant risk.** 482 GB. A 36 GB fetch was near-instant on
  this cluster, but extrapolating that is exactly the assumption pattern that
  has failed repeatedly in this phase. Measure throughput on a partial fetch
  first, and stage the download in a session *before* the one that serves it.
- **62 GB of KV cache is not much for a 262k-context model.** P122.3 found
  long-context concurrency to be the binding constraint, and that additional
  cache did not move it. This configuration may hit the same wall at a larger
  model size, with the KV budget rather than the weights as the limit.
- An eight-device allocation is a substantial shared-resource request. Have the
  weights staged and the serving arguments settled before claiming it.

### Quantization does not change the device count much

Measured weight sizes for the same 480B checkpoint across published variants:

| Variant | Weights | 2 devices (136 GB) | 4 devices (272 GB) |
| --- | --- | --- | --- |
| FP8 | 482.1 GB | no | no |
| NVFP4 | 272.9 GB | no | no, misses by ~1 GB |
| MXFP4 | 272.8 GB | no | no |
| GPTQ int4-mixed | 266.6 GB | no | yes, ~5 GB KV left |
| AWQ 4-bit | 252.3 GB | no | yes, ~20 GB KV left |

Worth stating plainly because it is a natural assumption: **quantization scales
weights, not architecture.** Halving precision halves memory, so a checkpoint
three times too large for a device budget stays too large. The floor is set by
parameter count. The realistic choices for this checkpoint are four devices with
a 4-bit build and a thin KV budget, or eight devices at FP8 with roughly 62 GB
of cache.

Note also that two of the 4-bit variants land within a gigabyte of the four-
device budget *before* accounting for activations and CUDA graphs, so treat them
as not fitting rather than barely fitting.

## Very large candidates: DeepSeek V4 family

Measured, for sizing purposes. `DeepseekV4ForCausalLM` is a distinct
architecture from everything tested in this phase, and the engine in use carries
a dedicated attention operator for it, so support is not in question.

| Model | Weights | hidden | experts | Context | Minimum devices |
| --- | --- | --- | --- | --- | --- |
| V4-Flash | 159.6 GB | 4096 | 256 | 1,048,576 | **4** (~112 GB KV left) |
| V4-Flash NVFP4 | 168.3 GB | 4096 | 256 | 1,048,576 | 4 |
| V4-Pro | 864.7 GB | 7168 | 384 | 1,048,576 | **16** — two nodes |
| V4-Pro NVFP4 | 913.1 GB | 7168 | 384 | 1,048,576 | 16 — two nodes |

**Flash is the most attractive large candidate found.** It fits on four devices
on a single node with substantial KV headroom, which is a far better position
than the 480B coder at eight devices with 62 GB. It is also a genuinely
different architecture, which addresses the family-diversity gap directly.

**Pro requires two nodes.** That pulls in multi-node collective communication —
the same class of path whose single-node variant blocked tensor parallelism in
P122.3. Treat Pro as out of scope until single-node multi-device serving is
proven working and understood.

### Two things to verify before downloading

- **The NVFP4 repositories measure larger than their base repositories** (168.3
  against 159.6; 913.1 against 864.7). Four-bit weights should be smaller. The
  likely explanation is that the base repositories already ship a low-precision
  format and the NVFP4 repositories carry mixed-precision layers or duplicate
  format directories that a naive size sum double-counts. **Inspect the file
  layout before starting a fetch**, particularly for Pro, where a wrong
  assumption costs a 913 GB download.
- **An attractive hypothesis that did not survive checking.** DeepSeek
  architectures have been associated with compressed key/value attention, which
  would directly address the long-context bottleneck measured in P122.3. The V4
  configuration does **not** expose a `kv_lora_rank` field, so that could not be
  confirmed from configuration alone and is recorded here as unverified. Read
  the modeling code before relying on it.

The advertised million-token context is the interesting property regardless. Given
that P122.3 found capacity collapsing at agent-sized context, a model claiming a
million tokens is either a real advance on that constraint or a more dramatic
instance of it. Both outcomes are worth measuring, and the crossed grid from
P122.3 is the way to find out.




## Method

Reuse `scripts/bench_capacity.py` unchanged, so results are comparable with
P122.3. Binding requirements carried forward:

- Unique prompt content per request unless prefix caching is the variable.
- Token counts from server-reported usage, never streamed chunk counts.
- Pinned decode length (`ignore_eos` with fixed `max_tokens`).
- Discard or repeat the first measurement at each configuration; warmup
  contaminated several P122.3 runs by up to 121%.
- Report aggregate **and** per-stream throughput together.

Per candidate:

1. Serve on one device if it fits at all, even with minimal KV cache. Record KV
   cache size and maximum reported concurrency.
2. Serve with `--tensor-parallel-size 2`, compiled (not eager).
3. Benchmark both at 16k and 32k prompts, at concurrency 8 and 32. Short prompts
   measure the wrong regime and will flatter the system by an order of
   magnitude.
4. Record the TP-versus-single ratio per candidate alongside `hidden_size`.

Apply the FlashInfer fix from P122.3 before starting, or TP will fail to compile:

```bash
export FLASHINFER_EXTRA_CUDAFLAGS="-DCCCL_DISABLE_CTK_COMPATIBILITY_CHECK"
export FLASHINFER_EXTRA_LDFLAGS="-L<venv>/nvidia/cu13/lib -L/usr/lib64"
# one-time, in the wheel lib dir:
ln -sf libcudart.so.13 libcudart.so
```

Clear `.../cached_ops/trtllm_mnnvl_comm` between attempts or a previous failure
replays from cache.

## Acceptance criteria

- TP-versus-single-device ratio measured for at least two candidates differing
  substantially in `hidden_size`.
- An explicit statement of whether the tensor-shape hypothesis survived.
- Where a candidate does not fit on one device, KV cache headroom under TP is
  recorded, since that is the operational justification.
- Any conclusion that revises P122.3 guidance is written into the operations
  note as a correction, not appended as if it were new.

## Practical notes

- **Start the download first.** It is the long pole. A 36 GB fetch was near-
  instant on this cluster, but that may not generalize to 130 GB, and an
  allocation spent downloading produces nothing.
- Prefer a longer allocation over a larger one. Two devices suffice for every
  candidate here; time is the binding constraint.
- Weight sizes above are safetensors totals. Actual device footprint is larger
  once activations and CUDA graphs are accounted for, so treat the 128 GB
  candidate as tight on 160 GB rather than comfortable.

## Risks

- The 120-128 GB candidates leave little room for KV cache even across two
  devices, so a poor result there may reflect memory pressure rather than
  parallelism cost. Read those alongside the smaller candidates rather than
  alone.
- Architectures differ in more ways than `hidden_size`. This is a natural
  experiment, not a controlled one; a clean result is suggestive, not decisive.
- Download time may consume the allocation. Stage weights in a prior session if
  possible.
