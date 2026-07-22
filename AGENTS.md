# AGENTS.md

This file is the working contract for AI coding agents in this repository.

## Provider & Endpoint

A single configured remote vLLM endpoint serves one custom Qwen 3.6 27B
coding model. All roles (Coordinator, Supervisor, Worker, Advisor) share
this model. Role separation comes from bounded instructions and authority,
not architecture.

Endpoint and provider credentials are stored locally in untracked files.
Do not publish URLs or credentials in tracked content.

## Repo Purpose

`agent-workbench` develops, tests, and documents supervised multi-agent
development workflows. The durable output is the workflow contract:
prompts, handoff formats, verification rituals, issue discipline, and
public-safe notes.

Stay generic across the UBC-FRESH ecosystem. Do not encode private project
assumptions as core rules.

## Working Principles

- Read `AGENTS.md`, `ROADMAP.md`, and `CHANGE_LOG.md` before making
  project-shaping changes.
- Keep changes scoped to the active roadmap phase and issue.
- Treat raw transcripts, credentials, and private paths as local working
  material. Promote only sanitized, public-safe findings.
- Prefer file-based handoffs and result files.
- Require evidence for completion claims: diffs, command output, issue URLs,
  or inspected artifacts.
- Treat a worker's prose report as untrusted until verified.
- Preserve uncertainty. If evidence is missing, report a blocker.

## Concurrent Inference

The configured remote vLLM model is concurrency-optimized. Fan out 2-4
parallel agents for independent work. Keep coupled or mutating work serial.

**Parallel** (preferred): code inspection across files, separate tests or
lints, multi-file research, competing hypotheses, background monitoring.
Narrow each agent's objective so they don't overlap.

**Serial** (preferred): same-file mutations, dependent steps, destructive ops,
installs or migrations, final synthesis before committing or publishing.

**Conventions:**

- Default target: **2-4** active agents in parallel.
- Burst limit: up to **6** agents for read-only/diagnostic work; avoid
  sustained **>8** concurrent.
- For parallel agents, require concise findings with artifact paths,
  commands, and confidence.
- Merge parallel findings centrally before editing files.
- Avoid duplicating context across agents; give each agent a distinct slice.
- Reduce fan-out if per-agent latency or quality degrades.

**Coordination:** a Coordinator or Supervisor may fan out independent
subagents, but a single agent at a time should own mutating writes to the
same file or coupled step chain.

## Verdicts

Report quality, protocol, and economics separately:

- **Quality** — does the implementation work?
- **Protocol** — did the session boundary hold?
- **Economics** — what provider usage was captured?

Never collapse these into one vague verdict.

## Repo Layout

- `README.md` — public overview
- `AGENTS.md` — this contract
- `ROADMAP.md` — phase/task plan and issue map
- `CHANGE_LOG.md` — append-only narrative
- `planning/` — sanitized planning notes
- `.github/agents/` — custom agent profiles
- `scripts/` — local helpers (bridge, probe, delegate)
- `tmp/`, `runtime/`, `local/`, `outputs/` — ignored local areas

Do not claim the repo contains a package, CI, benchmark harness, or
extension until a later phase records that evidence.

## Planning Workflow

This repo follows the UBC-FRESH phase/task/subtask workflow:

- `ROADMAP.md` is the current plan and issue tracker map.
- One roadmap phase maps to one GitHub parent issue and one feature branch.
- One roadmap task maps to one child issue linked from the parent issue body.
- Subtasks usually stay as checklist items inside the child issue body.
- Use at most three issue levels: phase, task, implementation subtask.
- Record issue numbers beside roadmap phases and tasks once created.
- Keep `ROADMAP.md`, `CHANGE_LOG.md`, planning notes, issue bodies, and PR
  descriptions synchronized.
- Open a PR from the phase branch to `main` only after phase tasks, tests, docs,
  and closeout notes are complete or explicitly deferred.

## Strict Development Workflow

Use this workflow for active development from the first phase boundary onward:

- One active roadmap phase should generally correspond to one GitHub parent
  issue and one feature branch.
- Create or activate the GitHub parent issue before starting a roadmap phase.
- Create the feature branch from current `main` for that parent issue.
- Create child issues for roadmap tasks under the parent issue.
- Document task subtasks as checklist steps inside the child issue body unless
  they are large enough to deserve third-level implementation issues.
- Work child issues one at a time where practical, usually in roadmap order.
- Before closing a child issue, update every issue-body checklist item to
  checked, or rewrite the issue body to make explicitly clear which items were
  superseded or are not applicable.
- Close each child issue only after its repo changes, documentation, issue-body
  checklist, and verification for that task are complete.
- Keep `ROADMAP.md`, `CHANGE_LOG.md`, and issue comments synchronized as task
  state changes.
- Open a PR from the phase branch back to `main` when the parent issue's child
  issues are complete or explicitly deferred.
- Close the parent issue only after the PR has merged back to `main`.
- Do not start a new active parent issue and branch until the current parent
  issue is closed, unless the maintainer explicitly approves a parallel lane.

## GitHub Issue And Comment Formatting

Formatting matters. GitHub issue bodies and comments must be readable as
rendered Markdown, not flattened prose.

Rules:

- Use short section labels on their own lines, such as `Roadmap task: P3.1`,
  `Parent phase issue: #18`, `Status: active`, and `Checklist:`.
- Use real GitHub task-list syntax, with one checklist item per line.
- Never write inline pseudo-checklists such as
  `Checklist: [ ] first. [ ] second.`
- Wrap branch names, file paths, commands, and commit hashes in backticks.
- For parent phase issues, list child issues as task-list bullets with issue
  numbers and task IDs.
- Before creating or editing several issues, prepare bodies as multi-line
  Markdown strings or temporary body files.

## GitHub Issue Body Quality Standard

Issue bodies are part of the project specification and onboarding material.
Write them so a new lab student, external collaborator, or coding agent can
understand the task, implement it, verify it, and close it without reading the
original chat transcript.

Parent phase issues must include phase identifier, status, branch name, roadmap
links, goal, scope, out-of-scope boundaries, architecture notes, child task
checklist, acceptance criteria, verification, and closeout requirements.

Child task issues must include task identifier, parent phase issue, status,
related planning links, goal, scope, out-of-scope boundaries, subtasks,
acceptance criteria, verification commands, artifacts, risks, and completion
metadata once closed.

Do not create placeholder issue bodies with only a title and a short checklist
unless the maintainer explicitly asks for a placeholder.

## Development Workflow Constraints

- Do not commit, push, create PRs, or mutate GitHub without approval.