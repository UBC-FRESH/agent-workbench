from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_workbench.p113_function_tool_adapter import StreamTranslator, transform_request


FIXTURE = ROOT / "benchmarks" / "p113_function_tool_adapter" / "adapter_contract_fixtures.json"


def fixtures() -> tuple[str, dict[str, dict]]:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return data["allowed_root"], {case["id"]: case for case in data["cases"]}


def stream(call: dict) -> list[dict]:
    arguments = call["arguments"]
    return [
        {"type": "response.output_item.added", "output_index": 0, "item": {"type": "function_call", "id": call["id"], "call_id": call["call_id"], "name": call["name"]}},
        {"type": "response.function_call_arguments.done", "item_id": call["id"], "arguments": arguments},
        {"type": "response.output_item.done", "output_index": 0, "item": {"type": "function_call", "id": call["id"]}},
    ]


def test_valid_fixture_translates_one_call() -> None:
    root, cases = fixtures()
    translator = StreamTranslator(root)
    call_events = stream(cases["valid_translation"]["provider_calls"][0])
    added = translator.consume(call_events[0])
    assert added[0]["item"]["input"] == ""
    events = [*added, *(output for event in call_events[1:] for output in translator.consume(event))]
    assert [event["type"] for event in events] == ["response.output_item.added", "response.custom_tool_call_input.delta", "response.custom_tool_call_input.done", "response.output_item.done"]
    assert events[0]["item"]["id"] == "fc_valid"
    assert events[-1]["item"]["call_id"] == "call_valid"


def test_call_limit_and_containment_fail_before_custom_input_completion() -> None:
    root, cases = fixtures()
    translator = StreamTranslator(root)
    first = stream(cases["one_call_limit"]["provider_calls"][0])[:1]
    second = stream(cases["one_call_limit"]["provider_calls"][1])[:1]
    assert translator.consume(first[0])[0]["type"] == "response.output_item.added"
    assert translator.consume(second[0])[0]["error"]["code"] == "call_limit_exceeded"
    escaped = StreamTranslator(root)
    events = [output for event in stream(cases["allowed_root_containment"]["provider_calls"][0]) for output in escaped.consume(event)]
    assert events[-1] == {"type": "response.error", "error": {"code": "path_outside_allowed_root", "message": "path_outside_allowed_root"}}
    assert "response.custom_tool_call_input.done" not in [event["type"] for event in events]


def test_malformed_provider_output_and_history_round_trip() -> None:
    root, cases = fixtures()
    bad = StreamTranslator(root)
    events = [output for event in stream(cases["malformed_provider_output"]["provider_calls"][0]) for output in bad.consume(event)]
    assert events[-1]["error"]["code"] == "malformed_provider_call"
    assert "response.custom_tool_call_input.done" not in [event["type"] for event in events]
    history = cases["history_round_trip"]["custom_history"]
    request = transform_request({"input": [{"type": "message", "role": "user", "content": "patch"}, *history], "reasoning": {"effort": "low"}}, root)
    assert request["tools"] == [] and request["tool_choice"] == "none" and "reasoning" not in request
    assert [item["type"] for item in request["input"][-2:]] == ["function_call", "function_call_output"]
    assert request["input"][-2]["id"] == "fc_history"
    output_only = cases["output_only_history"]["custom_history"]
    request = transform_request({"input": output_only}, root, {"call_output_only": {"id": "fc_output_only"}})
    assert request["input"] == [{"type": "function_call_output", "call_id": "call_output_only", "output": "unsupported custom tool call: apply_patch"}]
    replay = [history[0], history[1], history[0], history[1]]
    request = transform_request({"input": replay}, root)
    assert [item["type"] for item in request["input"]] == ["function_call", "function_call_output", "function_call", "function_call_output"]
    idless = [dict(history[0], id=None), history[1]]
    request = transform_request({"input": idless}, root, {"call_history": {"id": "fc_history"}})
    assert request["input"][0]["id"] == "fc_history"


def test_loopback_host_remains_a_single_tool_adapter() -> None:
    text = (ROOT / "scripts" / "p113_apply_patch_function_adapter.py").read_text(encoding="utf-8")
    assert 'self.path not in {"/responses", "/v1/responses"}' in text
    assert "transform_request(payload, self.allowed_root, self.validated_calls)" in text
    assert "StreamTranslator(self.allowed_root)" in text
    assert "ThreadingHTTPServer((\"127.0.0.1\", args.port)" in text
    assert "subprocess" not in text.casefold()
