# P107 first matched ordinary workload

`p107-workflow-package-v1` extends the existing public `workflow` command from
one step record to a validated multi-step package.

The feature must:

1. load a package manifest and contained workflow-step JSON records;
2. validate each existing step record and cross-step artifact references;
3. build a deterministic dependency order and reject cycles, missing producers,
   duplicate produced artifact IDs, and invalid package paths;
4. emit an aggregate public-safe JSON validation result with per-step findings;
5. render one deterministic Markdown package report through a new CLI route.

Allowed implementation surface: `workflow.py`, a new package helper module,
`cli.py`, focused workflow-package tests, existing workflow tests, and README.
Acceptance uses a clean three-step package plus malformed/cyclic/missing/duplicate
cases, deterministic ordering, and CLI output checks. The same frozen task is
used for clean C0, C1, and C2 observations under the common Agent Hub mission.
