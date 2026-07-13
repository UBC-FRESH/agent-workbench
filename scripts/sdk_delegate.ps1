# sdk_delegate.ps1 — Coordinator-safe wrapper for agent-workbench copilot-sdk start
#
# Usage (from repo root):
#   .\scripts\sdk_delegate.ps1 --manifest runtime/agent_jobs/<name>_manifest.json
#   .\scripts\sdk_delegate.ps1 monitor --manifest runtime/agent_jobs/<name>_manifest.json
#
# This script is the ONLY command the Coordinator needs to invoke for supervisor
# delegation. It:
#   1. Loads Ollama endpoint env vars from ~/.agent-workbench-env.txt
#   2. Uses the project .venv Python (not a system Python)
#   3. Passes all arguments through to agent-workbench copilot-sdk
#
# The Coordinator does NOT need to activate a venv, source env files, or know
# where Python lives. Just run this script.

$REPO_ROOT = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$PYTHON = Join-Path $REPO_ROOT ".venv\Scripts\python.exe"

# Load Ollama endpoint and provider headers env vars
$envFile = "$env:USERPROFILE\.agent-workbench-env.txt"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^(\w+)=(.+)$') {
            Set-Item "env:\$($matches[1])" "$($matches[2])"
        }
    }
}

# Verify the copilot module is importable before trying the full command
$check = & $PYTHON -c "import copilot; print('ok')" 2>&1
if ($check -ne "ok") {
    Write-Error "ERROR: copilot Python module not available at $PYTHON"
    Write-Error "Run: $PYTHON -m pip install --quiet copilot-sdk  (or check your install)"
    exit 1
}

# Generate a manifest automatically for: start --ticket ... --profile ... --run-id ...
if ($args.Count -gt 0 -and $args[0] -eq "start" -and $args -contains "--ticket") {
    $manifest = & $PYTHON -m agent_workbench copilot-sdk new-manifest @($args[1..($args.Count - 1)])
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $PYTHON -m agent_workbench copilot-sdk start --manifest $manifest
    exit $LASTEXITCODE
}

# Run agent-workbench copilot-sdk with all passed arguments
& $PYTHON -m agent_workbench copilot-sdk @args
exit $LASTEXITCODE
