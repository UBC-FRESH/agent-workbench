<# Enable or disable the temporary P114 native-session bridge route. #>
[CmdletBinding()]
param(
    [ValidateSet('Enable', 'Disable')]
    [string]$Mode = 'Enable',
    [string]$RunId = 'p114_native_bridge_probe',
    [int]$AdapterPort = 18920,
    [int]$ProviderPort = 18921,
    [string]$Baseline = '139e725ee069c27cf68c797dd66aa88b5bb2824d',
    [string]$ControllerRoot = (Get-Location).Path
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$configPath = Join-Path $HOME '.codex\config.toml'
$agentPaths = @(
    (Join-Path $HOME '.codex\agents\ollama_qwen_coder_worker.toml'),
    (Join-Path $ControllerRoot '.codex\agents\ollama_qwen_coder_worker.toml')
) | Select-Object -Unique
$controllerAgentPath = Join-Path $ControllerRoot '.codex\agents\ollama_qwen_coder_worker.toml'
$catalogNormal = 'agent-workbench-terra-v1-models-0.144.2.json'
$catalogTools = 'agent-workbench-terra-v1-models-0.144.2-qwen3-coder-function-tools.json'
$markerStart = '# BEGIN P114 NATIVE BRIDGE'
$markerEnd = '# END P114 NATIVE BRIDGE'
$providerName = 'agent_workbench_ollama_p114_loopback'

if ($Mode -eq 'Disable') {
    $config = Get-Content -LiteralPath $configPath -Raw
    $config = [regex]::Replace($config, '(?s)' + [regex]::Escape($markerStart) + '.*?' + [regex]::Escape($markerEnd) + '\r?\n?', '')
    $config = $config.Replace($catalogTools, $catalogNormal)
    [IO.File]::WriteAllText($configPath, $config, [Text.UTF8Encoding]::new($false))
    foreach ($agentPath in $agentPaths) {
        if (-not (Test-Path -LiteralPath $agentPath)) { continue }
        $agent = Get-Content -LiteralPath $agentPath -Raw
        $agent = $agent.Replace('model_provider = "' + $providerName + '"', 'model_provider = "agent_workbench_ollama"')
        if ($agentPath -eq $controllerAgentPath) {
            $agent = $agent.Replace('default_permissions = ":workspace"', 'default_permissions = "agent_workbench_ollama_readonly"')
        }
        [IO.File]::WriteAllText($agentPath, $agent, [Text.UTF8Encoding]::new($false))
    }
    $runDir = Join-Path $repoRoot "runtime\agent_jobs\$RunId"
    foreach ($pidFile in @('adapter.pid', 'provider.pid')) {
        $path = Join-Path $runDir $pidFile
        if (Test-Path -LiteralPath $path) { Stop-Process -Id (Get-Content -LiteralPath $path -Raw) -Force -ErrorAction SilentlyContinue }
    }
    Write-Output 'P114 native bridge disabled.'
    exit 0
}

foreach ($agentPath in $agentPaths) {
    if (-not (Test-Path -LiteralPath $agentPath)) {
        throw "Worker profile is missing: $agentPath"
    }
}

$runDir = Join-Path $repoRoot "runtime\agent_jobs\$RunId"
if (Test-Path -LiteralPath $runDir) { throw "Run directory already exists: $runDir" }
New-Item -ItemType Directory -Path $runDir | Out-Null
$worktree = Join-Path $runDir 'worktree'
& git -C $repoRoot worktree add --detach $worktree $Baseline
[IO.File]::WriteAllText((Join-Path $worktree 'p114_host_proof.txt'), "before`n", [Text.UTF8Encoding]::new($false))
$commonGitDir = (& git -C $repoRoot rev-parse --path-format=absolute --git-common-dir).Trim()
$sharedRoot = Split-Path -Parent $commonGitDir
$python = Join-Path $sharedRoot '.venv\Scripts\python.exe'
$provider = Join-Path $repoRoot 'scripts\p114_scripted_provider.py'
$adapter = Join-Path $repoRoot 'scripts\p114_capability_tool_adapter.py'
$worktreeForward = $worktree.Replace('\', '/')
$providerProcess = Start-Process -FilePath $python -ArgumentList @($provider, '--port', $ProviderPort, '--worktree', $worktreeForward, '--request-log', (Join-Path $runDir 'scripted_provider_requests.jsonl')) -RedirectStandardOutput (Join-Path $runDir 'provider.stdout.log') -RedirectStandardError (Join-Path $runDir 'provider.stderr.log') -PassThru -WindowStyle Hidden
$adapterProcess = Start-Process -FilePath $python -ArgumentList @($adapter, '--port', $AdapterPort, '--upstream', "http://127.0.0.1:$ProviderPort/v1", '--allowed-root', $worktreeForward, '--verdict-log', (Join-Path $runDir 'adapter_verdicts.jsonl'), '--event-log', (Join-Path $runDir 'adapter_events.jsonl')) -RedirectStandardOutput (Join-Path $runDir 'adapter.stdout.log') -RedirectStandardError (Join-Path $runDir 'adapter.stderr.log') -PassThru -WindowStyle Hidden
$providerProcess.Id | Set-Content -LiteralPath (Join-Path $runDir 'provider.pid') -NoNewline
$adapterProcess.Id | Set-Content -LiteralPath (Join-Path $runDir 'adapter.pid') -NoNewline

$config = Get-Content -LiteralPath $configPath -Raw
$pattern = '(?ms)^\[model_providers\.agent_workbench_ollama\]\r?\n.*?(?=^\[|\z)'
$sourceProvider = [regex]::Match($config, $pattern)
if (-not $sourceProvider.Success) { throw 'Configured Ollama provider block is missing.' }
$loopbackProvider = $sourceProvider.Value.Replace('[model_providers.agent_workbench_ollama]', '[model_providers.' + $providerName + ']')
$loopbackProvider = [regex]::Replace($loopbackProvider, '(?m)^base_url = ".*"$', ('base_url = "http://127.0.0.1:' + $AdapterPort + '/v1"'))
$block = "$markerStart`r`n$loopbackProvider$markerEnd"
$config = $config.Replace($catalogNormal, $catalogTools)
$config = [regex]::Replace($config, '(?s)' + [regex]::Escape($markerStart) + '.*?' + [regex]::Escape($markerEnd), $block)
if ($config -notmatch [regex]::Escape($markerStart)) { $config = $config.TrimEnd() + "`r`n`r`n$block`r`n" }
[IO.File]::WriteAllText($configPath, $config, [Text.UTF8Encoding]::new($false))
foreach ($agentPath in $agentPaths) {
    $agent = Get-Content -LiteralPath $agentPath -Raw
    $agent = $agent.Replace('model_provider = "agent_workbench_ollama"', 'model_provider = "' + $providerName + '"')
    $agent = [regex]::Replace($agent, '(?m)^model_reasoning_effort = ".*"$', 'model_reasoning_effort = "high"')
    if ($agentPath -eq $controllerAgentPath) {
        $agent = $agent.Replace('default_permissions = "agent_workbench_ollama_readonly"', 'default_permissions = ":workspace"')
    }
    [IO.File]::WriteAllText($agentPath, $agent, [Text.UTF8Encoding]::new($false))
}
Write-Output "P114 native bridge enabled. Spawn one fresh ollama_qwen_coder_worker now; literal worktree: $worktree"
