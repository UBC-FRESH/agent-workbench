from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_workbench.p113_function_tool_adapter import AdapterError
from agent_workbench.p114_capability_tool_adapter import MCP_INVENTORY_TOOL_NAME, StreamTranslator, force_tool_choice, mcp_exec_probe_tool, parse_provider_call, transform_request
from agent_workbench.agent_bridge.tools import package_mcp_compatibility_tool, package_mcp_namespace


ROOT_PATH = "runtime/agent_jobs/p114_fixture/worktree"
PATCH = "*** Begin Patch\n*** Update File: runtime/agent_jobs/p114_fixture/worktree/allowed.txt\n@@\n-old\n+new\n*** End Patch"


def function_events(name: str, arguments: dict[str, object], item_id: str = "fc_1", call_id: str = "call_1") -> list[dict[str, object]]:
    return [
        {"type": "response.output_item.added", "output_index": 0, "item": {"type": "function_call", "id": item_id, "call_id": call_id, "name": name}},
        {"type": "response.function_call_arguments.done", "item_id": item_id, "arguments": json.dumps(arguments)},
        {"type": "response.output_item.done", "output_index": 0, "item": {"type": "function_call", "id": item_id}},
    ]


def test_initial_request_exposes_patch_and_exec_without_reasoning() -> None:
    request = transform_request({"input": [{"type": "message", "role": "user", "content": "work"}], "reasoning": {"effort": "high"}}, ROOT_PATH)
    assert [tool["name"] for tool in request["tools"]] == ["apply_patch", "exec"]
    assert request["tool_choice"] == "auto"
    assert request["parallel_tool_calls"] is False
    assert "reasoning" not in request


def test_mcp_inventory_initial_request_exposes_only_tool_search() -> None:
    request = transform_request({"input": [{"type": "message", "role": "user", "content": "work"}], "reasoning": {"effort": "high"}}, ROOT_PATH, mcp_inventory=True)
    assert [tool["name"] for tool in request["tools"]] == ["tool_search"]
    assert request["tool_choice"] == "auto"
    assert request["parallel_tool_calls"] is False
    assert "reasoning" not in request


def test_package_mcp_initial_request_then_search_exposes_separate_grant_tools() -> None:
    server_name = "agent_bridge_p114_package_fixture"
    initial = transform_request({"input": [{"type": "message", "role": "user", "content": "work"}]}, ROOT_PATH, package_mcp_server=server_name)
    assert [tool["name"] for tool in initial["tools"]] == ["tool_search"]

    history = [
        {"type": "tool_search_call", "id": "search_1", "call_id": "call_search_1", "execution": "client", "arguments": {"query": f"{server_name} exec apply_patch"}},
        {"type": "tool_search_output", "call_id": "call_search_1", "status": "completed", "execution": "client", "tools": [{"type": "namespace", "name": package_mcp_namespace(server_name), "tools": [{"name": "exec"}, {"name": "apply_patch"}]}]},
    ]
    request = transform_request({"input": history}, ROOT_PATH, {"call_search_1": {"id": "search_1", "call_id": "call_search_1", "name": "tool_search", "provider_arguments": {"query": f"{server_name} exec apply_patch"}}}, package_mcp_server=server_name)
    assert [tool["name"] for tool in request["tools"]] == [
        package_mcp_compatibility_tool(server_name, "exec")["name"],
        package_mcp_compatibility_tool(server_name, "apply_patch")["name"],
    ]


def test_package_mcp_read_file_is_exposed_only_when_the_qualification_flag_is_set() -> None:
    server_name = "agent_bridge_p114_package_fixture"
    history = [
        {"type": "tool_search_call", "id": "search_1", "call_id": "call_search_1", "execution": "client", "arguments": {"query": f"{server_name} exec apply_patch read_file"}},
        {"type": "tool_search_output", "call_id": "call_search_1", "status": "completed", "execution": "client", "tools": [{"type": "namespace", "name": package_mcp_namespace(server_name), "tools": [{"name": "exec"}, {"name": "apply_patch"}, {"name": "read_file"}]}]},
    ]
    request = transform_request(
        {"input": history}, ROOT_PATH,
        {"call_search_1": {"id": "search_1", "call_id": "call_search_1", "name": "tool_search", "provider_arguments": {"query": f"{server_name} exec apply_patch read_file"}}},
        package_mcp_server=server_name,
        package_mcp_read_file=True,
    )
    assert [tool["name"] for tool in request["tools"]] == [
        package_mcp_compatibility_tool(server_name, "exec")["name"],
        package_mcp_compatibility_tool(server_name, "apply_patch")["name"],
        package_mcp_compatibility_tool(server_name, "read_file")["name"],
    ]


def test_qualification_accepts_the_frozen_ticket_path_as_the_discovery_query() -> None:
    server_name = "agent_bridge_p114_package_fixture"
    translator = StreamTranslator(ROOT_PATH, package_mcp_server=server_name, package_mcp_read_file=True)
    outputs = [item for event in function_events("tool_search", {"query": "runtime/agent_jobs/p107_suite_provenance_audit_bundle_ticket.md"}) for item in translator.consume(event)]
    assert outputs[-1]["item"] == {
        "type": "tool_search_call",
        "id": "fc_1",
        "call_id": "call_1",
        "execution": "client",
        "arguments": {"query": f"{server_name} exec apply_patch read_file"},
    }
    assert translator.accepted_calls["call_1"]["provider_arguments"] == {
        "query": "runtime/agent_jobs/p107_suite_provenance_audit_bundle_ticket.md"
    }


def test_package_mcp_qualification_accepts_bounded_read_file_arguments() -> None:
    server_name = "agent_bridge_p114_package_fixture"
    translator = StreamTranslator(ROOT_PATH, package_mcp_server=server_name, package_mcp_read_file=True)
    name = package_mcp_compatibility_tool(server_name, "read_file")["name"]

    output = [item for event in function_events(name, {"path": "README.md", "start_line": 2, "end_line": 4}) for item in translator.consume(event)]

    completed = [event["item"] for event in output if event["type"] == "response.output_item.done"]
    assert [(item["namespace"], item["name"]) for item in completed] == [(package_mcp_namespace(server_name), "read_file")]
    schema = package_mcp_compatibility_tool(server_name, "read_file")["parameters"]
    assert set(schema["properties"]) == {"path", "start_line", "end_line"}


@pytest.mark.parametrize(
    "tools",
    [
        [{"name": MCP_INVENTORY_TOOL_NAME}],
        [{"type": "namespace", "name": "mcp__wrong_server", "tools": [{"name": "exec"}, {"name": "apply_patch"}]}],
        [{"type": "namespace", "name": "mcp__agent_bridge_p114_package_fixture", "tools": [{"name": "exec"}]}],
    ],
)
def test_package_mcp_discovery_requires_both_exact_namespaced_tools(tools: list[dict[str, object]]) -> None:
    server_name = "agent_bridge_p114_package_fixture"
    history = [
        {"type": "tool_search_call", "id": "search_1", "call_id": "call_search_1", "execution": "client", "arguments": {"query": f"{server_name} exec apply_patch"}},
        {"type": "tool_search_output", "call_id": "call_search_1", "status": "completed", "execution": "client", "tools": tools},
    ]
    request = transform_request({"input": history}, ROOT_PATH, {"call_search_1": {"id": "search_1", "call_id": "call_search_1", "name": "tool_search", "provider_arguments": {"query": f"{server_name} exec apply_patch"}}}, package_mcp_server=server_name)
    assert [tool["name"] for tool in request["tools"]] == ["tool_search"]


def test_package_mcp_translates_flat_exec_and_patch_to_native_namespace() -> None:
    server_name = "agent_bridge_p114_package_fixture"
    translator = StreamTranslator(ROOT_PATH, package_mcp_server=server_name)
    exec_name = package_mcp_compatibility_tool(server_name, "exec")["name"]
    patch_name = package_mcp_compatibility_tool(server_name, "apply_patch")["name"]
    exec_items = [output for event in function_events(exec_name, {"command": "Get-Content allowed.txt", "workdir": ROOT_PATH}, "exec_1", "call_exec_1") for output in translator.consume(event)]
    package_patch = PATCH.replace(ROOT_PATH + "/", "")
    patch_items = [output for event in function_events(patch_name, {"patch": package_patch}, "patch_1", "call_patch_1") for output in translator.consume(event)]
    completed = [event["item"] for event in exec_items + patch_items if event["type"] == "response.output_item.done"]
    assert [(item["namespace"], item["name"]) for item in completed] == [
        (package_mcp_namespace(server_name), "exec"),
        (package_mcp_namespace(server_name), "apply_patch"),
    ]


def test_package_mcp_accepts_standard_unified_patch_for_an_allowed_relative_path() -> None:
    server_name = "agent_bridge_p114_package_fixture"
    patch = "--- /dev/null\n+++ b/new.py\n@@ -0,0 +1 @@\n+value = 1\n"
    translator = StreamTranslator(ROOT_PATH, package_mcp_server=server_name)
    name = package_mcp_compatibility_tool(server_name, "apply_patch")["name"]

    output = [item for event in function_events(name, {"patch": patch}) for item in translator.consume(event)]

    completed = [event["item"] for event in output if event["type"] == "response.output_item.done"]
    assert [(item["namespace"], item["name"]) for item in completed] == [(package_mcp_namespace(server_name), "apply_patch")]


@pytest.mark.parametrize("path", ["/absolute.txt", "../escape.txt"])
def test_package_mcp_rejects_absolute_and_traversing_patch_paths(path: str) -> None:
    server_name = "agent_bridge_p114_package_fixture"
    patch = f"*** Begin Patch\n*** Update File: {path}\n@@\n-before\n+after\n*** End Patch"
    translator = StreamTranslator(ROOT_PATH, package_mcp_server=server_name)
    name = package_mcp_compatibility_tool(server_name, "apply_patch")["name"]
    output = [item for event in function_events(name, {"patch": patch}) for item in translator.consume(event)]
    assert output == [{"type": "response.error", "error": {"code": "path_outside_allowed_root", "message": "path_outside_allowed_root"}}]


def test_mcp_inventory_continuation_exposes_only_inventory_tool() -> None:
    history = [
        {"type": "tool_search_call", "id": "search_1", "call_id": "call_search_1", "execution": "client", "arguments": {"query": "p114_exec_probe p114_exec inventory"}},
        {"type": "tool_search_output", "call_id": "call_search_1", "status": "completed", "execution": "client", "tools": [{"name": MCP_INVENTORY_TOOL_NAME}]},
        {"type": "additional_tools", "tools": [{"name": MCP_INVENTORY_TOOL_NAME}]},
    ]
    request = transform_request({"input": history}, ROOT_PATH, {"call_search_1": {"id": "search_1", "call_id": "call_search_1", "name": "tool_search", "provider_arguments": {"query": "p114_exec_probe p114_exec inventory"}}}, mcp_inventory=True)
    assert [tool["name"] for tool in request["tools"]] == [MCP_INVENTORY_TOOL_NAME]
    assert [item["type"] for item in request["input"]] == ["function_call", "function_call_output"]
    assert request["input"][0] == {
        "type": "function_call",
        "id": "search_1",
        "call_id": "call_search_1",
        "name": "tool_search",
        "arguments": json.dumps({"query": "p114_exec_probe p114_exec inventory"}, separators=(",", ":")),
    }
    assert json.loads(request["input"][1]["output"]) == {
        "status": "completed",
        "execution": "client",
        "tools": [{"name": MCP_INVENTORY_TOOL_NAME}],
    }


def test_mcp_patch_continuation_exposes_only_patch_tool_schema() -> None:
    history = [
        {"type": "tool_search_call", "id": "search_1", "call_id": "call_search_1", "execution": "client", "arguments": {"query": "p114_exec_probe p114_exec patch"}},
        {"type": "tool_search_output", "call_id": "call_search_1", "status": "completed", "execution": "client", "tools": [{"name": MCP_INVENTORY_TOOL_NAME}]},
    ]
    request = transform_request(
        {"input": history},
        ROOT_PATH,
        {"call_search_1": {"id": "search_1", "call_id": "call_search_1", "name": "tool_search", "provider_arguments": {"query": "p114_exec_probe p114_exec patch"}}},
        mcp_inventory=True,
        mcp_operation="patch",
    )
    assert request["tools"] == [mcp_exec_probe_tool("patch")]


def test_mcp_inventory_continuation_accepts_namespace_tool_search_output() -> None:
    history = [
        {"type": "tool_search_call", "id": "search_1", "call_id": "call_search_1", "execution": "client", "arguments": {"query": "p114_exec_probe p114_exec inventory"}},
        {
            "type": "tool_search_output",
            "call_id": "call_search_1",
            "status": "completed",
            "execution": "client",
            "tools": [{"type": "namespace", "name": "mcp__p114_exec_probe", "tools": [{"type": "function", "name": "p114_exec"}]}],
        },
    ]
    request = transform_request({"input": history}, ROOT_PATH, {"call_search_1": {"id": "search_1", "call_id": "call_search_1", "name": "tool_search", "provider_arguments": {"query": "p114_exec_probe p114_exec inventory"}}}, mcp_inventory=True)
    assert [tool["name"] for tool in request["tools"]] == [MCP_INVENTORY_TOOL_NAME]
    assert [item["type"] for item in request["input"]] == ["function_call", "function_call_output"]
    assert "mcp__p114_exec_probe" in request["input"][1]["output"]


def test_mcp_inventory_does_not_expose_inventory_tool_without_search_hit() -> None:
    history = [
        {"type": "tool_search_call", "id": "search_1", "call_id": "call_search_1", "execution": "client", "arguments": {"query": "p114_exec_probe p114_exec inventory"}},
        {"type": "tool_search_output", "call_id": "call_search_1", "status": "completed", "execution": "client", "tools": []},
    ]
    request = transform_request({"input": history}, ROOT_PATH, {"call_search_1": {"id": "search_1", "call_id": "call_search_1", "name": "tool_search", "provider_arguments": {"query": "p114_exec_probe p114_exec inventory"}}}, mcp_inventory=True)
    assert [tool["name"] for tool in request["tools"]] == ["tool_search"]


def test_forced_tool_choice_preserves_the_complete_c4_catalog() -> None:
    translated = force_tool_choice({"tools": []}, "exec")
    assert [tool["name"] for tool in translated["tools"]] == ["apply_patch", "exec"]
    assert translated["tool_choice"] == {"type": "function", "name": "exec"}


def test_patch_supports_strict_and_known_freeform_provider_shape() -> None:
    strict = parse_provider_call({"id": "patch_1", "call_id": "call_patch_1", "name": "apply_patch", "arguments": json.dumps({"patch": PATCH})}, ROOT_PATH)
    freeform = parse_provider_call({"id": "patch_2", "call_id": "call_patch_2", "name": "apply_patch", "arguments": json.dumps({"command": "apply_patch\n" + PATCH})}, ROOT_PATH)
    assert strict["input"] == PATCH
    assert freeform["input"] == PATCH


def test_literal_absolute_worktree_allows_only_contained_patch_and_exec() -> None:
    absolute_root = "C:/worktree"
    absolute_patch = PATCH.replace(ROOT_PATH, absolute_root)
    patch = parse_provider_call({"id": "patch_absolute", "call_id": "call_patch_absolute", "name": "apply_patch", "arguments": json.dumps({"patch": absolute_patch})}, absolute_root)
    assert patch["input"] == absolute_patch
    exec_call = parse_provider_call({"id": "exec_absolute", "call_id": "call_exec_absolute", "name": "exec", "arguments": json.dumps({"command": "Get-Content allowed.txt", "workdir": "C:/worktree/subdir"})}, absolute_root)
    assert '"workdir":"C:/worktree/subdir"' in exec_call["input"]
    with pytest.raises(AdapterError, match="path_outside_allowed_root"):
        parse_provider_call({"id": "patch_escape", "call_id": "call_patch_escape", "name": "apply_patch", "arguments": json.dumps({"patch": absolute_patch.replace("C:/worktree/allowed.txt", "C:/outside/allowed.txt")})}, absolute_root)


def test_exec_is_bound_to_worktree_and_never_runs_in_adapter() -> None:
    call = parse_provider_call({"id": "exec_1", "call_id": "call_exec_1", "name": "exec", "arguments": json.dumps({"command": "Get-Content allowed.txt", "workdir": ROOT_PATH, "timeout_ms": 2500})}, ROOT_PATH)
    assert call["name"] == "exec"
    assert "tools.shell_command" in call["input"]
    assert "Get-Content allowed.txt" in call["input"]
    with pytest.raises(AdapterError, match="path_outside_allowed_root"):
        parse_provider_call({"id": "exec_2", "call_id": "call_exec_2", "name": "exec", "arguments": json.dumps({"command": "pwd", "workdir": "C:/outside"})}, ROOT_PATH)


def test_stream_translates_sequential_exec_and_patch_calls() -> None:
    translator = StreamTranslator(ROOT_PATH)
    events = function_events("exec", {"command": "Get-Content allowed.txt"}, "exec_1", "call_exec_1") + function_events("apply_patch", {"patch": PATCH}, "patch_1", "call_patch_1")
    translated = [output for event in events for output in translator.consume(event)]
    completed = [event["item"] for event in translated if event["type"] == "response.output_item.done"]
    assert [item["name"] for item in completed] == ["exec", "apply_patch"]
    assert "tools.shell_command" in completed[0]["input"]
    assert completed[1]["input"] == PATCH


def test_standard_exec_preserves_a_complete_host_shell_lifecycle() -> None:
    translator = StreamTranslator(ROOT_PATH, standard_exec=True)
    translated = [output for event in function_events("exec", {"command": "Get-Content allowed.txt"}, "exec_1", "call_exec_1") for output in translator.consume(event)]
    assert [event["type"] for event in translated] == [
        "response.output_item.added",
        "response.function_call_arguments.delta",
        "response.function_call_arguments.done",
        "response.output_item.done",
    ]
    assert translated[0]["item"]["name"] == "shell_command"
    assert json.loads(translated[1]["delta"]) == {"command": "Get-Content allowed.txt"}
    assert translated[2]["arguments"] == translated[1]["delta"]
    assert translated[3]["item"]["arguments"] == translated[1]["delta"]


def test_standard_exec_rejects_an_undeclared_command_before_emitting_a_host_call() -> None:
    translator = StreamTranslator(
        ROOT_PATH,
        standard_exec=True,
        call_validator=lambda call: "undeclared_exec" if call["provider_arguments"]["command"] == "Set-Content blocked.txt after" else None,
    )
    translated = [
        output
        for event in function_events("exec", {"command": "Set-Content blocked.txt after"}, "exec_1", "call_exec_1")
        for output in translator.consume(event)
    ]
    assert translated == [{"type": "response.error", "error": {"code": "undeclared_exec", "message": "undeclared_exec"}}]
    assert translator.accepted_calls == {}
    assert translator.rejected is True


def test_standard_shell_history_round_trips_to_provider_exec() -> None:
    history = [
        {"type": "function_call", "id": "host_shell_1", "call_id": "call_exec_1", "name": "shell_command", "arguments": json.dumps({"command": "Get-Content allowed.txt"})},
        {"type": "function_call_output", "call_id": "call_exec_1", "output": "ok"},
    ]
    request = transform_request({"input": history}, ROOT_PATH, {"call_exec_1": {"id": "exec_1", "call_id": "call_exec_1", "name": "exec", "provider_arguments": {"command": "Get-Content allowed.txt", "workdir": ROOT_PATH}}})
    assert request["input"][0] == {"type": "function_call", "id": "exec_1", "call_id": "call_exec_1", "name": "exec", "arguments": json.dumps({"command": "Get-Content allowed.txt", "workdir": ROOT_PATH}, separators=(",", ":"))}
    assert request["input"][1] == history[1]


def test_stream_rewrites_completed_response_output_to_custom_tool_identity() -> None:
    translator = StreamTranslator(ROOT_PATH)
    events = function_events("apply_patch", {"patch": PATCH}, "patch_1", "call_patch_1")
    translated = [output for event in events for output in translator.consume(event)]
    translated.extend(translator.consume({"type": "response.completed", "response": {"output": [{"type": "function_call", "id": "patch_1", "call_id": "call_patch_1", "name": "apply_patch", "arguments": json.dumps({"patch": PATCH})}]}}))
    completed = translated[-1]["response"]["output"]
    assert completed == [{"type": "custom_tool_call", "id": "patch_1", "call_id": "call_patch_1", "name": "apply_patch", "input": PATCH}]


def test_patch_via_exec_matches_lunas_native_exec_wrapper() -> None:
    translator = StreamTranslator(ROOT_PATH, patch_via_exec=True)
    translated = [output for event in function_events("apply_patch", {"patch": PATCH}, "patch_1", "call_patch_1") for output in translator.consume(event)]
    completed = [event["item"] for event in translated if event["type"] == "response.output_item.done"]
    assert completed[0]["name"] == "exec"
    assert completed[0]["input"] == "const r = await tools.apply_patch(" + json.dumps(PATCH) + "); text(r);\n"


def test_host_tool_inventory_uses_one_inert_custom_exec_call() -> None:
    translator = StreamTranslator(ROOT_PATH, standard_exec=True, host_tool_inventory=True)
    translated = [output for event in function_events("exec", {"command": "Write-Output P114_C4_HOST_TOOL_INVENTORY"}, "exec_1", "call_exec_1") for output in translator.consume(event)]
    completed = [event["item"] for event in translated if event["type"] == "response.output_item.done"]
    assert [item["name"] for item in completed] == ["exec"]
    assert completed[0]["input"] == "text(JSON.stringify(ALL_TOOLS.map(({name}) => name).sort()));\n"
    assert "tools.shell_command" not in completed[0]["input"]


def test_dynamic_exec_inventory_uses_registered_function_call() -> None:
    translator = StreamTranslator(ROOT_PATH, standard_exec=True, dynamic_exec_inventory=True)
    translated = [output for event in function_events("exec", {"command": "Write-Output P114_C4_HOST_TOOL_INVENTORY"}, "exec_1", "call_exec_1") for output in translator.consume(event)]
    completed = [event["item"] for event in translated if event["type"] == "response.output_item.done"]
    assert [item["name"] for item in completed] == ["p114_exec"]
    assert completed[0]["type"] == "function_call"
    assert completed[0]["arguments"] == '{"operation":"inventory"}'
    assert translator.accepted_calls["call_exec_1"]["host_name"] == "p114_exec"


def test_mcp_inventory_forwards_tool_search_as_a_native_tool_search_call() -> None:
    translator = StreamTranslator(ROOT_PATH, mcp_inventory=True)
    translated = [output for event in function_events("tool_search", {"query": "p114_exec_probe p114_exec inventory", "limit": 1}, "search_1", "call_search_1") for output in translator.consume(event)]
    completed = [event["item"] for event in translated if event["type"] == "response.output_item.done"]
    assert completed == [
        {
            "type": "tool_search_call",
            "id": "search_1",
            "call_id": "call_search_1",
            "execution": "client",
            "arguments": {"query": "p114_exec_probe p114_exec inventory", "limit": 1},
        }
    ]
    assert translator.accepted_calls["call_search_1"]["name"] == "tool_search"


def test_mcp_inventory_forwards_exact_inventory_call_only() -> None:
    translator = StreamTranslator(ROOT_PATH, mcp_inventory=True)
    translated = [output for event in function_events(MCP_INVENTORY_TOOL_NAME, {"operation": "inventory"}, "mcp_1", "call_mcp_1") for output in translator.consume(event)]
    completed = [event["item"] for event in translated if event["type"] == "response.output_item.done"]
    assert [item["namespace"] for item in completed] == ["mcp__p114_exec_probe"]
    assert [item["name"] for item in completed] == ["p114_exec"]
    assert completed[0]["arguments"] == '{"operation":"inventory"}'
    assert translator.accepted_calls["call_mcp_1"]["name"] == MCP_INVENTORY_TOOL_NAME
    blocked = StreamTranslator(ROOT_PATH, mcp_inventory=True)
    assert [
        output
        for event in function_events(MCP_INVENTORY_TOOL_NAME, {"operation": "mutate"}, "mcp_2", "call_mcp_2")
        for output in blocked.consume(event)
    ] == [{"type": "response.error", "error": {"code": "malformed_provider_call", "message": "malformed_provider_call"}}]


def test_mcp_patch_forwards_exact_patch_call_only() -> None:
    translator = StreamTranslator(ROOT_PATH, mcp_inventory=True, mcp_operation="patch")
    translated = [output for event in function_events(MCP_INVENTORY_TOOL_NAME, {"operation": "patch"}, "mcp_1", "call_mcp_1") for output in translator.consume(event)]
    completed = [event["item"] for event in translated if event["type"] == "response.output_item.done"]
    assert [item["namespace"] for item in completed] == ["mcp__p114_exec_probe"]
    assert [item["name"] for item in completed] == ["p114_exec"]
    assert completed[0]["arguments"] == '{"operation":"patch"}'
    blocked = StreamTranslator(ROOT_PATH, mcp_inventory=True, mcp_operation="patch")
    assert [
        output
        for event in function_events(MCP_INVENTORY_TOOL_NAME, {"operation": "inventory"}, "mcp_2", "call_mcp_2")
        for output in blocked.consume(event)
    ] == [{"type": "response.error", "error": {"code": "malformed_provider_call", "message": "malformed_provider_call"}}]


def test_mcp_inventory_namespaced_host_history_round_trips_to_provider_flat_call() -> None:
    history = [
        {"type": "function_call", "id": "mcp_1", "call_id": "call_mcp_1", "namespace": "mcp__p114_exec_probe", "name": "p114_exec", "arguments": json.dumps({"operation": "inventory"})},
        {"type": "function_call_output", "call_id": "call_mcp_1", "output": "P114_MCP_EXEC_HANDLER_REACHED"},
    ]
    request = transform_request(
        {"input": history},
        ROOT_PATH,
        {"call_mcp_1": {"id": "mcp_1", "call_id": "call_mcp_1", "name": MCP_INVENTORY_TOOL_NAME, "provider_arguments": {"operation": "inventory"}}},
        mcp_inventory=True,
    )
    assert [item["type"] for item in request["input"]] == ["function_call", "function_call_output"]
    assert request["input"][0] == {
        "type": "function_call",
        "id": "mcp_1",
        "call_id": "call_mcp_1",
        "name": MCP_INVENTORY_TOOL_NAME,
        "arguments": json.dumps({"operation": "inventory"}, separators=(",", ":")),
    }
    assert request["input"][1] == history[1]


def test_mcp_patch_namespaced_host_history_round_trips_to_provider_flat_call() -> None:
    history = [
        {"type": "function_call", "id": "mcp_1", "call_id": "call_mcp_1", "namespace": "mcp__p114_exec_probe", "name": "p114_exec", "arguments": json.dumps({"operation": "patch"})},
        {"type": "function_call_output", "call_id": "call_mcp_1", "output": "P114_MCP_PATCH_HANDLER_REACHED"},
    ]
    request = transform_request(
        {"input": history},
        ROOT_PATH,
        {"call_mcp_1": {"id": "mcp_1", "call_id": "call_mcp_1", "name": MCP_INVENTORY_TOOL_NAME, "provider_arguments": {"operation": "patch"}}},
        mcp_inventory=True,
        mcp_operation="patch",
    )
    assert request["input"][0] == {
        "type": "function_call",
        "id": "mcp_1",
        "call_id": "call_mcp_1",
        "name": MCP_INVENTORY_TOOL_NAME,
        "arguments": json.dumps({"operation": "patch"}, separators=(",", ":")),
    }
    assert request["input"][1] == history[1]


def test_patch_via_exec_round_trips_the_host_exec_history_to_provider_patch() -> None:
    host_input = "const r = await tools.apply_patch(" + json.dumps(PATCH) + "); text(r);\n"
    history = [
        {"type": "custom_tool_call", "id": "patch_1", "call_id": "call_patch_1", "name": "exec", "input": host_input},
        {"type": "custom_tool_call_output", "call_id": "call_patch_1", "output": "ok"},
    ]
    request = transform_request({"input": history}, ROOT_PATH, {"call_patch_1": {"id": "patch_1", "call_id": "call_patch_1", "name": "apply_patch", "input": PATCH, "host_name": "exec", "host_input": host_input}})
    assert request["input"][0]["name"] == "apply_patch"
    assert json.loads(request["input"][0]["arguments"]) == {"patch": PATCH}


def test_continuation_keeps_tools_and_requires_known_output_call() -> None:
    history = [
        {"type": "custom_tool_call", "id": "exec_1", "call_id": "call_exec_1", "name": "exec", "input": "const r = await tools.shell_command({}); text(r);\n"},
        {"type": "custom_tool_call_output", "call_id": "call_exec_1", "output": "ok"},
    ]
    request = transform_request({"input": history}, ROOT_PATH, {"call_exec_1": {"id": "exec_1", "provider_arguments": {"command": "Get-Content allowed.txt"}}})
    assert [tool["name"] for tool in request["tools"]] == ["apply_patch", "exec"]
    assert [item["type"] for item in request["input"]] == ["function_call", "function_call_output"]
    assert json.loads(request["input"][0]["arguments"]) == {"command": "Get-Content allowed.txt"}
    with pytest.raises(AdapterError, match="history_round_trip_invalid"):
        transform_request({"input": [{"type": "custom_tool_call_output", "call_id": "unknown", "output": "no"}]}, ROOT_PATH)


def test_unsupported_provider_tool_fails_closed() -> None:
    translator = StreamTranslator(ROOT_PATH)
    output = translator.consume({"type": "response.output_item.added", "item": {"type": "function_call", "id": "bad_1", "call_id": "call_bad_1", "name": "web_search"}})
    assert output == [{"type": "response.error", "error": {"code": "unsupported_tool_or_event", "message": "unsupported_tool_or_event"}}]


def test_loopback_host_never_executes_provider_commands() -> None:
    text = (ROOT / "scripts" / "p114_capability_tool_adapter.py").read_text(encoding="utf-8")
    assert 'self.path not in {"/responses", "/v1/responses"}' in text
    assert "package_mcp_read_file=self.package_mcp_read_file" in text
    assert "ThreadingHTTPServer((\"127.0.0.1\", args.port)" in text
    assert "subprocess" not in text.casefold()


def test_role_bridge_scopes_the_temporary_provider_to_the_run_id() -> None:
    text = (ROOT / "scripts" / "enable_p114_c4_role_bridge.ps1").read_text(encoding="utf-8")
    assert "agent_workbench_ollama_p114_c4_role_' + ($RunId" in text


def test_role_bridge_changes_only_the_run_scoped_provider() -> None:
    text = (ROOT / "scripts" / "enable_p114_c4_role_bridge.ps1").read_text(encoding="utf-8")
    assert 'model_provider = "' + "' + $providerName + '" in text
    assert "default_permissions = \":danger-full-access\"" not in text


def test_bridge_can_strip_an_unsupported_cli_child_include_request() -> None:
    bridge = (ROOT / "scripts" / "enable_p114_c4_role_bridge.ps1").read_text(encoding="utf-8")
    adapter = (ROOT / "scripts" / "p114_capability_tool_adapter.py").read_text(encoding="utf-8")
    assert "[switch]$StripInclude" in bridge
    assert "--strip-include" in bridge
    assert 'translated["include"] = []' in adapter
    assert "[switch]$PatchViaExec" in bridge
    assert "--patch-via-exec" in adapter
    assert "[switch]$HostToolInventory" in bridge
    assert "--host-tool-inventory" in adapter
    assert "P114_C4_HOST_TOOL_INVENTORY_DONE" in bridge
    assert "[switch]$DynamicExecInventory" in bridge
    assert "--dynamic-exec-inventory" in adapter
    assert "P114_C4_DYNAMIC_EXEC_INHERITANCE_DONE" in bridge
    assert "[switch]$McpPatch" in bridge
    assert "--mcp-operation" in adapter
    assert "P114_C4_MCP_PATCH_DONE" in bridge
    assert "[switch]$McpInventory" in bridge
    assert "--mcp-inventory-route" in adapter
    assert "[switch]$PackageMcp" in bridge
    assert "--package-mcp-server" in bridge


def test_role_bridge_has_a_separate_package_mcp_exec_proof_mode() -> None:
    bridge = (ROOT / "scripts" / "enable_p114_c4_role_bridge.ps1").read_text(encoding="utf-8")
    assert "[switch]$PackageMcpExec" in bridge
    assert "$PackageMcp -or $PackageMcpExec" in bridge
    assert "$packageReadCommand = 'python -c" in bridge
    assert "--allow-exec-command', $packageReadCommand" in bridge
    assert "$packageWorkdir = if ($PackageMcpQualification)" in bridge
    assert "[switch]$PackageMcpQualification" in bridge
    assert "--allow-patch-path" in bridge
    assert "--allow-read-path" in bridge
    assert "p107_suite_provenance_audit_bundle_ticket.md" in bridge
    assert "p107_suite_provenance_audit_bundle_acceptance.py" in bridge
    assert "FILE_ABSENT is not a permission" in bridge
    assert "do not call exec until the two final validation commands" in bridge
    assert "Do not call ls, pip, echo, import checks" in bridge
    assert "create source_audit.py; add its import in the real" in bridge
    assert "parser.set_defaults(func=run_overview)" in bridge
    assert "workdir: $packageWorkdir" in bridge
    assert "P114_C4_PACKAGE_MCP_EXEC_DONE" in bridge
    assert "package_mcp_exec = [bool]$PackageMcpExec" in bridge


def test_role_bridge_has_a_grant_bound_package_mcp_composite_mode() -> None:
    bridge = (ROOT / "scripts" / "enable_p114_c4_role_bridge.ps1").read_text(encoding="utf-8")
    assert "[switch]$PackageMcpComposite" in bridge
    assert "$PackageMcp -or $PackageMcpExec -or $PackageMcpComposite" in bridge
    assert "--allow-exec-command', $packageValidationCommand" in bridge
    assert "--allow-patch-sha256" in bridge
    assert "P114_C4_PACKAGE_MCP_COMPOSITE_DONE" in bridge
    assert "package_mcp_composite = [bool]$PackageMcpComposite" in bridge


def test_role_bridge_has_a_grant_bound_package_mcp_battery_mode() -> None:
    bridge = (ROOT / "scripts" / "enable_p114_c4_role_bridge.ps1").read_text(encoding="utf-8")
    assert "[switch]$PackageMcpBattery" in bridge
    assert "$PackageMcp -or $PackageMcpExec -or $PackageMcpComposite -or $PackageMcpBattery" in bridge
    assert "$packageDefectValidationCommand" in bridge
    assert "$packageDefectPatch" in bridge
    assert "$packageRepairPatch" in bridge
    assert "$packageBatteryDefectPatch" in bridge
    assert "$packageBatteryRepairPatch" in bridge
    assert "P114_C4_PACKAGE_MCP_BATTERY_DONE" in bridge
    assert "battery = [bool]($Battery -or $PackageMcpBattery)" in bridge
    assert "package_mcp_battery = [bool]$PackageMcpBattery" in bridge


def test_role_bridge_has_a_declared_five_call_battery_mode() -> None:
    bridge = (ROOT / "scripts" / "enable_p114_c4_role_bridge.ps1").read_text(encoding="utf-8")
    assert "[switch]$Battery" in bridge
    assert "'--forced-tool', 'exec', '--forced-tool', 'apply_patch', '--forced-tool', 'exec', '--forced-tool', 'apply_patch', '--forced-tool', 'exec'" in bridge
    assert "exit 17" in bridge
    assert "P114_C4_BATTERY_DONE only." in bridge


def test_bridge_records_upstream_transport_outcomes_for_cli_children() -> None:
    bridge = (ROOT / "scripts" / "enable_p114_c4_role_bridge.ps1").read_text(encoding="utf-8")
    adapter = (ROOT / "scripts" / "p114_capability_tool_adapter.py").read_text(encoding="utf-8")
    assert "adapter_upstream.jsonl" in bridge
    assert 'parser.add_argument("--upstream-log", type=Path)' in adapter
    assert 'code = "upstream_empty_stream" if event_count == 0 else "upstream_incomplete_stream"' in adapter
    assert 'redirect_host=redirect.netloc if redirect else None' in adapter
    assert 'redirect_path=redirect.path if redirect else None' in adapter
    assert "if response.status >= 300:" in adapter
