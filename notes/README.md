# Notes KB

This directory holds durable, non-planning knowledge for the repository.
It is intended to capture operational lessons, cluster-specific observations,
and workflow patterns that future coding agents can mine when they need
context about how this environment behaves.

## Top-level sections

- clusters/ — host- and cluster-specific facts, scheduler behavior, and hardware notes.
- operations/ — workflow patterns, launch strategies, queueing lessons, and recovery playbooks.

## Frequently needed

- `operations/keklick-copilot-extension-config.md` — where the Keklick Copilot
  custom-endpoint settings live, model-object shape, and the two model-reference
  formats. Read this before hunting for Copilot model config.

## Guidance

- Prefer short, evidence-based notes with concrete facts and observed commands.
- Capture both what worked and what failed so later agents can avoid repeating the same mistakes.
- When a new cluster is tested, add a fresh note rather than relying on memory alone.
