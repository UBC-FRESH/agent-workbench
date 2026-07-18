"""TOML validation helpers for boot-critical Codex configuration files."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from agent_workbench.agent_bridge.errors import TomlValidationError


def parse_toml_text(text: str) -> dict[str, Any]:
    """Parse a complete TOML document and raise a stable package error."""
    try:
        document = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise TomlValidationError(str(exc)) from exc
    if not isinstance(document, dict):
        raise TomlValidationError("TOML root must be a table")
    return document


def parse_toml_file(path: Path) -> dict[str, Any]:
    """Read and parse a complete TOML file."""
    return parse_toml_text(path.read_text(encoding="utf-8"))


def assert_valid_toml_text(text: str) -> None:
    """Validate TOML text without returning the parsed document."""
    parse_toml_text(text)


def assert_valid_toml_file(path: Path) -> None:
    """Validate a TOML file without returning the parsed document."""
    parse_toml_file(path)

