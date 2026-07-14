"""Validate native Codex role configuration and a sanitized proof manifest.

This verifier deliberately accepts references to ignored runtime evidence rather
than reading raw sessions. A Coordinator must inspect those sessions separately
before asserting that a proof manifest is accepted.
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Any


EXPECTED_PROVIDER = "agent_workbench_ollama"
EXPECTED_AGENTS = {
    "ollama_supervisor": "ollama_supervisor.toml",
    "ollama_worker": "ollama_worker.toml",
}
EXPECTED_HONEYCOMB_AGENTS = {
    "gpt_luna_supervisor": ("gpt_luna_supervisor.toml", "gpt-5.6-luna", "medium"),
    "gpt_luna_worker": ("gpt_luna_worker.toml", "gpt-5.6-luna", "low"),
    "gpt_sol_advisor": ("gpt_sol_advisor.toml", "gpt-5.6-sol", "high"),
}
EXPECTED_EDGES = {
    ("coordinator", "ollama_supervisor"),
    ("ollama_supervisor", "ollama_worker"),
}


def read_toml(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"cannot read TOML {path}: {exc}")
        return {}


def validate_profiles(config_root: Path) -> list[str]:
    """Return configuration errors for the tracked native role surfaces."""
    errors: list[str] = []
    config = read_toml(config_root / "config.toml", errors)
    if config.get("model") != "gpt-5.6":
        errors.append("config.toml must set the Coordinator model to gpt-5.6")
    if config.get("model_reasoning_effort") != "high":
        errors.append("config.toml must set Coordinator reasoning effort to high")
    agents = config.get("agents")
    if not isinstance(agents, dict) or agents.get("max_depth") != 2:
        errors.append("config.toml must set agents.max_depth to 2 for recursive delegation")

    for name, filename in EXPECTED_AGENTS.items():
        profile = read_toml(config_root / "agents" / filename, errors)
        for required in ("name", "description", "developer_instructions"):
            if not isinstance(profile.get(required), str) or not profile[required].strip():
                errors.append(f"{filename} must define non-empty {required}")
        if profile.get("name") != name:
            errors.append(f"{filename} must name agent {name}")
        if profile.get("model_provider") != EXPECTED_PROVIDER:
            errors.append(f"{filename} must use provider {EXPECTED_PROVIDER}")
        if not isinstance(profile.get("model"), str) or not profile["model"].strip():
            errors.append(f"{filename} must declare a model")
        if profile.get("default_permissions") != "agent_workbench_ollama_readonly":
            errors.append(
                f"{filename} must use the agent_workbench_ollama_readonly permission profile"
            )
    for name, (filename, model, effort) in EXPECTED_HONEYCOMB_AGENTS.items():
        profile = read_toml(config_root / "agents" / filename, errors)
        for required in ("name", "description", "developer_instructions"):
            if not isinstance(profile.get(required), str) or not profile[required].strip():
                errors.append(f"{filename} must define non-empty {required}")
        if profile.get("name") != name:
            errors.append(f"{filename} must name agent {name}")
        if profile.get("model") != model:
            errors.append(f"{filename} must set model {model}")
        if profile.get("model_reasoning_effort") != effort:
            errors.append(f"{filename} must set reasoning effort {effort}")
    return errors


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_manifest(data: Any) -> list[str]:
    """Return errors for a sanitized two-edge native delegation proof manifest."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["proof manifest must be a JSON object"]
    if data.get("schema_version") != 1:
        errors.append("proof manifest schema_version must be 1")
    if not non_empty_string(data.get("run_id")):
        errors.append("proof manifest must provide run_id")

    roles = data.get("roles")
    if not isinstance(roles, dict):
        return errors + ["proof manifest roles must be an object"]
    for role in ("coordinator", "supervisor", "worker"):
        identity = roles.get(role)
        if not isinstance(identity, dict):
            errors.append(f"roles.{role} must be an object")
            continue
        for key in ("provider", "model", "session_ref"):
            if not non_empty_string(identity.get(key)):
                errors.append(f"roles.{role}.{key} must be a non-empty string")
    supervisor = roles.get("supervisor", {})
    worker = roles.get("worker", {})
    if isinstance(supervisor, dict):
        if supervisor.get("agent_name") != "ollama_supervisor":
            errors.append("roles.supervisor.agent_name must be ollama_supervisor")
        if supervisor.get("provider") != EXPECTED_PROVIDER:
            errors.append(f"roles.supervisor.provider must be {EXPECTED_PROVIDER}")
    if isinstance(worker, dict):
        if worker.get("agent_name") != "ollama_worker":
            errors.append("roles.worker.agent_name must be ollama_worker")
        if worker.get("provider") != EXPECTED_PROVIDER:
            errors.append(f"roles.worker.provider must be {EXPECTED_PROVIDER}")

    edges = data.get("delegation_edges")
    if not isinstance(edges, list):
        errors.append("delegation_edges must be a list")
    else:
        observed: set[tuple[str, str]] = set()
        for edge in edges:
            if not isinstance(edge, dict):
                errors.append("each delegation edge must be an object")
                continue
            source, target = edge.get("from"), edge.get("to")
            if edge.get("observed") is not True:
                errors.append(f"delegation edge {source!r}->{target!r} is not observed")
            if not non_empty_string(edge.get("evidence_ref")):
                errors.append(f"delegation edge {source!r}->{target!r} lacks evidence_ref")
            if isinstance(source, str) and isinstance(target, str):
                observed.add((source, target))
        missing_edges = EXPECTED_EDGES - observed
        for source, target in sorted(missing_edges):
            errors.append(f"missing delegation edge {source}->{target}")

    markers = data.get("markers")
    if not isinstance(markers, dict):
        errors.append("markers must be an object")
    else:
        for key in ("worker", "supervisor"):
            if not non_empty_string(markers.get(key)):
                errors.append(f"markers.{key} must be a non-empty string")
        if markers.get("worker") == markers.get("supervisor"):
            errors.append("worker and supervisor markers must be distinct")

    verdicts = data.get("verdicts")
    if not isinstance(verdicts, dict):
        errors.append("verdicts must be an object")
    else:
        for key in (
            "quality_validated_candidate",
            "protocol_accepted_candidate",
            "economics_usable",
        ):
            if not isinstance(verdicts.get(key), bool):
                errors.append(f"verdicts.{key} must be a boolean")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-root", type=Path, default=Path(".codex"))
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    errors = validate_profiles(args.config_root)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read proof manifest {args.manifest}: {exc}")
        manifest = None
    if manifest is not None:
        errors.extend(validate_manifest(manifest))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("native Codex delegation configuration and proof manifest: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
