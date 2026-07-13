"""Persistent, no-tool Worker host for an OpenAI-compatible Ollama provider.

The host keeps provider credentials in the existing ignored operator files. It
never includes those values in prompts, output, or runtime status records.
Worker requests are non-streaming and ticket/result paths are confined to
``runtime/agent_jobs``.  ``--serve`` handles sequential JSON jobs in one local
host process without spawning nested Codex sandboxes.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def runtime_path(repo_root: Path, value: str, kind: str) -> Path:
    root = (repo_root / "runtime" / "agent_jobs").resolve()
    candidate = (repo_root / value).resolve()
    if root not in candidate.parents and candidate != root:
        raise ValueError(f"{kind} must be below runtime/agent_jobs")
    return candidate


def provider_settings() -> tuple[str, dict[str, str]]:
    values: dict[str, str] = {}
    for line in (Path.home() / ".agent-workbench-env.txt").read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    base_url = values.get("AGENT_WORKBENCH_OLLAMA_OPENAI_BASE_URL")
    headers_file = values.get("AGENT_WORKBENCH_PROVIDER_HEADERS_FILE")
    if not base_url or not headers_file:
        raise RuntimeError("operator environment file lacks the required provider settings")
    headers = json.loads(Path(headers_file).read_text(encoding="utf-8-sig"))
    required = ("CF-Access-Client-Id", "CF-Access-Client-Secret", "User-Agent")
    if any(not isinstance(headers.get(name), str) or not headers[name] for name in required):
        raise RuntimeError("provider headers file is incomplete")
    return base_url.rstrip("/"), {name: headers[name] for name in required}


def response_text(payload: dict[str, Any]) -> str:
    return "".join(
        content.get("text", "")
        for item in payload.get("output", [])
        if isinstance(item, dict)
        for content in item.get("content", [])
        if isinstance(content, dict) and isinstance(content.get("text"), str)
    )


def run_ticket(repo_root: Path, ticket: Path, output: Path, model: str, timeout_seconds: float) -> dict[str, Any]:
    base_url, headers = provider_settings()
    prompt = ticket.read_text(encoding="utf-8")
    request = urllib.request.Request(
        base_url + "/responses",
        data=json.dumps({"model": model, "input": prompt, "stream": False}).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json", **headers},
    )
    started = time.monotonic()
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        body = json.loads(response.read().decode("utf-8"))
        status_code = response.status
    text = response_text(body).strip()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text + "\n", encoding="utf-8")
    return {
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "http_status": status_code,
        "model": model,
        "output": str(output),
    }


def job_paths(repo_root: Path, ticket_value: str, output_value: str) -> tuple[Path, Path]:
    ticket = runtime_path(repo_root, ticket_value, "ticket")
    output = runtime_path(repo_root, output_value, "output")
    if not ticket.is_file():
        raise ValueError(f"ticket does not exist: {ticket_value}")
    return ticket, output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticket")
    parser.add_argument("--output")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--model", default="qwen3-coder:latest")
    parser.add_argument("--timeout-seconds", type=float, default=45.0)
    args = parser.parse_args()
    if args.serve == (bool(args.ticket) and bool(args.output)):
        parser.error("supply --serve or both --ticket and --output")
    repo_root = Path(__file__).resolve().parents[1]

    def execute(ticket_value: str, output_value: str) -> dict[str, Any]:
        ticket, output = job_paths(repo_root, ticket_value, output_value)
        print(json.dumps({"event": "worker_request_started", "ticket": ticket_value}, sort_keys=True), flush=True)
        return run_ticket(repo_root, ticket, output, args.model, args.timeout_seconds)

    try:
        if args.serve:
            for raw in sys.stdin:
                if not raw.strip():
                    continue
                try:
                    job = json.loads(raw)
                    if not isinstance(job, dict):
                        raise ValueError("job must be a JSON object")
                    result = execute(job["ticket"], job["output"])
                    print(json.dumps({"event": "worker_request_completed", "ok": True, **result}, sort_keys=True), flush=True)
                except (KeyError, OSError, RuntimeError, ValueError, urllib.error.URLError, json.JSONDecodeError) as exc:
                    print(json.dumps({"event": "worker_request_completed", "ok": False, "error": str(exc)}, sort_keys=True), flush=True)
            return 0
        result = execute(args.ticket, args.output)
        print(json.dumps({"ok": True, **result}, sort_keys=True))
        return 0
    except (OSError, RuntimeError, ValueError, urllib.error.URLError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
