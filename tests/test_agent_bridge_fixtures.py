from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_workbench.agent_bridge.protocol import native_mcp_function_call, provider_flat_function_call, tool_search_output_has_namespace
from agent_workbench.agent_bridge.tools import MCP_PROBE_COMPATIBILITY_TOOL_NAME, MCP_PROBE_NAMESPACE, MCP_PROBE_TOOL, mcp_compatibility_tool

FIXTURE_DIR = ROOT / "tests" / "fixtures" / "p114"


def load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def lifecycle_types(fixture: dict[str, Any]) -> list[str]:
    return [item["type"] for item in fixture["lifecycle"]]


def test_r22_and_r23_fixtures_preserve_namespaced_mcp_lifecycle() -> None:
    contract = load_fixture("mcp_tool_search_contract.json")
    for name, operation, marker, target_after in [
        ("r22_namespaced_mcp_inventory.json", "inventory", "P114_MCP_EXEC_HANDLER_REACHED", "before\n"),
        ("r23_namespaced_mcp_patch.json", "patch", "P114_MCP_PATCH_HANDLER_REACHED", "after\n"),
    ]:
        fixture = load_fixture(name)
        assert lifecycle_types(fixture) == contract["required_lifecycle"]
        assert fixture["provider_compatibility_tool"] == contract["provider_flat_compatibility"]
        assert fixture["native_namespace"] == contract["child_native_namespace"]
        assert fixture["native_tool"] == contract["child_native_tool"]
        assert fixture["operation"] == operation
        assert fixture["target_before"] == "before\n"
        assert fixture["target_after"] == target_after

        search_call, search_output, function_call, function_output = fixture["lifecycle"]
        assert search_call["arguments"]["query"] == fixture["search_query"]
        assert search_output["call_id"] == search_call["call_id"]
        assert search_output["tools"][0]["name"] == fixture["native_namespace"]
        assert search_output["tools"][0]["tools"][0]["name"] == fixture["native_tool"]
        assert function_call["namespace"] == fixture["native_namespace"]
        assert function_call["name"] == fixture["native_tool"]
        assert function_call["arguments"] == {"operation": operation}
        assert function_output["call_id"] == function_call["call_id"]
        assert function_output["output_contains"] == marker


def test_r23_fixture_records_forbidden_fallback_tools() -> None:
    fixture = load_fixture("r23_namespaced_mcp_patch.json")
    child_items = fixture["lifecycle"]
    forbidden_names = set(fixture["forbidden_child_tool_names"])
    forbidden_types = set(fixture["forbidden_child_item_types"])
    assert not [item for item in child_items if item.get("name") in forbidden_names]
    assert not [item for item in child_items if item.get("type") in forbidden_types]


def test_p114_fixtures_are_sanitized() -> None:
    forbidden_fragments = [
        "C:/Users/",
        "C:\\Users\\",
        "https://",
        "AGENT_WORKBENCH_PROVIDER_HEADERS",
        "Cloudflare",
        "019f",
    ]
    for path in FIXTURE_DIR.glob("*.json"):
        text = path.read_text(encoding="utf-8")
        assert json.loads(text)
        for fragment in forbidden_fragments:
            assert fragment not in text


def test_agent_bridge_protocol_helpers_preserve_flat_and_namespaced_shapes() -> None:
    flat = provider_flat_function_call(item_id="mcp_1", call_id="call_mcp_1", name=MCP_PROBE_COMPATIBILITY_TOOL_NAME, arguments={"operation": "patch"})
    native = native_mcp_function_call(item_id="mcp_1", call_id="call_mcp_1", arguments={"operation": "patch"})
    assert flat["name"] == "mcp__p114_exec_probe__p114_exec"
    assert "namespace" not in flat
    assert native["namespace"] == MCP_PROBE_NAMESPACE
    assert native["name"] == MCP_PROBE_TOOL
    assert json.loads(native["arguments"]) == {"operation": "patch"}
    assert mcp_compatibility_tool("patch")["parameters"]["properties"]["operation"]["enum"] == ["patch"]

    search_output = load_fixture("r23_namespaced_mcp_patch.json")["lifecycle"][1]
    assert tool_search_output_has_namespace(search_output, namespace=MCP_PROBE_NAMESPACE, tool=MCP_PROBE_TOOL) is True
    assert tool_search_output_has_namespace(search_output, namespace=MCP_PROBE_NAMESPACE, tool="missing") is False
