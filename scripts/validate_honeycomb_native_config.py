"""Validate the machine-local Honeycomb profile without exposing credentials."""

from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path


ROLES = {
    "gpt_luna_supervisor": ("gpt_luna_supervisor.toml", "gpt-5.6-luna", "medium"),
    "gpt_luna_worker": ("gpt_luna_worker.toml", "gpt-5.6-luna", "low"),
    "gpt_sol_advisor": ("gpt_sol_advisor.toml", "gpt-5.6-sol", "medium"),
    "ollama_worker": ("ollama_worker.toml", "qwen3.6:35b-a3b-bf16", "medium"),
}


def read_toml(path: Path, errors: list[str]) -> dict[str, object]:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"cannot read {path.name}: {exc}")
        return {}


def read_catalog(path: Path, errors: list[str]) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read model catalog {path}: {exc}")
        return {}


def find_model_entry(value: object, slug: str) -> dict[str, object] | None:
    if isinstance(value, dict):
        if value.get("slug") == slug:
            return value
        for child in value.values():
            result = find_model_entry(child, slug)
            if result is not None:
                return result
    elif isinstance(value, list):
        for child in value:
            result = find_model_entry(child, slug)
            if result is not None:
                return result
    return None


def validate(codex_home: Path, project_config: Path | None = None) -> list[str]:
    errors: list[str] = []
    config = read_toml(codex_home / "config.toml", errors)
    agents = config.get("agents")
    if not isinstance(agents, dict):
        return errors + ["config.toml must define [agents]"]
    project: dict[str, object] = {}
    project_agents: dict[str, object] = {}
    if project_config is not None:
        project = read_toml(project_config, errors)
        candidate = project.get("agents", {})
        if isinstance(candidate, dict):
            project_agents = candidate
    max_threads = project_agents.get("max_threads", agents.get("max_threads"))
    max_depth = project_agents.get("max_depth", agents.get("max_depth"))
    if max_threads != 6:
        errors.append("effective agents.max_threads must be 6")
    if max_depth != 2:
        errors.append("effective agents.max_depth must be 2")
    root_model = project.get("model", config.get("model"))
    root_effort = project.get("model_reasoning_effort", config.get("model_reasoning_effort"))
    if root_model != "gpt-5.6-terra" or root_effort != "medium":
        errors.append("effective UI Coordinator must be gpt-5.6-terra with medium reasoning for role-aware v1 spawning")
    catalog_value = config.get("model_catalog_json")
    if not isinstance(catalog_value, str) or not catalog_value.strip():
        errors.append("effective global config must define model_catalog_json for the Terra v1 catalog")
    else:
        catalog_path = Path(catalog_value).expanduser()
        if not catalog_path.is_absolute():
            catalog_path = codex_home / catalog_path
        catalog = read_catalog(catalog_path, errors)
        terra = find_model_entry(catalog, "gpt-5.6-terra")
        if terra is None:
            errors.append("model catalog must contain gpt-5.6-terra metadata")
        elif terra.get("multi_agent_version") != "v1":
            errors.append("gpt-5.6-terra catalog metadata must set multi_agent_version to v1")
    features = config.get("features", {})
    if not isinstance(features, dict) or features.get("multi_agent") is not True:
        errors.append("features.multi_agent must be true")
    resolved_profiles: dict[str, dict[str, object]] = {}
    project_role_root = project_config.parent / "agents" if project_config is not None else None
    for name, (filename, model, effort) in ROLES.items():
        registration = agents.get(name)
        project_registration = project_agents.get(name)
        if (
            isinstance(project_registration, dict)
            and project_registration.get("config_file") == f"agents/{filename}"
            and project_role_root is not None
            and (project_role_root / filename).is_file()
        ):
            profile = read_toml(project_role_root / filename, errors)
        elif isinstance(registration, dict) and registration.get("config_file") == f"agents/{filename}":
            profile = read_toml(codex_home / "agents" / filename, errors)
        elif project_role_root is not None and (project_role_root / filename).is_file():
            profile = read_toml(project_role_root / filename, errors)
        else:
            errors.append(f"role {name} must exist in project .codex/agents or user agents configuration")
            continue
        resolved_profiles[name] = profile
        if profile.get("name") != name:
            errors.append(f"{filename} must name {name}")
        if profile.get("model") != model:
            errors.append(f"{filename} must set model {model}")
        if profile.get("model_reasoning_effort") != effort:
            errors.append(f"{filename} must set reasoning effort {effort}")
    worker = resolved_profiles.get("ollama_worker", {})
    if worker.get("model_provider") != "agent_workbench_ollama":
        errors.append("ollama_worker must use agent_workbench_ollama")
    providers = config.get("model_providers", {})
    entry = providers.get("agent_workbench_ollama") if isinstance(providers, dict) else None
    if not isinstance(entry, dict) or not isinstance(entry.get("env_http_headers"), dict):
        errors.append("Ollama provider must use environment-backed headers")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--project-config", type=Path, default=Path.cwd() / ".codex" / "config.toml")
    args = parser.parse_args()
    project_config = args.project_config if args.project_config.exists() else None
    errors = validate(args.codex_home, project_config)
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
