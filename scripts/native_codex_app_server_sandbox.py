"""Inspect or explicitly provision the native Codex Windows sandbox once.

This helper talks JSON-RPC to one local ``codex app-server`` process.  It does
not contact an LLM provider and it does not start a Worker.  The default action
only reports the sandbox readiness.  ``--setup`` deliberately requires an
operator's explicit invocation because Windows may request elevation once while
installing the durable sandbox components.
"""

from __future__ import annotations

import argparse
import json
import queue
import subprocess
import sys
import threading
from collections.abc import Iterator
from typing import Any


class AppServer:
    def __init__(self) -> None:
        self.process = subprocess.Popen(
            [
                "codex",
                "app-server",
                "--stdio",
                "-c",
                'default_permissions="agent_workbench_ollama_readonly"',
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
        self._next_id = 1
        self._messages: queue.Queue[dict[str, Any]] = queue.Queue()
        self._reader = threading.Thread(target=self._read_messages, daemon=True)
        self._reader.start()

    def __enter__(self) -> "AppServer":
        if self.process.stdin is None or self.process.stdout is None:
            raise RuntimeError("native Codex app-server did not expose stdio")
        return self

    def __exit__(self, *_: object) -> None:
        self.process.terminate()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=10)

    def _read_messages(self) -> None:
        assert self.process.stdout is not None
        while line := self.process.stdout.readline():
            try:
                self._messages.put(json.loads(line))
            except json.JSONDecodeError:
                continue

    def messages(self) -> Iterator[dict[str, Any]]:
        while True:
            yield self.next_message()

    def next_message(self, timeout_seconds: float | None = None) -> dict[str, Any]:
        try:
            return self._messages.get(timeout=timeout_seconds)
        except queue.Empty as exc:
            raise TimeoutError(f"no app-server event for {timeout_seconds:g} seconds") from exc

    def request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        assert self.process.stdin is not None
        request_id = self._next_id
        self._next_id += 1
        message: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            message["params"] = params
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()
        while True:
            response = self.next_message(timeout_seconds=30)
            if response.get("id") != request_id:
                continue
            if "error" in response:
                raise RuntimeError(f"{method} failed: {response['error']}")
            return response["result"]
        stderr = self.process.stderr.read() if self.process.stderr else ""
        raise RuntimeError(f"app-server stopped before responding to {method}: {stderr[-1000:]}")

    def initialize(self) -> dict[str, Any]:
        return self.request(
            "initialize",
            {
                "clientInfo": {"name": "agent-workbench-sandbox", "version": "0.1"},
                "capabilities": {"experimentalApi": True},
            },
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--setup",
        action="store_true",
        help="start the one-time Windows sandbox setup; omitted by default",
    )
    parser.add_argument(
        "--mode",
        choices=("unelevated", "elevated"),
        default="unelevated",
        help="one-time setup mode when --setup is supplied",
    )
    parser.add_argument("--cwd", help="optional absolute workspace path for setup")
    args = parser.parse_args()

    try:
        with AppServer() as server:
            initialized = server.initialize()
            before = server.request("windowsSandbox/readiness")
            result: dict[str, Any] = {"before": before["status"], "setup_started": False}
            if args.setup and before["status"] != "ready":
                setup_params: dict[str, Any] = {"mode": args.mode}
                if args.cwd:
                    setup_params["cwd"] = args.cwd
                response = server.request("windowsSandbox/setupStart", setup_params)
                result["setup_started"] = response["started"]
            result["platform"] = initialized["platformOs"]
            print(json.dumps(result, sort_keys=True))
            return 0
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
