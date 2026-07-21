# P107 workflow-package v2 matched workload

`p107-workflow-package-v2` is the self-contained replacement for the earlier
workflow-package ticket. It exists because v1 referred to a planning file that
was not present in the clean test-run worktrees. The task contract below is the
complete worker handoff; no other planning file is required to perform it.

## Task

Extend the public `workflow` CLI from validating and rendering one workflow
step to handling a package of contained step JSON files.

The implementation must:

1. Load a package manifest with `schema_version: "workflow_package_v1"` and a
   `steps` list of contained relative JSON paths.
2. Validate every step with the existing workflow-step validation rules.
3. Validate cross-step artifact references: each generated input consumed by a
   step must have exactly one producer in the package; reject missing producers
   and duplicate produced artifact IDs.
4. Produce deterministic dependency order regardless of manifest ordering and
   reject cycles.
5. Reject malformed manifests or records and paths that escape the manifest
   directory.
6. Write public-safe aggregate JSON including the deterministic `step_order`
   and per-step findings, plus a deterministic Markdown report.
7. Preserve existing single-step CLI behaviour.

Allowed implementation surface: the existing workflow module, one new
workflow-package helper module, the CLI, focused workflow-package tests, and
README documentation. Do not make GitHub changes, commits, provider changes,
or unrelated workflow changes.

## Required focused checks

Add `tests/test_workflow_package.py`. It must exercise:

- a three-step package declared out of dependency order and its deterministic
  `a`, `b`, `c` result order;
- successful JSON and Markdown CLI output;
- rejected path escape, cycle, missing producer, duplicate producer, and
  malformed step or manifest cases; and
- preservation of existing single-step CLI behaviour.

The supplied acceptance script independently exercises the successful package,
CLI output, and path-escape rejection. It is a floor, not a substitute for the
focused tests above.

## C2 operational boundary

The Terra Coordinator delegates the task once to the Ollama Worker and owns
acceptance. It verifies the returned work against this contract and the supplied
acceptance script. If an actual implementation defect is found, it returns that
specific defect to the Worker. A Worker that does not return an inspectable
shared-worktree result is recorded as a worker-route failure for the outer
controller; the Coordinator does not turn that condition into repeated
monitoring, re-specification, or direct implementation.

This v2 workload begins a new matched series; v1 C0/C1/C2 remain diagnostic
observations only.
