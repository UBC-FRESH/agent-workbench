#!/usr/bin/env bash
set -euo pipefail

VLLM_LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -n "${VLLM_CUDA_HOME_OVERRIDE:-}" ]]; then
  VLLM_CUDA_HOME="$VLLM_CUDA_HOME_OVERRIDE"
elif [[ -n "${CUDA_HOME:-}" ]]; then
  VLLM_CUDA_HOME="$CUDA_HOME"
elif [[ -n "${CUDA_PATH:-}" ]]; then
  VLLM_CUDA_HOME="$CUDA_PATH"
else
  if command -v nvcc >/dev/null 2>&1; then
    NVCC_BIN="$(command -v nvcc)"
    VLLM_CUDA_HOME="$(dirname "$(dirname "$NVCC_BIN")")"
  elif command -v module >/dev/null 2>&1; then
    if module avail cuda 2>/dev/null | grep -q 'cuda/'; then
      module load cuda >/dev/null 2>&1 || true
    fi
    if command -v nvcc >/dev/null 2>&1; then
      NVCC_BIN="$(command -v nvcc)"
      VLLM_CUDA_HOME="$(dirname "$(dirname "$NVCC_BIN")")"
    else
      VLLM_CUDA_HOME="$VLLM_LAB_DIR/.venv/lib/python3.12/site-packages/nvidia/cu13"
    fi
  else
    VLLM_CUDA_HOME="$VLLM_LAB_DIR/.venv/lib/python3.12/site-packages/nvidia/cu13"
  fi
fi

DEFAULT_WORKDIR="${VLLM_REMOTE_WORKDIR:-${PWD}}"
VLLM_SHARED_CACHE="${VLLM_SHARED_CACHE:-$DEFAULT_WORKDIR/.cache/vllm}"

export HF_HOME="${HF_HOME:-$VLLM_SHARED_CACHE/huggingface}"
export HUGGINGFACE_HUB_CACHE="${HUGGINGFACE_HUB_CACHE:-$HF_HOME/hub}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-$HF_HOME/transformers}"
export HF_XET_CACHE="${HF_XET_CACHE:-$HF_HOME/xet}"
export VLLM_CACHE_ROOT="${VLLM_CACHE_ROOT:-$VLLM_SHARED_CACHE/vllm-cache}"
export FLASHINFER_WORKSPACE_BASE="${FLASHINFER_WORKSPACE_BASE:-$VLLM_SHARED_CACHE/flashinfer}"
export FLASHINFER_CUBIN_DIR="${FLASHINFER_CUBIN_DIR:-$FLASHINFER_WORKSPACE_BASE/.cache/flashinfer/cubins}"
export FLASHINFER_WORKSPACE_DIR="${FLASHINFER_WORKSPACE_DIR:-$FLASHINFER_WORKSPACE_BASE}"
export TORCHINDUCTOR_CACHE_DIR="${TORCHINDUCTOR_CACHE_DIR:-$VLLM_CACHE_ROOT/torchinductor}"
export TRITON_CACHE_DIR="${TRITON_CACHE_DIR:-$VLLM_CACHE_ROOT/triton}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$VLLM_SHARED_CACHE/xdg-cache}"
export TMPDIR="${TMPDIR:-$VLLM_SHARED_CACHE/tmp}"

mkdir -p \
  "$HF_HOME" \
  "$HUGGINGFACE_HUB_CACHE" \
  "$TRANSFORMERS_CACHE" \
  "$HF_XET_CACHE" \
  "$VLLM_CACHE_ROOT" \
  "$FLASHINFER_WORKSPACE_BASE" \
  "$FLASHINFER_CUBIN_DIR" \
  "$FLASHINFER_WORKSPACE_DIR" \
  "$TORCHINDUCTOR_CACHE_DIR" \
  "$TRITON_CACHE_DIR" \
  "$XDG_CACHE_HOME" \
  "$TMPDIR"

if [[ -d "$VLLM_CUDA_HOME" ]]; then
  export CUDA_HOME="$VLLM_CUDA_HOME"
  export CUDA_PATH="$VLLM_CUDA_HOME"
  export PATH="$VLLM_CUDA_HOME/bin:$PATH"
  export LD_LIBRARY_PATH="$VLLM_CUDA_HOME/lib:$VLLM_CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"
fi

export VLLM_USE_FLASHINFER_SAMPLER="${VLLM_USE_FLASHINFER_SAMPLER:-0}"
