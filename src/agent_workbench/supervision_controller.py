"""Local, credential-free reducer for P116 supervision events."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .supervision import SCHEMA_VERSION, SupervisionValidation, validate_cursor, validate_events


def load_events(path: Path, *, assigned_root: Path) -> list[dict[str, Any]]:
    """Load an event log only when every record satisfies the P116 contract."""
    _require_within_assigned_root(path, assigned_root=assigned_root, label="events path")
    events: list[dict[str, Any]] = []
    if not path.exists():
        return events
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"events line {line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"events line {line_number}: event must be an object")
        events.append(value)
    validation = validate_events(events, assigned_root=assigned_root)
    if not validation.ok:
        raise ValueError("invalid events: " + "; ".join(validation.errors))
    return events


def load_cursor(path: Path, *, max_sequence: int) -> int:
    """Return the last acknowledged event sequence, or zero before first review."""
    if not path.exists():
        return 0
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"cursor: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("cursor: must be an object")
    validation = validate_cursor(value, max_sequence=max_sequence)
    if not validation.ok:
        raise ValueError("invalid cursor: " + "; ".join(validation.errors))
    return int(value["last_sequence"])


def build_review_delta(events: list[dict[str, Any]], *, last_sequence: int) -> dict[str, Any]:
    """Build a compact, safe Supervisor input from unacknowledged events."""
    delta = [event for event in events if int(event["sequence"]) > last_sequence]
    safe_events = [_safe_event(event) for event in delta]
    classifications = {
        "workspace_mismatch": sum(event["kind"] == "workspace_mismatch" for event in safe_events),
        "tool_failed": sum(event["kind"] == "tool_failed" for event in safe_events),
        "terminal": sum(event["kind"] == "terminal" for event in safe_events),
    }
    end_sequence = int(delta[-1]["sequence"]) if delta else last_sequence
    return {
        "schema_version": SCHEMA_VERSION,
        "cursor_start_sequence": last_sequence,
        "cursor_end_sequence": end_sequence,
        "event_count": len(safe_events),
        "events": safe_events,
        "signals": classifications,
    }


def acknowledge_cursor(path: Path, *, last_sequence: int, assigned_root: Path) -> None:
    """Atomically persist a reviewed cursor for restart-safe idempotency."""
    if last_sequence < 0:
        raise ValueError("last_sequence must be non-negative")
    _require_within_assigned_root(path, assigned_root=assigned_root, label="cursor path")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(
            {"schema_version": SCHEMA_VERSION, "last_sequence": last_sequence},
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def prepare_review_delta(
    *, events_path: Path, cursor_path: Path, assigned_root: Path
) -> tuple[dict[str, Any], int]:
    """Read one deterministic review delta without advancing the cursor."""
    events = load_events(events_path, assigned_root=assigned_root)
    _require_within_assigned_root(cursor_path, assigned_root=assigned_root, label="cursor path")
    maximum = int(events[-1]["sequence"]) if events else 0
    last_sequence = load_cursor(cursor_path, max_sequence=maximum)
    return build_review_delta(events, last_sequence=last_sequence), maximum


def _safe_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        key: event[key]
        for key in (
            "sequence",
            "event_id",
            "timestamp",
            "kind",
            "stage",
            "outcome",
            "run_id",
            "hook_event",
            "tool_name",
            "root_match",
        )
        if key in event
    }


def _require_within_assigned_root(path: Path, *, assigned_root: Path, label: str) -> None:
    """Refuse controller reads or writes outside the declared run root."""
    resolved_root = assigned_root.resolve()
    resolved_path = path.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"{label} must stay within assigned_root") from exc
