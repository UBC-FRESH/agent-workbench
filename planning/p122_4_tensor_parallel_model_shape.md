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
