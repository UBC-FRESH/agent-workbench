import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from replay_p107_contract import replay_contract


def valid():
    return {"topology_valid": True, "frozen_inputs_valid": True,
            "advisor_hard_wait_valid": True, "advisor_verdict_valid": True,
            "accounting_valid": True, "contamination_valid": True,
            "c0_eligible": True}


def test_valid_synthetic_replay_is_eligible_without_roi_claim():
    assert replay_contract(valid()) == {"outcome": "eligible", "reason_codes": [], "roi": None}


def test_each_failure_class_fails_closed():
    cases = {
        "topology_session_reuse": {"topology_valid": False},
        "frozen_input_hash_drift": {"hash_drift": True},
        "advisor_hard_wait_failure": {"advisor_hard_wait_valid": False},
        "accounting_invalid": {"accounting_valid": False},
        "contamination": {"contaminated": True},
        "c0_absent_or_mismatched": {"c0_eligible": False},
    }
    for reason, change in cases.items():
        state = valid(); state.update(change)
        result = replay_contract(state)
        assert result["outcome"] == "not_comparable"
        assert result["reason_codes"] == [reason]


def test_multiple_failures_are_all_reported_and_roi_is_not_fabricated():
    state = valid(); state.update({"session_reuse": True, "hash_drift": True, "c0_mismatched": True})
    result = replay_contract(state)
    assert result["outcome"] == "not_comparable"
    assert result["reason_codes"] == ["topology_session_reuse", "frozen_input_hash_drift", "c0_absent_or_mismatched"]
    assert result["roi"] is None
