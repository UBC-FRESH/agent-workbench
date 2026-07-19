from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from compare_p107_observations import compare

def test_comparison_requires_clean_accepted_c0_and_treatment() -> None:
    report=compare(ROOT/"benchmarks"/"document_library"/"p107_synthetic_observations.json")
    assert report["comparisons"][0]["roi_status"]=="eligible_baseline"
    assert report["comparisons"][1]["roi_status"]=="comparable"
    assert report["comparisons"][2]["roi_status"]=="not_comparable"
    assert report["comparisons"][2]["reason_codes"]==["contaminated"]

def test_comparison_reports_contract_failures(tmp_path: Path) -> None:
    data = {"observations": [{"evaluation_block_id":"block-a","evaluation_block_valid":True,"advisor_binding_valid":True,"accounting_provenance_valid":True,"configuration_topology_valid":True,"model_identity_valid":True,"run_id":"c0","configuration_id":"C0","deterministic_acceptance":True,"advisor_verdict":"accepted","contaminated":False,"accounting_complete":True,"baseline_run_id":None,"paid_run_cost":10},{"evaluation_block_id":"block-a","run_id":"c1","configuration_id":"C1","deterministic_acceptance":False,"advisor_verdict":"pending","contaminated":True,"accounting_complete":False,"baseline_run_id":"c0","paid_run_cost":8,"evaluation_block_valid":False,"advisor_binding_valid":False,"accounting_provenance_valid":False,"configuration_topology_valid":False,"model_identity_valid":False}]}
    path = tmp_path / "observations.json"; path.write_text(json.dumps(data))
    assert compare(path)["comparisons"][1]["reason_codes"] == ["invalid_evaluation_block","deterministic_acceptance_failed","advisor_not_accepted","advisor_binding_invalid","contaminated","accounting_ineligible","accounting_provenance_invalid","configuration_topology_mismatch","model_identity_mismatch"]

def test_missing_evidence_flag_is_not_comparable(tmp_path: Path) -> None:
    data = {"observations": [{"evaluation_block_id":"block-a","run_id":"c0","configuration_id":"C0","deterministic_acceptance":True,"advisor_verdict":"accepted","contaminated":False,"accounting_complete":True,"baseline_run_id":None,"paid_run_cost":10}]}
    path = tmp_path / "observations.json"; path.write_text(json.dumps(data))
    result = compare(path)["comparisons"][0]
    assert result["roi_status"] == "not_comparable"
    assert result["reason_codes"] == ["invalid_evaluation_block","advisor_binding_invalid","accounting_provenance_invalid","configuration_topology_mismatch","model_identity_mismatch"]
