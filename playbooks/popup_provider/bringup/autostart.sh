#!/usr/bin/env bash
# popup_provider bring-up: unattended bring-up sequence for one target.
#
# Usage:
#   ./autostart.sh --target targets/sockeye.yaml --profile profiles/qwen25-coder-7b.yaml
#
# This script:
#   1. Validates inputs and runs the fit preflight
#   2. Submits the allocation (via the target's submission script)
#   3. Waits for the allocation to start
#   4. Launches vLLM inside the allocation
#   5. Starts the loopback bridge
#   6. Verifies readiness
#   7. Reports the result
#
# All output goes to runtime/popup_provider/<target-name>.log
#
# Safety: this script runs on the cluster, not locally. It must be sourced
# from within the cluster's working directory.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMEWORK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

TARGET=""
PROFILE=""
RUNTIME_DIR=""
LOG_FILE=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --profile) PROFILE="$2"; shift 2 ;;
    --runtime-dir) RUNTIME_DIR="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$TARGET" || -z "$PROFILE" ]]; then
  echo "Usage: $0 --target <target.yaml> --profile <profile.yaml> [--runtime-dir <dir>]" >&2
  exit 2
fi

# Resolve paths relative to framework dir
TARGET_PATH="$FRAMEWORK_DIR/$TARGET"
PROFILE_PATH="$FRAMEWORK_DIR/$PROFILE"

if [[ ! -f "$TARGET_PATH" ]]; then
  echo "ERROR: target descriptor not found: $TARGET_PATH" >&2
  exit 2
fi
if [[ ! -f "$PROFILE_PATH" ]]; then
  echo "ERROR: launch profile not found: $PROFILE_PATH" >&2
  exit 2
fi

# Extract target name for logging
TARGET_NAME=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$TARGET_PATH'))
    print(d.get('name', 'unknown'))
except ImportError:
    import json
    # fallback: read first line with 'name:'
    for line in open('$TARGET_PATH'):
        if line.startswith('name:'):
            print(line.split(':', 1)[1].strip())
            break
")

if [[ -z "$RUNTIME_DIR" ]]; then
  RUNTIME_DIR="$FRAMEWORK_DIR/../runtime/popup_provider"
fi
mkdir -p "$RUNTIME_DIR"
LOG_FILE="$RUNTIME_DIR/${TARGET_NAME}.log"

log() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
  echo "$msg" | tee -a "$LOG_FILE"
}

error() {
  log "ERROR: $*"
  echo "$*" >&2
}

# ------------------------------------------------------------------
# Step 1: Fit preflight
# ------------------------------------------------------------------
log "=== Step 1: Fit preflight ==="
if ! python3 "$FRAMEWORK_DIR/playbooks/popup_provider/preflight/check.py" \
     --target "$TARGET_PATH" --profile "$PROFILE_PATH"; then
  error "Fit preflight failed. Model does not fit this target."
  exit 1
fi

# ------------------------------------------------------------------
# Step 2: Submit allocation
# ------------------------------------------------------------------
log "=== Step 2: Submit allocation ==="

# Read submission script path from target descriptor
SUBMISSION_SCRIPT=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$TARGET_PATH'))
    print(d.get('submission_script', ''))
except ImportError:
    for line in open('$TARGET_PATH'):
        if line.startswith('submission_script:'):
            print(line.split(':', 1)[1].strip())
            break
")

if [[ -z "$SUBMISSION_SCRIPT" ]]; then
  error "Target descriptor has no submission_script"
  exit 1
fi

if [[ "$DRY_RUN" == "true" ]]; then
  log "DRY RUN: would submit $SUBMISSION_SCRIPT"
else
  if [[ ! -f "$SUBMISSION_SCRIPT" ]]; then
    error "Submission script not found on cluster: $SUBMISSION_SCRIPT"
    exit 1
  fi
  log "Submitting allocation: $SUBMISSION_SCRIPT"
  SBATCH_OUTPUT=$(sbatch "$SUBMISSION_SCRIPT" 2>&1) || {
    error "sbatch failed: $SBATCH_OUTPUT"
    exit 1
  }
  JOB_ID=$(echo "$SBATCH_OUTPUT" | grep -oP 'Submitted batch job \K\d+' || true)
  if [[ -z "$JOB_ID" ]]; then
    error "Could not extract job ID from sbatch output: $SBATCH_OUTPUT"
    exit 1
  fi
  log "Submitted job: $JOB_ID"
fi

# ------------------------------------------------------------------
# Step 3: Wait for allocation
# ------------------------------------------------------------------
log "=== Step 3: Wait for allocation ==="

if [[ "$DRY_RUN" == "true" ]]; then
  log "DRY RUN: would wait for job $JOB_ID to start"
else
  log "Waiting for job $JOB_ID to enter RUNNING state..."
  while true; do
    STATE=$(squeue -j "$JOB_ID" -h -o "%T" 2>/dev/null || echo "NOT_FOUND")
    if [[ "$STATE" == "RUNNING" ]]; then
      log "Job $JOB_ID is RUNNING"
      break
    elif [[ "$STATE" == "NOT_FOUND" || -z "$STATE" ]]; then
      # Job may have completed or been cancelled — check sacct
      FINAL_STATE=$(sacct -j "$JOB_ID" --format=State --noheader 2>/dev/null | tail -1 || echo "UNKNOWN")
      log "Job $JOB_ID state: $FINAL_STATE"
      if [[ "$FINAL_STATE" == "COMPLETED" || "$FINAL_STATE" == "TIMEOUT" ]]; then
        error "Job $JOB_ID ended before we could attach: $FINAL_STATE"
        exit 1
      fi
      error "Job $JOB_ID no longer in queue"
      exit 1
    fi
    log "Job $JOB_ID state: $STATE — waiting..."
    sleep 30
  done
fi

# ------------------------------------------------------------------
# Step 4: Launch vLLM inside the allocation
# ------------------------------------------------------------------
log "=== Step 4: Launch vLLM ==="

# Read profile values
VLLM_MODEL=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$PROFILE_PATH'))
    print(d.get('model_id', ''))
except ImportError:
    for line in open('$PROFILE_PATH'):
        if line.startswith('model_id:'):
            print(line.split(':', 1)[1].strip().strip('\"'))
            break
")

VLLM_SERVED_MODEL_NAME=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$PROFILE_PATH'))
    print(d.get('served_model_name', ''))
except ImportError:
    for line in open('$PROFILE_PATH'):
        if line.startswith('served_model_name:'):
            print(line.split(':', 1)[1].strip().strip('\"'))
            break
")

VLLM_MAX_MODEL_LEN=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$PROFILE_PATH'))
    print(d.get('max_model_len', 32768))
except ImportError:
    for line in open('$PROFILE_PATH'):
        if line.startswith('max_model_len:'):
            print(line.split(':', 1)[1].strip())
            break
")

if [[ -z "$VLLM_MODEL" ]]; then
  error "Profile has no model_id"
  exit 1
fi

log "Launching vLLM: model=$VLLM_MODEL served_name=$VLLM_SERVED_MODEL_NAME max_len=$VLLM_MAX_MODEL_LEN"

# Source the existing serve-native.sh from P119 with our profile values
# Export profile values as environment variables
export VLLM_MODEL
export VLLM_SERVED_MODEL_NAME
export VLLM_MAX_MODEL_LEN

# Use the P119 serve-native.sh pattern via srun --overlap
# The serve script sources the profile's env vars and launches vllm serve
srun --overlap --pty bash -c "
  cd '$FRAMEWORK_DIR'
  source playbooks/vllm_blackwell/scripts/load-env.sh
  # Source profile values
  export VLLM_MODEL='$VLLM_MODEL'
  export VLLM_SERVED_MODEL_NAME='$VLLM_SERVED_MODEL_NAME'
  export VLLM_MAX_MODEL_LEN='$VLLM_MAX_MODEL_LEN'
  # Launch vLLM
  source playbooks/vllm_blackwell/scripts/serve-native.sh
" > "$RUNTIME_DIR/vllm.log" 2>&1 &
VLLM_PID=$!
log "vLLM launch initiated (PID $VLLM_PID in allocation)"

# ------------------------------------------------------------------
# Step 5: Start the loopback bridge
# ------------------------------------------------------------------
log "=== Step 5: Start loopback bridge ==="

# Read bridge port from target
SERVICE_PORT=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$TARGET_PATH'))
    print(d.get('service_port', 8000))
except ImportError:
    for line in open('$TARGET_PATH'):
        if line.startswith('service_port:'):
            print(line.split(':', 1)[1].strip())
            break
")

BRIDGE_PORT=18125
log "Bridge will listen on login node port $BRIDGE_PORT -> allocation port $SERVICE_PORT"

if [[ "$DRY_RUN" == "true" ]]; then
  log "DRY RUN: would start bridge on port $BRIDGE_PORT"
else
  # Start the bridge (adapted from P124)
  python3 "$FRAMEWORK_DIR/playbooks/popup_provider/bringup/bridge.py" \
    --job-id "$JOB_ID" \
    --remote-port "$SERVICE_PORT" \
    --local-port "$BRIDGE_PORT" \
    --log "$RUNTIME_DIR/bridge.log" &
  BRIDGE_PID=$!
  log "Bridge started (PID $BRIDGE_PID)"
fi

# ------------------------------------------------------------------
# Step 6: Wait for readiness and verify
# ------------------------------------------------------------------
log "=== Step 6: Readiness check ==="

if [[ "$DRY_RUN" == "true" ]]; then
  log "DRY RUN: would wait for readiness on port $BRIDGE_PORT"
else
  # Wait for vLLM to be ready (reuse P119 wait-ready.sh logic)
  log "Waiting for vLLM readiness..."
  python3 -c "
import time
import urllib.request
import sys

port = $BRIDGE_PORT
url = f'http://127.0.0.1:{port}/v1/models'
for i in range(240):  # 20 minutes max
    try:
        resp = urllib.request.urlopen(url, timeout=5)
        if resp.status == 200:
            print(f'READY at port {port}')
            sys.exit(0)
    except Exception:
        pass
    time.sleep(5)

print(f'TIMED OUT waiting for vLLM on port {port}')
sys.exit(1)
"
  if [[ $? -ne 0 ]]; then
    error "vLLM did not become ready within 20 minutes"
    error "Check logs: $RUNTIME_DIR/vllm.log"
    exit 1
  fi
fi

# ------------------------------------------------------------------
# Done
# ------------------------------------------------------------------
log "=== Bring-up complete ==="
log "Target: $TARGET_NAME"
log "Model: $VLLM_MODEL ($VLLM_SERVED_MODEL_NAME)"
log "Bridge port: $BRIDGE_PORT"
log "vLLM log: $RUNTIME_DIR/vllm.log"
log "Bridge log: $RUNTIME_DIR/bridge.log"
log ""
log "Next step: establish client forward"
log "  ssh -O forward -L 18001:127.0.0.1:$BRIDGE_PORT $TARGET"
log ""
log "Then verify: curl http://127.0.0.1:18001/v1/models"

exit 0