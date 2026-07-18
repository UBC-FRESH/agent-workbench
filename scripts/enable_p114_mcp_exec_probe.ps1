<# Enable or disable the reversible P114 MCP routing probe. #>
[CmdletBinding()]
param(
    [ValidateSet('Enable', 'Disable')]
    [string]$Mode = 'Enable',
    [string]$RunId = 'p114_mcp_exec_probe_r1',
    [switch]$EnableCodeMode,
    [switch]$DirectMcpTools,
    [switch]$AllowPatch,
    [string]$PatchTarget,
    [string]$CodexHome = (Join-Path $HOME '.codex')
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$runDir = Join-Path $repoRoot "runtime\agent_jobs\$RunId"
$configPath = Join-Path $CodexHome 'config.toml'
$backupPath = Join-Path $runDir 'config.before.toml'
$serverName = 'p114_exec_probe'
$sharedRoot = Split-Path -Parent ((& git -C $repoRoot rev-parse --path-format=absolute --git-common-dir).Trim())
$python = (Join-Path $sharedRoot '.venv\Scripts\python.exe').Replace('\', '/')
$env:PYTHONPATH = (Join-Path $repoRoot 'src') + [IO.Path]::PathSeparator + $env:PYTHONPATH

function Show-ConfigContext {
    param(
        [string]$Path,
        [string]$Pattern,
        [int]$After = 10
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
    if (-not (Test-Path -LiteralPath $backupPath)) { throw 'P114 MCP probe backup is missing.' }
    & $python -m agent_workbench.agent_bridge.transaction_cli restore --run-id $RunId --journal (Join-Path $runDir 'transaction.json') --lock (Join-Path $runDir 'transaction.lock') --target "config|$configPath|$backupPath"
    if ($LASTEXITCODE -ne 0) { throw 'P114 MCP probe transaction restore failed.' }
    Write-Output "P114 MCP probe restored: $runDir"
    exit 0
}

if (Test-Path -LiteralPath $runDir) { throw "Run directory already exists: $runDir" }
if (-not (Test-Path -LiteralPath $configPath)) { throw 'Codex configuration is missing.' }
if ($DirectMcpTools -and -not $EnableCodeMode) { throw 'DirectMcpTools requires EnableCodeMode.' }
if ($AllowPatch -and -not $PatchTarget) { throw 'AllowPatch requires PatchTarget.' }
if ($AllowPatch -and -not (Test-Path -LiteralPath $PatchTarget)) { throw "PatchTarget does not exist: $PatchTarget" }
$config = Get-Content -LiteralPath $configPath -Raw
if ($config -match "(?m)^\[mcp_servers\.$serverName\]$") { throw "MCP server $serverName is already configured." }

New-Item -ItemType Directory -Path $runDir | Out-Null
$server = (Join-Path $repoRoot 'scripts\p114_mcp_exec_probe_server.py').Replace('\', '/')
$log = (Join-Path $runDir 'mcp_calls.jsonl').Replace('\', '/')

$serverBlockLines = @(
    '',
    "[mcp_servers.$serverName]",
    "command = ""$python""",
    "args = [""$server""]",
    "cwd = ""$($repoRoot.Replace('\', '/'))""",
    'enabled = true',
    'required = true',
    'enabled_tools = ["p114_exec"]',
    'default_tools_approval_mode = "auto"',
    'startup_timeout_sec = 10',
    'tool_timeout_sec = 20',
    '',
    "[mcp_servers.$serverName.env]",
    "P114_MCP_PROBE_LOG = ""$log"""
)
if ($AllowPatch) {
    $patchTargetForward = (Resolve-Path -LiteralPath $PatchTarget).Path.Replace('\', '/')
    $serverBlockLines += 'P114_MCP_PROBE_ALLOW_PATCH = "1"'
    $serverBlockLines += "P114_MCP_PROBE_TARGET = ""$patchTargetForward"""
}
$config = $config.TrimEnd() + "`r`n" + ($serverBlockLines -join "`r`n") + "`r`n"
if ($EnableCodeMode) {
    # This deliberately leaves both namespace lists empty: `direct_only` would
    # prevent executor exposure, which is the behavior this probe is testing.
    $config = $config.TrimEnd() + "`r`n" + (@(
        '',
        '[features.code_mode]',
        'enabled = true',
        'excluded_tool_namespaces = []',
        'direct_only_tool_namespaces = []'
    ) -join "`r`n") + "`r`n"
}
if ($DirectMcpTools) {
    # The nested code-mode host does not dispatch tool_search. This temporary
    # setting asks Codex to emit MCP tools directly instead of deferring them.
    $config = [regex]::Replace(
        $config,
        '(?ms)(^\[features\]\r?\n.*?)(?=^\[|\z)',
        '$1tool_search_always_defer_mcp_tools = false' + "`r`n",
        1
    )
}
$stagedConfig = Join-Path $runDir 'config.staged.toml'
[IO.File]::WriteAllText($stagedConfig, $config, [Text.UTF8Encoding]::new($false))
& $python -m agent_workbench.agent_bridge.transaction_cli commit --run-id $RunId --journal (Join-Path $runDir 'transaction.json') --lock (Join-Path $runDir 'transaction.lock') --target "config|$configPath|$backupPath|$stagedConfig"
if ($LASTEXITCODE -ne 0) { throw 'P114 MCP probe transaction commit failed.' }
Show-ConfigContext -Path $configPath -Pattern "[mcp_servers.$serverName.env]"
$manifest = [ordered]@{ run_id = $RunId; mcp_server = $serverName; tool = 'p114_exec'; marker = 'P114_MCP_EXEC_HANDLER_REACHED'; patch_marker = 'P114_MCP_PATCH_HANDLER_REACHED'; allow_patch = [bool]$AllowPatch; patch_target = $PatchTarget; code_mode_enabled = [bool]$EnableCodeMode; direct_mcp_tools = [bool]$DirectMcpTools; excluded_tool_namespaces = @(); direct_only_tool_namespaces = @(); config_backup = 'config.before.toml'; call_log = 'mcp_calls.jsonl' }
[IO.File]::WriteAllText((Join-Path $runDir 'manifest.json'), ($manifest | ConvertTo-Json), [Text.UTF8Encoding]::new($false))
Write-Output "P114 MCP probe enabled: $runDir"
