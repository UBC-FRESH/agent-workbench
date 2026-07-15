"""Serve the P113 single-function adapter on a local loopback port.

This is intentionally not a general Responses proxy: it accepts only the
single `apply_patch(patch: string)` transaction defined in P113.1, forwards no
additional tools, and emits a fail-closed error before Codex can invoke its
native patch handler when the provider output is invalid.
"""

from __future__ import annotations

import argparse
import http.client
import json
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_workbench.p113_function_tool_adapter import AdapterError, StreamTranslator, transform_request


def write_sse(handler: BaseHTTPRequestHandler, event: dict[str, object]) -> None:
    event_name = str(event.get("type", "message"))
    handler.wfile.write(f"event: {event_name}\n".encode("utf-8"))
    handler.wfile.write(b"data: " + json.dumps(event, separators=(",", ":")).encode("utf-8") + b"\n\n")
    handler.wfile.flush()


class Handler(BaseHTTPRequestHandler):
    upstream: str
    allowed_root: str
    verdict_log: Path | None
    event_log: Path | None
    request_log: Path | None
    validated_calls: dict[str, dict[str, str]] = {}

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def verdict(self, *, status: str, code: str | None = None) -> None:
        if self.verdict_log is None:
            return
        self.verdict_log.parent.mkdir(parents=True, exist_ok=True)
        record = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "status": status}
        if code:
            record["code"] = code
        with self.verdict_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def event_shape(self, event: object) -> None:
        """Capture protocol shape only; patches and model text stay out of logs."""
        if self.event_log is None or not isinstance(event, dict):
            return
        item = event.get("item")
        record: dict[str, object] = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "type": event.get("type")}
        if isinstance(item, dict):
            record["item"] = {
                "type": item.get("type"),
                "name": item.get("name"),
                "has_id": isinstance(item.get("id"), str) and bool(item.get("id")),
                "has_call_id": isinstance(item.get("call_id"), str) and bool(item.get("call_id")),
                "arguments_type": type(item.get("arguments")).__name__,
            }
        if "item_id" in event:
            record["has_item_id"] = isinstance(event.get("item_id"), str) and bool(event.get("item_id"))
        self.event_log.parent.mkdir(parents=True, exist_ok=True)
        with self.event_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def request_shape(self, payload: object) -> None:
        """Record continuation structure without retaining patch or tool output text."""
        if self.request_log is None or not isinstance(payload, dict) or not isinstance(payload.get("input"), list):
            return
        items = payload["input"]
        record: dict[str, object] = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "item_types": [item.get("type") for item in items if isinstance(item, dict)],
            "custom_calls": [],
            "custom_outputs": [],
        }
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "custom_tool_call":
                record["custom_calls"].append({"id": item.get("id"), "call_id": item.get("call_id"), "name": item.get("name"), "input_bytes": len(item.get("input", "")) if isinstance(item.get("input"), str) else None})
            elif item.get("type") == "custom_tool_call_output":
                record["custom_outputs"].append({"call_id": item.get("call_id"), "output_bytes": len(item.get("output", "")) if isinstance(item.get("output"), str) else None})
        self.request_log.parent.mkdir(parents=True, exist_ok=True)
        with self.request_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def do_POST(self) -> None:
        if self.path not in {"/responses", "/v1/responses"}:
            self.send_error(404, "P113 adapter accepts only /responses")
            return
        try:
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            payload = json.loads(body.decode("utf-8"))
            self.request_shape(payload)
            forwarded = json.dumps(transform_request(payload, self.allowed_root, self.validated_calls), separators=(",", ":")).encode("utf-8")
        except (UnicodeDecodeError, json.JSONDecodeError, AdapterError) as exc:
            code = exc.code if isinstance(exc, AdapterError) else "malformed_request"
            self.verdict(status="rejected", code=code)
            self.send_error(400, code)
            return

        upstream = urlsplit(self.upstream)
        path = f"{upstream.path.rstrip('/')}{self.path.removeprefix('/v1')}"
        headers = {key: value for key, value in self.headers.items() if key.lower() not in {"host", "content-length", "connection"}}
        connection = http.client.HTTPSConnection(upstream.netloc, timeout=120)
        try:
            connection.request("POST", path, body=forwarded, headers=headers)
            response = connection.getresponse()
            self.send_response(response.status)
            for key, value in response.getheaders():
                if key.lower() not in {"connection", "transfer-encoding", "content-length"}:
                    self.send_header(key, value)
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            if response.status >= 400:
                self.verdict(status="provider_error", code=str(response.status))
                self.wfile.write(response.read())
                return
            self.forward_sse(response)
        finally:
            connection.close()

    def forward_sse(self, response: http.client.HTTPResponse) -> None:
        event_name, data_lines = "message", []
        translator = StreamTranslator(self.allowed_root)
        while line := response.readline():
            if line in {b"\n", b"\r\n"}:
                if data_lines:
                    self.forward_event(event_name, b"\n".join(data_lines), translator)
                event_name, data_lines = "message", []
            elif line.startswith(b"event:"):
                event_name = line.split(b":", 1)[1].strip().decode("utf-8")
            elif line.startswith(b"data:"):
                data_lines.append(line.split(b":", 1)[1].strip())

    def forward_event(self, event_name: str, raw: bytes, translator: StreamTranslator) -> None:
        if raw == b"[DONE]":
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
            return
        try:
            event = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.verdict(status="rejected", code="malformed_provider_call")
            write_sse(self, {"type": "response.error", "error": {"code": "malformed_provider_call", "message": "malformed_provider_call"}})
            return
        self.event_shape(event)
        for translated in translator.consume(event):
            if translated.get("type") == "response.output_item.done":
                item = translated.get("item")
                if isinstance(item, dict) and item.get("type") == "custom_tool_call" and isinstance(item.get("call_id"), str):
                    self.validated_calls[item["call_id"]] = {"id": str(item["id"]), "patch": str(item["input"])}
            if translated.get("type") == "response.error":
                code = str(translated["error"]["code"])
                self.verdict(status="rejected", code=code)
            write_sse(self, translated)
        if not translator.rejected:
            self.verdict(status="accepted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--upstream", required=True, help="Configured OpenAI-compatible base URL, such as https://host/v1")
    parser.add_argument("--allowed-root", required=True)
    parser.add_argument("--verdict-log", type=Path)
    parser.add_argument("--event-log", type=Path)
    parser.add_argument("--request-log", type=Path)
    args = parser.parse_args()
    Handler.upstream = args.upstream.rstrip("/")
    Handler.allowed_root = args.allowed_root.replace("\\", "/")
    Handler.verdict_log = args.verdict_log
    Handler.event_log = args.event_log
    Handler.request_log = args.request_log
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
