import json
from pathlib import Path

from scripts.p116_in_session_mcp_server import InSessionP116Mcp


class FakeBroker:
    def __init__(self, _manifest: Path):
        self.timeout = None

    def wait_for_trigger(self, *, timeout: float):
        self.timeout = timeout
        return {"run_id": "p116_ui_test", "cursor_start_sequence": 0, "cursor_end_sequence": 1, "event_count": 1, "events": [{"sequence": 1, "kind": "tool_failed"}]}


class SequenceBroker:
    def __init__(self, _manifest: Path):
        self.calls = 0

    def wait_for_trigger(self, *, timeout: float):
        self.calls += 1
        start, end = self.calls - 1, self.calls
        return {"run_id": "p116_ui_sequence", "cursor_start_sequence": start, "cursor_end_sequence": end, "event_count": 1, "events": [{"sequence": end, "kind": "tool_completed"}]}


def call(server, name, arguments):
    response = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}})
    assert response is not None
    return response


def test_inventory_exposes_in_session_lifecycle_tools():
    server = InSessionP116Mcp(cursor_initializer=lambda **_: Path("cursor"))
    response = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert [tool["name"] for tool in response["result"]["tools"]] == ["supervision_start_run", "supervision_wait_delta", "supervision_acknowledge_delta", "supervision_close_run"]


def test_start_wait_close_binds_one_ui_coordinator_run(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    acknowledgements = []
    server = InSessionP116Mcp(broker_factory=FakeBroker, cursor_initializer=lambda **_: Path("cursor"), acknowledger=lambda **kwargs: acknowledgements.append(kwargs))
    started = call(server, "supervision_start_run", {"root": str(tmp_path), "worker_session_id": "worker-ui-1", "supervisor_session_id": "supervisor-ui-1", "run_id": "p116_ui_test"})
    assert json.loads(started["result"]["content"][0]["text"])["status"] == "active"
    manifest = tmp_path / "runtime" / "agent_jobs" / "p116_ui_test" / "supervision" / "manifest.json"
    assert json.loads(manifest.read_text(encoding="utf-8"))["worker_session_id"] == "worker-ui-1"
    waited = call(server, "supervision_wait_delta", {"timeout_ms": 250})
    assert json.loads(waited["result"]["content"][0]["text"])["event_count"] == 1
    pending = call(server, "supervision_wait_delta", {"timeout_ms": 250})
    assert pending["error"]["message"] == "BROKER_VALIDATION: pending delta must be acknowledged before another wait"
    acknowledged = call(server, "supervision_acknowledge_delta", {"classification": "blocked", "recommended_action": "nudge", "decision": "nudge", "evidence_summary": "safe failure review"})
    assert json.loads(acknowledged["result"]["content"][0]["text"])["last_sequence"] == 1
    assert acknowledgements[0]["last_sequence"] == 1
    closed = call(server, "supervision_close_run", {})
    assert json.loads(closed["result"]["content"][0]["text"])["status"] == "closed"
    assert not manifest.parent.joinpath("activation.json").exists()


def test_wait_refuses_before_the_ui_coordinator_binds_sessions():
    server = InSessionP116Mcp(cursor_initializer=lambda **_: Path("cursor"))
    response = call(server, "supervision_wait_delta", {"timeout_ms": 1})
    assert response["error"]["message"] == "BROKER_VALIDATION: no active supervision run"


def test_acknowledgement_unblocks_only_the_next_delta(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    acknowledgements = []
    server = InSessionP116Mcp(broker_factory=SequenceBroker, cursor_initializer=lambda **_: Path("cursor"), acknowledger=lambda **kwargs: acknowledgements.append(kwargs))
    call(server, "supervision_start_run", {"root": str(tmp_path), "worker_session_id": "worker-ui-2", "supervisor_session_id": "supervisor-ui-2", "run_id": "p116_ui_sequence"})
    first = json.loads(call(server, "supervision_wait_delta", {"timeout_ms": 1})["result"]["content"][0]["text"])
    call(server, "supervision_acknowledge_delta", {"classification": "productive_repair", "recommended_action": "continue", "decision": "continue", "evidence_summary": "first delta reviewed"})
    second = json.loads(call(server, "supervision_wait_delta", {"timeout_ms": 1})["result"]["content"][0]["text"])
    assert (first["cursor_start_sequence"], first["cursor_end_sequence"]) == (0, 1)
    assert (second["cursor_start_sequence"], second["cursor_end_sequence"]) == (1, 2)
    assert [item["last_sequence"] for item in acknowledgements] == [1]


def test_start_rejects_internal_policy_and_leaves_no_stale_run_directory(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    server = InSessionP116Mcp(broker_factory=FakeBroker, cursor_initializer=lambda **_: Path("cursor"))
    result = call(server, "supervision_start_run", {"root": str(tmp_path), "worker_session_id": "worker-ui-3", "supervisor_session_id": "supervisor-ui-3", "run_id": "p116_ui_policy", "diagnostic_policy": {}})
    assert result["error"]["message"] == "BROKER_VALIDATION: invalid start arguments"
    assert not (tmp_path / "runtime" / "agent_jobs" / "p116_ui_policy").exists()


def test_start_rolls_back_run_directory_when_cursor_initialization_fails(tmp_path: Path):
    (tmp_path / ".git").mkdir()

    def missing_transcript(**_):
        raise ValueError("Worker session transcript is not discoverable before activation")

    server = InSessionP116Mcp(broker_factory=FakeBroker, cursor_initializer=missing_transcript)
    result = call(server, "supervision_start_run", {"root": str(tmp_path), "worker_session_id": "worker-ui-4", "supervisor_session_id": "supervisor-ui-4", "run_id": "p116_ui_retry"})
    assert result["error"]["message"] == "BROKER_VALIDATION: Worker session transcript is not discoverable before activation"
    assert not (tmp_path / "runtime" / "agent_jobs" / "p116_ui_retry" / "supervision").exists()
