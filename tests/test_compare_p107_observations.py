from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from compare_p107_observations import _legacy_cost_compatible, compare


def _write(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "observations.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_legacy_paid_cost_cannot_override_validated_accounting() -> None:
    assert _legacy_cost_compatible({}, 7) is True
    assert _legacy_cost_compatible({"paid_run_cost": 7}, 7) is True
    assert _legacy_cost_compatible({"paid_run_cost": 8}, 7) is False


def test_current_plan_does_not_require_advisor_fields(tmp_path: Path) -> None:
    observation = {
        "evaluation_block_id": "block-a",
        "evaluation_block_valid": True,
        "accounting_provenance_valid": True,
        "configuration_topology_valid": True,
        "model_identity_valid": True,
        "run_id": "c0",
        "configuration_id": "C0",
        "deterministic_acceptance": True,
        "contaminated": False,
        "accounting_complete": False,
        "baseline_run_id": None,
    }

    result = compare(_write(tmp_path, {"observations": [observation]}))["comparisons"][0]

    assert result["roi_status"] == "not_comparable"
    assert "advisor_hard_wait_failure" not in result["reason_codes"]
    assert "accounting_ineligible" in result["reason_codes"]


def test_invalid_observation_shape_remains_not_comparable(tmp_path: Path) -> None:
    result = compare(_write(tmp_path, {"observations": [None]}))["comparisons"][0]
    assert result["roi_status"] == "not_comparable"
    assert result["reason_codes"] == ["invalid_observation_shape"]
