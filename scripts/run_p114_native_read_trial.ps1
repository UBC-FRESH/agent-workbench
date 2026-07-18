<# Run the P114 R5 native shell-read MWE against the configured Ollama route. #>
[CmdletBinding()]
param(
    [string]$RunId = 'p114_native_read_mwe_r5',
    [string]$TerminalMarker = 'P114_READ_DONE',
    [int]$ProxyPort = 18934,
    [switch]$PatchAfterRead,
    [switch]$ValidateAfterPatch,
    [switch]$CoreAdapter,
    [switch]$CoreReadOnly,
    [switch]$CorePatchOnly,
    [switch]$RepairAfterValidation
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$runDir = Join-Path $repoRoot "runtime\agent_jobs\$RunId"
if (Test-Path -LiteralPath $runDir) { throw "Run directory already exists: $runDir" }
New-Item -ItemType Directory -Path $runDir | Out-Null
$targetRoot = Join-Path $runDir 'target'
New-Item -ItemType Directory -Path $targetRoot | Out-Null
$targetPath = Join-Path $targetRoot 'p114_host_proof.txt'
[IO.File]::WriteAllText($targetPath, "before`n", [Text.UTF8Encoding]::new($false))

$settings = @{}
Get-Content -LiteralPath (Join-Path $HOME '.agent-workbench-env.txt') | ForEach-Object {
    if ($_ -match '^([^=]+)=(.+)$') { $settings[$matches[1]] = $matches[2] }
}
$headers = Get-Content -LiteralPath $settings['AGENT_WORKBENCH_PROVIDER_HEADERS_FILE'] -Raw | ConvertFrom-Json

$codexHome = Join-Path $runDir 'codex_home'
New-Item -ItemType Directory -Path $codexHome | Out-Null
$sourceConfigPath = Join-Path $HOME '.codex\config.toml'
$sourceConfigHashBefore = (Get-FileHash -LiteralPath $sourceConfigPath -Algorithm SHA256).Hash
Copy-Item -LiteralPath $sourceConfigPath -Destination (Join-Path $codexHome 'config.toml')
Copy-Item -LiteralPath (Join-Path $HOME '.codex\agents') -Destination (Join-Path $codexHome 'agents') -Recurse
$configPath = Join-Path $codexHome 'config.toml'
$config = Get-Content -LiteralPath $configPath -Raw
$replacement = 'base_url = "http://127.0.0.1:' + $ProxyPort + '/v1"'
$upstream = [regex]::Escape($settings['AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL'])
$config = [regex]::Replace($config, ('(?m)^base_url = "' + $upstream + '"$'), $replacement)
if ($config -notmatch [regex]::Escape($replacement)) { throw 'Configured Ollama base_url is missing.' }
$headerMatch = [regex]::Match($config, '(?m)^env_http_headers = \{ (.+) \}$')
if (-not $headerMatch.Success) { throw 'Configured provider header bindings are missing.' }
foreach ($binding in [regex]::Matches($headerMatch.Groups[1].Value, '"([^\"]+)"\s*=\s*"([^\"]+)"')) {
    $headerValue = $headers.PSObject.Properties[$binding.Groups[1].Value].Value
    if (-not $headerValue) { throw "Configured provider header is missing: $($binding.Groups[1].Value)" }
    Set-Item -LiteralPath ("env:" + $binding.Groups[2].Value) -Value $headerValue
}
$catalog = Join-Path $HOME '.codex\agent-workbench-terra-v1-models-0.144.2-qwen3-coder-function-tools.json'
if (-not (Test-Path -LiteralPath $catalog)) { throw "Function-tools model catalog is missing: $catalog" }
$catalogToml = $catalog.Replace('\', '\\')
$config = [regex]::Replace($config, '(?m)^model_catalog_json = .+$', ('model_catalog_json = "' + $catalogToml + '"'))
[IO.File]::WriteAllText($configPath, $config, [Text.UTF8Encoding]::new($false))

$relativeTarget = "runtime/agent_jobs/$RunId/target/p114_host_proof.txt"
$forwardWorktree = $repoRoot.Replace('\', '/')
$forwardTarget = $targetPath.Replace('\', '/')
$shellCommand = 'Get-Content -LiteralPath "' + $relativeTarget + '" -Raw; (Get-Location).Path'
$patch = @"
*** Begin Patch
*** Update File: $relativeTarget
@@
-before
+after
*** End Patch
"@
if ($ValidateAfterPatch -and -not $PatchAfterRead) { throw 'Declared validation requires PatchAfterRead.' }
if ($RepairAfterValidation -and -not $CoreAdapter) { throw 'Repair continuation requires CoreAdapter.' }
$validationCommand = 'Get-Content -LiteralPath "' + $relativeTarget + '" -Raw'
if (($CoreReadOnly -or $CorePatchOnly) -and -not $CoreAdapter) { throw 'Core-only modes require CoreAdapter.' }
if ($CoreReadOnly) {
$coreReadCommand = 'Get-Content -LiteralPath "' + $forwardTarget + '" -Raw; (Get-Location).Path'
$ticket = @"
Use exactly one native exec call with these exact arguments:
command: $coreReadCommand
workdir: $forwardWorktree

After receiving the result, return $TerminalMarker only. Do not call any other tool.
"@
} elseif ($CoreAdapter -and $RepairAfterValidation) {
$coreReadCommand = 'Get-Content -LiteralPath "' + $forwardTarget + '" -Raw; (Get-Location).Path'
$coreFailureValidationCommand = 'Get-Content -LiteralPath "' + $forwardTarget + '" -Raw | Out-Null; Write-Error P114_repair_required; exit 17'
$coreFinalValidationCommand = 'Get-Content -LiteralPath "' + $forwardTarget + '" -Raw'
$coreInitialPatch = @"
*** Begin Patch
*** Update File: $forwardTarget
@@
-before
+needs_repair
*** End Patch
"@
$coreRepairPatch = @"
*** Begin Patch
*** Update File: $forwardTarget
@@
-needs_repair
+after
*** End Patch
"@
$ticket = @"
Use exactly five native tool calls in order.

1. exec with these exact arguments:
command: $coreReadCommand
workdir: $forwardWorktree
2. apply_patch with this exact patch:
$coreInitialPatch
3. exec with these exact arguments:
command: $coreFailureValidationCommand
workdir: $forwardWorktree
4. apply_patch with this exact repair patch after that validation reports the declared defect:
$coreRepairPatch
5. exec with these exact arguments:
command: $coreFinalValidationCommand
workdir: $forwardWorktree

Do not use shell writes, Set-Content, other paths, or additional calls. After the final validation result return $TerminalMarker only.
"@
} elseif ($CoreAdapter) {
$coreReadCommand = 'Get-Content -LiteralPath "' + $forwardTarget + '" -Raw; (Get-Location).Path'
$coreValidationCommand = 'Get-Content -LiteralPath "' + $forwardTarget + '" -Raw'
$corePatch = $patch.Replace($relativeTarget, $forwardTarget)
$ticket = @"
Use exactly three native tool calls in order.

1. exec with these exact arguments:
command: $coreReadCommand
workdir: $forwardWorktree
2. apply_patch with this exact patch:
$corePatch
3. exec with these exact arguments:
command: $coreValidationCommand
workdir: $forwardWorktree

Do not use shell writes, Set-Content, other paths, or additional calls. After the validation result return $TerminalMarker only.
"@
} elseif ($ValidateAfterPatch) {
$ticket = @"
Make exactly three native tool calls, in this order.

First, use exactly one native shell command, unchanged:
$shellCommand

After receiving that command result, use exactly one native apply_patch call,
unchanged:
$patch

After receiving the patch result, use exactly one native shell command,
unchanged:
$validationCommand

Do not make any other tool call. Do not use `Set-Content`, another shell write,
a different patch, path, or validation command. After receiving the validation
result, return $TerminalMarker only.
"@
} elseif ($PatchAfterRead) {
$ticket = @"
Make exactly two native tool calls, in this order.

First, use exactly one native shell command, unchanged:
$shellCommand

After receiving that command result, use exactly one native apply_patch call,
unchanged:
$patch

Do not make another shell command after the read. Do not use `Set-Content`,
another shell write, a different patch, another path, or any additional tool
call. After receiving the patch result, return $TerminalMarker only.
"@
} else {
    $ticket = @"
Your only tool action is exactly one native shell command. Use this exact command:
$shellCommand

Do not apply a patch, write a file, inspect another path, alter the command, or
call a second tool.

After receiving the tool result, reply with $TerminalMarker followed by the exact file content and literal CWD.
"@
}
[IO.File]::WriteAllText((Join-Path $runDir 'ticket.md'), $ticket, [Text.UTF8Encoding]::new($false))

$commonGitDir = (& git -C $repoRoot rev-parse --path-format=absolute --git-common-dir).Trim()
$sharedRepoRoot = Split-Path -Parent $commonGitDir
$python = Join-Path $sharedRepoRoot '.venv\Scripts\python.exe'
$translator = if ($CoreAdapter) { Join-Path $repoRoot 'scripts\p114_capability_tool_adapter.py' } else { Join-Path $repoRoot 'scripts\p114_shell_markup_translator.py' }
# Start-Process joins its argument array on Windows; preserve the exact allowed
# command as one argument so the translator can validate it byte-for-byte.
$allowedCommandArgument = '"' + $shellCommand.Replace('"', '\"') + '"'
$translatorArguments = if ($CoreAdapter) { @($translator, '--port', $ProxyPort, '--upstream', $settings['AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL'], '--allowed-root', $forwardWorktree, '--verdict-log', (Join-Path $runDir 'adapter_verdicts.jsonl'), '--event-log', (Join-Path $runDir 'adapter_events.jsonl'), '--request-log', (Join-Path $runDir 'adapter_requests.jsonl'), '--force-initial-exec', '--standard-exec', '--declared-command', ('"' + $coreReadCommand.Replace('"', '\"') + '"'), '--declared-workdir', ('"' + $forwardWorktree.Replace('"', '\"') + '"')) } else { @($translator, '--port', $ProxyPort, '--upstream', $settings['AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL'], '--allowed-command', $allowedCommandArgument, '--request-log', (Join-Path $runDir 'translator_requests.jsonl'), '--response-log', (Join-Path $runDir 'translator_responses.sse')) }
if ($CoreAdapter -and $RepairAfterValidation) {
    $translatorArguments += @('--forced-tool', 'exec', '--forced-tool', 'apply_patch', '--forced-tool', 'exec', '--forced-tool', 'apply_patch', '--forced-tool', 'exec', '--declared-command', ('"' + $coreFailureValidationCommand.Replace('"', '\"') + '"'), '--declared-workdir', ('"' + $forwardWorktree.Replace('"', '\"') + '"'), '--declared-command', ('"' + $coreFinalValidationCommand.Replace('"', '\"') + '"'), '--declared-workdir', ('"' + $forwardWorktree.Replace('"', '\"') + '"'))
} elseif ($CoreAdapter -and -not $CoreReadOnly -and -not $CorePatchOnly) { $translatorArguments += @('--declared-command', ('"' + $coreValidationCommand.Replace('"', '\"') + '"'), '--declared-workdir', ('"' + $forwardWorktree.Replace('"', '\"') + '"')) }
if ($PatchAfterRead -and -not $CoreAdapter) {
    $translatorArguments += @('--allowed-patch', ('"' + $patch.Replace('"', '\"') + '"'))
}
if ($ValidateAfterPatch -and -not $CoreAdapter) {
    $translatorArguments += @('--allowed-validation-command', ('"' + $validationCommand.Replace('"', '\"') + '"'), '--allowed-validation-workdir', ('"' + $repoRoot.Replace('"', '\"') + '"'), '--validation-kind', 'shell')
}
$proxyProcess = Start-Process -FilePath $python -ArgumentList $translatorArguments -RedirectStandardOutput (Join-Path $runDir 'proxy.stdout.log') -RedirectStandardError (Join-Path $runDir 'proxy.stderr.log') -PassThru -WindowStyle Hidden
try {
    Start-Sleep -Milliseconds 500
    $env:CODEX_HOME = $codexHome
    $codexArgs = @('exec', '-C', $repoRoot, '-c', 'approval_policy="never"', '-c', 'model_provider="agent_workbench_ollama"', '-c', 'apply_patch_tool_type="freeform"', '-m', 'qwen3-coder:latest', '--dangerously-bypass-approvals-and-sandbox', '--json', '-o', (Join-Path $runDir 'final.txt'), $ticket)
    & codex @codexArgs | Tee-Object -LiteralPath (Join-Path $runDir 'codex_events.jsonl')
    $exitCode = $LASTEXITCODE
} finally {
    Remove-Item Env:CODEX_HOME -ErrorAction SilentlyContinue
    if (-not $proxyProcess.HasExited) {
        Stop-Process -Id $proxyProcess.Id -Force
        $proxyProcess.WaitForExit()
    }
}
$sourceConfigHashAfter = (Get-FileHash -LiteralPath $sourceConfigPath -Algorithm SHA256).Hash
if ($sourceConfigHashAfter -ne $sourceConfigHashBefore) {
    throw 'Run-scoped configuration altered the normal Codex configuration.'
}
if ($exitCode -ne 0) { throw "Codex R5 read trial failed with exit code $exitCode" }
$expectedTarget = if (($PatchAfterRead -or $CoreAdapter) -and -not $CoreReadOnly) { "after`n" } else { "before`n" }
if ((Get-Content -LiteralPath $targetPath -Raw) -ne $expectedTarget) { throw 'Native trial target content does not match the declared increment.' }
$final = Get-Content -LiteralPath (Join-Path $runDir 'final.txt') -Raw
if ($final -notmatch [regex]::Escape($TerminalMarker)) {
    throw 'Native trial did not return its declared terminal marker.'
}
if (-not $PatchAfterRead -and -not $CoreAdapter -and ($final -notmatch 'before' -or $final -notmatch [regex]::Escape($repoRoot))) {
    throw 'R5 read trial did not return the exact target content and literal CWD.'
}
$completedCommands = Get-Content -LiteralPath (Join-Path $runDir 'codex_events.jsonl') | ForEach-Object { $_ | ConvertFrom-Json } | Where-Object { $_.type -eq 'item.completed' -and $_.item.type -eq 'command_execution' -and $_.item.status -in @('completed', 'failed') }
$expectedCommandCount = if ($CoreAdapter -and $RepairAfterValidation) { 3 } elseif ($CoreAdapter -and -not $CoreReadOnly -and -not $CorePatchOnly) { 2 } else { 1 }
if (@($completedCommands).Count -ne $expectedCommandCount) {
    throw 'Native trial did not record the declared native command count.'
}
if (($PatchAfterRead -or $CoreAdapter) -and -not $CoreReadOnly) {
    $completedPatches = Get-Content -LiteralPath (Join-Path $runDir 'codex_events.jsonl') | ForEach-Object { $_ | ConvertFrom-Json } | Where-Object { $_.type -eq 'item.completed' -and $_.item.type -eq 'file_change' -and $_.item.status -eq 'completed' }
    $expectedPatchCount = if ($CoreAdapter -and $RepairAfterValidation) { 2 } else { 1 }
    if (@($completedPatches).Count -ne $expectedPatchCount) { throw 'Native trial did not record the declared native file change count.' }
}
if ($CoreAdapter -and -not $CoreReadOnly -and -not $CorePatchOnly) {
    if ($RepairAfterValidation -and @($completedCommands)[1].item.exit_code -ne 17) { throw 'Repair continuation did not receive the declared failing validation result.' }
    $validation = @($completedCommands)[-1]
    if ($validation.item.exit_code -ne 0) { throw 'Core-adapter validation did not exit successfully.' }
}
if ($ValidateAfterPatch -and -not $CoreAdapter) {
    if (@($completedCommands).Count -ne 2) { throw 'R7 trial did not record exactly two completed native commands.' }
    $validation = @($completedCommands)[1]
    if ($validation.exit_code -ne 0 -or $validation.aggregated_output -ne "after`n") {
        throw 'R7 trial did not record successful declared validation output.'
    }
}
$deploymentProof = [ordered]@{
    schema_version = 1
    run_id = $RunId
    core_adapter = [bool]$CoreAdapter
    run_scoped_codex_home = $codexHome
    configured_model = 'qwen3-coder:latest'
    configured_provider = 'agent_workbench_ollama'
    literal_worktree = $repoRoot
    adapter_listener = "127.0.0.1:$ProxyPort"
    adapter_teardown_observed = $proxyProcess.HasExited
    normal_config_sha256_before = $sourceConfigHashBefore
    normal_config_sha256_after = $sourceConfigHashAfter
    normal_config_restored = ($sourceConfigHashBefore -eq $sourceConfigHashAfter)
    terminal_marker = $TerminalMarker
    command_count = @($completedCommands).Count
    native_patch_count = if (($PatchAfterRead -or $CoreAdapter) -and -not $CoreReadOnly) { @($completedPatches).Count } else { 0 }
}
[IO.File]::WriteAllText((Join-Path $runDir 'deployment_proof.json'), ($deploymentProof | ConvertTo-Json -Depth 4), [Text.UTF8Encoding]::new($false))
$resultPath = Join-Path $runDir 'result.md'
$result = @"
# P114 Direct-MWE Result

Status: accepted-candidate

Run: `$RunId`

Terminal marker: `$TerminalMarker`

Native command count: $(@($completedCommands).Count)

Native patch count: $(@($completedPatches).Count)

Target: `after`

Validation: final exit code zero
"@
[IO.File]::WriteAllText($resultPath, $result, [Text.UTF8Encoding]::new($false))
$heartbeat = [ordered]@{
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
    checklist_item = 'P114 direct-MWE composite'
    status = 'accepted-candidate'
    action = 'verified native tool sequence'
    artifact_path = $runDir
    command_summary = "$(@($completedCommands).Count) native command executions; $(@($completedPatches).Count) native patches"
    next_intended_action = 'supervisor review of artifact envelope'
}
[IO.File]::WriteAllText((Join-Path $runDir 'heartbeat.jsonl'), (($heartbeat | ConvertTo-Json -Compress) + "`n"), [Text.UTF8Encoding]::new($false))
$archiveManifest = [ordered]@{
    schema_version = 1
    archive_kind = 'direct_codex_exec'
    run_id = $RunId
    ticket = 'ticket.md'
    result = 'result.md'
    heartbeat = 'heartbeat.jsonl'
    event_log = 'codex_events.jsonl'
    adapter_events = 'adapter_events.jsonl'
    adapter_requests = 'adapter_requests.jsonl'
    deployment_proof = 'deployment_proof.json'
    raw_artifacts_retained = $true
}
[IO.File]::WriteAllText((Join-Path $runDir 'archive_manifest.json'), ($archiveManifest | ConvertTo-Json -Depth 4), [Text.UTF8Encoding]::new($false))
Write-Output "P114 R5 native read trial complete: $runDir"
