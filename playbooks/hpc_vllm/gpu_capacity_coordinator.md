# Multi-cluster GPU capacity coordinator

`agent-workbench-gpu-capacity` watches Slurm clusters reachable over SSH and
collects short-lived allocations until a requested GPU target is covered.
It is intended for temporary inference or validation work, not a replacement
for a cluster scheduler's own fair-share policy.

## Safety contract

- The default mode is **dry-run**: it scans and reports actions, but sends no
  `sbatch` or `scancel` command.
- `--apply` is required before remote scheduler mutation.
- The state file records only job IDs created by this coordinator.
- It never cancels a running allocation. Once the target is met by running
  jobs, it cancels only coordinator-owned jobs still reported as pending.
- A coarse request shape can overshoot the exact GPU target after jobs start;
  the coordinator will not cancel an already allocated job to compensate.

## Configuration

Copy `templates/workbench_templates/gpu_capacity_clusters.example.yaml` to an
untracked local path. Fill in the per-cluster SSH target, submission script,
account, and request shape. Keep all real targets, accounts, and paths out of
tracked files.

Each `submission_script` must already exist on its own cluster and should be
safe to submit repeatedly. The coordinator supplies resource flags through
`sbatch`, so the script should avoid conflicting resource directives.

## Usage

First inspect the plan without changing any scheduler state:

```bash
agent-workbench-gpu-capacity \
  --config local/gpu_capacity_clusters.yaml \
  --state runtime/gpu-capacity-state.json \
  --target-gpus 8
```

Apply the planned submissions or cancellation of tracked pending jobs:

```bash
agent-workbench-gpu-capacity \
  --config local/gpu_capacity_clusters.yaml \
  --state runtime/gpu-capacity-state.json \
  --target-gpus 8 \
  --apply
```

Run the same command repeatedly to monitor arrivals. It records the observed
state of its jobs, adds new requests only while tracked running plus pending
capacity is below the target, and releases its own pending excess once enough
allocations are running.

## Evidence to retain

Capture the generated state file, dry-run/apply report, and each cluster's
Slurm job IDs. Report the result separately as:

- **Quality:** whether the requested GPU target was actually running and the
  intended workload passed its health checks.
- **Protocol:** whether only tracked pending jobs were cancelled and all
  scheduler mutations used `--apply`.
- **Economics:** allocation hours requested, allocated, and released.
