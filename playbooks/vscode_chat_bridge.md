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

## Response Capture Boundary

This phase does not automate response parsing from VS Code Chat.

The bridge can launch a chat session with a bounded prompt. The supervisor still
must inspect worker-reported evidence, local files, and GitHub state directly.
If reliable response capture becomes necessary, it should be planned in a later
phase after real bridge trials show what evidence is missing.

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
