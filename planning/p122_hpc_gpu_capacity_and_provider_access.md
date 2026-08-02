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
