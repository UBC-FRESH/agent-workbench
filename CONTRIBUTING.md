# Contributing

Agent Workbench is a public UBC-FRESH sandbox for developing supervised
multi-agent development workflows. Contributions should keep the repository
generic, public-safe, and aligned with the active roadmap phase.

## Workflow

- Check `ROADMAP.md` before starting non-trivial work.
- Use the active phase branch and linked GitHub issues.
- Keep `CHANGE_LOG.md`, roadmap checklists, issue comments, and PR descriptions
  synchronized with completed work.
- Use one parent GitHub issue per roadmap phase.
- Use one child GitHub issue per roadmap task.
- Track roadmap subtasks as checklist items in the child issue body.
- Check off child issue checklist items as subtasks complete.
- Close child issues before closing the parent issue.
- Close the parent issue only after the phase PR merges to `main`.

## Public-Safety Rules

- Do not commit raw agent transcripts, private project notes, credentials,
  generated local outputs, or machine-specific paths.
- Keep `tmp/`, `runtime/`, `local/`, and `outputs/` as ignored local working
  areas.
- Promote only sanitized and generally useful findings into tracked
  `planning/` notes.
- Keep examples generic unless a roadmap phase explicitly introduces a
  public-safe case study.

## Local Checks

For governance-only changes, run:

```bash
git status --short --branch
git diff --check
```

Also inspect changed Markdown files and search for accidental private paths,
credentials, raw transcripts, and unrelated project-specific assumptions.

See `AGENTS.md` for the full agent and development workflow contract.
