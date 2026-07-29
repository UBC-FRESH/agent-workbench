# P121 CPU Document Scraper Implementation

**Parent issue:** #758
**Child task:** #759
**Branch:** `feature/p121-cpu-document-scraper`

P121 packages a CPU-first document-extraction workflow without consuming an
interactive GPU model service. It includes a public-safe schema, CPU and
optional GPU-fallback profiles, a resumable JSONL coordinator, controlled
OpenAI-compatible endpoint tests, and a decision-packet template.

The coordinator resolves ignored runtime text from a manifest, validates each
structured response, retries a CPU failure once, optionally records a
GPU-fallback attempt, and resumes from append-safe checkpoints.

## Evidence boundary

- Controlled endpoint tests establish request, retry, fallback, checkpoint, and
  summary behavior only.
- No productive corpus run, live provider URL, credentials, raw document text,
  hardware-specific route, throughput result, or economics claim is tracked.
- A future registered benchmark must decide the route using measured quality,
  latency, retries, fallback use, and resource observations.
