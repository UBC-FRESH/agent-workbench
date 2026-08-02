# HPC and Repository Recovery Runbook — 2026-07-29

## Scope

This local operational note supports follow-up work after the P119/P121/P122
merges. It contains no live connection details. Keep actual cluster commands,
allocation records, endpoint URLs, credentials, and logs in ignored local
files.

## Recent Completed Work

- P119 service-hardening follow-up merged. It adds public-safe vLLM watchdog,
  service-template, secrets-path, and remote-access safety guidance.
- P121 CPU extraction implementation merged. It is implementation/test work,
  not a benchmark result.
- P122 merged. It adds generic multi-cluster GPU capacity planning plus safe
  provider-access patterns.

## Provider Access Decision

Use client-owned SSH forwarding first for short-lived allocations or personal
client use. Bind the provider to loopback on its host. Bind the SSH forward to
loopback on the client. Validate discovery and one small authenticated request
from the actual client application.

Use an existing Cloudflare Tunnel only when a stable shared endpoint is needed.
Before any DNS action, inspect the actual tunnel topology, verify the intended
ingress rule already exists, back up the live config, preserve the active
access path, and verify from an authorized client. Never create a replacement
connector as an experiment.

## GPU Allocation Decision

Before requesting capacity, write down:

- required GPUs per node and model-parallel layout;
- required GPU memory and architecture;
- minimum CPU/RAM/local-NVMe requirements;
- maximum acceptable walltime and queue wait;
- runtime archive checksum and staging plan;
- acceptance checks and expected client access mode.

Run the capacity coordinator in dry-run mode first. Put real cluster targets,
accounts, scripts, and paths only in an ignored local config. Use `--apply`
only after reviewing the proposed jobs. Treat one-GPU allocations as build or
smoke resources unless the model/service profile truly supports one GPU.

## Local Cleanup Checklist

- Make an ignored inventory before moving the stale worktree's contents.
- Mark each item as merged duplicate, raw local, future phase, or discard
  candidate.
- Move raw cluster exports, source captures, archives, and host-specific notes
  into ignored `local/` storage; keep a local manifest with origin and purpose.
- Do not delete the stale branch or a worktree until the manifest verifies that
  all unique material is either merged or preserved locally.
- Close superseded legacy issues only with an explicit successor reference.
- Finish on current `main` with a clean status.
