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
from typing import Any, Callable

from agent_workbench.agent_bridge.tools import (
    EXEC_TOOL,
    MCP_PROBE_COMPATIBILITY_TOOL_NAME,
    PATCH_TOOL,
    TOOL_SEARCH_TOOL,
    TOOLS,
    package_mcp_compatibility_tool,
    package_mcp_namespace,
    mcp_compatibility_tool,
)
from agent_workbench.agent_bridge.protocol import tool_search_output_has_namespace
from agent_workbench.agent_bridge.patch_backend import PatchBackendError, patch_paths as package_patch_paths
from agent_workbench.p113_function_tool_adapter import AdapterError, patch_paths


MCP_INVENTORY_TOOL_NAME = MCP_PROBE_COMPATIBILITY_TOOL_NAME


def mcp_exec_probe_tool(operation: str = "inventory") -> dict[str, Any]:
    return mcp_compatibility_tool(operation)


MCP_INVENTORY_TOOL = mcp_exec_probe_tool("inventory")


def _package_mcp_tool_name(server_name: str, tool_name: str) -> str:
    return package_mcp_compatibility_tool(server_name, tool_name)["name"]


def _package_mcp_tool_names(include_read_file: bool = False) -> tuple[str, ...]:
    return ("exec", "apply_patch", "read_file") if include_read_file else ("exec", "apply_patch")


def _package_mcp_tools(server_name: str, include_read_file: bool = False) -> list[dict[str, Any]]:
    return [package_mcp_compatibility_tool(server_name, name) for name in _package_mcp_tool_names(include_read_file)]


def _parse_package_mcp_call(call: object, allowed_root: str, server_name: str, include_read_file: bool = False) -> dict[str, Any]:
    namespace = package_mcp_namespace(server_name)
    names = {_package_mcp_tool_name(server_name, tool) for tool in _package_mcp_tool_names(include_read_file)}
    item_id, call_id, name, arguments = _parse_arguments(call, {"tool_search", *names})
    if name == "tool_search":
        query = arguments.get("query")
        required_terms = {server_name, *_package_mcp_tool_names(include_read_file)}
        qualification_ticket_query = "runtime/agent_jobs/p107_suite_provenance_audit_bundle_ticket.md"
        qualification_ticket_search = include_read_file and query == qualification_ticket_query
        if not isinstance(query, str) or (required_terms.issubset(set(query.split())) is False and not qualification_ticket_search):
            raise AdapterError("malformed_provider_call")
        if set(arguments) - {"query", "limit"}:
            raise AdapterError("malformed_provider_call")
    elif name == _package_mcp_tool_name(server_name, "exec"):
        _exec_input(arguments, allowed_root)
    elif include_read_file and name == _package_mcp_tool_name(server_name, "read_file"):
        if set(arguments) - {"path", "start_line", "end_line"} or not isinstance(arguments.get("path"), str):
            raise AdapterError("malformed_provider_call")
        start_line = arguments.get("start_line")
        end_line = arguments.get("end_line")
        if start_line is not None and (not isinstance(start_line, int) or isinstance(start_line, bool) or start_line < 1):
            raise AdapterError("malformed_provider_call")
        if end_line is not None and (not isinstance(end_line, int) or isinstance(end_line, bool) or end_line < 1):
            raise AdapterError("malformed_provider_call")
        if start_line is not None and end_line is not None and end_line < start_line:
            raise AdapterError("malformed_provider_call")
    else:
        _package_patch_from_arguments(arguments)
    native_tool = name.removeprefix(f"{namespace}__") if name != "tool_search" else None
    native_search_arguments = (
        {"query": f"{server_name} {' '.join(_package_mcp_tool_names(include_read_file))}"}
        if name == "tool_search" and qualification_ticket_search
        else arguments
    )
    return {
        "id": item_id,
        "call_id": call_id,
        "name": name,
        "provider_arguments": arguments,
        "native_search_arguments": native_search_arguments,
        "native_tool": native_tool,
    }


def _package_patch_from_arguments(arguments: dict[str, Any]) -> str:
    """Validate the package backend's deliberately relative patch contract."""
    if set(arguments) != {"patch"} or not isinstance(arguments["patch"], str):
        raise AdapterError("malformed_provider_call")
    patch = arguments["patch"]
    try:
        paths = package_patch_paths(patch)
    except PatchBackendError as exc:
        if str(exc) == "path_outside_root":
            raise AdapterError("path_outside_allowed_root") from exc
        raise AdapterError("malformed_provider_call") from exc
    if not paths:
        raise AdapterError("malformed_provider_call")
    if any(PurePosixPath(path).is_absolute() or ".." in PurePosixPath(path).parts for path in paths):
        raise AdapterError("path_outside_allowed_root")
    return patch


def force_tool_choice(payload: dict[str, Any], name: str) -> dict[str, Any]:
    """Force one next call while retaining the complete C4 tool catalog."""
    if name not in {"apply_patch", "exec"}:
        raise ValueError(f"unsupported forced tool: {name}")
    translated = dict(payload)
    translated["tools"] = TOOLS
    translated["tool_choice"] = {"type": "function", "name": name}
    return translated


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


def _parse_arguments(call: object, allowed_names: set[str] | None = None) -> tuple[str, str, str, dict[str, Any]]:
    if not isinstance(call, dict):
        raise AdapterError("malformed_provider_call")
    item_id, call_id, name = call.get("id"), call.get("call_id"), call.get("name")
    allowed_names = allowed_names or {"apply_patch", "exec"}
    if not all(isinstance(value, str) and value for value in (item_id, call_id)) or name not in allowed_names:
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


def _patch_exec_input(patch: str) -> str:
    """Use the UI host's supported native exec route for a validated patch."""
    return "const r = await tools.apply_patch(" + json.dumps(patch) + "); text(r);\n"


def _tool_inventory_exec_input() -> str:
    """Return executor-visible tool names without invoking a repo tool."""
    return "text(JSON.stringify(ALL_TOOLS.map(({name}) => name).sort()));\n"


def parse_provider_call(call: object, allowed_root: str) -> dict[str, Any]:
    """Validate one provider function call and produce native custom input."""
    item_id, call_id, name, arguments = _parse_arguments(call)
    if name == "apply_patch":
        return {"id": item_id, "call_id": call_id, "name": name, "input": _patch_from_arguments(arguments, allowed_root), "provider_arguments": arguments}
    return {"id": item_id, "call_id": call_id, "name": name, "input": _exec_input(arguments, allowed_root), "provider_arguments": arguments}


def _parse_mcp_inventory_call(call: object, operation: str = "inventory") -> dict[str, Any]:
    if operation not in {"inventory", "patch"}:
        raise AdapterError("unsupported_tool_or_event")
    item_id, call_id, name, arguments = _parse_arguments(call, {"tool_search", MCP_INVENTORY_TOOL_NAME})
    if name == "tool_search":
        query = arguments.get("query")
        if not isinstance(query, str) or not {"p114_exec_probe", "p114_exec", operation}.issubset(set(query.split())):
            raise AdapterError("malformed_provider_call")
        if set(arguments) - {"query", "limit"}:
            raise AdapterError("malformed_provider_call")
        limit = arguments.get("limit")
        if limit is not None and (not isinstance(limit, (int, float)) or isinstance(limit, bool) or limit <= 0 or limit > 8):
            raise AdapterError("malformed_provider_call")
    else:
        if arguments != {"operation": operation}:
            raise AdapterError("malformed_provider_call")
    return {"id": item_id, "call_id": call_id, "name": name, "provider_arguments": arguments}


def _tool_search_output_has_mcp_inventory_tool(item: dict[str, Any], namespace: str = "mcp__p114_exec_probe", tool_name: str = "p114_exec") -> bool:
    tools = item.get("tools")
    if not isinstance(tools, list):
        return False
    for entry in tools:
        if not isinstance(entry, dict):
            continue
        if entry.get("name") == MCP_INVENTORY_TOOL_NAME:
            return True
        if entry.get("type") == "namespace" and entry.get("name") == namespace and isinstance(entry.get("tools"), list):
            for namespace_tool in entry["tools"]:
                if isinstance(namespace_tool, dict) and namespace_tool.get("name") == tool_name:
                    return True
        nested_namespace = entry.get("namespace")
        if isinstance(nested_namespace, dict):
            namespace_name = nested_namespace.get("name")
            namespace_tools = nested_namespace.get("tools")
            if namespace_name == namespace and isinstance(namespace_tools, list):
                for namespace_tool in namespace_tools:
                    if isinstance(namespace_tool, dict) and namespace_tool.get("name") == tool_name:
                        return True
    return False


def _native_tool_search_call(call: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "tool_search_call",
        "id": call["id"],
        "call_id": call["call_id"],
        "execution": "client",
        "arguments": call.get("native_search_arguments", call["provider_arguments"]),
    }


def _native_mcp_inventory_call(call: dict[str, Any], arguments: str | None = None) -> dict[str, Any]:
    return {
        "type": "function_call",
        "id": call["id"],
        "call_id": call["call_id"],
        "name": "p114_exec",
        "namespace": "mcp__p114_exec_probe",
        "arguments": arguments if arguments is not None else json.dumps(call["provider_arguments"], separators=(",", ":")),
    }


def _native_package_mcp_call(call: dict[str, Any], server_name: str, arguments: str | None = None) -> dict[str, Any]:
    return {
        "type": "function_call",
        "id": call["id"],
        "call_id": call["call_id"],
        "name": call["native_tool"],
        "namespace": package_mcp_namespace(server_name),
        "arguments": arguments if arguments is not None else json.dumps(call["provider_arguments"], separators=(",", ":")),
    }


def _provider_function_call(call: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "function_call",
        "id": call["id"],
        "call_id": call["call_id"],
        "name": call["name"],
        "arguments": json.dumps(call["provider_arguments"], separators=(",", ":")),
    }


def _provider_tool_search_output(item: dict[str, Any]) -> str:
    return json.dumps(
        {
            "status": item.get("status"),
            "execution": item.get("execution"),
            "tools": item.get("tools", []),
        },
        separators=(",", ":"),
    )


def transform_request(payload: object, allowed_root: str, validated_calls: dict[str, dict[str, str]] | None = None, mcp_inventory: bool = False, mcp_operation: str = "inventory", package_mcp_server: str | None = None, package_mcp_read_file: bool = False) -> dict[str, Any]:
    """Translate initial and continuation requests without reducing tool scope."""
    if not isinstance(payload, dict) or not isinstance(payload.get("input"), list):
        raise AdapterError("malformed_request")
    items = payload["input"]
    if not (mcp_inventory or package_mcp_server) and any(isinstance(item, dict) and item.get("type") == "additional_tools" for item in items):
        raise AdapterError("unsupported_tool_or_event")
    translated = dict(payload)
    translated.pop("reasoning", None)
    translated["parallel_tool_calls"] = False
    translated["tools"] = TOOLS
    translated["tool_choice"] = "auto"
    validated_calls = validated_calls or {}
    translated_items: list[Any] = []
    completed_names: set[str] = set()
    for item in items:
        if (mcp_inventory or package_mcp_server) and isinstance(item, dict) and item.get("type") == "additional_tools":
            continue
        if package_mcp_server and isinstance(item, dict) and item.get("type") == "tool_search_call":
            call_id = item.get("call_id")
            cached = validated_calls.get(call_id) if isinstance(call_id, str) else None
            if not isinstance(cached, dict) or cached.get("name") != "tool_search":
                raise AdapterError("history_round_trip_invalid")
            translated_items.append(_provider_function_call(cached))
            continue
        if package_mcp_server and isinstance(item, dict) and item.get("type") == "tool_search_output":
            call_id = item.get("call_id")
            cached = validated_calls.get(call_id) if isinstance(call_id, str) else None
            if not isinstance(cached, dict) or cached.get("name") != "tool_search":
                raise AdapterError("history_round_trip_invalid")
            if all(tool_search_output_has_namespace(item, namespace=package_mcp_namespace(package_mcp_server), tool=tool) for tool in _package_mcp_tool_names(package_mcp_read_file)):
                completed_names.add("tool_search")
            translated_items.append({"type": "function_call_output", "call_id": call_id, "output": _provider_tool_search_output(item)})
            continue
        if package_mcp_server and isinstance(item, dict) and item.get("type") == "function_call" and item.get("namespace") == package_mcp_namespace(package_mcp_server) and item.get("name") in _package_mcp_tool_names(package_mcp_read_file):
            call_id = item.get("call_id")
            cached = validated_calls.get(call_id) if isinstance(call_id, str) else None
            if not isinstance(cached, dict) or cached.get("name") != _package_mcp_tool_name(package_mcp_server, item["name"]):
                raise AdapterError("history_round_trip_invalid")
            translated_items.append(_provider_function_call(cached))
            continue
        if package_mcp_server and isinstance(item, dict) and item.get("type") == "function_call_output":
            call_id = item.get("call_id")
            cached = validated_calls.get(call_id) if isinstance(call_id, str) else None
            accepted_names = {"tool_search", *(_package_mcp_tool_name(package_mcp_server, name) for name in _package_mcp_tool_names(package_mcp_read_file))}
            if not isinstance(cached, dict) or cached.get("name") not in accepted_names:
                raise AdapterError("history_round_trip_invalid")
            translated_items.append({"type": "function_call_output", "call_id": call_id, "output": item.get("output", "")})
            continue
        if mcp_inventory and isinstance(item, dict) and item.get("type") == "tool_search_call":
            call_id = item.get("call_id")
            cached = validated_calls.get(call_id) if isinstance(call_id, str) else None
            if not isinstance(cached, dict) or cached.get("name") != "tool_search" or not isinstance(cached.get("id"), str) or not isinstance(cached.get("provider_arguments"), dict):
                raise AdapterError("history_round_trip_invalid")
            translated_items.append(_provider_function_call(cached))
            continue
        if mcp_inventory and isinstance(item, dict) and item.get("type") == "tool_search_output":
            call_id = item.get("call_id")
            cached = validated_calls.get(call_id) if isinstance(call_id, str) else None
            if not isinstance(cached, dict) or cached.get("name") != "tool_search":
                raise AdapterError("history_round_trip_invalid")
            if _tool_search_output_has_mcp_inventory_tool(item):
                completed_names.add("tool_search")
            translated_items.append({"type": "function_call_output", "call_id": call_id, "output": _provider_tool_search_output(item)})
            continue
        if mcp_inventory and isinstance(item, dict) and item.get("type") == "function_call" and item.get("name") in {"tool_search", MCP_INVENTORY_TOOL_NAME}:
            call_id = item.get("call_id")
            cached = validated_calls.get(call_id) if isinstance(call_id, str) else None
            if not isinstance(cached, dict) or cached.get("name") != item.get("name") or not isinstance(cached.get("id"), str) or not isinstance(cached.get("provider_arguments"), dict):
                raise AdapterError("history_round_trip_invalid")
            if cached["name"] == "tool_search":
                translated_items.append(_provider_function_call(cached))
                continue
            translated_items.append(_provider_function_call(cached))
            continue
        if mcp_inventory and isinstance(item, dict) and item.get("type") == "function_call" and item.get("namespace") == "mcp__p114_exec_probe" and item.get("name") == "p114_exec":
            call_id = item.get("call_id")
            cached = validated_calls.get(call_id) if isinstance(call_id, str) else None
            if not isinstance(cached, dict) or cached.get("name") != MCP_INVENTORY_TOOL_NAME or not isinstance(cached.get("id"), str) or not isinstance(cached.get("provider_arguments"), dict):
                raise AdapterError("history_round_trip_invalid")
            translated_items.append(_provider_function_call(cached))
            continue
        if mcp_inventory and isinstance(item, dict) and item.get("type") == "function_call_output":
            call_id = item.get("call_id")
            cached = validated_calls.get(call_id) if isinstance(call_id, str) else None
            if not isinstance(cached, dict) or cached.get("name") not in {"tool_search", MCP_INVENTORY_TOOL_NAME}:
                raise AdapterError("history_round_trip_invalid")
            if cached["name"] != "tool_search" or MCP_INVENTORY_TOOL_NAME in str(item.get("output", "")):
                completed_names.add(cached["name"])
            translated_items.append({"type": "function_call_output", "call_id": call_id, "output": item.get("output", "")})
            continue
        if isinstance(item, dict) and item.get("type") == "function_call" and item.get("name") == "p114_exec":
            call_id = item.get("call_id")
            cached = validated_calls.get(call_id) if isinstance(call_id, str) else None
            if not isinstance(cached, dict) or cached.get("name") != "exec" or cached.get("host_name") != "p114_exec" or not isinstance(cached.get("id"), str) or not isinstance(cached.get("provider_arguments"), dict):
                raise AdapterError("history_round_trip_invalid")
            translated_items.append({"type": "function_call", "id": cached["id"], "call_id": call_id, "name": "exec", "arguments": json.dumps(cached["provider_arguments"], separators=(",", ":"))})
            continue
        if isinstance(item, dict) and item.get("type") == "function_call" and item.get("name") == "shell_command":
            call_id = item.get("call_id")
            cached = validated_calls.get(call_id) if isinstance(call_id, str) else None
            if not isinstance(cached, dict) or cached.get("name") != "exec" or not isinstance(cached.get("id"), str) or not isinstance(cached.get("provider_arguments"), dict):
                raise AdapterError("history_round_trip_invalid")
            translated_items.append({"type": "function_call", "id": cached["id"], "call_id": call_id, "name": "exec", "arguments": json.dumps(cached["provider_arguments"], separators=(",", ":"))})
            continue
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
                if isinstance(cached, dict) and cached.get("name") == "apply_patch" and cached.get("host_name") == "exec":
                    arguments = {"patch": cached["input"]}
                    name = "apply_patch"
                else:
                    arguments = cached.get("provider_arguments") if isinstance(cached, dict) else None
                if not isinstance(arguments, dict) or (name == "exec" and not isinstance(arguments.get("command"), str)):
                    raise AdapterError("history_round_trip_invalid")
            translated_items.append({"type": "function_call", "id": item_id, "call_id": call_id, "name": name, "arguments": json.dumps(arguments, separators=(",", ":"))})
        else:
            call_id = item.get("call_id")
            if not isinstance(call_id, str) or call_id not in validated_calls:
                raise AdapterError("history_round_trip_invalid")
            translated_items.append({"type": "function_call_output", "call_id": call_id, "output": item.get("output", "")})
    translated["input"] = translated_items
    if package_mcp_server:
        translated["tools"] = _package_mcp_tools(package_mcp_server, package_mcp_read_file) if "tool_search" in completed_names else [TOOL_SEARCH_TOOL]
    elif mcp_inventory:
        translated["tools"] = [mcp_exec_probe_tool(mcp_operation)] if "tool_search" in completed_names else [TOOL_SEARCH_TOOL]
    return translated


@dataclass
class StreamTranslator:
    """Translate sequential provider calls and preserve their native identity."""

    allowed_root: str
    pending: dict[str, dict[str, Any]] = field(default_factory=dict)
    accepted_calls: dict[str, dict[str, Any]] = field(default_factory=dict)
    rejected: bool = False
    standard_exec: bool = False
    patch_via_exec: bool = False
    host_tool_inventory: bool = False
    dynamic_exec_inventory: bool = False
    mcp_inventory: bool = False
    mcp_operation: str = "inventory"
    package_mcp_server: str | None = None
    package_mcp_read_file: bool = False
    call_validator: Callable[[dict[str, Any]], str | None] | None = None

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
            package_names = ({"tool_search", *(_package_mcp_tool_name(self.package_mcp_server, name) for name in _package_mcp_tool_names(self.package_mcp_read_file))} if self.package_mcp_server else set())
            if (self.mcp_inventory and item.get("name") in {"tool_search", MCP_INVENTORY_TOOL_NAME} or self.package_mcp_server and item.get("name") in package_names) and isinstance(item.get("id"), str) and isinstance(item.get("call_id"), str):
                self.pending[item["id"]] = {"item": item, "output_index": event.get("output_index", 0), "deltas": "", "mcp_inventory": True}
                return []
            if item.get("name") not in {"apply_patch", "exec"} or not isinstance(item.get("id"), str) or not isinstance(item.get("call_id"), str):
                return self._reject("unsupported_tool_or_event")
            if item.get("name") == "exec" and self.standard_exec and not self.host_tool_inventory and not self.dynamic_exec_inventory:
                provider_item = dict(item)
                host_item = dict(item)
                host_item["name"] = "shell_command"
                self.pending[item["id"]] = {"item": host_item, "provider_item": provider_item, "output_index": event.get("output_index", 0), "deltas": "", "standard_exec": True}
                return []
            custom = {"type": "custom_tool_call", "id": item["id"], "call_id": item["call_id"], "name": item["name"], "input": ""}
            self.pending[item["id"]] = {"item": item, "output_index": event.get("output_index", 0), "deltas": "", "custom": custom}
            return []
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
            item = dict(entry.get("provider_item", entry["item"]))
            item["arguments"] = event.get("arguments") or entry["deltas"]
            try:
                call = _parse_package_mcp_call(item, self.allowed_root, self.package_mcp_server, self.package_mcp_read_file) if entry.get("mcp_inventory") and self.package_mcp_server else _parse_mcp_inventory_call(item, self.mcp_operation) if entry.get("mcp_inventory") else parse_provider_call(item, self.allowed_root)
            except AdapterError as exc:
                return self._reject(exc.code)
            if self.call_validator is not None:
                code = self.call_validator(call)
                if code is not None:
                    return self._reject(code)
            if entry.get("standard_exec"):
                arguments = call["provider_arguments"]
                host_arguments = json.dumps({"command": arguments["command"]}, separators=(",", ":"))
                entry["item"]["arguments"] = host_arguments
                entry["provider_call"] = call
                self.accepted_calls[call["call_id"]] = call
                return [
                    {"type": "response.output_item.added", "output_index": entry["output_index"], "item": entry["item"]},
                    {"type": "response.function_call_arguments.delta", "item_id": call["id"], "output_index": entry["output_index"], "delta": host_arguments},
                    {"type": "response.function_call_arguments.done", "item_id": call["id"], "arguments": host_arguments},
                ]
            if call["name"] == "exec" and self.dynamic_exec_inventory:
                host_arguments = json.dumps({"operation": "inventory"}, separators=(",", ":"))
                host_item = {"type": "function_call", "id": call["id"], "call_id": call["call_id"], "name": "p114_exec", "arguments": host_arguments}
                entry["item"] = host_item
                entry["dynamic_exec_inventory"] = True
                call = {**call, "host_name": "p114_exec", "host_arguments": host_arguments}
                self.accepted_calls[call["call_id"]] = call
                return [
                    {"type": "response.output_item.added", "output_index": entry["output_index"], "item": host_item},
                    {"type": "response.function_call_arguments.delta", "item_id": call["id"], "output_index": entry["output_index"], "delta": host_arguments},
                    {"type": "response.function_call_arguments.done", "item_id": call["id"], "arguments": host_arguments},
                ]
            if entry.get("mcp_inventory"):
                host_arguments = json.dumps(call["provider_arguments"], separators=(",", ":"))
                if call["name"] == "tool_search":
                    host_item = _native_tool_search_call(call)
                    entry["item"] = host_item
                    self.accepted_calls[call["call_id"]] = call
                    return [
                        {"type": "response.output_item.added", "output_index": entry["output_index"], "item": host_item},
                    ]
                entry["item"] = _native_package_mcp_call(call, self.package_mcp_server, host_arguments) if self.package_mcp_server else _native_mcp_inventory_call(call, host_arguments)
                self.accepted_calls[call["call_id"]] = call
                return [
                    {"type": "response.output_item.added", "output_index": entry["output_index"], "item": entry["item"]},
                    {"type": "response.function_call_arguments.delta", "item_id": call["id"], "output_index": entry["output_index"], "delta": host_arguments},
                    {"type": "response.function_call_arguments.done", "item_id": call["id"], "arguments": host_arguments},
                ]
            host_input = call["input"]
            if call["name"] == "apply_patch" and self.patch_via_exec:
                host_input = _patch_exec_input(call["input"])
                entry["custom"]["name"] = "exec"
                call = {**call, "host_name": "exec", "host_input": host_input}
            elif call["name"] == "exec" and self.host_tool_inventory:
                host_input = _tool_inventory_exec_input()
                entry["custom"]["name"] = "exec"
                call = {**call, "host_name": "exec", "host_input": host_input}
            entry["custom"]["input"] = host_input
            self.accepted_calls[call["call_id"]] = call
            return [
                {"type": "response.output_item.added", "output_index": entry["output_index"], "item": entry["custom"]},
                {"type": "response.custom_tool_call_input.delta", "item_id": call["id"], "output_index": entry["output_index"], "delta": host_input},
                {"type": "response.custom_tool_call_input.done", "item_id": call["id"], "output_index": entry["output_index"], "input": host_input},
            ]
        if event_type == "response.output_item.done":
            item = event.get("item")
            if isinstance(item, dict) and item.get("type") == "function_call":
                entry = self.pending.get(item.get("id"))
                if entry is None:
                    return self._reject("malformed_provider_call")
                if entry.get("standard_exec"):
                    return [{"type": "response.output_item.done", "output_index": event.get("output_index", entry["output_index"]), "item": entry["item"]}]
                if entry.get("dynamic_exec_inventory"):
                    return [{"type": "response.output_item.done", "output_index": event.get("output_index", entry["output_index"]), "item": entry["item"]}]
                if entry.get("mcp_inventory"):
                    return [{"type": "response.output_item.done", "output_index": event.get("output_index", entry["output_index"]), "item": entry["item"]}]
                return [{"type": "response.output_item.done", "output_index": event.get("output_index", entry["output_index"]), "item": entry["custom"]}]
            if isinstance(item, dict) and item.get("type") == "tool_search_call":
                entry = self.pending.get(item.get("id"))
                if entry is None or not entry.get("mcp_inventory"):
                    return self._reject("malformed_provider_call")
                return [{"type": "response.output_item.done", "output_index": event.get("output_index", entry["output_index"]), "item": entry["item"]}]
        if event_type == "response.completed" and isinstance(event.get("response"), dict):
            completed = dict(event)
            response = dict(event["response"])
            output = response.get("output")
            if isinstance(output, list):
                response["output"] = [
                    (
                        {"type": "function_call", "id": call["id"], "call_id": call["call_id"], "name": "p114_exec", "arguments": call["host_arguments"]}
                        if call.get("host_name") == "p114_exec"
                        else _native_tool_search_call(call)
                        if (self.mcp_inventory or self.package_mcp_server) and call["name"] == "tool_search"
                        else _native_package_mcp_call(call, self.package_mcp_server)
                        if self.package_mcp_server and call["name"] != "tool_search"
                        else _native_mcp_inventory_call(call)
                        if self.mcp_inventory and call["name"] == MCP_INVENTORY_TOOL_NAME
                        else {"type": "custom_tool_call", "id": call["id"], "call_id": call["call_id"], "name": call.get("host_name", call["name"]), "input": call.get("host_input", call["input"])}
                    )
                    if isinstance(item, dict)
                    and item.get("type") == "function_call"
                    and isinstance(item.get("call_id"), str)
                    and (call := self.accepted_calls.get(item["call_id"])) is not None
                    else item
                    for item in output
                ]
            completed["response"] = response
            return [completed]
        return [event]

    def _reject(self, code: str) -> list[dict[str, Any]]:
        self.rejected = True
        return [{"type": "response.error", "error": {"code": code, "message": code}}]
