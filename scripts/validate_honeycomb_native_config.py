"""Validate the machine-local Honeycomb profile without exposing credentials."""

from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path


ROLES = {
    "gpt_luna_supervisor": ("gpt_luna_supervisor.toml", "gpt-5.6-luna", "medium"),
    "gpt_luna_worker": ("gpt_luna_worker.toml", "gpt-5.6-luna", "low"),
    "gpt_sol_advisor": ("gpt_sol_advisor.toml", "gpt-5.6-sol", "high"),
    "ollama_worker": ("ollama_worker.toml", "qwen3.6:35b-a3b-bf16", "low"),
}


def read_toml(path: Path, errors: list[str]) -> dict[str, object]:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"cannot read {path.name}: {exc}")
        return {}


def validate(codex_home: Path) -> list[str]:
    errors: list[str] = []
    config = read_toml(codex_home / "config.toml", errors)
    agents = config.get("agents")
    if not isinstance(agents, dict):
        return errors + ["config.toml must define [agents]"]
    if agents.get("max_threads") != 6:
        errors.append("agents.max_threads must be 6")
    if agents.get("max_depth") != 1:
        errors.append("agents.max_depth must be 1")
    features = config.get("features", {})
    if not isinstance(features, dict) or features.get("multi_agent") is not True:
        errors.append("features.multi_agent must be true")
    for name, (filename, model, effort) in ROLES.items():
        registration = agents.get(name)
        if not isinstance(registration, dict) or registration.get("config_file") != f"agents/{filename}":
            errors.append(f"agents.{name} must register agents/{filename}")
            continue
        profile = read_toml(codex_home / "agents" / filename, errors)
        if profile.get("name") != name:
            errors.append(f"{filename} must name {name}")
        if profile.get("model") != model:
            errors.append(f"{filename} must set model {model}")
        if profile.get("model_reasoning_effort") != effort:
            errors.append(f"{filename} must set reasoning effort {effort}")
    worker = read_toml(codex_home / "agents" / "ollama_worker.toml", errors)
    if worker.get("model_provider") != "agent_workbench_ollama":
        errors.append("ollama_worker must use agent_workbench_ollama")
    provider = config.get("model_providers", {})
    entry = provider.get("agent_workbench_ollama") if isinstance(provider, dict) else None
    if not isinstance(entry, dict) or not isinstance(entry.get("env_http_headers"), dict):
        errors.append("Ollama provider must use environment-backed headers")
    coordinator = read_toml(codex_home / "agent-workbench-coordinator.config.toml", errors)
    if coordinator.get("model") != "gpt-5.6-terra" or coordinator.get("model_reasoning_effort") != "medium":
        errors.append("Coordinator profile must be gpt-5.6-terra with medium reasoning")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", type=Path, default=Path.home() / ".codex")
    args = parser.parse_args()
    errors = validate(args.codex_home)
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
