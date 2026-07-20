<#
Launch one bounded native Agent Hub job with the P116 supervision control loop.

The run is explicitly supervised: the script stages P116 before creating the
Coordinator, then the fresh Coordinator owns Worker/Supervisor session binding,
event review, same-Worker intervention, and final inspection.  This is not an
SDK or app-server route and does not create a worktree.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Ticket,
    [string]$RunId = ("p116_supervised_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [string]$CodexHome = (Join-Path $env:USERPROFILE ".codex"),
    [string]$Root = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = $repoRoot }
$Root = (Resolve-Path $Root).Path
$ticketPath = (Resolve-Path $Ticket).Path
if (-not $ticketPath.StartsWith($Root, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Ticket must stay within the declared root."
}
if ($RunId -notmatch '^[A-Za-z0-9][A-Za-z0-9_.-]{2,127}$') {
    throw "RunId must be a safe identifier."
}

$runDir = Join-Path $repoRoot "runtime\agent_jobs\$RunId"
$supervisionDir = Join-Path $runDir "supervision"
if (Test-Path -LiteralPath $runDir) { throw "Run directory already exists: $RunDir" }
New-Item -ItemType Directory -Path $supervisionDir -Force | Out-Null

$manifest = [ordered]@{
    schema_version = "p116_supervision_v1"
    run_id = $RunId
    worker_session_id = "worker-placeholder"
    supervisor_session_id = "supervisor-placeholder"
    assigned_root = $Root
    supervision_dir = $supervisionDir
    events_path = "runtime/agent_jobs/$RunId/supervision/events.jsonl"
    cursor_path = "runtime/agent_jobs/$RunId/supervision/cursor.json"
    packets_path = "runtime/agent_jobs/$RunId/supervision/supervisor_packets.jsonl"
    actions_path = "runtime/agent_jobs/$RunId/supervision/coordinator_actions.jsonl"
}
$manifestPath = Join-Path $supervisionDir "manifest.json"
[IO.File]::WriteAllText($manifestPath, ($manifest | ConvertTo-Json -Compress), [Text.UTF8Encoding]::new($false))
Copy-Item -LiteralPath $ticketPath -Destination (Join-Path $runDir "worker_ticket.md")

$promptPath = Join-Path $runDir "coordinator_prompt.md"
$prompt = @"
You are the fresh native Coordinator for supervised job `$RunId` in `$Root`.

The P116 MCP/hook route was staged before this Coordinator started. Native Codex Agent Hub only: do not use SDKs, app-server APIs, a worktree, provider changes, or nested `codex exec`. Preserve unrelated dirty changes. The Worker ticket is `$runDir\worker_ticket.md`; the manifest is `$manifestPath`.

Run this control loop as the job's normal execution, not as a separate proof:

1. Spawn exactly one `gpt_luna_worker` and one `gpt_luna_supervisor`, each with `fork_context:false`. Initially tell both to remain idle without tools.
2. Bind their exact IDs before Worker tools using `python scripts/bind_p116_worker.py --manifest `$manifestPath --worker-session-id <worker> --supervisor-session-id <supervisor>`.
3. Send the Worker the ticket verbatim. While it works, use the native `supervision_wait_delta` MCP tool for meaningful deltas; do not wait for terminal status before reviewing failures, validation errors, material repeats, directive deviations, or terminal events.
4. For a review-worthy delta, resume the same Supervisor if needed and send it the sanitized delta plus the fixed ticket boundary. The Supervisor is advisory only. Ask it to call `supervision_wait_delta` itself when it needs the next delta, then give ordinary-language advice.
5. Independently decide whether intervention is warranted. For a nudge, create and validate a packet against the exact unacknowledged delta using `scripts/p116_supervision_review.py`; send the approved bounded cue only to the same Worker session; then record the action and acknowledge the cursor using `scripts/p116_supervision_controller.py --record-nudge`.
6. Continue until the Worker reaches its ticket stop condition. Inspect its diff and declared validation yourself. Keep quality, protocol, and economics separate; this run does not make a P107 economics claim.

Never nudge ordinary successful progress. Never manufacture a failure merely to exercise supervision. Always leave the run artifacts under `$runDir` for operational review.
"@
[IO.File]::WriteAllText($promptPath, $prompt, [Text.UTF8Encoding]::new($false))

if ($DryRun) {
    [PSCustomObject]@{ run_id = $RunId; root = $Root; manifest = $manifestPath; ticket = (Join-Path $runDir "worker_ticket.md"); coordinator_prompt = $promptPath; staged = $false } | ConvertTo-Json -Compress
    exit 0
}

$enable = Join-Path $repoRoot "scripts\enable_p116_supervision_mcp.ps1"
$stdout = Join-Path $runDir "coordinator.stdout.jsonl"
$stderr = Join-Path $runDir "coordinator.stderr.log"
try {
    & $enable -Mode Enable -RunId $RunId -CodexHome $CodexHome -Root $Root -ProjectRoot $Root
    $codex = (Get-Command codex -ErrorAction Stop).Source
    $process = Start-Process -FilePath $codex -ArgumentList @("exec", "--json", "-C", $Root, "-s", "danger-full-access", "-") -RedirectStandardInput $promptPath -RedirectStandardOutput $stdout -RedirectStandardError $stderr -Wait -PassThru -WindowStyle Hidden
    if ($process.ExitCode -ne 0) { throw "Fresh Coordinator exited with code $($process.ExitCode). Inspect $stderr" }
} finally {
    if (Test-Path -LiteralPath (Join-Path $runDir "p116_staging_manifest.json")) {
        & $enable -Mode Disable -RunId $RunId -CodexHome $CodexHome -Root $Root -ProjectRoot $Root
    }
}

[PSCustomObject]@{ run_id = $RunId; root = $Root; manifest = $manifestPath; ticket = (Join-Path $runDir "worker_ticket.md"); coordinator_stdout = $stdout; coordinator_stderr = $stderr; restored = $true } | ConvertTo-Json -Compress
