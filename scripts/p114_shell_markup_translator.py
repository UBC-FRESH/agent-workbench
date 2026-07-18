"""Translate one validated Qwen shell-call markup response into Responses tools."""

from __future__ import annotations

import argparse
import http.client
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


MARKUP = re.compile(
    r"^<function=(?P<name>[a-z_]+)>\s*<parameter=(?P<parameter>[a-z_]+)>\s*(?P<input>.*?)\s*</parameter>\s*</function>\s*</tool_call>\s*$",
    re.DOTALL,
)
PATCH_TOOL = {
    "type": "function",
    "name": "apply_patch",
    "parameters": {
        "type": "object",
        "properties": {"patch": {"type": "string"}},
        "required": ["patch"],
        "additionalProperties": False,
    },
    "strict": True,
}
SHELL_TOOL = {
    "type": "function",
    "name": "shell_command",
    "parameters": {
        "type": "object",
        "properties": {"command": {"type": "string"}},
        "required": ["command"],
        "additionalProperties": False,
    },
    "strict": True,
}
EXEC_TOOL = {
    "type": "function",
    "name": "exec",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {"type": "string"},
            "workdir": {"type": "string"},
        },
        "required": ["command", "workdir"],
        "additionalProperties": False,
    },
    "strict": True,
}


def sse(event: dict[str, Any]) -> bytes:
    return f"event: {event['type']}\n".encode("utf-8") + b"data: " + json.dumps(event, separators=(",", ":")).encode("utf-8") + b"\n\n"


class Handler(BaseHTTPRequestHandler):
    upstream: str
    allowed_command: str
    allowed_patch: str | None
    allowed_validation_command: str | None
    allowed_validation_workdir: str | None
    validation_kind: str
    request_log: Path | None
    response_log: Path | None
    validated_patch_ids: dict[str, str] = {}
    validated_exec_calls: dict[str, dict[str, str]] = {}
    stage = "read"

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def do_POST(self) -> None:
        if self.path not in {"/responses", "/v1/responses"}:
            self.send_error(404, "P114 translator accepts only /responses")
            return
        try:
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8"))
        except (KeyError, UnicodeDecodeError, json.JSONDecodeError):
            self.send_error(400, "malformed request")
            return
        payload.pop("reasoning", None)
        self.normalise_patch_history(payload)
        if self.allowed_patch and type(self).stage == "read" and self.has_completed_shell_call(payload):
            type(self).stage = "patch"
        if type(self).stage == "patch":
            payload["tools"] = [PATCH_TOOL]
            payload["tool_choice"] = {"type": "function", "name": "apply_patch"}
            payload["parallel_tool_calls"] = False
        elif type(self).stage == "validate":
            payload["tools"] = [SHELL_TOOL if self.validation_kind == "shell" else EXEC_TOOL]
            payload["tool_choice"] = {"type": "function", "name": "shell_command" if self.validation_kind == "shell" else "exec"}
            payload["parallel_tool_calls"] = False
        elif type(self).stage == "terminal":
            payload["tools"] = []
            payload["tool_choice"] = "none"
            payload["parallel_tool_calls"] = False
        if type(self).request_log is not None:
            with type(self).request_log.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, separators=(",", ":")) + "\n")
        upstream = urlsplit(self.upstream)
        path = f"{upstream.path.rstrip('/')}{self.path.removeprefix('/v1')}"
        headers = {key: value for key, value in self.headers.items() if key.lower() not in {"host", "content-length", "connection"}}
        connection = http.client.HTTPSConnection(upstream.netloc, timeout=120)
        try:
            connection.request("POST", path, body=json.dumps(payload, separators=(",", ":")).encode("utf-8"), headers=headers)
            response = connection.getresponse()
            body = response.read()
            if type(self).response_log is not None:
                with type(self).response_log.open("ab") as handle:
                    handle.write(body + b"\n")
            self.send_response(response.status)
            for key, value in response.getheaders():
                if key.lower() not in {"connection", "transfer-encoding", "content-length"}:
                    self.send_header(key, value)
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            if response.status >= 400:
                self.wfile.write(body)
                return
            translated = self.translate_markup(body)
            self.wfile.write(translated if translated is not None else body)
            self.wfile.flush()
        finally:
            connection.close()

    @staticmethod
    def has_completed_shell_call(payload: dict[str, Any]) -> bool:
        items = payload.get("input")
        if not isinstance(items, list):
            return False
        shell_call_ids = {
            item.get("call_id")
            for item in items
            if isinstance(item, dict)
            and item.get("type") == "function_call"
            and item.get("name") == "shell_command"
            and isinstance(item.get("call_id"), str)
        }
        return any(
            isinstance(item, dict)
            and item.get("type") == "function_call_output"
            and item.get("call_id") in shell_call_ids
            for item in items
        )

    @staticmethod
    def normalise_patch_history(payload: dict[str, Any]) -> None:
        items = payload.get("input")
        if not isinstance(items, list):
            return
        normalised: list[Any] = []
        for item in items:
            if not isinstance(item, dict) or item.get("type") not in {"custom_tool_call", "custom_tool_call_output"}:
                normalised.append(item)
                continue
            if item.get("type") == "custom_tool_call":
                call_id = item.get("call_id")
                item_id = item.get("id") or (Handler.validated_patch_ids.get(call_id) if isinstance(call_id, str) else None)
                if not isinstance(item_id, str) or not isinstance(call_id, str) or not isinstance(item.get("input"), str):
                    raise ValueError("p114_invalid_patch_history")
                if item.get("name") == "apply_patch":
                    normalised.append({"type": "function_call", "id": item_id, "call_id": call_id, "name": "apply_patch", "arguments": json.dumps({"patch": item["input"]}, separators=(",", ":"))})
                    continue
                exec_call = Handler.validated_exec_calls.get(call_id)
                if item.get("name") != "exec" or exec_call is None:
                    raise ValueError("p114_invalid_patch_history")
                normalised.append({"type": "function_call", "id": item_id, "call_id": call_id, "name": "exec", "arguments": json.dumps(exec_call, separators=(",", ":"))})
                continue
            if not isinstance(item.get("call_id"), str):
                raise ValueError("p114_invalid_patch_history")
            normalised.append({"type": "function_call_output", "call_id": item["call_id"], "output": item.get("output", "")})
        payload["input"] = normalised

    def translate_markup(self, body: bytes) -> bytes | None:
        if type(self).stage == "patch":
            translated_function = self.function_patch(body)
            if translated_function is not None:
                return translated_function
        if type(self).stage == "validate":
            translated_function = self.function_validation(body)
            if translated_function is not None:
                return translated_function
        text = self.output_text(body)
        match = MARKUP.fullmatch(text.strip())
        if match is None:
            return None
        if match.group("name") == "shell_command" and match.group("parameter") == "command" and type(self).stage == "read":
            return self.shell_call(match.group("input").strip())
        if match.group("name") == "apply_patch" and match.group("parameter") == "patch" and type(self).stage == "patch":
            return self.patch_call(match.group("input").strip())
        return sse({"type": "response.error", "error": {"code": "p114_unapproved_tool_markup", "message": "p114_unapproved_tool_markup"}}) + b"data: [DONE]\n\n"

    def shell_call(self, command: str) -> bytes:
        if command != self.allowed_command:
            return sse({"type": "response.error", "error": {"code": "p114_unapproved_shell_command", "message": "p114_unapproved_shell_command"}}) + b"data: [DONE]\n\n"
        type(self).stage = "patch" if self.allowed_patch else "complete"
        item = {"type": "function_call", "id": "p114_shell_1", "call_id": "call_p114_shell_1", "name": "shell_command", "arguments": ""}
        events = [
            {"type": "response.output_item.added", "output_index": 0, "item": item},
            {"type": "response.function_call_arguments.done", "item_id": "p114_shell_1", "arguments": json.dumps({"command": command}, separators=(",", ":"))},
            {"type": "response.output_item.done", "output_index": 0, "item": item},
        ]
        return b"".join(sse(event) for event in events) + b"data: [DONE]\n\n"

    def function_patch(self, body: bytes) -> bytes | None:
        events = self.sse_events(body)
        calls = [event.get("item") for event in events if event.get("type") == "response.output_item.added" and isinstance(event.get("item"), dict) and event["item"].get("type") == "function_call"]
        if not calls:
            return None
        if len(calls) != 1:
            return sse({"type": "response.error", "error": {"code": "p114_call_limit_exceeded", "message": "p114_call_limit_exceeded"}}) + b"data: [DONE]\n\n"
        call = calls[0]
        item_id, call_id, name = call.get("id"), call.get("call_id"), call.get("name")
        if not all(isinstance(value, str) and value for value in (item_id, call_id)) or name != "apply_patch":
            return sse({"type": "response.error", "error": {"code": "p114_unsupported_function", "message": "p114_unsupported_function"}}) + b"data: [DONE]\n\n"
        arguments = next((event.get("arguments") for event in events if event.get("type") == "response.function_call_arguments.done" and event.get("item_id") == item_id), None)
        try:
            patch = json.loads(arguments)["patch"]
        except (TypeError, KeyError, json.JSONDecodeError):
            return sse({"type": "response.error", "error": {"code": "p114_malformed_patch", "message": "p114_malformed_patch"}}) + b"data: [DONE]\n\n"
        if patch != self.allowed_patch:
            return sse({"type": "response.error", "error": {"code": "p114_unapproved_patch", "message": "p114_unapproved_patch"}}) + b"data: [DONE]\n\n"
        return self.patch_response(events, patch, item_id, call_id)

    def patch_response(self, events: list[dict[str, Any]], patch: str, item_id: str, call_id: str) -> bytes:
        type(self).stage = "validate" if self.allowed_validation_command else "complete"
        type(self).validated_patch_ids[call_id] = item_id
        custom = {"type": "custom_tool_call", "id": item_id, "call_id": call_id, "name": "apply_patch", "input": patch}
        translated: list[dict[str, Any]] = []
        for event in events:
            event_type = event.get("type")
            if event_type == "response.output_item.added" and isinstance(event.get("item"), dict) and event["item"].get("id") == item_id:
                translated.append({"type": event_type, "output_index": event.get("output_index", 0), "item": {**custom, "input": ""}})
            elif event_type == "response.function_call_arguments.delta" and event.get("item_id") == item_id:
                continue
            elif event_type == "response.function_call_arguments.done" and event.get("item_id") == item_id:
                translated.extend([
                    {"type": "response.custom_tool_call_input.delta", "item_id": item_id, "output_index": event.get("output_index", 0), "delta": patch},
                    {"type": "response.custom_tool_call_input.done", "item_id": item_id, "output_index": event.get("output_index", 0), "input": patch},
                ])
            elif event_type == "response.output_item.done" and isinstance(event.get("item"), dict) and event["item"].get("id") == item_id:
                translated.append({"type": event_type, "output_index": event.get("output_index", 0), "item": custom})
            elif event_type == "response.completed" and isinstance(event.get("response"), dict):
                completed = json.loads(json.dumps(event))
                output = completed["response"].get("output")
                if isinstance(output, list):
                    completed["response"]["output"] = [custom if isinstance(item, dict) and item.get("id") == item_id else item for item in output]
                translated.append(completed)
            else:
                translated.append(event)
        return b"".join(sse(event) for event in translated) + b"data: [DONE]\n\n"

    def patch_call(self, patch: str, *, item_id: str = "p114_patch_1", call_id: str = "call_p114_patch_1") -> bytes:
        if patch != self.allowed_patch:
            return sse({"type": "response.error", "error": {"code": "p114_unapproved_patch", "message": "p114_unapproved_patch"}}) + b"data: [DONE]\n\n"
        type(self).stage = "validate" if self.allowed_validation_command else "complete"
        item = {"type": "custom_tool_call", "id": item_id, "call_id": call_id, "name": "apply_patch", "input": patch}
        type(self).validated_patch_ids[call_id] = item_id
        events = [
            {"type": "response.output_item.added", "output_index": 0, "item": item},
            {"type": "response.custom_tool_call_input.delta", "item_id": item_id, "output_index": 0, "delta": patch},
            {"type": "response.custom_tool_call_input.done", "item_id": item_id, "output_index": 0, "input": patch},
            {"type": "response.output_item.done", "output_index": 0, "item": item},
        ]
        return b"".join(sse(event) for event in events) + b"data: [DONE]\n\n"

    def function_validation(self, body: bytes) -> bytes | None:
        events = self.sse_events(body)
        calls = [event.get("item") for event in events if event.get("type") == "response.output_item.added" and isinstance(event.get("item"), dict) and event["item"].get("type") == "function_call"]
        if not calls:
            return None
        if len(calls) != 1:
            return sse({"type": "response.error", "error": {"code": "p114_call_limit_exceeded", "message": "p114_call_limit_exceeded"}}) + b"data: [DONE]\n\n"
        call = calls[0]
        item_id, name = call.get("id"), call.get("name")
        arguments = next((event.get("arguments") for event in events if event.get("type") == "response.function_call_arguments.done" and event.get("item_id") == item_id), None)
        try:
            command = json.loads(arguments)["command"]
        except (TypeError, KeyError, json.JSONDecodeError):
            return sse({"type": "response.error", "error": {"code": "p114_malformed_validation", "message": "p114_malformed_validation"}}) + b"data: [DONE]\n\n"
        if self.validation_kind == "shell":
            if name != "shell_command" or command != self.allowed_validation_command:
                return sse({"type": "response.error", "error": {"code": "p114_unapproved_validation", "message": "p114_unapproved_validation"}}) + b"data: [DONE]\n\n"
            type(self).stage = "terminal"
            return body
        try:
            arguments_object = json.loads(arguments)
            command = arguments_object["command"]
            workdir = arguments_object["workdir"]
        except (TypeError, KeyError, json.JSONDecodeError):
            return sse({"type": "response.error", "error": {"code": "p114_malformed_validation", "message": "p114_malformed_validation"}}) + b"data: [DONE]\n\n"
        if name != "exec" or command != self.allowed_validation_command or workdir != self.allowed_validation_workdir:
            return sse({"type": "response.error", "error": {"code": "p114_unapproved_validation", "message": "p114_unapproved_validation"}}) + b"data: [DONE]\n\n"
        type(self).stage = "terminal"
        call_id = call.get("call_id")
        if not isinstance(item_id, str) or not isinstance(call_id, str):
            return sse({"type": "response.error", "error": {"code": "p114_malformed_validation", "message": "p114_malformed_validation"}}) + b"data: [DONE]\n\n"
        invocation = {"command": command, "workdir": workdir}
        input_value = "const r = await tools.shell_command(" + json.dumps(invocation, separators=(",", ":")) + "); text(r);\n"
        item = {"type": "custom_tool_call", "id": item_id, "call_id": call_id, "name": "exec", "input": input_value}
        type(self).validated_exec_calls[call_id] = invocation
        events = [
            {"type": "response.output_item.added", "output_index": 0, "item": item},
            {"type": "response.custom_tool_call_input.delta", "item_id": item_id, "output_index": 0, "delta": input_value},
            {"type": "response.custom_tool_call_input.done", "item_id": item_id, "output_index": 0, "input": input_value},
            {"type": "response.output_item.done", "output_index": 0, "item": item},
        ]
        return b"".join(sse(event) for event in events) + b"data: [DONE]\n\n"

    @staticmethod
    def output_text(body: bytes) -> str:
        deltas: list[str] = []
        completed: str | None = None
        for block in body.split(b"\n\n"):
            for line in block.splitlines():
                if not line.startswith(b"data:"):
                    continue
                try:
                    event = json.loads(line.removeprefix(b"data:").strip().decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
                if not isinstance(event, dict):
                    continue
                if event.get("type") == "response.output_text.delta" and isinstance(event.get("delta"), str):
                    deltas.append(event["delta"])
                elif event.get("type") == "response.output_text.done" and isinstance(event.get("text"), str):
                    completed = event["text"]
        return completed if completed is not None else "".join(deltas)

    @staticmethod
    def sse_events(body: bytes) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for block in body.split(b"\n\n"):
            for line in block.splitlines():
                if not line.startswith(b"data:"):
                    continue
                try:
                    event = json.loads(line.removeprefix(b"data:").strip().decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
                if isinstance(event, dict):
                    events.append(event)
        return events


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--upstream", required=True)
    parser.add_argument("--allowed-command", required=True)
    parser.add_argument("--allowed-patch")
    parser.add_argument("--allowed-validation-command")
    parser.add_argument("--allowed-validation-workdir")
    parser.add_argument("--validation-kind", choices=("exec", "shell"), default="exec")
    parser.add_argument("--request-log", type=Path)
    parser.add_argument("--response-log", type=Path)
    args = parser.parse_args()
    Handler.upstream = args.upstream.rstrip("/")
    Handler.allowed_command = args.allowed_command
    Handler.allowed_patch = args.allowed_patch
    Handler.allowed_validation_command = args.allowed_validation_command
    Handler.allowed_validation_workdir = args.allowed_validation_workdir
    Handler.validation_kind = args.validation_kind
    Handler.request_log = args.request_log
    Handler.response_log = args.response_log
    Handler.validated_patch_ids = {}
    Handler.validated_exec_calls = {}
    Handler.stage = "read"
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
