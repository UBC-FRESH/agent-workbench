# FIR (Alliance Canada) cluster notes

## Access and identity

- Host: fir.alliancecan.ca
- Account used during testing: def-gep_gpu
- Access method: SSH via the local Alliance config and key setup

## Observed scheduler and GPU facts

These notes are based on the Slurm probes run on 2026-07-26.

### Interactive GPU pool

- The interactive GPU partition is `gpubase_interac`.
- It appears to be a very small pool: a single interactive node (`fc11020`) was visible.
- The visible GRES shape for that partition is a MIG-style H100 resource layout, including:
  - `gpu:nvidia_h100_80gb_hbm3_3g.40gb:4(S:2-3)`
  - `gpu:nvidia_h100_80gb_hbm3_2g.20gb:4(S:2-3)`
  - `gpu:nvidia_h100_80gb_hbm3_1g.10gb:8(S:2-3)`
- This is important because it means the interactive pool is not just "one GPU" in a generic sense; it is a constrained, shared pool with a specific partition structure.

### Broader GPU partitions

- The broader GPU partitions include `gpubase_bygpu_b4`, `gpubase_bygpu_b5`, and similar nodes.
- These are more suitable for batch jobs than for popup-style interactive launches.

## What we learned from trial and error

### 1. Generic interactive requests are weak

- A simple request such as `--gres=gpu:h100:1` was not a strong priority shape for this cluster.
- It queued and did not provide a reliable popup-style experience for bringing up a vLLM endpoint.

### 2. The interactive pool is not a robust path for vLLM bootstrap smoke tests

- For a short-lived LLM provider or local model-serving test, the interactive pool can be too small or too contested.
- The scheduler behavior is not purely about whether the resource exists; it is also about whether the request shape is attractive enough to be scheduled quickly.

### 3. Batch submission is the better default

- The batch workflow with `sbatch` was the first reliable path that actually reached the scheduler successfully.
- The most promising request shape was a short batch job using a broader GPU partition and an explicit GRES request.
- A fresh FIR smoke test on 2026-07-26 submitted successfully as job `51278274` and ran on node `fc10702`, proving that the scheduler can allocate a GPU for a short job.
- A follow-up torch/CUDA probe job (`51278340`) remained pending with reason `Resources`, which shows the main current blocker is cluster contention rather than a syntax or submission error in the batch script.

## Recommended request shape for future FIR smoke tests

For short vLLM bootstrap or model-provider smoke tests, use:

- partition: `gpubase_bygpu_b4` (or a similar broader GPU partition)
- account: `def-gep_gpu`
- wall time: 30 minutes or less
- GRES: an explicit MIG-style H100 request such as `gpu:nvidia_h100_80gb_hbm3_3g.40gb:1`
- batch submission via `sbatch`

This is a pragmatic compromise: more scheduler-friendly than a tiny interactive request, while still short enough for a smoke test.

## Durable takeaway

Do not assume that a small interactive GPU request on FIR will launch quickly. For this cluster, the scheduler behavior suggests that popup-style vLLM provider requests should be treated as opportunistic, short-lived jobs and routed through batch submission rather than interactive allocation.

The immediate operational lesson is: submit the job, watch for `Resources` vs `Priority`, and treat queue delay as a normal part of FIR GPU access rather than a sign that the environment setup is broken.

## Access reminder

- The home-based secrets file for Alliance access is ~/.config/agent-workbench/secrets.env.
- That file should contain CCDB_USERNAME and CCDB_PASSWORD.
- For first-time login to systems such as Nibi, the interactive Duo MFA path must be completed once and approved on the user's iPhone.
