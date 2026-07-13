"""Fail-closed sanitizer for a direct native Honeycomb proof."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        text = raw.decode("utf-16")
    else:
        text = raw.decode("utf-8-sig")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def spawn_items(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for event in events:
        payload = event.get("payload", event)
        item = payload.get("item", {}) if isinstance(payload, dict) else {}
        if item.get("type") == "collabAgentToolCall" and item.get("tool") == "spawnAgent":
            found.append(item)
    return found


def verdict(events: list[dict[str, Any]], provider: Any) -> dict[str, Any]:
    spawns = spawn_items(events)
    child_ids = [child for item in spawns for child in item.get("receiverThreadIds", []) if isinstance(child, str) and child]
    requested_models = [item.get("model") for item in spawns]
    requested_efforts = [item.get("reasoningEffort") for item in spawns]
    provider_rows = provider.get("children", []) if isinstance(provider, dict) else []
    corroborated = [row for row in provider_rows if isinstance(row, dict) and row.get("status") == "completed" and row.get("model") == "qwen3.6:35b-a3b-bf16" and row.get("provider") == "agent_workbench_ollama"]
    errors: list[str] = []
    if len(spawns) != 4:
        errors.append(f"expected 4 native spawnAgent events, found {len(spawns)}")
    if len(set(child_ids)) != 4:
        errors.append("each native child must have a distinct nonempty thread ID")
    if any(model is None for model in requested_models):
        errors.append("native events did not preserve requested child model values")
    if any(effort is None for effort in requested_efforts):
        errors.append("native events did not preserve requested child reasoning effort values")
    if len(corroborated) < 2:
        errors.append("provider evidence does not corroborate two completed qwen3.6 Ollama Workers")
    return {
        "schema_version": 1,
        "transport": "codex_native_handoff",
        "spawn_events": len(spawns),
        "child_thread_ids": child_ids,
        "requested_models": requested_models,
        "requested_reasoning_efforts": requested_efforts,
        "provider_corroborated_ollama_workers": len(corroborated),
        "protocol_accepted_candidate": not errors,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--provider-evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.events.is_file():
        result = {
            "schema_version": 1,
            "transport": "codex_native_handoff",
            "spawn_events": 0,
            "child_thread_ids": [],
            "requested_models": [],
            "requested_reasoning_efforts": [],
            "provider_corroborated_ollama_workers": 0,
            "protocol_accepted_candidate": False,
            "errors": ["native event stream was not created"],
        }
    else:
        result = verdict(load_jsonl(args.events), json.loads(args.provider_evidence.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return int(not result["protocol_accepted_candidate"])


if __name__ == "__main__":
    raise SystemExit(main())
