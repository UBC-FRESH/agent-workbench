#!/usr/bin/env python3
"""Resolve a stable secrets file location for Agent Workbench user secrets."""

from __future__ import annotations

import os
from pathlib import Path


def resolve_secrets_path(*, default_workdir: str | os.PathLike[str] | None = None) -> Path:
    """Return the secrets file that Agent Workbench should use.

    Resolution order:
    1. AGENT_WORKBENCH_SECRETS_ENV override if set.
    2. ~/.config/agent-workbench/secrets.env (home config path).
    3. <default_workdir>/.cache/secrets.env if a workdir is provided.
    """
    override = os.environ.get("AGENT_WORKBENCH_SECRETS_ENV")
    if override:
        return Path(override).expanduser().resolve()

    home_dir = Path(os.environ.get("HOME", "~")).expanduser()
    home_config = home_dir / ".config" / "agent-workbench" / "secrets.env"
    if home_config.exists():
        return home_config

    if default_workdir is None:
        return home_config

    workdir = Path(default_workdir).expanduser().resolve()
    fallback = workdir / ".cache" / "secrets.env"
    return fallback
