<#
.SYNOPSIS
Runs the direct native Honeycomb role-provenance probe.

.DESCRIPTION
Starts a fresh Terra Coordinator through the user-local Coordinator profile and
asks it to spawn the configured named roles directly. Raw JSONL stays ignored
under runtime; inspect_native_honeycomb_proof.py produces the sanitized,
fail-closed verdict after an operator supplies provider-side corroboration.
#>
[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Mandatory = $true)] [string]$RunId,
    [Parameter(Mandatory = $true)] [string]$ProviderEvidence
)

$ErrorActionPreference = 'Stop'
if ($RunId -notmatch '^[A-Za-z0-9_-]+$') { throw 'RunId contains invalid characters.' }
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$runDir = Join-Path $repoRoot "runtime\agent_jobs\$RunId"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null

$prompt = @"
You are the configured Agent Workbench Coordinator. Use the native spawnAgent
tool to launch these direct child roles exactly once each: gpt_luna_supervisor,
gpt_sol_advisor, ollama_worker, ollama_worker. Give each a distinct no-tool
marker task and require it to return its marker. Wait for all four. Do not edit
files, invoke GitHub, change providers, or claim this proof passed. End by
returning exactly HONEYCOMB_DIRECT_FANOUT_FINISHED.
"@

$codexArgs = @(
    'exec', '--profile', 'agent-workbench-coordinator', '-C', $repoRoot,
    '-s', 'read-only', '-c', 'approval_policy="never"', '--json',
    '-o', (Join-Path $runDir 'coordinator_last_message.txt'), $prompt
)
$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes((ConvertTo-Json $codexArgs -Compress)))
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'invoke_codex_ollama.ps1') -CodexArgsBase64 $encoded |
    Tee-Object -LiteralPath (Join-Path $runDir 'native_events.jsonl')
$exitCode = $LASTEXITCODE
python (Join-Path $PSScriptRoot 'inspect_native_honeycomb_proof.py') `
    --events (Join-Path $runDir 'native_events.jsonl') `
    --provider-evidence $ProviderEvidence `
    --output (Join-Path $runDir 'sanitized_verdict.json')
exit $exitCode
