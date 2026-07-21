"""Run-scoped P116 MCP tools for a native Coordinator already open in VS Code.

This server is intentionally inert until that Coordinator binds the Worker and
Supervisor sessions it just spawned.  It never creates sessions or sends
messages itself; those native Agent Hub operations remain owned by the live
Coordinator context.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import uuid
import hashlib
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_workbench.native_session_events import initialize_session_cursor
from agent_workbench.supervision import SCHEMA_VERSION, validate_manifest
from agent_workbench.supervision_controller import acknowledge_cursor
from agent_workbench.supervision_event_broker import SupervisionEventBroker


START = {
    "name": "supervision_start_run",
    "description": "Bind the current native Coordinator's Worker and Supervisor to one inert P116 supervision run.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "root": {"type": "string"},
            "worker_session_id": {"type": "string"},
            "supervisor_session_id": {"type": "string"},
            "run_id": {"type": "string"},
        },
        "required": ["root", "worker_session_id", "supervisor_session_id"],
        "additionalProperties": False,
    },
}
WAIT = {
    "name": "supervision_wait_delta",
    "description": "Wait for one meaningful sanitized delta from the Worker bound by supervision_start_run.",
    "inputSchema": {"type": "object", "properties": {"timeout_ms": {"type": "integer", "minimum": 1}}, "required": ["timeout_ms"], "additionalProperties": False},
}
ACKNOWLEDGE = {
    "name": "supervision_acknowledge_delta",
    "description": "Record the Coordinator's reviewed decision for the pending delta and advance its cursor.",
    "inputSchema": {"type": "object", "properties": {
        "classification": {"type": "string", "enum": ["productive_repair", "material_repeat", "directive_deviation", "blocked", "terminal"]},
        "recommended_action": {"type": "string", "enum": ["continue", "nudge", "escalate", "terminal"]},
        "decision": {"type": "string", "enum": ["continue", "nudge", "escalate", "terminal"]},
        "evidence_summary": {"type": "string", "minLength": 1, "maxLength": 512},
    }, "required": ["classification", "recommended_action", "decision", "evidence_summary"], "additionalProperties": False},
}
CLOSE = {
    "name": "supervision_close_run",
    "description": "Deactivate the current in-session P116 run after the Coordinator finishes the Worker job.",
    "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
}
TOOLS = (START, WAIT, ACKNOWLEDGE, CLOSE)


class InSessionP116Mcp:
    def __init__(
        self,
        *,
        broker_factory: Callable[[Path], Any] = SupervisionEventBroker,
        cursor_initializer: Callable[..., Path] = initialize_session_cursor,
        acknowledger: Callable[..., None] = acknowledge_cursor,
    ) -> None:
        self._broker_factory = broker_factory
        self._cursor_initializer = cursor_initializer
        self._acknowledger = acknowledger
        self.manifest_path: Path | None = None
        self.broker: Any | None = None
        self._pending_delta: dict[str, Any] | None = None

    def handle(self, request: dict[str, Any]) -> dict[str, Any] | None:
        method, request_id = request.get("method"), request.get("id")
        if method == "notifications/initialized":
            return None
        if method == "initialize":
            return _result(request_id, {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "p116-in-session", "version": "0.1"}})
        if method == "tools/list":
            return _result(request_id, {"tools": list(TOOLS)})
        if method != "tools/call":
            return _error(request_id, "METHOD_NOT_SUPPORTED")
        params = request.get("params")
        if not isinstance(params, dict) or not {"name", "arguments"}.issubset(params) or set(params) - {"name", "arguments", "_meta"}:
            return _error(request_id, "INVALID_TOOL")
        return self._call(request_id, params["name"], params["arguments"])

    def _call(self, request_id: Any, name: Any, arguments: Any) -> dict[str, Any]:
        if not isinstance(arguments, dict):
            return _error(request_id, "INVALID_ARGUMENTS")
        try:
            if name == START["name"]:
                return _result(request_id, self._start(arguments))
            if name == WAIT["name"]:
                return _result(request_id, self._wait(arguments))
            if name == ACKNOWLEDGE["name"]:
                return _result(request_id, self._acknowledge(arguments))
            if name == CLOSE["name"]:
                return _result(request_id, self._close(arguments))
        except TimeoutError:
            return _error(request_id, "BROKER_TIMEOUT")
        except (OSError, TypeError, ValueError) as exc:
            return _error(request_id, f"BROKER_VALIDATION: {exc}")
        return _error(request_id, "INVALID_TOOL")

    def _start(self, arguments: dict[str, Any]) -> dict[str, Any]:
        if set(arguments) - {"root", "worker_session_id", "supervisor_session_id", "run_id"} or not {"root", "worker_session_id", "supervisor_session_id"}.issubset(arguments):
            raise ValueError("invalid start arguments")
        if self.manifest_path is not None:
            raise ValueError("a supervision run is already active in this Coordinator session")
        root_text = arguments["root"]
        worker = arguments["worker_session_id"]
        supervisor = arguments["supervisor_session_id"]
        if not all(isinstance(value, str) and value for value in (root_text, worker, supervisor)):
            raise ValueError("start identifiers must be non-empty strings")
        root = Path(root_text).resolve()
        if not root.is_dir() or not (root / ".git").exists():
            raise ValueError("root must be the current Git workspace")
        run_id = arguments.get("run_id") or f"p116_ui_{uuid.uuid4().hex[:16]}"
        if not isinstance(run_id, str) or not run_id.replace("-", "").replace("_", "").isalnum():
            raise ValueError("run_id must be safe")
        supervision = root / "runtime" / "agent_jobs" / run_id / "supervision"
        supervision.mkdir(parents=True, exist_ok=False)
        try:
            manifest_path = supervision / "manifest.json"
            manifest = {
                "schema_version": SCHEMA_VERSION,
                "run_id": run_id,
                "worker_session_id": worker,
                "supervisor_session_id": supervisor,
                "assigned_root": str(root),
                "supervision_dir": str(supervision),
                "events_path": f"runtime/agent_jobs/{run_id}/supervision/events.jsonl",
                "cursor_path": f"runtime/agent_jobs/{run_id}/supervision/cursor.json",
                "packets_path": f"runtime/agent_jobs/{run_id}/supervision/supervisor_packets.jsonl",
                "actions_path": f"runtime/agent_jobs/{run_id}/supervision/coordinator_actions.jsonl",
            }
            validation = validate_manifest(manifest)
            if not validation.ok:
                raise ValueError("manifest is invalid")
            _write_json(manifest_path, manifest)
            self._cursor_initializer(manifest=manifest, root=root)
            _write_json(supervision / "activation.json", {"active": True, "run_id": run_id, "assigned_root": str(root), "supervision_dir": str(supervision), "worker_session_id": worker})
            broker = self._broker_factory(manifest_path)
        except Exception:
            shutil.rmtree(supervision)
            raise
        self.manifest_path = manifest_path
        self.broker = broker
        self._pending_delta = None
        return _content({"run_id": run_id, "worker_session_id": worker, "supervisor_session_id": supervisor, "status": "active"})

    def _wait(self, arguments: dict[str, Any]) -> dict[str, Any]:
        if set(arguments) != {"timeout_ms"} or not isinstance(arguments["timeout_ms"], int) or isinstance(arguments["timeout_ms"], bool) or arguments["timeout_ms"] < 1:
            raise ValueError("invalid wait arguments")
        if self.broker is None:
            raise ValueError("no active supervision run")
        if self._pending_delta is not None:
            raise ValueError("pending delta must be acknowledged before another wait")
        delta = self.broker.wait_for_trigger(timeout=arguments["timeout_ms"] / 1000)
        self._pending_delta = delta
        return _content(delta)

    def _acknowledge(self, arguments: dict[str, Any]) -> dict[str, Any]:
        if self.manifest_path is None or self._pending_delta is None:
            raise ValueError("no pending delta to acknowledge")
        if set(arguments) != {"classification", "recommended_action", "decision", "evidence_summary"}:
            raise ValueError("invalid acknowledgement arguments")
        if not all(isinstance(arguments[key], str) and arguments[key] for key in arguments):
            raise ValueError("invalid acknowledgement values")
        delta = self._pending_delta
        start, end = delta.get("cursor_start_sequence"), delta.get("cursor_end_sequence")
        if not isinstance(start, int) or not isinstance(end, int) or end < 1:
            raise ValueError("pending delta has invalid cursor range")
        packet = {"schema_version": SCHEMA_VERSION, "run_id": delta.get("run_id"),
                  "classification": arguments["classification"], "recommended_action": arguments["recommended_action"],
                  "evidence_summary": arguments["evidence_summary"], "event_start_sequence": start + 1,
                  "event_end_sequence": end}
        digest = hashlib.sha256(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        action = {"schema_version": SCHEMA_VERSION, "run_id": delta.get("run_id"), "packet_sha256": digest,
                  "decision": arguments["decision"]}
        self._acknowledger(manifest_path=self.manifest_path, last_sequence=end, packet=packet, action=action)
        self._pending_delta = None
        return _content({"run_id": packet["run_id"], "status": "acknowledged", "last_sequence": end})

    def _close(self, arguments: dict[str, Any]) -> dict[str, Any]:
        if arguments:
            raise ValueError("close takes no arguments")
        if self.manifest_path is None:
            raise ValueError("no active supervision run")
        activation = self.manifest_path.parent / "activation.json"
        if activation.exists():
            activation.unlink()
        run_id = json.loads(self.manifest_path.read_text(encoding="utf-8"))["run_id"]
        self.manifest_path = None
        self.broker = None
        self._pending_delta = None
        return _content({"run_id": run_id, "status": "closed"})


def _write_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _content(value: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(value, sort_keys=True, separators=(",", ":"))}], "isError": False}


def _result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": code}}


def main() -> int:
    server = InSessionP116Mcp()
    for line in sys.stdin:
        if line.strip():
            response = server.handle(json.loads(line))
            if response is not None:
                sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
                sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
