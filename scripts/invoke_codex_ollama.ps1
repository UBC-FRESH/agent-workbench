<#!
.SYNOPSIS
Starts Codex with the local Agent Workbench Ollama provider configuration.

.DESCRIPTION
Reads the ignored operator environment file and provider-header JSON named by
it. The endpoint and header values are placed only in this PowerShell process.
The script then invokes the installed Codex CLI, whose project-local role files
may reference the generic `agent_workbench_ollama` provider identifier.

No endpoint, header value, or generated provider configuration is written to
the repository. The root Codex session continues to use the caller's normal
Codex account/configuration, so a paid Coordinator can spawn the configured
Ollama Supervisor and Worker profiles.
#>
[CmdletBinding(PositionalBinding = $false)]
param(
    # Base64-encoded JSON array avoids PowerShell interpreting Codex flags such
    # as -o as its own common parameters. The decoded value is like
    # ["exec","--version"].
    [Parameter(Mandatory = $true)]
    [string]$CodexArgsBase64,

    [string]$ProfileName = 'agent-workbench-ollama'
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
    Set-Item -Path "env:$($headerMap[$headerName])" -Value $value
}

$escapedBaseUrl = $baseUrl.Replace('\', '\\').Replace('"', '\"')
$codexHome = Join-Path $HOME '.codex'
New-Item -ItemType Directory -Force -Path $codexHome | Out-Null
$profilePath = Join-Path $codexHome "$ProfileName.config.toml"
@"
# Generated locally by Agent Workbench. Do not commit this file.
[model_providers.agent_workbench_ollama]
name = "Agent Workbench Ollama"
base_url = "$escapedBaseUrl"
wire_api = "responses"
env_http_headers = {
  "CF-Access-Client-Id" = "AW_CF_CLIENT_ID",
  "CF-Access-Client-Secret" = "AW_CF_CLIENT_SECRET",
  "User-Agent" = "AW_PROVIDER_USER_AGENT"
}
"@ | Set-Content -LiteralPath $profilePath -Encoding utf8

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

$arguments = @('-p', $ProfileName)
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
