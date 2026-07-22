#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

source scripts/load-env.sh

host="${1:-127.0.0.1}"
start_port="${2:-${VLLM_PORT:-18000}}"
port_span="${VLLM_PORT_SCAN_SPAN:-10}"

echo "Waiting for vLLM on ${host}:${start_port}-$(( start_port + port_span - 1 ))"

for attempt in {1..240}; do
  for (( offset = 0; offset < port_span; offset++ )); do
    port=$(( start_port + offset ))
    url="http://${host}:${port}/v1/models"
    if curl -fs "$url" >/dev/null 2>&1; then
      echo "$port" > .vllm-ready-port
      echo "vLLM is ready at ${url}"
      exit 0
    fi
  done

  if (( attempt % 12 == 0 )); then
    echo "Still waiting after $(( attempt * 5 ))s..."
  fi

  sleep 5
done

echo "Timed out waiting for vLLM on ${host}:${start_port}-$(( start_port + port_span - 1 ))" >&2
exit 1
