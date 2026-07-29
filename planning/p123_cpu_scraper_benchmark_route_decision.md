# P123 CPU Scraper Benchmark and Route Decision

Parent issue: #764  
Child task: #765  
Branch: `feature/p123-cpu-scraper-benchmark-route-decision`  
Status: planned

## Purpose

P123 evaluates the already-merged P121 CPU document-scraper implementation
against a registered subset and produces one evidence-backed route decision.
It is the successor to the unimplemented benchmark scope formerly tracked in
legacy issue #752.

P121 provided the extraction contract, CPU and optional fallback profiles,
resumable coordinator, controlled endpoint tests, and decision-packet template.
It did not run a productive corpus job, benchmark a live endpoint, or establish
a quality, throughput, economics, or provider-availability result.

## Entry Requirements

- Register smoke, representative pilot, and field-level audit subsets before
  execution.
- Record the local endpoint profile, model provenance, timeout policy, and
  worker level in a sanitized manifest.
- Keep raw texts, endpoint details, credentials, allocation records, host
  paths, and raw logs in ignored local storage.
- Use client-owned loopback SSH forwarding if remote access is required. Do
  not create or modify public ingress, Cloudflare tunnels, or connectors.

## Measurement Sequence

1. Run a one-worker CPU smoke evaluation and preserve sanitized checkpoint and
   summary artifacts.
2. Review parseability, schema validity, retries, latency, throughput, and
   local resource observations.
3. Increase concurrency only with recorded evidence at each worker level.
4. Use GPU fallback only when explicitly approved and when it cannot impair
   interactive-service commitments.
5. Audit a pre-registered sample against an approved reference.
6. Publish one sanitized route-decision packet.

## Decision Outcomes

The final packet must recommend exactly one of:

- CPU-first with guarded GPU fallback;
- GPU-only;
- another CPU backend or model;
- a document-type split; or
- no-go pending a different approach.

It must report **Quality**, **Protocol**, and **Economics** separately and
identify every evidence limitation. No cost, performance, quality, context,
tool-use, or provider-availability claim is valid without captured evidence.

## Closeout

Before closing #765 or #764, reconcile this note, `ROADMAP.md`,
`CHANGE_LOG.md`, issue bodies, sanitized artifacts, and the phase PR. Close
the parent only after the PR merges to `main`.
