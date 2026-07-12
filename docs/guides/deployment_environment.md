Deployment Environment Playbook
===============================

This guide covers deployment environment setup and operator procedures for Agent Workbench.

> **Status**: This guide is in progress. The current default deployment target is GitHub Pages via the Actions workflow at `.github/workflows/docs.yml`, which builds Sphinx docs with `-W` (warnings as errors) and deploys via `deploy-pages@v4`.

Operator procedures include verifying CI build success, confirming theme rendering on the live site, and checking that all content pages resolve without 404s.
