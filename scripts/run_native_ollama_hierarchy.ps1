<#!
.SYNOPSIS
Runs one bounded native Ollama Supervisor -> Worker process proof.

.DESCRIPTION
The caller is the paid Coordinator. This script materializes an ignored worker
ticket, starts the Ollama Supervisor through `invoke_codex_ollama.ps1`, and
requires that Supervisor to start the Worker through
`run_native_ollama_worker.ps1`. It does not read or print credentials.
#>
[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Mandatory = $true)]
    [string]$RunId,

    [string]$WorkerMarker = 'P102_PROCESS_WORKER_MARKER',

    [string]$SupervisorMarker = 'P102_PROCESS_SUPERVISOR_VERIFIED'
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$runDir = Join-Path $repoRoot (Join-Path 'runtime\agent_jobs' $RunId)
New-Item -ItemType Directory -Force -Path $runDir | Out-Null

$ticketPath = Join-Path $runDir 'worker_ticket.md'
$workerOutput = Join-Path $runDir 'worker_final.txt'
$supervisorOutput = Join-Path $runDir 'supervisor_final.txt'
@"
# Native Ollama Worker Ticket

Run id: `$RunId`

Return exactly this marker and do not call tools:

`$WorkerMarker`
"@ | Set-Content -LiteralPath $ticketPath -Encoding utf8

$relativeTicket = [IO.Path]::GetRelativePath($repoRoot, $ticketPath).Replace('\', '/')
$relativeWorkerOutput = [IO.Path]::GetRelativePath($repoRoot, $workerOutput).Replace('\', '/')
$relativeSupervisorOutput = [IO.Path]::GetRelativePath($repoRoot, $supervisorOutput).Replace('\', '/')
$prompt = @"
You are the native Ollama Supervisor for one bounded proof. Run exactly this
PowerShell command once, without changing its arguments:

powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/run_native_ollama_worker.ps1 -Ticket $relativeTicket -Output $relativeWorkerOutput

Then read $relativeWorkerOutput. If and only if its content is exactly
`$WorkerMarker`, return exactly `$SupervisorMarker`. Do not read credentials or
provider configuration, edit files other than the Worker output created by the
command, invoke Git/GitHub, start extra agents, or retry.
"@

$codexArgs = @(
    'exec', '-C', $repoRoot, '-s', 'read-only',
    '-c', 'model_provider=agent_workbench_ollama',
    '-m', 'qwen3-coder:latest', '--json', '-o', $relativeSupervisorOutput,
    $prompt
)
$json = ConvertTo-Json -InputObject $codexArgs -Compress
$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($json))
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'invoke_codex_ollama.ps1') -CodexArgsBase64 $encoded
exit $LASTEXITCODE
