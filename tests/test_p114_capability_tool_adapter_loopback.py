from __future__ import annotations

import http.client
import json
import socket
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "scripts" / "p114_capability_tool_adapter.py"
WORKTREE = "runtime/agent_jobs/p114_fixture/worktree"
PATCH = "*** Begin Patch\n*** Update File: runtime/agent_jobs/p114_fixture/worktree/allowed.txt\n@@\n-old\n+new\n*** End Patch"


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class ScriptedProvider(BaseHTTPRequestHandler):
    requests: list[dict] = []
    response_events: list[dict] = []

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def do_POST(self) -> None:
        body = self.rfile.read(int(self.headers["Content-Length"]))
        type(self).requests.append(json.loads(body.decode("utf-8")))
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        for event in type(self).response_events:
            self.wfile.write(f"event: {event['type']}\n".encode("utf-8"))
            self.wfile.write(b"data: " + json.dumps(event, separators=(",", ":")).encode("utf-8") + b"\n\n")
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()


def post_adapter(port: int, payload: dict) -> str:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    connection.request("POST", "/v1/responses", body=json.dumps(payload), headers={"Content-Type": "application/json"})
    response = connection.getresponse()
    assert response.status == 200
    text = response.read().decode("utf-8")
    connection.close()
    return text


def wait_for_adapter(port: int) -> None:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=0.2)
            connection.connect()
            connection.close()
            return
        except OSError:
            time.sleep(0.05)
    raise AssertionError("P114 loopback adapter did not start")


def test_loopback_process_preserves_multitool_history_without_live_provider(tmp_path: Path) -> None:
    ScriptedProvider.requests = []
    ScriptedProvider.response_events = [
        {"type": "response.output_item.added", "output_index": 0, "item": {"type": "function_call", "id": "exec_1", "call_id": "call_exec_1", "name": "exec"}},
        {"type": "response.function_call_arguments.done", "item_id": "exec_1", "arguments": json.dumps({"command": "Get-Content allowed.txt", "workdir": WORKTREE})},
        {"type": "response.output_item.done", "output_index": 0, "item": {"type": "function_call", "id": "exec_1"}},
        {"type": "response.output_item.added", "output_index": 1, "item": {"type": "function_call", "id": "patch_1", "call_id": "call_patch_1", "name": "apply_patch"}},
        {"type": "response.function_call_arguments.done", "item_id": "patch_1", "arguments": json.dumps({"patch": PATCH})},
        {"type": "response.output_item.done", "output_index": 1, "item": {"type": "function_call", "id": "patch_1"}},
    ]
    upstream = ThreadingHTTPServer(("127.0.0.1", 0), ScriptedProvider)
    upstream_port = int(upstream.server_address[1])
    import threading

    thread = threading.Thread(target=upstream.serve_forever, daemon=True)
    thread.start()
    adapter_port = free_port()
    process = subprocess.Popen(
        [
            sys.executable,
            str(ADAPTER),
            "--port",
            str(adapter_port),
            "--upstream",
            f"http://127.0.0.1:{upstream_port}/v1",
            "--allowed-root",
            WORKTREE,
            "--verdict-log",
            str(tmp_path / "verdicts.jsonl"),
            "--declared-command",
            "Get-Content allowed.txt",
            "--declared-workdir",
            WORKTREE,
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        wait_for_adapter(adapter_port)
        first = post_adapter(adapter_port, {"input": [{"type": "message", "role": "user", "content": "read then patch"}]})
        assert '"name":"exec"' in first and '"name":"apply_patch"' in first
        assert "tools.shell_command" in first
        assert PATCH.replace("\n", "\\n") in first
        forwarded = ScriptedProvider.requests[0]
        assert [tool["name"] for tool in forwarded["tools"]] == ["apply_patch", "exec"]
        assert forwarded["tool_choice"] == "auto"

        ScriptedProvider.response_events = []
        post_adapter(
            adapter_port,
            {
                "input": [
                    {"type": "custom_tool_call", "id": "exec_1", "call_id": "call_exec_1", "name": "exec", "input": "const r = await tools.shell_command({}); text(r);\n"},
                    {"type": "custom_tool_call_output", "call_id": "call_exec_1", "output": "read complete"},
                    {"type": "custom_tool_call", "id": "patch_1", "call_id": "call_patch_1", "name": "apply_patch", "input": PATCH},
                    {"type": "custom_tool_call_output", "call_id": "call_patch_1", "output": "patch complete"},
                    {"type": "message", "role": "user", "content": "repair: run the focused test"},
                ]
            },
        )
        continuation = ScriptedProvider.requests[1]
        assert [tool["name"] for tool in continuation["tools"]] == ["apply_patch", "exec"]
        assert [item["type"] for item in continuation["input"][:4]] == ["function_call", "function_call_output", "function_call", "function_call_output"]
        assert json.loads(continuation["input"][0]["arguments"])["command"] == "Get-Content allowed.txt"
        assert json.loads(continuation["input"][2]["arguments"]) == {"patch": PATCH}
    finally:
        process.terminate()
        process.wait(timeout=5)
        upstream.shutdown()
        upstream.server_close()
    assert process.returncode is not None
