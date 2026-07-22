# Blackwell vLLM Agent Endpoint Playbook

This playbook packages the public-safe parts of a local vLLM deployment used
for Agent Workbench multi-agent trials on a single NVIDIA RTX PRO 6000
Blackwell-class GPU.

The observed deployment serves one OpenAI-compatible Qwen 3.6 27B NVFP4 model
alias to VS Code Copilot custom agents. Role separation remains an instruction
and authority contract; the endpoint is one shared model service.

Do not commit live endpoint URLs, Cloudflare configuration, Hugging Face tokens,
`.env` files, model blobs, caches, or raw logs. The files here are templates and
operator aids only.

## Included Files

- `profiles/qwen36-27b-nvfp4.env.example` — stable BF16-KV / FlashAttention
  profile, useful as a rollback and single-stream baseline.
- `profiles/qwen36-27b-nvfp4-copilot.env.example` — stable profile with
  Copilot/OpenAI-client-compatible content output.
- `profiles/qwen36-27b-nvfp4-flashinfer-copilot.env.example` — multi-agent
  profile using FlashInfer attention, FP8 KV cache, MTP speculative decoding,
  prefix caching, and Copilot-compatible output.
- `scripts/serve-native.sh` — launches `vllm serve` from a selected profile.
- `scripts/bench_openai.py` and `scripts/bench_openai_concurrent.py` — small
  OpenAI-compatible endpoint smoke and concurrency benchmarks.
- `scripts/watch-vllm.sh` — compact operator dashboard for server/GPU/load
  monitoring.
- `systemd/vllm-blackwell.service.example` — host-service template with
  bounded auto-restart on failure.

## Recommended Multi-Agent Profile

Create the local virtual environment first:

```bash
cd playbooks/vllm_blackwell
./scripts/install-native.sh
```

For VS Code Copilot custom-agent workflows, then start with:

```bash
cd playbooks/vllm_blackwell
VLLM_ENV_FILE=profiles/qwen36-27b-nvfp4-flashinfer-copilot.env.example \
  ./scripts/serve-native.sh
```

This profile keeps response chunks in normal `message.content` /
`delta.content` shape rather than Qwen reasoning-only fields. That compatibility
choice matters for OpenAI-style clients that do not consume vLLM/Qwen-specific
`reasoning` streams.

The profile assumes model and compile caches live outside the repository, by
default under `/srv/shared-data/vllm`. Override the cache variables in a local
`.env` or copied profile if your host uses a different shared-data mount.
Set `VLLM_SECRETS_ENV_OVERRIDE` when a launch or validation run must bypass the
profile's default external secrets file.

The install helper intentionally follows the current compatible vLLM release
rather than pinning a host-independent version. Operators should record the
installed `torch`, CUDA, and vLLM versions from `scripts/probe_runtime.py` when
capturing host-specific evidence.

## Host Prerequisites

- Python 3.12-compatible vLLM environment.
- NVIDIA driver and CUDA runtime suitable for Blackwell.
- Sufficient shared storage for Hugging Face weights and compile caches.
- For FlashInfer JIT on Blackwell, a full CUDA 13 toolkit tree such as
  `/usr/local/cuda-13.0` with headers and libraries available.
- A Hugging Face token stored outside the repo if higher Hub rate limits are
  needed. Use `scripts/set-hf-token.sh` or an equivalent local secret manager.

## VS Code Custom Endpoint Shape

Configure the client as a Chat Completions endpoint. Use a full
`/v1/chat/completions` URL in the client model configuration and keep the model
id aligned with the served model alias:

```json
{
  "vendor": "customendpoint",
  "name": "Fresh vLLM",
  "apiType": "chat-completions",
  "apiKey": "dummy-or-local-secret",
  "models": [
    {
      "id": "qwen3.6-27b-nvfp4",
      "name": "Qwen 3.6 27B NVFP4",
      "url": "https://example.invalid/v1/chat/completions",
      "toolCalling": true,
      "streaming": true,
      "maxInputTokens": 258000,
      "maxOutputTokens": 4096
    }
  ]
}
```

Replace the example URL with a local or authenticated route. Do not commit live
provider URLs or access headers.

## Smoke Checks

After launch:

```bash
./scripts/wait-ready.sh 127.0.0.1 18000
curl http://127.0.0.1:18000/v1/models
python scripts/bench_openai.py \
  --base-url http://127.0.0.1:18000/v1 \
  --model qwen3.6-27b-nvfp4
```

For concurrent long-context pressure:

```bash
python scripts/bench_openai_concurrent.py \
  --base-url http://127.0.0.1:18000/v1 \
  --model qwen3.6-27b-nvfp4 \
  --requests 8 \
  --concurrency 8 \
  --context-words 80000 \
  --max-tokens 64
```

Watch the live service:

```bash
./scripts/watch-vllm.sh
SHOW_RECENT=0 ./scripts/watch-vllm.sh
HEALTH_CHECK=1 ./scripts/watch-vllm.sh
VERBOSE=1 ./scripts/watch-vllm.sh
```

## Host Service

For routine use, run the endpoint under `systemd` rather than an interactive
shell. The template in `systemd/vllm-blackwell.service.example` preserves the
same profile and adds bounded recovery:

- `Restart=on-failure` revives the API after an engine process crash.
- `RestartSec=15s` avoids a tight restart loop.
- `StartLimitIntervalSec=900` and `StartLimitBurst=3` stop repeated crashes
  from hiding a persistent kernel or configuration fault.
- stdout/stderr go to journald, and CUDA coredumps remain in the configured
  external shared-data directory.

Adapt the template before installing:

- Set `User` and `Group` to the local runtime account.
- Set `WorkingDirectory` to the copied vLLM lab checkout.
- Set `ExecStart` to that checkout's `scripts/serve-native.sh`.
- Point `VLLM_ENV_FILE` at a local, untracked profile with real cache and
  secret-file paths.

Example install flow:

```bash
sudo install -m 0644 systemd/vllm-blackwell.service.example \
  /etc/systemd/system/vllm-blackwell.service
sudo systemctl daemon-reload
sudo systemctl enable --now vllm-blackwell.service
systemctl status vllm-blackwell.service
./scripts/wait-ready.sh 127.0.0.1 18000
```

Common operations:

```bash
systemctl status vllm-blackwell.service
journalctl -u vllm-blackwell.service -f
sudo systemctl restart vllm-blackwell.service
sudo systemctl stop vllm-blackwell.service
```

## Observed Operating Guidance

The FlashInfer/FP8-KV profile is optimized for concurrent, long-context agent
work rather than fastest single-stream decoding. In the observed host run, vLLM
reported roughly 1.7M GPU KV-cache tokens and about 6.6x theoretical
concurrency at 262K context. Agent Hub sessions also showed high prefix-cache
reuse during repeated Copilot-agent context turns.

Use bounded concurrency, not indiscriminate fan-out:

- Normal fan-out: 2-4 active agents for independent read/diagnostic work.
- Burst fan-out: up to about 6 agents for read-only or clearly partitioned
  work.
- Avoid sustained fan-out above the configured `VLLM_MAX_NUM_SEQS` unless the
  operator is deliberately stress-testing.
- Serialize tasks that mutate the same files, require ordered decisions, run
  destructive commands, restart services, or perform final synthesis.

## Public-Safety Boundary

Track only reusable deployment logic and sanitized findings. Keep these local:

- `.env`, `.env.*`, `*.env` files with real secrets or endpoints;
- Hugging Face tokens and Cloudflare access/service-token headers;
- downloaded model blobs and cache directories;
- raw vLLM logs, client transcripts, and private session archives;
- host-specific reverse-proxy configuration.

## Validation Boundary

Repository validation covers shell parsing, Python compilation, CLI argument
smoke checks, sanitized path and secret scans, and mocked OpenAI-compatible
streaming responses. A real launch still requires a suitable Blackwell host,
CUDA toolkit, model access, and external cache storage.
