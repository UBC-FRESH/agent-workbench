"""Sanitized incremental tail of one local native Codex session."""

from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .diagnostic_policy import EVENT_SCHEMA_VERSION_V2, classify_call, classify_failure, freeze_policy
from .supervision import SCHEMA_VERSION

_EXIT = re.compile(r"\bExit\s+code:\s*(-?\d+)\b", re.IGNORECASE)
_TOOL_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$")


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
    policy_id, policy = _load_policy(manifest, root)
    call_context = _call_context(cursor)
    next_sequence = _next_sequence(root / manifest["events_path"])
    for line in records.splitlines():
        try:
            record = json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(record, dict):
            continue
        tool_record = record.get("payload") if record.get("type") == "response_item" else record
        if isinstance(tool_record, dict) and tool_record.get("type") in {"custom_tool_call", "function_call"}:
            call_id, name = tool_record.get("call_id"), tool_record.get("name")
            if isinstance(call_id, str) and isinstance(name, str) and _TOOL_NAME.fullmatch(name):
                arguments = tool_record.get("arguments", tool_record.get("input"))
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        arguments = None
                context = {"tool_name": name}
                if policy is not None:
                    context.update(classify_call(policy=policy, tool_name=name, arguments=arguments))
                call_context[call_id] = context
            continue
        if not isinstance(tool_record, dict) or tool_record.get("type") not in {
            "custom_tool_call_output",
            "function_call_output",
        }:
            continue
        text = " ".join(_strings(tool_record.get(key)) for key in ("output", "content", "result"))
        match = _EXIT.search(text)
        exit_code = int(match.group(1)) if match else None
        failed = exit_code is not None and exit_code != 0
        digest = hashlib.sha256(line).hexdigest()
        if digest in cursor.get("event_ids", []):
            continue
        context = call_context.get(tool_record.get("call_id"), {"tool_name": "native_tool"})
        event = {"schema_version": EVENT_SCHEMA_VERSION_V2 if policy is not None else SCHEMA_VERSION, "sequence": next_sequence,
                       "event_id": f"native-{digest[:24]}",
                       "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                       "kind": "tool_failed" if failed else "tool_completed",
                       "stage": "tool", "outcome": "failed" if failed else "succeeded",
                       "redaction_applied": True, "run_id": manifest["run_id"],
                       "hook_event": "native_session", "tool_name": context["tool_name"], "root_match": True,
                       **({"exit_code": exit_code, "failure_class": classify_failure(text, exit_code)} if failed else {})}
        if policy is not None:
            event.update({"policy_id": policy_id, "operation_class": context.get("operation_class", "unknown"),
                          "scope_status": context.get("scope_status", "unclassified")})
            if isinstance(context.get("check_id"), str):
                event["check_id"] = context["check_id"]
        events.append(event)
        next_sequence += 1
        cursor.setdefault("event_ids", []).append(digest)
    _write_cursor(cursor_path, {"path": str(session), "offset": next_offset, "event_ids": cursor.get("event_ids", [])[-256:], "call_context": dict(list(call_context.items())[-256:])})
    return events


def initialize_session_cursor(
    *,
    manifest: dict[str, Any],
    root: Path,
    sessions_root: Path | None = None,
    discovery_timeout_seconds: float = 5.0,
    discovery_poll_seconds: float = 0.05,
) -> Path:
    """Checkpoint the exact Worker transcript at complete-line EOF before activation."""
    sessions_root = sessions_root or (Path.home() / ".codex" / "sessions")
    session = _find_session(manifest["worker_session_id"], sessions_root)
    deadline = time.monotonic() + discovery_timeout_seconds
    while session is None and time.monotonic() < deadline:
        time.sleep(min(discovery_poll_seconds, max(0.0, deadline - time.monotonic())))
        session = _find_session(manifest["worker_session_id"], sessions_root)
    if session is None:
        raise ValueError("Worker session transcript is not discoverable before activation")
    data = session.read_bytes()
    offset = len(data) if data.endswith(b"\n") else data.rfind(b"\n") + 1
    cursor_path = _cursor_path(manifest, root)
    _write_cursor(cursor_path, {"path": str(session), "offset": offset, "event_ids": [], "call_context": {}})
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


def _call_context(cursor: dict[str, Any]) -> dict[str, dict[str, str]]:
    value = cursor.get("call_context", {})
    if not isinstance(value, dict):
        return {}
    return {
        call_id: {key: item for key, item in context.items() if key in {"tool_name", "operation_class", "scope_status", "check_id"} and isinstance(item, str)}
        for call_id, context in value.items()
        if isinstance(call_id, str) and isinstance(context, dict) and isinstance(context.get("tool_name"), str) and _TOOL_NAME.fullmatch(context["tool_name"])
    }


def _load_policy(manifest: dict[str, Any], root: Path) -> tuple[str | None, dict[str, Any] | None]:
    path_text = manifest.get("diagnostic_policy_path")
    if path_text is None:
        return None, None
    if not isinstance(path_text, str):
        raise ValueError("diagnostic policy path is invalid")
    path = (root / path_text).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("diagnostic policy escapes root")
    policy_id, policy = freeze_policy(json.loads(path.read_text(encoding="utf-8")))
    if manifest.get("diagnostic_policy_id") != policy_id:
        raise ValueError("diagnostic policy binding mismatch")
    return policy_id, policy


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
