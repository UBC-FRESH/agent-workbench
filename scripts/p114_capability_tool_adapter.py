"""Serve the P114 two-tool bridge on a local loopback port.

This host translates only `apply_patch` and `exec` provider function calls into
native Codex custom tools. Codex retains patch and shell authority; this script
does not execute provider-supplied commands or mutate files itself.
"""

from __future__ import annotations

import argparse
import http.client
import json
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_workbench.p113_function_tool_adapter import AdapterError
from agent_workbench.p114_capability_tool_adapter import StreamTranslator, force_tool_choice, transform_request


def write_sse(handler: BaseHTTPRequestHandler, event: dict[str, object]) -> None:
    handler.wfile.write(f"event: {event.get('type', 'message')}\n".encode("utf-8"))
    handler.wfile.write(b"data: " + json.dumps(event, separators=(",", ":")).encode("utf-8") + b"\n\n")
    handler.wfile.flush()


class Handler(BaseHTTPRequestHandler):
    upstream: str
    allowed_root: str
    verdict_log: Path | None
    event_log: Path | None
    request_log: Path | None
    raw_request_log: Path | None
    upstream_log: Path | None
    force_initial_exec: bool
    forced_tools: list[str]
    standard_exec: bool
    patch_via_exec: bool
    host_tool_inventory: bool
    dynamic_exec_inventory: bool
    mcp_inventory_route: bool
    mcp_operation: str
    package_mcp_server: str | None
    package_mcp_read_file: bool
    strip_include: bool
    declared_exec: list[dict[str, str]]
    declared_patch: list[str] | None
    validated_calls: dict[str, dict[str, Any]] = {}

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def verdict(self, status: str, code: str | None = None) -> None:
        if self.verdict_log is None:
            return
        self.verdict_log.parent.mkdir(parents=True, exist_ok=True)
        record: dict[str, str] = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "status": status}
        if code:
            record["code"] = code
        with self.verdict_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def event_shape(self, event: object) -> None:
        if self.event_log is None or not isinstance(event, dict):
            return
        item = event.get("item")
        record: dict[str, object] = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "type": event.get("type")}
        if isinstance(item, dict):
            record["item_type"] = item.get("type")
            record["item_name"] = item.get("name")
        if event.get("type") == "response.function_call_arguments.done":
            record["item_id"] = event.get("item_id")
            record["arguments"] = event.get("arguments")
        self.event_log.parent.mkdir(parents=True, exist_ok=True)
        with self.event_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def upstream_record(self, **record: object) -> None:
        """Persist transport facts without capturing provider response bodies."""
        if self.upstream_log is None:
            return
        self.upstream_log.parent.mkdir(parents=True, exist_ok=True)
        record["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
        with self.upstream_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def do_POST(self) -> None:
        if self.path not in {"/responses", "/v1/responses"}:
            self.send_error(404, "P114 adapter accepts only /responses")
            return
        try:
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            payload = json.loads(body.decode("utf-8"))
            if self.raw_request_log is not None:
                self.raw_request_log.parent.mkdir(parents=True, exist_ok=True)
                with self.raw_request_log.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(payload, separators=(",", ":")) + "\n")
            translated = transform_request(payload, self.allowed_root, self.validated_calls, mcp_inventory=self.mcp_inventory_route, mcp_operation=self.mcp_operation, package_mcp_server=self.package_mcp_server, package_mcp_read_file=self.package_mcp_read_file)
            if self.strip_include:
                translated["include"] = []
            calls = {
                item.get("call_id"): "exec" if item.get("name") == "shell_command" else item.get("name")
                for item in payload["input"]
                if isinstance(item, dict)
                and item.get("type") in {"function_call", "custom_tool_call"}
                and isinstance(item.get("call_id"), str)
            }
            completed = {
                calls[item.get("call_id")]
                for item in payload["input"]
                if isinstance(item, dict)
                and item.get("type") in {"function_call_output", "custom_tool_call_output"}
                and item.get("call_id") in calls
            }
            forced_index = len(self.validated_calls)
            if self.forced_tools and forced_index < len(self.forced_tools):
                forced_tool = self.forced_tools[forced_index]
                translated = force_tool_choice(translated, forced_tool)
            elif self.force_initial_exec and not completed:
                translated = force_tool_choice(translated, "exec")
            elif self.force_initial_exec and "exec" in completed and "apply_patch" not in completed:
                translated = force_tool_choice(translated, "apply_patch")
            elif self.force_initial_exec and "apply_patch" in completed:
                translated = force_tool_choice(translated, "exec")
            if self.request_log is not None:
                self.request_log.parent.mkdir(parents=True, exist_ok=True)
                with self.request_log.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(translated, separators=(",", ":")) + "\n")
            forwarded = json.dumps(translated, separators=(",", ":")).encode("utf-8")
        except (UnicodeDecodeError, json.JSONDecodeError, AdapterError) as exc:
            code = exc.code if isinstance(exc, AdapterError) else "malformed_request"
            self.verdict("rejected", code)
            self.send_error(400, code)
            return
        upstream = urlsplit(self.upstream)
        path = f"{upstream.path.rstrip('/')}{self.path.removeprefix('/v1')}"
        headers = {key: value for key, value in self.headers.items() if key.lower() not in {"host", "content-length", "connection"}}
        connection_type = http.client.HTTPSConnection if upstream.scheme == "https" else http.client.HTTPConnection
        connection = connection_type(upstream.netloc, timeout=120)
        try:
            connection.request("POST", path, body=forwarded, headers=headers)
            response = connection.getresponse()
            location = response.getheader("Location")
            redirect = urlsplit(location) if location else None
            self.upstream_record(
                kind="response_headers",
                status=response.status,
                content_type=response.getheader("Content-Type"),
                content_length=response.getheader("Content-Length"),
                redirect_host=redirect.netloc if redirect else None,
                redirect_path=redirect.path if redirect else None,
            )
            self.send_response(response.status)
            for key, value in response.getheaders():
                if key.lower() not in {"connection", "transfer-encoding", "content-length"}:
                    self.send_header(key, value)
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            if response.status >= 300:
                self.verdict("provider_error", str(response.status))
                self.wfile.write(response.read())
                return
            self.forward_sse(response)
        except (OSError, http.client.HTTPException) as exc:
            self.upstream_record(kind="connection_error", error_type=type(exc).__name__, message=str(exc))
            self.verdict("provider_error", "upstream_connection_error")
            self.send_error(502, "upstream_connection_error")
        finally:
            connection.close()

    def forward_sse(self, response: http.client.HTTPResponse) -> None:
        event_name, data_lines = "message", []
        translator = StreamTranslator(self.allowed_root, standard_exec=self.standard_exec, patch_via_exec=self.patch_via_exec, host_tool_inventory=self.host_tool_inventory, dynamic_exec_inventory=self.dynamic_exec_inventory, mcp_inventory=self.mcp_inventory_route, mcp_operation=self.mcp_operation, package_mcp_server=self.package_mcp_server, package_mcp_read_file=self.package_mcp_read_file, call_validator=self.validate_declared_call)
        event_count = 0
        completed = False
        try:
            while line := response.readline():
                if line in {b"\n", b"\r\n"}:
                    if data_lines:
                        event_count += 1
                        completed = self.forward_event(event_name, b"\n".join(data_lines), translator) or completed
                    event_name, data_lines = "message", []
                elif line.startswith(b"event:"):
                    event_name = line.split(b":", 1)[1].strip().decode("utf-8")
                elif line.startswith(b"data:"):
                    data_lines.append(line.split(b":", 1)[1].strip())
        except (OSError, http.client.HTTPException) as exc:
            self.upstream_record(kind="stream_error", event_count=event_count, error_type=type(exc).__name__, message=str(exc))
            self.verdict("provider_error", "upstream_stream_error")
            write_sse(self, {"type": "response.error", "error": {"code": "upstream_stream_error", "message": "upstream_stream_error"}})
            return
        self.upstream_record(kind="stream_eof", event_count=event_count, completed=completed)
        if not completed:
            code = "upstream_empty_stream" if event_count == 0 else "upstream_incomplete_stream"
            self.verdict("provider_error", code)
            write_sse(self, {"type": "response.error", "error": {"code": code, "message": code}})

    def forward_event(self, _event_name: str, raw: bytes, translator: StreamTranslator) -> bool:
        if raw == b"[DONE]":
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
            return False
        try:
            event = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.verdict("rejected", "malformed_provider_call")
            write_sse(self, {"type": "response.error", "error": {"code": "malformed_provider_call", "message": "malformed_provider_call"}})
            return False
        self.event_shape(event)
        for translated in translator.consume(event):
            if translated.get("type") == "response.output_item.done":
                item = translated.get("item")
                if isinstance(item, dict) and isinstance(item.get("call_id"), str):
                    call = translator.accepted_calls.get(item["call_id"])
                    if call is not None:
                        self.validated_calls[item["call_id"]] = call
            if translated.get("type") == "response.error":
                self.verdict("rejected", str(translated["error"]["code"]))
            write_sse(self, translated)
        if not translator.rejected:
            self.verdict("accepted")
        return event.get("type") == "response.completed"

    def validate_declared_call(self, call: dict[str, Any]) -> str | None:
        if call.get("name") == "exec":
            expected = self.declared_exec[0] if self.declared_exec else None
            actual = call.get("provider_arguments")
            if not isinstance(actual, dict) or expected is None or actual.get("command") != expected["command"] or actual.get("workdir") != expected["workdir"] or set(actual) - {"command", "workdir", "timeout_ms"}:
                return "undeclared_exec"
            self.declared_exec.pop(0)
            return None
        if call.get("name") == "apply_patch" and self.declared_patch is not None:
            expected_patch = self.declared_patch[0] if self.declared_patch else None
            if expected_patch is None or call.get("input") != expected_patch:
                return "undeclared_patch"
            self.declared_patch.pop(0)
        if self.mcp_inventory_route and call.get("name") == "tool_search":
            prior_searches = [accepted for accepted in self.validated_calls.values() if accepted.get("name") == "tool_search"]
            if prior_searches:
                return "extra_tool_search"
        if self.mcp_inventory_route and call.get("name") == "mcp__p114_exec_probe__p114_exec":
            prior_mcp = [accepted for accepted in self.validated_calls.values() if accepted.get("name") == "mcp__p114_exec_probe__p114_exec"]
            if prior_mcp:
                return "extra_mcp_call"
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--upstream", required=True, help="OpenAI-compatible base URL; HTTP is allowed only for a local scripted provider.")
    parser.add_argument("--allowed-root", required=True)
    parser.add_argument("--verdict-log", type=Path)
    parser.add_argument("--event-log", type=Path)
    parser.add_argument("--request-log", type=Path)
    parser.add_argument("--raw-request-log", type=Path)
    parser.add_argument("--upstream-log", type=Path)
    parser.add_argument("--force-initial-exec", action="store_true")
    parser.add_argument("--forced-tool", action="append", choices=["exec", "apply_patch"], default=[])
    parser.add_argument("--standard-exec", action="store_true")
    parser.add_argument("--patch-via-exec", action="store_true")
    parser.add_argument("--host-tool-inventory", action="store_true")
    parser.add_argument("--dynamic-exec-inventory", action="store_true")
    parser.add_argument("--mcp-inventory-route", action="store_true")
    parser.add_argument("--mcp-operation", choices=["inventory", "patch"], default="inventory")
    parser.add_argument("--package-mcp-server")
    parser.add_argument("--package-mcp-read-file", action="store_true")
    parser.add_argument("--strip-include", action="store_true")
    parser.add_argument("--declared-command", action="append", default=[])
    parser.add_argument("--declared-workdir", action="append", default=[])
    parser.add_argument("--declared-patch", action="append")
    args = parser.parse_args()
    Handler.upstream = args.upstream.rstrip("/")
    Handler.allowed_root = args.allowed_root.replace("\\", "/")
    Handler.verdict_log = args.verdict_log
    Handler.event_log = args.event_log
    Handler.request_log = args.request_log
    Handler.raw_request_log = args.raw_request_log
    Handler.upstream_log = args.upstream_log
    Handler.force_initial_exec = args.force_initial_exec
    Handler.forced_tools = args.forced_tool
    Handler.standard_exec = args.standard_exec
    Handler.patch_via_exec = args.patch_via_exec
    Handler.host_tool_inventory = args.host_tool_inventory
    Handler.dynamic_exec_inventory = args.dynamic_exec_inventory
    Handler.mcp_inventory_route = args.mcp_inventory_route
    Handler.mcp_operation = args.mcp_operation
    Handler.package_mcp_server = args.package_mcp_server
    Handler.package_mcp_read_file = args.package_mcp_read_file
    Handler.strip_include = args.strip_include
    if len(args.declared_command) != len(args.declared_workdir):
        parser.error("declared command/workdir counts must match")
    Handler.declared_exec = [{"command": command, "workdir": workdir} for command, workdir in zip(args.declared_command, args.declared_workdir)]
    Handler.declared_patch = args.declared_patch
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
