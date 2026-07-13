<#!
.SYNOPSIS
Runs one bounded native Codex Worker with the already-installed local Ollama
provider configuration.

.DESCRIPTION
This is invoked by a native Ollama Supervisor through its shell tool. It never
reads the provider-header file and does not receive provider credential
environment variables. The Codex client reads its provider configuration from
the protected user-level config written by `invoke_codex_ollama.ps1`.
#>
[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Mandatory = $true)]
    [string]$Ticket,

    [Parameter(Mandatory = $true)]
    [string]$Output,

    [switch]$Background
)

$ErrorActionPreference = 'Stop'

if ($Background) {
    # A native model shell call has a short command timeout. Start the actual
    # Worker in a separate process so the Supervisor can poll its one output
    # file with short shell calls instead of timing out the model invocation.
    $arguments = @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $PSCommandPath,
        '-Ticket', $Ticket, '-Output', $Output
    )
    $outputDirectory = Split-Path -Parent $Output
    New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
    $stdoutPath = Join-Path $outputDirectory 'worker_process.stdout.log'
    $stderrPath = Join-Path $outputDirectory 'worker_process.stderr.log'
    Remove-Item -LiteralPath $stdoutPath, $stderrPath -Force -ErrorAction SilentlyContinue
    $process = Start-Process -FilePath 'powershell.exe' -ArgumentList $arguments -WorkingDirectory (Resolve-Path (Join-Path $PSScriptRoot '..')).Path -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru
    Write-Output "Worker started with PID $($process.Id)."
    exit 0
}

function Resolve-WorkerRuntimePath {
    param([string]$Candidate, [string]$Kind)

    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    $runtimeRoot = (Resolve-Path (Join-Path $repoRoot 'runtime\agent_jobs')).Path
    $full = [IO.Path]::GetFullPath((Join-Path $repoRoot $Candidate))
    if (-not $full.StartsWith($runtimeRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "$Kind must be below runtime/agent_jobs"
    }
    return $full
}

$ticketPath = Resolve-WorkerRuntimePath -Candidate $Ticket -Kind 'Ticket'
$outputPath = Resolve-WorkerRuntimePath -Candidate $Output -Kind 'Output'
if (-not (Test-Path -LiteralPath $ticketPath)) {
    throw "Worker ticket does not exist: $Ticket"
}

$prompt = Get-Content -LiteralPath $ticketPath -Raw
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
# The Supervisor's command sandbox cannot write to the operator-wide Codex
# state directory. The hierarchy launcher pre-materializes a run-local home
# beside the ticket, keeping SQLite state in the writable runtime boundary.
$env:CODEX_HOME = Join-Path (Split-Path -Parent $ticketPath) 'codex_home'
if (-not (Test-Path -LiteralPath (Join-Path $env:CODEX_HOME 'config.toml'))) {
    throw "Worker Codex home is missing its prepared config: $env:CODEX_HOME"
}
& codex exec -C $repoRoot -s read-only --add-dir $env:CODEX_HOME --add-dir (Split-Path -Parent $outputPath) `
    -c 'approval_policy="never"' `
    -c 'model_provider=agent_workbench_ollama' `
    -m 'qwen3-coder:latest' `
    -o $outputPath $prompt
exit $LASTEXITCODE
