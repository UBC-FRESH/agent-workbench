import sys
import json, hashlib, tempfile, subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from replay_p107_contract import replay_contract


def valid():
    root = Path(tempfile.mkdtemp())
    repo = root / "worktree"; repo.mkdir(); subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=repo, check=True); subprocess.run(["git", "config", "user.name", "Fixture"], cwd=repo, check=True)
    (repo / "tracked.txt").write_text("fixture\n"); subprocess.run(["git", "add", "tracked.txt"], cwd=repo, check=True); subprocess.run(["git", "commit", "-qm", "fixture"], cwd=repo, check=True)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()
    raw = root / "coordinator.jsonl"; raw.write_text("{}\n"); raw_hash = hashlib.sha256(raw.read_bytes()).hexdigest()
    advisor_raw = root / "advisor.jsonl"; advisor_raw.write_text("{}\n"); advisor_hash = hashlib.sha256(advisor_raw.read_bytes()).hexdigest()
    edge_artifact = root / "spawn.json"; edge_artifact.write_text("{}\n"); edge_hash = hashlib.sha256(edge_artifact.read_bytes()).hexdigest()
    manifest = {"schema_version":"p107_run_evidence_manifest_v1", "run_id":"r", "configuration_id":"C0", "repository_path":str(repo), "starting_commit":commit, "terminal_event":"completed", "raw_sessions":[{"role":"coordinator","session_id":"coordinator-1","parent_session_id":None,"provider":"fixture","model_class":"fixture","raw_session_path":raw.name,"sha256":raw_hash,"terminal_event":"completed"},{"role":"advisor","session_id":"s","parent_session_id":"coordinator-1","provider":"fixture","model_class":"fixture","raw_session_path":advisor_raw.name,"sha256":advisor_hash,"terminal_event":"completed"}], "spawn_edges":[{"parent_session_id":"coordinator-1","child_session_id":"s","parent_role":"coordinator","child_role":"advisor","fork_context":False,"source_artifact_path":edge_artifact.name,"source_artifact_sha256":edge_hash}]}
    manifest_path = root / "manifest.json"; manifest_path.write_text(json.dumps(manifest)); manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    bundle = {"bundle_sha256":"", "run_id":"r", "review_number":1, "packet_kind":"initial", "packet_bytes":1, "estimated_input_tokens":1, "acceptance_output":"ok", "scope_report":"ok", "changed_files":[], "contamination_status":"clean", "advisor_session_id":"s", "advisor_lineage_id":"l"}
    bundle["bundle_sha256"] = hashlib.sha256((json.dumps(bundle, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()
    verdict = {"review_number":1,"verdict":"accepted","deterministic_acceptance":True,"correctness":3,"score":8,"critical_defects":[],"defect_packet":None,"run_id":"r","bundle_sha256":bundle["bundle_sha256"],"advisor_session_id":"s","advisor_lineage_id":"l"}
    bp, vp = root / "bundle.json", root / "verdict.json"; bp.write_text(json.dumps(bundle)); vp.write_text(json.dumps(verdict))
    return {"topology_valid": True, "frozen_inputs_valid": True,
            "advisor_hard_wait_valid": True, "advisor_verdict_valid": True,
            "advisor_bundle_path": str(bp), "advisor_verdict_path": str(vp),
            "advisor_events": [{"to": "COORDINATOR_PRECHECK"}, {"to": "FREEZE_REVIEW_BUNDLE"}, {"to": "ADVISOR_HARD_WAIT"}, {"to": "ACCEPTED"}],
            "accounting_valid": True, "contamination_valid": True,
            "c0_eligible": True, "evidence_manifest_path": str(manifest_path), "evidence_manifest_sha256": manifest_hash}


def test_valid_synthetic_replay_is_eligible_without_roi_claim():
    result = replay_contract(valid())
    assert result["outcome"] == "not_comparable"
    assert "accounting_ineligible" in result["reason_codes"]


def test_each_failure_class_fails_closed():
    cases = {
        "topology_session_reuse": {"evidence_manifest_path": "missing", "evidence_manifest_sha256": "missing"},
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
        assert reason in result["reason_codes"]
        assert reason in result["reason_codes"]


def test_multiple_failures_are_all_reported_and_roi_is_not_fabricated():
    state = valid(); state.update({"evidence_manifest_path": "missing", "evidence_manifest_sha256": "missing", "hash_drift": True, "c0_mismatched": True})
    result = replay_contract(state)
    assert result["outcome"] == "not_comparable"
    assert {"topology_session_reuse", "frozen_input_hash_drift", "accounting_ineligible", "c0_absent_or_mismatched"}.issubset(result["reason_codes"])
    assert result["roi"] is None

def test_verified_blocker_is_terminal_non_comparable_not_wait_failure():
    state = valid(); state["advisor_events"][-1] = {"to": "VERIFIED_BLOCKER"}
    verdict = json.loads(Path(state["advisor_verdict_path"]).read_text()); verdict["verdict"] = "verified_blocker"; verdict["critical_defects"] = ["evidence"]; Path(state["advisor_verdict_path"]).write_text(json.dumps(verdict))
    result = replay_contract(state)
    assert result["outcome"] == "not_comparable"
    assert "verified_blocker" in result["reason_codes"]

def test_mismatched_asserted_terminal_is_rejected():
    state = valid(); state["advisor_terminal"] = "verified_blocker"
    assert replay_contract(state)["outcome"] == "not_comparable"

def test_boolean_claims_without_validator_and_evidence_are_rejected():
    state = valid(); state.pop("advisor_bundle_path"); state.pop("advisor_verdict_path")
    assert "advisor_hard_wait_failure" in replay_contract(state)["reason_codes"]
