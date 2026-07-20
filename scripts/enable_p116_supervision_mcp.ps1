<# Reversibly stage the single P116 supervision wait MCP server. #>
[CmdletBinding()]
param(
    [ValidateSet('Enable', 'Disable')][string]$Mode = 'Enable',
    [Parameter(Mandatory=$true)][string]$RunId,
    [Parameter(Mandatory=$true)][string]$CodexHome,
    [string]$Root = '',
    [string]$ProjectRoot = ''
)
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = $repoRoot }
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $repoRoot }
$runDir = Join-Path $repoRoot "runtime\agent_jobs\$RunId"
$configPath = Join-Path $CodexHome 'config.toml'
$backupPath = Join-Path $runDir 'config.before.toml'
$hooksPath = Join-Path $ProjectRoot '.codex\hooks.json'
$hooksBackupPath = Join-Path $runDir 'hooks.before.json'
$transaction = Join-Path $runDir 'transaction.json'
$lock = Join-Path $runDir 'transaction.lock'
$serverName = ('p116_supervision_' + ($RunId -replace '[^A-Za-z0-9_]', '_'))
$manifestPath = Join-Path $runDir 'supervision\manifest.json'
$sharedRoot = Split-Path -Parent ((& git -C $repoRoot rev-parse --path-format=absolute --git-common-dir).Trim())
$python = Join-Path $sharedRoot '.venv\Scripts\python.exe'

if ($Mode -eq 'Disable') {
    if (-not (Test-Path -LiteralPath $backupPath)) { throw 'P116 transaction backup is missing.' }
    & $python -m agent_workbench.agent_bridge.transaction_cli restore --run-id $RunId --journal $transaction --lock $lock --target "config|$configPath|$backupPath" --target "hooks|$hooksPath|$hooksBackupPath"
    if ($LASTEXITCODE -ne 0) { throw 'P116 transaction restore failed.' }
    $activation = Join-Path $runDir 'supervision\activation.json'
    if (Test-Path -LiteralPath $activation) { Remove-Item -LiteralPath $activation -Force }
    Write-Output "P116 supervision MCP restored: $RunId"
    exit 0
}

if (Test-Path -LiteralPath (Join-Path $runDir 'p116_staging_manifest.json')) { throw "P116 run is already staged: $RunId" }
if (-not (Test-Path -LiteralPath $manifestPath)) { throw 'P116 supervision manifest is missing.' }
if (-not (Test-Path -LiteralPath $configPath)) { throw 'Codex configuration is missing.' }
if (-not (Test-Path -LiteralPath $hooksPath)) { throw 'Project hooks configuration is missing.' }
if (-not (Test-Path -LiteralPath $python)) { throw "Python executable is missing: $python" }
$manifest = (Resolve-Path -LiteralPath $manifestPath).Path.Replace('\','/')
$pythonText = $python.Replace('\','/')
$scriptText = (Join-Path $repoRoot 'scripts\p116_supervision_mcp_server.py').Replace('\','/')
$captureText = (Join-Path $repoRoot 'scripts\p116_capture_hook.py').Replace('\','/')
$existing = Get-Content -LiteralPath $configPath -Raw
if ($existing -match "(?m)^\[mcp_servers\.$serverName\]$") { throw "P116 MCP server is already configured." }
New-Item -ItemType Directory -Path $runDir -Force | Out-Null
$staged = Join-Path $runDir 'config.staged.toml'
$repoText = $repoRoot.Replace('\','/')
$block = @("", "[mcp_servers.$serverName]", "command = `"$pythonText`"", "args = [`"$scriptText`", `"$manifest`"]", "cwd = `"$repoText`"", 'enabled = true', 'required = true', 'enabled_tools = ["supervision_wait_delta"]', 'startup_timeout_sec = 10', 'tool_timeout_sec = 120', "") -join "`r`n"
[IO.File]::WriteAllText($staged, $existing.TrimEnd() + "`r`n" + $block + "`r`n", [Text.UTF8Encoding]::new($false))
if (-not (Test-Path -LiteralPath $hooksPath)) { throw 'Project hooks configuration is missing.' }
$hooksStaged = Join-Path $runDir 'hooks.staged.json'
$hookCommand = "& `"$pythonText`" `"$captureText`""
$hookJson = [ordered]@{ hooks = [ordered]@{
    PreToolUse = @([ordered]@{ matcher='^Bash$'; hooks=@([ordered]@{ type='command'; command=$hookCommand }) })
    PostToolUse = @([ordered]@{ matcher='^Bash$'; hooks=@([ordered]@{ type='command'; command=$hookCommand }) })
} }
[IO.File]::WriteAllText($hooksStaged, ($hookJson | ConvertTo-Json -Depth 10), [Text.UTF8Encoding]::new($false))
$commitArgs = @(' -m','agent_workbench.agent_bridge.transaction_cli','commit')
& $python -m agent_workbench.agent_bridge.transaction_cli commit --run-id $RunId --journal $transaction --lock $lock --target "config|$configPath|$backupPath|$staged" --target "hooks|$hooksPath|$hooksBackupPath|$hooksStaged"
if ($LASTEXITCODE -ne 0) { throw 'P116 transaction commit failed.' }
$activationPath = Join-Path $runDir 'supervision\activation.json'
$activationRecord = [ordered]@{ active=$false; run_id=$RunId; assigned_root=((Resolve-Path $Root).Path); supervision_dir=((Resolve-Path (Join-Path $runDir 'supervision')).Path) }
[IO.File]::WriteAllText($activationPath, ($activationRecord | ConvertTo-Json), [Text.UTF8Encoding]::new($false))
$record = [ordered]@{ run_id=$RunId; mcp_server=$serverName; tool='supervision_wait_delta'; manifest='supervision/manifest.json'; config_backup='config.before.toml'; hooks_backup='hooks.before.json'; transaction_journal='transaction.json'; activation='supervision/activation.json' }
[IO.File]::WriteAllText((Join-Path $runDir 'p116_staging_manifest.json'), ($record | ConvertTo-Json), [Text.UTF8Encoding]::new($false))
Write-Output "P116 supervision MCP enabled: $RunId"
