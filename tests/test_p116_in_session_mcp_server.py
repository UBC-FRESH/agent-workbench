import json
from pathlib import Path

from scripts.p116_in_session_mcp_server import InSessionP116Mcp


class FakeBroker:
    def __init__(self, _manifest: Path):
        self.timeout = None

    def wait_for_trigger(self, *, timeout: float):
        self.timeout = timeout
        return {"run_id": "p116_ui_test", "event_count": 1, "events": [{"sequence": 1, "kind": "tool_failed"}]}


def call(server, name, arguments):
    response = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}})
    assert response is not None
    return response


def test_inventory_exposes_in_session_lifecycle_tools():
    server = InSessionP116Mcp(cursor_initializer=lambda **_: Path("cursor"))
    response = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert [tool["name"] for tool in response["result"]["tools"]] == ["supervision_start_run", "supervision_wait_delta", "supervision_close_run"]


def test_start_wait_close_binds_one_ui_coordinator_run(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    server = InSessionP116Mcp(broker_factory=FakeBroker, cursor_initializer=lambda **_: Path("cursor"))
    started = call(server, "supervision_start_run", {"root": str(tmp_path), "worker_session_id": "worker-ui-1", "supervisor_session_id": "supervisor-ui-1", "run_id": "p116_ui_test"})
    assert json.loads(started["result"]["content"][0]["text"])["status"] == "active"
    manifest = tmp_path / "runtime" / "agent_jobs" / "p116_ui_test" / "supervision" / "manifest.json"
    assert json.loads(manifest.read_text(encoding="utf-8"))["worker_session_id"] == "worker-ui-1"
    waited = call(server, "supervision_wait_delta", {"timeout_ms": 250})
    assert json.loads(waited["result"]["content"][0]["text"])["event_count"] == 1
    closed = call(server, "supervision_close_run", {})
    assert json.loads(closed["result"]["content"][0]["text"])["status"] == "closed"
    assert not manifest.parent.joinpath("activation.json").exists()


def test_wait_refuses_before_the_ui_coordinator_binds_sessions():
    server = InSessionP116Mcp(cursor_initializer=lambda **_: Path("cursor"))
    response = call(server, "supervision_wait_delta", {"timeout_ms": 1})
    assert response["error"]["message"] == "BROKER_VALIDATION"
