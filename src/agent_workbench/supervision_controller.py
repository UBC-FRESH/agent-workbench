"""Credential-free, manifest-bound reducer for P116 supervision events."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .supervision import (
    SCHEMA_VERSION,
    validate_coordinator_action,
    validate_cursor,
    validate_events,
    validate_manifest,
    validate_supervisor_packet,
)


def load_manifest(path: Path) -> tuple[dict[str, Any], Path]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"manifest: cannot read valid JSON: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError("manifest: must be an object")
    validation = validate_manifest(manifest)
    if not validation.ok:
        raise ValueError("invalid manifest: " + "; ".join(validation.errors))
    root = Path(manifest["assigned_root"]).resolve()
    supervision_dir = Path(manifest["supervision_dir"]).resolve()
    _require_within(supervision_dir, root, "supervision_dir")
    if not path.resolve().is_relative_to(supervision_dir):
        raise ValueError("manifest: manifest file must be within supervision_dir")
    return manifest, root


def _artifact(manifest: dict[str, Any], root: Path, field: str) -> Path:
    value = manifest[field]
    path = (root / value).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"manifest {field} escapes assigned_root") from exc
    return path


def _read_events(path: Path, *, assigned_root: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise ValueError("events: truncated final record (missing newline)")
    for number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"events line {number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"events line {number}: event must be an object")
        records.append(value)
    validation = validate_events(records, assigned_root=assigned_root)
    if not validation.ok:
        raise ValueError("invalid events: " + "; ".join(validation.errors))
    return records


def _load_cursor(path: Path, maximum: int) -> int:
    if not path.exists():
        return 0
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"cursor: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("cursor: must be an object")
    validation = validate_cursor(value, max_sequence=maximum)
    if not validation.ok:
        raise ValueError("invalid cursor: " + "; ".join(validation.errors))
    return int(value["last_sequence"])


def _append(path: Path, value: dict[str, Any], root: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _require_within(path, root, "artifact path")
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def _packet_digest(packet: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def prepare_review_delta(*, manifest_path: Path) -> tuple[dict[str, Any], int]:
    manifest, root = load_manifest(manifest_path)
    events = _read_events(_artifact(manifest, root, "events_path"), assigned_root=root)
    maximum = int(events[-1]["sequence"]) if events else 0
    last = _load_cursor(_artifact(manifest, root, "cursor_path"), maximum)
    delta = [event for event in events if int(event["sequence"]) > last]
    safe = [{key: event[key] for key in ("sequence", "event_id", "timestamp", "kind", "stage", "outcome", "run_id", "hook_event", "tool_name", "root_match") if key in event} for event in delta]
    return {"schema_version": SCHEMA_VERSION, "run_id": manifest["run_id"], "cursor_start_sequence": last, "cursor_end_sequence": int(delta[-1]["sequence"]) if delta else last, "event_count": len(safe), "events": safe, "signals": {kind: sum(e["kind"] == kind for e in safe) for kind in ("workspace_mismatch", "tool_failed", "terminal")}}, maximum


def record_review(*, manifest_path: Path, packet: dict[str, Any], action: dict[str, Any]) -> None:
    manifest, root = load_manifest(manifest_path)
    for value, validator, label in ((packet, validate_supervisor_packet, "packet"), (action, validate_coordinator_action, "action")):
        result = validator(value)
        if not result.ok:
            raise ValueError(f"invalid {label}: " + "; ".join(result.errors))
    if packet["run_id"] != manifest["run_id"] or action["run_id"] != manifest["run_id"]:
        raise ValueError("review chain run_id does not match manifest")
    if action["packet_sha256"] != _packet_digest(packet):
        raise ValueError("action packet_sha256 does not match packet")
    _append(_artifact(manifest, root, "packets_path"), packet, root)
    _append(_artifact(manifest, root, "actions_path"), action, root)


def acknowledge_cursor(*, manifest_path: Path, last_sequence: int, packet: dict[str, Any], action: dict[str, Any]) -> None:
    manifest, root = load_manifest(manifest_path)
    events = _read_events(_artifact(manifest, root, "events_path"), assigned_root=root)
    maximum = max((int(event["sequence"]) for event in events), default=0)
    if last_sequence < 0:
        raise ValueError("last_sequence must be non-negative")
    if last_sequence > maximum:
        raise ValueError("last_sequence exceeds observed validated event maximum")
    if packet.get("event_end_sequence") != last_sequence:
        raise ValueError("cursor acknowledgement must cite packet event_end_sequence")
    record_review(manifest_path=manifest_path, packet=packet, action=action)
    cursor = _artifact(manifest, root, "cursor_path")
    temporary = cursor.with_suffix(cursor.suffix + ".tmp")
    temporary.write_text(json.dumps({"schema_version": SCHEMA_VERSION, "last_sequence": last_sequence}, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, cursor)


def _require_within(path: Path, root: Path, label: str) -> None:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} must stay within assigned_root") from exc
