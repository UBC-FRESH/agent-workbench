#!/usr/bin/env bash
set -euo pipefail

VLLM_ENV_FILE="${VLLM_ENV_FILE:-.env}"
if [[ ! -f "$VLLM_ENV_FILE" ]]; then
  echo "Missing $VLLM_ENV_FILE." >&2
  echo "Copy a profile from profiles/*.env.example to .env, or set VLLM_ENV_FILE." >&2
  exit 1
fi

source "$VLLM_ENV_FILE"

DEFAULT_WORKDIR="${VLLM_REMOTE_WORKDIR:-${PWD}}"
if [[ -n "${VLLM_SECRETS_ENV_OVERRIDE:-}" ]]; then
  VLLM_SECRETS_ENV="$VLLM_SECRETS_ENV_OVERRIDE"
elif [[ -n "${VLLM_SECRETS_ENV:-}" ]]; then
  VLLM_SECRETS_ENV="$VLLM_SECRETS_ENV"
else
  if command -v python3 >/dev/null 2>&1; then
    VLLM_SECRETS_ENV="$(python3 - <<'PY'
import os
from pathlib import Path
import sys
repo_root = Path(os.getcwd())
if os.path.exists('pyproject.toml'):
    repo_root = Path.cwd()
else:
    repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))
from scripts.util.user_secrets import resolve_secrets_path
print(resolve_secrets_path(default_workdir=os.environ.get('VLLM_REMOTE_WORKDIR', os.getcwd())))
PY
)"
  else
    VLLM_SECRETS_ENV="$DEFAULT_WORKDIR/.cache/secrets.env"
  fi
fi
if [[ -f "$VLLM_SECRETS_ENV" ]]; then
  source "$VLLM_SECRETS_ENV"
fi

if [[ -n "${HF_TOKEN:-}" ]]; then
  export HF_TOKEN
  export HUGGING_FACE_HUB_TOKEN="${HUGGING_FACE_HUB_TOKEN:-$HF_TOKEN}"
fi

export AGENT_WORKBENCH_SECRETS_ENV="${VLLM_SECRETS_ENV}"
