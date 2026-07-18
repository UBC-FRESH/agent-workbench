"""Local scripted Responses provider for the non-live P114.3 host proof."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


class Handler(BaseHTTPRequestHandler):
    worktree: str
    request_log: Path
    request_count = 0

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def do_POST(self) -> None:
        if self.path not in {"/responses", "/v1/responses"}:
            self.send_error(404, "P114 scripted provider accepts only /responses")
            return
        try:
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8"))
        except (KeyError, UnicodeDecodeError, json.JSONDecodeError):
            self.send_error(400, "malformed request")
            return
        type(self).request_count += 1
        self.record_shape(payload)
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        events = self.tool_events() if type(self).request_count == 1 else self.final_events()
        for event in events:
            self.wfile.write(f"event: {event['type']}\n".encode("utf-8"))
            self.wfile.write(b"data: " + json.dumps(event, separators=(",", ":")).encode("utf-8") + b"\n\n")
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()

    def record_shape(self, payload: dict[str, Any]) -> None:
        tools = payload.get("tools")
        items = payload.get("input")
        record = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "request_number": type(self).request_count,
            "model": payload.get("model"),
            "tool_names": [item.get("name") for item in tools if isinstance(item, dict)] if isinstance(tools, list) else [],
            "tool_choice": payload.get("tool_choice"),
            "input_types": [item.get("type") for item in items if isinstance(item, dict)] if isinstance(items, list) else [],
        }
        self.request_log.parent.mkdir(parents=True, exist_ok=True)
        with self.request_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def tool_events(self) -> list[dict[str, Any]]:
        path = f"{self.worktree}/p114_host_proof.txt"
        patch = f"*** Begin Patch\n*** Update File: {path}\n@@\n-before\n+after\n*** End Patch"
        return [
            {"type": "response.output_item.added", "output_index": 0, "item": {"type": "function_call", "id": "patch_1", "call_id": "call_patch_1", "name": "apply_patch"}},
            {"type": "response.function_call_arguments.done", "item_id": "patch_1", "arguments": json.dumps({"patch": patch})},
            {"type": "response.output_item.done", "output_index": 0, "item": {"type": "function_call", "id": "patch_1"}},
        ]

    @staticmethod
    def final_events() -> list[dict[str, Any]]:
        return [
            {"type": "response.output_item.added", "output_index": 0, "item": {"id": "msg_final", "type": "message", "role": "assistant", "content": []}},
            {"type": "response.output_text.delta", "item_id": "msg_final", "output_index": 0, "delta": "P114_HOST_DONE"},
            {"type": "response.output_text.done", "item_id": "msg_final", "output_index": 0, "text": "P114_HOST_DONE"},
            {"type": "response.output_item.done", "output_index": 0, "item": {"id": "msg_final", "type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "P114_HOST_DONE"}]}},
            {"type": "response.completed", "response": {"id": "resp_final", "status": "completed", "output": []}},
        ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--worktree", required=True)
    parser.add_argument("--request-log", type=Path, required=True)
    args = parser.parse_args()
    Handler.worktree = args.worktree.replace("\\", "/")
    Handler.request_log = args.request_log
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
