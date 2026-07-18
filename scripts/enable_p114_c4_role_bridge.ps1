<# Configure one reversible P114.3 C4 Worker role-binding proof. #>
[CmdletBinding()]
param(
    [ValidateSet('Enable', 'Disable')]
    [string]$Mode = 'Enable',
    [string]$RunId = 'p114_c4_role_binding_r1',
    [int]$AdapterPort = 18990,
    [switch]$StripInclude,
    [switch]$Battery,
    [switch]$PatchViaExec,
    [switch]$HostToolInventory,
    [switch]$DynamicExecInventory,
    [switch]$McpInventory,
    [switch]$McpDirectInventory,
    [switch]$McpPatch,
    [switch]$PackageMcp,
    [switch]$PackageMcpExec,
    [switch]$PackageMcpComposite,
    [switch]$PackageMcpBattery,
    [switch]$PackageMcpQualification,
    [string]$QualificationWorktree,
    [string]$CodexHome = (Join-Path $HOME '.codex'),
    [string]$AgentWorkbenchEnvPath = (Join-Path $HOME '.agent-workbench-env.txt')
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$runDir = Join-Path $repoRoot "runtime\agent_jobs\$RunId"
$configPath = Join-Path $CodexHome 'config.toml'
$agentPath = Join-Path $CodexHome 'agents\ollama_qwen_coder_worker.toml'
$backupConfig = Join-Path $runDir 'config.before.toml'
$backupAgent = Join-Path $runDir 'ollama_qwen_coder_worker.before.toml'
$providerName = 'agent_workbench_ollama_p114_c4_role_' + ($RunId -replace '[^A-Za-z0-9_]', '_')
$commonGitDir = (& git -C $repoRoot rev-parse --path-format=absolute --git-common-dir).Trim()
$sharedRoot = Split-Path -Parent $commonGitDir
$python = Join-Path $sharedRoot '.venv\Scripts\python.exe'
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
    if (-not (Test-Path -LiteralPath $backupConfig) -or -not (Test-Path -LiteralPath $backupAgent)) { throw 'P114.3 role-binding backups are missing.' }
    & $python -m agent_workbench.agent_bridge.transaction_cli restore --run-id $RunId --journal (Join-Path $runDir 'transaction.json') --lock (Join-Path $runDir 'transaction.lock') --target "config|$configPath|$backupConfig" --target "agent_role|$agentPath|$backupAgent"
    if ($LASTEXITCODE -ne 0) { throw 'P114.3 role bridge transaction restore failed.' }
    $pidPath = Join-Path $runDir 'adapter.pid'
    if (Test-Path -LiteralPath $pidPath) {
        $adapterPid = [int](Get-Content -LiteralPath $pidPath -Raw)
        Stop-Process -Id $adapterPid -Force -ErrorAction SilentlyContinue
    }
    Write-Output "P114.3 role bridge restored: $runDir"
    exit 0
}

if (($HostToolInventory -or $DynamicExecInventory -or $McpInventory -or $McpDirectInventory -or $McpPatch -or $PackageMcp -or $PackageMcpExec -or $PackageMcpComposite -or $PackageMcpBattery -or $PackageMcpQualification) -and ($Battery -or $PatchViaExec)) { throw 'Inventory/MCP modes cannot be combined with battery or patch-via-exec mode.' }
$mcpOrInventoryModeCount = [int][bool]$HostToolInventory + [int][bool]$DynamicExecInventory + [int][bool]$McpInventory + [int][bool]$McpDirectInventory + [int][bool]$McpPatch + [int][bool]$PackageMcp + [int][bool]$PackageMcpExec + [int][bool]$PackageMcpComposite + [int][bool]$PackageMcpBattery + [int][bool]$PackageMcpQualification
if ($mcpOrInventoryModeCount -gt 1) { throw 'Only one inventory/MCP mode may be enabled.' }

if ($PackageMcpQualification -and (-not $QualificationWorktree -or -not (Test-Path -LiteralPath $QualificationWorktree))) { throw 'PackageMcpQualification requires an existing literal QualificationWorktree.' }
if ((Test-Path -LiteralPath $runDir) -and -not $PackageMcpQualification) { throw "Run directory already exists: $runDir" }
if ($PackageMcpQualification -and -not (Test-Path -LiteralPath (Join-Path $runDir 'qualification_manifest.json'))) { throw 'PackageMcpQualification requires the prepared qualification manifest.' }
if (-not (Test-Path -LiteralPath $configPath) -or -not (Test-Path -LiteralPath $agentPath)) { throw 'Required Codex configuration or C4 Worker role file is missing.' }
if (-not (Test-Path -LiteralPath $runDir)) { New-Item -ItemType Directory -Path $runDir | Out-Null }

$targetRoot = Join-Path $runDir 'target'
if ($PackageMcpQualification) {
    $targetPath = $null
} else {
    New-Item -ItemType Directory -Path $targetRoot | Out-Null
    $targetPath = Join-Path $targetRoot 'p114_host_proof.txt'
    [IO.File]::WriteAllText($targetPath, "before`n", [Text.UTF8Encoding]::new($false))
}
$settings = @{}
Get-Content -LiteralPath $AgentWorkbenchEnvPath | ForEach-Object { if ($_ -match '^([^=]+)=(.+)$') { $settings[$matches[1]] = $matches[2] } }
$adapter = Join-Path $repoRoot 'scripts\p114_capability_tool_adapter.py'
$worktree = if ($PackageMcpQualification) { (Resolve-Path $QualificationWorktree).Path.Replace('\', '/') } else { $repoRoot.Replace('\', '/') }
$target = if ($targetPath) { $targetPath.Replace('\', '/') } else { '__qualification_unused__' }
$packageWorkdir = if ($PackageMcpQualification) { $worktree } else { $targetRoot.Replace('\', '/') }
$readCommand = 'Get-Content -LiteralPath "' + $target + '" -Raw; (Get-Location).Path'
$packageReadCommand = 'python -c "from pathlib import Path; print(Path(''p114_host_proof.txt'').read_text(), end=''''); print(Path.cwd())"'
$packageDefectValidationCommand = 'python -c "from pathlib import Path; value=Path(''p114_host_proof.txt'').read_text(); assert value == ''needs_repair\n'', repr(value); print(''P114_PACKAGE_MCP_REPAIR_REQUIRED''); raise SystemExit(17)"'
$packageValidationCommand = 'python -c "from pathlib import Path; value=Path(''p114_host_proof.txt'').read_text(); assert value == ''after\n'', repr(value); print(''P114_PACKAGE_MCP_PATCH_VALIDATED'')"'
$validationCommand = 'Get-Content -LiteralPath "' + $target + '" -Raw'
$inventoryCommand = 'Write-Output P114_C4_HOST_TOOL_INVENTORY'
$defectValidationCommand = 'Get-Content -LiteralPath "' + $target + '" -Raw | Out-Null; Write-Error P114_repair_required; exit 17'
$patch = @"
*** Begin Patch
*** Update File: $target
@@
-before
+after
*** End Patch
"@
$packagePatch = $patch.Replace($target, ('runtime/agent_jobs/' + $RunId + '/target/p114_host_proof.txt'))
$repairPatch = @"
*** Begin Patch
*** Update File: $target
@@
-needs_repair
+after
*** End Patch
"@
$defectPatch = @"
*** Begin Patch
*** Update File: $target
@@
-before
+needs_repair
*** End Patch
"@
$packageDefectPatch = $defectPatch.Replace($target, ('runtime/agent_jobs/' + $RunId + '/target/p114_host_proof.txt'))
$packageRepairPatch = $repairPatch.Replace($target, ('runtime/agent_jobs/' + $RunId + '/target/p114_host_proof.txt'))
$packageBatteryDefectPatch = "*** Begin Patch`n*** Update File: p114_host_proof.txt`n@@`n-before`n+needs_repair`n*** End Patch"
$packageBatteryRepairPatch = "*** Begin Patch`n*** Update File: p114_host_proof.txt`n@@`n-needs_repair`n+after`n*** End Patch"
$adapterArguments = @($adapter, '--port', $AdapterPort, '--upstream', $settings['AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL'], '--allowed-root', $worktree, '--verdict-log', (Join-Path $runDir 'adapter_verdicts.jsonl'), '--event-log', (Join-Path $runDir 'adapter_events.jsonl'), '--request-log', (Join-Path $runDir 'adapter_requests.jsonl'), '--raw-request-log', (Join-Path $runDir 'adapter_raw_requests.jsonl'), '--upstream-log', (Join-Path $runDir 'adapter_upstream.jsonl'), '--standard-exec')
if ($PackageMcp -or $PackageMcpExec -or $PackageMcpComposite -or $PackageMcpBattery -or $PackageMcpQualification) {
    $packageServerName = 'agent_bridge_' + ($RunId -replace '[^A-Za-z0-9_]', '_')
    $adapterArguments += @('--package-mcp-server', $packageServerName)
    if ($PackageMcpQualification) { $adapterArguments += '--package-mcp-read-file' }
} elseif ($McpInventory -or $McpDirectInventory -or $McpPatch) {
    # Preserve the raw child request for an exact one-tool MCP schema repair.
    if ($McpInventory) { $adapterArguments += '--mcp-inventory-route' }
    if ($McpPatch) { $adapterArguments += @('--mcp-inventory-route', '--mcp-operation', 'patch') }
} elseif ($DynamicExecInventory) {
    $adapterArguments += @('--dynamic-exec-inventory', '--forced-tool', 'exec', '--declared-command', ('"' + $inventoryCommand.Replace('"', '\"') + '"'), '--declared-workdir', ('"' + $worktree.Replace('"', '\"') + '"'))
} elseif ($HostToolInventory) {
    $adapterArguments += @('--host-tool-inventory', '--forced-tool', 'exec', '--declared-command', ('"' + $inventoryCommand.Replace('"', '\"') + '"'), '--declared-workdir', ('"' + $worktree.Replace('"', '\"') + '"'))
} elseif ($Battery) {
    $adapterArguments += @('--forced-tool', 'exec', '--forced-tool', 'apply_patch', '--forced-tool', 'exec', '--forced-tool', 'apply_patch', '--forced-tool', 'exec', '--declared-command', ('"' + $readCommand.Replace('"', '\"') + '"'), '--declared-workdir', ('"' + $worktree.Replace('"', '\"') + '"'), '--declared-patch', ('"' + $defectPatch.Replace('"', '\"') + '"'), '--declared-command', ('"' + $defectValidationCommand.Replace('"', '\"') + '"'), '--declared-workdir', ('"' + $worktree.Replace('"', '\"') + '"'), '--declared-patch', ('"' + $repairPatch.Replace('"', '\"') + '"'), '--declared-command', ('"' + $validationCommand.Replace('"', '\"') + '"'), '--declared-workdir', ('"' + $worktree.Replace('"', '\"') + '"'))
} else {
    $adapterArguments += @('--force-initial-exec', '--declared-command', ('"' + $readCommand.Replace('"', '\"') + '"'), '--declared-workdir', ('"' + $worktree.Replace('"', '\"') + '"'), '--declared-patch', ('"' + $patch.Replace('"', '\"') + '"'), '--declared-command', ('"' + $validationCommand.Replace('"', '\"') + '"'), '--declared-workdir', ('"' + $worktree.Replace('"', '\"') + '"'))
}
if ($StripInclude) { $adapterArguments += '--strip-include' }
if ($PatchViaExec) { $adapterArguments += '--patch-via-exec' }
$adapterProcess = Start-Process -FilePath $python -ArgumentList $adapterArguments -RedirectStandardOutput (Join-Path $runDir 'adapter.stdout.log') -RedirectStandardError (Join-Path $runDir 'adapter.stderr.log') -PassThru -WindowStyle Hidden
[IO.File]::WriteAllText((Join-Path $runDir 'adapter.pid'), $adapterProcess.Id.ToString(), [Text.UTF8Encoding]::new($false))

$config = Get-Content -LiteralPath $configPath -Raw
$providerPattern = '(?ms)^\[model_providers\.agent_workbench_ollama\]\r?\n.*?(?=^\[|\z)'
$providerMatch = [regex]::Match($config, $providerPattern)
if (-not $providerMatch.Success) { throw 'Configured Ollama provider block is missing.' }
$loopbackProvider = $providerMatch.Value.Replace('[model_providers.agent_workbench_ollama]', '[model_providers.' + $providerName + ']')
$loopbackProvider = [regex]::Replace($loopbackProvider, '(?m)^base_url = ".*"$', ('base_url = "http://127.0.0.1:' + $AdapterPort + '/v1"'))
$config += "`r`n$loopbackProvider"
$functionCatalog = 'agent-workbench-terra-v1-models-0.144.2-qwen3-coder-function-tools.json'
$config = $config.Replace('agent-workbench-terra-v1-models-0.144.2.json', $functionCatalog)
$config = [regex]::Replace($config, '(?m)^apply_patch_tool_type = ".*"$', 'apply_patch_tool_type = "freeform"')
if ($config -notmatch '(?m)^apply_patch_tool_type = "freeform"$') { $config = $config.TrimEnd() + "`r`napply_patch_tool_type = `"freeform`"`r`n" }
if ($PackageMcp -or $PackageMcpExec -or $PackageMcpComposite -or $PackageMcpBattery -or $PackageMcpQualification) {
    $server = (Join-Path $repoRoot 'src').Replace('\', '/')
    $packageRoot = if ($PackageMcpBattery -or $PackageMcpQualification) { $packageWorkdir } else { $repoRoot.Replace('\', '/') }
    $packageArgs = @('-m', 'agent_workbench.agent_bridge.mcp_server', '--run-id', $RunId, '--root', $packageRoot, '--event-log', (Join-Path $runDir 'mcp_events.jsonl').Replace('\', '/'))
    if ($PackageMcp -or $PackageMcpComposite) {
        $packageArgs += @('--allow-patch-sha256', (& $python -c "from agent_workbench.agent_bridge.mcp_server import sha256_text; print(sha256_text('''$packagePatch'''))").Trim())
    }
    if ($PackageMcpBattery) {
        $packageArgs += @('--allow-patch-sha256', (& $python -c "from agent_workbench.agent_bridge.mcp_server import sha256_text; print(sha256_text('''$packageBatteryDefectPatch'''))").Trim())
        $packageArgs += @('--allow-patch-sha256', (& $python -c "from agent_workbench.agent_bridge.mcp_server import sha256_text; print(sha256_text('''$packageBatteryRepairPatch'''))").Trim())
    }
    if ($PackageMcpExec -or $PackageMcpComposite -or $PackageMcpBattery) {
        $packageArgs += @('--allow-exec-command', $packageReadCommand)
    }
    if ($PackageMcpComposite -or $PackageMcpBattery) {
        $packageArgs += @('--allow-exec-command', $packageValidationCommand)
    }
    if ($PackageMcpBattery) { $packageArgs += @('--allow-exec-command', $packageDefectValidationCommand) }
    if ($PackageMcpQualification) {
        $qualification = Get-Content -LiteralPath (Join-Path $runDir 'qualification_manifest.json') -Raw | ConvertFrom-Json
        foreach ($path in $qualification.worker_allowed_patch_paths) { $packageArgs += @('--allow-patch-path', $path) }
        foreach ($path in @('runtime/agent_jobs/p107_suite_provenance_audit_bundle_ticket.md', 'runtime/agent_jobs/p107_suite_provenance_audit_bundle_acceptance.py', 'src/agent_workbench/cli.py', 'README.md', 'src/agent_workbench/source_audit.py', 'tests/test_source_audit.py')) { $packageArgs += @('--allow-read-path', $path) }
        foreach ($command in $qualification.frozen_validation_commands) { $packageArgs += @('--allow-exec-command', $command) }
    }
    $quotedArgs = ($packageArgs | ForEach-Object { '"' + (($_ -replace '\\', '\\') -replace '"', '\"') + '"' }) -join ', '
    $enabledTools = if ($PackageMcpQualification) { '["exec", "apply_patch", "read_file"]' } else { '["exec", "apply_patch"]' }
    $config = $config.TrimEnd() + "`r`n`r`n[mcp_servers.$packageServerName]`r`ncommand = `"$($python.Replace('\', '/'))`"`r`nargs = [$quotedArgs]`r`ncwd = `"$worktree`"`r`nenabled = true`r`nrequired = true`r`nenabled_tools = $enabledTools`r`ndefault_tools_approval_mode = `"auto`"`r`nstartup_timeout_sec = 10`r`ntool_timeout_sec = 120`r`n`r`n[mcp_servers.$packageServerName.env]`r`nPYTHONPATH = `"$server`"`r`n"
}
$agent = Get-Content -LiteralPath $agentPath -Raw
$agent = $agent.Replace('model_provider = "agent_workbench_ollama"', 'model_provider = "' + $providerName + '"')
$stagedConfig = Join-Path $runDir 'config.staged.toml'
$stagedAgent = Join-Path $runDir 'ollama_qwen_coder_worker.staged.toml'
[IO.File]::WriteAllText($stagedConfig, $config, [Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($stagedAgent, $agent, [Text.UTF8Encoding]::new($false))
& $python -m agent_workbench.agent_bridge.transaction_cli commit --run-id $RunId --journal (Join-Path $runDir 'transaction.json') --lock (Join-Path $runDir 'transaction.lock') --target "config|$configPath|$backupConfig|$stagedConfig" --target "agent_role|$agentPath|$backupAgent|$stagedAgent"
if ($LASTEXITCODE -ne 0) {
    Stop-Process -Id $adapterProcess.Id -Force -ErrorAction SilentlyContinue
    throw 'P114.3 role bridge transaction commit failed.'
}
Show-ConfigContext -Path $configPath -Pattern "[model_providers.$providerName]"

$ticket = if ($PackageMcpQualification) { @"
You are the frozen ollama_qwen_coder_worker C4 qualification Worker. Work only
in this literal detached worktree:
$worktree

The frozen workload ticket is at:
runtime/agent_jobs/p107_suite_provenance_audit_bundle_ticket.md

Use deferred discovery first with query:
$packageServerName exec apply_patch read_file

After discovery, use only the discovered package MCP read_file, apply_patch,
and exec tools. Read only declared files, change only the four paths listed by
the frozen ticket, and use apply_patch to implement the workload before any
validation. At the pinned baseline, source_audit.py and test_source_audit.py
are intentionally absent creation targets; FILE_ABSENT is not a permission
failure. Do not use an undeclared discovery or listing command.

For actual CLI patch context, use bounded read_file calls for
src/agent_workbench/cli.py lines 1 through 70 and lines 1660 through 1710.
Do not invent placeholder context such as "existing code" in a patch.

Implement in this order: create source_audit.py; add its import in the real
CLI import block; add the source-audit parser immediately before the real
parser.set_defaults(func=run_overview) line; create test_source_audit.py with
the ticket's required cases; then add the compact README example. Before a
patch to an existing file, read the exact local line range that the patch will
replace. The two absent files are new-file patches, not update patches.

Protocol rule: do not call exec until the two final validation commands below.
Do not call ls, pip, echo, import checks, or any other command. A denied tool
call invalidates this observation. Each patch must be a complete standard
unified diff whose hunk context comes from a declared read_file result; never
use ellipses or placeholder lines. If one patch is rejected, do not retry that
same patch. Continue only with a new patch based on declared read output.

After at least one apply_patch call, run only these exact validation commands
from the worktree root, in order:
1. python -m pytest -q tests/test_source_audit.py
2. python runtime/agent_jobs/p107_suite_provenance_audit_bundle_acceptance.py

Do not use shell, direct exec, direct apply_patch, files, other MCP tools,
GitHub, or configuration tools. Do not edit the materialized frozen ticket,
fixture, or manifest. Report the exact validation result and stop.
"@ } elseif ($PackageMcpBattery) { @"
You are the frozen ollama_qwen_coder_worker C4 Worker. Work only in this literal worktree:
$worktree

This is the bounded package-MCP battery. Use exactly these six MCP calls, in order:
1. tool_search with query $packageServerName exec apply_patch.
2. The discovered package MCP exec tool with command $packageReadCommand and workdir $packageWorkdir.
3. The discovered package MCP apply_patch tool with this exact defect patch:
$packageBatteryDefectPatch
4. The discovered package MCP exec tool with command $packageDefectValidationCommand and workdir $packageWorkdir.
5. The discovered package MCP apply_patch tool with this exact repair patch:
$packageBatteryRepairPatch
6. The discovered package MCP exec tool with command $packageValidationCommand and workdir $packageWorkdir.

Do not use shell, direct exec, direct apply_patch, files, any other tool, or extra calls. After the final MCP result, return exactly:
P114_C4_PACKAGE_MCP_BATTERY_DONE
"@ } elseif ($PackageMcpComposite) { @"
You are the frozen ollama_qwen_coder_worker C4 Worker. Work only in this literal worktree:
$worktree

This is the bounded package-MCP composite proof. Use exactly these four MCP calls, in order:
1. tool_search with query $packageServerName exec apply_patch.
2. The discovered package MCP exec tool with this exact command and workdir:
   command: $packageReadCommand
   workdir: $packageWorkdir
3. The discovered package MCP apply_patch tool with this exact patch:
$packagePatch
4. The discovered package MCP exec tool with this exact command and workdir:
   command: $packageValidationCommand
   workdir: $packageWorkdir

Do not use shell, direct exec, direct apply_patch, files, any other tool, or extra calls. After the final MCP result, return exactly:
P114_C4_PACKAGE_MCP_COMPOSITE_DONE
"@ } elseif ($PackageMcpExec) { @"
You are the frozen ollama_qwen_coder_worker C4 Worker. Work only in this literal worktree:
$worktree

This is the bounded package-MCP exec proof. Use exactly these two MCP calls, in order:
1. tool_search with query $packageServerName exec apply_patch.
2. The discovered package MCP exec tool with this exact command and workdir:
   command: $packageReadCommand
   workdir: $packageWorkdir

Do not use the package MCP apply_patch tool, shell, direct exec, direct apply_patch, files, any other tool, or extra calls. After the final MCP result, return exactly:
P114_C4_PACKAGE_MCP_EXEC_DONE
"@ } elseif ($PackageMcp) { @"
You are the frozen ollama_qwen_coder_worker C4 Worker. Work only in this literal worktree:
$worktree

This is the bounded package-MCP patch proof. Use exactly these two MCP calls, in order:
1. tool_search with query $packageServerName exec apply_patch.
2. The discovered package MCP apply_patch tool with this exact patch:
$packagePatch

Do not use the package MCP exec tool, shell, direct exec, direct apply_patch, files, any other tool, or extra calls. After the final MCP result, return exactly:
P114_C4_PACKAGE_MCP_DONE
"@ } elseif ($McpDirectInventory) { @"
You are the frozen ollama_qwen_coder_worker C4 Worker. Work only in this literal worktree:
$worktree

This is a no-mutation direct-MCP routing proof. Use exactly one discovered MCP
tool call: server p114_exec_probe, tool p114_exec, arguments
{"operation":"inventory"}. Do not use tool_search, shell, exec, apply_patch,
files, other tools, or extra calls. After the successful MCP result, return
exactly:
P114_C4_DIRECT_MCP_ROUTING_DONE
"@ } elseif ($McpInventory) { @"
You are the frozen ollama_qwen_coder_worker C4 Worker. Work only in this literal worktree:
$worktree

This is a no-mutation MCP routing proof. Use exactly these two calls, in order:
1. tool_search with query p114_exec_probe p114_exec inventory.
2. The single discovered MCP tool call for server p114_exec_probe, tool
   p114_exec, arguments {"operation":"inventory"}.

Do not use shell, exec, apply_patch, files, other tools, or extra calls. After
the successful MCP result, return exactly:
P114_C4_MCP_ROUTING_DONE
"@ } elseif ($McpPatch) { @"
You are the frozen ollama_qwen_coder_worker C4 Worker. Work only in this literal worktree:
$worktree

This is a bounded MCP patch proof against the already configured ignored target:
$target

Use exactly these two calls, in order:
1. tool_search with query p114_exec_probe p114_exec patch.
2. The single discovered MCP tool call for server p114_exec_probe, tool
   p114_exec, arguments {"operation":"patch"}.

Do not use shell, exec, apply_patch, files, other tools, or extra calls. After
the successful MCP result, return exactly:
P114_C4_MCP_PATCH_DONE
"@ } elseif ($DynamicExecInventory) { @"
You are the frozen ollama_qwen_coder_worker C4 Worker. Work only in this literal worktree:
$worktree

This is a no-mutation dynamic-tool inheritance preflight. Use exactly one native call:
1. exec command: $inventoryCommand
   workdir: $worktree

The bridge replaces that declared sentinel with the registered `p114_exec`
dynamic function call using only `{"operation":"inventory"}`. Do not
inspect files, use shell writes, apply a patch, make another tool call, or infer
tools from prior runs.

After the one call, return exactly: P114_C4_DYNAMIC_EXEC_INHERITANCE_DONE
"@ } elseif ($HostToolInventory) { @"
You are the frozen ollama_qwen_coder_worker C4 Worker. Work only in this literal worktree:
$worktree

This is a no-mutation host-capability preflight. Use exactly one native call:
1. exec command: $inventoryCommand
   workdir: $worktree

The bridge replaces that declared sentinel with executor-local JavaScript that
prints the current ALL_TOOLS names. Do not inspect files, use shell writes,
apply a patch, make another tool call, or infer tools from prior runs.

After the one call, return exactly: P114_C4_HOST_TOOL_INVENTORY_DONE
"@ } elseif ($Battery) { @"
You are the frozen ollama_qwen_coder_worker C4 Worker. Work only in this literal worktree:
$worktree

Use exactly five native calls in order:
1. exec command: $readCommand
   workdir: $worktree
2. apply_patch with this exact defect patch:
$defectPatch
3. exec command: $defectValidationCommand
   workdir: $worktree
4. apply_patch with this exact repair patch:
$repairPatch
5. exec command: $validationCommand
   workdir: $worktree

Do not use shell writes, Set-Content, undeclared tools, other paths, or extra calls. After final validation return P114_C4_BATTERY_DONE only.
"@ } else { @"
You are the frozen `ollama_qwen_coder_worker` C4 Worker. Work only in this literal worktree:
$worktree

Use exactly three native calls in order:
1. exec command: $readCommand
   workdir: $worktree
2. apply_patch with this exact patch:
$patch
3. exec command: $validationCommand
   workdir: $worktree

Do not use shell writes, Set-Content, undeclared tools, other paths, or extra calls. After validation return P114_C4_ROLE_DONE only.
"@ }
[IO.File]::WriteAllText((Join-Path $runDir 'ticket.md'), $ticket, [Text.UTF8Encoding]::new($false))
$manifest = [ordered]@{ run_id = $RunId; worker_role = 'ollama_qwen_coder_worker'; model = 'qwen3-coder:latest'; provider = $providerName; literal_worktree = $worktree; target = $targetPath; adapter_port = $AdapterPort; battery = [bool]($Battery -or $PackageMcpBattery); package_mcp_battery = [bool]$PackageMcpBattery; package_mcp_qualification = [bool]$PackageMcpQualification; host_tool_inventory = [bool]$HostToolInventory; dynamic_exec_inventory = [bool]$DynamicExecInventory; mcp_inventory = [bool]$McpInventory; mcp_direct_inventory = [bool]$McpDirectInventory; mcp_patch = [bool]$McpPatch; package_mcp = [bool]$PackageMcp; package_mcp_exec = [bool]$PackageMcpExec; package_mcp_composite = [bool]$PackageMcpComposite; package_mcp_server = $packageServerName; ticket = 'ticket.md' }
[IO.File]::WriteAllText((Join-Path $runDir 'role_binding_manifest.json'), ($manifest | ConvertTo-Json), [Text.UTF8Encoding]::new($false))
Write-Output "P114.3 role bridge enabled: $runDir"
