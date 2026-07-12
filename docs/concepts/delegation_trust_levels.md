Delegation Trust Levels
======================

Worker authority is governed by `planning/delegation_policy.md`.

Current default boundary:

- **L0**: No-tool responses and L1 proposal-only work are allowed when bounded and supervisor verification is possible.
- **L2**: Supervisor-applied mutation is allowed only when supervisor-owned tooling applies a worker proposal to an explicitly allowed ignored sandbox target.
- **L3**: Restricted worker tool use is allowed only for narrow trials against explicitly listed ignored runtime paths with observed tool evidence.
- **L4**: Tracked-file mutation is not delegated to workers by default.
- **L5**: GitHub mutation is not delegated to workers by default.
- **L6**: Release or phase-closeout authority is not delegated to workers by default.

Nondelegable supervisor actions include tracked-file commits, branch pushes, PR creation/merge, issue closure, release publication, model/provider configuration changes, and final completion claims.

For full delegation policy details see `planning/delegation_policy.md`.
