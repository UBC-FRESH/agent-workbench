#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

source scripts/load-env.sh

host="${VLLM_BENCH_HOST:-127.0.0.1}"
port="${VLLM_PORT:-18000}"
model="${VLLM_SERVED_MODEL_NAME:-qwen-coder}"

./scripts/wait-ready.sh "$host" "$port"
ready_port="$(cat .vllm-ready-port)"

source .venv/bin/activate
python scripts/bench_openai.py \
  --base-url "http://${host}:${ready_port}/v1" \
  --model "$model" \
  "$@"
