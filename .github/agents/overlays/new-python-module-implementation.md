# New Python Module Implementation Overlay

Use this overlay when the task is to add a new Python module.

- Match the package's existing module layout, naming, typing, and test style.
- Keep public APIs small and explicit.
- Prefer ordinary Python data structures and existing local helpers before adding abstractions.
- Add focused tests that exercise the module's externally visible behavior.
- Avoid broad package restructuring unless the ticket explicitly requires it.
- Document only behavior that users or future maintainers need to rely on.
- Final evidence must identify the new module, tests added, and validation commands run.
