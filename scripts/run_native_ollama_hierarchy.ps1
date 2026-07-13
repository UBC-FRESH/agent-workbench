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
if ($RunId -notmatch '^[A-Za-z0-9_-]+$') {
    throw 'RunId may contain only letters, digits, underscores, and hyphens.'
}
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$runDir = Join-Path $repoRoot (Join-Path 'runtime\agent_jobs' $RunId)
New-Item -ItemType Directory -Force -Path $runDir | Out-Null

$ticketPath = Join-Path $runDir 'worker_ticket.md'
$workerOutput = Join-Path $runDir 'worker_final.txt'
$supervisorOutput = Join-Path $runDir 'supervisor_final.txt'
$supervisorEvents = Join-Path $runDir 'supervisor_events.jsonl'
$workerCodexHome = Join-Path $runDir 'codex_home'
$operatorCodexHome = Join-Path $env:USERPROFILE '.codex'

# The Worker runs inside the Supervisor's workspace sandbox. Give it a
# private, writable Codex home in this ignored run directory instead of the
# operator-wide home, whose state database cannot be written from that sandbox.
New-Item -ItemType Directory -Force -Path $workerCodexHome | Out-Null
Copy-Item -LiteralPath (Join-Path $operatorCodexHome 'config.toml') -Destination (Join-Path $workerCodexHome 'config.toml') -Force
if (Test-Path -LiteralPath (Join-Path $operatorCodexHome 'agents')) {
    Copy-Item -LiteralPath (Join-Path $operatorCodexHome 'agents') -Destination (Join-Path $workerCodexHome 'agents') -Recurse -Force
}
@"
# Native Ollama Worker Ticket

Run id: $RunId

Return exactly this marker and do not call tools:

$WorkerMarker
"@ | Set-Content -LiteralPath $ticketPath -Encoding utf8

$relativeTicket = "runtime/agent_jobs/$RunId/worker_ticket.md"
$relativeWorkerOutput = "runtime/agent_jobs/$RunId/worker_final.txt"
$relativeSupervisorOutput = "runtime/agent_jobs/$RunId/supervisor_final.txt"
$prompt = @"
You are the native Ollama Supervisor for one bounded proof. Run exactly this
PowerShell command once, without changing its arguments. Use the actual shell
tool provided by Codex with timeout_ms set to 120000; do not print a
function/tool-call markup block as text:

powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/run_native_ollama_worker.ps1 -Ticket $relativeTicket -Output $relativeWorkerOutput

Then read $relativeWorkerOutput. If and only if its content is exactly
$WorkerMarker, return exactly $SupervisorMarker. Do not read credentials or
provider configuration, edit files other than the Worker output created by the
command, invoke Git/GitHub, start extra agents, or retry the Worker.
"@

$codexArgs = @(
    'exec', '-C', $repoRoot, '-s', 'read-only', '-c', 'approval_policy="never"',
    '-c', 'model_provider=agent_workbench_ollama',
    '-m', 'qwen3-coder:latest', '--json', '-o', $relativeSupervisorOutput,
    $prompt
)
$json = ConvertTo-Json -InputObject $codexArgs -Compress
$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($json))
# Preserve the Supervisor's machine-readable event stream beside the result so
# the Coordinator can inspect the live conversation after host output has been
# truncated. The same stream continues to stdout for interactive observation.
# Do not merge stderr into the pipeline: native stderr becomes a terminating
# PowerShell error under this script's strict error policy. JSON stdout remains
# available both live and in the ignored event file.
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'invoke_codex_ollama.ps1') -CodexArgsBase64 $encoded | Tee-Object -LiteralPath $supervisorEvents
$exitCode = $LASTEXITCODE
exit $exitCode
