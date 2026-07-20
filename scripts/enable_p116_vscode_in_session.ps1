<# Install or remove the inert P116 tools for fresh native Codex VS Code sessions. #>
[CmdletBinding()]
param(
    [ValidateSet('Enable', 'Disable')][string]$Mode = 'Enable',
    [string]$InstallId = 'p116_vscode_in_session',
    [string]$CodexHome = (Join-Path $env:USERPROFILE '.codex')
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$stateDir = Join-Path $repoRoot "runtime\agent_jobs\$InstallId"
$configPath = Join-Path $CodexHome 'config.toml'
$hooksPath = Join-Path $CodexHome 'hooks.json'
$configBackup = Join-Path $stateDir 'config.before.toml'
$hooksBackup = Join-Path $stateDir 'hooks.before.json'
$journal = Join-Path $stateDir 'transaction.json'
$lock = Join-Path $stateDir 'transaction.lock'
$python = Join-Path $repoRoot '.venv\Scripts\python.exe'
$server = Join-Path $repoRoot 'scripts\p116_in_session_mcp_server.py'
$capture = Join-Path $repoRoot 'scripts\p116_capture_hook.py'
$serverName = 'p116_in_session_supervision'

function ConvertTo-Hashtable([object]$Value) {
    if ($null -eq $Value) { return $null }
    if ($Value -is [System.Management.Automation.PSCustomObject]) {
        $result = [ordered]@{}
        foreach ($property in $Value.PSObject.Properties) {
            $result[$property.Name] = ConvertTo-Hashtable $property.Value
        }
        return $result
    }
    if ($Value -is [System.Collections.IEnumerable] -and -not ($Value -is [string])) {
        return @($Value | ForEach-Object { ConvertTo-Hashtable $_ })
    }
    return $Value
}

if ($Mode -eq 'Disable') {
    if (-not (Test-Path -LiteralPath $configBackup) -or -not (Test-Path -LiteralPath $hooksBackup)) { throw 'P116 VS Code installation backup is missing.' }
    & $python -m agent_workbench.agent_bridge.transaction_cli restore --run-id $InstallId --journal $journal --lock $lock --target "config|$configPath|$configBackup" --target "hooks|$hooksPath|$hooksBackup"
    if ($LASTEXITCODE -ne 0) { throw 'P116 VS Code installation restore failed.' }
    Write-Output 'P116 in-session supervision removed. Restart VS Code to refresh its tool inventory.'
    exit 0
}

if (-not (Test-Path -LiteralPath $configPath) -or -not (Test-Path -LiteralPath $hooksPath)) { throw 'Codex user config and hooks files must exist.' }
if (-not (Test-Path -LiteralPath $python)) { throw 'Repository virtual environment is missing.' }
if (Test-Path -LiteralPath (Join-Path $stateDir 'p116_vscode_install.json')) { throw 'P116 VS Code in-session supervision is already installed.' }
New-Item -ItemType Directory -Path $stateDir -Force | Out-Null

$config = Get-Content -LiteralPath $configPath -Raw
if ($config -match "(?m)^\[mcp_servers\.$serverName\]$") { throw 'P116 in-session MCP server is already configured.' }
$serverBlock = @(
    '',
    "[mcp_servers.$serverName]",
    "command = `"$($python.Replace('\', '/'))`"",
    "args = [`"$($server.Replace('\', '/'))`"]",
    "cwd = `"$($repoRoot.Replace('\', '/'))`"",
    'enabled = true',
    'required = true',
    'enabled_tools = ["supervision_start_run", "supervision_wait_delta", "supervision_close_run"]',
    'default_tools_approval_mode = "auto"',
    'startup_timeout_sec = 10',
    'tool_timeout_sec = 120',
    '',
    "[mcp_servers.$serverName.env]",
    "PYTHONPATH = `"$($repoRoot.Replace('\', '/'))/src`"",
    ''
) -join "`r`n"
$configStaged = Join-Path $stateDir 'config.staged.toml'
[IO.File]::WriteAllText($configStaged, $config.TrimEnd() + "`r`n" + $serverBlock, [Text.UTF8Encoding]::new($false))

$hooks = ConvertTo-Hashtable (Get-Content -LiteralPath $hooksPath -Raw | ConvertFrom-Json)
if (-not $hooks.Contains('hooks')) { $hooks['hooks'] = [ordered]@{} }
$command = "& `"$python`" `"$capture`""
foreach ($eventName in @('PreToolUse', 'PostToolUse')) {
    if (-not $hooks['hooks'].Contains($eventName)) { $hooks['hooks'][$eventName] = @() }
    $hooks['hooks'][$eventName] += [ordered]@{ matcher = '^Bash$'; hooks = @([ordered]@{ type = 'command'; command = $command }) }
}
$hooksStaged = Join-Path $stateDir 'hooks.staged.json'
[IO.File]::WriteAllText($hooksStaged, ($hooks | ConvertTo-Json -Depth 16), [Text.UTF8Encoding]::new($false))

& $python -m agent_workbench.agent_bridge.transaction_cli commit --run-id $InstallId --journal $journal --lock $lock --target "config|$configPath|$configBackup|$configStaged" --target "hooks|$hooksPath|$hooksBackup|$hooksStaged"
if ($LASTEXITCODE -ne 0) { throw 'P116 VS Code installation transaction failed.' }
[IO.File]::WriteAllText((Join-Path $stateDir 'p116_vscode_install.json'), (@{ install_id = $InstallId; mcp_server = $serverName; tools = @('supervision_start_run', 'supervision_wait_delta', 'supervision_close_run') } | ConvertTo-Json), [Text.UTF8Encoding]::new($false))
Write-Output 'P116 in-session supervision installed. Restart VS Code, then invoke $native-supervised-coordinator from the native Codex Coordinator chat.'
