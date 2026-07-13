from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def load_module() -> object:
    path = Path(__file__).resolve().parents[1] / "scripts" / "validate_native_codex_delegation.py"
    spec = importlib.util.spec_from_file_location("native_codex_validator", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def example_manifest() -> dict[str, object]:
    root = Path(__file__).resolve().parents[1]
    path = root / "templates" / "native_codex_delegation_proof_manifest.example.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_profiles_and_example_manifest_are_valid() -> None:
    validator = load_module()
    root = Path(__file__).resolve().parents[1]

    assert validator.validate_profiles(root / ".codex") == []
    assert validator.validate_manifest(example_manifest()) == []


def test_manifest_requires_both_observed_edges_and_distinct_verdicts() -> None:
    validator = load_module()
    manifest = example_manifest()
    manifest["delegation_edges"] = manifest["delegation_edges"][:1]
    manifest["verdicts"].pop("economics_usable")

    errors = validator.validate_manifest(manifest)

    assert "missing delegation edge ollama_supervisor->ollama_worker" in errors
    assert "verdicts.economics_usable must be a boolean" in errors
