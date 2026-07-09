# Repair List Execution Overlay

Use this overlay when the task is a bounded list of defects to repair.

- Treat the listed defects as the complete scope.
- Repair one listed defect at a time.
- Do not add opportunistic refactors, cleanup, or new features.
- For each repaired defect, preserve evidence that the exact requested behavior changed.
- If a listed defect is already fixed, record that finding instead of editing.
- Stop and report a blocker when the remaining defects cannot be repaired within the allowed paths or tools.
- Final evidence must map each listed defect to `fixed`, `already-satisfied`, `deferred`, or `blocked`.
