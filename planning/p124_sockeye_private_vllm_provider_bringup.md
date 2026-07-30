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

## Implementation Decision — July 30, 2026

P124 remains **active** under parent issue #766 and child task #767. The
preflight findings are ordinary bring-up work, not a phase blocker:

- Existing staged launchers bind to all network interfaces. P124 will retain
  them as references and create an ignored, allocation-local wrapper that
  binds only to provider-host loopback.
- The selected allocation's default environment does not expose the intended
  vLLM command. P124 will first locate and reuse a suitable staged runtime; if
  none exists, it will create an isolated, version-pinned runtime compatible
  with the selected GPU architecture.

No installer ran, no launch script ran, no listener was created, and no access
topology changed during preflight. The next work is to implement the wrapper,
validate local discovery and one bounded request, then verify client-owned SSH
forwarding.

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
