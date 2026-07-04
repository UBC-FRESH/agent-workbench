# Phase 17 Evidence Schema Notes

Phase 17 defines a lightweight evidence store contract for Agent Workbench. The
goal is to make local evidence auditable without turning the repository into a
database, benchmark harness, package, or CI system.

## Artifacts Added

- `templates/evidence_summary.md`: human-readable summary template.
- `templates/evidence_summary.schema.json`: field checklist for structured
  summaries and future local tooling.
- `playbooks/evidence_store.md`: raw evidence versus tracked summary rules.

## Evidence Layout

Raw evidence remains ignored under `runtime/`, `tmp/`, `local/`, and
`outputs/`. Tracked summaries live under `planning/`, `templates/`,
`playbooks/`, and `rubrics/`.

This split matters because model trials and bridge runs may include local
provider references, assistant messages, generated runtime manifests, and
workspace-specific paths that should not be committed.

## Sanitized Summary Fields

The summary contract requires:

- phase/task metadata;
- evidence ID and evidence type;
- repo-relative source runtime paths;
- ticket family and harness/bridge surface;
- model or agent host identity;
- allowed and forbidden authority;
- classification/count outcomes;
- supervisor verification commands and inspections;
- promotion boundary; and
- supervisor decision with rationale.

## Backfilled P15 Summary

Evidence type: `model-run`

Source runtime paths:

- `runtime/agent_jobs/p15_marker_eval/summary.json`
- `runtime/agent_jobs/p15_structured_eval/summary.json`
- `runtime/agent_jobs/p15_patch_eval/summary.json`

Sanitized outcomes:

| Model | Marker | Structured Output | Patch Proposal |
| --- | --- | --- | --- |
| `codestral:latest` | `exact-marker` | `structured-output` | `patch-proposal` |
| `devstral-small-2:latest` | `exact-marker` | `structured-output` | `patch-proposal` |
| `deepseek-coder-v2:16b` | `exact-marker` | `structured-output` | `missing-section` |

Supervisor decision: accept P15 evidence for model-shortlist planning, but keep
raw assistant messages and manifests ignored. Treat the patch-proposal family as
the useful discriminator in this pass.

## Evidence-Retention Decision

Keep the evidence store as an ignored local directory convention plus tracked
summary templates. Do not add a database, schema validator, CI enforcement, or
packaged evidence collector yet. P18 and P19 should test the schema against
richer tool and delegation evidence before P20 revisits packaging.
