"""Sanitize Codex lifecycle-hook payloads into P116 supervision events."""

from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .supervision import SCHEMA_VERSION, validate_events


RUN_ID_ENV = "P116_RUN_ID"
ASSIGNED_ROOT_ENV = "P116_ASSIGNED_ROOT"
SUPERVISION_DIR_ENV = "P116_SUPERVISION_DIR"
ACTIVATION_FILENAME = "activation.json"


def _activation_manifest(project_root: Path) -> dict[str, str] | None:
    """Load the one Coordinator-staged activation manifest for this root."""
    candidates = sorted(
        (project_root / "runtime" / "agent_jobs").glob(f"*/supervision/{ACTIVATION_FILENAME}")
    )
    if len(candidates) != 1:
        return None
    manifest_path = candidates[0]
    try:
        value = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(value, dict) or manifest_path.parent.parent.name == "":
            return None
        run_id = value.get("run_id")
        assigned_root = value.get("assigned_root")
        supervision_dir = value.get("supervision_dir")
        if not all(isinstance(item, str) and item for item in (run_id, assigned_root, supervision_dir)):
            return None
        root = project_root.resolve()
        assigned = Path(assigned_root).resolve()
        output = Path(supervision_dir).resolve()
        run_dir = manifest_path.parent.parent.resolve()
        if assigned != root or not _within(output, root) or not _within(output, run_dir):
            return None
        return {"run_id": run_id, "assigned_root": str(assigned), "supervision_dir": str(output)}
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return None


def event_from_hook_payload(
    payload: dict[str, Any],
    *,
    run_id: str,
    assigned_root: Path,
    sequence: int,
) -> dict[str, Any]:
    """Return a bounded event without retaining hook tool input or response."""
    hook_event = str(payload.get("hook_event_name", ""))
    tool_name = _safe_tool_name(payload.get("tool_name"))
    cwd_matches_root = _same_path(payload.get("cwd"), assigned_root)
    kind, outcome = _event_type(hook_event, cwd_matches_root)
    return {
        "schema_version": SCHEMA_VERSION,
        "sequence": sequence,
        "event_id": f"hook-{uuid.uuid4().hex}",
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "kind": kind,
        "stage": "tool",
        "outcome": outcome,
        "redaction_applied": True,
        "run_id": run_id,
        "hook_event": hook_event,
        "tool_name": tool_name,
        "root_match": cwd_matches_root,
    }


def capture_from_environment(payload: dict[str, Any]) -> bool:
    """Append one event from explicit environment or staged root-local activation."""
    run_id = os.environ.get(RUN_ID_ENV)
    assigned_root_text = os.environ.get(ASSIGNED_ROOT_ENV)
    supervision_dir_text = os.environ.get(SUPERVISION_DIR_ENV)
    if not (run_id and assigned_root_text and supervision_dir_text):
        activation = _activation_manifest(Path.cwd())
        if activation is None:
            return False
        run_id = activation["run_id"]
        assigned_root_text = activation["assigned_root"]
        supervision_dir_text = activation["supervision_dir"]

    assigned_root = Path(assigned_root_text).resolve()
    events_path = Path(supervision_dir_text) / "events.jsonl"
    if not _within(events_path.parent, assigned_root):
        return False
    try:
        events_path.parent.mkdir(parents=True, exist_ok=True)
        sequence = _next_sequence(events_path)
        event = event_from_hook_payload(
            payload,
            run_id=run_id,
            assigned_root=assigned_root,
            sequence=sequence,
        )
        validation = validate_events([event], assigned_root=assigned_root)
        if not validation.ok:
            _append_error_event(events_path, assigned_root, sequence, run_id, "invalid_event")
            return True
        with events_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
    except (OSError, TypeError, ValueError):
        try:
            _append_error_event(
                events_path,
                assigned_root,
                _next_sequence(events_path),
                run_id,
                "capture_failure",
            )
        except (OSError, ValueError):
            return False
    return True


def _event_type(hook_event: str, cwd_matches_root: bool) -> tuple[str, str]:
    if not cwd_matches_root:
        return "workspace_mismatch", "failed"
    if hook_event == "PreToolUse":
        return "tool_started", "started"
    if hook_event == "PostToolUse":
        return "tool_completed", "succeeded"
    return "stage_transition", "started"


def _next_sequence(events_path: Path) -> int:
    if not events_path.exists():
        return 1
    highest = 0
    for line in events_path.read_text(encoding="utf-8").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        sequence = value.get("sequence") if isinstance(value, dict) else None
        if isinstance(sequence, int):
            highest = max(highest, sequence)
    return highest + 1


def _safe_tool_name(value: object) -> str:
    if not isinstance(value, str) or not value:
        return "unknown"
    safe = "".join(char for char in value if char.isalnum() or char in "_.:-")
    return safe[:128] or "unknown"


def _same_path(value: object, assigned_root: Path) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        return Path(value).resolve() == assigned_root.resolve()
    except OSError:
        return False


def _within(path: Path, assigned_root: Path) -> bool:
    try:
        path.resolve().relative_to(assigned_root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _append_error_event(
    events_path: Path,
    assigned_root: Path,
    sequence: int,
    run_id: str,
    code: str,
) -> None:
    event = {
        "schema_version": SCHEMA_VERSION,
        "sequence": sequence,
        "event_id": f"hook-{uuid.uuid4().hex}",
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "kind": "tool_failed",
        "stage": "hook",
        "outcome": "failed",
        "redaction_applied": True,
        "run_id": run_id,
        "hook_event": "hook_error",
        "tool_name": "hook",
        "root_match": True,
        "error_code": code[:32],
    }
    validation = validate_events([event], assigned_root=assigned_root)
    if not validation.ok:
        return
    with events_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
