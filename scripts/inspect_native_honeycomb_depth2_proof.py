"""Fail-closed sanitizer for a recursive native Honeycomb UI proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


EXPECTED = {
    "root": {"agent_role": None, "provider": "openai", "model": "gpt-5.6-terra", "effort": "medium", "depth": None},
    "supervisor": {"agent_role": "gpt_luna_supervisor", "provider": "openai", "model": "gpt-5.6-luna", "effort": "medium", "depth": 1},
    "worker": {"agent_role": "ollama_worker", "provider": "agent_workbench_ollama", "model": "qwen3.6:35b-a3b-bf16", "effort": "low", "depth": 2},
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    text = raw.decode("utf-16") if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else raw.decode("utf-8-sig")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def spawn_requests(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for event in events:
        payload = event.get("payload", {})
        if payload.get("type") == "function_call" and payload.get("name") == "spawn_agent":
            arguments = json.loads(payload.get("arguments", "{}"))
            found.append({"agent_type": arguments.get("agent_type"), "fork_context": arguments.get("fork_context"), "model_override": arguments.get("model")})
        if payload.get("type") == "custom_tool_call" and payload.get("name") == "exec":
            source = payload.get("input", "")
            for match in re.finditer(r"multi_agent_v1__spawn_agent\s*\(\s*\{(.*?)\}\s*\)", source, re.DOTALL):
                arguments = match.group(1)
                agent_type = re.search(r"agent_type\s*:\s*[\"']([^\"']+)", arguments)
                fork_context = re.search(r"fork_context\s*:\s*(true|false)", arguments)
                model = re.search(r"(?:^|[,\n])\s*model\s*:\s*[\"']([^\"']+)", arguments)
                found.append({
                    "agent_type": agent_type.group(1) if agent_type else None,
                    "fork_context": fork_context.group(1) == "true" if fork_context else None,
                    "model_override": model.group(1) if model else None,
                })
    return found


def session_summary(path: Path) -> dict[str, Any]:
    events = load_jsonl(path)
    meta = next((event.get("payload", {}) for event in events if event.get("type") == "session_meta"), {})
    contexts = [event.get("payload", {}) for event in events if event.get("type") == "turn_context"]
    completes = [event for event in events if event.get("type") == "event_msg" and event.get("payload", {}).get("type") == "task_complete"]
    source = meta.get("source", {})
    spawn = source.get("subagent", {}).get("thread_spawn", {}) if isinstance(source, dict) else {}
    return {
        "file": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "thread_id": meta.get("id"),
        "parent_thread_id": meta.get("parent_thread_id"),
        "originator": meta.get("originator"),
        "agent_role": spawn.get("agent_role"),
        "provider": meta.get("model_provider"),
        "depth": spawn.get("depth"),
        "models": sorted({context.get("model") for context in contexts if context.get("model")}),
        "reasoning_efforts": sorted({context.get("effort") for context in contexts if context.get("effort")}),
        "multi_agent_versions": sorted({context.get("multi_agent_version") for context in contexts if context.get("multi_agent_version")}),
        "turns": len(contexts),
        "terminal_task_complete_events": len(completes),
        "shell_tool_calls": sum(
            1 for event in events
            if event.get("payload", {}).get("type") in {"custom_tool_call", "function_call"}
            and event.get("payload", {}).get("name") == "shell_command"
        ),
        "spawn_requests": spawn_requests(events),
    }


def validate_role(name: str, summary: dict[str, Any], errors: list[str]) -> None:
    expected = EXPECTED[name]
    for field in ("agent_role", "provider", "depth"):
        if summary.get(field) != expected[field]:
            errors.append(f"{name} {field} must be {expected[field]!r}")
    if summary.get("models") != [expected["model"]]:
        errors.append(f"{name} model must remain {expected['model']}")
    if summary.get("reasoning_efforts") != [expected["effort"]]:
        errors.append(f"{name} reasoning effort must remain {expected['effort']}")
    if summary.get("multi_agent_versions") != ["v1"]:
        errors.append(f"{name} must use multi-agent v1")
    if not summary.get("thread_id"):
        errors.append(f"{name} thread ID must be nonempty")
    if summary.get("terminal_task_complete_events", 0) < 1:
        errors.append(f"{name} must contain a terminal task_complete event")


def verdict(root_path: Path, supervisor_path: Path, worker_path: Path) -> dict[str, Any]:
    summaries = {"root": session_summary(root_path), "supervisor": session_summary(supervisor_path), "worker": session_summary(worker_path)}
    errors: list[str] = []
    for name, summary in summaries.items():
        validate_role(name, summary, errors)
    root, supervisor, worker = summaries["root"], summaries["supervisor"], summaries["worker"]
    if root.get("parent_thread_id") is not None:
        errors.append("root parent thread must be empty")
    if root.get("originator") != "codex_vscode":
        errors.append("root originator must be codex_vscode")
    if supervisor.get("parent_thread_id") != root.get("thread_id"):
        errors.append("Supervisor parent must equal the Coordinator thread")
    if worker.get("parent_thread_id") != supervisor.get("thread_id"):
        errors.append("Worker parent must equal the Supervisor thread")
    for parent, agent_type in ((root, "gpt_luna_supervisor"), (supervisor, "ollama_worker")):
        matching = [request for request in parent["spawn_requests"] if request.get("agent_type") == agent_type]
        if len(matching) != 1:
            errors.append(f"expected exactly one {agent_type} spawn request")
        elif matching[0].get("fork_context") is not False or matching[0].get("model_override") is not None:
            errors.append(f"{agent_type} must spawn with fork_context false and no model override")
    if worker.get("turns", 0) < 2 or worker.get("terminal_task_complete_events", 0) < 2:
        errors.append("Worker must preserve at least two completed interactive UI turns")
    return {
        "schema_version": 1,
        "transport": "codex_native_handoff",
        "topology": "coordinator_supervisor_worker_depth_2",
        "sessions": summaries,
        "recursive_protocol_accepted_candidate": not errors,
        "interactive_ui_usable_candidate": not errors,
        "economics_usable": False,
        "economics_note": "No bounded paid-Coordinator token span was captured for this exploration proof.",
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--supervisor", type=Path, required=True)
    parser.add_argument("--worker", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    missing = [path for path in (args.root, args.supervisor, args.worker) if not path.is_file()]
    if missing:
        result = {"schema_version": 1, "transport": "codex_native_handoff", "recursive_protocol_accepted_candidate": False, "interactive_ui_usable_candidate": False, "economics_usable": False, "errors": [f"missing rollout: {path.name}" for path in missing]}
    else:
        result = verdict(args.root, args.supervisor, args.worker)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return int(not result["recursive_protocol_accepted_candidate"])


if __name__ == "__main__":
    raise SystemExit(main())
