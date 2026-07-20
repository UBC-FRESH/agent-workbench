"""Sanitized incremental tail of one local native Codex session."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .supervision import SCHEMA_VERSION

_EXIT = re.compile(r"\bExit\s+code:\s*(-?\d+)\b", re.IGNORECASE)


def ingest_worker_session(*, manifest: dict[str, Any], root: Path, sessions_root: Path | None = None) -> list[dict[str, Any]]:
    worker_id = manifest["worker_session_id"]
    sessions_root = sessions_root or (Path.home() / ".codex" / "sessions")
    session = _find_session(worker_id, sessions_root)
    if session is None:
        return []
    cursor_path = _cursor_path(manifest, root)
    cursor_path.parent.mkdir(parents=True, exist_ok=True)
    cursor = _read_cursor(cursor_path)
    offset = cursor.get("offset", 0) if cursor.get("path") == str(session) else 0
    data = session.read_bytes()
    complete = data[: len(data) if data.endswith(b"\n") else data.rfind(b"\n") + 1]
    records = complete[offset:]
    next_offset = offset + len(records)
    events: list[dict[str, Any]] = []
    next_sequence = _next_sequence(root / manifest["events_path"])
    for line in records.splitlines():
        try:
            record = json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(record, dict):
            continue
        tool_record = record.get("payload") if record.get("type") == "response_item" else record
        if not isinstance(tool_record, dict) or tool_record.get("type") != "custom_tool_call_output":
            continue
        text = " ".join(_strings(tool_record.get(key)) for key in ("output", "content", "result"))
        match = _EXIT.search(text)
        failed = bool(match and int(match.group(1)) != 0)
        digest = hashlib.sha256(line).hexdigest()
        if digest in cursor.get("event_ids", []):
            continue
        events.append({"schema_version": SCHEMA_VERSION, "sequence": next_sequence,
                       "event_id": f"native-{digest[:24]}",
                       "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                       "kind": "tool_failed" if failed else "tool_completed",
                       "stage": "tool", "outcome": "failed" if failed else "succeeded",
                       "redaction_applied": True, "run_id": manifest["run_id"],
                       "hook_event": "native_session", "tool_name": "native_tool", "root_match": True})
        next_sequence += 1
        cursor.setdefault("event_ids", []).append(digest)
    _write_cursor(cursor_path, {"path": str(session), "offset": next_offset, "event_ids": cursor.get("event_ids", [])[-256:]})
    return events


def initialize_session_cursor(*, manifest: dict[str, Any], root: Path, sessions_root: Path | None = None) -> Path:
    """Checkpoint the exact Worker transcript at complete-line EOF before activation."""
    sessions_root = sessions_root or (Path.home() / ".codex" / "sessions")
    session = _find_session(manifest["worker_session_id"], sessions_root)
    if session is None:
        raise ValueError("Worker session transcript is not discoverable")
    data = session.read_bytes()
    offset = len(data) if data.endswith(b"\n") else data.rfind(b"\n") + 1
    cursor_path = _cursor_path(manifest, root)
    _write_cursor(cursor_path, {"path": str(session), "offset": offset, "event_ids": []})
    return cursor_path


def _find_session(worker_id: str, sessions_root: Path) -> Path | None:
    candidates = [path for path in sessions_root.rglob("*.jsonl") if worker_id in path.name]
    return max(candidates, key=lambda path: path.stat().st_mtime_ns) if candidates else None


def _cursor_path(manifest: dict[str, Any], root: Path) -> Path:
    supervision = Path(manifest["supervision_dir"])
    return (supervision if supervision.is_absolute() else root / supervision) / "native_session_cursor.json"


def _strings(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(_strings(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_strings(item) for item in value)
    return ""


def _read_cursor(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _write_cursor(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    temporary.replace(path)


def _next_sequence(path: Path) -> int:
    if not path.exists():
        return 1
    highest = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            value = json.loads(line)
            highest = max(highest, int(value.get("sequence", 0)))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            continue
    return highest + 1
