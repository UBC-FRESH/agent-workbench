# P124 Sockeye Private vLLM Provider Bring-up

Parent issue: #766  
Child task: #767  
Branch: `feature/p124-sockeye-vllm-provider-bringup`  
Status: parked — bring-up automated, awaiting scheduled allocation

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
   - Sockeye requires MFA, so an agent cannot open a new SSH session. Verify the
     human-authenticated master with `ssh -O check sockeye` first.
   - Add the forward to that live master with
     `ssh -O forward -L 18001:127.0.0.1:18125 sockeye`. Do not use `ssh -N -L`,
     a `LocalForward` entry, or `-o`/`-F` overrides.
   - Procedure and triage order: `notes/clusters/sockeye.md`.
4. Verify the same discovery and bounded request from the actual client.
5. Capture sanitized readiness, error, and resource evidence.

## Bring-up Automation and Current State — July 30, 2026

The first live bring-up reached a serving vLLM endpoint inside a Sockeye GPU
allocation. That allocation then ran its full walltime and was reaped
(`State=TIMEOUT`, a normal completion). The PoC stack could not recover
unattended, so the bring-up path was rebuilt before parking the phase.

What was proven:

- The three-hop access path is sound: client loopback forward -> login-node
  bridge -> `srun --overlap` into the allocation -> vLLM on compute-node
  loopback. vLLM never binds a routable interface.
- Client-owned SSH forwarding works without a new login by injecting the
  forward into the human-authenticated multiplexed master
  (`ssh -O forward`). MFA clusters cannot be authenticated by an agent.

PoC defects found and corrected (details in the local operations note):

- the bridge hardcoded a Slurm job id, so it broke silently when that
  allocation ended;
- bridge errors were discarded, making a dead allocation indistinguishable
  from a dead model;
- tensor parallelism was set to 4 for a 7B model that fits one 32 GB GPU,
  adding collective-communication failure modes for no benefit;
- model staging and server launch were manual steps, which is unworkable when
  queue waits are measured in hours;
- no tool-call parser was enabled, so agent-mode tool calls could not be
  parsed even with a working transport;
- the client declared a context window far larger than the server served.

The rebuilt stack stages the model, serves it, and re-establishes the bridge
unattended when an allocation lands, and discovers the job id at runtime.

Remaining acceptance evidence is blocked only on scheduler queue time: the
replacement allocation is queued and expected to start roughly nineteen hours
after submission. Until a bounded client request is served end-to-end, P124
must not be reported as complete.

## Acceptance Boundary

P124 may conclude only that the selected provider starts, remains private, and
serves a bounded client request through SSH forwarding. It may not claim
throughput, long-context capability, tool-use compatibility, model quality,
provider availability, or economics without separate captured evidence.

## Reporting

Record **Quality**, **Protocol**, and **Economics** separately. Any inability
to start or access the provider is a valid blocker result and must preserve the
current access path.
