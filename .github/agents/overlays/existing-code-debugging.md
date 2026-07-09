# Existing Code Debugging Overlay

Use this overlay when the task is to debug existing code.

- Reproduce or localize the failure before changing code when practical.
- Prefer the smallest behavioral fix that addresses the observed root cause.
- Preserve existing public contracts unless the ticket explicitly changes them.
- Add or update a regression test that would have failed before the fix.
- Do not hide failures by weakening assertions, broadening exception handling, or skipping tests.
- If the root cause cannot be proven, report the evidence gap and the safest next diagnostic step.
- Final evidence must state the failure signal, root cause, fix, and regression validation.
