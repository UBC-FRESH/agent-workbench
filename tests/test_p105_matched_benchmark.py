from pathlib import Path

from scripts.validate_p105_matched_benchmark import validate


def test_p105_contract_validates() -> None:
    root = Path(__file__).parents[1]
    errors = validate(
        root / "benchmarks/document_library/p105_matched_benchmark_contract.json",
        root,
    )
    assert errors == []


def test_p105_contract_rejects_live_inference(tmp_path: Path) -> None:
    import json

    root = Path(__file__).parents[1]
    contract = json.loads(
        (root / "benchmarks/document_library/p105_matched_benchmark_contract.json").read_text()
    )
    contract["live_inference_allowed"] = True
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract))
    assert "P105 must be dry-run-only" in validate(path, root)
