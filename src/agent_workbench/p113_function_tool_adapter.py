"""Fail-closed P113 adapter between one Responses function and Codex apply_patch.

This module deliberately has no provider configuration, shell fallback, or file
mutation.  A small HTTP host may use these pure transformations to relay an
already-authorized request to a provider.  Codex remains the patch authority.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any


FUNCTION_TOOL = {
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
PATCH_PATH = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", re.MULTILINE)


class AdapterError(ValueError):
    """A stable, public-safe rejection from the constrained adapter."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def patch_paths(patch: str) -> list[str]:
    return PATCH_PATH.findall(patch)


def _contained(path: str, allowed_root: str) -> bool:
    if not path or "\x00" in path or path.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", path):
        return False
    candidate, root = PurePosixPath(path), PurePosixPath(allowed_root)
    if ".." in candidate.parts:
        return False
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def validate_patch(patch: object, allowed_root: str) -> str:
    if not isinstance(patch, str) or not patch:
        raise AdapterError("malformed_provider_call")
    if not patch.startswith("*** Begin Patch\n") or not patch.rstrip().endswith("*** End Patch"):
        raise AdapterError("malformed_provider_call")
    paths = patch_paths(patch)
    if not paths:
        raise AdapterError("malformed_provider_call")
    if any(not _contained(path, allowed_root) for path in paths):
        raise AdapterError("path_outside_allowed_root")
    return patch


def parse_provider_call(call: object, allowed_root: str) -> dict[str, str]:
    if not isinstance(call, dict):
        raise AdapterError("malformed_provider_call")
    item_id, call_id, name = call.get("id"), call.get("call_id"), call.get("name")
    if not all(isinstance(value, str) and value for value in (item_id, call_id)) or name != "apply_patch":
        raise AdapterError("malformed_provider_call")
    try:
        arguments = json.loads(call.get("arguments"))
    except (TypeError, json.JSONDecodeError) as exc:
        raise AdapterError("malformed_provider_call") from exc
    if not isinstance(arguments, dict) or set(arguments) != {"patch"}:
        raise AdapterError("malformed_provider_call")
    return {"id": item_id, "call_id": call_id, "name": name, "patch": validate_patch(arguments["patch"], allowed_root)}


def custom_call(call: dict[str, str]) -> dict[str, str]:
    return {"type": "custom_tool_call", "id": call["id"], "call_id": call["call_id"], "name": "apply_patch", "input": call["patch"]}


def transform_request(payload: object, allowed_root: str, validated_calls: dict[str, dict[str, str]] | None = None) -> dict[str, Any]:
    """Return the only provider request shape permitted by P113.

    Initial requests force one function. Follow-up history may replay prior
    apply_patch calls, but every replayed patch and output correlation is
    revalidated before tools are disabled.
    """
    if not isinstance(payload, dict) or not isinstance(payload.get("input"), list):
        raise AdapterError("malformed_request")
    items = payload["input"]
    if any(isinstance(item, dict) and item.get("type") == "additional_tools" for item in items):
        raise AdapterError("unsupported_tool_or_event")
    custom_calls = [item for item in items if isinstance(item, dict) and item.get("type") == "custom_tool_call"]
    outputs = [item for item in items if isinstance(item, dict) and item.get("type") == "custom_tool_call_output"]
    translated = dict(payload)
    translated.pop("reasoning", None)
    translated["parallel_tool_calls"] = False
    if not custom_calls and not outputs:
        translated["tools"] = [FUNCTION_TOOL]
        translated["tool_choice"] = {"type": "function", "name": "apply_patch"}
        return translated
    validated_calls = validated_calls or {}
    replayed_call_ids: set[str] = set()
    replayed_item_ids: dict[int, str] = {}
    for call in custom_calls:
        if call.get("name") != "apply_patch" or not isinstance(call.get("call_id"), str) or not isinstance(call.get("input"), str):
            raise AdapterError("history_round_trip_invalid")
        validate_patch(call["input"], allowed_root)
        replayed_call_ids.add(call["call_id"])
        item_id = call.get("id")
        if not isinstance(item_id, str) or not item_id:
            cached = validated_calls.get(call["call_id"])
            item_id = cached.get("id") if isinstance(cached, dict) else None
        if not isinstance(item_id, str) or not item_id:
            raise AdapterError("history_round_trip_invalid")
        replayed_item_ids[id(call)] = item_id
    known_call_ids = replayed_call_ids | set(validated_calls)
    for output in outputs:
        if not isinstance(output.get("call_id"), str) or output["call_id"] not in known_call_ids:
            raise AdapterError("history_round_trip_invalid")
    translated_items: list[Any] = []
    for item in items:
        if isinstance(item, dict) and item.get("type") == "custom_tool_call":
            translated_items.append({"type": "function_call", "id": replayed_item_ids[id(item)], "call_id": item["call_id"], "name": "apply_patch", "arguments": json.dumps({"patch": item["input"]}, separators=(",", ":"))})
        elif isinstance(item, dict) and item.get("type") == "custom_tool_call_output":
            translated_items.append({"type": "function_call_output", "call_id": item["call_id"], "output": item.get("output", "")})
        elif isinstance(item, dict) and item.get("type") in {"custom_tool_call", "custom_tool_call_output"}:
            raise AdapterError("history_round_trip_invalid")
        else:
            translated_items.append(item)
    translated["input"] = translated_items
    translated["tools"] = []
    translated["tool_choice"] = "none"
    return translated


@dataclass
class StreamTranslator:
    """Translate one complete provider function call after validating it."""

    allowed_root: str
    seen_calls: int = 0
    pending: dict[str, dict[str, Any]] = field(default_factory=dict)
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
            self.seen_calls += 1
            if self.seen_calls > 1 or item.get("name") != "apply_patch":
                return self._reject("call_limit_exceeded" if self.seen_calls > 1 else "unsupported_tool_or_event")
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id:
                return self._reject("malformed_provider_call")
            call_id = item.get("call_id")
            if not isinstance(call_id, str) or not call_id:
                return self._reject("malformed_provider_call")
            custom = {"type": "custom_tool_call", "id": item_id, "call_id": call_id, "name": "apply_patch", "input": ""}
            self.pending[item_id] = {"item": item, "output_index": event.get("output_index", 0), "deltas": "", "custom": custom}
            return [{"type": "response.output_item.added", "output_index": event.get("output_index", 0), "item": custom}]
        if event_type == "response.function_call_arguments.delta":
            entry = self.pending.get(event.get("item_id"))
            if entry is None or not isinstance(event.get("delta"), str):
                return self._reject("malformed_provider_call")
            entry["deltas"] += event["delta"]
            return []
        if event_type == "response.function_call_arguments.done":
            item_id = event.get("item_id")
            entry = self.pending.get(item_id)
            if entry is None:
                return self._reject("malformed_provider_call")
            item = dict(entry["item"])
            item["arguments"] = event.get("arguments") or entry["deltas"]
            try:
                call = parse_provider_call(item, self.allowed_root)
            except AdapterError as exc:
                return self._reject(exc.code)
            custom = entry["custom"]
            custom["input"] = call["patch"]
            return [
                {"type": "response.custom_tool_call_input.delta", "item_id": call["id"], "output_index": entry["output_index"], "delta": call["patch"]},
                {"type": "response.custom_tool_call_input.done", "item_id": call["id"], "output_index": entry["output_index"], "input": call["patch"]},
            ]
        if event_type == "response.output_item.done":
            item = event.get("item")
            if isinstance(item, dict) and item.get("type") == "function_call":
                entry = self.pending.get(item.get("id"))
                if entry is None or "custom" not in entry:
                    return self._reject("malformed_provider_call")
                return [{"type": "response.output_item.done", "output_index": event.get("output_index", entry["output_index"]), "item": entry["custom"]}]
        return [event]

    def _reject(self, code: str) -> list[dict[str, Any]]:
        self.rejected = True
        return [{"type": "response.error", "error": {"code": code, "message": code}}]
