"""Run a no-modal serial remote Ollama Supervisor -> Worker marker proof.

The Coordinator owns transport between serial turns.  That deliberately avoids
the concurrent response-stream failure observed when a remote Supervisor waits
on a remote Worker tool call.  The result is a quality proof, not evidence of a
Supervisor-direct dispatch edge.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from ollama_responses_worker_host import provider_settings, response_text, run_ticket


def call_model(prompt: str, model: str, timeout_seconds: float) -> tuple[int, str, float]:
    base_url, headers = provider_settings()
    request = urllib.request.Request(
        base_url + "/responses",
        data=json.dumps({"model": model, "input": prompt, "stream": False}).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json", **headers},
    )
    started = time.monotonic()
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        payload: dict[str, Any] = json.loads(response.read().decode("utf-8"))
        return response.status, response_text(payload).strip(), round(time.monotonic() - started, 3)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model", default="qwen3-coder:latest")
    parser.add_argument("--timeout-seconds", type=float, default=45.0)
    args = parser.parse_args()
    if not args.run_id.replace("-", "").replace("_", "").isalnum():
        parser.error("--run-id may contain only letters, digits, hyphens, and underscores")

    repo_root = Path(__file__).resolve().parents[1]
    run_dir = repo_root / "runtime" / "agent_jobs" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    dispatch_marker = "P102_SERIAL_SUPERVISOR_DISPATCH"
    worker_marker = "P102_SERIAL_WORKER_RESULT"
    verify_marker = "P102_SERIAL_SUPERVISOR_VERIFIED"
    ticket = run_dir / "worker_ticket.md"
    worker_output = run_dir / "worker_output.txt"
    ticket.write_text(f"Return exactly this marker and do not call tools:\n\n{worker_marker}\n", encoding="utf-8")

    try:
        dispatch_status, dispatch, dispatch_seconds = call_model(
            f"You are a bounded Ollama Supervisor. Return exactly {dispatch_marker} and nothing else.",
            args.model,
            args.timeout_seconds,
        )
        if dispatch != dispatch_marker:
            raise RuntimeError("Supervisor dispatch marker did not match")
        worker = run_ticket(repo_root, ticket, worker_output, args.model, args.timeout_seconds)
        worker_text = worker_output.read_text(encoding="utf-8").strip()
        if worker_text != worker_marker:
            raise RuntimeError("Worker marker did not match")
        verify_status, verify, verify_seconds = call_model(
            f"You are a bounded Ollama Supervisor. A Worker returned {worker_text}. "
            f"If and only if that is exactly {worker_marker}, return exactly {verify_marker} and nothing else.",
            args.model,
            args.timeout_seconds,
        )
        if verify != verify_marker:
            raise RuntimeError("Supervisor verification marker did not match")
        (run_dir / "supervisor_dispatch.txt").write_text(dispatch + "\n", encoding="utf-8")
        (run_dir / "supervisor_verify.txt").write_text(verify + "\n", encoding="utf-8")
        print(json.dumps({"ok": True, "dispatch_http_status": dispatch_status, "dispatch_seconds": dispatch_seconds, "worker": worker, "verify_http_status": verify_status, "verify_seconds": verify_seconds}, sort_keys=True))
        return 0
    except (OSError, RuntimeError, ValueError, urllib.error.URLError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
