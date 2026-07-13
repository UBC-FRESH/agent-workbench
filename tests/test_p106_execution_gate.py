import json
from pathlib import Path

import pytest

from scripts.validate_p106_execution_gate import validate


ROOT = Path(__file__).parents[1]
GATE = ROOT / "benchmarks/document_library/p106_matched_execution_gate.json"


def write_gate(tmp_path: Path, mutate) -> Path:
    data = json.loads(GATE.read_text(encoding="utf-8"))
    mutate(data)
    path = tmp_path / "gate.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_p106_gate_validates_native_bindings() -> None:
    assert validate(GATE, ROOT) == []


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda data: data["budgets_usd"].__setitem__("total_paid_coordinator_cap", 0.3), "total paid Coordinator cap"),
        (lambda data: data["pricing"].__setitem__("catalog_required", False), "pricing requirement missing"),
        (lambda data: data["attempts"].__setitem__("initial", 2), "attempt and repair limits"),
        (lambda data: data["delegated_quality_gate"].__setitem__("minimum_useful_yield", 0.8), "delegated quality gate"),
        (lambda data: data.__setitem__("p105_contract", "missing.json"), "referenced P105 contract"),
    ],
)
def test_p106_gate_rejects_tampering(tmp_path: Path, mutate, expected: str) -> None:
    errors = validate(write_gate(tmp_path, mutate), ROOT)
    assert any(expected in error for error in errors)
