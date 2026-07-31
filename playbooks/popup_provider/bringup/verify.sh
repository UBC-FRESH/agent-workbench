#!/usr/bin/env bash
# Popup provider verification: bounded client request + readiness record.
#
# Usage:
#   ./verify.sh --port 18125 --model qwen2.5-coder-7b-instruct
#
# Runs a minimal /v1/models check and a single chat completion request.
# Records the result as a JSON evidence file.

set -euo pipefail

PORT="${1:-18125}"
MODEL="${2:-qwen2.5-coder-7b-instruct}"
EVIDENCE_DIR="${3:-../runtime/popup_provider}"

mkdir -p "$EVIDENCE_DIR"
EVIDENCE_FILE="$EVIDENCE_DIR/verify-$(date +%Y%m%d-%H%M%S).json"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

# Step 1: /v1/models
log "Checking /v1/models on port $PORT..."
MODELS_RESP=$(curl -sf "http://127.0.0.1:$PORT/v1/models" 2>&1) || {
  echo "{\"status\":\"fail\",\"step\":\"models\",\"error\":\"curl failed\"}" > "$EVIDENCE_FILE"
  log "FAIL: /v1/models returned non-200"
  exit 1
}
MODELS_OK=true

# Step 2: /v1/chat/completions (bounded: 1 prompt token, 5 max tokens)
log "Sending bounded chat completion request..."
CHAT_RESP=$(curl -sf -X POST "http://127.0.0.1:$PORT/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$MODEL\",
    \"messages\": [{\"role\": \"user\", \"content\": \"hi\"}],
    \"max_tokens\": 5
  }" 2>&1) || {
  CHAT_OK=false
  CHAT_ERROR="$CHAT_RESP"
} || CHAT_OK=false

if [[ "${CHAT_OK:-true}" == "true" ]]; then
  # Extract usage if present
  USAGE=$(echo "$CHAT_RESP" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    u = d.get('usage', {})
    print(json.dumps({'prompt_tokens': u.get('prompt_tokens'), 'completion_tokens': u.get('completion_tokens')}))
except Exception:
    print('{}')
" 2>/dev/null || echo "{}")
else
  USAGE="{}"
fi

# Write evidence
python3 -c "
import json, sys
evidence = {
    'status': 'pass' if ('$MODELS_OK' == 'true' and '${CHAT_OK:-true}' == 'true') else 'fail',
    'step': 'complete',
    'port': $PORT,
    'model': '$MODEL',
    'models_ok': $MODELS_OK,
    'chat_ok': ${CHAT_OK:-true},
    'usage': json.loads('$USAGE'),
    'timestamp': '$(date -u +"%Y-%m-%dT%H:%M:%SZ")'
}
print(json.dumps(evidence, indent=2))
" > "$EVIDENCE_FILE"

log "Evidence written to $EVIDENCE_FILE"
cat "$EVIDENCE_FILE"

if [[ "${CHAT_OK:-true}" != "true" ]]; then
  exit 1
fi

exit 0