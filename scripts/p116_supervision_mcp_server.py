"""Minimal stdio JSON-RPC MCP server for one local P116 wait tool."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from agent_workbench.supervision_event_broker import SupervisionEventBroker


TOOL = {
    "name": "supervision_wait_delta",
    "description": "Wait for one meaningful sanitized P116 supervision delta.",
    "inputSchema": {"type": "object", "properties": {"timeout_ms": {"type": "integer", "minimum": 1}}, "required": ["timeout_ms"], "additionalProperties": False},
}


class P116SupervisionMcp:
    def __init__(self, manifest_path: Path, *, broker: Any | None = None) -> None:
        self.broker = broker or SupervisionEventBroker(manifest_path)

    def handle(self, request: dict[str, Any]) -> dict[str, Any] | None:
        method = request.get("method")
        request_id = request.get("id")
        if method == "notifications/initialized":
            return None
        if method == "initialize":
            return self._result(request_id, {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "p116-supervision", "version": "0.1"}})
        if method == "tools/list":
            return self._result(request_id, {"tools": [TOOL]})
        if method == "tools/call":
            return self._call(request_id, request.get("params"))
        return self._error(request_id, "METHOD_NOT_SUPPORTED")

    def _call(self, request_id: Any, params: Any) -> dict[str, Any]:
        if (
            not isinstance(params, dict)
            or not {"name", "arguments"}.issubset(params)
            or set(params) - {"name", "arguments", "_meta"}
            or params["name"] != TOOL["name"]
        ):
            return self._error(request_id, "INVALID_TOOL")
        arguments = params["arguments"]
        if not isinstance(arguments, dict) or set(arguments) != {"timeout_ms"} or not isinstance(arguments["timeout_ms"], int) or isinstance(arguments["timeout_ms"], bool) or arguments["timeout_ms"] <= 0:
            return self._error(request_id, "INVALID_ARGUMENTS")
        try:
            delta = self.broker.wait_for_trigger(timeout=arguments["timeout_ms"] / 1000)
        except TimeoutError:
            return self._error(request_id, "BROKER_TIMEOUT")
        except (ValueError, OSError):
            return self._error(request_id, "BROKER_VALIDATION")
        return self._result(request_id, {"content": [{"type": "text", "text": json.dumps(delta, sort_keys=True, separators=(",", ":"))}], "isError": False})

    @staticmethod
    def _result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    @staticmethod
    def _error(request_id: Any, code: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": code}}


def main() -> int:
    if len(sys.argv) != 2:
        return 2
    server = P116SupervisionMcp(Path(sys.argv[1]))
    for line in sys.stdin:
        if line.strip():
            response = server.handle(json.loads(line))
            if response is not None:
                sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
                sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
