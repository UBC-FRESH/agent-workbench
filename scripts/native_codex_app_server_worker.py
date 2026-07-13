"""Run bounded remote-Ollama Worker tickets through one native Codex app-server.

The host owns result-file writes.  Worker turns are read-only and use approval
policy ``never``; a model request outside that boundary fails instead of
showing a Windows approval dialog.  ``--serve`` keeps one app-server process
alive for sequential ticket jobs so the Windows sandbox is not relaunched per
ticket.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

from native_codex_app_server_sandbox import AppServer


def runtime_path(repo_root: Path, value: str, kind: str) -> Path:
    root = (repo_root / "runtime" / "agent_jobs").resolve()
    candidate = (repo_root / value).resolve()
    if root not in candidate.parents and candidate != root:
        raise ValueError(f"{kind} must be below runtime/agent_jobs")
    return candidate


def run_ticket(
    server: AppServer,
    repo_root: Path,
    ticket_path: Path,
    output_path: Path,
    model: str,
    provider: str,
    idle_timeout_seconds: float,
    event_sink: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    prompt = ticket_path.read_text(encoding="utf-8")
    thread = server.request(
        "thread/start",
        {
            "cwd": str(repo_root),
            "model": model,
            "modelProvider": provider,
            "approvalPolicy": "never",
            "sandbox": "read-only",
            "ephemeral": True,
            "developerInstructions": (
                "You are a bounded Worker. Do not call tools, edit files, or request permissions. "
                "Return only the ticket result."
            ),
        },
    )
    thread_id = thread["thread"]["id"]
    server.request(
        "turn/start",
        {"threadId": thread_id, "input": [{"type": "text", "text": prompt}]},
    )

    fragments: list[str] = []
    status = "unknown"
    while True:
        message = server.next_message(timeout_seconds=idle_timeout_seconds)
        method = message.get("method")
        params = message.get("params", {})
        if event_sink is not None and method:
            event: dict[str, Any] = {"event": "app_server", "method": method}
            if method == "item/agentMessage/delta" and isinstance(params, dict):
                delta = params.get("delta")
                if isinstance(delta, str):
                    event = {"event": "assistant_delta", "text": delta}
            event_sink(event)
        item = params.get("item", {}) if isinstance(params, dict) else {}
        if item.get("type") in {"agentMessage", "assistantMessage"}:
            text = item.get("text") or item.get("content")
            if isinstance(text, str):
                fragments.append(text)
        if method == "turn/completed":
            status = str(params.get("status", "completed"))
            break

    result = "\n".join(fragments).strip()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result + "\n", encoding="utf-8")
    return {
        "status": status,
        "thread_id": thread_id,
        "model_provider": thread["modelProvider"],
        "sandbox": thread["sandbox"],
        "approval_policy": thread["approvalPolicy"],
        "output": str(output_path),
    }


def parse_job(raw: str, repo_root: Path) -> tuple[Path, Path]:
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("job must be a JSON object")
    ticket = data.get("ticket")
    output = data.get("output")
    if not isinstance(ticket, str) or not isinstance(output, str):
        raise ValueError("job must provide string ticket and output paths")
    ticket_path = runtime_path(repo_root, ticket, "ticket")
    output_path = runtime_path(repo_root, output, "output")
    if not ticket_path.is_file():
        raise ValueError(f"ticket does not exist: {ticket}")
    return ticket_path, output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticket", help="ignored runtime ticket path for one job")
    parser.add_argument("--output", help="ignored runtime output path for one job")
    parser.add_argument("--serve", action="store_true", help="read sequential JSON jobs from stdin")
    parser.add_argument("--model", default="qwen3-coder:latest")
    parser.add_argument("--provider", default="agent_workbench_ollama")
    parser.add_argument("--idle-timeout-seconds", type=float, default=30.0)
    parser.add_argument("--stream-events", action="store_true", help="write live app-server events as JSONL")
    args = parser.parse_args()
    if args.serve == (bool(args.ticket) and bool(args.output)):
        parser.error("supply --serve or both --ticket and --output")

    repo_root = Path(__file__).resolve().parents[1]
    try:
        with AppServer() as server:
            server.initialize()
            readiness = server.request("windowsSandbox/readiness")
            if readiness["status"] != "ready":
                raise RuntimeError(f"Windows sandbox is not ready: {readiness['status']}")
            def emit(event: dict[str, Any]) -> None:
                if args.stream_events:
                    print(json.dumps(event, sort_keys=True), flush=True)

            if args.serve:
                for raw in sys.stdin:
                    if not raw.strip():
                        continue
                    try:
                        ticket, output = parse_job(raw, repo_root)
                        result = run_ticket(server, repo_root, ticket, output, args.model, args.provider, args.idle_timeout_seconds, emit)
                        print(json.dumps({"ok": True, **result}, sort_keys=True), flush=True)
                    except (OSError, RuntimeError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
                        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True), flush=True)
                return 0
            ticket, output = parse_job(json.dumps({"ticket": args.ticket, "output": args.output}), repo_root)
            print(json.dumps(run_ticket(server, repo_root, ticket, output, args.model, args.provider, args.idle_timeout_seconds, emit), sort_keys=True))
            return 0
    except (OSError, RuntimeError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
