"""Run a bounded no-modal Supervisor-authored ticket -> Worker -> verification proof.

The native Supervisor uses one restricted app-server shell action to create an
ignored Worker ticket.  The Coordinator relays that ticket to the persistent
Responses Worker host, then a fresh native Supervisor turn independently reads
and verifies the result.  This proves Supervisor-owned ticket authorship; it
does not claim that the Supervisor directly launched the Worker host.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from native_codex_app_server_sandbox import AppServer
from ollama_responses_worker_host import run_ticket


def supervisor_turn(
    server: AppServer,
    repo_root: Path,
    prompt: str,
    sandbox_policy: dict[str, Any],
    model: str,
) -> tuple[str, list[dict[str, Any]]]:
    thread = server.request(
        "thread/start",
        {
            "cwd": str(repo_root),
            "model": model,
            "modelProvider": "agent_workbench_ollama",
            "approvalPolicy": "never",
            "sandbox": "read-only",
            "ephemeral": True,
            "developerInstructions": "You are a bounded Supervisor. Use only the exact requested shell action.",
        },
    )
    thread_id = thread["thread"]["id"]
    server.request(
        "turn/start",
        {"threadId": thread_id, "input": [{"type": "text", "text": prompt}], "sandboxPolicy": sandbox_policy},
    )
    final: list[str] = []
    evidence: list[dict[str, Any]] = []
    while True:
        message = server.next_message(timeout_seconds=30)
        method = message.get("method")
        params = message.get("params", {})
        item = params.get("item", {}) if isinstance(params, dict) else {}
        if method == "item/completed" and item.get("type") == "commandExecution":
            evidence.append(
                {
                    "command": item.get("command"),
                    "exit_code": item.get("exitCode"),
                    "output": item.get("aggregatedOutput") or item.get("aggregated_output"),
                }
            )
        if item.get("type") in {"agentMessage", "assistantMessage"} and isinstance(item.get("text"), str):
            final.append(item["text"])
        if method == "turn/completed":
            return "\n".join(final).strip(), evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model", default="qwen3-coder:latest", help="Supervisor model")
    parser.add_argument(
        "--worker-model",
        default="qwen3.6:35b-a3b-bf16",
        help="Worker model",
    )
    args = parser.parse_args()
    if not args.run_id.replace("-", "").replace("_", "").isalnum():
        parser.error("--run-id may contain only letters, digits, hyphens, and underscores")

    repo_root = Path(__file__).resolve().parents[1]
    run_dir = repo_root / "runtime" / "agent_jobs" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    ticket = run_dir / "worker_ticket.md"
    worker_output = run_dir / "worker_output.txt"
    dispatch_marker = "P102_HYBRID_DISPATCH"
    worker_marker = "P102_HYBRID_WORKER"
    verify_marker = "P102_HYBRID_VERIFIED"

    try:
        with AppServer() as server:
            server.initialize()
            readiness = server.request("windowsSandbox/readiness")
            if readiness["status"] != "ready":
                raise RuntimeError(f"Windows sandbox is not ready: {readiness['status']}")
            dispatch_prompt = (
                "Use the actual shell tool exactly once. Run this exact PowerShell command: "
                f'Set-Content -LiteralPath runtime/agent_jobs/{args.run_id}/worker_ticket.md '
                f'-Value "Return exactly this marker and do not call tools: {worker_marker}" -NoNewline. '
                f"Then return exactly {dispatch_marker}. Do not perform any other action."
            )
            dispatch, dispatch_evidence = supervisor_turn(
                server,
                repo_root,
                dispatch_prompt,
                {"type": "workspaceWrite", "writableRoots": [str(run_dir)], "networkAccess": False},
                args.model,
            )
            if dispatch != dispatch_marker or not ticket.is_file():
                raise RuntimeError("Supervisor did not create the expected Worker ticket")
            worker = run_ticket(repo_root, ticket, worker_output, args.worker_model, 45.0)
            if worker_output.read_text(encoding="utf-8").strip() != worker_marker:
                raise RuntimeError("Worker marker did not match")
            verify_prompt = (
                "Use the actual shell tool exactly once to run "
                f"Get-Content -LiteralPath runtime/agent_jobs/{args.run_id}/worker_output.txt. "
                f"The exact expected text is {worker_marker}. After seeing the output, return exactly "
                f"{verify_marker} if equal, otherwise P102_HYBRID_REJECTED."
            )
            verify, verify_evidence = supervisor_turn(
                server,
                repo_root,
                verify_prompt,
                {"type": "readOnly", "networkAccess": False},
                args.model,
            )
        if verify != verify_marker:
            raise RuntimeError("Supervisor verification marker did not match")
        (run_dir / "supervisor_dispatch.txt").write_text(dispatch + "\n", encoding="utf-8")
        (run_dir / "supervisor_verify.txt").write_text(verify + "\n", encoding="utf-8")
        (run_dir / "supervisor_evidence.json").write_text(
            json.dumps(
                {
                    "supervisor_model": args.model,
                    "worker_model": args.worker_model,
                    "dispatch": dispatch_evidence,
                    "verify": verify_evidence,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(json.dumps({"ok": True, "worker": worker, "dispatch": dispatch, "verify": verify}, sort_keys=True))
        return 0
    except (OSError, RuntimeError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
