# Rorqual (Alliance Canada) cluster notes

## Access and identity

- Host: rorqual.alliancecan.ca
- Access status: SSH access confirmed
- Current role: candidate next cluster to test while FIR is queued

## Observed scheduler and GPU facts

These notes are based on the Slurm probes run on 2026-07-26.

- The cluster exposes CPU partitions such as `cpubase_interac` and several `cpubase_bynode_*` queues.
- GPU-facing partitions are visible, including `gpubase_interac` and `gpubase_bygpu_b1` through `gpubase_bygpu_b5`.
- The visible `gpubase_interac` shape includes a large number of H100-style resources, with many nodes available in the GPU partition family.
- Active GPU jobs were visible during the probe, so the cluster is clearly servicing GPU workloads rather than only exposing empty queues.

## Why Rorqual is a good next target

- We already have SSH access to it.
- It appears to expose a broader GPU scheduling surface than FIR's small interactive pool.
- It is a good second data point for evaluating whether the same vLLM bootstrap pattern behaves differently on a different Alliance cluster.

## Trial result from 2026-07-26

- The initial attempt to use `gpubase_interac` failed at the Slurm submission boundary, even though the partition exists.
- A later probe succeeded on `gpubase_bygpu_b1` with a batch submission and a MIG-style GRES request:
  - partition: `gpubase_bygpu_b1`
  - account: `def-gep_gpu`
  - GRES: `gpu:nvidia_h100_80gb_hbm3_3g.40gb:1`
- The resulting vLLM launch job was accepted by Slurm as job `17477065`, but it remained in `PENDING` with reason `Priority` rather than starting immediately.
- A fresh smoke test on 2026-07-26 submitted a new job `17480607` with the same shape. It also remained `PENDING` with reason `Priority`, which confirms that Rorqual accepts the request but still requires queue time.
- A follow-up submission to `gpubase_bygpu_b2` as job `17480633` behaved the same way: the request entered the queue but remained `PENDING` with reason `Priority`.
- This is an important distinction from FIR: Rorqual can accept the request, but the queue still imposes a priority delay, so the launch is not necessarily instantaneous.

## What to test next

Use the same short-lived smoke-test workflow as on FIR:

1. Submit a short batch allocation rather than relying on an interactive popup.
2. Keep the wall time short and realistic.
3. Record the partition, GRES, and time-to-running for comparison.
4. Compare whether Rorqual gives a better or worse path to a reachable model endpoint.

## Current recommendation

Treat Rorqual as the next best cluster to probe after FIR while the FIR queue is still occupied. It is the most practical next step because it is already accessible and has a visibly broader GPU scheduling surface.
