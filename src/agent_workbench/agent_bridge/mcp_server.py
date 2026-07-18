"""Grant-bound MCP server primitives for Agent Workbench bridge tools."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TextIO

from agent_workbench.agent_bridge.errors import AgentBridgeError
from agent_workbench.agent_bridge.patch_backend import apply_patch_subset, patch_paths as backend_patch_paths

EXEC_TOOL_NAME = "exec"
APPLY_PATCH_TOOL_NAME = "apply_patch"
READ_FILE_TOOL_NAME = "read_file"


class BridgePolicyError(AgentBridgeError):
    """Raised when a tool call is outside the active run grant."""


@dataclass(frozen=True)
class RunGrant:
    """Minimal deny-by-default authority grant for one MCP bridge run."""

    run_id: str
    root: Path
    allowed_exec_commands: frozenset[str] = frozenset()
    allowed_patch_sha256: frozenset[str] = frozenset()
    allowed_patch_paths: frozenset[str] = frozenset()
    allowed_read_paths: frozenset[str] = frozenset()
    max_read_bytes: int = 131072

    def normalized_root(self) -> Path:
        return self.root.resolve()


@dataclass
class ToolOutcome:
    """Normalized tool-handler outcome."""

    text: str
    is_error: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


ExecHandler = Callable[[str, Path, int], ToolOutcome]
ApplyPatchHandler = Callable[[str, Path], ToolOutcome]


def sha256_text(text: str) -> str:
    """Return a stable SHA-256 digest for UTF-8 text."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _relative_grant_path(path_text: str) -> str | None:
    candidate = Path(path_text)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    normalized = candidate.as_posix()
    return normalized if normalized not in {"", "."} else None


def _patch_paths(patch: str) -> list[str]:
    try:
        return list(backend_patch_paths(patch))
    except AgentBridgeError:
        return []


def exec_tool_schema() -> dict[str, Any]:
    """Return the child-facing MCP schema for bounded command execution."""

    return {
        "name": EXEC_TOOL_NAME,
        "description": "Run one command only when it exactly matches the active Agent Workbench run grant.",
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["command"],
            "properties": {
                "command": {"type": "string"},
                "workdir": {"type": "string"},
                "timeout_ms": {"type": "integer", "minimum": 1, "maximum": 120000},
            },
        },
    }


def apply_patch_tool_schema() -> dict[str, Any]:
    """Return the child-facing MCP schema for bounded patch application."""

    return {
        "name": APPLY_PATCH_TOOL_NAME,
        "description": "Apply one patch only when its SHA-256 matches the active Agent Workbench run grant.",
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["patch"],
            "properties": {"patch": {"type": "string"}},
        },
    }


def read_file_tool_schema() -> dict[str, Any]:
    """Return the child-facing schema for a bounded UTF-8 file read."""

    return {
        "name": READ_FILE_TOOL_NAME,
        "description": "Read one UTF-8 file only when its relative path is explicitly granted for this run.",
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["path"],
            "properties": {
                "path": {"type": "string"},
                "start_line": {"type": "integer", "minimum": 1},
                "end_line": {"type": "integer", "minimum": 1},
            },
        },
    }


def _jsonrpc_response(request_id: object, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _jsonrpc_error(request_id: object, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _mcp_text_result(text: str, *, is_error: bool = False) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


def _default_exec_handler(command: str, workdir: Path, timeout_ms: int) -> ToolOutcome:
    completed = subprocess.run(
        command,
        cwd=workdir,
        shell=True,
        check=False,
        text=True,
        capture_output=True,
        timeout=timeout_ms / 1000,
    )
    text = json.dumps(
        {
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        },
        sort_keys=True,
    )
    return ToolOutcome(text=text, is_error=completed.returncode != 0, metadata={"exit_code": completed.returncode})


def _default_apply_patch_handler(patch: str, root: Path) -> ToolOutcome:
    result = apply_patch_subset(patch, root)
    return ToolOutcome(text="PATCH_OK", metadata={"changed_files": [str(path) for path in result.changed_files]})


class AgentBridgeMcpServer:
    """Small JSON-RPC MCP handler for grant-bound bridge tools.

    This class is intentionally transport-agnostic. Stdio/server wiring can feed
    each parsed JSON-RPC object to :meth:`handle` and serialize the reply.
    """

    def __init__(
        self,
        grant: RunGrant,
        *,
        event_log_path: Path | None = None,
        exec_handler: ExecHandler | None = None,
        apply_patch_handler: ApplyPatchHandler | None = None,
    ) -> None:
        self.grant = grant
        self.event_log_path = event_log_path
        self.exec_handler = exec_handler or _default_exec_handler
        self.apply_patch_handler = apply_patch_handler or _default_apply_patch_handler

    def handle(self, message: dict[str, Any]) -> dict[str, Any] | None:
        method = message.get("method")
        request_id = message.get("id")
        params = message.get("params", {})
        self._log("request", method=method, request_id=request_id)
        if method == "notifications/initialized":
            return None
        if method == "initialize":
            return _jsonrpc_response(
                request_id,
                {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "agent-workbench-bridge", "version": "0.1.0"},
                    "instructions": "Use bridge tools only as explicitly granted for this run.",
                },
            )
        if method == "tools/list":
            tools = [exec_tool_schema(), apply_patch_tool_schema()]
            if self.grant.allowed_read_paths:
                tools.append(read_file_tool_schema())
            return _jsonrpc_response(request_id, {"tools": tools})
        if method == "tools/call":
            return self._handle_tool_call(request_id, params)
        return _jsonrpc_error(request_id, -32601, f"method not found: {method}")

    def _handle_tool_call(self, request_id: object, params: object) -> dict[str, Any]:
        if not isinstance(params, dict) or not isinstance(params.get("arguments"), dict):
            return _jsonrpc_error(request_id, -32602, "tools/call requires an arguments object")
        name = params.get("name")
        arguments = params["arguments"]
        if name == EXEC_TOOL_NAME:
            return self._handle_exec(request_id, arguments)
        if name == APPLY_PATCH_TOOL_NAME:
            return self._handle_apply_patch(request_id, arguments)
        if name == READ_FILE_TOOL_NAME:
            return self._handle_read_file(request_id, arguments)
        return _jsonrpc_error(request_id, -32602, f"unsupported bridge tool: {name}")

    def _handle_exec(self, request_id: object, arguments: dict[str, Any]) -> dict[str, Any]:
        command = arguments.get("command")
        workdir_text = arguments.get("workdir")
        timeout_ms = arguments.get("timeout_ms", 120000)
        if not isinstance(command, str) or not command:
            return _jsonrpc_error(request_id, -32602, "exec requires a non-empty command")
        if not isinstance(timeout_ms, int) or timeout_ms < 1 or timeout_ms > 120000:
            return _jsonrpc_error(request_id, -32602, "exec timeout_ms must be 1..120000")
        try:
            workdir = self._resolve_workdir(workdir_text)
        except BridgePolicyError as exc:
            return self._deny(request_id, EXEC_TOOL_NAME, str(exc), {"command": command})
        if command not in self.grant.allowed_exec_commands:
            return self._deny(request_id, EXEC_TOOL_NAME, "command_not_granted", {"command": command})
        self._log("policy_decision", tool=EXEC_TOOL_NAME, decision="allow", command=command, workdir=str(workdir))
        try:
            outcome = self.exec_handler(command, workdir, timeout_ms)
        except Exception as exc:  # pragma: no cover - defensive handler boundary
            self._log("tool_outcome", tool=EXEC_TOOL_NAME, status="handler_exception", error=f"{type(exc).__name__}: {exc}")
            return _jsonrpc_response(request_id, _mcp_text_result(f"exec handler failed: {type(exc).__name__}: {exc}", is_error=True))
        self._log("tool_outcome", tool=EXEC_TOOL_NAME, status="completed", command=command, is_error=outcome.is_error, **outcome.metadata)
        return _jsonrpc_response(request_id, _mcp_text_result(outcome.text, is_error=outcome.is_error))

    def _handle_apply_patch(self, request_id: object, arguments: dict[str, Any]) -> dict[str, Any]:
        patch = arguments.get("patch")
        if not isinstance(patch, str) or not patch:
            return _jsonrpc_error(request_id, -32602, "apply_patch requires a non-empty patch")
        patch_hash = sha256_text(patch)
        patch_paths = _patch_paths(patch)
        allowed_by_hash = patch_hash in self.grant.allowed_patch_sha256
        allowed_by_path = bool(patch_paths) and set(patch_paths).issubset(self.grant.allowed_patch_paths)
        if not allowed_by_hash and not allowed_by_path:
            return self._deny(request_id, APPLY_PATCH_TOOL_NAME, "patch_not_granted", {"patch_sha256": patch_hash})
        root = self.grant.normalized_root()
        self._log("policy_decision", tool=APPLY_PATCH_TOOL_NAME, decision="allow", patch_sha256=patch_hash, patch_paths=patch_paths, root=str(root))
        try:
            outcome = self.apply_patch_handler(patch, root)
        except Exception as exc:  # pragma: no cover - defensive handler boundary
            self._log("tool_outcome", tool=APPLY_PATCH_TOOL_NAME, status="handler_exception", error=f"{type(exc).__name__}: {exc}", patch_sha256=patch_hash)
            return _jsonrpc_response(request_id, _mcp_text_result(f"apply_patch handler failed: {type(exc).__name__}: {exc}", is_error=True))
        self._log("tool_outcome", tool=APPLY_PATCH_TOOL_NAME, status="completed", is_error=outcome.is_error, patch_sha256=patch_hash, **outcome.metadata)
        return _jsonrpc_response(request_id, _mcp_text_result(outcome.text, is_error=outcome.is_error))

    def _handle_read_file(self, request_id: object, arguments: dict[str, Any]) -> dict[str, Any]:
        path_text = arguments.get("path")
        if not isinstance(path_text, str) or not path_text:
            return _jsonrpc_error(request_id, -32602, "read_file requires a non-empty path")
        start_line = arguments.get("start_line")
        end_line = arguments.get("end_line")
        if start_line is not None and (not isinstance(start_line, int) or isinstance(start_line, bool) or start_line < 1):
            return _jsonrpc_error(request_id, -32602, "read_file start_line must be a positive integer")
        if end_line is not None and (not isinstance(end_line, int) or isinstance(end_line, bool) or end_line < 1):
            return _jsonrpc_error(request_id, -32602, "read_file end_line must be a positive integer")
        if start_line is not None and end_line is not None and end_line < start_line:
            return _jsonrpc_error(request_id, -32602, "read_file end_line must not precede start_line")
        normalized = _relative_grant_path(path_text)
        if normalized is None or normalized not in self.grant.allowed_read_paths:
            return self._deny(request_id, READ_FILE_TOOL_NAME, "path_not_granted", {"path": path_text})
        root = self.grant.normalized_root()
        path = (root / normalized).resolve()
        if root not in path.parents:
            return self._deny(request_id, READ_FILE_TOOL_NAME, "read_target_unavailable", {"path": normalized})
        if not path.is_file():
            # A declared creation target may legitimately be absent at the
            # pinned baseline. That is a read result, not an authority denial.
            self._log("policy_decision", tool=READ_FILE_TOOL_NAME, decision="allow", path=normalized, exists=False)
            self._log("tool_outcome", tool=READ_FILE_TOOL_NAME, status="not_found", is_error=False, path=normalized)
            return _jsonrpc_response(request_id, _mcp_text_result(f"FILE_ABSENT:{normalized}"))
        if path.stat().st_size > self.grant.max_read_bytes:
            return self._deny(request_id, READ_FILE_TOOL_NAME, "read_limit_exceeded", {"path": normalized})
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return self._deny(request_id, READ_FILE_TOOL_NAME, "read_not_utf8", {"path": normalized})
        if start_line is not None or end_line is not None:
            lines = text.splitlines(keepends=True)
            first = (start_line or 1) - 1
            last = end_line or len(lines)
            text = "".join(lines[first:last])
        size = len(text.encode("utf-8"))
        range_fields = {"start_line": start_line, "end_line": end_line} if start_line is not None or end_line is not None else {}
        self._log("policy_decision", tool=READ_FILE_TOOL_NAME, decision="allow", path=normalized, bytes=size, **range_fields)
        self._log("tool_outcome", tool=READ_FILE_TOOL_NAME, status="completed", is_error=False, bytes=size, **range_fields)
        return _jsonrpc_response(request_id, _mcp_text_result(text))

    def _resolve_workdir(self, workdir_text: object) -> Path:
        root = self.grant.normalized_root()
        if workdir_text is None:
            return root
        if not isinstance(workdir_text, str):
            raise BridgePolicyError("workdir_not_string")
        workdir = Path(workdir_text)
        if not workdir.is_absolute():
            workdir = root / workdir
        resolved = workdir.resolve()
        if resolved != root and root not in resolved.parents:
            raise BridgePolicyError("workdir_outside_root")
        return resolved

    def _deny(self, request_id: object, tool: str, reason: str, fields: dict[str, Any]) -> dict[str, Any]:
        self._log("policy_decision", tool=tool, decision="deny", reason=reason, **fields)
        return _jsonrpc_response(request_id, _mcp_text_result(f"policy_denied:{reason}", is_error=True))

    def _log(self, kind: str, **fields: Any) -> None:
        if self.event_log_path is None:
            return
        self.event_log_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "kind": kind,
            "run_id": self.grant.run_id,
            **fields,
        }
        with self.event_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def handle_json_line(server: AgentBridgeMcpServer, line: str) -> dict[str, Any] | None:
    """Parse and handle one JSON-RPC line."""

    try:
        message = json.loads(line)
        if not isinstance(message, dict):
            raise ValueError("message must be an object")
    except (ValueError, json.JSONDecodeError) as exc:
        return _jsonrpc_error(None, -32700, str(exc))
    return server.handle(message)


def serve_jsonl(server: AgentBridgeMcpServer, input_stream: TextIO, output_stream: TextIO) -> None:
    """Serve newline-delimited JSON-RPC messages over text streams."""

    for line in input_stream:
        reply = handle_json_line(server, line)
        if reply is not None:
            output_stream.write(json.dumps(reply, separators=(",", ":")) + "\n")
            output_stream.flush()


def build_arg_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Run the Agent Workbench bridge MCP server over stdin/stdout JSON-RPC.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--event-log")
    parser.add_argument("--allow-exec-command", action="append", default=[])
    parser.add_argument("--allow-patch-sha256", action="append", default=[])
    parser.add_argument("--allow-patch-path", action="append", default=[])
    parser.add_argument("--allow-read-path", action="append", default=[])
    parser.add_argument("--max-read-bytes", type=int, default=131072)
    return parser


def server_from_args(args: Namespace) -> AgentBridgeMcpServer:
    return AgentBridgeMcpServer(
        RunGrant(
            run_id=args.run_id,
            root=Path(args.root),
            allowed_exec_commands=frozenset(args.allow_exec_command),
            allowed_patch_sha256=frozenset(args.allow_patch_sha256),
            allowed_patch_paths=frozenset(args.allow_patch_path),
            allowed_read_paths=frozenset(args.allow_read_path),
            max_read_bytes=args.max_read_bytes,
        ),
        event_log_path=Path(args.event_log) if args.event_log else None,
    )


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    serve_jsonl(server_from_args(args), sys.stdin, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
