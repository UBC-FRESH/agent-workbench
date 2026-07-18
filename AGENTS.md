# AGENTS.md

This file is the working contract for AI coding agents in this repository.

## Ollama Endpoint & Provider Headers (Remote Worker)

**Important: every new Copilot session MUST read this section before attempting to launch a probe script.**

The remote Ollama OpenAI-compatible endpoint and provider credentials are stored at:
- `~/.agent-workbench-env.txt` (user home, ignored from git)

Contents of that file:
```
AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL=https://fresh01x.01101.dev/v1
AGENT_WORKBENCH_PROVIDER_HEADERS_FILE=C:\Users\gep\Projects\agent-workbench\runtime\local_provider_headers.json
```

- `/v1` suffix is **required** for the SDK (the bare host `https://fresh01x.01101.dev` is for the VS Code extension only).
- Provider headers use Cloudflare Access Client credentials stored in `runtime/local_provider_headers.json`.
- To use: `. ~/.agent-workbench-env.txt` or read and export the variables in PowerShell:
  ```powershell
  Get-Content $env:USERPROFILE\.agent-workbench-env.txt | ForEach-Object { if ($_ -match '^(\w+)=(.+)$') { Set-Item "env:\$($matches[1])" "$($matches[2])" } }
  ```

## Project Purpose

`agent-workbench` exists to develop, test, and document supervised multi-agent
development workflows for UBC-FRESH software projects.

The main pattern under study is a high-reliability supervisor agent decomposing
work into narrow, evidence-driven tickets for lower-cost worker agents. Worker
agents may run in VS Code Copilot Chat, local Ollama-backed tools, CLI agents, or
other agent hosts. The durable project output is the workflow contract: prompts,
handoff formats, verification rituals, issue discipline, and public-safe notes.

This repository must stay generic across the UBC-FRESH software ecosystem. Do
not encode FEMIC, FreshForge, Patchworks, forestry-modelling, or private project
assumptions as core workflow rules unless a future roadmap phase explicitly adds
that case study as a public-safe example.

## Current Repo State

This repository is an active workflow sandbox. It currently contains governance
documents, planning notes, worker templates, a local VS Code Chat bridge helper,
a local Copilot SDK/Ollama probe scaffold, and Markdown evaluation rubrics:

- `README.md`: concise public overview.
- `AGENTS.md`: agent operating contract.
- `CONTRIBUTING.md`: contributor workflow guide.
- `ROADMAP.md`: phase/task roadmap and issue tracker map.
- `CHANGE_LOG.md`: append-only project narrative.
- `planning/`: sanitized planning notes.
- `.github/agents/`: experimental VS Code workspace custom agents.
- `playbooks/`: public-safe workflow playbooks.
- `templates/`: reusable worker ticket, result, failure, acceptance, and
  evaluation templates.
- `rubrics/`: Markdown scoring rubrics.
- `scripts/`: local repo helper scripts, including local-only bridge/probe
  helpers that write raw evidence to ignored runtime paths.
- `tmp/`, `runtime/`, `local/`, and `outputs/`: ignored local working areas.

Do not claim that this repository contains a package, test framework, CI system,
benchmark harness, VS Code extension, MCP server, or automated model evaluation
suite until a later roadmap phase records that evidence.

## Working Principles

- Read `AGENTS.md`, `ROADMAP.md`, and `CHANGE_LOG.md` before making
  project-shaping changes.
- Keep changes scoped to the active roadmap phase and issue.
- Treat raw agent transcripts, private project notes, credentials, local model
  outputs, and machine-specific paths as local working material by default.
- Promote only sanitized, public-safe findings into tracked planning notes.
- Prefer file-based handoffs and result files when coordinating between agents.
- Require evidence for completion claims: command output, file diffs, issue URLs,
  PR URLs, merge commits, or inspected artifacts.
- Treat a worker agent's prose report as untrusted until the supervisor verifies
  the underlying repo, GitHub, or filesystem state.
- Preserve uncertainty. If a worker cannot prove a command ran or a file changed,
  record that as a blocker rather than smoothing it into success.

## Paid Supervisor Cost Discipline

Agent Workbench must not burn paid supervisor tokens on repetitive experiments
that have no stated purpose or no accumulating evidence. Before a live run,
state the engineering question, the evidence that motivated this run, the
artifact to inspect afterward, and the specific result that would change the
next engineering decision. Record cost when economics are part of the claim.

Continue while results converge: each run should either validate a capability,
rule out a cause, identify the responsible component, or justify a concrete
next repair. Reassess when runs merely repeat the same outcome without changing
the diagnosis. There is no automatic numerical retry limit, stop rule, restart
gate, or maintainer-approval requirement. The developer retains judgment over
whether further work is worthwhile.

A repeated host, bridge, or transport symptom is not by itself proof that the
responsible component is external or unrepairable. Before ending a live lane,
inspect the raw child session and boundary artifacts, distinguish offline
adapter evidence from native-host evidence, and identify the next bounded local
repair or probe. Claim that further work requires outside authority only when
the missing authority or component is named and the local repair/probe surface
has been exhausted.

Controller-local failures after a role, provider, MCP, or route configuration
change are diagnostic rather than terminal: controller state is cached at
startup. If the current controller predates staging, do not infer that an
advertised role or tool is unavailable from one rejected direct call. Before
reporting the lane blocked, inspect the run handoff, recent raw sessions, and
existing runner scripts for the established fresh-controller path. Use that
path when it preserves the exact requested role, one-child limit,
`fork_context:false`, ticket, and no-fallback boundary; then inspect the raw
child and run artifacts before classifying the result.

See `planning/iteration_reasoning_and_convergence.md` for the developer's
standing explanation of reasonable iteration, convergence, and decision signal.

Historical plans, changelog entries, archived benchmarks, and raw run records
may describe earlier caps or halt decisions, but they are evidence only and
never authority to impose a new automatic cap, restart gate, or approval gate.

Separate these outcomes explicitly:

- `quality_validated_candidate`: the local worker/supervisor produced artifacts
  that deterministic validators accept;
- `protocol_accepted_candidate`: the run also obeyed the intended authority and
  workflow boundaries; and
- `economics_usable`: paid-supervisor token spans were captured at the correct
  boundary and the run was not aborted or stale-contaminated.

Never collapse those into a single vague success/failure claim.

## Supervisor And Worker Agent Roles

Supervisor agents are responsible for:

- decomposing work into bounded worker tickets;
- delegating one roadmap child task at a time by default;
- stating exact allowed commands, files, and success criteria;
- selecting worker models only from the configured Ollama host's live
  `ollama list` inventory unless a ticket explicitly includes model
  installation/setup as part of the task;
- verifying worker outputs independently;
- deciding whether a result is accepted, rejected, or needs another ticket; and
- keeping roadmap, changelog, issue, and PR state synchronized.

Worker agents are responsible for:

- executing only the assigned ticket;
- stopping at the requested boundary;
- reporting exact command evidence and errors;
- writing final evidence to the requested result file when asked; and
- avoiding broad interpretation of repository workflow unless the ticket asks
  for it explicitly.

Worker prompts should avoid open-ended requests such as "finish the workflow" or
"do the proper closeout" unless the prompt also includes the exact state machine,
commands, stop conditions, and evidence requirements.

Default delegation unit:

- Delegate one child task, not one whole roadmap phase, unless the whole-phase
  behavior is itself the experiment being measured.
- The coordinator owns phase setup, task sequencing, acceptance decisions,
  commits, branch pushes, PR creation, PR merge, parent issue closure, and final
  completion claims.
- The delegated local supervisor or worker owns only the child task named in
  the ticket and must stop at that boundary.
- A follow-on repair run must cite exact defects from the previous result or
  coordinator decision packet rather than reopening the whole task.

## Delegation Trust Levels

Worker authority is governed by `planning/delegation_policy.md`.

Current default boundary:

- L0 no-tool responses and L1 proposal-only work are allowed when the ticket is
  bounded and supervisor verification is possible.
- L2 supervisor-applied mutation is allowed only when supervisor-owned tooling
  applies a worker proposal to an explicitly allowed ignored sandbox target.
- L3 restricted worker tool use is allowed only for narrow trials against
  explicitly listed ignored runtime paths with observed tool evidence.
- L4 tracked-file mutation is allowed in productive-delegation mode under an
  explicit coordinator/developer-authorized implementation ticket that names the
  allowed files, commands, and stop conditions, keeps edits within those allowed
  paths, and has the supervisor review the diff and run validation before
  returning. See `planning/delegation_policy.md` (Productive-Delegation Mode).
- L5 GitHub mutation and L6 release or phase-closeout authority are not delegated
  to workers.

Nondelegable supervisor actions include tracked-file commits, branch pushes, PR
creation, PR merge, issue closure, release publication, model/provider
configuration changes, and final claims that a roadmap phase is complete.

Current worker-model boundary:

- Treat the configured Ollama host's `ollama list` output as the source of truth
  for available worker models.
- Do not assign non-Ollama models or Ollama models that are not installed in the
  active host inventory by default.
- Do not treat VS Code custom-agent `model` frontmatter as proof of model
  selection. Persisted session evidence must show the expected model before a
  run counts for model comparison.
- Do not treat a Copilot SDK provider/model configuration as proof of successful
  model execution. Captured event/output evidence must show that the run reached
  the expected stop condition before it counts for model comparison.
- Installing a new or larger model is a separate setup task that must include
  the model name, host/session used for installation, and post-install
  verification with `ollama list`.
- Keep public documentation generic: describe the model host as the configured
  Ollama/GPU worker host rather than publishing personal server details.

## File-Based Agent Handoff Protocol

Use ignored local files for raw coordination:

- worker ticket path: `runtime/agent_jobs/<phase_or_task>_ticket.md`
- worker result path: `runtime/agent_jobs/<phase_or_task>_result.md`
- raw transcript path: `tmp/transcripts/<date>_<short-topic>.md`
- Copilot session archive path:
  `runtime/agent_jobs/<run_id>/copilot_session_archive/`

Worker tickets should include:

- current known state;
- governing parent and child issue;
- exact task boundary;
- files or issues in scope;
- commands to run or commands to avoid;
- result, blocker, heartbeat, archive, and token-ledger paths;
- shell and workspace-root context;
- success criteria;
- failure stop conditions; and
- required final evidence format.

Worker result files should include:

- commands actually run;
- files changed;
- tests/checks run;
- GitHub URLs touched;
- exact blockers or error text; and
- final status: `accepted-candidate`, `blocked`, or `needs-supervisor-review`.

Do not commit raw tickets, raw results, or transcripts unless they have been
sanitized and moved into `planning/` as durable public notes.

For Copilot-backed delegation runs, capture the ticket-plus-chatlog behavior
pair before evaluating the run whenever possible. Use:

```text
agent-workbench copilot archive --workspace-root <repo> --output-dir <runtime-dir>
```

The archive must keep raw `chatSessions/*.jsonl` and
`GitHub.copilot-chat/transcripts/*.jsonl` copies in ignored runtime storage and
emit only a sanitized manifest for review. Treat this behavior trace as part of
the evidence unit alongside the worker ticket, result file, final artifacts, and
token/cash ledger. Do not promote raw chat logs into tracked files.

Delegated runs should also append heartbeat records to:

`runtime/agent_jobs/<run_id>.heartbeat.jsonl`

Use `agent-workbench heartbeat validate`, `agent-workbench heartbeat summarize`,
and `agent-workbench nudge suggest` to turn those records into structured
coordinator decisions. Heartbeat files should contain public-safe run metadata
only: checklist item, status, action, artifact path, command summary, and next
intended action. After repeated stale or ineffective nudges in the same lane,
stop and review the ticket, result, blocker, archive, and token/cash ledger
instead of continuing to prompt the local supervisor.

For one child-task Copilot delegation run, prefer a controller manifest that
ties together run id, ticket, child issue, expected model, permission mode,
heartbeat, result, blocker, archive manifest, token ledger, and workspace root.
Use `agent-workbench copilot task-validate`, `task-prompt`, and `task-review`
to check the manifest, generate the bounded Copilot directive, and render the
coordinator review packet. The default controller prompt must not ask VS Code to
maximize or rearrange the UI.

Use `agent-workbench behavior analyze` and `agent-workbench behavior synthesize`
on sanitized Copilot archive manifests and behavior summaries when comparing
delegated-run behavior. Behavior metrics are diagnostic until enough archived
runs exist to support policy tuning; do not tune defaults from a single run.

## Planning Workflow

This repo follows the UBC-FRESH phase/task/subtask workflow:

- `ROADMAP.md` is the current plan and issue tracker map.
- One roadmap phase maps to one GitHub parent issue and one feature branch.
- One roadmap task maps to one child issue linked from the parent issue body.
- Roadmap subtasks usually stay as checklist items inside the child issue body.
- Use at most three issue levels: phase, task, implementation subtask.
- Record issue numbers beside roadmap phases and tasks once created.
- Planned and active roadmap phases must be fleshed out to task/subtask level
  before they are treated as ready for implementation. A phase section with
  only broad one-line task bullets is not sufficiently planned.
- For planned future phases whose GitHub issues do not exist yet, use task IDs
  such as `P60.1` and nested subtask checklists in `ROADMAP.md`; replace `TBD`
  with issue numbers when the phase is activated.
- Keep `ROADMAP.md`, `CHANGE_LOG.md`, planning notes, issue bodies, and PR
  descriptions synchronized.
- Open a PR from the phase branch to `main` only after phase tasks, verification,
  and closeout notes are complete or explicitly deferred.

## Strict Development Workflow

Use this workflow for active development:

- Create or activate the GitHub parent issue before starting a roadmap phase.
- Create the feature branch from current `main` for that parent issue.
- Create child issues for roadmap tasks under the parent issue.
- Document task subtasks as checklist steps inside each child issue body unless
  they are large enough to deserve third-level implementation issues.
- Work child issues one at a time where practical, usually in roadmap order.
- Before closing a child issue, update every issue-body checklist item to
  checked, or rewrite the issue body to make explicitly clear which items were
  superseded or are not applicable.
- Close each child issue only after its repo changes, documentation, issue-body
  checklist, and verification are complete.
- Keep `ROADMAP.md`, `CHANGE_LOG.md`, and issue comments synchronized as task
  state changes.
- Open a PR from the phase branch back to `main` when the parent issue's child
  issues are complete or explicitly deferred.
- Close the parent issue only after the PR has merged back to `main`.
- Do not start a new active parent issue and branch until the current parent
  issue is closed, unless the maintainer explicitly approves a parallel lane.

## GitHub Issue And PR Discipline

Formatting matters. GitHub issue bodies and comments must be readable as
rendered Markdown, not flattened prose.

Rules:

- Use short section labels such as `Roadmap task: P0.1`, `Parent phase issue:
  #1`, `Status: active`, and `Checklist:`.
- Use real GitHub task-list syntax, with one checklist item per line.
- Never write inline pseudo-checklists such as
  `Checklist: [ ] first. [ ] second.`
- Wrap branch names, file paths, commands, and commit hashes in backticks.
- For parent phase issues, list child issues as task-list bullets with issue
  numbers and task IDs.
- Before creating or editing several issues, prepare bodies as multi-line
  Markdown strings or temporary body files.
- If `gh auth status` succeeds, use `gh` for issue comments, issue edits, PR
  creation, PR status checks, merges, and closeout verification.
- Only claim GitHub access is unavailable after running a concrete `gh` command
  and reporting the exact failed command plus error text.

Parent phase issues must include phase identifier, status, branch name, goal,
scope, out-of-scope boundaries, child task checklist, acceptance criteria,
verification, and closeout requirements.

Child task issues must include task identifier, parent phase issue, status, goal,
scope, subtasks, acceptance criteria, verification, and completion metadata once
closed.

## Verification

Default governance-only checks:

```bash
git status --short --branch
git diff --check
```

Before closeout, also inspect the rendered Markdown surfaces and search for:

- personal home-directory paths;
- credentials or tokens;
- raw private transcripts;
- project-specific contamination from unrelated repositories; and
- claims about package, CI, benchmark, extension, or agent-runtime features that
  are not yet implemented.
