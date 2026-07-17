from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_workbench.p113_function_tool_adapter import AdapterError
from agent_workbench.p114_capability_tool_adapter import StreamTranslator, parse_provider_call, transform_request


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
    assert "transform_request(payload, self.allowed_root, self.validated_calls)" in text
    assert "ThreadingHTTPServer((\"127.0.0.1\", args.port)" in text
    assert "subprocess" not in text.casefold()
