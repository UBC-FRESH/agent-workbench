<# Enable or disable the run-local P113 native-child adapter route. #>
[CmdletBinding()]
param(
    [ValidateSet('Enable', 'Disable')]
    [string]$Mode = 'Enable',
    [int]$Port = 18889
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$configPath = Join-Path $HOME '.codex\config.toml'
$agentPath = Join-Path $HOME '.codex\agents\ollama_qwen_coder_worker.toml'
$markerStart = '# BEGIN P113 NATIVE ADAPTER'
$markerEnd = '# END P113 NATIVE ADAPTER'

if ($Mode -eq 'Disable') {
    $config = Get-Content -LiteralPath $configPath -Raw
    $config = [regex]::Replace($config, '(?s)' + [regex]::Escape($markerStart) + '.*?' + [regex]::Escape($markerEnd) + '\r?\n?', '')
    $config = $config.Replace('agent-workbench-terra-v1-models-0.144.2-qwen3-coder-function-tools.json', 'agent-workbench-terra-v1-models-0.144.2.json')
    [IO.File]::WriteAllText($configPath, $config, [Text.UTF8Encoding]::new($false))
    $agent = Get-Content -LiteralPath $agentPath -Raw
    $agent = $agent.Replace('model_provider = "agent_workbench_ollama_function_wire_probe"', 'model_provider = "agent_workbench_ollama"')
    [IO.File]::WriteAllText($agentPath, $agent, [Text.UTF8Encoding]::new($false))
    Write-Output 'P113 native adapter route disabled. Start a fresh Codex session.'
    exit 0
}

$runDir = Join-Path $repoRoot 'runtime\agent_jobs\p113_native_in_session'
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$settings = @{}
Get-Content -LiteralPath (Join-Path $HOME '.agent-workbench-env.txt') | ForEach-Object { if ($_ -match '^([^=]+)=(.+)$') { $settings[$matches[1]] = $matches[2] } }
$python = Join-Path ((Split-Path -Parent ((& git -C $repoRoot rev-parse --path-format=absolute --git-common-dir).Trim()))) '.venv\Scripts\python.exe'
$adapter = Join-Path $repoRoot 'scripts\p113_apply_patch_function_adapter.py'
$targetRoot = 'runtime/agent_jobs/p113_native_in_session/target'
New-Item -ItemType Directory -Force -Path (Join-Path $repoRoot $targetRoot) | Out-Null
if (-not (Test-Path -LiteralPath (Join-Path $repoRoot "$targetRoot\alpha.txt"))) { [IO.File]::WriteAllText((Join-Path $repoRoot "$targetRoot\alpha.txt"), "alpha`n", [Text.UTF8Encoding]::new($false)) }
if (-not (Test-Path -LiteralPath (Join-Path $repoRoot "$targetRoot\beta.txt"))) { [IO.File]::WriteAllText((Join-Path $repoRoot "$targetRoot\beta.txt"), "beta`n", [Text.UTF8Encoding]::new($false)) }
if (-not (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath $python -ArgumentList @($adapter, '--port', $Port, '--upstream', $settings['AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL'], '--allowed-root', $targetRoot, '--verdict-log', (Join-Path $runDir 'adapter_verdicts.jsonl'), '--event-log', (Join-Path $runDir 'adapter_events.jsonl'), '--request-log', (Join-Path $runDir 'adapter_requests.jsonl')) -RedirectStandardOutput (Join-Path $runDir 'adapter.stdout.log') -RedirectStandardError (Join-Path $runDir 'adapter.stderr.log') -WindowStyle Hidden
}
$agent = Get-Content -LiteralPath $agentPath -Raw
$agent = $agent.Replace('model_provider = "agent_workbench_ollama"', 'model_provider = "agent_workbench_ollama_function_wire_probe"')
[IO.File]::WriteAllText($agentPath, $agent, [Text.UTF8Encoding]::new($false))
$config = Get-Content -LiteralPath $configPath -Raw
$providerPattern = '(?ms)^\[model_providers\.agent_workbench_ollama\]\r?\n.*?(?=^\[|\z)'
$providerMatch = [regex]::Match($config, $providerPattern)
if (-not $providerMatch.Success) { throw 'Configured Ollama provider block is missing.' }
$probeProvider = $providerMatch.Value.Replace('[model_providers.agent_workbench_ollama]', '[model_providers.agent_workbench_ollama_function_wire_probe]')
$probeProvider = [regex]::Replace($probeProvider, '(?m)^base_url = ".*"$', ('base_url = "http://127.0.0.1:' + $Port + '/v1"'))
if ($probeProvider -eq $providerMatch.Value) { throw 'Configured Ollama provider block has no base_url.' }
$block = "$markerStart`r`n$probeProvider$markerEnd"
$functionCatalog = 'agent-workbench-terra-v1-models-0.144.2-qwen3-coder-function-tools.json'
if (-not (Test-Path -LiteralPath (Join-Path $HOME ".codex\$functionCatalog"))) { throw "Function-tools catalog is missing: $functionCatalog" }
$config = $config.Replace('agent-workbench-terra-v1-models-0.144.2.json', $functionCatalog)
$config = [regex]::Replace($config, '(?s)' + [regex]::Escape($markerStart) + '.*?' + [regex]::Escape($markerEnd), $block)
if ($config -notmatch [regex]::Escape($markerStart)) { $config = $config.TrimEnd() + "`r`n`r`n$block`r`n" }
[IO.File]::WriteAllText($configPath, $config, [Text.UTF8Encoding]::new($false))
Write-Output "P113 native adapter route enabled on port $Port. Start a fresh Codex session, then spawn ollama_qwen_coder_worker with fork_context:false."
