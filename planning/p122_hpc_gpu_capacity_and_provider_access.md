# HPC GPU Capacity and Provider Access Notes

**Date:** 2026-07-29
**Status:** Design and local implementation recorded; no live deployment claim.

## Purpose

Capture the durable, public-safe lessons from a blocked multi-GPU inference
deployment attempt and the local tooling added while waiting for scheduler
capacity. This note intentionally omits hostnames, user names, job IDs,
provider URLs, credentials, tunnel IDs, account names, and storage paths.

## Operating Constraints

- A useful large-model deployment may require a co-scheduled multi-GPU node,
  not an arbitrary sum of GPUs spread across independent allocations.
- Existing Slurm allocations are scarce and time-limited. A new batch request
  does not automatically consume an already-running allocation; work intended
  for an existing allocation must be launched through the scheduler's supported
  in-allocation mechanism.
- Shared cluster filesystems can make package trees and model repositories slow
  to stage because metadata-heavy copies involve many small files. Node-local
  NVMe is often a better runtime staging location once a job has landed.
- Cluster-compatible binaries must match the allocated GPU architecture and
  installed CUDA/runtime constraints. A successful source build is not the
  same thing as a successful model-serving deployment.
- Remote access is production-sensitive. Do not create, replace, or test a
  connector without inspecting the existing topology and preserving the active
  path.

## Deployment Pattern Under Evaluation

### 1. Allocation and staging

1. Request the exact one-node GPU shape needed by the serving engine and model
   parallelism. Treat a 1-GPU request as a build or smoke-test fallback, not as
   a substitute for a 4-GPU tensor-parallel service.
2. Keep build artifacts on durable project storage in a compact archive when
   possible. On allocation, copy the archive to node-local NVMe and unpack
   there rather than repeatedly copying a large package tree over shared
   storage.
3. Use the cluster's supported container workflow (for example, Apptainer) and
   build extensions for the real target GPU architecture. Record the toolchain,
   architecture flags, package versions, and resulting artifact checksum.
4. Run a short model-server smoke test before configuring an IDE provider:
   model discovery, one short completion, one longer-context request, and
   process/GPU observation.

### 2. Serving acceptance checks

Do not call a deployment usable until the following evidence is captured in an
ignored runtime report and distilled into a sanitized planning note:

- scheduler job ID and requested resource shape;
- model-server launch command class, model revision, quantization, and
  parallelism configuration;
- `/v1/models` or equivalent discovery response;
- short chat completion correctness and time-to-first-token;
- sustained generation throughput in tokens/second;
- a context-window request at the intended client size;
- tool-call or structured-output behavior if the target client requires it;
- concurrent-request behavior and GPU-memory headroom;
- failure logs if any check fails.

The previous attempt reached partial local-provider behavior but did not yet
produce this complete acceptance record. No performance, tool-use, or
long-context success claim is therefore warranted.

## Multi-Cluster Capacity Coordinator

Local implementation: `src/agent_workbench/gpu_capacity.py`.

The coordinator is intentionally conservative:

- Reads scheduler inventory and queue state through per-cluster SSH/Slurm
  adapters.
- Uses YAML for local, untracked cluster specifications. Real SSH targets,
  accounts, submission scripts, and project paths stay out of tracked files.
- Persists only job IDs submitted by the coordinator itself.
- Defaults to dry-run. `--apply` is required for scheduler mutations.
- Submits across listed clusters until tracked running plus pending capacity
  covers the requested GPU target, respecting a per-cluster pending-job limit.
- Once the tracked running capacity reaches the target, cancels only the
  coordinator-owned jobs that are still pending. It never cancels a running
  allocation.
- Marks a tracked job `UNKNOWN` if scheduler state cannot be refreshed rather
  than trusting stale state.

Known limitation: heterogeneous request shapes can overshoot a target once
multiple pending jobs start. The coordinator will not terminate a running job
to compensate. For a model that needs GPUs on one node, the operator must use
cluster specs that request the complete compatible shape and must not treat
separate smaller allocations as interchangeable capacity.

The implementation has focused unit coverage for multi-cluster dry-run plans,
apply-time submissions, pending-only cancellation, dry-run non-mutation,
scheduler failure handling, and state/config round trips. It has not yet been
run against a real multi-cluster configuration.

## Provider Access Modes

### Default: client-owned SSH local forwarding

When no Cloudflare option is used, the provider stays loopback-only on the
provider host. Each consuming environment owns an SSH local forward:

```text
client 127.0.0.1:<client-port>
    -> SSH transport
    -> provider-host 127.0.0.1:<provider-port>
```

The client config uses `http://127.0.0.1:<client-port>/v1`. A scheduler-node
deployment may require the site's approved jump-host route. This mode creates
no public listener, DNS record, shared connector, or public endpoint. It is
the preferred first integration path for a personal laptop or a short-lived
allocation.

### Optional: established Cloudflare Tunnel plus DNS

Local implementation: `src/agent_workbench/cloudflared_provider.py`.

This helper is not a tunnel lifecycle manager. It:

- renders a review-only candidate ingress configuration for an existing tunnel;
- performs a read-only tunnel inspection in its default plan mode;
- can attach a DNS record only with an exact existing-tunnel confirmation;
- reads the active configuration and requires a matching tunnel ID, hostname,
  and private origin before DNS mutation;
- creates a timestamped backup of the live configuration without rewriting it;
- reinspects the tunnel and checks a configured public health URL afterward.

It does **not** create a tunnel, copy credentials, install or start a
connector, modify a live ingress file, replace a configuration, or delete DNS
on failure. A reviewed operational change must add the ingress rule to the
established connector before the DNS helper is used.

## Immediate Operator Sequence When Capacity Lands

1. Inspect the allocation's actual node, GPUs, CPU count, local NVMe capacity,
   and remaining walltime.
2. Stage the prebuilt runtime archive to node-local NVMe; do not rebuild or
   redownload large dependency trees unless the artifact verification fails.
3. Launch the model server inside the allocation using the recorded compatible
   profile.
4. Capture the serving acceptance record before IDE integration.
5. Start with client-owned SSH forwarding and test model discovery plus a
   small authenticated chat from the actual client application.
6. Consider the optional Cloudflare route only after a stable shared endpoint
   is genuinely required and the existing connector topology has been reviewed.

## Quality, Protocol, and Economics

- **Quality:** local coordinator and provider-access helpers have unit-test
  coverage; no live capacity-collection or provider-exposure result is claimed.
- **Protocol:** live scheduler and Cloudflare mutations are explicit opt-in;
  real values are expected only in ignored local configuration files.
- **Economics:** no allocation-hour, cloud, or provider-cost measurement was
  captured in this work. A future run should record requested GPU-hours,
  queue wait, actual GPU-hours, successful service time, and client usefulness.

---

## Session Record: Single-GPU Provider Deployment (2026-08-01)

**Status:** The serving acceptance record defined above is now **complete for
the single-GPU case**. Multi-GPU tensor-parallel serving remains unevaluated.

### Acceptance evidence

| Check | Result |
| --- | --- |
| Requested resource shape | 1 GPU (80 GB class), 8 CPU, 64 GB RAM, 8 h interactive |
| Engine / model / parallelism | Current vLLM release; 4-bit quantized dense ~27B checkpoint; no parallelism |
| `/v1/models` discovery | 200, served alias matches the client-configured id |
| Short chat completion | Correct; clean `message.content`, no reasoning leakage |
| Time-to-first-token | 0.31 s at 1.4k-token prompt |
| Sustained throughput | 97 tok/s single stream; 633 tok/s aggregate at 16 concurrent |
| Intended client context | Served at 131072 after raising from an initial 32768 |
| Tool-call behavior | Verified with a real function call (`finish_reason=tool_calls`, well-formed arguments) |
| Concurrency / KV headroom | ~1.37M-token KV cache; ~10.4x concurrency at full context |
| Failure logs | Four distinct startup failures captured, each with a fix |

Economics captured: roughly 8 requested GPU-hours for the session; queue wait
under one minute for a single GPU; light historical account usage meant
fair-share was not a limiting factor at this size.

### Durable findings

Full operational detail, including exact error strings and fixes, is in
`notes/operations/hpc-vllm-agent-provider-findings.md`. Headlines:

- **`max_num_seqs` was the dominant throughput control.** Raising it from a low
  default removed invisible queueing: aggregate throughput rose sharply *and*
  time-to-first-token fell at the same time. Nothing in the logs reported an
  error while requests were queueing.
- **Three plausible tuning hypotheses were falsified** by measurement: raising
  the prefill batch size, enabling asynchronous scheduling, and forcing an FP8
  KV dtype. One actively degraded latency. Prefill was already compute-bound.
- **Model architecture dominated hardware.** A sparse MoE checkpoint with a
  small active-parameter count decoded about twice as fast as a dense
  checkpoint on a GPU with higher memory bandwidth.
- **Benchmark method matters more than expected.** Shared prompt prefixes,
  counting stream chunks instead of tokens, and single-run measurements each
  produced badly wrong numbers.

### Process deviation to correct

This session's work began without a phase branch or child issue and was
performed directly against the default branch until the developer intervened.
The repository standard is scaffold-before-work. The work belongs to this
phase (HPC GPU capacity and provider workflow) and has been moved onto the
phase branch; a child issue should record it before any pull request.

## Planned Next Task: Sparse-MoE Comparison on a Single GPU

**Objective.** Serve a sparse-MoE checkpoint of roughly 35B total parameters on
the same single-GPU allocation and compare it against the dense checkpoint
already measured, using an identical harness.

**Why this specific test.** It answers three open questions with one download:

1. **Isolates hardware.** The existing cross-provider comparison confounds GPU,
   model, quantization, and engine version. Running the *same* checkpoint on
   both GPU classes is the only way to separate the hardware contribution.
2. **Tests the MoE thesis** on a second GPU architecture.
3. **Tests fleet unification.** The operating contract prefers one shared model
   across roles; this checks whether one checkpoint can serve both providers.

**Design constraints.**

- Serve on a **distinct port** from the incumbent model so both endpoints stay
  live and directly comparable. Do not replace the working provider.
- Weights of roughly 35 GB against an 80 GB device leave materially less KV
  cache than the dense 4-bit checkpoint. Expect to reduce the context window;
  read the reported KV cache size and maximum-concurrency line before setting
  it.
- Reuse the proven serving profile for this checkpoint family: matching
  tool-call and reasoning parsers, FP8 KV cache, prefix caching, chunked
  prefill, and the same sequence-slot count used for the incumbent.
- Apply the documented platform fixes: wheel-provided CUDA library paths and
  the sampler fallback.

**Sequence.**

1. Confirm the checkpoint identifier and that it is retrievable.
2. Pre-stage the download in a **CPU-only allocation** so GPU hours are not
   spent on file transfer. Caches persist on shared scratch between jobs.
3. Write a serving script adapted from the incumbent launcher, detached at the
   scheduler-client layer so it survives client disconnection.
4. Launch; read KV cache size and maximum concurrency; adjust context if needed.
5. Smoke test: model discovery, one chat completion, and **one real tool call**.
   The attention backend and parser combination is unverified on this GPU
   architecture, so tool calling must be proven, not assumed.
6. Benchmark with the established harness: unique prompts, usage-reported token
   counts, three repeats, at 1/4/8/16 concurrency, plus one large-prompt run.

**Acceptance.** The comparison is only reportable if the tool call succeeds and
the benchmark repeats agree within a few percent. If the checkpoint cannot be
served within the device memory budget at a useful context length, record that
as the finding and stop rather than degrading the incumbent.

**Risks.** Attention-backend compatibility on this GPU architecture is
unverified; download time may exceed the remaining allocation window; and the
reduced KV budget may force a context window too small for real agent use.

## Result: Sparse-MoE Comparison on a Single GPU (2026-08-01)

**Status:** Complete. The planned comparison was executed and the sparse-MoE
checkpoint is now the active HPC provider.

### Serving acceptance record (MoE checkpoint)

| Check | Result |
| --- | --- |
| Weights / load | ~34.5 GiB on an 80 GB device |
| Context served | 131072, matching the dense baseline |
| KV cache | ~2.94M tokens, ~22.4x concurrency (dense baseline: ~1.37M, ~10.4x) |
| Tool call | Verified: `finish_reason=tool_calls`, well-formed arguments |
| Staging | ~36 GB fetched to shared scratch in under two minutes |

### Throughput, same GPU, same harness

| Concurrency | MoE aggregate | Dense aggregate | Gain | MoE TTFT | Dense TTFT |
| --- | --- | --- | --- | --- | --- |
| 1 | 151 tok/s | 86 tok/s | +75% | 0.23 s | 0.31 s |
| 4 | 497 tok/s | 279 tok/s | +78% | 0.31 s | 0.81 s |
| 8 | 838 tok/s | 445 tok/s | +88% | 0.40 s | 1.44 s |
| 16 | 1320 tok/s | 633 tok/s | +109% | 0.48 s | 2.50 s |

Three repeats per level agreed within 0.6%.

### Hardware confound resolved

Running the **same** MoE checkpoint on both GPU classes isolates hardware for
the first time:

| Same checkpoint, concurrency 16 | Aggregate | Per-stream | TTFT |
| --- | --- | --- | --- |
| HPC datacentre GPU | 1320 tok/s | 99.4 tok/s | 0.48 s |
| Workstation GPU | 986 tok/s | 81.5 tok/s | 0.94 s |

The datacentre GPU is roughly **34% faster on identical software**. The earlier
cross-provider comparison had suggested the opposite; that impression was
entirely an artifact of the workstation running a sparse model while the HPC
node ran a dense one. Architecture was masking a hardware deficit.

**Durable lesson:** never attribute a cross-provider performance gap to hardware
until the same checkpoint has run on both.

### Quality spot-check

The same bounded analysis task was run against both checkpoints with identical
inputs and output-format requirements.

- Both correctly identified every real portability blocker later confirmed by
  live deployment.
- The MoE checkpoint produced materially better evidence discipline: per-claim
  file *and line* citations, and it explicitly flagged one input it had not
  been given rather than inventing content.
- **Both fabricated specifics with equal confidence.** The dense checkpoint
  invented a hardware memory figure; the sparse one invented a plausible-looking
  filesystem path and asserted a toolkit-version requirement that live
  deployment had already disproved.

One sample each. This is a spot-check, not an evaluation, and it does not
support a general quality ranking. It does reinforce the existing rule that
worker claims require independent verification regardless of model.

### Operator state at close

- HPC node serves the MoE checkpoint on a dedicated port with a distinct served
  model alias, so it cannot be confused with the workstation instance.
- The dense checkpoint is stopped: a single device cannot hold both (the dense
  server alone occupied ~70 of ~81 GB).
- Launch scripts for both checkpoints persist on shared scratch; switching is a
  single command.
- Client configuration points at the HPC MoE endpoint through an operator-owned
  forward. Model ids across all configured entries remain unique.

### Follow-up candidates

- Multi-GPU tensor-parallel serving remains unevaluated; the engine supports
  tensor, pipeline, and data parallel modes.
- A non-Qwen-family checkpoint would give genuine architectural diversity; both
  checkpoints compared here share a family.
- Sequence-slot count was set to 16 on both providers and not pushed further;
  KV headroom suggests room to increase, at the cost of per-stream latency.

## Workflow Lessons From This Session

These concern how the work was conducted, not the deployment itself. They are
recorded because the same failure modes will recur otherwise.

**Scaffold before work, not after.** The session ran a full deployment, four
repairs, two production configuration changes and six benchmark rounds against
the default branch before the developer asked whether a phase branch existed.
An active phase covering exactly this work, with a planning note and an
acceptance checklist, already existed and would have structured the session had
it been read first. Cost: retrofitted scaffolding and a process-deviation entry.

**Do not report success before verifying it.** A server launch was reported as
"launched, processes alive" while its log was zero bytes and the process was
already dead. The claim was inferred from the launch command returning cleanly.
Every completion claim needs an independent check against the artifact, not the
command's exit status.

**Answer status questions with the last verified state.** Repeated requests for
status were met with additional commands rather than a direct report. When a
check cannot complete, the correct response is the most recent verified state
plus an explicit note that nothing newer has been confirmed.

**One measurement is not a result.** Three separate anomalies during this
session vanished on repeat: an apparent 57% throughput regression, a spurious
concurrency-4 collapse, and a misleading first-run latency. Each would have
become a false finding if reported immediately. Repeat before believing, and
report variance.

**Tuning advice must be tested, not assumed.** A confident recommendation to
raise the prefill batch size was wrong: it degraded latency and left throughput
flat. Two further plausible changes had no effect at all. The only intervention
that mattered was raising the sequence-slot limit. Publish the falsified
hypotheses alongside the successful one, so the next operator does not retry
them.

**Reconstructing a command is riskier than reusing the project's launcher.** A
production server was briefly broken by rebuilding its command line from the
process table; the rebuilt command omitted environment setup that the project's
own launch script performs. Prefer the supported entry point, and capture the
exact arguments and a rollback path before stopping anything.

**Verify which configuration file is actually in use.** The default environment
file in the local lab pointed at a different model from the one actually
serving. Launching from it would have silently replaced a working endpoint with
a differently-configured model on the same port.

## Planned Next Task: Concurrency Knee and Long-Context Behaviour

Two gaps remain in the single-GPU capacity picture, and both can only be closed
while an allocation is live.

### Gap 1: the concurrency knee was never found

The MoE sweep stopped at sixteen concurrent streams because that was the
server's configured sequence-slot ceiling, not because the device saturated. At
that point aggregate throughput was still climbing steeply and time-to-first-
token had barely moved. The correct reading of the recorded result is therefore
a **lower bound**, not a capacity figure.

For a phase whose purpose is capacity planning, the number of concurrent agent
sessions one device supports is the central question, and it is still open.

Method: raise the sequence-slot limit well above the previous ceiling, then
sweep concurrency upward, holding the harness fixed. Identify the knee as the
point where per-stream throughput degrades materially or time-to-first-token
crosses a usability threshold. Report both aggregate and per-stream figures;
aggregate alone hides the latency cost paid to obtain it.

### Gap 2: every published number came from short prompts

All recorded throughput and latency figures were produced with small inputs,
while the server advertises a very large context window and real agent turns
carry substantial prompt context.

Prefill was measured as compute-saturated. At that rate, a realistic
agent-sized prompt implies seconds of prefill before the first token — roughly
an order of magnitude worse than the sub-second figures already recorded. If
that holds, the existing latency numbers do not transfer to agent workloads,
and anyone planning capacity from this note would be misled.

This is the test most likely to change a conclusion already written down, which
is why it is worth spending allocation time on.

Method: hold concurrency fixed and sweep prompt length across roughly an order
of magnitude, up to a substantial fraction of the advertised window. Record
time-to-first-token and decode throughput separately, since prefill and decode
scale differently.

### Gap 3 (cheap add-on): prefix caching as a feature

Prefix caching was previously treated as a measurement contaminant and
suppressed with unique prompts. That was correct for benchmarking, but agent
workloads resend a large shared prompt prefix every turn, so in production it is
a genuine speedup that has never been quantified. Measure it at one operating
point by repeating a shared-prefix request with caching effective and defeated.

### Not planned

- Soak or stability testing: the remaining window is too short to support a
  meaningful stability claim.
- Further quality comparison: the existing single-sample check already showed
  both checkpoints fabricating specifics with equal confidence. More samples
  through inconsistent retrieval paths would not fix that design flaw.

### Method requirements carried forward

These follow from failures recorded earlier in this note and are binding on the
sweep:

- Unique prompt content per request unless prefix caching is the variable under
  test.
- Token counts taken from server-reported usage, never from streamed chunk
  counts.
- Repeat every operating point; report variance, and treat a single measurement
  as provisional.
- Capture the exact serving arguments and a rollback path before restarting the
  server.

### Risks

- Restarting the server interrupts the live agent lane. The launcher is
  known-good and only the sequence-slot value changes, so exposure is small,
  but the endpoint is briefly unavailable.
- If the restart fails, debugging consumes the remaining allocation. Mitigation:
  keep the prior launcher intact so the previous configuration can be restored
  with one command.
- A large sequence-slot value may reduce the KV cache below what long-context
  testing needs. If the two gaps conflict, they must be measured at different
  server configurations rather than silently compromised.

## Result: Concurrency Knee and Long-Context Behaviour (2026-08-02)

All figures below come from one harness on one device against the MoE
checkpoint. Output length was pinned so every request decodes an identical
number of tokens, prompt content was unique per request except where prefix
caching is the variable, and token counts came from server-reported usage.

The harness is `scripts/bench_capacity.py`. Exact serving flags, request
parameters, invocations, prompt-length calibration, per-configuration KV cache
figures, and the complete result tables (including concurrency rows omitted from
the summary below) are recorded under "Reproducing the capacity measurements" in
`notes/operations/hpc-vllm-agent-provider-findings.md`.

The harness was first reconciled against the previously recorded operating
point and reproduced it within normal run-to-run spread, so the two sessions'
numbers are comparable.

### The previously reported peak was an artifact of a configuration ceiling

Sequence slots were raised in two steps. At short prompts, aggregate throughput
kept climbing at every setting, and the observed "peak" tracked whichever slot
ceiling was configured:

| Concurrency | Aggregate tok/s | Per-stream tok/s | TTFT mean |
| --- | --- | --- | --- |
| 1 | 126 | 154 | 0.15 s |
| 8 | 534 | 108 | 0.27 s |
| 16 | 1,113 | 88 | 0.32 s |
| 32 | 2,345 | 74 | 0.30 s |
| 64 | 3,726 | 59 | 0.37 s |
| 128 | 5,343 | 46 | 0.45 s |
| 192 | 6,963 | 37 | 0.52 s |
| 256 | 7,850 | 32 | 0.58 s |

The figure recorded in the previous session as a peak is roughly a fifth of what
the same device sustains once the ceiling is lifted. It measured the
configuration, not the hardware.

**No aggregate knee exists within the tested range.** Throughput was still
climbing at the highest concurrency tested, and time-to-first-token remained
below a second throughout.

The real constraint is per-stream degradation, which is smooth and monotonic:
roughly 154 tok/s alone, 59 at sixty-four concurrent, 32 at two hundred
fifty-six. Single-device capacity is therefore set by **the per-stream speed the
operator is willing to accept**, not by a saturation cliff. Capacity planning
must state a per-stream floor before it can state a session count.

Increasing sequence slots sixteenfold cost about two percent of KV cache, so the
risk that a high slot count would crowd out long-context work did not
materialise.

### Short-prompt latency figures do not transfer to agent workloads

Holding concurrency at eight and sweeping prompt length:

| Prompt tokens | Aggregate tok/s | Per-stream tok/s | TTFT mean | TTFT p95 |
| --- | --- | --- | --- | --- |
| 1,031 | 836 | 110 | 0.33 s | 0.33 s |
| 4,106 | 618 | 94 | 0.59 s | 0.69 s |
| 16,410 | 448 | 57 | 1.48 s | 2.15 s |
| 32,887 | 322 | 41 | 2.48 s | 3.61 s |
| 65,857 | 162 | 21 | 5.82 s | 8.88 s |

Across the range, time-to-first-token grows about eighteenfold and aggregate
throughput falls roughly fivefold, at constant concurrency and constant output
length. The only variable is input size.

This revises the previous session's headline latency figures. Those were
measured with negligible prompts; at prompt sizes typical of an agent turn,
first-token latency is measured in seconds. Any capacity estimate drawn from the
short-prompt numbers overstates responsiveness for real agent use.

Prefill rate rose with input size up to roughly the mid range and then fell
back at the largest size tested, consistent with attention cost growing faster
than linearly. An earlier claim that prefill was compute-saturated was also too
low by several times; prefill scales considerably further than that claim
assumed.

### Prefix caching is a large, previously unmeasured win

At eight concurrent streams with a large shared prefix, compared with unique
prompts of the same size:

| Metric | Unique prompts | Shared prefix | Change |
| --- | --- | --- | --- |
| Aggregate tok/s | 448 | 656 | +46% |
| TTFT mean | 1.48 s | 0.77 s | ~2x faster |

Agent workloads resend a large common prompt prefix every turn, so this is the
production case rather than the benchmark case. Suppressing prefix caching was
correct for measuring the engine; it understates what agent traffic will see.

### What this changes

- Single-device session capacity is a per-stream-latency policy decision, not a
  fixed number. Publish the floor alongside the count.
- Sizing must be done at the prompt lengths actually in use. Short-prompt
  benchmarks flatter the system by roughly an order of magnitude on latency.
- Any measured "peak" throughput should be checked against the configured
  sequence-slot limit before being reported as a device characteristic.

### Method faults found in this round

- Early low-concurrency points disagreed between repeats by up to 121%, caused
  by warmup contaminating the first run. High-concurrency points were stable
  within a few percent. Discard or repeat the first measurement at each
  configuration.
- A pattern-based process kill matched the wrapper shell that was issuing it, so
  the kill terminated itself before reaching the server. The stop appeared to
  succeed silently while the old server kept holding its port, and the next
  launch failed with an address conflict. Kill by explicit process id, and
  confirm the port is released rather than trusting the stop command.
- A local copy of the launch script had drifted from the authoritative remote
  copy, disagreeing on both context length and served alias. The running
  server's own reported configuration is the only reliable source.
