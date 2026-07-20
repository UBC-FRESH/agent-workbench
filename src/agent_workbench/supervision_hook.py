"""Sanitize Codex lifecycle-hook payloads into P116 supervision events."""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .supervision import SCHEMA_VERSION, validate_events


RUN_ID_ENV = "P116_RUN_ID"
ASSIGNED_ROOT_ENV = "P116_ASSIGNED_ROOT"
SUPERVISION_DIR_ENV = "P116_SUPERVISION_DIR"
ACTIVATION_FILENAME = "activation.json"
RECEIPT_FILENAME = "invocation_receipt.json"
RECEIPT_STATUSES = {"invoked", "payload_rejected", "event_dropped", "event_written"}


def _activation_manifest(project_root: Path) -> dict[str, str] | None:
    """Load the one explicitly active Coordinator manifest for this root."""
    manifest, _ = _staged_activation(project_root)
    return manifest


def _staged_activation(project_root: Path) -> tuple[dict[str, str] | None, bool]:
    """Return the active manifest and whether any active marker was staged."""
    candidates = sorted(
        (project_root / "runtime" / "agent_jobs").glob(f"*/supervision/{ACTIVATION_FILENAME}")
    )
    active_manifests: list[tuple[Path, dict[str, object]]] = []
    for manifest_path in candidates:
        try:
            value = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError):
            continue
        if isinstance(value, dict) and value.get("active") is True:
            active_manifests.append((manifest_path, value))
    if len(active_manifests) != 1:
        return None, bool(candidates)
    manifest_path, value = active_manifests[0]
    try:
        if manifest_path.parent.parent.name == "":
            return None, True
        run_id = value.get("run_id")
        assigned_root = value.get("assigned_root")
        supervision_dir = value.get("supervision_dir")
        worker_session_id = value.get("worker_session_id")
        if not all(isinstance(item, str) and item for item in (run_id, assigned_root, supervision_dir)):
            return None, True
        if value.get("active") is not True or not isinstance(worker_session_id, str) or not worker_session_id:
            return None, True
        root = project_root.resolve()
        assigned = Path(assigned_root).resolve()
        output = Path(supervision_dir).resolve()
        run_dir = manifest_path.parent.parent.resolve()
        if assigned != root or not _within(output, root) or not _within(output, run_dir):
            return None, True
        return {"run_id": run_id, "assigned_root": str(assigned), "supervision_dir": str(output), "worker_session_id": worker_session_id}, True
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return None, True


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
    kind, outcome = _event_type(hook_event, cwd_matches_root, payload)
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
    context = _capture_context()
    if context is None:
        return False
    run_id, assigned_root, supervision_dir, worker_session_id = context
    if worker_session_id is not None and payload.get("session_id") != worker_session_id:
        return False

    events_path = supervision_dir / "events.jsonl"
    if not _within(events_path.parent, assigned_root):
        return False
    try:
        events_path.parent.mkdir(parents=True, exist_ok=True)
        _write_receipt(supervision_dir, "invoked")
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
            _write_receipt(supervision_dir, "payload_rejected")
            return True
        existing = _read_events(events_path)
        if not validate_events(existing, assigned_root=assigned_root).ok:
            _write_receipt(supervision_dir, "payload_rejected")
            return True
        combined_validation = validate_events([*existing, event], assigned_root=assigned_root)
        if not combined_validation.ok:
            _write_receipt(supervision_dir, "event_dropped")
            return True
        with events_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
        _write_receipt(supervision_dir, "event_written")
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


def record_hook_invocation() -> bool:
    """Record that the hook command started, without inspecting its payload."""
    context = _capture_context()
    if context is None:
        return False
    _, assigned_root, supervision_dir, _ = context
    if not _within(supervision_dir, assigned_root):
        return False
    try:
        supervision_dir.mkdir(parents=True, exist_ok=True)
        _write_receipt(supervision_dir, "invoked")
        return True
    except OSError:
        return False


def record_hook_payload_rejected() -> bool:
    """Record unusable hook input using only a categorical status."""
    context = _capture_context()
    if context is None:
        return False
    _, assigned_root, supervision_dir, _ = context
    if not _within(supervision_dir, assigned_root):
        return False
    try:
        supervision_dir.mkdir(parents=True, exist_ok=True)
        _write_receipt(supervision_dir, "payload_rejected")
        return True
    except OSError:
        return False


def _capture_context() -> tuple[str, Path, Path, str | None] | None:
    activation, active_staged = _staged_activation(Path.cwd())
    if activation is not None:
        return activation["run_id"], Path(activation["assigned_root"]), Path(activation["supervision_dir"]), activation["worker_session_id"]
    if active_staged:
        return None
    run_id = os.environ.get(RUN_ID_ENV)
    assigned_text = os.environ.get(ASSIGNED_ROOT_ENV)
    supervision_text = os.environ.get(SUPERVISION_DIR_ENV)
    if not (run_id and assigned_text and supervision_text):
        if activation is None:
            return None
        run_id, assigned_text, supervision_text = (
            activation["run_id"], activation["assigned_root"], activation["supervision_dir"]
        )
    try:
        assigned_root = Path(assigned_text).resolve()
        supervision_dir = Path(supervision_text).resolve()
    except (TypeError, OSError, ValueError):
        return None
    if not _within(supervision_dir, assigned_root):
        return None
    return run_id, assigned_root, supervision_dir, None


def _write_receipt(supervision_dir: Path, status: str) -> None:
    if status not in RECEIPT_STATUSES:
        raise ValueError("invalid receipt status")
    receipt = {"receipt_version": 1, "status": status}
    receipt_path = supervision_dir / RECEIPT_FILENAME
    receipt_path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")


def _event_type(hook_event: str, cwd_matches_root: bool, tool_response: object = None) -> tuple[str, str]:
    if not cwd_matches_root:
        return "workspace_mismatch", "failed"
    if hook_event == "PreToolUse":
        return "tool_started", "started"
    if hook_event == "PostToolUse" and _tool_response_failed(tool_response):
        return "tool_failed", "failed"
    if hook_event == "PostToolUse":
        return "tool_completed", "succeeded"
    return "stage_transition", "started"


def _tool_response_failed(value: object) -> bool:
    return _scan_failure(value)


def _failure_signal(value: object) -> bool:
    if isinstance(value, int) and not isinstance(value, bool):
        return value != 0
    if isinstance(value, str):
        if value.lower() in {"failed", "error", "denied"}:
            return True
        match = re.search(r"\bExit\s+code:\s*(-?\d+)\b", value, re.IGNORECASE)
        return bool(match and int(match.group(1)) != 0)
    if isinstance(value, dict):
        exit_code = value.get("exit_code")
        if isinstance(exit_code, int) and not isinstance(exit_code, bool) and exit_code != 0:
            return True
        if value.get("is_error") is True:
            return True
        if isinstance(value.get("status"), str) and value["status"].lower() in {"failed", "error", "denied"}:
            return True
        return any(_failure_signal(value.get(key)) for key in ("tool_response", "tool_result", "result", "content", "text", "output"))
    if isinstance(value, list):
        return any(_failure_signal(item) for item in value)
    return False


_FAILURE_SCAN_EXCLUDED_KEYS = {"input", "command", "arguments", "environment", "header", "headers", "secret", "secrets", "token", "tokens", "tool_input", "tool_arguments", "request", "params", "payload"}


def _scan_failure(value: object, key: str | None = None) -> bool:
    if key is not None and key.lower() in _FAILURE_SCAN_EXCLUDED_KEYS:
        return False
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            normalized = str(child_key).lower()
            if normalized in _FAILURE_SCAN_EXCLUDED_KEYS:
                continue
            if normalized == "exit_code" and isinstance(child_value, int) and not isinstance(child_value, bool) and child_value != 0:
                return True
            if normalized == "is_error" and child_value is True:
                return True
            if normalized == "status" and isinstance(child_value, str) and child_value.lower() in {"failed", "error", "denied"}:
                return True
            if _scan_failure(child_value, normalized):
                return True
        return False
    if isinstance(value, list):
        return any(_scan_failure(item, key) for item in value)
    if isinstance(value, str):
        match = re.fullmatch(r".*\bExit\s+code:\s*(-?\d+)\b.*", value, re.IGNORECASE)
        return bool(match and int(match.group(1)) != 0)
    return False


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


def _read_events(events_path: Path) -> list[dict[str, Any]]:
    if not events_path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in events_path.read_text(encoding="utf-8").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    return events


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
