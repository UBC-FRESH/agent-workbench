from __future__ import annotations
import json
import hashlib
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from compare_p107_observations import compare, _advisor_artifacts_valid, _legacy_cost_compatible

def _valid_artifacts(tmp_path: Path, run_id: str, cost: float, *, verdict="accepted", advisor_run_id=None, advisor_session="advisor-1") -> dict:
    bundle = {"bundle_sha256":"0"*64,"run_id":advisor_run_id or run_id,"review_number":1,"packet_kind":"initial","packet_bytes":1,"estimated_input_tokens":1,"acceptance_output":"pass","scope_report":"clean","changed_files":[],"contamination_status":"clean","previous_defect_packet":None,"advisor_session_id":advisor_session,"advisor_lineage_id":"line-1"}
    unsigned = dict(bundle); unsigned["bundle_sha256"] = ""
    bundle["bundle_sha256"] = hashlib.sha256((json.dumps(unsigned, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()
    verdict_doc = {"run_id":advisor_run_id or run_id,"review_number":1,"verdict":verdict,"bundle_sha256":bundle["bundle_sha256"],"deterministic_acceptance":True,"correctness":4,"score":9,"critical_defects":[],"defect_packet":None,"advisor_session_id":advisor_session,"advisor_lineage_id":"line-1"}
    if verdict == "defect_packet": verdict_doc["defect_packet"] = {"defect_id":"D1","failed_evidence":"failed","acceptance_condition":"pass"}
    bp, vp = tmp_path / f"{run_id}-bundle.json", tmp_path / f"{run_id}-verdict.json"
    bp.write_text(json.dumps(bundle) + "\n"); vp.write_text(json.dumps(verdict_doc) + "\n")
    manifest = {"schema_version":"p107_run_evidence_manifest_v1","run_id":run_id,"configuration_id":"C0","repository_path":str(ROOT),"starting_commit":"773f2d7".ljust(40,"0"),"terminal_event":"done","raw_sessions":[],"spawn_edges":[]}
    # The comparator's focused checks use the manifest's declared Advisor identity.
    manifest["raw_sessions"] = [{"role":"advisor","session_id":advisor_session}]
    mp = tmp_path / f"{run_id}-manifest.json"; mp.write_text(json.dumps(manifest))
    return {"advisor_bundle_path":str(bp),"advisor_verdict_path":str(vp),"evidence_manifest_path":str(mp),"evidence_manifest_sha256":hashlib.sha256(mp.read_bytes()).hexdigest(),"accounting_record_path":str(tmp_path / "missing-accounting.json"),"paid_run_cost":cost}

def test_advisor_false_positives_fail_closed(tmp_path: Path) -> None:
    accepted = _valid_artifacts(tmp_path, "run-1", 1)
    assert _advisor_artifacts_valid(dict(accepted, run_id="run-1")) is True
    assert _advisor_artifacts_valid(dict(_valid_artifacts(tmp_path, "run-2", 1, verdict="defect_packet"), run_id="run-2")) is False
    assert _advisor_artifacts_valid(dict(_valid_artifacts(tmp_path, "run-3", 1, advisor_run_id="other"), run_id="run-3")) is False
    assert _advisor_artifacts_valid(dict(_valid_artifacts(tmp_path, "run-4", 1), run_id="run-4", advisor_session_id="other")) is False

def test_legacy_paid_cost_cannot_override_validated_accounting() -> None:
    assert _legacy_cost_compatible({}, 7) is True
    assert _legacy_cost_compatible({"paid_run_cost": 7}, 7) is True
    assert _legacy_cost_compatible({"paid_run_cost": 8}, 7) is False

def test_comparison_requires_clean_accepted_c0_and_treatment() -> None:
    report=compare(ROOT/"benchmarks"/"document_library"/"p107_synthetic_observations.json")
    assert report["comparisons"][0]["roi_status"]=="not_comparable"
    assert report["comparisons"][1]["roi_status"]=="not_comparable"
    assert report["comparisons"][2]["roi_status"]=="not_comparable"
    assert "contaminated" in report["comparisons"][2]["reason_codes"]

def test_comparison_reports_contract_failures(tmp_path: Path) -> None:
    data = {"observations": [{"evaluation_block_id":"block-a","evaluation_block_valid":True,"advisor_binding_valid":True,"accounting_provenance_valid":True,"configuration_topology_valid":True,"model_identity_valid":True,"run_id":"c0","configuration_id":"C0","deterministic_acceptance":True,"advisor_verdict":"accepted","contaminated":False,"accounting_complete":True,"baseline_run_id":None,"paid_run_cost":10},{"evaluation_block_id":"block-a","run_id":"c1","configuration_id":"C1","deterministic_acceptance":False,"advisor_verdict":"pending","contaminated":True,"accounting_complete":False,"baseline_run_id":"c0","paid_run_cost":8,"evaluation_block_valid":False,"advisor_binding_valid":False,"accounting_provenance_valid":False,"configuration_topology_valid":False,"model_identity_valid":False}]}
    path = tmp_path / "observations.json"; path.write_text(json.dumps(data))
    assert "advisor_hard_wait_failure" in compare(path)["comparisons"][1]["reason_codes"]

def test_missing_evidence_flag_is_not_comparable(tmp_path: Path) -> None:
    data = {"observations": [{"evaluation_block_id":"block-a","run_id":"c0","configuration_id":"C0","deterministic_acceptance":True,"advisor_verdict":"accepted","contaminated":False,"accounting_complete":True,"baseline_run_id":None,"paid_run_cost":10}]}
    path = tmp_path / "observations.json"; path.write_text(json.dumps(data))
    result = compare(path)["comparisons"][0]
    assert result["roi_status"] == "not_comparable"
    assert "advisor_hard_wait_failure" in result["reason_codes"]

def test_adversarial_costs_duplicates_and_shape(tmp_path: Path) -> None:
    base = {"evaluation_block_id":"b", "evaluation_block_valid":True, "advisor_binding_valid":True, "accounting_provenance_valid":True, "configuration_topology_valid":True, "model_identity_valid":True, "run_id":"c0", "configuration_id":"C0", "deterministic_acceptance":True, "advisor_verdict":"accepted", "contaminated":False, "accounting_complete":True, "baseline_run_id":None}
    rows = [dict(base, paid_run_cost=None), dict(base, run_id="c0", paid_run_cost=1), dict(base, run_id="t", configuration_id="C1", baseline_run_id="c0", paid_run_cost=-1), None]
    results = compare_path = compare(_write(tmp_path, {"observations": rows}))["comparisons"]
    assert all(r["roi_status"] == "not_comparable" for r in results)
    assert "duplicate_run_id" in results[0]["reason_codes"]
    assert "accounting_ineligible" in results[2]["reason_codes"]
    assert results[3]["reason_codes"] == ["invalid_observation_shape"]

def _write(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "observations.json"; path.write_text(json.dumps(data)); return path
