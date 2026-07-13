<#!
.SYNOPSIS
Starts Codex with the local Agent Workbench Ollama provider configuration.

.DESCRIPTION
Reads the ignored operator environment file and provider-header JSON named by
it. The endpoint and header values are written only to the protected user-level
Codex configuration block; model-launched shell processes do not inherit them.
The script then invokes the installed Codex CLI, whose role files may reference
the generic `agent_workbench_ollama` provider identifier.

No endpoint, header value, or generated provider configuration is written to
the repository. The root Codex session continues to use the caller's normal
Codex account/configuration, so a paid Coordinator can invoke configured
Ollama Supervisor and Worker processes.
#>
[CmdletBinding(PositionalBinding = $false)]
param(
    # Base64-encoded JSON array avoids PowerShell interpreting Codex flags such
    # as -o as its own common parameters. The decoded value is like
    # ["exec","--version"].
    [Parameter(Mandatory = $true)]
    [string]$CodexArgsBase64
)

$ErrorActionPreference = 'Stop'

function Read-AgentWorkbenchEnvironment {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Agent Workbench environment file is missing: $Path"
    }
    $values = @{}
    foreach ($line in Get-Content -LiteralPath $Path) {
        if ($line -match '^(\w+)=(.+)$') {
            $values[$matches[1]] = $matches[2]
        }
    }
    return $values
}

$environmentFile = Join-Path $HOME '.agent-workbench-env.txt'
$values = Read-AgentWorkbenchEnvironment -Path $environmentFile
$baseUrl = $values['AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL']
$headersPath = $values['AGENT_WORKBENCH_PROVIDER_HEADERS_FILE']
if ([string]::IsNullOrWhiteSpace($baseUrl) -or [string]::IsNullOrWhiteSpace($headersPath)) {
    throw 'Agent Workbench environment file must define the Ollama base URL and provider headers path.'
}
if (-not (Test-Path -LiteralPath $headersPath)) {
    throw "Provider headers file is missing: $headersPath"
}

$headers = Get-Content -LiteralPath $headersPath -Raw | ConvertFrom-Json
$headerMap = @{
    'CF-Access-Client-Id' = 'AW_CF_CLIENT_ID'
    'CF-Access-Client-Secret' = 'AW_CF_CLIENT_SECRET'
    'User-Agent' = 'AW_PROVIDER_USER_AGENT'
}
foreach ($headerName in $headerMap.Keys) {
    $value = $headers.$headerName
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Provider headers file does not contain required header: $headerName"
    }
}

function ConvertTo-TomlString {
    param([string]$Value)
    return $Value.Replace('\', '\\').Replace('"', '\"')
}

$escapedBaseUrl = ConvertTo-TomlString -Value $baseUrl
$escapedClientId = ConvertTo-TomlString -Value $headers.'CF-Access-Client-Id'
$escapedClientSecret = ConvertTo-TomlString -Value $headers.'CF-Access-Client-Secret'
$escapedUserAgent = ConvertTo-TomlString -Value $headers.'User-Agent'
$codexHome = Join-Path $HOME '.codex'
New-Item -ItemType Directory -Force -Path $codexHome | Out-Null
$configPath = Join-Path $codexHome 'config.toml'
$managedStart = '# BEGIN AGENT WORKBENCH OLLAMA'
$managedEnd = '# END AGENT WORKBENCH OLLAMA'
$managedBlock = @"
$managedStart
# Generated locally by Agent Workbench. Do not commit this block.
[model_providers.agent_workbench_ollama]
name = "Agent Workbench Ollama"
base_url = "$escapedBaseUrl"
wire_api = "responses"

[model_providers.agent_workbench_ollama.http_headers]
"CF-Access-Client-Id" = "$escapedClientId"
"CF-Access-Client-Secret" = "$escapedClientSecret"
"User-Agent" = "$escapedUserAgent"

[agents.agent_workbench_ollama_supervisor]
description = "Bounded local Ollama Supervisor for Agent Workbench delegation."
config_file = "agents/agent_workbench_ollama_supervisor.toml"

[agents.agent_workbench_ollama_worker]
description = "Bounded local Ollama Worker for Agent Workbench delegation."
config_file = "agents/agent_workbench_ollama_worker.toml"

# Keep provider credentials available to Codex itself but out of model-launched
# shell processes. The header file is likewise not readable by those processes.
[shell_environment_policy]
exclude = ["AW_CF_CLIENT_ID", "AW_CF_CLIENT_SECRET", "AW_PROVIDER_USER_AGENT", "AGENT_WORKBENCH_*"]

[permissions.agent_workbench_ollama_readonly]
extends = ":workspace"

[permissions.agent_workbench_ollama_readonly.filesystem.":workspace_roots"]
"runtime/local_provider_headers.json" = "deny"
$managedEnd
"@
if (Test-Path -LiteralPath $configPath) {
    $baseConfig = Get-Content -LiteralPath $configPath -Raw
} else {
    $baseConfig = ''
}
$pattern = '(?s)' + [regex]::Escape($managedStart) + '.*?' + [regex]::Escape($managedEnd)
if ($baseConfig -match $pattern) {
    $updatedConfig = [regex]::Replace($baseConfig, $pattern, $managedBlock)
} else {
    $updatedConfig = $baseConfig.TrimEnd() + "`r`n`r`n" + $managedBlock + "`r`n"
}
Set-Content -LiteralPath $configPath -Value $updatedConfig -Encoding utf8

# Project-scoped config cannot own a provider definition. Materialize the
# generic role files into the operator's Codex home so their model-provider
# overrides are loaded as user-level agent configuration. The source profiles
# contain no endpoint or credential values.
$repoRoot = Split-Path -Parent $PSScriptRoot
$projectAgents = Join-Path $repoRoot '.codex\agents'
$localAgents = Join-Path $codexHome 'agents'
New-Item -ItemType Directory -Force -Path $localAgents | Out-Null
foreach ($agentFile in @('ollama_supervisor.toml', 'ollama_worker.toml')) {
    $source = Join-Path $projectAgents $agentFile
    if (-not (Test-Path -LiteralPath $source)) {
        throw "Project agent profile is missing: $source"
    }
    $role = if ($agentFile -eq 'ollama_supervisor.toml') { 'supervisor' } else { 'worker' }
    $localName = "agent_workbench_ollama_$role"
    $content = Get-Content -LiteralPath $source -Raw
    $content = $content.Replace("name = `"ollama_$role`"", "name = `"$localName`"")
    if ($role -eq 'supervisor') {
        $content = $content.Replace('`ollama_worker`', '`agent_workbench_ollama_worker`')
    }
    Set-Content -LiteralPath (Join-Path $localAgents "$localName.toml") -Value $content -Encoding utf8
}

$arguments = @()
try {
    $json = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($CodexArgsBase64))
    $codexArgs = ConvertFrom-Json -InputObject $json
} catch {
    throw 'CodexArgsBase64 must decode to a JSON array of Codex command arguments.'
}
$nonStringArgs = @($codexArgs | Where-Object { $_ -isnot [string] })
if ($codexArgs.Count -eq 0 -or $nonStringArgs.Count -gt 0) {
    throw 'CodexArgsBase64 must contain at least one string argument.'
}
$arguments += $codexArgs

& codex @arguments
exit $LASTEXITCODE
