Alpha Readiness Criteria
======================

Before Agent Workbench can be published as a public-alpha release, the following acceptance criteria must be met:

- [ ] Phase 101 complete — Sphinx documentation builds without warnings or errors
- [ ] GitHub Pages deployment verified and accessible
- [ ] Welcome page, guides, concepts, reference, and roadmap sections all present
- [ ] No private content, credentials, or local paths in published docs
- [ ] CLI reference section documents available subcommands
- [ ] Template catalog reflects current promoted/retired templates
- [ ] All playbooks cross-referenced correctly from documentation surface

**Verification command**: ``sphinx-build -b html docs _build/html -W`` should pass with zero warnings.

For the complete alpha readiness checklist, see Phase 100 (Public Alpha Readiness Review) in `ROADMAP.md`.
