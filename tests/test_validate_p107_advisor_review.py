import hashlib
import json
import os

from scripts.validate_p107_advisor_review import validate_review


def write_pair(tmp_path, *, kind="initial", review=1, verdict="accepted"):
    bundle = {"bundle_sha256":"0"*64,"run_id":"run-1","review_number":review,"packet_kind":kind,"packet_bytes":1,"estimated_input_tokens":1,"acceptance_output":"pass","scope_report":"clean","changed_files":[],"contamination_status":"clean","previous_defect_packet":None,"advisor_session_id":"advisor-1","advisor_lineage_id":"line-1"}
    if kind == "repair_delta": bundle["previous_defect_packet"] = {"defect_id":"D1"}
    unsigned = dict(bundle); unsigned["bundle_sha256"] = ""
    bundle["bundle_sha256"] = hashlib.sha256((json.dumps(unsigned, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()
    result = {"run_id":"run-1","review_number":review,"verdict":verdict,"bundle_sha256":bundle["bundle_sha256"],"deterministic_acceptance":True,"correctness":4,"score":9,"critical_defects":[],"defect_packet":None,"advisor_session_id":"advisor-1","advisor_lineage_id":"line-1"}
    if verdict == "defect_packet": result["defect_packet"] = {"defect_id":"D1","failed_evidence":"test failed","acceptance_condition":"test passes"}
    bp, vp = tmp_path / "bundle.json", tmp_path / "verdict.json"
    bp.write_text(json.dumps(bundle) + "\n"); vp.write_text(json.dumps(result) + "\n")
    return bp, vp


def test_valid_initial_pair(tmp_path):
    assert validate_review(*write_pair(tmp_path)) == []


def test_validation_is_independent_of_current_working_directory(tmp_path):
    pair = write_pair(tmp_path)
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    original = os.getcwd()
    try:
        os.chdir(unrelated)
        assert validate_review(*pair) == []
    finally:
        os.chdir(original)


def test_rejects_hash_run_and_session_reuse(tmp_path):
    bp, vp = write_pair(tmp_path)
    data = json.loads(vp.read_text()); data["run_id"] = "run-2"; vp.write_text(json.dumps(data))
    assert any("run ID" in e for e in validate_review(bp, vp, prior_session_ids={"advisor-1"}))
    assert any("reused" in e for e in validate_review(bp, vp, prior_session_ids={"advisor-1"}))


def test_repair_and_defect_packet_require_lineage_fields(tmp_path):
    bp, vp = write_pair(tmp_path, kind="repair_delta", review=2, verdict="defect_packet")
    data = json.loads(vp.read_text()); del data["defect_packet"]["acceptance_condition"]; vp.write_text(json.dumps(data))
    assert any("acceptance_condition" in e for e in validate_review(bp, vp))


def test_pending_is_invalid_and_initial_cannot_have_prior(tmp_path):
    bp, vp = write_pair(tmp_path)
    bundle = json.loads(bp.read_text()); bundle["previous_defect_packet"] = {"defect_id":"D1"}; bp.write_text(json.dumps(bundle))
    verdict = json.loads(vp.read_text()); verdict["verdict"] = "pending"; vp.write_text(json.dumps(verdict))
    errors = validate_review(bp, vp)
    assert any("initial packet" in e for e in errors)
    assert any("valid verdict" in e for e in errors)


def test_accepted_requires_all_quality_gates(tmp_path):
    bp, vp = write_pair(tmp_path)
    data = json.loads(vp.read_text())
    for field, value in (("deterministic_acceptance", False), ("correctness", 2), ("score", 7), ("critical_defects", ["C1"])):
        data[field] = value
        vp.write_text(json.dumps(data))
        assert validate_review(bp, vp), field
        data[field] = {"deterministic_acceptance": True, "correctness": 4, "score": 9, "critical_defects": []}[field]


def test_review_numbers_are_exactly_one_through_three(tmp_path):
    for review in (0, 4, 8):
        case = tmp_path / str(review); case.mkdir()
        bp, vp = write_pair(case, review=review)
        assert validate_review(bp, vp)


def test_verified_blocker_is_a_valid_terminal_verdict(tmp_path):
    bp, vp = write_pair(tmp_path, verdict="verified_blocker")
    data = json.loads(vp.read_text()); data["deterministic_acceptance"] = False; data["critical_defects"] = ["worker evidence unavailable"]; vp.write_text(json.dumps(data))
    assert validate_review(bp, vp) == []


def test_orphan_review_three_is_rejected_without_history(tmp_path):
    bp, vp = write_pair(tmp_path, kind="repair_delta", review=3)
    errors = validate_review(bp, vp)
    assert any("history is required" in error for error in errors)


def test_broken_prior_hash_cannot_be_represented_as_valid_history(tmp_path):
    bp, vp = write_pair(tmp_path, kind="repair_delta", review=2)
    errors = validate_review(bp, vp)
    assert any("history is required" in error for error in errors)


def test_advisor_identity_change_does_not_supply_history(tmp_path):
    bp, vp = write_pair(tmp_path, kind="repair_delta", review=2)
    data = json.loads(vp.read_text()); data["advisor_session_id"] = "advisor-2"; vp.write_text(json.dumps(data))
    errors = validate_review(bp, vp)
    assert any("session/lineage mismatch" in error for error in errors)
    assert any("history is required" in error for error in errors)


def test_verified_blocker_requires_explicit_evidence(tmp_path):
    bp, vp = write_pair(tmp_path, verdict="verified_blocker")
    data = json.loads(vp.read_text()); data["deterministic_acceptance"] = False; vp.write_text(json.dumps(data))
    assert any("explicit blocker evidence" in error for error in validate_review(bp, vp))


def test_defect_packet_must_be_complete(tmp_path):
    bp, vp = write_pair(tmp_path, kind="repair_delta", review=2, verdict="defect_packet")
    data = json.loads(vp.read_text())
    for field in ("defect_id", "failed_evidence", "acceptance_condition"):
        del data["defect_packet"][field]
        vp.write_text(json.dumps(data))
        assert validate_review(bp, vp)
        data["defect_packet"][field] = "present"


def write_history(tmp_path, count=3):
    entries = []
    prior = None
    for review in range(1, count + 1):
        folder = tmp_path / f"r{review}"; folder.mkdir()
        bp, vp = write_pair(folder, kind="initial" if review == 1 else "repair_delta", review=review, verdict="accepted" if review == count else "defect_packet")
        entries.append({"review_number": review, "bundle_path": f"r{review}/{bp.name}", "verdict_path": f"r{review}/{vp.name}", "bundle_sha256": hashlib.sha256(bp.read_bytes()).hexdigest(), "verdict_sha256": hashlib.sha256(vp.read_bytes()).hexdigest(), "prior_verdict_sha256": prior, "advisor_lineage_id": "line-1", "advisor_session_id": "advisor-1"})
        prior = entries[-1]["verdict_sha256"]
    history = tmp_path / "history.json"; history.write_text(json.dumps({"entries": entries}) + "\n")
    return history, tmp_path / f"r{count}" / "bundle.json", tmp_path / f"r{count}" / "verdict.json"


def test_valid_three_review_history(tmp_path):
    history, bp, vp = write_history(tmp_path)
    assert validate_review(bp, vp, history_path=history) == []


def test_history_rejects_missing_middle_review(tmp_path):
    history, bp, vp = write_history(tmp_path)
    data = json.loads(history.read_text()); data["entries"].pop(1); history.write_text(json.dumps(data))
    assert any("contiguous" in error for error in validate_review(bp, vp, history_path=history))


def test_history_rejects_broken_prior_hash(tmp_path):
    history, bp, vp = write_history(tmp_path)
    data = json.loads(history.read_text()); data["entries"][2]["prior_verdict_sha256"] = "f" * 64; history.write_text(json.dumps(data))
    assert any("prior verdict hash" in error for error in validate_review(bp, vp, history_path=history))


def test_history_rejects_advisor_identity_change(tmp_path):
    history, bp, vp = write_history(tmp_path)
    data = json.loads(history.read_text()); data["entries"][1]["advisor_session_id"] = "advisor-2"; history.write_text(json.dumps(data))
    assert any("Advisor identity mismatch" in error for error in validate_review(bp, vp, history_path=history))


def test_history_rejects_altered_artifact_bytes(tmp_path):
    history, bp, vp = write_history(tmp_path)
    first = tmp_path / "r1" / "bundle.json"; first.write_text(first.read_text() + " ")
    assert any("sha256 mismatch" in error for error in validate_review(bp, vp, history_path=history))
