import json
from pathlib import Path

import pytest

from scripts.validate_p105_matched_benchmark import validate


ROOT = Path(__file__).parents[1]
CONTRACT = ROOT / "benchmarks/document_library/p105_matched_benchmark_contract.json"


def write_contract(tmp_path: Path, mutate) -> Path:
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    mutate(data)
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_p105_contract_validates() -> None:
    assert validate(CONTRACT, ROOT) == []


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda data: data.__setitem__("live_inference_allowed", True), "P105 must be dry-run-only"),
        (lambda data: data["source"].__setitem__("source_manifest_sha256", "0" * 64), "source manifest sha256 mismatch"),
        (lambda data: data["source"].__setitem__("text_sha256", "0" * 64), "source chunk text_sha256 mismatch"),
        (lambda data: data["p89_contract"].__setitem__("record_validation_contract", "missing.json"), "P89 record validation contract missing"),
        (lambda data: data["records"].__setitem__("selected_ticket_ids", ["missing-ticket"]), "selected ticket is absent"),
        (lambda data: data["lanes"].__setitem__("model_argument_contract", {}), "model argument contract mismatch"),
        (lambda data: data.__setitem__("stop_rules", []), "stop rules mismatch"),
        (lambda data: data["output_contract"].__setitem__("audit_statuses", ["accepted"]), "output contract mismatch"),
    ],
)
def test_p105_contract_rejects_tampering(tmp_path: Path, mutate, expected: str) -> None:
    errors = validate(write_contract(tmp_path, mutate), ROOT)
    assert any(expected in error for error in errors)
