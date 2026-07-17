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
    assert report["comparisons"][1]=={"run_id":"c1-a","roi_status":"comparable","paid_roi":0.3}
    assert report["comparisons"][2]["roi_status"]=="not_comparable"
