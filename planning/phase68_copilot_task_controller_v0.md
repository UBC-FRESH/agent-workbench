# Phase 68: Copilot Task Controller V0

Phase 68 packages the launch, heartbeat, archive, and review surfaces for one
child-task delegation run. It does not run a live Copilot session by itself; the
v0 controller prepares and verifies the deterministic evidence boundaries.

## Issue And Branch

- Parent issue: #448
- Child issues: #449, #450, #451, #452
- Branch: `feature/p68-copilot-task-controller-v0`

## Controller Boundaries

The controller run manifest ties together:

- high-entropy run id;
- ticket path;
- child issue;
- expected model;
- permission mode;
- heartbeat path;
- result path;
- blocker path;
- archive manifest path;
- token ledger path;
- workspace root; and
- optional budget record when economics are claimed.

The launch prompt intentionally avoids `--maximize` so the coordinator does not
disrupt the operator's VS Code layout. The generated command is a preview
surface, not proof that the UI received or executed the prompt.

## Review Packet

The review packet combines:

- manifest validation;
- heartbeat summary;
- result and blocker presence;
- archive metrics; and
- recommended coordinator decision.

The v0 decision recommendation is intentionally conservative. Missing archive
evidence, missing result files, invalid heartbeat records, or blocker files
produce repair or escalation recommendations rather than success claims.
