from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module() -> object:
    path = ROOT / "scripts" / "validate_honeycomb_native_config.py"
    spec = importlib.util.spec_from_file_location("honeycomb_config", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_terra_catalog(path: Path, multi_agent_version: str = "v1") -> None:
    write(
        path,
        '{"models": [{"slug": "gpt-5.6-terra", "multi_agent_version": "'
        + multi_agent_version
        + '"}]}',
    )


def test_accepts_complete_machine_local_honeycomb_config(tmp_path: Path) -> None:
    module = load_module()
    home = tmp_path / ".codex"
    catalog = tmp_path / "terra-v1-catalog.json"
    write_terra_catalog(catalog)
    write(home / "config.toml", f"""
model = "gpt-5.6-terra"
model_reasoning_effort = "medium"
model_catalog_json = "{catalog.as_posix()}"
[agents]
max_threads = 6
max_depth = 2
[features]
multi_agent = true
[model_providers.agent_workbench_ollama]
env_http_headers = {{ "X-Test" = "TEST_ENV" }}
""" + "\n".join(
        f'\n[agents.{name}]\nconfig_file = "agents/{filename}"'
        for name, (filename, _, _) in module.ROLES.items()
    ))
    for name, (filename, model, effort) in module.ROLES.items():
        provider = '\nmodel_provider = "agent_workbench_ollama"' if name == "ollama_worker" else ""
        write(home / "agents" / filename, f'name = "{name}"\nmodel = "{model}"\nmodel_reasoning_effort = "{effort}"{provider}\n')
    assert module.validate(home) == []


def test_rejects_missing_ollama_provider_provenance(tmp_path: Path) -> None:
    module = load_module()
    home = tmp_path / ".codex"
    write(home / "config.toml", "[agents]\nmax_threads = 6\nmax_depth = 2\n[features]\nmulti_agent = true\n")
    errors = module.validate(home)
    assert "Ollama provider must use environment-backed headers" in errors


def test_project_config_overrides_machine_defaults(tmp_path: Path) -> None:
    module = load_module()
    home = tmp_path / ".codex"
    project_config = tmp_path / "project" / ".codex" / "config.toml"
    catalog = tmp_path / "terra-v1-catalog.json"
    write_terra_catalog(catalog)
    write(home / "config.toml", f"""
model = "gpt-5.6"
model_reasoning_effort = "high"
model_catalog_json = "{catalog.as_posix()}"
[agents]
max_threads = 3
max_depth = 1
[features]
multi_agent = true
[model_providers.agent_workbench_ollama]
env_http_headers = {{ "X-Test" = "TEST_ENV" }}
""")
    for name, (filename, model, effort) in module.ROLES.items():
        provider = '\nmodel_provider = "agent_workbench_ollama"' if name == "ollama_worker" else ""
        write(project_config.parent / "agents" / filename, f'name = "{name}"\nmodel = "{model}"\nmodel_reasoning_effort = "{effort}"{provider}\n')
    write(project_config, 'model = "gpt-5.6-terra"\nmodel_reasoning_effort = "medium"\n[agents]\nmax_threads = 6\nmax_depth = 2\n')
    assert module.validate(home, project_config) == []


def test_rejects_v2_ui_coordinator_defaults(tmp_path: Path) -> None:
    module = load_module()
    home = tmp_path / ".codex"
    write(home / "config.toml", '[agents]\nmax_threads = 6\nmax_depth = 2\n[features]\nmulti_agent = true\n')
    errors = module.validate(home)
    assert any("role-aware v1" in error for error in errors)


def test_rejects_terra_catalog_without_v1_metadata(tmp_path: Path) -> None:
    module = load_module()
    home = tmp_path / ".codex"
    catalog = tmp_path / "terra-v2-catalog.json"
    write_terra_catalog(catalog, "v2")
    write(
        home / "config.toml",
        f'model = "gpt-5.6-terra"\nmodel_reasoning_effort = "medium"\nmodel_catalog_json = "{catalog.as_posix()}"\n[agents]\nmax_threads = 6\nmax_depth = 2\n[features]\nmulti_agent = true\n',
    )
    errors = module.validate(home)
    assert "gpt-5.6-terra catalog metadata must set multi_agent_version to v1" in errors
