# CPU Document Scraper Lane

This playbook implements the P120 CPU-first extraction lane for pre-extracted
document text. It sends independent chunks to an OpenAI-compatible endpoint,
validates structured output, retries the CPU route once by default, optionally
falls back to a separate GPU endpoint, and writes a durable JSONL checkpoint.

It is an evaluation tool, not authorization for a bulk corpus run. Do not put
model files, live endpoint URLs, tokens, raw backend logs, or private corpus
material in tracked files.

## Inputs and Output

The coordinator accepts either a P108 global index or one document chunk
manifest. Each chunk requires `chunk_id`, `page_start`, `page_end`, and either
`runtime_text_path` or `raw_text_path`. Text paths are resolved from
`--project-root`.

Each completed or failed chunk becomes one JSONL checkpoint entry. Checkpoints
are flushed and synced after every chunk, so a process crash loses at most an
active request. A rerun skips completed entries; use `--retry-failed` to retry
previous explicit failures. The response schema is in
`schemas/extraction_response.schema.json`.

The summary separates the required verdict dimensions:

- **Quality:** completed/failed chunks, validation success, and fallback use.
- **Protocol:** checkpointing, retry policy, isolation, and unprocessed work.
- **Economics:** validated chunks/hour, latency, retry/fallback rates, and local
  resource observations. Provider cost remains explicitly uncaptured.

## Profiles

Copy a profile template to an ignored local path and replace every placeholder:

```bash
cp playbooks/cpu_document_scraper/profiles/ollama.env.example \
  local/cpu-scraper.env
```

`ollama.env.example` is the initial CPU profile when an existing local Ollama
service is available. `llama_cpp.env.example` remains the alternative for a
dedicated `llama.cpp` server. The optional GPU profile is for adjudication only;
it must not be used as the default bulk lane.

### CPU-Only Ollama

Ollama may offload model layers to an available GPU unless the service is
configured otherwise. For a CPU lane that preserves the interactive GPU route,
place this systemd drop-in on the host, reload systemd, and restart only Ollama:

```ini
[Service]
Environment="CUDA_VISIBLE_DEVICES=-1"
Environment="ROCR_VISIBLE_DEVICES=-1"
Environment="GGML_VK_VISIBLE_DEVICES=-1"
```

Confirm the selected model reports `100% CPU` in `ollama ps` and that no
Ollama `llama-server` process appears in the NVIDIA compute-process list before
starting a benchmark. A service restart unloads any current Ollama model and
interrupts its clients.

## Smoke Run

Start with three chunks and one worker. This example writes ignored local
artifacts and does not expose a real route or credential:

```bash
python playbooks/cpu_document_scraper/scripts/run_scraper.py \
  --project-root . \
  --manifest benchmarks/document_library/tsa23_tsr/chunk_manifests/p108_2_global_index.json \
  --cpu-profile local/cpu-scraper.env \
  --output runtime/p120_cpu_smoke.jsonl \
  --summary runtime/p120_cpu_smoke_summary.json \
  --limit 3 \
  --workers 1
```

Scale only after recording the one-worker result: test 4, 8, then 16 workers.
Optimize validated chunks/hour, not raw token rate. Watch CPU oversubscription,
memory bandwidth, NUMA effects, queueing, JSON validity, and context truncation.

## Optional Fallback

To use the GPU only after both CPU attempts fail, add a locally stored profile:

```bash
  --gpu-profile local/gpu-fallback.env
```

The coordinator records every attempted lane and error. HTTP health alone is
not evidence of useful progress; a hung request is bounded by the configured
per-chunk timeout and becomes an explicit failed record if no route succeeds.

## External Access

Use a distinct public hostname for the CPU Ollama endpoint. One Cloudflare
Tunnel can publish multiple hostname-to-local-service mappings, so the new
Ollama hostname can target `http://127.0.0.1:11434` while the existing vLLM
hostname continues to target its own local service. Add a matching DNS route to
the same tunnel and protect the new hostname with an appropriate access policy.

Do not reuse a vLLM hostname with an `/ollama` path prefix unless a local proxy
also removes that prefix before requests reach Ollama.

## Benchmark Evidence

Record benchmark summaries under `benchmarks/document_library/p120_*` only
after sanitizing them. Compare CPU-only and CPU-first/GPU-fallback runs on the
same registered P108 subset. Use
`templates/p121_cpu_document_scraper_decision_packet.md` to state a decision;
do not claim an economics win without a measured comparison.
