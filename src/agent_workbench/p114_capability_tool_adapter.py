"""Fail-closed multi-tool translation for the P114 C4 capability contract.

The adapter never executes commands or edits files.  It translates an
OpenAI-compatible provider's function calls into the native Codex custom tool
events that retain authority over shell execution and patch application.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any

from agent_workbench.p113_function_tool_adapter import AdapterError, patch_paths


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
EXEC_TOOL = {
    "type": "function",
    "name": "exec",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {"type": "string"},
            "workdir": {"type": "string"},
            "timeout_ms": {"type": "integer", "minimum": 1, "maximum": 120000},
        },
        "required": ["command"],
        "additionalProperties": False,
    },
    "strict": True,
}
TOOLS = [PATCH_TOOL, EXEC_TOOL]


def _normalise_path(value: str) -> str:
    return value.replace("\\", "/").rstrip("/")


def _contained(value: str, root: str) -> bool:
    value, root = _normalise_path(value), _normalise_path(root)
    if not value or not root or "\x00" in value or "\x00" in root:
        return False
    candidate, parent = PurePosixPath(value), PurePosixPath(root)
    if ".." in candidate.parts:
        return False
    candidate_absolute = value.startswith("/") or bool(re.match(r"^[A-Za-z]:/", value))
    parent_absolute = root.startswith("/") or bool(re.match(r"^[A-Za-z]:/", root))
    if candidate_absolute != parent_absolute:
        return False
    try:
        candidate.relative_to(parent)
    except ValueError:
        return False
    return True


def _validate_patch(patch: object, allowed_root: str) -> str:
    if not isinstance(patch, str) or not patch or not patch.startswith("*** Begin Patch\n") or not patch.rstrip().endswith("*** End Patch"):
        raise AdapterError("malformed_provider_call")
    paths = patch_paths(patch)
    if not paths:
        raise AdapterError("malformed_provider_call")
    if any(not _contained(path, allowed_root) for path in paths):
        raise AdapterError("path_outside_allowed_root")
    return patch


def _parse_arguments(call: object) -> tuple[str, str, str, dict[str, Any]]:
    if not isinstance(call, dict):
        raise AdapterError("malformed_provider_call")
    item_id, call_id, name = call.get("id"), call.get("call_id"), call.get("name")
    if not all(isinstance(value, str) and value for value in (item_id, call_id)) or name not in {"apply_patch", "exec"}:
        raise AdapterError("unsupported_tool_or_event")
    try:
        arguments = json.loads(call.get("arguments"))
    except (TypeError, json.JSONDecodeError) as exc:
        raise AdapterError("malformed_provider_call") from exc
    if not isinstance(arguments, dict):
        raise AdapterError("malformed_provider_call")
    return item_id, call_id, name, arguments


def _patch_from_arguments(arguments: dict[str, Any], allowed_root: str) -> str:
    if set(arguments) == {"patch"}:
        return _validate_patch(arguments["patch"], allowed_root)
    # Some OpenAI-compatible coding models emit the native freeform envelope
    # inside a generic command argument despite receiving the strict schema.
    if set(arguments) == {"command"} and isinstance(arguments["command"], str):
        command = arguments["command"]
        if command.startswith("apply_patch\n"):
            return _validate_patch(command.removeprefix("apply_patch\n"), allowed_root)
    raise AdapterError("malformed_provider_call")


def _exec_input(arguments: dict[str, Any], worktree_root: str) -> str:
    if set(arguments) - {"command", "workdir", "timeout_ms"} or not isinstance(arguments.get("command"), str) or not arguments["command"].strip():
        raise AdapterError("malformed_provider_call")
    workdir = arguments.get("workdir", worktree_root)
    if not isinstance(workdir, str) or not _contained(workdir, worktree_root):
        raise AdapterError("path_outside_allowed_root")
    timeout = arguments.get("timeout_ms", 10000)
    if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 120000:
        raise AdapterError("malformed_provider_call")
    invocation = {"command": arguments["command"], "workdir": workdir, "timeout_ms": timeout}
    return "const r = await tools.shell_command(" + json.dumps(invocation, separators=(",", ":")) + "); text(r);\n"


def parse_provider_call(call: object, allowed_root: str) -> dict[str, Any]:
    """Validate one provider function call and produce native custom input."""
    item_id, call_id, name, arguments = _parse_arguments(call)
    if name == "apply_patch":
        return {"id": item_id, "call_id": call_id, "name": name, "input": _patch_from_arguments(arguments, allowed_root), "provider_arguments": arguments}
    return {"id": item_id, "call_id": call_id, "name": name, "input": _exec_input(arguments, allowed_root), "provider_arguments": arguments}


def transform_request(payload: object, allowed_root: str, validated_calls: dict[str, dict[str, str]] | None = None) -> dict[str, Any]:
    """Translate initial and continuation requests without reducing tool scope."""
    if not isinstance(payload, dict) or not isinstance(payload.get("input"), list):
        raise AdapterError("malformed_request")
    items = payload["input"]
    if any(isinstance(item, dict) and item.get("type") == "additional_tools" for item in items):
        raise AdapterError("unsupported_tool_or_event")
    translated = dict(payload)
    translated.pop("reasoning", None)
    translated["parallel_tool_calls"] = False
    translated["tools"] = TOOLS
    translated["tool_choice"] = "auto"
    validated_calls = validated_calls or {}
    translated_items: list[Any] = []
    for item in items:
        if not isinstance(item, dict) or item.get("type") not in {"custom_tool_call", "custom_tool_call_output"}:
            translated_items.append(item)
            continue
        if item["type"] == "custom_tool_call":
            name, call_id, input_value = item.get("name"), item.get("call_id"), item.get("input")
            if name not in {"apply_patch", "exec"} or not isinstance(call_id, str) or not isinstance(input_value, str):
                raise AdapterError("history_round_trip_invalid")
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id:
                cached = validated_calls.get(call_id)
                item_id = cached.get("id") if isinstance(cached, dict) else None
            if not isinstance(item_id, str) or not item_id:
                raise AdapterError("history_round_trip_invalid")
            cached = validated_calls.get(call_id)
            if name == "apply_patch":
                _validate_patch(input_value, allowed_root)
                arguments: dict[str, Any] = {"patch": input_value}
            else:
                arguments = cached.get("provider_arguments") if isinstance(cached, dict) else None
                if not isinstance(arguments, dict) or not isinstance(arguments.get("command"), str):
                    raise AdapterError("history_round_trip_invalid")
            translated_items.append({"type": "function_call", "id": item_id, "call_id": call_id, "name": name, "arguments": json.dumps(arguments, separators=(",", ":"))})
        else:
            call_id = item.get("call_id")
            if not isinstance(call_id, str) or call_id not in validated_calls:
                raise AdapterError("history_round_trip_invalid")
            translated_items.append({"type": "function_call_output", "call_id": call_id, "output": item.get("output", "")})
    translated["input"] = translated_items
    return translated


@dataclass
class StreamTranslator:
    """Translate sequential provider calls and preserve their native identity."""

    allowed_root: str
    pending: dict[str, dict[str, Any]] = field(default_factory=dict)
    accepted_calls: dict[str, dict[str, Any]] = field(default_factory=dict)
    rejected: bool = False

    def consume(self, event: object) -> list[dict[str, Any]]:
        if self.rejected:
            return []
        if not isinstance(event, dict):
            return self._reject("unsupported_tool_or_event")
        event_type = event.get("type")
        if event_type == "response.output_item.added":
            item = event.get("item")
            if not isinstance(item, dict) or item.get("type") != "function_call":
                return [event]
            if item.get("name") not in {"apply_patch", "exec"} or not isinstance(item.get("id"), str) or not isinstance(item.get("call_id"), str):
                return self._reject("unsupported_tool_or_event")
            custom = {"type": "custom_tool_call", "id": item["id"], "call_id": item["call_id"], "name": item["name"], "input": ""}
            self.pending[item["id"]] = {"item": item, "output_index": event.get("output_index", 0), "deltas": "", "custom": custom}
            return [{"type": "response.output_item.added", "output_index": event.get("output_index", 0), "item": custom}]
        if event_type == "response.function_call_arguments.delta":
            entry = self.pending.get(event.get("item_id"))
            if entry is None or not isinstance(event.get("delta"), str):
                return self._reject("malformed_provider_call")
            entry["deltas"] += event["delta"]
            return []
        if event_type == "response.function_call_arguments.done":
            entry = self.pending.get(event.get("item_id"))
            if entry is None:
                return self._reject("malformed_provider_call")
            item = dict(entry["item"])
            item["arguments"] = event.get("arguments") or entry["deltas"]
            try:
                call = parse_provider_call(item, self.allowed_root)
            except AdapterError as exc:
                return self._reject(exc.code)
            entry["custom"]["input"] = call["input"]
            self.accepted_calls[call["call_id"]] = call
            return [
                {"type": "response.custom_tool_call_input.delta", "item_id": call["id"], "output_index": entry["output_index"], "delta": call["input"]},
                {"type": "response.custom_tool_call_input.done", "item_id": call["id"], "output_index": entry["output_index"], "input": call["input"]},
            ]
        if event_type == "response.output_item.done":
            item = event.get("item")
            if isinstance(item, dict) and item.get("type") == "function_call":
                entry = self.pending.get(item.get("id"))
                if entry is None:
                    return self._reject("malformed_provider_call")
                return [{"type": "response.output_item.done", "output_index": event.get("output_index", entry["output_index"]), "item": entry["custom"]}]
        return [event]

    def _reject(self, code: str) -> list[dict[str, Any]]:
        self.rejected = True
        return [{"type": "response.error", "error": {"code": code, "message": code}}]
