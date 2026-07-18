<# Enable or disable the package-backed Agent Workbench MCP bridge. #>
[CmdletBinding()]
param(
    [ValidateSet('Enable', 'Disable')]
    [string]$Mode = 'Enable',
    [string]$RunId = 'agent_bridge_mcp_r1',
    [string]$CodexHome = (Join-Path $HOME '.codex'),
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
    [string[]]$AllowExecCommand = @(),
    [string[]]$AllowPatchSha256 = @()
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$runDir = Join-Path $repoRoot "runtime\agent_jobs\$RunId"
$configPath = Join-Path $CodexHome 'config.toml'
$backupPath = Join-Path $runDir 'config.before.toml'
$serverName = ('agent_bridge_' + ($RunId -replace '[^A-Za-z0-9_]', '_'))
$sharedRoot = Split-Path -Parent ((& git -C $repoRoot rev-parse --path-format=absolute --git-common-dir).Trim())
$python = (Join-Path $sharedRoot '.venv\Scripts\python.exe').Replace('\', '/')
$srcPath = (Join-Path $repoRoot 'src').Replace('\', '/')
$env:PYTHONPATH = (Join-Path $repoRoot 'src') + [IO.Path]::PathSeparator + $env:PYTHONPATH

function Quote-TomlString {
    param([string]$Value)
    return '"' + (($Value -replace '\\', '\\') -replace '"', '\"') + '"'
}

function Show-ConfigContext {
    param(
        [string]$Path,
        [string]$Pattern,
        [int]$After = 14
    )
    $lines = Get-Content -LiteralPath $Path
    $match = Select-String -LiteralPath $Path -Pattern $Pattern -SimpleMatch | Select-Object -First 1
    if ($null -eq $match) { throw "Expected config context not found: $Pattern" }
    $start = [Math]::Max(1, $match.LineNumber)
    $end = [Math]::Min($lines.Count, $match.LineNumber + $After)
    for ($i = $start; $i -le $end; $i++) {
        Write-Output ("config.toml:{0}: {1}" -f $i, $lines[$i - 1])
    }
}

if ($Mode -eq 'Disable') {
    if (-not (Test-Path -LiteralPath $backupPath)) { throw 'Agent bridge MCP backup is missing.' }
    & $python -m agent_workbench.agent_bridge.transaction_cli restore --run-id $RunId --journal (Join-Path $runDir 'transaction.json') --lock (Join-Path $runDir 'transaction.lock') --target "config|$configPath|$backupPath"
    if ($LASTEXITCODE -ne 0) { throw 'Agent bridge MCP transaction restore failed.' }
    Write-Output "Agent bridge MCP restored: $runDir"
    exit 0
}

if (Test-Path -LiteralPath $runDir) { throw "Run directory already exists: $runDir" }
if (-not (Test-Path -LiteralPath $configPath)) { throw 'Codex configuration is missing.' }
if (-not (Test-Path -LiteralPath $python)) { throw "Python executable is missing: $python" }
$resolvedRoot = (Resolve-Path -LiteralPath $Root).Path.Replace('\', '/')
$config = Get-Content -LiteralPath $configPath -Raw
if ($config -match "(?m)^\[mcp_servers\.$serverName\]$") { throw "MCP server $serverName is already configured." }

New-Item -ItemType Directory -Path $runDir | Out-Null
$log = (Join-Path $runDir 'mcp_events.jsonl').Replace('\', '/')
$argsList = @(
    '-m',
    'agent_workbench.agent_bridge.mcp_server',
    '--run-id',
    $RunId,
    '--root',
    $resolvedRoot,
    '--event-log',
    $log
)
foreach ($command in $AllowExecCommand) {
    $argsList += '--allow-exec-command'
    $argsList += $command
}
foreach ($patchHash in $AllowPatchSha256) {
    $argsList += '--allow-patch-sha256'
    $argsList += $patchHash
}
$argsToml = ($argsList | ForEach-Object { Quote-TomlString $_ }) -join ', '
$serverBlockLines = @(
    '',
    "[mcp_servers.$serverName]",
    "command = ""$python""",
    "args = [$argsToml]",
    "cwd = ""$($repoRoot.Replace('\', '/'))""",
    'enabled = true',
    'required = true',
    'enabled_tools = ["exec", "apply_patch"]',
    'default_tools_approval_mode = "auto"',
    'startup_timeout_sec = 10',
    'tool_timeout_sec = 120',
    '',
    "[mcp_servers.$serverName.env]",
    "PYTHONPATH = ""$srcPath"""
)
$config = $config.TrimEnd() + "`r`n" + ($serverBlockLines -join "`r`n") + "`r`n"
$stagedConfig = Join-Path $runDir 'config.staged.toml'
[IO.File]::WriteAllText($stagedConfig, $config, [Text.UTF8Encoding]::new($false))
& $python -m agent_workbench.agent_bridge.transaction_cli commit --run-id $RunId --journal (Join-Path $runDir 'transaction.json') --lock (Join-Path $runDir 'transaction.lock') --target "config|$configPath|$backupPath|$stagedConfig"
if ($LASTEXITCODE -ne 0) { throw 'Agent bridge MCP transaction commit failed.' }
Show-ConfigContext -Path $configPath -Pattern "[mcp_servers.$serverName]"
$manifest = [ordered]@{
    run_id = $RunId
    mcp_server = $serverName
    tools = @('exec', 'apply_patch')
    root = $Root
    allowed_exec_commands = $AllowExecCommand
    allowed_patch_sha256 = $AllowPatchSha256
    config_backup = 'config.before.toml'
    event_log = 'mcp_events.jsonl'
}
[IO.File]::WriteAllText((Join-Path $runDir 'manifest.json'), ($manifest | ConvertTo-Json), [Text.UTF8Encoding]::new($false))
Write-Output "Agent bridge MCP enabled: $runDir"
