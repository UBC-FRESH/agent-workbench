"""Immutable, redaction-first policy used to classify native P116 tool events."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


POLICY_SCHEMA_VERSION = "p116_diagnostic_policy_v1"
EVENT_SCHEMA_VERSION_V2 = "p116_supervision_event_v2"
NORMALIZER_VERSION = "p116_command_normalizer_v1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SAFE_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$")


def normalize_command(command: str) -> str:
    return " ".join(command.split())


def command_digest(command: str) -> str:
    return hashlib.sha256(normalize_command(command).encode("utf-8")).hexdigest()


def freeze_policy(value: Any) -> tuple[str, dict[str, Any]]:
    """Validate and canonically freeze a policy before Worker tool use."""
    if not isinstance(value, dict) or set(value) != {"schema_version", "normalizer_version", "allowed_tools", "checks", "edit_paths"}:
        raise ValueError("diagnostic policy has invalid shape")
    if value.get("schema_version") != POLICY_SCHEMA_VERSION or value.get("normalizer_version") != NORMALIZER_VERSION:
        raise ValueError("diagnostic policy has unsupported version")
    tools = value.get("allowed_tools")
    paths = value.get("edit_paths")
    checks = value.get("checks")
    if not isinstance(tools, list) or not tools or not all(isinstance(item, str) and _SAFE_ID.fullmatch(item) for item in tools):
        raise ValueError("diagnostic policy has invalid allowed_tools")
    if not isinstance(paths, list) or not all(_safe_path(item) for item in paths):
        raise ValueError("diagnostic policy has invalid edit_paths")
    if not isinstance(checks, list):
        raise ValueError("diagnostic policy has invalid checks")
    canonical_checks: list[dict[str, str]] = []
    check_ids: set[str] = set()
    for item in checks:
        if not isinstance(item, dict) or set(item) != {"check_id", "command_sha256"}:
            raise ValueError("diagnostic policy has invalid check")
        check_id, digest = item.get("check_id"), item.get("command_sha256")
        if not isinstance(check_id, str) or not _SAFE_ID.fullmatch(check_id) or check_id in check_ids:
            raise ValueError("diagnostic policy has invalid check_id")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise ValueError("diagnostic policy has invalid command digest")
        check_ids.add(check_id)
        canonical_checks.append({"check_id": check_id, "command_sha256": digest})
    policy = {"schema_version": POLICY_SCHEMA_VERSION, "normalizer_version": NORMALIZER_VERSION,
              "allowed_tools": sorted(set(tools)), "checks": sorted(canonical_checks, key=lambda item: item["check_id"]),
              "edit_paths": sorted(set(paths))}
    encoded = json.dumps(policy, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"policy-{hashlib.sha256(encoded).hexdigest()[:24]}", policy


def classify_call(*, policy: dict[str, Any], tool_name: str, arguments: Any) -> dict[str, Any]:
    """Return safe classification only; never return input text or paths not declared."""
    allowed = set(policy["allowed_tools"])
    if tool_name not in allowed:
        return {"operation_class": _operation(tool_name), "scope_status": "outside_ticket"}
    if tool_name == "shell_command":
        command = arguments.get("command") if isinstance(arguments, dict) else None
        if not isinstance(command, str):
            return {"operation_class": "unknown", "scope_status": "unclassified"}
        digest = command_digest(command)
        for check in policy["checks"]:
            if digest == check["command_sha256"]:
                return {"operation_class": "test", "scope_status": "within_ticket", "check_id": check["check_id"]}
        return {"operation_class": "unknown", "scope_status": "unclassified"}
    if tool_name == "apply_patch":
        patch = arguments.get("patch") if isinstance(arguments, dict) else None
        paths = _patch_paths(patch) if isinstance(patch, str) else None
        if paths is None:
            return {"operation_class": "edit", "scope_status": "unclassified"}
        return {"operation_class": "edit", "scope_status": "within_ticket" if all(path in policy["edit_paths"] for path in paths) else "outside_ticket"}
    return {"operation_class": _operation(tool_name), "scope_status": "within_ticket"}


def classify_failure(text: str, exit_code: int | None) -> str:
    lower = text.lower()
    if "syntaxerror" in lower or "parsererror" in lower:
        return "syntax_error"
    if "assertionerror" in lower or "assert " in lower:
        return "assertion_failure"
    if "no such file" in lower or "file or directory not found" in lower:
        return "missing_file"
    if "permission denied" in lower or "access is denied" in lower:
        return "permission_denied"
    if "unsupported call" in lower or "not available" in lower:
        return "tool_unavailable"
    return "nonzero_exit" if exit_code not in (None, 0) else "unknown"


def _operation(tool_name: str) -> str:
    if tool_name in {"spawn_agent", "send_input", "wait_agent", "multi_agent_v1"}:
        return "agent_manage"
    return "inspect" if tool_name in {"shell_command", "read_file"} else "unknown"


def _safe_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or Path(value).is_absolute() or ".." in Path(value).parts:
        return False
    return all(part not in {"", "."} for part in Path(value).parts)


def _patch_paths(value: str) -> list[str] | None:
    paths = re.findall(r"^\*\*\* (?:Add|Update|Delete) File: ([^\r\n]+)$", value, flags=re.MULTILINE)
    return paths if paths and all(_safe_path(path) for path in paths) else None
