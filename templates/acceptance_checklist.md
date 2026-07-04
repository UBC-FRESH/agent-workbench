# Acceptance Checklist Template

Use this checklist before accepting worker-agent output.

## Worker Result

- Result file or response reviewed:
- Claimed final status:
- Claimed files changed:
- Claimed GitHub URLs:

## Independent Verification

- [ ] `git status --short --branch` matches the expected branch and cleanliness.
- [ ] Claimed files exist and contain the expected changes.
- [ ] No out-of-scope files changed.
- [ ] Claimed checks were actually run, or the missing checks are documented.
- [ ] Claimed GitHub issues, comments, PRs, or merges exist.
- [ ] Required issue checklists, roadmap entries, changelog entries, and PR body
      agree.
- [ ] No private paths, credentials, raw transcripts, or unrelated
      project-specific content were introduced.
- [ ] The worker did not use "would have", "ready", "should be", or similar
      language as a substitute for completed actions.

## Decision

Choose exactly one:

- `accepted`: evidence is verified and no required work remains.
- `retry`: bounded follow-up ticket is needed.
- `blocked`: progress requires maintainer input or external state change.
- `reject`: worker output is unsafe, incorrect, or outside scope.

## Supervisor Notes

- 
