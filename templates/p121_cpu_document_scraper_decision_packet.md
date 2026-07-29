# P120 CPU Document Scraper Decision Packet

## Scope

- Run ID:
- Registered manifest and chunk subset:
- CPU backend and model:
- CPU concurrency:
- Optional GPU fallback model:
- Comparison baseline:

## Quality Verdict

- Parseable structured output rate after CPU retry:
- Valid records after GPU fallback:
- Explicit failure count:
- Registered audit sample and agreement result:
- Verdict: accepted / rejected / incomplete

## Protocol Verdict

- Checkpoint and resume evidence:
- Per-chunk timeout and retry policy:
- CPU/GPU endpoint isolation evidence:
- Sanitization and private-data review:
- Verdict: accepted / rejected / incomplete

## Economics Verdict

- Validated chunks/hour:
- Mean and p95 chunk latency:
- CPU retry rate and GPU fallback rate:
- CPU/RAM/NUMA observations:
- Provider usage or explicitly uncaptured costs:
- Verdict: measured improvement / no improvement / insufficient evidence

## Recommendation

Choose exactly one:

- Proceed with CPU-first/GPU-fallback bulk extraction.
- Use GPU-only because CPU quality or throughput is inadequate.
- Try a different CPU backend or model before scaling.
- Split document types by model or backend.

## Evidence

- Sanitized run summary:
- Sanitized JSONL checkpoint or failure sample:
- Audit artifact:
- Known limitations and follow-up:
