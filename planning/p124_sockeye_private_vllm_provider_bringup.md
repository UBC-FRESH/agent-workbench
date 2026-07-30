# P124 Sockeye Private vLLM Provider Bring-up

Parent issue: #766  
Child task: #767  
Branch: `feature/p124-sockeye-vllm-provider-bringup`  
Status: active

## Purpose

P124 establishes a private, OpenAI-compatible vLLM provider within an existing
approved Sockeye allocation. It is a readiness and client-access phase, not a
benchmark or an external-publication phase.

P123 CPU scraper benchmark and route decision is parked until the provider
passes P124 readiness checks. P124 must not advance P123's registered subsets,
benchmark claims, or decision packet.

## Safety Boundary

- Use the allocation's supported in-allocation execution mechanism; do not
  request, extend, cancel, replace, or otherwise modify allocations.
- Bind vLLM only to loopback on the provider host.
- Use client-owned SSH forwarding from a client loopback port to the provider
  loopback port for client access.
- Do not create, modify, test, migrate, or replace Cloudflare tunnels, DNS,
  connectors, or public ingress.
- Keep allocation records, endpoint values, credentials, host paths, model
  cache locations, raw prompts, and raw logs in ignored local storage.

## Entry Checks

1. Confirm an existing allocation has the required GPU shape, free memory, and
   remaining walltime.
2. Inspect the selected staged runtime, model artifacts, and launch script
   without promoting host-specific material into tracked files.
3. Confirm that the requested model/profile is compatible with the allocation
   GPU architecture and memory shape.
4. Stop with a sanitized blocker if any entry check fails.

## Preflight Status — July 30, 2026

**Blocked before launch.** The inspected staged vLLM launchers bind to all
network interfaces, which violates P124's loopback-only boundary. The selected
allocation's default environment also lacks a usable current-vLLM runtime: it
does not expose `vllm`, a newer Python interpreter, a Python module, or an
environment manager. The default Python has virtual-environment support but is
not sufficient for the selected current-vLLM installation path.

No installer ran, no launch script ran, no listener was created, and no access
topology changed.

### Required Retry Prerequisites

1. Stage a version-pinned vLLM runtime that is validated for the selected GPU
   architecture and provides a supported Python version.
2. Create an ignored, allocation-local wrapper that binds only to provider-host
   loopback; do not edit a public-binding launcher in place.
3. Re-run the entry checks, local discovery, and one bounded request before
   attempting client SSH forwarding.

## Bring-up Sequence

1. Start the selected vLLM command only inside the existing allocation and
   bind it to provider-host loopback.
2. Verify local model discovery and one bounded request from the provider host.
3. Open a client-owned loopback SSH forward.
4. Verify the same discovery and bounded request from the actual client.
5. Capture sanitized readiness, error, and resource evidence.

## Acceptance Boundary

P124 may conclude only that the selected provider starts, remains private, and
serves a bounded client request through SSH forwarding. It may not claim
throughput, long-context capability, tool-use compatibility, model quality,
provider availability, or economics without separate captured evidence.

## Reporting

Record **Quality**, **Protocol**, and **Economics** separately. Any inability
to start or access the provider is a valid blocker result and must preserve the
current access path.
