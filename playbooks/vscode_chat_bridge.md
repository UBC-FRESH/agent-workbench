# VS Code Chat Bridge Playbook

This playbook describes how a supervisor can launch a bounded worker-agent task
through VS Code Chat using the local `code chat` command while keeping
verification outside the chat session.

## Command Surface

The local VS Code command supports:

```text
code chat [options] [prompt]
```

Relevant options:

- `--mode ask|edit|agent`: choose chat mode; use `--mode agent` for worker jobs.
- `--add-file <path>`: attach one or more files as context.
- `--reuse-window`: open the chat session in the last active VS Code window.
- `--new-window`: open a separate window.
- `--maximize`: maximize the chat session view.
- `-`: read prompt content from stdin.

## Standard Launch Pattern

Use an ignored ticket file as the source of truth:

```powershell
Get-Content runtime\agent_jobs\<task>_ticket.md -Raw |
  code chat --mode agent --reuse-window -
```

Add explicit file context only when the worker needs it:

```powershell
Get-Content runtime\agent_jobs\<task>_ticket.md -Raw |
  code chat --mode agent --reuse-window `
    --add-file AGENTS.md `
    --add-file ROADMAP.md `
    -
```

Use `--new-window` when isolation matters more than continuity:

```powershell
Get-Content runtime\agent_jobs\<task>_ticket.md -Raw |
  code chat --mode agent --new-window -
```

## Worker Model Boundary

For now, VS Code Chat worker jobs should use only models available from the
configured Ollama worker host.

Before assigning a worker model, verify the active inventory in the host/session
that will serve the model:

```powershell
ollama list
```

Rules:

- Use the live `ollama list` output as the source of truth.
- Do not assume that a model exists because it is listed in a public Ollama
  library or appears in a prior experiment.
- Do not assign a non-Ollama model for this bridge unless a later phase expands
  the model boundary.
- Treat installing a larger model as a separate setup task with explicit
  post-install verification.
- Keep tickets generic about infrastructure; avoid publishing personal hostnames,
  private endpoints, credentials, or workstation-specific paths.

## File Protocol

Raw worker materials stay ignored by default:

- ticket: `runtime/agent_jobs/<phase_or_task>_ticket.md`
- expected result: `runtime/agent_jobs/<phase_or_task>_result.md`
- optional transcript: `tmp/transcripts/<date>_<short-topic>.md`
- launch note: `runtime/agent_jobs/<phase_or_task>_launch.md`

The ticket should use `templates/supervisor_ticket.md`.

The worker should write or report using `templates/worker_result.md`.

If the worker blocks, use `templates/failure_report.md`.

Promote only sanitized durable findings into `planning/`.

## Supervisor Verification

Do not accept a chat worker's prose report as sufficient evidence.

After a worker candidate, the supervisor verifies:

- repository state with `git status --short --branch`;
- changed files and diffs;
- relevant GitHub issue, PR, comment, and merge state;
- claimed checks and command outputs;
- public-safety boundaries; and
- agreement among roadmap, changelog, issues, and PR body.

Use `templates/acceptance_checklist.md` before accepting a worker result.

Allowed supervisor decisions:

- `accepted`: evidence is verified and no required work remains.
- `retry`: a new bounded worker ticket is needed.
- `blocked`: maintainer input or external state is required.
- `reject`: output is unsafe, incorrect, or outside scope.

## V0 Harness

Phase 3 adds a local-only prototype helper:

```powershell
python scripts\copilot_chat_bridge.py `
  --ticket runtime\agent_jobs\<task>.ticket.md `
  --marker <unique-marker> `
  --workspace-root . `
  --report runtime\agent_jobs\<task>.supervisor.md
```

The helper launches a visible VS Code Chat worker session with stdin, searches
local persisted chat artifacts for the marker, and writes an ignored supervisor
report. The report compares observed terminal commands and file-tool activity
against the ticket.

V0 evidence is local and supervisor-facing. It is not a stable VS Code API
contract, and it does not replace human review.

Current v0 limitations:

- Permission-level values are reported as observed session evidence and may
  contain more than one stored value.
- The verifier treats duplicate terminal commands as deviations when the ticket
  allowed the command only once.
- Worker prose remains non-authoritative; observed tools, files, and GitHub
  state are the evidence surfaces.
- Raw tickets, reports, and transcripts remain ignored unless sanitized and
  intentionally promoted into `planning/`.

## Minimal Dry-Run Command

For public-safe bridge trials, use a ticket that asks the worker to inspect only
generic Agent Workbench governance files and write a result to an ignored path.

Example launch shape:

```powershell
Get-Content runtime\agent_jobs\p2_dry_run_ticket.md -Raw |
  code chat --mode agent --reuse-window `
    --add-file AGENTS.md `
    --add-file templates\supervisor_ticket.md `
    -
```

The supervisor then verifies the expected result file and any claimed actions.
