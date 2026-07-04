# Phase 21 Minimal Package And CLI Notes

Phase 21 adds the smallest local Python package and CLI skeleton needed to make
Agent Workbench supervisor tooling easier to install and discover.

## Added Surfaces

- `pyproject.toml`: package metadata and `agent-workbench` console script.
- `src/agent_workbench/__init__.py`: importable package namespace and version.
- `src/agent_workbench/__main__.py`: `python -m agent_workbench` entrypoint.
- `src/agent_workbench/cli.py`: minimal argparse CLI with help and version.

## Boundaries

P21 does not wrap existing scripts yet. It only creates the package and CLI
entrypoint that P22 can extend.

P21 does not change worker trust levels. Tracked-file mutation, GitHub mutation,
issue closure, PR merge, release, and phase closeout remain supervisor-only.

P21 does not add CI, docs builds, release automation, VS Code extension, MCP,
hosted agent, dashboard, or benchmark harnesses.

## Verification Expectations

The package skeleton is considered usable when:

- `python -m pip install -e .` succeeds in the local development environment;
- `agent-workbench --help` works;
- `agent-workbench --version` works;
- `python -m agent_workbench --help` works; and
- existing direct script smoke checks still pass.

## Decision

The local package skeleton is narrow enough to proceed. P22 should add wrappers
for existing supervisor-owned commands while keeping the direct scripts
available for compatibility.
