#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

source scripts/load-env.sh

if [[ -z "${VLLM_MODEL:-}" ]]; then
  echo "Set VLLM_MODEL in $VLLM_ENV_FILE to a Hugging Face safetensors model." >&2
  exit 1
fi

source .venv/bin/activate
source scripts/env-native.sh

export VLLM_SLEEP_WHEN_IDLE="${VLLM_SLEEP_WHEN_IDLE:-0}"
export VLLM_LOG_STATS_INTERVAL="${VLLM_LOG_STATS_INTERVAL:-10}"
if [[ -n "${SAFETENSORS_FAST_GPU:-}" ]]; then
  export SAFETENSORS_FAST_GPU
fi
if [[ -n "${VLLM_TEST_FORCE_FP8_MARLIN:-}" ]]; then
  export VLLM_TEST_FORCE_FP8_MARLIN
fi

args=(
  serve "$VLLM_MODEL"
  --served-model-name "${VLLM_SERVED_MODEL_NAME:-qwen-coder}"
  --host "${VLLM_HOST:-0.0.0.0}"
  --port "${VLLM_PORT:-8000}"
  --max-model-len "${VLLM_MAX_MODEL_LEN:-32768}"
  --gpu-memory-utilization "${VLLM_GPU_MEMORY_UTILIZATION:-0.88}"
  --max-num-seqs "${VLLM_MAX_NUM_SEQS:-16}"
  --max-num-batched-tokens "${VLLM_MAX_NUM_BATCHED_TOKENS:-8192}"
)

if [[ -n "${VLLM_GENERATION_CONFIG:-}" ]]; then
  args+=(--generation-config "$VLLM_GENERATION_CONFIG")
fi

if [[ -n "${VLLM_QUANTIZATION:-}" ]]; then
  args+=(--quantization "$VLLM_QUANTIZATION")
fi

if [[ -n "${VLLM_DTYPE:-}" ]]; then
  args+=(--dtype "$VLLM_DTYPE")
fi

if [[ -n "${VLLM_LOAD_FORMAT:-}" ]]; then
  args+=(--load-format "$VLLM_LOAD_FORMAT")
fi

if [[ -n "${VLLM_ATTENTION_BACKEND:-}" ]]; then
  args+=(--attention-backend "$VLLM_ATTENTION_BACKEND")
fi

if [[ -n "${VLLM_LINEAR_BACKEND:-}" ]]; then
  args+=(--linear-backend "$VLLM_LINEAR_BACKEND")
fi

if [[ -n "${VLLM_MOE_BACKEND:-}" ]]; then
  args+=(--moe-backend "$VLLM_MOE_BACKEND")
fi

if [[ -n "${VLLM_GDN_PREFILL_BACKEND:-}" ]]; then
  args+=(--gdn-prefill-backend "$VLLM_GDN_PREFILL_BACKEND")
fi

if [[ -n "${VLLM_MM_ENCODER_ATTN_BACKEND:-}" ]]; then
  args+=(--mm-encoder-attn-backend "$VLLM_MM_ENCODER_ATTN_BACKEND")
fi

if [[ -n "${VLLM_KV_CACHE_DTYPE:-}" ]]; then
  args+=(--kv-cache-dtype "$VLLM_KV_CACHE_DTYPE")
fi

if [[ -n "${VLLM_SPECULATIVE_CONFIG:-}" ]]; then
  args+=(--speculative-config "$VLLM_SPECULATIVE_CONFIG")
fi

if [[ -n "${VLLM_TOKENIZER:-}" ]]; then
  args+=(--tokenizer "$VLLM_TOKENIZER")
fi

if [[ "${VLLM_TRUST_REMOTE_CODE:-0}" == "1" ]]; then
  args+=(--trust-remote-code)
fi

if [[ "${VLLM_ENABLE_PREFIX_CACHING:-0}" == "1" ]]; then
  args+=(--enable-prefix-caching)
fi

if [[ "${VLLM_LANGUAGE_MODEL_ONLY:-0}" == "1" ]]; then
  args+=(--language-model-only)
fi

if [[ "${VLLM_ASYNC_SCHEDULING:-0}" == "1" ]]; then
  args+=(--async-scheduling)
fi

if [[ -n "${VLLM_DEFAULT_CHAT_TEMPLATE_KWARGS:-}" ]]; then
  args+=(--default-chat-template-kwargs "$VLLM_DEFAULT_CHAT_TEMPLATE_KWARGS")
fi

if [[ "${VLLM_ENABLE_CHUNKED_PREFILL:-0}" == "1" ]]; then
  args+=(--enable-chunked-prefill)
fi

if [[ -n "${VLLM_TOOL_CALL_PARSER:-}" ]]; then
  args+=(--tool-call-parser "$VLLM_TOOL_CALL_PARSER")
fi

if [[ "${VLLM_ENABLE_AUTO_TOOL_CHOICE:-0}" == "1" ]]; then
  args+=(--enable-auto-tool-choice)
fi

if [[ -n "${VLLM_REASONING_PARSER:-}" ]]; then
  args+=(--reasoning-parser "$VLLM_REASONING_PARSER")
fi

if [[ -n "${VLLM_MM_ENCODER_TP_MODE:-}" ]]; then
  args+=(--mm-encoder-tp-mode "$VLLM_MM_ENCODER_TP_MODE")
fi

if [[ -n "${VLLM_MM_PROCESSOR_CACHE_TYPE:-}" ]]; then
  args+=(--mm-processor-cache-type "$VLLM_MM_PROCESSOR_CACHE_TYPE")
fi

printf 'Launching: vllm' >&2
printf ' %q' "${args[@]}" >&2
printf '\n' >&2

if [[ "${VLLM_DRY_RUN:-0}" == "1" ]]; then
  exit 0
fi

exec vllm "${args[@]}"
