#!/usr/bin/env bash
set -euo pipefail

VLLM_ENV_FILE="${VLLM_ENV_FILE:-.env}"
if [[ ! -f "$VLLM_ENV_FILE" ]]; then
  echo "Missing $VLLM_ENV_FILE." >&2
  echo "Copy a profile from profiles/*.env.example to .env, or set VLLM_ENV_FILE." >&2
  exit 1
fi

source "$VLLM_ENV_FILE"

VLLM_SECRETS_ENV="${VLLM_SECRETS_ENV_OVERRIDE:-${VLLM_SECRETS_ENV:-/srv/shared-data/vllm/secrets.env}}"
if [[ -f "$VLLM_SECRETS_ENV" ]]; then
  source "$VLLM_SECRETS_ENV"
fi

if [[ -n "${HF_TOKEN:-}" ]]; then
  export HF_TOKEN
  export HUGGING_FACE_HUB_TOKEN="${HUGGING_FACE_HUB_TOKEN:-$HF_TOKEN}"
fi
