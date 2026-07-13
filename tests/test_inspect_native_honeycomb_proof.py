from __future__ import annotations

import importlib.util
from pathlib import Path


def load_module() -> object:
    path = Path(__file__).parents[1] / "scripts" / "inspect_native_honeycomb_proof.py"
    spec = importlib.util.spec_from_file_location("honeycomb_proof", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def spawn(thread_id: str, model: str = "qwen3.6:35b-a3b-bf16") -> dict[str, object]:
    return {"payload": {"item": {"type": "collabAgentToolCall", "tool": "spawnAgent", "receiverThreadIds": [thread_id], "model": model, "reasoningEffort": "low"}}}


def test_accepts_four_native_spawns_and_two_provider_records() -> None:
    module = load_module()
    events = [spawn(f"child-{index}") for index in range(4)]
    provider = {"children": [{"status": "completed", "provider": "agent_workbench_ollama", "model": "qwen3.6:35b-a3b-bf16"}] * 2}
    assert module.verdict(events, provider)["protocol_accepted_candidate"] is True


def test_rejects_missing_model_and_provider_corroboration() -> None:
    module = load_module()
    result = module.verdict([spawn("child-1", model=None)], {"children": []})
    assert result["protocol_accepted_candidate"] is False
    assert any("provider evidence" in error for error in result["errors"])
