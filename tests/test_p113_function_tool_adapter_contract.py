from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_p113_function_tool_adapter_contract.py"
FIXTURE = ROOT / "benchmarks" / "p113_function_tool_adapter" / "adapter_contract_fixtures.json"


def load_validator():
    spec = importlib.util.spec_from_file_location("p113_contract", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fixture_contract_is_valid() -> None:
    validator = load_validator()
    assert validator.validate(json.loads(FIXTURE.read_text(encoding="utf-8"))) == []


def test_fixture_contract_rejects_path_escape() -> None:
    validator = load_validator()
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    valid = next(case for case in data["cases"] if case["id"] == "valid_translation")
    valid["provider_calls"][0]["arguments"] = json.dumps({"patch": "*** Begin Patch\n*** Update File: ../escape.txt\n*** End Patch"})
    assert "valid_translation: valid patch path escapes allowed_root" in validator.validate(data)


def test_fixture_contract_rejects_malformed_patch_envelope() -> None:
    validator = load_validator()
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    valid = next(case for case in data["cases"] if case["id"] == "valid_translation")
    valid["provider_calls"][0]["arguments"] = json.dumps({"patch": "Update File: runtime/agent_jobs/p113_fixture/allowed.txt"})
    assert "valid_translation: patch must have one supported complete envelope" in validator.validate(data)
