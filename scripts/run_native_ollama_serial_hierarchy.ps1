<#!
.SYNOPSIS
Runs a serial native Codex Coordinator -> Ollama Supervisor -> Ollama Worker proof.

.DESCRIPTION
Some OpenAI-compatible Ollama/proxy deployments do not sustain a Worker
response stream while a Supervisor response stream is paused for a tool result.
This launcher preserves the three roles while serializing their remote turns:
Supervisor dispatch acknowledgement, Worker execution, then Supervisor
verification. Raw events and the temporary Worker Codex home remain ignored.
#>
[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Mandatory = $true)]
    [string]$RunId,
    [string]$WorkerMarker = 'P102_SERIAL_WORKER_MARKER',
    [string]$SupervisorMarker = 'P102_SERIAL_SUPERVISOR_MARKER'
)

$ErrorActionPreference = 'Stop'
if ($RunId -notmatch '^[A-Za-z0-9_-]+$') { throw 'RunId may contain only letters, digits, underscores, and hyphens.' }

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$runDir = Join-Path $repoRoot (Join-Path 'runtime\agent_jobs' $RunId)
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$ticketPath = Join-Path $runDir 'worker_ticket.md'
$workerOutput = Join-Path $runDir 'worker_final.txt'
$dispatchOutput = Join-Path $runDir 'supervisor_dispatch.txt'
$verifyOutput = Join-Path $runDir 'supervisor_verify.txt'
$workerCodexHome = Join-Path $runDir 'codex_home'

function Remove-WorkerCodexHome {
    if (Test-Path -LiteralPath $workerCodexHome) {
        Remove-Item -LiteralPath $workerCodexHome -Recurse -Force
    }
}

# The run-local home contains the provider configuration only long enough for
# the Worker. Ensure a failed proof cannot leave that copied config behind.
trap {
    Remove-WorkerCodexHome
    throw $_
}

@"
# Native Ollama Worker Ticket

Return exactly this marker and do not call tools:

$WorkerMarker
"@ | Set-Content -LiteralPath $ticketPath -Encoding utf8

function Invoke-OllamaTurn {
    param([string]$Prompt, [string]$OutputPath, [switch]$AllowTools)
    $args = @('exec', '-C', $repoRoot, '-s', 'read-only', '-c', 'approval_policy="never"', '-c', 'model_provider=agent_workbench_ollama', '-m', 'qwen3-coder:latest')
    if (-not $AllowTools) { $args += @('-c', 'features.shell_tool=false') }
    $args += @('-o', $OutputPath, $Prompt)
    $json = ConvertTo-Json -InputObject $args -Compress
    $encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($json))
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'invoke_codex_ollama.ps1') -CodexArgsBase64 $encoded
    if ($LASTEXITCODE -ne 0) { throw "Ollama turn failed with exit code $LASTEXITCODE" }
}

$dispatchMarker = "$SupervisorMarker`_DISPATCHED"
Invoke-OllamaTurn -Prompt "You are the native Ollama Supervisor. The Coordinator will execute one bounded Worker ticket after this turn. Return exactly $dispatchMarker and nothing else." -OutputPath $dispatchOutput
if ((Get-Content -LiteralPath $dispatchOutput -Raw).Trim() -ne $dispatchMarker) { throw 'Supervisor dispatch acknowledgement did not match.' }

# `invoke_codex_ollama.ps1` has materialized the credential-bearing provider
# config locally. The Worker needs a writable run-local state home, which is
# removed by the coordinator after inspection.
$operatorCodexHome = Join-Path $env:USERPROFILE '.codex'
New-Item -ItemType Directory -Force -Path $workerCodexHome | Out-Null
Copy-Item -LiteralPath (Join-Path $operatorCodexHome 'config.toml') -Destination (Join-Path $workerCodexHome 'config.toml') -Force

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'run_native_ollama_worker.ps1') -Ticket "runtime/agent_jobs/$RunId/worker_ticket.md" -Output "runtime/agent_jobs/$RunId/worker_final.txt"
if ($LASTEXITCODE -ne 0) { throw "Worker exited with code $LASTEXITCODE" }
if ((Get-Content -LiteralPath $workerOutput -Raw).Trim() -ne $WorkerMarker) { throw 'Worker marker did not match.' }

Invoke-OllamaTurn -AllowTools -Prompt "You are the native Ollama Supervisor. Use the actual shell tool to read runtime/agent_jobs/$RunId/worker_final.txt. If and only if its content is exactly $WorkerMarker, return exactly $SupervisorMarker. Do not print tool-call markup as text or take any other action." -OutputPath $verifyOutput
if ((Get-Content -LiteralPath $verifyOutput -Raw).Trim() -ne $SupervisorMarker) { throw 'Supervisor verification marker did not match.' }
Remove-WorkerCodexHome
Write-Output $SupervisorMarker
