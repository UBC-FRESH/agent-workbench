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
