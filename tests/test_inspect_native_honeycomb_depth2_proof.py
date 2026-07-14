from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module() -> object:
    path = ROOT / "scripts" / "inspect_native_honeycomb_depth2_proof.py"
    spec = importlib.util.spec_from_file_location("honeycomb_depth2", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_jsonl(path: Path, events: list[dict[str, object]]) -> None:
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")


def session(thread_id: str, parent: str | None, role: str | None, provider: str, model: str, effort: str, depth: int | None, spawn_role: str | None = None, turns: int = 1) -> list[dict[str, object]]:
    source: object = "vscode"
    if parent:
        source = {"subagent": {"thread_spawn": {"parent_thread_id": parent, "depth": depth, "agent_role": role}}}
    events: list[dict[str, object]] = [{"type": "session_meta", "payload": {"id": thread_id, "parent_thread_id": parent, "originator": "codex_vscode", "source": source, "model_provider": provider}}]
    if spawn_role:
        events.append({"type": "response_item", "payload": {"type": "function_call", "name": "spawn_agent", "arguments": json.dumps({"agent_type": spawn_role, "fork_context": False, "message": "bounded task"})}})
    for index in range(turns):
        events.extend([
            {"type": "turn_context", "payload": {"turn_id": f"turn-{index}", "model": model, "effort": effort, "multi_agent_version": "v1"}},
            {"type": "event_msg", "payload": {"type": "task_complete", "turn_id": f"turn-{index}", "last_agent_message": "ok"}},
        ])
    return events


def test_accepts_role_bound_recursive_ui_chain(tmp_path: Path) -> None:
    module = load_module()
    root, supervisor, worker = tmp_path / "root.jsonl", tmp_path / "supervisor.jsonl", tmp_path / "worker.jsonl"
    write_jsonl(root, session("root", None, None, "openai", "gpt-5.6", "high", None, "gpt_luna_supervisor"))
    write_jsonl(supervisor, session("supervisor", "root", "gpt_luna_supervisor", "openai", "gpt-5.6-luna", "medium", 1, "ollama_worker"))
    write_jsonl(worker, session("worker", "supervisor", "ollama_worker", "agent_workbench_ollama", "qwen3.6:35b-a3b-bf16", "low", 2, turns=3))
    result = module.verdict(root, supervisor, worker)
    assert result["recursive_protocol_accepted_candidate"] is True
    assert result["interactive_ui_usable_candidate"] is True


def test_rejects_generic_v2_worker_and_wrong_parent(tmp_path: Path) -> None:
    module = load_module()
    root, supervisor, worker = tmp_path / "root.jsonl", tmp_path / "supervisor.jsonl", tmp_path / "worker.jsonl"
    write_jsonl(root, session("root", None, None, "openai", "gpt-5.6", "high", None, "gpt_luna_supervisor"))
    write_jsonl(supervisor, session("supervisor", "root", "gpt_luna_supervisor", "openai", "gpt-5.6-luna", "medium", 1, "ollama_worker"))
    events = session("worker", "wrong-parent", None, "openai", "gpt-5.6", "high", 2, turns=2)
    for event in events:
        if event["type"] == "turn_context":
            event["payload"]["multi_agent_version"] = "v2"  # type: ignore[index]
    write_jsonl(worker, events)
    result = module.verdict(root, supervisor, worker)
    assert result["recursive_protocol_accepted_candidate"] is False
    assert any("Worker parent" in error for error in result["errors"])
    assert any("multi-agent v1" in error for error in result["errors"])


def test_rejects_full_history_or_model_override(tmp_path: Path) -> None:
    module = load_module()
    root, supervisor, worker = tmp_path / "root.jsonl", tmp_path / "supervisor.jsonl", tmp_path / "worker.jsonl"
    root_events = session("root", None, None, "openai", "gpt-5.6", "high", None, "gpt_luna_supervisor")
    root_events[1]["payload"]["arguments"] = json.dumps({"agent_type": "gpt_luna_supervisor", "fork_context": True, "model": "gpt-5.6-luna"})  # type: ignore[index]
    write_jsonl(root, root_events)
    write_jsonl(supervisor, session("supervisor", "root", "gpt_luna_supervisor", "openai", "gpt-5.6-luna", "medium", 1, "ollama_worker"))
    write_jsonl(worker, session("worker", "supervisor", "ollama_worker", "agent_workbench_ollama", "qwen3.6:35b-a3b-bf16", "low", 2, turns=2))
    result = module.verdict(root, supervisor, worker)
    assert result["recursive_protocol_accepted_candidate"] is False
    assert any("fork_context false" in error for error in result["errors"])
