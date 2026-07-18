"""Canonical tool schemas for the Agent Workbench agent bridge."""

from __future__ import annotations

from typing import Any


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
READ_FILE_TOOL = {
    "type": "function",
    "name": "read_file",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "start_line": {"type": "integer", "minimum": 1},
            "end_line": {"type": "integer", "minimum": 1},
        },
        "required": ["path"],
        "additionalProperties": False,
    },
    "strict": True,
}
TOOLS = [PATCH_TOOL, EXEC_TOOL]

TOOL_SEARCH_TOOL = {
    "type": "function",
    "name": "tool_search",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "limit": {"type": "number"},
        },
        "required": ["query"],
        "additionalProperties": False,
    },
    "strict": True,
}

MCP_PROBE_NAMESPACE = "mcp__p114_exec_probe"
MCP_PROBE_TOOL = "p114_exec"
MCP_PROBE_COMPATIBILITY_TOOL_NAME = f"{MCP_PROBE_NAMESPACE}__{MCP_PROBE_TOOL}"
SUPPORTED_MCP_PROBE_OPERATIONS = frozenset({"inventory", "patch"})


def mcp_compatibility_tool(operation: str) -> dict[str, Any]:
    """Return the provider-facing flat compatibility schema for one MCP op."""
    if operation not in SUPPORTED_MCP_PROBE_OPERATIONS:
        raise ValueError(f"unsupported MCP probe operation: {operation}")
    return {
        "type": "function",
        "name": MCP_PROBE_COMPATIBILITY_TOOL_NAME,
        "parameters": {
            "type": "object",
            "properties": {"operation": {"type": "string", "enum": [operation]}},
            "required": ["operation"],
            "additionalProperties": False,
        },
        "strict": True,
    }


def package_mcp_namespace(server_name: str) -> str:
    """Return the native child namespace for one configured package server."""
    if not server_name or any(not (character.isalnum() or character == "_") for character in server_name):
        raise ValueError(f"invalid MCP server name: {server_name!r}")
    return f"mcp__{server_name}"


def package_mcp_compatibility_tool(server_name: str, tool_name: str) -> dict[str, Any]:
    """Return the flat provider schema for a package MCP tool.

    Codex itself receives the corresponding namespaced call after native
    deferred discovery.  The OpenAI-compatible provider never sees that
    child-facing namespace shape.
    """
    namespace = package_mcp_namespace(server_name)
    source = {"exec": EXEC_TOOL, "apply_patch": PATCH_TOOL, "read_file": READ_FILE_TOOL}.get(tool_name)
    if source is None:
        raise ValueError(f"unsupported package MCP tool: {tool_name}")
    return {
        **source,
        "name": f"{namespace}__{tool_name}",
        "parameters": dict(source["parameters"]),
    }
