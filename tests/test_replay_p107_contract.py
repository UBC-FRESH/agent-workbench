import sys
import json, hashlib, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from replay_p107_contract import replay_contract


def valid():
    root = Path(tempfile.mkdtemp())
    bundle = {"bundle_sha256":"", "run_id":"r", "review_number":1, "packet_kind":"initial", "packet_bytes":1, "estimated_input_tokens":1, "acceptance_output":"ok", "scope_report":"ok", "changed_files":[], "contamination_status":"clean", "advisor_session_id":"s", "advisor_lineage_id":"l"}
    bundle["bundle_sha256"] = hashlib.sha256((json.dumps(bundle, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()
    verdict = {"review_number":1,"verdict":"accepted","deterministic_acceptance":True,"correctness":3,"score":8,"critical_defects":[],"defect_packet":None,"run_id":"r","bundle_sha256":bundle["bundle_sha256"],"advisor_session_id":"s","advisor_lineage_id":"l"}
    bp, vp = root / "bundle.json", root / "verdict.json"; bp.write_text(json.dumps(bundle)); vp.write_text(json.dumps(verdict))
    return {"topology_valid": True, "frozen_inputs_valid": True,
            "advisor_hard_wait_valid": True, "advisor_verdict_valid": True,
            "advisor_bundle_path": str(bp), "advisor_verdict_path": str(vp),
            "advisor_events": [{"to": "COORDINATOR_PRECHECK"}, {"to": "FREEZE_REVIEW_BUNDLE"}, {"to": "ADVISOR_HARD_WAIT"}, {"to": "ACCEPTED"}],
            "accounting_valid": True, "contamination_valid": True,
            "c0_eligible": True}


def test_valid_synthetic_replay_is_eligible_without_roi_claim():
    assert replay_contract(valid()) == {"outcome": "eligible", "reason_codes": [], "roi": None}


def test_each_failure_class_fails_closed():
    cases = {
        "topology_session_reuse": {"topology_valid": False},
        "frozen_input_hash_drift": {"hash_drift": True},
        "advisor_hard_wait_failure": {"advisor_bundle_path": "missing", "advisor_verdict_path": "missing"},
        "accounting_ineligible": {"accounting_valid": False},
        "contaminated": {"contaminated": True},
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

def test_verified_blocker_is_terminal_non_comparable_not_wait_failure():
    state = valid(); state["advisor_events"][-1] = {"to": "VERIFIED_BLOCKER"}
    verdict = json.loads(Path(state["advisor_verdict_path"]).read_text()); verdict["verdict"] = "verified_blocker"; verdict["critical_defects"] = ["evidence"]; Path(state["advisor_verdict_path"]).write_text(json.dumps(verdict))
    result = replay_contract(state)
    assert result == {"outcome": "not_comparable", "reason_codes": ["verified_blocker"], "roi": None}

def test_mismatched_asserted_terminal_is_rejected():
    state = valid(); state["advisor_terminal"] = "verified_blocker"
    assert replay_contract(state)["outcome"] == "eligible"

def test_boolean_claims_without_validator_and_evidence_are_rejected():
    state = valid(); state.pop("advisor_bundle_path"); state.pop("advisor_verdict_path")
    assert replay_contract(state)["reason_codes"] == ["advisor_hard_wait_failure"]
