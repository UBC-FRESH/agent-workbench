# Evidence Store Playbook

Agent Workbench separates raw local evidence from tracked public summaries.
This keeps the repository useful for workflow design without publishing private
model-provider configuration, raw transcripts, or workstation-specific paths.

## Directory Boundary

Raw evidence belongs in ignored local paths:

- `runtime/agent_jobs/`: worker tickets, worker results, SDK manifests, bridge
  reports, model-run summaries, and sandbox outputs.
- `runtime/command_surface_smoke/`: local smoke reports and generated dry-run
  fixtures.
- `tmp/transcripts/`: manually captured chat transcripts, if any.
- `local/` and `outputs/`: scratch outputs that are not ready for public
  promotion.

Tracked summaries belong in public-safe paths:

- `planning/`: phase notes, sanitized findings, and architecture decisions.
- `templates/`: reusable public-safe schema and workflow templates.
- `playbooks/`: durable workflow instructions.
- `rubrics/`: scoring and decision rules.

## Promotion Rules

Promote only the minimum evidence needed for a reviewer to understand the
supervisor decision.

Allowed in tracked files:

- model IDs from the configured inventory;
- classification counts;
- issue and PR numbers;
- repo-relative tracked paths;
- repo-relative ignored runtime paths when needed as evidence pointers;
- exact command names and arguments after private values are redacted; and
- concise supervisor interpretation.

Forbidden in tracked files:

- provider URLs and access headers;
- tokens, credentials, cookies, or personal authentication material;
- personal home-directory paths;
- raw private transcripts;
- long raw assistant messages;
- local SDK cache internals; and
- private project material unrelated to Agent Workbench.

## Summary Shape

Use `templates/evidence_summary.md` for human-readable summaries and
`templates/evidence_summary.schema.json` as the field checklist for local
tooling. A valid summary identifies:

- what phase/task produced the evidence;
- what ticket family or command surface was tested;
- which model or bridge was involved;
- what authority was allowed and forbidden;
- what classification/count outcome was observed;
- what supervisor checks were run; and
- what decision follows from the evidence.

## Supervisor Review

A worker report is never enough by itself. Before promoting a summary, the
supervisor should inspect the relevant runtime report, generated summary, GitHub
object, or filesystem state. If the supervisor did not inspect the raw evidence,
the tracked summary must say that the result is unverified or deferred.
