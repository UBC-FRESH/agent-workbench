"""Fail-closed P107 C0-relative paid ROI comparison."""
from __future__ import annotations
import json
import sys
from pathlib import Path

def eligible(row: dict) -> bool:
    return row.get("deterministic_acceptance") is True and row.get("advisor_verdict")=="accepted" and row.get("contaminated") is False and row.get("accounting_complete") is True

def compare(path: str | Path) -> dict:
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    rows=data.get("observations",[])
    by_id={row.get("run_id"):row for row in rows if isinstance(row,dict)}
    result=[]
    for row in rows:
        if row.get("configuration_id")=="C0":
            result.append({"run_id":row.get("run_id"),"roi_status":"eligible_baseline" if eligible(row) else "not_comparable","paid_roi":None}); continue
        base=by_id.get(row.get("baseline_run_id"))
        if not eligible(row) or not base or base.get("configuration_id")!="C0" or not eligible(base) or base.get("evaluation_block_id")!=row.get("evaluation_block_id"):
            result.append({"run_id":row.get("run_id"),"roi_status":"not_comparable","paid_roi":None}); continue
        cost=float(row["paid_run_cost"]); base_cost=float(base["paid_run_cost"])
        result.append({"run_id":row["run_id"],"roi_status":"comparable","paid_roi":(base_cost-cost)/base_cost})
    return {"comparisons":result}

if __name__=="__main__":
    print(json.dumps(compare(sys.argv[1]),indent=2))
