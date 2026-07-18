"""Pure protocol helpers for flat-provider and native Codex tool shapes."""

from __future__ import annotations

import json
from typing import Any

from agent_workbench.agent_bridge.tools import MCP_PROBE_NAMESPACE, MCP_PROBE_TOOL


def native_mcp_function_call(*, item_id: str, call_id: str, arguments: dict[str, Any], namespace: str = MCP_PROBE_NAMESPACE, tool: str = MCP_PROBE_TOOL) -> dict[str, Any]:
    """Build the child-facing namespaced MCP function call shape."""
    return {
        "type": "function_call",
        "id": item_id,
        "call_id": call_id,
        "name": tool,
        "namespace": namespace,
        "arguments": json.dumps(arguments, separators=(",", ":")),
    }


def provider_flat_function_call(*, item_id: str, call_id: str, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Build the provider-facing flat function call shape."""
    return {
        "type": "function_call",
        "id": item_id,
        "call_id": call_id,
        "name": name,
        "arguments": json.dumps(arguments, separators=(",", ":")),
    }


def tool_search_output_has_namespace(item: dict[str, Any], *, namespace: str, tool: str) -> bool:
    """Return true when a native tool_search_output exposes a namespaced tool."""
    tools = item.get("tools")
    if not isinstance(tools, list):
        return False
    for entry in tools:
        if not isinstance(entry, dict):
            continue
        if entry.get("type") == "namespace" and entry.get("name") == namespace and isinstance(entry.get("tools"), list):
            return any(isinstance(candidate, dict) and candidate.get("name") == tool for candidate in entry["tools"])
        nested = entry.get("namespace")
        if isinstance(nested, dict) and nested.get("name") == namespace and isinstance(nested.get("tools"), list):
            return any(isinstance(candidate, dict) and candidate.get("name") == tool for candidate in nested["tools"])
    return False

