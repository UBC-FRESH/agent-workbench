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

## Three process-management traps

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

**A pattern kill can match the shell that issued it.** Running
`pkill -9 -f "vllm serve"` inside `bash -c "..."` puts that same string in the
wrapper's own command line, so `pkill` matches itself and dies before reaching
the server. The command produces no output and appears to have worked, while
the old server keeps running and holding its port. The failure only surfaces at
the next launch, as `OSError: [Errno 98] Address already in use`.

- Resolve the target with `pgrep -af` first, then kill by explicit PID.
- Confirm the port is actually released before relaunching, rather than
  trusting the stop command's silence.
- A silent kill command is not evidence of a stopped process.

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

**It also silently caps your benchmark.** Measured "peak" throughput tends to
land at whatever this value is set to, because aggregate throughput keeps
climbing right up to the ceiling. A peak figure is only a device characteristic
if you confirmed the slot limit was not the binding constraint. Raising the
limit from 16 to 256 raised measured aggregate throughput about fivefold on the
same hardware and the same checkpoint.

Raising it sixteenfold cost about 2% of KV cache, so it does not meaningfully
trade against context capacity.

## Capacity is a per-stream latency policy, not a number

Sweeping concurrency from 1 to 256 at short prompts, aggregate throughput never
stopped climbing and TTFT stayed under a second throughout. There was no
saturation knee to find.

What degrades instead is per-stream speed, smoothly and monotonically: roughly
154 tok/s for a lone request, 59 at 64 concurrent, 32 at 256. Aggregate rose
from 126 to 7,850 tok/s across the same range.

So "how many agents fit on one device" has no hardware answer. It is set by the
per-stream speed you are willing to accept. State that floor first, then read
off the session count. Reporting aggregate alone hides the latency being paid to
obtain it.

## Short-prompt benchmarks flatter latency by an order of magnitude

Holding concurrency fixed and varying only input size:

| Prompt tokens | Aggregate tok/s | Per-stream tok/s | TTFT mean | TTFT p95 |
| --- | --- | --- | --- | --- |
| 1,031 | 836 | 110 | 0.33 s | 0.33 s |
| 16,410 | 448 | 57 | 1.48 s | 2.15 s |
| 32,887 | 322 | 41 | 2.48 s | 3.61 s |
| 65,857 | 162 | 21 | 5.82 s | 8.88 s |

TTFT grows about eighteenfold and aggregate throughput falls about fivefold,
with output length pinned and concurrency constant.

Agent turns carry large prompts, so benchmark at the prompt sizes you will
actually serve. Sub-second latency measured on toy prompts becomes multi-second
latency in production, and it is the p95 that users notice.

## Prefix caching is worth measuring as a feature

Suppressing prefix caching with unique prompts is correct when benchmarking the
engine, but agent traffic resends a large shared prompt prefix every turn.
Measured at 8 concurrent streams with ~16k-token prompts, a shared prefix versus
unique prompts gave **+46% aggregate throughput (448 → 656 tok/s)** and **~2x
faster TTFT (1.48 s → 0.77 s)**.

Benchmark both ways: unique prompts to characterize the engine, shared prefixes
to predict production.

## Reproducing the capacity measurements

Harness: `scripts/bench_capacity.py`. It enforces the method requirements
described above — unique prompt content per request, server-reported token
counts, pinned output length, and repeats with variance reported.

### Engine and serving configuration

Engine version 0.26.0. Serving flags held constant across every measurement
except `--max-num-seqs`, which was the swept variable:

```
--max-model-len 131072
--gpu-memory-utilization 0.85
--max-num-batched-tokens 8192
--max-num-seqs <16 | 64 | 256>
--kv-cache-dtype fp8_e4m3
--enable-prefix-caching
--enable-chunked-prefill
--async-scheduling
--language-model-only
--generation-config vllm
--enable-auto-tool-choice
--tool-call-parser <family-xml>
--reasoning-parser <family>
```

Reported KV cache at startup, showing that slot count barely affects it:

| `--max-num-seqs` | GPU KV cache tokens | Max concurrency at full context |
| --- | --- | --- |
| 16 | 2,948,170 | 22.49x |
| 64 | 2,948,170 | 22.49x |
| 256 | 2,875,985 | 21.94x |

### Request parameters

Every request used `temperature 0.8`, `top_p 0.95`, `max_tokens 256`,
`ignore_eos true` (so decode length is identical across requests), streaming
with `stream_options.include_usage true`, and thinking disabled via
`chat_template_kwargs`. Token counts come from `usage.completion_tokens` and
`usage.prompt_tokens`, never from counting stream chunks.

### Invocations

```bash
# Concurrency sweep (short prompts)
python3 scripts/bench_capacity.py --mode conc \
    --conc 1 8 16 24 32 48 64 --ctx 64 --max-tokens 256 --repeats 2
python3 scripts/bench_capacity.py --mode conc \
    --conc 64 96 128 192 256 --ctx 64 --max-tokens 256 --repeats 2

# Low-concurrency re-measurement, and slot-ceiling comparison
python3 scripts/bench_capacity.py --mode conc \
    --conc 1 4 8 --ctx 64 --max-tokens 256 --repeats 3

# Long-context sweep at fixed concurrency
python3 scripts/bench_capacity.py --mode conc --conc 8 \
    --ctx 1024 4096 16384 32768 65536 --max-tokens 256 --repeats 2

# Prefix-cache benefit at one operating point
python3 scripts/bench_capacity.py --mode prefix --conc 8 \
    --ctx 16384 --max-tokens 256 --repeats 3

# Crossed grid: agent-sized context at increasing concurrency
python3 scripts/bench_capacity.py --mode conc \
    --conc 16 32 64 96 --ctx 32768 --max-tokens 256 --repeats 2
```

### Prompt-length calibration

Prompts are random lowercase words, which get no vocabulary compression and
tokenize at roughly **3.36 tokens per word** on this tokenizer. The harness
divides by that constant, so `--ctx` is approximate; the `ctx_in` column reports
the actual server-measured prompt length and is the figure to cite.

Synthetic random tokens are correct for prefill cost, which depends on token
count rather than content, and they reliably defeat caching. They are *not*
representative of how real prompts compress, and results may differ on natural
text or code.

### Full concurrency results

Short prompts (~76 server-measured tokens), 256 output tokens per request:

| Concurrency | Aggregate tok/s | Decode tok/s | Prefill tok/s | Per-stream tok/s | TTFT mean | TTFT p95 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 163 | 182 | 509 | 165 | 0.15 s | 0.15 s |
| 4 | 525 | 581 | 1,671 | 132 | 0.18 s | 0.18 s |
| 8 | 926 | 1,029 | 2,829 | 117 | 0.21 s | 0.21 s |
| 16 | 1,113 | 1,567 | 3,772 | 88 | 0.32 s | 0.32 s |
| 24 | 1,916 | 2,133 | 5,615 | 80 | 0.32 s | 0.33 s |
| 32 | 2,345 | 2,590 | 8,072 | 74 | 0.30 s | 0.31 s |
| 48 | 3,032 | 3,388 | 10,131 | 65 | 0.36 s | 0.38 s |
| 64 | 3,726 | 4,097 | 13,128 | 59 | 0.37 s | 0.38 s |
| 96 | 4,916 | 5,345 | 19,382 | 52 | 0.38 s | 0.41 s |
| 128 | 5,343 | 6,367 | 21,439 | 46 | 0.45 s | 0.50 s |
| 192 | 6,963 | 7,564 | 28,552 | 37 | 0.52 s | 0.57 s |
| 256 | 7,850 | 8,683 | 33,489 | 32 | 0.58 s | 0.68 s |

Rows 1-8 were re-measured with three repeats at spread under 3%. Rows 16-64
come from a two-repeat pass at a 64-slot ceiling and rows 96-256 from a
two-repeat pass at a 256-slot ceiling; of these, rows from 24 upward held spread
under ~5%, while 16 was noisier and should be treated as indicative.

The first attempt at rows 1-8 produced markedly worse figures with 44-121%
spread. That was warmup on the first repeat, not a real effect; the corrected
values above are higher. Always discard or repeat the first measurement at a
given configuration.

## `max_num_seqs` is a ceiling, not a reservation

Raising the slot limit does not slow down low-concurrency work. Measured at a
256-slot ceiling, concurrency 1, 4 and 8 matched or beat the same points
measured at a 64-slot ceiling.

The setting only binds once in-flight requests exceed it. Below that the
scheduler behaves identically, so for an interactive agent lane running a few
requests at a time the value is invisible.

Consequences for choosing it:

- A high limit is never worse for a lightly loaded endpoint, and is better if
  the client ever fans out many parallel subagents.
- A low limit acts as crude admission control: excess requests queue instead of
  being admitted, so the admitted ones finish sooner. Same total work, different
  latency shape.
- The cost of a high limit is a small KV cache reduction, about 2.4% going from
  16 slots to 256.

So pick it from the fan-out you expect, not from a belief that a low value keeps
single requests fast. It does not.

### Full long-context results

Concurrency fixed at 8, 256 output tokens per request:

| Prompt tokens | Aggregate tok/s | Decode tok/s | Prefill tok/s | Per-stream tok/s | TTFT mean | TTFT p95 |
| --- | --- | --- | --- | --- | --- | --- |
| 1,031 | 836 | 1,023 | 24,968 | 110 | 0.33 s | 0.33 s |
| 4,106 | 618 | 953 | 55,490 | 94 | 0.59 s | 0.69 s |
| 16,410 | 448 | 671 | 88,649 | 57 | 1.48 s | 2.15 s |
| 32,887 | 322 | 534 | 106,234 | 41 | 2.48 s | 3.61 s |
| 65,857 | 162 | 303 | 90,494 | 21 | 5.82 s | 8.88 s |

Prefill rate rises with input size, peaks near the 32k point, then falls back at
65k — consistent with attention cost growing faster than linearly.

## Capacity is context-dependent, and the two axes must be crossed

Sweeping concurrency at short prompts and context length at low concurrency
measures two edges of a grid. The production case is the interior: many agents
each carrying a large prompt. Behaviour there is not predictable from either
edge.

At ~32.9k-token prompts, 256 output tokens, unique prompts:

| Concurrency | Aggregate tok/s | Per-stream tok/s | TTFT mean | TTFT p95 |
| --- | --- | --- | --- | --- |
| 16 | 271 | 17.7 | 6.38 s | 11.05 s |
| 32 | **481** | 15.7 | 4.05 s | 11.39 s |
| 64 | 309 | 5.3 | 24.23 s | 45.30 s |
| 96 | 316 | 4.1 | 36.46 s | 68.97 s |

**Here a real knee exists.** Aggregate throughput peaks near 32 concurrent
streams and then *declines*. Past the peak, additional load buys no extra output
at all — it only adds latency, and p95 TTFT reaches over a minute.

Compare the short-prompt sweep, where throughput was still climbing at 256
streams and TTFT stayed under a second. Single-device capacity therefore differs
by roughly an order of magnitude depending on prompt size. A capacity figure
quoted without the context length it was measured at is meaningless.

For planning at agent-sized context, the usable operating point on this device
is around 32 concurrent streams, delivering roughly 16 tok/s per stream with
about 4 s mean and 11 s p95 first-token latency.

### The failure mode is queueing, not preemption or errors

At the collapse points the server logged **no preemption events**, reported KV
cache usage reaching 100%, and showed a waiting queue as deep as 87 requests.
Excess load is admitted to a queue rather than preempting running sequences or
returning errors.

Operationally this is good news: the endpoint degrades in latency, not in
correctness, and does not thrash. It also means overload is invisible to clients
except as slowness — there is no error to alert on, so watch queue depth and p95
TTFT rather than waiting for failures.

### The collapse arrives earlier than KV arithmetic predicts

Predicted before running: with a 2,875,985-token cache, 32k-context streams
should fit comfortably to 64 (~73% utilisation) and only break near 96 (~110%).

That prediction was wrong. Throughput had already collapsed at 64 streams, at
roughly three-quarters of nominal cache. KV capacity alone does not predict the
usable operating point.

The likely mechanism at 64 streams is prefill scheduling rather than cache
exhaustion: with a batched-token budget of 8192, admitting 64 streams of ~33k
tokens requires on the order of 250 scheduler iterations of prefill before those
streams can decode, which shows up directly as multi-second TTFT. At 96 streams
the cache genuinely does saturate and the queue absorbs the excess.

This attribution is not fully isolated — the log evidence confirms queueing and
100% cache usage but does not cleanly separate which run produced which. Treat
the prefill explanation as the leading hypothesis, not a settled result.

The practical rule stands regardless: size from measurement at your real prompt
length, not from dividing cache size by context length.

## Verify the tool *loop*, not just a single tool call

A request that returns `finish_reason=tool_calls` proves the parser can emit one
call. It does not prove an agent can run. The loop — feeding a tool result back
and getting a second, dependent call — is a separate capability and can fail
independently.

Probe: `scripts/tool_loop_probe.py`. It defines two tools where the second
requires an identifier that appears only in the first tool's result, so a model
that fabricates instead of reading the result fails visibly rather than
plausibly.

```bash
python3 scripts/tool_loop_probe.py --url <endpoint>/v1/chat/completions \
    --model <served-alias>
```

Result on the MoE checkpoint with the family XML tool parser: **pass**. Round one
called the lookup tool, round two called the second tool with the exact
identifier returned by round one, and round three stopped with a final answer
containing an order id that exists nowhere but in a tool result. Arguments
parsed as valid JSON at every round and the loop terminated on its own.

Worth checking on any new checkpoint or parser change. Failure modes this
catches that a single-call check does not: arguments that stop parsing on the
second round, a model that ignores the tool result and invents an identifier,
and loops that never emit a final answer.

## Also verify streaming *with* tools, which is what editors actually do

Testing tool calls non-streaming and streaming without tools leaves the real
client path unexercised. Editor clients stream *and* use tools, and that
combination is a separate code path: tool calls arrive as incremental deltas
that must be reassembled across chunks. A parser that is correct on complete
responses can still emit split arguments or truncated names when streamed.

Probe: `scripts/agent_path_probe.py`, covering three checks in one run.

```bash
python3 scripts/agent_path_probe.py --url <endpoint>/v1/chat/completions \
    --model <served-alias>
```

Results on the MoE checkpoint with the family XML tool parser:

| Check | Result | Evidence |
| --- | --- | --- |
| Streaming + tools | pass | `finish_reason=tool_calls`; arguments arrived across four deltas and reassembled into valid JSON |
| Parallel tool calls | pass | two calls in one assistant turn, distinct valid arguments |
| Structured output (`json_schema`) | pass | response parsed, all required keys present, no extra keys |

The streaming case genuinely exercised the incremental path rather than
arriving in a single chunk, so reassembly is confirmed rather than assumed. If a
probe reports only one argument delta, the test did not actually exercise the
risk and should be re-run with a longer argument payload.

Together with the loop probe, this covers the agent path end to end: streamed
incremental tool calls, several calls per turn, dependent multi-turn sequencing,
and schema-constrained output.

### Prefix-cache comparison

Both rows at concurrency 8 with ~16.4k-token prompts:

| Variant | Aggregate tok/s | Prefill tok/s | Per-stream tok/s | TTFT mean |
| --- | --- | --- | --- | --- |
| Unique prompts | 448 | 88,649 | 57 | 1.48 s |
| Shared prefix | 656 | 170,313 | 85 | 0.77 s |

### Cross-session reconciliation

Before any new claim was made, the harness was run against the operating point
recorded in the previous session. It returned 1,412 aggregate tok/s at
concurrency 16 versus 1,320 recorded previously, and 144 versus 151 at
concurrency 1 — agreement within normal run-to-run spread, so figures from the
two sessions are comparable.

### Definitions

- **Aggregate tok/s** — total completion tokens divided by wall time for the
  whole batch, including prefill. This is the user-visible rate.
- **Decode tok/s** — completion tokens divided by wall time minus mean TTFT.
  Excludes prefill, so it is comparable across prompt lengths.
- **Prefill tok/s** — total prompt tokens divided by mean TTFT.
- **Per-stream tok/s** — mean across requests of that request's own completion
  tokens divided by its own duration.

Report aggregate and per-stream together. Aggregate alone hides the per-stream
latency being paid to achieve it.

## Hypotheses that were tested and falsified

- **`--max-num-batched-tokens` is throttling prefill.** Raising it 8192 → 65536
  made TTFT *worse* at every concurrency (26 s → 39 s at 4) while aggregate
  stayed flat. The knob traded TTFT against decode rate without helping. Common
  tuning advice that did not apply here.

  The reason originally given — that prefill was already compute-saturated at
  ~6,100 tok/s — was itself wrong. Later measurement at higher concurrency and
  larger inputs reached well above 100,000 prefill tok/s. Prefill scales much
  further than that figure implies, so the observed behaviour needs another
  explanation. Recorded here as an unexplained result rather than a solved one.
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
