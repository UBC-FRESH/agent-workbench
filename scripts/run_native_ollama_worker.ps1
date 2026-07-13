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
    [string]$Output
)

$ErrorActionPreference = 'Stop'

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
& codex exec -C $repoRoot -s read-only `
    -c 'model_provider=agent_workbench_ollama' `
    -m 'qwen3-coder:latest' `
    -o $outputPath $prompt
exit $LASTEXITCODE
