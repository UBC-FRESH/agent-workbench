"""Bounded MCP tool used to test Codex Worker MCP routing."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_NAME = "p114_exec"
MARKER = "P114_MCP_EXEC_HANDLER_REACHED"
PATCH_MARKER = "P114_MCP_PATCH_HANDLER_REACHED"


def patch_enabled() -> bool:
    return os.environ.get("P114_MCP_PROBE_ALLOW_PATCH") == "1"


def allowed_operations() -> list[str]:
    operations = ["inventory"]
    if patch_enabled():
        operations.append("patch")
    return operations


def patch_target() -> Path:
    path_text = os.environ.get("P114_MCP_PROBE_TARGET")
    if not path_text:
        raise ValueError("P114_MCP_PROBE_TARGET is required for operation=patch")
    return Path(path_text)


def log_event(kind: str, **fields: object) -> None:
    path_text = os.environ.get("P114_MCP_PROBE_LOG")
    if not path_text:
        return
    path = Path(path_text)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "kind": kind, **fields}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def response(request_id: object, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error(request_id: object, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    params = message.get("params", {})
    log_event("request", method=method, request_id=request_id)
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        operations = ", ".join(allowed_operations())
        return response(
            request_id,
            {
                "protocolVersion": "2025-03-26",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "p114-exec-probe", "version": "1.0.0"},
                "instructions": f"Use p114_exec only with these operations: {operations}. Patch mode is a bounded P114 routing probe.",
            },
        )
    if method == "tools/list":
        operations = allowed_operations()
        return response(
            request_id,
            {
                "tools": [
                    {
                        "name": TOOL_NAME,
                        "description": "Bounded P114 MCP routing probe.",
                        "inputSchema": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["operation"],
                            "properties": {"operation": {"type": "string", "enum": operations}},
                        },
                    }
                ]
            },
        )
    if method == "tools/call":
        if not isinstance(params, dict) or params.get("name") != TOOL_NAME or not isinstance(params.get("arguments"), dict):
            return error(request_id, -32602, "p114_exec requires a valid arguments object")
        arguments = params["arguments"]
        if arguments == {"operation": "inventory"}:
            log_event("tool_call", tool=TOOL_NAME, arguments=arguments, marker=MARKER)
            return response(request_id, {"content": [{"type": "text", "text": MARKER}], "isError": False})
        if arguments == {"operation": "patch"} and patch_enabled():
            try:
                target = patch_target()
                before = target.read_text(encoding="utf-8")
                if before != "before\n":
                    return error(request_id, -32602, "patch target did not contain exact before state")
                target.write_text("after\n", encoding="utf-8", newline="")
                after = target.read_text(encoding="utf-8")
                if after != "after\n":
                    return error(request_id, -32603, "patch target did not reach exact after state")
            except OSError as exc:
                return error(request_id, -32603, f"patch target write failed: {type(exc).__name__}: {exc}")
            log_event("tool_call", tool=TOOL_NAME, arguments=arguments, marker=PATCH_MARKER, target=str(target), before=before, after=after)
            return response(request_id, {"content": [{"type": "text", "text": PATCH_MARKER}], "isError": False})
        return error(request_id, -32602, f"p114_exec accepts only operation in {allowed_operations()}")
    return error(request_id, -32601, f"method not found: {method}")


def main() -> None:
    for line in sys.stdin:
        try:
            message = json.loads(line)
            if not isinstance(message, dict):
                raise ValueError("message must be an object")
            reply = handle(message)
        except (ValueError, json.JSONDecodeError) as exc:
            reply = error(None, -32700, str(exc))
        if reply is not None:
            print(json.dumps(reply, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    main()
