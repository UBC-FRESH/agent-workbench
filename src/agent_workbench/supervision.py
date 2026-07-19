"""P116 contracts for sanitized, cursor-driven Worker supervision."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence import find_private_values


SCHEMA_VERSION = "p116_supervision_v1"
EVENT_KINDS = {
    "tool_started",
    "tool_completed",
    "tool_failed",
    "stage_transition",
    "workspace_mismatch",
    "terminal",
}
OUTCOME_CLASSES = {"started", "succeeded", "failed", "denied", "terminal"}
SUPERVISOR_CLASSIFICATIONS = {
    "productive_repair",
    "material_repeat",
    "directive_deviation",
    "blocked",
    "terminal",
}
COORDINATOR_ACTIONS = {"continue", "nudge", "escalate", "terminal"}
FORBIDDEN_EVENT_KEYS = {
    "arguments",
    "command",
    "environment",
    "headers",
    "raw_output",
    "output",
    "provider_headers",
    "secret",
    "token",
}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{2,127}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
MAX_TEXT_LENGTH = 512


@dataclass(frozen=True)
class SupervisionValidation:
    ok: bool
    errors: list[str]


def validate_manifest(manifest: dict[str, Any]) -> SupervisionValidation:
    """Validate a local-only run binding before any event is accepted."""
    errors: list[str] = []
    required = (
        "schema_version",
        "run_id",
        "worker_session_id",
        "supervisor_session_id",
        "assigned_root",
        "events_path",
        "cursor_path",
        "packets_path",
        "actions_path",
    )
    _required_strings(manifest, required, errors)
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION!r}")
    for field in ("run_id", "worker_session_id", "supervisor_session_id"):
        value = manifest.get(field)
        if isinstance(value, str) and not SAFE_ID.match(value):
            errors.append(f"{field} must be a safe identifier")

    root_text = manifest.get("assigned_root")
    if isinstance(root_text, str):
        root = Path(root_text)
        if not root.is_absolute():
            errors.append("assigned_root must be absolute")

    for field in ("events_path", "cursor_path", "packets_path", "actions_path"):
        value = manifest.get(field)
        if isinstance(value, str) and not _is_relative_path(value):
            errors.append(f"{field} must be a relative path within the run directory")

    return SupervisionValidation(ok=not errors, errors=errors)


def validate_events(
    events: list[dict[str, Any]], *, assigned_root: Path
) -> SupervisionValidation:
    """Validate a strictly ordered, redacted event sequence."""
    errors: list[str] = []
    previous_sequence = 0
    for index, event in enumerate(events, 1):
        prefix = f"event {index}"
        _required_strings(
            event,
            ("schema_version", "event_id", "timestamp", "kind", "stage", "outcome"),
            errors,
            prefix=prefix,
        )
        if event.get("schema_version") != SCHEMA_VERSION:
            errors.append(f"{prefix}: invalid schema_version")
        sequence = event.get("sequence")
        if not isinstance(sequence, int) or sequence < 1:
            errors.append(f"{prefix}: sequence must be a positive integer")
        elif sequence <= previous_sequence:
            errors.append(f"{prefix}: sequence must be strictly increasing")
        else:
            previous_sequence = sequence
        for field in ("event_id", "stage"):
            value = event.get(field)
            if isinstance(value, str) and not SAFE_ID.match(value):
                errors.append(f"{prefix}: {field} must be a safe identifier")
        if event.get("kind") not in EVENT_KINDS:
            errors.append(f"{prefix}: invalid kind")
        if event.get("outcome") not in OUTCOME_CLASSES:
            errors.append(f"{prefix}: invalid outcome")
        if event.get("redaction_applied") is not True:
            errors.append(f"{prefix}: redaction_applied must be true")
        _reject_forbidden_payload(event, errors, prefix)
        _validate_observed_path(event, assigned_root, errors, prefix)
        _validate_bounded_text(event, errors, prefix)
        for finding in find_private_values(event):
            errors.append(f"{prefix}: private-looking value detected: {finding}")
    return SupervisionValidation(ok=not errors, errors=errors)


def validate_cursor(cursor: dict[str, Any], *, max_sequence: int) -> SupervisionValidation:
    errors: list[str] = []
    if cursor.get("schema_version") != SCHEMA_VERSION:
        errors.append("cursor: invalid schema_version")
    last_sequence = cursor.get("last_sequence")
    if not isinstance(last_sequence, int) or not 0 <= last_sequence <= max_sequence:
        errors.append("cursor: last_sequence must be within observed event range")
    return SupervisionValidation(ok=not errors, errors=errors)


def validate_supervisor_packet(packet: dict[str, Any]) -> SupervisionValidation:
    errors: list[str] = []
    _required_strings(
        packet,
        ("schema_version", "run_id", "classification", "recommended_action", "evidence_summary"),
        errors,
        prefix="packet",
    )
    if packet.get("schema_version") != SCHEMA_VERSION:
        errors.append("packet: invalid schema_version")
    if packet.get("classification") not in SUPERVISOR_CLASSIFICATIONS:
        errors.append("packet: invalid classification")
    if packet.get("recommended_action") not in COORDINATOR_ACTIONS:
        errors.append("packet: invalid recommended_action")
    start = packet.get("event_start_sequence")
    end = packet.get("event_end_sequence")
    if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
        errors.append("packet: invalid event cursor range")
    _reject_forbidden_payload(packet, errors, "packet")
    _validate_bounded_text(packet, errors, "packet")
    for finding in find_private_values(packet):
        errors.append(f"packet: private-looking value detected: {finding}")
    return SupervisionValidation(ok=not errors, errors=errors)


def validate_coordinator_action(action: dict[str, Any]) -> SupervisionValidation:
    errors: list[str] = []
    _required_strings(
        action,
        ("schema_version", "run_id", "packet_sha256", "decision"),
        errors,
        prefix="action",
    )
    if action.get("schema_version") != SCHEMA_VERSION:
        errors.append("action: invalid schema_version")
    if action.get("decision") not in COORDINATOR_ACTIONS:
        errors.append("action: invalid decision")
    digest = action.get("packet_sha256")
    if isinstance(digest, str) and not SHA256.match(digest):
        errors.append("action: packet_sha256 must be a lowercase SHA-256 digest")
    _reject_forbidden_payload(action, errors, "action")
    _validate_bounded_text(action, errors, "action")
    for finding in find_private_values(action):
        errors.append(f"action: private-looking value detected: {finding}")
    return SupervisionValidation(ok=not errors, errors=errors)


def _required_strings(
    value: dict[str, Any], fields: tuple[str, ...], errors: list[str], *, prefix: str = ""
) -> None:
    for field in fields:
        item = value.get(field)
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{prefix + ': ' if prefix else ''}{field} must be a non-empty string")


def _reject_forbidden_payload(value: Any, errors: list[str], prefix: str, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_EVENT_KEYS:
                errors.append(f"{prefix}: forbidden payload key: {path}.{key}")
            _reject_forbidden_payload(child, errors, prefix, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_payload(child, errors, prefix, f"{path}[{index}]")


def _validate_observed_path(event: dict[str, Any], root: Path, errors: list[str], prefix: str) -> None:
    path_text = event.get("observed_path")
    if path_text is None:
        return
    if not isinstance(path_text, str) or not path_text:
        errors.append(f"{prefix}: observed_path must be a non-empty relative path")
        return
    if not _is_relative_path(path_text):
        errors.append(f"{prefix}: observed_path must stay within assigned_root")
        return
    resolved = (root / path_text).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        errors.append(f"{prefix}: observed_path escapes assigned_root")


def _validate_bounded_text(value: Any, errors: list[str], prefix: str, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            _validate_bounded_text(child, errors, prefix, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_bounded_text(child, errors, prefix, f"{path}[{index}]")
    elif isinstance(value, str) and len(value) > MAX_TEXT_LENGTH:
        errors.append(f"{prefix}: text exceeds {MAX_TEXT_LENGTH} characters at {path}")


def _is_relative_path(value: str) -> bool:
    path = Path(value)
    return not path.is_absolute() and not re.match(r"^[A-Za-z]:", value) and ".." not in path.parts
