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

## Serial Inference

The GPU constraint means only one active child at a time. Delegate one
task, wait for completion, inspect, then move on. No parallel fan-out.

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

## Development Workflow

- One roadmap phase = one parent issue + one feature branch.
- Work child tasks one at a time.
- Keep `ROADMAP.md` and `CHANGE_LOG.md` synchronized with issues and PRs.
- Do not commit, push, create PRs, or mutate GitHub without approval.