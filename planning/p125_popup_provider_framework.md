# P125 Popup Remote LLM Provider Deployment Framework

Parent issue: #769  
Child task: TBD  
Branch: `feature/p125-popup-provider-framework`  
Status: active

## Purpose

P125 generalizes the per-cluster provider bring-up work into one portable
framework for standing up short-lived ("popup") OpenAI-compatible LLM
providers on shared HPC clusters and research clouds.

Every previous bring-up (Alliance FIR/Nibi/Rorqual, Arbutus OpenStack, UBC ARC
Sockeye) rebuilt the same five concerns by hand: find capacity, stage a model,
launch a server, expose it to the client, and keep it alive. Each rebuild
produced a different set of host-specific scripts and a different set of
avoidable defects.

The durable output is a **portable deployment contract** — a small set of
target descriptors, launch profiles, and readiness checks that work across
schedulers and access topologies — not another one-off launcher.

## Motivating Constraint

Development against shared clusters is gated by *access latency*, not by
compute capability. Observed: a four-GPU 24 h request queued roughly nineteen
hours; fresh submissions estimated ~6 days out; an expired Alliance allocation
blocked work for days. A framework that cannot tolerate multi-hour, unattended
waits is not usable.

Two consequences shape the design:

1. **Right-size before requesting.** The smallest allocation that fits the
   model schedules soonest. A 7B model that fits one GPU must not request four.
2. **Assume nobody is watching.** Bring-up must complete unattended whenever
   the allocation lands, hours after submission.

## Prior Art To Reuse

Do not rewrite these; generalize them.

| Asset | Reuse as |
| --- | --- |
| `playbooks/hpc_vllm/gpu_capacity_coordinator.md` | multi-cluster capacity watcher and submitter |
| `playbooks/vllm_blackwell/scripts/serve-native.sh` + `profiles/*.env` | the parameterized launch-profile layer |
| `playbooks/vllm_blackwell/scripts/wait-ready.sh` | readiness probe (already port-scanning and host-agnostic) |
| `playbooks/vllm_blackwell/scripts/watchdog-vllm-progress.py` | liveness/wedged-engine recovery |
| `playbooks/vllm_blackwell/scripts/bench_openai*.py` | post-bring-up verification |
| `playbooks/cloudflared_model_provider.md` | the public-ingress access mode |
| Sockeye P124 bridge + autostart pattern | the private SSH-forward access mode |

## Scope

In scope:

- a **target descriptor**: scheduler kind, submit shape, account, partition,
  GPU/VRAM shape, access mode, auth constraints;
- a **model fit preflight**: refuse or downsize a request that cannot fit the
  target's VRAM, using measured values rather than guesses;
- an **unattended bring-up sequence**: wait for capacity, stage, serve, expose,
  verify, report;
- a uniform **access-mode abstraction** covering at least private SSH
  forwarding and existing-tunnel public ingress;
- a **client contract** ensuring the served model name, context window, and
  tool-call capability match what the client is configured to expect.

Out of scope for P125:

- creating, migrating, or replacing tunnels, DNS, or connectors;
- requesting, extending, or renewing allocations;
- throughput, quality, or economics claims about any model.

## Safety Boundary

- Bind model servers to loopback on the provider host unless an already
  established ingress explicitly covers them.
- Reuse human-authenticated sessions on MFA-gated clusters; never attempt to
  authenticate interactively as an agent.
- Keep allocation records, endpoints, credentials, host paths, and raw logs in
  ignored local storage.
- Treat every cluster's scheduler as a shared resource: prefer the smallest
  viable request and the shortest viable walltime.

## Entry Checks

1. Confirm at least one target has a currently valid allocation or account.
2. Confirm a measured VRAM figure exists for the intended model, or measure one
   before requesting capacity.
3. Confirm the access mode for that target is already established.
4. Stop with a sanitized blocker if any entry check fails.

## Sequence

1. Extract the portable contract from the Sockeye and Alliance bring-ups and
   record where they genuinely differ.
2. Define the target descriptor and launch-profile schema.
3. Implement the fit preflight against the existing model catalog.
4. Implement unattended bring-up for one Alliance target, reusing the P124
   autostart pattern.
5. Verify with a bounded client request and a readiness/verification record.
6. Generalize to a second target to prove portability.

## Acceptance Boundary

P125 may conclude only that the framework brought a provider up unattended on
at least two distinct targets and served a bounded client request on each. It
may not claim throughput, model quality, cost, or general cluster
availability without separately captured evidence.

## Reporting

Record **Quality**, **Protocol**, and **Economics** separately. Queue waits and
allocation expiry are expected findings and must be reported as observations,
not as failures of the framework.
