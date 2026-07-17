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
from agent_workbench.p114_capability_tool_adapter import StreamTranslator, transform_request


def write_sse(handler: BaseHTTPRequestHandler, event: dict[str, object]) -> None:
    handler.wfile.write(f"event: {event.get('type', 'message')}\n".encode("utf-8"))
    handler.wfile.write(b"data: " + json.dumps(event, separators=(",", ":")).encode("utf-8") + b"\n\n")
    handler.wfile.flush()


class Handler(BaseHTTPRequestHandler):
    upstream: str
    allowed_root: str
    verdict_log: Path | None
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

    def do_POST(self) -> None:
        if self.path not in {"/responses", "/v1/responses"}:
            self.send_error(404, "P114 adapter accepts only /responses")
            return
        try:
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            payload = json.loads(body.decode("utf-8"))
            forwarded = json.dumps(transform_request(payload, self.allowed_root, self.validated_calls), separators=(",", ":")).encode("utf-8")
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
            self.send_response(response.status)
            for key, value in response.getheaders():
                if key.lower() not in {"connection", "transfer-encoding", "content-length"}:
                    self.send_header(key, value)
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            if response.status >= 400:
                self.verdict("provider_error", str(response.status))
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

    def forward_event(self, _event_name: str, raw: bytes, translator: StreamTranslator) -> None:
        if raw == b"[DONE]":
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
            return
        try:
            event = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.verdict("rejected", "malformed_provider_call")
            write_sse(self, {"type": "response.error", "error": {"code": "malformed_provider_call", "message": "malformed_provider_call"}})
            return
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--upstream", required=True, help="OpenAI-compatible base URL; HTTP is allowed only for a local scripted provider.")
    parser.add_argument("--allowed-root", required=True)
    parser.add_argument("--verdict-log", type=Path)
    args = parser.parse_args()
    Handler.upstream = args.upstream.rstrip("/")
    Handler.allowed_root = args.allowed_root.replace("\\", "/")
    Handler.verdict_log = args.verdict_log
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
