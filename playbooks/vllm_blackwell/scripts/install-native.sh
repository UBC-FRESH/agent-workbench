#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m venv .venv
source .venv/bin/activate

source scripts/env-native.sh
python -m pip install --upgrade pip wheel setuptools
python -m pip install uv

if command -v module >/dev/null 2>&1; then
  module load cuda/12.9 >/dev/null 2>&1 || true
fi

if command -v nvcc >/dev/null 2>&1 || [[ -n "${CUDA_HOME:-}" ]] || [[ -n "${CUDA_PATH:-}" ]] || command -v module >/dev/null 2>&1; then
  python -m pip install torch==2.11.0+computecanada torchvision==0.26.0+computecanada
  uv pip install vllm --torch-backend auto
else
  uv pip install vllm --torch-backend auto
fi

python scripts/probe_runtime.py
