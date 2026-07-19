from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from compare_p107_observations import compare

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
