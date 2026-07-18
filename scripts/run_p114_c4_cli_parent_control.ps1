<# Run one P114.3 CLI-parent control through native multi_agent_v1. #>
[CmdletBinding()]
param(
    [string]$RunId = 'p114_c4_cli_parent_r10',
    [int]$AdapterPort = 18999,
    [switch]$Battery,
    [switch]$PackageMcpBattery,
    [switch]$PackageMcpQualification,
    [string]$QualificationWorktree
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$runDir = Join-Path $repoRoot "runtime\agent_jobs\$RunId"
$bridge = Join-Path $repoRoot 'scripts\enable_p114_c4_role_bridge.ps1'
$environmentFile = Join-Path $HOME '.agent-workbench-env.txt'
$settings = @{}
Get-Content -LiteralPath $environmentFile | ForEach-Object {
    if ($_ -match '^([^=]+)=(.+)$') { $settings[$matches[1]] = $matches[2] }
}
$headerFile = $settings['AGENT_WORKBENCH_PROVIDER_HEADERS_FILE']
if (-not $headerFile -or -not (Test-Path -LiteralPath $headerFile)) { throw 'Configured Cloudflare provider header file is missing.' }
$headers = Get-Content -LiteralPath $headerFile -Raw | ConvertFrom-Json
$providerEnvironment = @{
    'AW_CF_CLIENT_ID' = $headers.'CF-Access-Client-Id'
    'AW_CF_CLIENT_SECRET' = $headers.'CF-Access-Client-Secret'
    'AW_PROVIDER_USER_AGENT' = $headers.'User-Agent'
}
$previousProviderEnvironment = @{}
foreach ($name in $providerEnvironment.Keys) {
    $value = $providerEnvironment[$name]
    if (-not ($value -is [string]) -or -not $value) { throw "Configured provider header value is missing for $name." }
    $previousProviderEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
    [Environment]::SetEnvironmentVariable($name, $value, 'Process')
}

$bridgeEnabled = $false
try {
    if (($Battery -and $PackageMcpBattery) -or ($PackageMcpQualification -and ($Battery -or $PackageMcpBattery))) { throw 'Only one P114 battery or qualification mode may be enabled.' }
    if ($PackageMcpQualification) {
        & $bridge -Mode Enable -RunId $RunId -AdapterPort $AdapterPort -PackageMcpQualification -QualificationWorktree $QualificationWorktree
    } elseif ($PackageMcpBattery) {
        & $bridge -Mode Enable -RunId $RunId -AdapterPort $AdapterPort -PackageMcpBattery
    } elseif ($Battery) {
        & $bridge -Mode Enable -RunId $RunId -AdapterPort $AdapterPort -StripInclude -Battery
    } else {
        & $bridge -Mode Enable -RunId $RunId -AdapterPort $AdapterPort -StripInclude
    }
    $bridgeEnabled = $true
    $childTicket = Get-Content -LiteralPath (Join-Path $runDir 'ticket.md') -Raw
    $parentTicket = @"
You are the P114.3 CLI-parent control. Do not inspect files, alter configuration,
enable or disable a bridge, send follow-up input, or launch duplicate children.

Use the native multi_agent_v1 spawn tool exactly once with:
- agent_type: ollama_qwen_coder_worker
- fork_context: false
- no model, reasoning, or service-tier override
- message: the child ticket below, verbatim

Wait for that child exactly once. Return only its agent ID and terminal status.

CHILD TICKET START
$childTicket
CHILD TICKET END
"@
    [IO.File]::WriteAllText((Join-Path $runDir 'cli_parent_ticket.md'), $parentTicket, [Text.UTF8Encoding]::new($false))
    $events = Join-Path $runDir 'cli_parent_events.jsonl'
    $final = Join-Path $runDir 'cli_parent_final.txt'
    $controllerRoot = if ($PackageMcpQualification) { $QualificationWorktree } else { $repoRoot }
    $codexArgs = @('exec', '-C', $controllerRoot, '-c', 'approval_policy="never"', '--dangerously-bypass-approvals-and-sandbox', '--json', '-o', $final, '-')
    $parentTicket | & codex @codexArgs | Tee-Object -LiteralPath $events
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) { throw "CLI-parent control failed with exit code $exitCode" }
} finally {
    if ($bridgeEnabled) { & $bridge -Mode Disable -RunId $RunId -AdapterPort $AdapterPort }
    foreach ($name in $previousProviderEnvironment.Keys) {
        [Environment]::SetEnvironmentVariable($name, $previousProviderEnvironment[$name], 'Process')
    }
}

Write-Output "P114 CLI-parent control complete: $runDir"
