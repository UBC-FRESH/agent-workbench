from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

from agent_workbench.agent_bridge.mcp_server import (
    APPLY_PATCH_TOOL_NAME,
    EXEC_TOOL_NAME,
    READ_FILE_TOOL_NAME,
    AgentBridgeMcpServer,
    RunGrant,
    ToolOutcome,
    handle_json_line,
    main,
    serve_jsonl,
    sha256_text,
)


def make_server(
    tmp_path: Path,
    *,
    allowed_exec_commands: frozenset[str] = frozenset(),
    allowed_patch_sha256: frozenset[str] = frozenset(),
    allowed_patch_paths: frozenset[str] = frozenset(),
    allowed_read_paths: frozenset[str] = frozenset(),
):
    calls: list[tuple[str, object]] = []

    def exec_handler(command: str, workdir: Path, timeout_ms: int) -> ToolOutcome:
        calls.append(("exec", {"command": command, "workdir": workdir, "timeout_ms": timeout_ms}))
        return ToolOutcome(text="EXEC_OK", metadata={"exit_code": 0})

    def patch_handler(patch: str, root: Path) -> ToolOutcome:
        calls.append(("apply_patch", {"patch": patch, "root": root}))
        return ToolOutcome(text="PATCH_OK", metadata={"changed": True})

    server = AgentBridgeMcpServer(
        RunGrant(
            run_id="test_run",
            root=tmp_path,
            allowed_exec_commands=allowed_exec_commands,
            allowed_patch_sha256=allowed_patch_sha256,
            allowed_patch_paths=allowed_patch_paths,
            allowed_read_paths=allowed_read_paths,
        ),
        event_log_path=tmp_path / "events.jsonl",
        exec_handler=exec_handler,
        apply_patch_handler=patch_handler,
    )
    return server, calls


def call_tool(server: AgentBridgeMcpServer, request_id: int, name: str, arguments: dict[str, object]) -> dict[str, object]:
    reply = server.handle({"jsonrpc": "2.0", "id": request_id, "method": "tools/call", "params": {"name": name, "arguments": arguments}})
    assert reply is not None
    return reply


def result_text(reply: dict[str, object]) -> str:
    result = reply["result"]
    assert isinstance(result, dict)
    content = result["content"]
    assert isinstance(content, list)
    first = content[0]
    assert isinstance(first, dict)
    text = first["text"]
    assert isinstance(text, str)
    return text


def is_error(reply: dict[str, object]) -> bool:
    result = reply["result"]
    assert isinstance(result, dict)
    value = result["isError"]
    assert isinstance(value, bool)
    return value


def test_agent_bridge_mcp_server_lists_separate_exec_and_apply_patch_tools(tmp_path: Path) -> None:
    server, _calls = make_server(tmp_path)
    initialize = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    listed = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})

    assert initialize is not None
    assert initialize["result"]["serverInfo"]["name"] == "agent-workbench-bridge"  # type: ignore[index]
    assert listed is not None
    tools = listed["result"]["tools"]  # type: ignore[index]
    assert [tool["name"] for tool in tools] == [EXEC_TOOL_NAME, APPLY_PATCH_TOOL_NAME]
    assert tools[0]["inputSchema"]["required"] == ["command"]
    assert tools[1]["inputSchema"]["required"] == ["patch"]
    assert server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


def test_read_file_schema_is_exposed_only_when_read_paths_are_granted(tmp_path: Path) -> None:
    server, _calls = make_server(tmp_path, allowed_read_paths=frozenset({"src/allowed.py"}))
    listed = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    assert listed is not None
    assert [tool["name"] for tool in listed["result"]["tools"]] == [EXEC_TOOL_NAME, APPLY_PATCH_TOOL_NAME, READ_FILE_TOOL_NAME]  # type: ignore[index]


def test_exec_is_denied_by_default_and_does_not_invoke_handler(tmp_path: Path) -> None:
    server, calls = make_server(tmp_path)
    reply = call_tool(server, 1, EXEC_TOOL_NAME, {"command": "python -V"})

    assert is_error(reply) is True
    assert result_text(reply) == "policy_denied:command_not_granted"
    assert calls == []


def test_allowed_exec_invokes_handler_and_logs_decision(tmp_path: Path) -> None:
    server, calls = make_server(tmp_path, allowed_exec_commands=frozenset({"python -V"}))
    reply = call_tool(server, 1, EXEC_TOOL_NAME, {"command": "python -V", "workdir": ".", "timeout_ms": 1000})

    assert is_error(reply) is False
    assert result_text(reply) == "EXEC_OK"
    assert calls[0][0] == "exec"
    records = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    assert any(record["kind"] == "policy_decision" and record["decision"] == "allow" for record in records)
    assert any(record["kind"] == "tool_outcome" and record["tool"] == EXEC_TOOL_NAME for record in records)


def test_exec_rejects_workdir_outside_granted_root(tmp_path: Path) -> None:
    server, calls = make_server(tmp_path, allowed_exec_commands=frozenset({"python -V"}))
    outside = tmp_path.parent
    reply = call_tool(server, 1, EXEC_TOOL_NAME, {"command": "python -V", "workdir": str(outside)})

    assert is_error(reply) is True
    assert result_text(reply) == "policy_denied:workdir_outside_root"
    assert calls == []


def test_apply_patch_is_denied_by_default_and_allowed_by_hash(tmp_path: Path) -> None:
    target = tmp_path / "target.txt"
    target.write_text("before\n", encoding="utf-8", newline="")
    patch = "*** Begin Patch\n*** Update File: target.txt\n@@\n-before\n+after\n*** End Patch"
    server, calls = make_server(tmp_path)
    denied = call_tool(server, 1, APPLY_PATCH_TOOL_NAME, {"patch": patch})
    assert is_error(denied) is True
    assert result_text(denied) == "policy_denied:patch_not_granted"
    assert calls == []

    server, calls = make_server(tmp_path, allowed_patch_sha256=frozenset({sha256_text(patch)}))
    allowed = call_tool(server, 2, APPLY_PATCH_TOOL_NAME, {"patch": patch})
    assert is_error(allowed) is False
    assert result_text(allowed) == "PATCH_OK"
    assert calls[0][0] == "apply_patch"


def test_task_specific_patch_paths_and_read_paths_are_contained(tmp_path: Path) -> None:
    target = tmp_path / "src" / "allowed.py"
    target.parent.mkdir()
    target.write_text("before\n", encoding="utf-8", newline="")
    patch = "*** Begin Patch\n*** Update File: src/allowed.py\n@@\n-before\n+after\n*** End Patch"
    server, calls = make_server(
        tmp_path,
        allowed_patch_paths=frozenset({"src/allowed.py"}),
        allowed_read_paths=frozenset({"src/allowed.py"}),
    )
    patch_reply = call_tool(server, 1, APPLY_PATCH_TOOL_NAME, {"patch": patch})
    read_reply = call_tool(server, 2, READ_FILE_TOOL_NAME, {"path": "src/allowed.py"})
    denied = call_tool(server, 3, READ_FILE_TOOL_NAME, {"path": "../outside.txt"})

    assert is_error(patch_reply) is False
    assert calls[0][0] == "apply_patch"
    assert is_error(read_reply) is False
    assert result_text(read_reply) == "before\n"
    assert is_error(denied) is True
    assert result_text(denied) == "policy_denied:path_not_granted"


def test_declared_but_absent_read_target_is_a_non_policy_result(tmp_path: Path) -> None:
    server, _calls = make_server(tmp_path, allowed_read_paths=frozenset({"src/new_file.py"}))

    reply = call_tool(server, 1, READ_FILE_TOOL_NAME, {"path": "src/new_file.py"})

    assert is_error(reply) is False
    assert result_text(reply) == "FILE_ABSENT:src/new_file.py"


def test_read_file_returns_only_the_requested_declared_line_range(tmp_path: Path) -> None:
    target = tmp_path / "src" / "allowed.py"
    target.parent.mkdir()
    target.write_text("one\ntwo\nthree\n", encoding="utf-8", newline="")
    server, _calls = make_server(tmp_path, allowed_read_paths=frozenset({"src/allowed.py"}))

    reply = call_tool(server, 1, READ_FILE_TOOL_NAME, {"path": "src/allowed.py", "start_line": 2, "end_line": 3})

    assert is_error(reply) is False
    assert result_text(reply) == "two\nthree\n"


def test_malformed_calls_return_jsonrpc_errors(tmp_path: Path) -> None:
    server, _calls = make_server(tmp_path)
    bad_args = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": EXEC_TOOL_NAME}})
    missing = server.handle({"jsonrpc": "2.0", "id": 2, "method": "missing"})

    assert bad_args is not None
    assert bad_args["error"]["code"] == -32602  # type: ignore[index]
    assert missing is not None
    assert missing["error"]["code"] == -32601  # type: ignore[index]


def test_jsonl_stdio_helper_handles_invalid_json_and_notifications(tmp_path: Path) -> None:
    server, _calls = make_server(tmp_path)
    invalid = handle_json_line(server, "not json\n")
    assert invalid is not None
    assert invalid["error"]["code"] == -32700  # type: ignore[index]

    output = StringIO()
    serve_jsonl(
        server,
        StringIO(
            "\n".join(
                [
                    json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"}),
                    json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
                    json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
                    "",
                ]
            )
        ),
        output,
    )
    replies = [json.loads(line) for line in output.getvalue().splitlines()]
    assert [reply["id"] for reply in replies] == [1, 2]


def test_package_mcp_stdio_main_smoke_allows_granted_exec(tmp_path: Path, monkeypatch) -> None:
    stdin = StringIO(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": EXEC_TOOL_NAME, "arguments": {"command": "python -V"}}}) + "\n")
    stdout = StringIO()
    monkeypatch.setattr("sys.stdin", stdin)
    monkeypatch.setattr("sys.stdout", stdout)

    assert main(["--run-id", "stdio_smoke", "--root", str(tmp_path), "--allow-exec-command", "python -V"]) == 0
    replies = [json.loads(line) for line in stdout.getvalue().splitlines()]
    assert replies[0]["result"]["isError"] is False
    assert json.loads(replies[0]["result"]["content"][0]["text"])["exit_code"] == 0


def test_package_mcp_stdio_main_smoke_applies_granted_patch(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "target.txt"
    target.write_text("before\n", encoding="utf-8", newline="")
    patch = "*** Begin Patch\n*** Update File: target.txt\n@@\n-before\n+after\n*** End Patch"
    stdin = StringIO(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": APPLY_PATCH_TOOL_NAME, "arguments": {"patch": patch}},
            }
        )
        + "\n"
    )
    stdout = StringIO()
    monkeypatch.setattr("sys.stdin", stdin)
    monkeypatch.setattr("sys.stdout", stdout)

    assert main(["--run-id", "stdio_patch_smoke", "--root", str(tmp_path), "--allow-patch-sha256", sha256_text(patch)]) == 0
    replies = [json.loads(line) for line in stdout.getvalue().splitlines()]
    assert replies[0]["result"]["isError"] is False
    assert replies[0]["result"]["content"][0]["text"] == "PATCH_OK"
    assert target.read_text(encoding="utf-8") == "after\n"
