from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_p114_c4_capability_contract.py"
CONTRACT = ROOT / "benchmarks" / "document_library" / "p114_c4_capability_contract.json"


def load_validator():
    spec = importlib.util.spec_from_file_location("p114_contract", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_is_valid() -> None:
    validator = load_validator()
    assert validator.validate(json.loads(CONTRACT.read_text(encoding="utf-8"))) == []


def test_contract_rejects_live_preregistration() -> None:
    validator = load_validator()
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    data["live_inference"] = True
    assert "preregistration must not enable live inference" in validator.validate(data)


def test_contract_rejects_missing_native_patch_capability() -> None:
    validator = load_validator()
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    data["required_capabilities"] = [
        item for item in data["required_capabilities"] if item["id"] != "native_patch_surface"
    ]
    assert "required capabilities must match the declared minimum interface" in validator.validate(data)


def test_contract_requires_failure_handling_without_an_attempt_cap() -> None:
    validator = load_validator()
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    data.pop("failure_handling")
    assert "failure handling must be explicit" in validator.validate(data)
