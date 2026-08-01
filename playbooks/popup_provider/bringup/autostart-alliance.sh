#!/usr/bin/env bash
# popup_provider bring-up: dry-run-safe planning script for Alliance clusters.
#
# Usage:
#   ./autostart-alliance.sh --target targets/nibi.yaml --profile profiles/qwen36-27b-nvfp4.yaml
#   ./autostart-alliance.sh --target targets/nibi.yaml --profile profiles/qwen36-27b-nvfp4.yaml --apply
#
# This script:
#   1. Validates inputs (target descriptor + launch profile exist)
#   2. Runs the local fit preflight (no network calls)
#   3. Renders and prints the Slurm submission plan
#   4. Optionally renders launch parameters (--apply)
#
# Safety:
#   - Default mode is DRY RUN. No scheduler commands, no SSH, no network.
#   - --apply does NOT submit. It prints a refusal because live apply requires
#     manual human action (SSH + Duo MFA) on the Alliance cluster.
#   - Nibi compute nodes have internet access; the bridge/ingress boundary
#     is a future step, not handled by this script.
#
# This script is repo-local. It does not invoke sbatch, srun, ssh, or any
# remote command. It is a planning and validation tool only.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMEWORK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

TARGET=""
PROFILE=""
APPLY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --profile) PROFILE="$2"; shift 2 ;;
    --apply) APPLY=true; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$TARGET" || -z "$PROFILE" ]]; then
  echo "Usage: $0 --target <target.yaml> --profile <profile.yaml> [--apply]" >&2
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

# Extract target name for display
TARGET_NAME=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$TARGET_PATH'))
    print(d.get('name', 'unknown'))
except ImportError:
    for line in open('$TARGET_PATH'):
        if line.startswith('name:'):
            print(line.split(':', 1)[1].strip())
            break
")

echo "=============================================="
echo " Alliance Popup Provider — Planning Mode"
echo "=============================================="
echo "Target:   $TARGET_NAME ($TARGET)"
echo "Profile:  $PROFILE"
echo "Mode:     $(if $APPLY; then echo 'APPLY (REFUSED — see below)'; else echo 'DRY RUN'; fi)"
echo "=============================================="
echo ""

# ------------------------------------------------------------------
# Step 1: Fit preflight (local, no network)
# ------------------------------------------------------------------
echo "--- Step 1: Fit preflight ---"
PREFLIGHT_EXIT=0
PREFLIGHT_OUTPUT=$(python3 "$FRAMEWORK_DIR/preflight/check.py" \
  --target "$TARGET_PATH" --profile "$PROFILE_PATH" 2>&1) || PREFLIGHT_EXIT=$?
echo "$PREFLIGHT_OUTPUT"
if [[ "$PREFLIGHT_EXIT" -ne 0 ]]; then
  echo ""
  echo "ERROR: Fit preflight failed (exit $PREFLIGHT_EXIT)." >&2
  echo "The model does not fit the target. Aborting plan." >&2
  exit "$PREFLIGHT_EXIT"
fi
echo ""

# ------------------------------------------------------------------
# Step 2: Render Slurm submission plan (dry-run)
# ------------------------------------------------------------------
echo "--- Step 2: Slurm submission plan ---"

# Read target fields
SLURM_ACCOUNT=$(python3 -c "
import sys, os
try:
    import yaml
    d = yaml.safe_load(open('$TARGET_PATH'))
    v = d.get('account', '')
    print(v if v else '')
except ImportError:
    for line in open('$TARGET_PATH'):
        if line.startswith('account:'):
            print(line.split(':', 1)[1].strip())
            break
")

SLURM_PARTITION=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$TARGET_PATH'))
    print(d.get('partition', ''))
except ImportError:
    for line in open('$TARGET_PATH'):
        if line.startswith('partition:'):
            print(line.split(':', 1)[1].strip())
            break
")

SLURM_GRES=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$TARGET_PATH'))
    v = d.get('gres', '')
    print(v if v else '')
except ImportError:
    for line in open('$TARGET_PATH'):
        if line.startswith('gres:'):
            print(line.split(':', 1)[1].strip())
            break
")

SLURM_NODES=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$TARGET_PATH'))
    print(d.get('nodes', 1))
except ImportError:
    print(1)
")

SLURM_NTASKS=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$TARGET_PATH'))
    print(d.get('ntasks', 1))
except ImportError:
    print(1)
")

SLURM_CPUS=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$TARGET_PATH'))
    print(d.get('cpus_per_task', 4))
except ImportError:
    print(4)
")

SLURM_MEM=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$TARGET_PATH'))
    print(d.get('mem', '8G'))
except ImportError:
    print('8G')
")

SLURM_TIME=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$TARGET_PATH'))
    print(d.get('time_limit', '02:00:00'))
except ImportError:
    print('02:00:00')
")

SLURM_CONSTRAINT=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$TARGET_PATH'))
    v = d.get('constraint', '')
    print(v if v else '')
except ImportError:
    print('')
")

# Read profile fields
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

VLLM_SERVED=$(python3 -c "
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

VLLM_MAX_LEN=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$PROFILE_PATH'))
    print(d.get('max_model_len', 32768))
except ImportError:
    print(32768)
")

VLLM_GPU_UTIL=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$PROFILE_PATH'))
    print(d.get('gpu_memory_utilization', 0.88))
except ImportError:
    print(0.88)
")

VLLM_PORT=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$TARGET_PATH'))
    print(d.get('service_port', 18000))
except ImportError:
    print(18000)
")

VLLM_HOST=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$TARGET_PATH'))
    print(d.get('bind_host', '127.0.0.1'))
except ImportError:
    print('127.0.0.1')
")

# Render the submission script template.
# The planner prints literal 'sbatch' / 'srun' directives as TEXT OUTPUT only.
# These are shown to the user so they can copy-paste; the script never
# executes them. No scheduler commands are invoked here.

echo "#!/bin/bash"
echo "sbatch --account=${SLURM_ACCOUNT}"
echo "sbatch --partition=${SLURM_PARTITION}"
echo "sbatch --nodes=${SLURM_NODES}"
echo "sbatch --ntasks=${SLURM_NTASKS}"
echo "sbatch --cpus-per-task=${SLURM_CPUS}"
echo "sbatch --mem=${SLURM_MEM}"
echo "sbatch --time=${SLURM_TIME}"

if [[ -n "$SLURM_GRES" ]]; then
  echo "sbatch --gres=gpu:${SLURM_GRES}"
fi

if [[ -n "$SLURM_CONSTRAINT" ]]; then
  echo "sbatch --constraint=${SLURM_CONSTRAINT}"
fi

echo ""
echo "--- Step 3: vLLM launch parameters (rendered) ---"
echo ""
echo "vllm serve ${VLLM_MODEL} \\"
echo "  --served-model-name ${VLLM_SERVED} \\"
echo "  --host ${VLLM_HOST} \\"
echo "  --port ${VLLM_PORT} \\"
echo "  --max-model-len ${VLLM_MAX_LEN} \\"
echo "  --gpu-memory-utilization ${VLLM_GPU_UTIL}"
echo ""

# ------------------------------------------------------------------
# Step 4: Access/ingress note (Alliance-specific)
# ------------------------------------------------------------------
echo "--- Step 4: Access boundary ---"
echo ""
echo "Nibi compute nodes have INTERNET ACCESS. No proxy or firewall"
echo "permission is required for outbound traffic."
echo ""
echo "The vLLM server binds to loopback (${VLLM_HOST}:${VLLM_PORT})."
echo "External access requires a SEPARATE ingress mechanism:"
echo "  - Cloudflare Tunnel (existing 'nginx' tunnel, do NOT create new)"
echo "  - SSH port forward (manual, requires Duo MFA)"
echo "  - Other established ingress (operator decision)"
echo ""
echo "This script does NOT handle ingress setup. That is a manual step."
echo ""

# ------------------------------------------------------------------
# Step 5: Apply gate (refusal)
# ------------------------------------------------------------------
if $APPLY; then
  echo "=============================================="
  echo " APPLY MODE — REFUSED"
  echo "=============================================="
  echo ""
  echo "Live scheduler submission is intentionally GATED."
  echo ""
  echo "Reasons:"
  echo "  1. Alliance access requires interactive SSH + Duo MFA"
  echo "     (first login needs human approval on iPhone)."
  echo "  2. This script runs repo-local; it has no remote shell."
  echo "  3. Submitting a Slurm allocation without human oversight"
  echo "     risks wasting shared HPC resources."
  echo ""
  echo "To apply manually:"
  echo "  1. SSH to nibi.alliancecan.ca with Duo MFA"
echo "  2. Copy the rendered allocation script above"
echo "  3. Submit the allocation script to the scheduler"
echo "  4. Attach vLLM inside the allocation"
  echo "  5. Set up ingress (tunnel/SSH-forward) separately"
  echo ""
  echo "This script will NOT execute sbatch, srun, ssh, or any"
  echo "remote command. It is a planning and validation tool only."
  echo "=============================================="
fi

echo ""
echo "--- Done ---"
echo "Plan rendered. Review and apply manually if satisfied."