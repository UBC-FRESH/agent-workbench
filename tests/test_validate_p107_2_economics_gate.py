from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_p107_2_economics_gate import validate_gate


GATE = ROOT / "benchmarks" / "document_library" / "p107_2_economics_gate.json"


def write_gate(tmp_path: Path, mutate) -> Path:
    document = json.loads(GATE.read_text(encoding="utf-8"))
    mutate(document)
    path = tmp_path / "gate.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def test_current_ab_preflight_contract_is_valid() -> None:
    assert validate_gate(GATE) == []


def test_rejects_one_shot_zero_repair_contract(tmp_path: Path) -> None:
    path = write_gate(
        tmp_path,
        lambda document: document["review"].update(
            max_completed_reviews_per_lane=1,
            max_repair_cycles_per_lane=0,
        ),
    )

    errors = validate_gate(path)

    assert "review.max_completed_reviews_per_lane must be 3" in errors
    assert "review.max_repair_cycles_per_lane must be 2" in errors


def test_rejects_worker_final_as_acceptance_and_passive_waiting(tmp_path: Path) -> None:
    path = write_gate(
        tmp_path,
        lambda document: (
            document["workbench"].update(worker_final_is_acceptance=True),
            document["liveness"].update(passive_waiting_allowed=True),
        ),
    )

    errors = validate_gate(path)

    assert "Worker final response cannot be acceptance" in errors
    assert "liveness.passive_waiting_allowed must be False" in errors
