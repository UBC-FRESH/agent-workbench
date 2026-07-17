<# Run one non-live P114.3 Codex host proof using isolated local configuration. #>
[CmdletBinding()]
param(
    [string]$RunId = ('p114_host_proof_' + (Get-Date -Format 'yyyyMMddTHHmmssZ')),
    [int]$AdapterPort = 18914,
    [int]$ProviderPort = 18915,
    [string]$Baseline = '139e725ee069c27cf68c797dd66aa88b5bb2824d',
    [switch]$UseBrokenWindowsSandbox
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$commonGitDir = (& git -C $repoRoot rev-parse --path-format=absolute --git-common-dir).Trim()
$sharedRoot = Split-Path -Parent $commonGitDir
$runDir = Join-Path $repoRoot "runtime\agent_jobs\$RunId"
if (Test-Path -LiteralPath $runDir) { throw "Run directory already exists: $runDir" }
New-Item -ItemType Directory -Path $runDir | Out-Null
$worktree = Join-Path $runDir 'worktree'
$codexHome = Join-Path $runDir 'codex_home'
$userConfig = Join-Path $HOME '.codex\config.toml'
$userAgentDir = Join-Path $HOME '.codex\agents'
$catalog = Join-Path $HOME '.codex\agent-workbench-terra-v1-models-0.144.2-qwen3-coder-function-tools.json'
$python = Join-Path $sharedRoot '.venv\Scripts\python.exe'
$adapter = Join-Path $repoRoot 'scripts\p114_capability_tool_adapter.py'
$provider = Join-Path $repoRoot 'scripts\p114_scripted_provider.py'
foreach ($path in @($userConfig, $userAgentDir, $catalog, $python, $adapter, $provider)) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Required local proof input is missing: $path" }
}

$beforeConfig = (Get-FileHash -Algorithm SHA256 -LiteralPath $userConfig).Hash
$beforeAgents = Get-ChildItem -LiteralPath $userAgentDir -File | Sort-Object Name | ForEach-Object { "$(($_.Name)):$(Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash" }
& git -C $repoRoot worktree add --detach $worktree $Baseline
[IO.File]::WriteAllText((Join-Path $worktree 'p114_host_proof.txt'), "before`n", [Text.UTF8Encoding]::new($false))
New-Item -ItemType Directory -Path $codexHome | Out-Null
Copy-Item -LiteralPath $userConfig -Destination (Join-Path $codexHome 'config.toml')
$configPath = Join-Path $codexHome 'config.toml'
$config = Get-Content -LiteralPath $configPath -Raw
$replacement = 'base_url = "http://127.0.0.1:' + $AdapterPort + '/v1"'
$settings = @{}
Get-Content -LiteralPath (Join-Path $HOME '.agent-workbench-env.txt') | ForEach-Object { if ($_ -match '^([^=]+)=(.+)$') { $settings[$matches[1]] = $matches[2] } }
$headers = Get-Content -LiteralPath $settings['AGENT_WORKBENCH_PROVIDER_HEADERS_FILE'] -Raw | ConvertFrom-Json
$upstream = [regex]::Escape($settings['AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL'])
$config = [regex]::Replace($config, ('(?m)^base_url = "' + $upstream + '"$'), $replacement)
if ($config -notmatch [regex]::Escape($replacement)) { throw 'Configured Ollama base_url is missing from isolated configuration.' }
$catalogToml = $catalog.Replace('\', '\\')
$config = [regex]::Replace($config, '(?m)^model_catalog_json = .+$', ('model_catalog_json = "' + $catalogToml + '"'))
[IO.File]::WriteAllText($configPath, $config, [Text.UTF8Encoding]::new($false))
$headerMatch = [regex]::Match($config, '(?m)^env_http_headers = \{ (.+) \}$')
if (-not $headerMatch.Success) { throw 'Configured provider header bindings are missing from isolated configuration.' }
foreach ($binding in [regex]::Matches($headerMatch.Groups[1].Value, '"([^\"]+)"\s*=\s*"([^\"]+)"')) {
    $headerValue = $headers.PSObject.Properties[$binding.Groups[1].Value].Value
    if (-not $headerValue) { throw "Configured provider header is missing: $($binding.Groups[1].Value)" }
    Set-Item -LiteralPath ("env:" + $binding.Groups[2].Value) -Value $headerValue
}

$worktreeForward = $worktree.Replace('\', '/')
$providerProcess = Start-Process -FilePath $python -ArgumentList @($provider, '--port', $ProviderPort, '--worktree', $worktreeForward, '--request-log', (Join-Path $runDir 'scripted_provider_requests.jsonl')) -RedirectStandardOutput (Join-Path $runDir 'provider.stdout.log') -RedirectStandardError (Join-Path $runDir 'provider.stderr.log') -PassThru -WindowStyle Hidden
$adapterProcess = Start-Process -FilePath $python -ArgumentList @($adapter, '--port', $AdapterPort, '--upstream', "http://127.0.0.1:$ProviderPort/v1", '--allowed-root', $worktreeForward, '--verdict-log', (Join-Path $runDir 'adapter_verdicts.jsonl'), '--event-log', (Join-Path $runDir 'adapter_events.jsonl')) -RedirectStandardOutput (Join-Path $runDir 'adapter.stdout.log') -RedirectStandardError (Join-Path $runDir 'adapter.stderr.log') -PassThru -WindowStyle Hidden
try {
    Start-Sleep -Milliseconds 500
    $env:CODEX_HOME = $codexHome
    $prompt = 'Use the provided native tools exactly as requested by the provider. Do not make additional calls. Return the provider terminal marker.'
    $codex = (Get-Command codex -ErrorAction Stop).Source
    $codexArguments = @('exec', '-C', $worktree, '-c', 'approval_policy="never"', '-c', 'model_provider="agent_workbench_ollama"', '-c', 'apply_patch_tool_type="freeform"', '-m', 'qwen3-coder:latest', '--json', '-o', (Join-Path $runDir 'final.txt'))
    if ($UseBrokenWindowsSandbox) {
        $codexArguments += @('-s', 'workspace-write')
    } else {
        # This host's Windows sandbox setup is known to fail before the native
        # tool bridge runs. The proof remains contained in its detached run
        # worktree and uses no live provider endpoint.
        $codexArguments += '--dangerously-bypass-approvals-and-sandbox'
    }
    # Start-Process joins argument arrays on Windows. Preserve the prompt as
    # one argument so Codex does not reinterpret its second word as a command.
    $codexArguments += ('"' + $prompt.Replace('"', '\"') + '"')
    $codexProcess = Start-Process -FilePath $codex -ArgumentList $codexArguments -RedirectStandardOutput (Join-Path $runDir 'codex_events.jsonl') -RedirectStandardError (Join-Path $runDir 'codex.stderr.log') -PassThru -WindowStyle Hidden
    Wait-Process -Id $codexProcess.Id -Timeout 45 -ErrorAction SilentlyContinue
    if (-not $codexProcess.HasExited) {
        Stop-Process -Id $codexProcess.Id -Force
        throw 'Codex host proof exceeded its 45-second timeout.'
    }
    $codexProcess.Refresh()
    $exitCode = $codexProcess.ExitCode
} finally {
    if (-not $adapterProcess.HasExited) { Stop-Process -Id $adapterProcess.Id -Force }
    if (-not $providerProcess.HasExited) { Stop-Process -Id $providerProcess.Id -Force }
    Remove-Item Env:CODEX_HOME -ErrorAction SilentlyContinue
}
$afterConfig = (Get-FileHash -Algorithm SHA256 -LiteralPath $userConfig).Hash
$afterAgents = Get-ChildItem -LiteralPath $userAgentDir -File | Sort-Object Name | ForEach-Object { "$(($_.Name)):$(Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash" }
$proof = [ordered]@{
    run_id = $RunId
    live_inference = $false
    codex_exit_code = $exitCode
    literal_worktree = $worktree
    target_content = Get-Content -LiteralPath (Join-Path $worktree 'p114_host_proof.txt') -Raw
    terminal_marker = if (Test-Path -LiteralPath (Join-Path $runDir 'final.txt')) { Get-Content -LiteralPath (Join-Path $runDir 'final.txt') -Raw } else { $null }
    original_config_unchanged = $beforeConfig -eq $afterConfig
    original_agents_unchanged = (@($beforeAgents) -join "`n") -eq (@($afterAgents) -join "`n")
}
$proof | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $runDir 'proof_summary.json') -Encoding utf8
if ($exitCode -ne 0) { throw "Codex host proof failed with exit code $exitCode. Inspect $runDir" }
if ($proof.target_content -ne "after`n" -or $proof.terminal_marker -notmatch 'P114_HOST_DONE' -or -not $proof.original_config_unchanged -or -not $proof.original_agents_unchanged) { throw "P114 host proof did not meet its declared acceptance conditions. Inspect $runDir" }
Write-Output "P114 scripted host proof passed: $runDir"
