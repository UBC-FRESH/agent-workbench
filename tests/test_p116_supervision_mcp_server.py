import json
from pathlib import Path

from scripts.p116_supervision_mcp_server import P116SupervisionMcp


class FakeBroker:
    def __init__(self, result=None, error=None): self.result, self.error, self.timeout = result, error, None
    def wait_for_trigger(self, *, timeout):
        self.timeout = timeout
        if self.error: raise self.error
        return self.result


def test_tool_inventory():
    response = P116SupervisionMcp(Path("unused"), broker=FakeBroker()).handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert [tool["name"] for tool in response["result"]["tools"]] == ["supervision_wait_delta"]


def test_successful_delta_is_text():
    delta = {"schema_version": "p116_supervision_v1", "run_id": "run-1", "event_count": 1, "events": [{"kind": "tool_failed", "sequence": 1}]}
    broker = FakeBroker(delta)
    response = P116SupervisionMcp(Path("unused"), broker=broker).handle({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "supervision_wait_delta", "arguments": {"timeout_ms": 250}}})
    assert json.loads(response["result"]["content"][0]["text"]) == delta and broker.timeout == 0.25


def test_standard_mcp_metadata_is_ignored_without_relaxing_tool_validation():
    delta = {"schema_version": "p116_supervision_v1", "run_id": "run-1", "event_count": 1, "events": [{"kind": "tool_failed", "sequence": 1}]}
    response = P116SupervisionMcp(Path("unused"), broker=FakeBroker(delta)).handle(
        {"id": 2, "method": "tools/call", "params": {"name": "supervision_wait_delta", "arguments": {"timeout_ms": 250}, "_meta": {"progressToken": "opaque"}}}
    )
    assert json.loads(response["result"]["content"][0]["text"]) == delta


def test_timeout_error_is_categorical_and_redacted():
    response = P116SupervisionMcp(Path("C:/private/manifest.json"), broker=FakeBroker(error=TimeoutError("secret path"))).handle({"id": 3, "method": "tools/call", "params": {"name": "supervision_wait_delta", "arguments": {"timeout_ms": 1}}})
    assert response["error"]["message"] == "BROKER_TIMEOUT" and "private" not in json.dumps(response)


def test_invalid_arguments_return_safe_error():
    response = P116SupervisionMcp(Path("unused"), broker=FakeBroker()).handle({"id": 4, "method": "tools/call", "params": {"name": "other", "arguments": {"timeout_ms": 0}}})
    assert response["error"]["message"] == "INVALID_TOOL"
