<# Run one P113.3 native apply_patch trial through a run-local loopback adapter. #>
[CmdletBinding()]
param(
    [string]$RunId = 'p113_adapter_r1',
    [int]$Port = 18777,
    [switch]$BypassWindowsSandbox
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$commonGitDir = (& git -C $repoRoot rev-parse --path-format=absolute --git-common-dir).Trim()
$sharedRepoRoot = Split-Path -Parent $commonGitDir
$runDir = Join-Path $repoRoot "runtime\agent_jobs\$RunId"
if (Test-Path -LiteralPath $runDir) { throw "Run directory already exists: $runDir" }
New-Item -ItemType Directory -Path $runDir | Out-Null
$targetRoot = Join-Path $runDir 'target'
New-Item -ItemType Directory -Path $targetRoot | Out-Null
[IO.File]::WriteAllText((Join-Path $targetRoot 'alpha.txt'), "alpha`n", [Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText((Join-Path $targetRoot 'beta.txt'), "beta`n", [Text.UTF8Encoding]::new($false))

$settings = @{}
Get-Content -LiteralPath (Join-Path $HOME '.agent-workbench-env.txt') | ForEach-Object { if ($_ -match '^([^=]+)=(.+)$') { $settings[$matches[1]] = $matches[2] } }
$headers = Get-Content -LiteralPath $settings['AGENT_WORKBENCH_PROVIDER_HEADERS_FILE'] -Raw | ConvertFrom-Json

$codexHome = Join-Path $runDir 'codex_home'
New-Item -ItemType Directory -Path $codexHome | Out-Null
Copy-Item -LiteralPath (Join-Path $HOME '.codex\config.toml') -Destination (Join-Path $codexHome 'config.toml')
Copy-Item -LiteralPath (Join-Path $HOME '.codex\agents') -Destination (Join-Path $codexHome 'agents') -Recurse
$configPath = Join-Path $codexHome 'config.toml'
$config = Get-Content -LiteralPath $configPath -Raw
$replacement = 'base_url = "http://127.0.0.1:' + $Port + '/v1"'
$headerMatch = [regex]::Match($config, '(?m)^env_http_headers = \{ (.+) \}$')
if (-not $headerMatch.Success) { throw 'Configured provider header bindings are missing.' }
foreach ($binding in [regex]::Matches($headerMatch.Groups[1].Value, '"([^\"]+)"\s*=\s*"([^\"]+)"')) {
    $headerValue = $headers.PSObject.Properties[$binding.Groups[1].Value].Value
    if (-not $headerValue) { throw "Configured provider header is missing: $($binding.Groups[1].Value)" }
    Set-Item -LiteralPath ("env:" + $binding.Groups[2].Value) -Value $headerValue
}
$upstream = [regex]::Escape($settings['AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL'])
$config = [regex]::Replace($config, ('(?m)^base_url = "' + $upstream + '"$'), $replacement)
if ($config -notmatch [regex]::Escape($replacement)) { throw 'Configured Ollama base_url is missing.' }
$catalog = Join-Path $HOME '.codex\agent-workbench-terra-v1-models-0.144.2-qwen3-coder-function-tools.json'
if (-not (Test-Path -LiteralPath $catalog)) { throw "Function-tools model catalog is missing: $catalog" }
$catalogToml = $catalog.Replace('\', '\\')
$config = [regex]::Replace($config, '(?m)^model_catalog_json = .+$', ('model_catalog_json = "' + $catalogToml + '"'))
[IO.File]::WriteAllText($configPath, $config, [Text.UTF8Encoding]::new($false))

$relativeTarget = "runtime/agent_jobs/$RunId/target"
$ticket = @"
Your only action must be apply_patch. Apply this exact patch as one call:
*** Begin Patch
*** Update File: $relativeTarget/alpha.txt
@@
-alpha
+alpha done
*** Update File: $relativeTarget/beta.txt
@@
-beta
+beta done
*** End Patch

Do not call another tool, retry, inspect files, or change another path. After receiving the tool result, return P113_DONE only.
"@
$ticketPath = Join-Path $runDir 'ticket.md'
[IO.File]::WriteAllText($ticketPath, $ticket, [Text.UTF8Encoding]::new($false))

$python = Join-Path $sharedRepoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw "Shared repository .venv Python is missing: $python" }
$adapter = Join-Path $repoRoot 'scripts\p113_apply_patch_function_adapter.py'
$adapterProcess = Start-Process -FilePath $python -ArgumentList @($adapter, '--port', $Port, '--upstream', $settings['AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL'], '--allowed-root', $relativeTarget, '--verdict-log', (Join-Path $runDir 'adapter_verdicts.jsonl')) -RedirectStandardOutput (Join-Path $runDir 'adapter.stdout.log') -RedirectStandardError (Join-Path $runDir 'adapter.stderr.log') -PassThru -WindowStyle Hidden
try {
    Start-Sleep -Milliseconds 500
    $env:CODEX_HOME = $codexHome
    $codexArgs = @('exec', '-C', $repoRoot, '-s', 'workspace-write', '-c', 'approval_policy="never"', '-c', 'model_provider="agent_workbench_ollama"', '-c', 'apply_patch_tool_type="freeform"', '-m', 'qwen3-coder:latest', '--json', '-o', (Join-Path $runDir 'final.txt'))
    if ($BypassWindowsSandbox) { $codexArgs += '--dangerously-bypass-approvals-and-sandbox' }
    $codexArgs += $ticket
    & codex @codexArgs | Tee-Object -LiteralPath (Join-Path $runDir 'codex_events.jsonl')
    $exitCode = $LASTEXITCODE
} finally {
    if (-not $adapterProcess.HasExited) { Stop-Process -Id $adapterProcess.Id -Force }
}
if ($exitCode -ne 0) { throw "Codex trial failed with exit code $exitCode" }
Write-Output "P113 trial complete: $runDir"
