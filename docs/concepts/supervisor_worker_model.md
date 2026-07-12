Supervisor/Worker Model
=======================

This page explains the supervisor and worker agent roles in Agent Workbench.

The **supervisor** decomposes work into bounded tasks, delegates to workers, verifies outputs independently, and decides whether results are accepted or need revision.

The **worker** executes only the assigned task, stops at the boundary, reports exact command evidence, and avoids broad interpretation unless explicitly asked.

Authority flows from supervisor → worker. Supervisors coordinate; workers execute.

For full details see: `AGENTS.md` in the repository root.
