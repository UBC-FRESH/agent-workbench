<#!
.SYNOPSIS
Runs a bounded native Codex P106 Coordinator through the operator bootstrap.

.DESCRIPTION
This launcher is deliberately the only P106 native launch surface. It routes
through invoke_codex_ollama.ps1 so provider configuration and renamed
user-level role registrations are materialized before Codex starts.
#>
[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Mandatory = $true)] [string]$RunId,
    [Parameter(Mandatory = $true)] [string]$PromptFile,
    [Parameter(Mandatory = $true)] [string]$OutputDir,
    [string]$Model = 'gpt-5.6-luna'
)

$ErrorActionPreference = 'Stop'
if ($RunId -notmatch '^[A-Za-z0-9_-]+$') { throw 'RunId contains invalid characters.' }
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$promptPath = Resolve-Path (Join-Path $repoRoot $PromptFile)
$outPath = Join-Path $repoRoot $OutputDir
New-Item -ItemType Directory -Force -Path $outPath | Out-Null

$prompt = Get-Content -LiteralPath $promptPath -Raw
# The bootstrap renames tracked role profiles at user level.
$prompt = $prompt.Replace('agent_type="ollama_supervisor"', 'agent_type="agent_workbench_ollama_supervisor"')
$prompt = $prompt.Replace('agent_type="ollama_worker"', 'agent_type="agent_workbench_ollama_worker"')
$prompt = $prompt.Replace('`ollama_supervisor`', '`agent_workbench_ollama_supervisor`')
$prompt = $prompt.Replace('`ollama_worker`', '`agent_workbench_ollama_worker`')

$args = @(
    'exec', '-m', $Model, '-C', $repoRoot, '-s', 'workspace-write',
    '-c', 'approval_policy="never"', '--json', '-o',
    (Join-Path $OutputDir 'coordinator_last_message.txt'), $prompt
)
$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes((ConvertTo-Json $args -Compress)))
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'invoke_codex_ollama.ps1') -CodexArgsBase64 $encoded |
    Tee-Object -LiteralPath (Join-Path $outPath 'codex_events.jsonl')
exit $LASTEXITCODE
